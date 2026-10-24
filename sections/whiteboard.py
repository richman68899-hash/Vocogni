"""Interactive Notes whiteboards backed by Vocogni's existing autosave bundle.

The canvas itself runs in the browser so drawing does not trigger a Streamlit
rerun for every pointer movement. A validated page snapshot is sent to Python
when a drawing gesture or object edit completes.
"""
from __future__ import annotations

import datetime
import json
from typing import Any

import streamlit as st

import state
import whiteboard_data


HTML = """
<div class="wb-shell">
  <div class="wb-toolbar" aria-label="Whiteboard tools">
    <div class="wb-toolset">
      <button type="button" data-tool="select" class="wb-tool active" title="Select and move">Select</button>
      <button type="button" data-tool="pen" class="wb-tool" title="Pen">Pen</button>
      <button type="button" data-tool="highlighter" class="wb-tool" title="Highlighter">Highlight</button>
      <button type="button" data-tool="eraser" class="wb-tool" title="Erase objects">Eraser</button>
      <button type="button" data-tool="text" class="wb-tool" title="Add text">Text</button>
      <button type="button" data-tool="sticky" class="wb-tool" title="Add sticky note">Sticky</button>
      <button type="button" data-tool="rect" class="wb-tool" title="Rectangle">Rectangle</button>
      <button type="button" data-tool="ellipse" class="wb-tool" title="Ellipse">Ellipse</button>
      <button type="button" data-tool="arrow" class="wb-tool" title="Arrow or line">Arrow</button>
    </div>
    <div class="wb-toolset wb-settings">
      <label class="wb-color-label" title="Drawing color">Color <input data-color type="color" value="#273142" /></label>
      <label class="wb-width-label" title="Stroke width">Size <input data-width type="range" min="1" max="18" value="4" /></label>
      <button type="button" data-action="undo" title="Undo (Ctrl/Cmd+Z)">↶</button>
      <button type="button" data-action="redo" title="Redo (Ctrl/Cmd+Y)">↷</button>
      <button type="button" data-action="delete" title="Delete selected object">Delete</button>
      <button type="button" data-action="clear" title="Clear page">Clear</button>
    </div>
    <div class="wb-toolset wb-export">
      <button type="button" data-action="png">PNG</button>
      <button type="button" data-action="pdf">Print / PDF</button>
      <button type="button" data-action="json">Page JSON</button>
    </div>
  </div>
  <div class="wb-canvas-viewport">
    <canvas class="wb-canvas" width="1200" height="800" aria-label="Interactive whiteboard canvas"></canvas>
  </div>
  <div class="wb-footer">
    <span data-status>Ready</span>
    <span>Draw with a mouse, stylus, or touch. Select moves objects; Delete removes the selection.</span>
  </div>
</div>
"""

CSS = """
.wb-shell { color: var(--st-text-color); border: 1px solid var(--st-border-color); border-radius: 14px; overflow: hidden; background: var(--st-secondary-background-color); }
.wb-toolbar { padding: 10px; display: flex; flex-wrap: wrap; gap: 8px; border-bottom: 1px solid var(--st-border-color); }
.wb-toolset { display: flex; align-items: center; gap: 5px; flex-wrap: wrap; }
.wb-settings, .wb-export { padding-left: 7px; border-left: 1px solid var(--st-border-color); }
.wb-toolbar button { border: 1px solid var(--st-border-color); border-radius: 8px; padding: 6px 9px; font-size: 12px; color: var(--st-text-color); background: var(--st-background-color); cursor: pointer; }
.wb-toolbar button:hover { border-color: var(--st-primary-color); }
.wb-toolbar button.active { color: white; background: var(--st-primary-color); border-color: var(--st-primary-color); }
.wb-color-label, .wb-width-label { display: flex; align-items: center; gap: 5px; font-size: 12px; white-space: nowrap; }
.wb-color-label input { width: 28px; height: 28px; padding: 1px; border: 0; background: transparent; }
.wb-width-label input { width: 68px; }
.wb-canvas-viewport { width: 100%; height: min(65vh, 650px); min-height: 310px; overflow: auto; background: var(--st-background-color); touch-action: pan-x pan-y; }
.wb-canvas { display: block; width: 100%; height: auto; aspect-ratio: 3/2; background: white; cursor: crosshair; touch-action: none; }
.wb-footer { display: flex; gap: 12px; justify-content: space-between; flex-wrap: wrap; padding: 8px 12px; font-size: 11px; color: var(--st-secondary-text-color); border-top: 1px solid var(--st-border-color); }
@media (max-width: 720px) { .wb-settings, .wb-export { padding-left: 0; border-left: 0; } .wb-canvas-viewport { min-height: 280px; height: 48vh; } .wb-toolbar button { padding: 7px 8px; } }
@media print { body * { visibility: hidden !important; } .wb-shell, .wb-shell * { visibility: visible !important; } .wb-toolbar, .wb-footer { display: none !important; } .wb-canvas-viewport { height: auto !important; overflow: visible !important; } .wb-canvas { width: 100% !important; } }
"""

JS = r"""
export default function(component) {
  const { parentElement, data, setStateValue } = component;
  const root = parentElement.querySelector(".wb-shell");
  if (!root) return;
  const canvas = root.querySelector(".wb-canvas");
  const ctx = canvas.getContext("2d");
  let wb = root.__vocogniWhiteboard;
  const clone = (value) => JSON.parse(JSON.stringify(value));
  const defaultPage = {id:"page", title:"Page", width:1200, height:800, background:"grid", objects:[]};
  const incoming = data && data.page && typeof data.page === "object" ? data.page : defaultPage;

  if (!wb) {
    wb = root.__vocogniWhiteboard = {
      page: clone(incoming), tool:"select", color:"#273142", width:4,
      selected:null, drawing:null, dragging:null, history:[], future:[],
      setStateValue, lastPageId:null, dirty:false
    };
  }
  wb.setStateValue = setStateValue;
  if (wb.lastPageId !== incoming.id) {
    wb.page = clone(incoming);
    wb.selected = null;
    wb.drawing = null;
    wb.dragging = null;
    wb.history = [];
    wb.future = [];
    wb.lastPageId = incoming.id;
  } else {
    // Python is the durable source of truth after a completed edit.
    wb.page = clone(incoming);
  }

  const status = (message) => { root.querySelector("[data-status]").textContent = message; };
  const colorInput = root.querySelector("[data-color]");
  const widthInput = root.querySelector("[data-width]");
  const objects = () => Array.isArray(wb.page.objects) ? wb.page.objects : (wb.page.objects = []);
  const uid = () => (crypto && crypto.randomUUID ? crypto.randomUUID() : "wb-" + Date.now() + "-" + Math.random().toString(16).slice(2));
  const emit = () => {
    wb.dirty = true;
    wb.setStateValue("page", clone(wb.page));
    status("Changes sent to Vocogni for saving…");
  };
  const snapshot = () => {
    wb.history.push(clone(wb.page));
    if (wb.history.length > 40) wb.history.shift();
    wb.future = [];
  };
  const colorFor = (obj) => typeof obj.color === "string" ? obj.color : "#273142";
  const drawBackground = () => {
    ctx.save();
    ctx.clearRect(0, 0, 1200, 800);
    ctx.fillStyle = wb.page.background === "dark" ? "#20242B" : "#FFFFFF";
    ctx.fillRect(0, 0, 1200, 800);
    if (wb.page.background === "grid") {
      ctx.strokeStyle = "#E7EAF0"; ctx.lineWidth = 1;
      for (let x=0; x<=1200; x+=40) { ctx.beginPath(); ctx.moveTo(x,0); ctx.lineTo(x,800); ctx.stroke(); }
      for (let y=0; y<=800; y+=40) { ctx.beginPath(); ctx.moveTo(0,y); ctx.lineTo(1200,y); ctx.stroke(); }
    } else if (wb.page.background === "dots") {
      ctx.fillStyle = "#D7DBE3";
      for (let x=20; x<1200; x+=40) for (let y=20; y<800; y+=40) { ctx.beginPath(); ctx.arc(x,y,1.4,0,Math.PI*2); ctx.fill(); }
    }
    ctx.restore();
  };
  const wrapText = (text, x, y, maxWidth, lineHeight, font) => {
    ctx.font = font;
    const lines = String(text || "").split("
");
    let yy = y;
    lines.forEach(line => {
      const words = line.split(/s+/);
      let current = "";
      for (const word of words) {
        const next = current ? current + " " + word : word;
        if (current && ctx.measureText(next).width > maxWidth) {
          ctx.fillText(current, x, yy); yy += lineHeight; current = word;
        } else current = next;
      }
      ctx.fillText(current, x, yy); yy += lineHeight;
    });
  };
  const bounds = (obj) => {
    if (obj.type === "stroke") {
      const xs = obj.points.map(p=>p.x), ys=obj.points.map(p=>p.y);
      return {x:Math.min(...xs)-8,y:Math.min(...ys)-8,w:Math.max(...xs)-Math.min(...xs)+16,h:Math.max(...ys)-Math.min(...ys)+16};
    }
    if (obj.type === "text") return {x:obj.x,y:obj.y-obj.fontSize,w:Math.max(80,String(obj.text||"").length*obj.fontSize*.6),h:obj.fontSize*1.6};
    return {x:obj.x,y:obj.y,w:obj.w||1,h:obj.h||1};
  };
  const drawObject = (obj) => {
    ctx.save();
    ctx.strokeStyle = colorFor(obj);
    ctx.fillStyle = colorFor(obj);
    ctx.lineWidth = Math.max(1, Number(obj.width || 3));
    ctx.lineCap = "round"; ctx.lineJoin = "round";
    if (obj.type === "stroke") {
      if (obj.tool === "highlighter") ctx.globalAlpha = 0.33;
      const pts = Array.isArray(obj.points) ? obj.points : [];
      if (pts.length) {
        ctx.beginPath(); ctx.moveTo(pts[0].x,pts[0].y);
        pts.slice(1).forEach(p=>ctx.lineTo(p.x,p.y));
        if (pts.length === 1) ctx.lineTo(pts[0].x+.1,pts[0].y+.1);
        ctx.stroke();
      }
    } else if (obj.type === "shape") {
      const x=obj.x,y=obj.y,w=obj.w,h=obj.h;
      ctx.beginPath();
      if (obj.shape === "rect") ctx.rect(x,y,w,h);
      else if (obj.shape === "ellipse") ctx.ellipse(x+w/2,y+h/2,Math.max(1,Math.abs(w/2)),Math.max(1,Math.abs(h/2)),0,0,Math.PI*2);
      else {
        ctx.moveTo(x,y); ctx.lineTo(x+w,y+h);
        if (obj.shape === "arrow") {
          const angle=Math.atan2(h,w), len=14+ctx.lineWidth*2;
          ctx.lineTo(x+w-len*Math.cos(angle-.45),y+h-len*Math.sin(angle-.45));
          ctx.moveTo(x+w,y+h);
          ctx.lineTo(x+w-len*Math.cos(angle+.45),y+h-len*Math.sin(angle+.45));
        }
      }
      ctx.stroke();
    } else if (obj.type === "sticky") {
      ctx.fillStyle = colorFor(obj); ctx.strokeStyle = "#D1B85C"; ctx.lineWidth=1;
      ctx.beginPath(); ctx.roundRect(obj.x,obj.y,obj.w||220,obj.h||140,8); ctx.fill(); ctx.stroke();
      ctx.fillStyle = "#273142";
      wrapText(obj.text,obj.x+12,obj.y+28,Math.max(40,(obj.w||220)-24),24,"18px sans-serif");
    } else if (obj.type === "text") {
      ctx.fillStyle = colorFor(obj);
      wrapText(obj.text,obj.x,obj.y,Math.max(100,1200-obj.x),Number(obj.fontSize||24)*1.3,Number(obj.fontSize||24)+"px sans-serif");
    }
    ctx.restore();
  };
  const redraw = () => {
    drawBackground();
    objects().forEach(drawObject);
    if (wb.selected) {
      const obj=objects().find(o=>o.id===wb.selected);
      if (obj) {
        const b=bounds(obj);
        ctx.save(); ctx.strokeStyle="#477ED1"; ctx.lineWidth=2; ctx.setLineDash([7,5]);
        ctx.strokeRect(b.x-5,b.y-5,b.w+10,b.h+10); ctx.restore();
      }
    }
  };
  const pointFromEvent = (e) => {
    const r=canvas.getBoundingClientRect();
    return {x:(e.clientX-r.left)*1200/r.width,y:(e.clientY-r.top)*800/r.height};
  };
  const objectAt = (p) => {
    const list=objects();
    for (let i=list.length-1;i>=0;i--) {
      const b=bounds(list[i]);
      if (p.x>=b.x-7 && p.x<=b.x+b.w+7 && p.y>=b.y-7 && p.y<=b.y+b.h+7) return list[i];
    }
    return null;
  };
  const removeSelected = () => {
    if (!wb.selected) return;
    snapshot(); wb.page.objects=objects().filter(o=>o.id!==wb.selected);
    wb.selected=null; redraw(); emit(); status("Object deleted");
  };
  const chooseTool = (tool) => {
    wb.tool=tool;
    root.querySelectorAll("[data-tool]").forEach(b=>b.classList.toggle("active",b.dataset.tool===tool));
    canvas.style.cursor=tool==="select"?"default":tool==="text"||tool==="sticky"?"text":"crosshair";
  };
  const undo = () => {
    if (!wb.history.length) return;
    wb.future.push(clone(wb.page)); wb.page=wb.history.pop(); wb.selected=null; redraw(); emit(); status("Undo");
  };
  const redo = () => {
    if (!wb.future.length) return;
    wb.history.push(clone(wb.page)); wb.page=wb.future.pop(); wb.selected=null; redraw(); emit(); status("Redo");
  };
  const addText = (p, sticky) => {
    const text=window.prompt(sticky?"Sticky note text":"Text");
    if (text === null || !text.trim()) return;
    snapshot();
    if (sticky) objects().push({id:uid(),type:"sticky",x:p.x,y:p.y,w:230,h:140,text:text.slice(0,5000),color:"#F8E7A1"});
    else objects().push({id:uid(),type:"text",x:p.x,y:p.y,text:text.slice(0,5000),color:wb.color,fontSize:24});
    wb.selected=objects()[objects().length-1].id; redraw(); emit();
  };
  const download = (blob, name) => {
    const url=URL.createObjectURL(blob), a=document.createElement("a");
    a.href=url; a.download=name; a.click(); setTimeout(()=>URL.revokeObjectURL(url),1500);
  };

  if (!root.__vocogniWhiteboardListeners) {
    root.__vocogniWhiteboardListeners = true;
    root.querySelectorAll("[data-tool]").forEach(button=>button.addEventListener("click",()=>chooseTool(button.dataset.tool)));
    colorInput.addEventListener("input",()=>{wb.color=colorInput.value;});
    widthInput.addEventListener("input",()=>{wb.width=Number(widthInput.value);});
    root.querySelectorAll("[data-action]").forEach(button=>button.addEventListener("click",()=>{
      const action=button.dataset.action;
      if (action==="undo") undo();
      else if (action==="redo") redo();
      else if (action==="delete") removeSelected();
      else if (action==="clear") {
        if (!objects().length || !window.confirm("Clear every object from this page?")) return;
        snapshot(); wb.page.objects=[]; wb.selected=null; redraw(); emit(); status("Page cleared");
      } else if (action==="png") {
        canvas.toBlob(blob=>{if(blob) download(blob,"vocogni-whiteboard.png");});
      } else if (action==="json") {
        download(new Blob([JSON.stringify(wb.page,null,2)],{type:"application/json"}),"vocogni-whiteboard-page.json");
      } else if (action==="pdf") {
        const popup=window.open("","_blank");
        if (!popup) { status("Allow pop-ups to print or save as PDF"); return; }
        const image=canvas.toDataURL("image/png");
        popup.document.write("<!doctype html><html><head><title>Vocogni Whiteboard</title><style>@page{size:landscape;margin:10mm}body{margin:0}img{width:100%;height:auto;object-fit:contain}</style></head><body><img alt='Vocogni whiteboard' src='"+image+"'><script>window.onload=()=>{window.print()}<\/script></body></html>");
        popup.document.close();
      }
    }));
    canvas.addEventListener("pointerdown",e=>{
      e.preventDefault(); canvas.setPointerCapture(e.pointerId);
      const p=pointFromEvent(e), tool=wb.tool;
      if (tool==="text" || tool==="sticky") { addText(p,tool==="sticky"); return; }
      if (tool==="select") {
        const hit=objectAt(p); wb.selected=hit?hit.id:null;
        if (hit) {
          snapshot();
          wb.dragging={id:hit.id,start:p,original:clone(hit),moved:false};
        }
        redraw(); return;
      }
      if (tool==="eraser") {
        const hit=objectAt(p);
        if (hit) { snapshot(); wb.page.objects=objects().filter(o=>o.id!==hit.id); wb.dirty=true; }
        redraw(); wb.drawing={type:"eraser",changed:!!hit}; return;
      }
      snapshot();
      if (tool==="pen" || tool==="highlighter") {
        const stroke={id:uid(),type:"stroke",points:[p],color:wb.color,width:wb.width,tool};
        objects().push(stroke); wb.drawing={type:"stroke",id:stroke.id};
      } else {
        const shape={id:uid(),type:"shape",shape:tool==="rect"?"rect":tool==="ellipse"?"ellipse":"arrow",x:p.x,y:p.y,w:0,h:0,color:wb.color,width:wb.width};
        objects().push(shape); wb.drawing={type:"shape",id:shape.id,start:p};
      }
      redraw();
    });
    canvas.addEventListener("pointermove",e=>{
      if (!wb.drawing && !wb.dragging) return;
      const p=pointFromEvent(e);
      if (wb.drawing?.type==="stroke") {
        const obj=objects().find(o=>o.id===wb.drawing.id); if(obj) obj.points.push(p);
        redraw();
      } else if (wb.drawing?.type==="shape") {
        const obj=objects().find(o=>o.id===wb.drawing.id);
        if(obj){obj.w=p.x-wb.drawing.start.x;obj.h=p.y-wb.drawing.start.y;}
        redraw();
      } else if (wb.drawing?.type==="eraser") {
        const hit=objectAt(p);
        if(hit){wb.page.objects=objects().filter(o=>o.id!==hit.id);wb.drawing.changed=true;redraw();}
      } else if (wb.dragging) {
        const hit=objects().find(o=>o.id===wb.dragging.id);
        if(hit){
          const dx=p.x-wb.dragging.start.x, dy=p.y-wb.dragging.start.y;
          const original=wb.dragging.original;
          if(hit.type==="stroke") hit.points=original.points.map(pt=>({x:pt.x+dx,y:pt.y+dy}));
          else {hit.x=original.x+dx;hit.y=original.y+dy;}
          wb.dragging.moved=wb.dragging.moved||Math.abs(dx)+Math.abs(dy)>0;
          redraw();
        }
      }
    });
    const finish = () => {
      let changed=false;
      if (wb.drawing) {
        changed=wb.drawing.type!=="eraser" || wb.drawing.changed;
        if(wb.drawing.type==="shape"){
          const obj=objects().find(o=>o.id===wb.drawing.id);
          if(obj && Math.abs(obj.w)<4 && Math.abs(obj.h)<4) wb.page.objects=objects().filter(o=>o.id!==obj.id);
        }
      }
      if (wb.dragging && wb.dragging.moved) changed=true;
      wb.drawing=null; wb.dragging=null;
      redraw();
      if(changed) emit();
    };
    canvas.addEventListener("pointerup",finish);
    canvas.addEventListener("pointercancel",finish);
    root.addEventListener("keydown",e=>{
      if((e.ctrlKey||e.metaKey)&&e.key.toLowerCase()==="z"){e.preventDefault();undo();}
      else if((e.ctrlKey||e.metaKey)&&(e.key.toLowerCase()==="y"||(e.shiftKey&&e.key.toLowerCase()==="z"))){e.preventDefault();redo();}
      else if((e.key==="Delete"||e.key==="Backspace") && wb.selected){e.preventDefault();removeSelected();}
    });
  }
  redraw();
}
"""

_WHITEBOARD_COMPONENT = st.components.v2.component(
    name="vocogni_notes_whiteboard",
    html=HTML,
    css=CSS,
    js=JS,
)


def _now() -> str:
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M")


def _mark_changed() -> None:
    state.mark_persistent_dirty()


def _on_page_change(board_id: str, page_id: str, component_key: str) -> None:
    """Accept a completed frontend edit and mark the learner bundle dirty."""
    component_state = st.session_state.get(component_key, {})
    if not isinstance(component_state, dict):
        return
    incoming = whiteboard_data.sanitize_page(component_state.get("page"))
    if incoming is None or incoming.get("id") != page_id:
        return
    board = next((item for item in st.session_state.whiteboards if item.get("id") == board_id), None)
    if board is None:
        return
    target = next((item for item in board["pages"] if item.get("id") == page_id), None)
    if target is None or target == incoming:
        return
    target.clear()
    target.update(incoming)
    board["updated_at"] = _now()
    _mark_changed()


def _board_by_id(board_id: str) -> dict[str, Any] | None:
    return next((b for b in st.session_state.whiteboards if b.get("id") == board_id), None)


def _page_by_id(board: dict[str, Any], page_id: str) -> dict[str, Any] | None:
    return next((p for p in board.get("pages", []) if p.get("id") == page_id), None)


def _create_board_form() -> None:
    with st.expander("＋ Create a whiteboard", expanded=not st.session_state.whiteboards):
        folders = st.session_state.note_folders
        folder_ids = [None] + [f.get("id") for f in folders]
        folder_labels = ["Unfiled"] + [str(f.get("name", "Folder")) for f in folders]
        with st.form("create_whiteboard_form", clear_on_submit=True):
            title = st.text_input("Whiteboard title", placeholder="e.g. Quadratics visual map")
            template = st.selectbox("Start with", ["Blank", "Graph paper", "Coordinate plane", "Mind map", "Flowchart"])
            folder_label = st.selectbox("Folder", folder_labels)
            submitted = st.form_submit_button("Create whiteboard", type="primary")
        if submitted:
            if len(st.session_state.whiteboards) >= whiteboard_data.MAX_BOARDS:
                st.error("You have reached the whiteboard limit. Export an old board before creating another.")
                return
            folder_id = folder_ids[folder_labels.index(folder_label)]
            board = whiteboard_data.create_board(title=title, folder_id=folder_id, template=template)
            st.session_state.whiteboards.append(board)
            st.session_state.selected_whiteboard_id = board["id"]
            st.session_state.selected_whiteboard_page_id = board["pages"][0]["id"]
            _mark_changed()
            st.rerun()


def render() -> None:
    """Render Notes' Whiteboard workspace."""
    st.markdown("### Whiteboard")
    st.caption("Sketch concepts, map ideas, and work through problems on a canvas. Changes are sent to Vocogni after each completed edit.")
    _create_board_form()
    boards = st.session_state.whiteboards
    if not boards:
        st.info("Create a whiteboard to begin. Your editable objects will be stored with your Vocogni learner data.")
        return

    labels = {b["id"]: b["title"] for b in boards}
    board_ids = [b["id"] for b in boards]
    selected_board_id = st.session_state.get("selected_whiteboard_id")
    if selected_board_id not in board_ids:
        selected_board_id = board_ids[0]
        st.session_state.selected_whiteboard_id = selected_board_id
    selected_board = _board_by_id(selected_board_id)
    if selected_board is None:
        st.error("This whiteboard could not be loaded.")
        return

    left, mid, right = st.columns([3, 1, 1])
    with left:
        chosen_id = st.selectbox(
            "Your whiteboards", board_ids,
            index=board_ids.index(selected_board_id),
            format_func=lambda value: labels.get(value, "Whiteboard"),
            key="notes_whiteboard_picker",
        )
        if chosen_id != selected_board_id:
            st.session_state.selected_whiteboard_id = chosen_id
            target_board = _board_by_id(chosen_id)
            st.session_state.selected_whiteboard_page_id = target_board["pages"][0]["id"] if target_board else None
            st.rerun()
    with mid:
        if st.button("Rename", key=f"rename_whiteboard_{selected_board_id}"):
            st.session_state[f"renaming_whiteboard_{selected_board_id}"] = True
    with right:
        if st.button("Delete", key=f"delete_whiteboard_{selected_board_id}"):
            st.session_state[f"confirm_delete_whiteboard_{selected_board_id}"] = True

    if st.session_state.get(f"renaming_whiteboard_{selected_board_id}", False):
        with st.form(f"rename_whiteboard_form_{selected_board_id}"):
            new_title = st.text_input("New title", value=selected_board.get("title", ""))
            save_title = st.form_submit_button("Save title")
        if save_title:
            if new_title.strip():
                selected_board["title"] = new_title.strip()[:100]
                selected_board["updated_at"] = _now()
                _mark_changed()
            st.session_state[f"renaming_whiteboard_{selected_board_id}"] = False
            st.rerun()

    if st.session_state.get(f"confirm_delete_whiteboard_{selected_board_id}", False):
        st.warning(f"Delete **{selected_board.get('title', 'this whiteboard')}** and all its pages? This cannot be undone.")
        confirm_col, cancel_col = st.columns(2)
        with confirm_col:
            if st.button("Confirm delete", type="primary", key=f"confirm_delete_{selected_board_id}"):
                st.session_state.whiteboards = [b for b in st.session_state.whiteboards if b.get("id") != selected_board_id]
                st.session_state.selected_whiteboard_id = st.session_state.whiteboards[0]["id"] if st.session_state.whiteboards else None
                current = _board_by_id(st.session_state.selected_whiteboard_id) if st.session_state.selected_whiteboard_id else None
                st.session_state.selected_whiteboard_page_id = current["pages"][0]["id"] if current else None
                _mark_changed()
                st.rerun()
        with cancel_col:
            if st.button("Cancel", key=f"cancel_delete_{selected_board_id}"):
                st.session_state[f"confirm_delete_whiteboard_{selected_board_id}"] = False
                st.rerun()

    page_ids = [p["id"] for p in selected_board["pages"]]
    selected_page_id = st.session_state.get("selected_whiteboard_page_id")
    if selected_page_id not in page_ids:
        selected_page_id = page_ids[0]
        st.session_state.selected_whiteboard_page_id = selected_page_id
    page_left, page_add, page_remove = st.columns([4, 1, 1])
    with page_left:
        selected_page_id = st.selectbox(
            "Page", page_ids,
            index=page_ids.index(selected_page_id),
            format_func=lambda value: next((p.get("title", "Page") for p in selected_board["pages"] if p["id"] == value), "Page"),
            key=f"whiteboard_page_picker_{selected_board_id}",
        )
        st.session_state.selected_whiteboard_page_id = selected_page_id
    with page_add:
        if st.button("＋ Page", key=f"add_whiteboard_page_{selected_board_id}", disabled=len(selected_board["pages"]) >= whiteboard_data.MAX_PAGES_PER_BOARD):
            new_page = whiteboard_data.create_page(f"Page {len(selected_board['pages']) + 1}", "grid")
            selected_board["pages"].append(new_page)
            st.session_state.selected_whiteboard_page_id = new_page["id"]
            selected_page_id = new_page["id"]
            selected_board["updated_at"] = _now()
            _mark_changed()
            st.rerun()
    with page_remove:
        if st.button("Remove page", key=f"remove_whiteboard_page_{selected_board_id}", disabled=len(selected_board["pages"]) <= 1):
            selected_board["pages"] = [p for p in selected_board["pages"] if p["id"] != selected_page_id]
            st.session_state.selected_whiteboard_page_id = selected_board["pages"][0]["id"]
            selected_board["updated_at"] = _now()
            _mark_changed()
            st.rerun()

    page = _page_by_id(selected_board, selected_page_id)
    if page is None:
        st.error("This page could not be loaded.")
        return

    settings_col, export_col = st.columns([3, 2])
    with settings_col:
        background_label = st.selectbox(
            "Canvas background", ["Plain", "Graph grid", "Dots", "Dark"],
            index={"plain": 0, "grid": 1, "dots": 2, "dark": 3}.get(page.get("background"), 1),
            key=f"whiteboard_background_{selected_board_id}_{selected_page_id}",
        )
        if st.button("Apply background", key=f"apply_background_{selected_board_id}_{selected_page_id}"):
            page["background"] = {"Plain": "plain", "Graph grid": "grid", "Dots": "dots", "Dark": "dark"}[background_label]
            selected_board["updated_at"] = _now()
            _mark_changed()
            st.rerun()
    with export_col:
        st.download_button(
            "Download editable board (.json)",
            data=json.dumps(selected_board, ensure_ascii=False, indent=2),
            file_name=(selected_board.get("title", "whiteboard").replace("/", "-").replace("\\", "-") + ".json"),
            mime="application/json",
            key=f"download_whiteboard_{selected_board_id}",
            use_container_width=True,
        )
        st.download_button(
            "Download page as SVG",
            data=whiteboard_data.page_to_svg(page),
            file_name=f"vocogni-page-{page.get('title', 'page').replace('/', '-')}.svg",
            mime="image/svg+xml",
            key=f"download_whiteboard_svg_{selected_board_id}_{selected_page_id}",
            use_container_width=True,
        )

    component_key = f"whiteboard_canvas_{selected_board_id}_{selected_page_id}"
    _WHITEBOARD_COMPONENT(
        data={"page": page},
        default={"page": page},
        key=component_key,
        on_page_change=lambda: _on_page_change(selected_board_id, selected_page_id, component_key),
    )
    st.caption("Export: PNG creates an image, SVG keeps shapes and text vector-based, and Print / PDF opens your browser's print dialog.")
