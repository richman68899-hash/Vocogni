(function () {
  "use strict";
  const send = (type, extra) => window.parent.postMessage(Object.assign({isStreamlitMessage:true,type}, extra || {}), "*");
  const $ = (selector) => document.querySelector(selector);
  const canvas = $("#canvas");
  const ctx = canvas.getContext("2d");
  const stage = $("#stage");
  const state = {
    board:null, pageId:null, tool:"select", color:"#273142", width:4, selected:null,
    drawing:null, dragging:null, handStart:null, history:[], future:[],
    pending:null, pendingRev:0, ack_event_id:null, initialized:false
  };
  const clone = value => JSON.parse(JSON.stringify(value));
  const uid = () => (window.crypto && window.crypto.randomUUID) ? window.crypto.randomUUID() : "wb-" + Date.now() + "-" + Math.random().toString(16).slice(2);
  const activePage = () => state.board && state.board.pages.find(p => p.id === state.pageId);
  const objects = () => { const p=activePage(); if (!p) return []; if (!Array.isArray(p.objects)) p.objects=[]; return p.objects; };
  const status = text => { $("#status").textContent = text; };
  function currentPageIndex() { return Math.max(0, state.board.pages.findIndex(p=>p.id===state.pageId)); }
  function updatePageLabel() { $("#page-label").textContent = "Page " + (currentPageIndex()+1) + " / " + state.board.pages.length; }

  function postPending() {
    if (!state.pending || !state.board) return;
    send("streamlit:setComponentValue", {value:clone(state.pending), dataType:"json"});
    status("Saving…");
  }
  function changed() {
    if (!state.board) return;
    state.pendingRev += 1;
    const board = clone(state.board);
    state.pending = {
      event_id: uid(), pendingRev: state.pendingRev,
      board_id: board.id, page_id: state.pageId, board: board
    };
    postPending();
  }
  function snapshot() {
    state.history.push(clone(state.board));
    if (state.history.length > 50) state.history.shift();
    state.future = [];
  }
  function undoFn() {
    if (!state.history.length) return;
    state.future.push(clone(state.board));
    state.board = state.history.pop();
    state.pageId = state.board.pages.some(p=>p.id===state.pageId) ? state.pageId : state.board.pages[0].id;
    state.selected=null; renderCanvas(); changed(); status("Undo queued for save");
  }
  function redoFn() {
    if (!state.future.length) return;
    state.history.push(clone(state.board));
    state.board = state.future.pop();
    state.pageId = state.board.pages.some(p=>p.id===state.pageId) ? state.pageId : state.board.pages[0].id;
    state.selected=null; renderCanvas(); changed(); status("Redo queued for save");
  }
  function bounds(obj) {
    if (obj.type === "stroke" && obj.points && obj.points.length) {
      const xs=obj.points.map(p=>p.x), ys=obj.points.map(p=>p.y);
      return {x:Math.min(...xs)-8,y:Math.min(...ys)-8,w:Math.max(...xs)-Math.min(...xs)+16,h:Math.max(...ys)-Math.min(...ys)+16};
    }
    if (obj.type==="text") return {x:obj.x,y:obj.y-(obj.fontSize||24),w:Math.max(50,String(obj.text||"").length*(obj.fontSize||24)*.6),h:(obj.fontSize||24)*1.5};
    return {x:Math.min(obj.x,obj.x+(obj.w||1)),y:Math.min(obj.y,obj.y+(obj.h||1)),w:Math.abs(obj.w||1),h:Math.abs(obj.h||1)};
  }
  function drawBackground() {
    const page=activePage(); if (!page) return;
    ctx.clearRect(0,0,1200,800);
    ctx.fillStyle=page.background==="dark"?"#20242b":"#ffffff"; ctx.fillRect(0,0,1200,800);
    if(page.background==="grid"){
      ctx.strokeStyle="#e7eaf0";ctx.lineWidth=1;
      for(let x=0;x<=1200;x+=40){ctx.beginPath();ctx.moveTo(x,0);ctx.lineTo(x,800);ctx.stroke();}
      for(let y=0;y<=800;y+=40){ctx.beginPath();ctx.moveTo(0,y);ctx.lineTo(1200,y);ctx.stroke();}
    } else if(page.background==="dots"){
      ctx.fillStyle="#d7dbe3";
      for(let x=20;x<1200;x+=40)for(let y=20;y<800;y+=40){ctx.beginPath();ctx.arc(x,y,1.4,0,Math.PI*2);ctx.fill();}
    }
  }
  function wrap(text,x,y,maxWidth,lineHeight,font) {
    ctx.font=font;
    String(text||"").split("\n").forEach(raw=>{
      let line="";
      for(const word of raw.split(/\s+/)){
        const candidate=line?line+" "+word:word;
        if(line&&ctx.measureText(candidate).width>maxWidth){ctx.fillText(line,x,y);y+=lineHeight;line=word;}
        else line=candidate;
      }
      ctx.fillText(line,x,y);y+=lineHeight;
    });
  }
  function drawObject(obj) {
    ctx.save();ctx.strokeStyle=obj.color||"#273142";ctx.fillStyle=obj.color||"#273142";
    ctx.lineWidth=Math.max(1,Number(obj.width||3));ctx.lineCap="round";ctx.lineJoin="round";
    if(obj.type==="stroke"){
      ctx.globalAlpha=obj.tool==="highlighter"?.32:1;
      const pts=obj.points||[];
      if(pts.length){ctx.beginPath();ctx.moveTo(pts[0].x,pts[0].y);pts.slice(1).forEach(p=>ctx.lineTo(p.x,p.y));ctx.stroke();}
    }else if(obj.type==="shape"){
      const {x,y,w,h}=obj;ctx.beginPath();
      if(obj.shape==="rect")ctx.rect(Math.min(x,x+w),Math.min(y,y+h),Math.abs(w),Math.abs(h));
      else if(obj.shape==="ellipse")ctx.ellipse(x+w/2,y+h/2,Math.max(1,Math.abs(w/2)),Math.max(1,Math.abs(h/2)),0,0,Math.PI*2);
      else if(obj.shape==="triangle"){ctx.moveTo(x+w/2,y);ctx.lineTo(x+w,y+h);ctx.lineTo(x,y+h);ctx.closePath();}
      else{
        ctx.moveTo(x,y);ctx.lineTo(x+w,y+h);
        if(obj.shape==="arrow"){const a=Math.atan2(h,w),len=16;ctx.moveTo(x+w,y+h);ctx.lineTo(x+w-len*Math.cos(a-.48),y+h-len*Math.sin(a-.48));ctx.moveTo(x+w,y+h);ctx.lineTo(x+w-len*Math.cos(a+.48),y+h-len*Math.sin(a+.48));}
      }ctx.stroke();
    }else if(obj.type==="sticky"){
      ctx.fillStyle=obj.color||"#f8e7a1";ctx.strokeStyle="#d1b85c";ctx.lineWidth=1;
      ctx.beginPath();ctx.roundRect(obj.x,obj.y,obj.w||230,obj.h||140,8);ctx.fill();ctx.stroke();
      ctx.fillStyle="#273142";wrap(obj.text,obj.x+12,obj.y+28,(obj.w||230)-24,24,"18px sans-serif");
    }else if(obj.type==="text"){
      ctx.fillStyle=obj.color||"#273142";const size=Number(obj.fontSize||24);
      wrap(obj.text,obj.x,obj.y,Math.max(70,1200-obj.x),size*1.3,size+"px sans-serif");
    }ctx.restore();
  }
  function renderCanvas() {
    if(!state.board||!activePage())return;
    drawBackground();objects().forEach(drawObject);
    if(state.selected){const obj=objects().find(o=>o.id===state.selected);if(obj){const b=bounds(obj);ctx.save();ctx.strokeStyle="#477ed1";ctx.lineWidth=2;ctx.setLineDash([7,5]);ctx.strokeRect(b.x-5,b.y-5,b.w+10,b.h+10);ctx.setLineDash([]);if(obj.type==="sticky"||(obj.type==="shape"&&["rect","ellipse","triangle"].includes(obj.shape))){ctx.fillStyle="#ffffff";ctx.strokeStyle="#477ed1";ctx.fillRect(b.x+b.w-5,b.y+b.h-5,10,10);ctx.strokeRect(b.x+b.w-5,b.y+b.h-5,10,10);}ctx.restore();}}
    $("#background").value=activePage().background||"grid";updatePageLabel();
  }
  function position(e){const r=canvas.getBoundingClientRect();return{x:(e.clientX-r.left)*1200/r.width,y:(e.clientY-r.top)*800/r.height};}
  function objectAt(p){const arr=objects();for(let i=arr.length-1;i>=0;i--){const b=bounds(arr[i]);if(p.x>=b.x-8&&p.x<=b.x+b.w+8&&p.y>=b.y-8&&p.y<=b.y+b.h+8)return arr[i];}return null;}
  function chooseTool(tool){state.tool=tool;document.querySelectorAll("[data-tool]").forEach(b=>{const active=b.dataset.tool===tool;b.classList.toggle("active",active);b.setAttribute("aria-pressed",String(active));});}
  function addText(p,sticky){const value=window.prompt(sticky?"Sticky note text":"Text");if(value===null||!value.trim())return;snapshot();const o=sticky?{id:uid(),type:"sticky",x:p.x,y:p.y,w:230,h:140,text:value.slice(0,5000),color:"#f8e7a1"}:{id:uid(),type:"text",x:p.x,y:p.y,text:value.slice(0,5000),color:state.color,fontSize:24};objects().push(o);state.selected=o.id;renderCanvas();changed();}
  function movePage(step){const idx=currentPageIndex(),next=idx+step;if(next>=0&&next<state.board.pages.length){state.pageId=state.board.pages[next].id;state.selected=null;renderCanvas();changed();}}
  function duplicateSelected(){const o=objects().find(o=>o.id===state.selected);if(!o)return;snapshot();const copy=clone(o);copy.id=uid();if(copy.type==="stroke")copy.points=copy.points.map(p=>({x:p.x+24,y:p.y+24}));else{copy.x+=24;copy.y+=24;}objects().push(copy);state.selected=copy.id;renderCanvas();changed();}
  function deleteSelected(){if(!state.selected)return;snapshot();state.board.pages[currentPageIndex()].objects=objects().filter(o=>o.id!==state.selected);state.selected=null;renderCanvas();changed();}
  function svgEscape(text){return String(text||"").replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;");}
  function exportSvg(){
    const p=activePage();if(!p)return "";
    const parts=['<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="800" viewBox="0 0 1200 800">'];
    parts.push('<rect width="1200" height="800" fill="'+(p.background==="dark"?"#20242b":"#fff")+'"/>');
    if(p.background==="grid"){for(let x=0;x<=1200;x+=40)parts.push('<path d="M'+x+' 0 V800" stroke="#e7eaf0"/>');for(let y=0;y<=800;y+=40)parts.push('<path d="M0 '+y+' H1200" stroke="#e7eaf0"/>');}
    for(const o of p.objects||[]){
      const c=o.color||"#273142",w=o.width||3;
      if(o.type==="stroke"&&o.points&&o.points.length){const d=o.points.map((pt,i)=>(i?"L":"M")+pt.x+" "+pt.y).join(" ");parts.push('<path d="'+d+'" fill="none" stroke="'+c+'" stroke-width="'+w+'" stroke-linecap="round"'+(o.tool==="highlighter"?' opacity=".32"':'')+'/>');}
      else if(o.type==="shape"){const x=o.x,y=o.y,ww=o.w,hh=o.h;if(o.shape==="rect")parts.push('<rect x="'+Math.min(x,x+ww)+'" y="'+Math.min(y,y+hh)+'" width="'+Math.abs(ww)+'" height="'+Math.abs(hh)+'" fill="none" stroke="'+c+'" stroke-width="'+w+'"/>');else if(o.shape==="ellipse")parts.push('<ellipse cx="'+(x+ww/2)+'" cy="'+(y+hh/2)+'" rx="'+Math.abs(ww/2)+'" ry="'+Math.abs(hh/2)+'" fill="none" stroke="'+c+'" stroke-width="'+w+'"/>');else if(o.shape==="triangle")parts.push('<path d="M'+(x+ww/2)+' '+y+' L'+(x+ww)+' '+(y+hh)+' L'+x+' '+(y+hh)+' Z" fill="none" stroke="'+c+'" stroke-width="'+w+'"/>');else parts.push('<path d="M'+x+' '+y+' L'+(x+ww)+' '+(y+hh)+'" fill="none" stroke="'+c+'" stroke-width="'+w+'"/>');}
      else if(o.type==="sticky"){parts.push('<rect x="'+o.x+'" y="'+o.y+'" width="'+(o.w||230)+'" height="'+(o.h||140)+'" rx="8" fill="'+c+'"/>');parts.push('<text x="'+(o.x+12)+'" y="'+(o.y+30)+'" fill="#273142" font-size="18">'+svgEscape(o.text)+'</text>');}
      else if(o.type==="text")parts.push('<text x="'+o.x+'" y="'+o.y+'" fill="'+c+'" font-size="'+(o.fontSize||24)+'">'+svgEscape(o.text)+'</text>');
    }parts.push("</svg>");return parts.join("\n");
  }
  function download(blob,name){const url=URL.createObjectURL(blob),a=document.createElement("a");a.href=url;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(url),1200);}
  function pdf(){const popup=window.open("","_blank");if(!popup){status("Allow pop-ups to print or save as PDF.");return;}const url=canvas.toDataURL("image/png");popup.document.write("<!doctype html><html><head><title>Vocogni whiteboard</title><style>@page{size:landscape;margin:10mm}body{margin:0}img{width:100%;height:auto}</style></head><body><img alt='Whiteboard' src='"+url+"'><script>window.onload=()=>window.print()<\/script></body></html>");popup.document.close();}
  function wireControls(){
    document.querySelectorAll("[data-tool]").forEach(b=>b.addEventListener("click",()=>chooseTool(b.dataset.tool)));
    $("#color").addEventListener("input",e=>state.color=e.target.value);
    $("#width").addEventListener("input",e=>state.width=Number(e.target.value));
    $("#undo").addEventListener("click",undoFn);$("#redo").addEventListener("click",redoFn);
    $("#duplicate").addEventListener("click",duplicateSelected);$("#delete-selected").addEventListener("click",deleteSelected);
    $("#clear-page").addEventListener("click",()=>{if(!objects().length||!window.confirm("Clear every object from this page?"))return;snapshot();activePage().objects=[];state.selected=null;renderCanvas();changed();});
    $("#zoom").addEventListener("change",e=>{canvas.style.width=e.target.value+"%";});
    $("#save-now").addEventListener("click",()=>{if(state.pending)postPending();else changed();});
    $("#previous-page").addEventListener("click",()=>movePage(-1));$("#next-page").addEventListener("click",()=>movePage(1));
    $("#new-page").addEventListener("click",()=>{if(state.board.pages.length>=40){status("Page limit reached");return;}snapshot();const n=state.board.pages.length+1;const page={id:uid(),title:"Page "+n,width:1200,height:800,background:"grid",objects:[]};state.board.pages.push(page);state.pageId=page.id;state.selected=null;renderCanvas();changed();});
    $("#duplicate-page").addEventListener("click",()=>{if(state.board.pages.length>=40){status("Page limit reached");return;}snapshot();const copy=clone(activePage());copy.id=uid();copy.title="Page "+(state.board.pages.length+1);state.board.pages.splice(currentPageIndex()+1,0,copy);state.pageId=copy.id;state.selected=null;renderCanvas();changed();});
    $("#delete-page").addEventListener("click",()=>{if(state.board.pages.length<=1){status("A board must have at least one page");return;}if(!window.confirm("Delete this page?"))return;snapshot();const idx=currentPageIndex();state.board.pages.splice(idx,1);state.pageId=state.board.pages[Math.max(0,idx-1)].id;state.selected=null;renderCanvas();changed();});
    $("#background").addEventListener("change",e=>{snapshot();activePage().background=e.target.value;renderCanvas();changed();});
    $("#export-png").addEventListener("click",()=>canvas.toBlob(blob=>{if(blob)download(blob,"vocogni-whiteboard.png");}));
    $("#export-json").addEventListener("click",()=>download(new Blob([JSON.stringify(state.board,null,2)],{type:"application/json"}),"vocogni-whiteboard.json"));
    $("#export-pdf").addEventListener("click",pdf);
    canvas.addEventListener("pointerdown",e=>{
      e.preventDefault();canvas.focus();const p=position(e);canvas.setPointerCapture(e.pointerId);
      if(state.tool==="hand"){state.handStart={x:e.clientX,y:e.clientY,left:stage.scrollLeft,top:stage.scrollTop};return;}
      if(state.tool==="text"||state.tool==="sticky"){addText(p,state.tool==="sticky");return;}
      if(state.tool==="select"){const hit=objectAt(p);state.selected=hit?hit.id:null;if(hit){const b=bounds(hit);const canResize=hit.type==="sticky"||(hit.type==="shape"&&["rect","ellipse","triangle"].includes(hit.shape));const resize=canResize&&p.x>=b.x+b.w-18&&p.y>=b.y+b.h-18;state.dragging={id:hit.id,start:p,original:clone(hit),moved:false,snapshotted:false,resize:!!resize,resizeOrigin:b};}renderCanvas();return;}
      if(state.tool==="eraser"){const hit=objectAt(p);if(hit){snapshot();state.board.pages[currentPageIndex()].objects=objects().filter(o=>o.id!==hit.id);state.drawing={type:"eraser",changed:true};renderCanvas();}else state.drawing={type:"eraser",changed:false};return;}
      snapshot();if(state.tool==="pen"||state.tool==="highlighter"){const obj={id:uid(),type:"stroke",points:[p],color:state.color,width:state.width,tool:state.tool};objects().push(obj);state.drawing={type:"stroke",id:obj.id};}else{const shape=state.tool==="rectangle"?"rect":state.tool==="ellipse"?"ellipse":state.tool==="triangle"?"triangle":state.tool==="line"?"line":"arrow";const obj={id:uid(),type:"shape",shape,x:p.x,y:p.y,w:0,h:0,color:state.color,width:state.width};objects().push(obj);state.drawing={type:"shape",id:obj.id,start:p};}renderCanvas();
    });
    canvas.addEventListener("pointermove",e=>{
      if(state.handStart){stage.scrollLeft=state.handStart.left-(e.clientX-state.handStart.x);stage.scrollTop=state.handStart.top-(e.clientY-state.handStart.y);return;}
      if(!state.drawing&&!state.dragging)return;const p=position(e);
      if(state.drawing?.type==="stroke"){const obj=objects().find(o=>o.id===state.drawing.id);if(obj)obj.points.push(p);renderCanvas();}
      else if(state.drawing?.type==="shape"){const obj=objects().find(o=>o.id===state.drawing.id);if(obj){obj.w=p.x-state.drawing.start.x;obj.h=p.y-state.drawing.start.y;}renderCanvas();}
      else if(state.drawing?.type==="eraser"){const hit=objectAt(p);if(hit){if(!state.drawing.changed)snapshot();state.board.pages[currentPageIndex()].objects=objects().filter(o=>o.id!==hit.id);state.drawing.changed=true;renderCanvas();}}
      else if(state.dragging){const obj=objects().find(o=>o.id===state.dragging.id);if(obj){const dx=p.x-state.dragging.start.x,dy=p.y-state.dragging.start.y;const orig=state.dragging.original;if(Math.abs(dx)+Math.abs(dy)>0&&!state.dragging.snapshotted){snapshot();state.dragging.snapshotted=true;}if(state.dragging.resize){obj.x=state.dragging.resizeOrigin.x;obj.y=state.dragging.resizeOrigin.y;obj.w=Math.max(20,p.x-obj.x);obj.h=Math.max(20,p.y-obj.y);}else if(obj.type==="stroke")obj.points=orig.points.map(pt=>({x:pt.x+dx,y:pt.y+dy}));else{obj.x=orig.x+dx;obj.y=orig.y+dy;}state.dragging.moved=true;renderCanvas();}}
    });
    const finish=()=>{let save=false;if(state.drawing){save=state.drawing.type!=="eraser"||state.drawing.changed;if(state.drawing.type==="stroke"){const obj=objects().find(o=>o.id===state.drawing.id);if(obj&&obj.points.length===1)obj.points.push({x:obj.points[0].x+0.1,y:obj.points[0].y+0.1});}if(state.drawing.type==="shape"){const obj=objects().find(o=>o.id===state.drawing.id);if(obj&&Math.abs(obj.w)<3&&Math.abs(obj.h)<3)state.board.pages[currentPageIndex()].objects=objects().filter(o=>o.id!==obj.id);}}if(state.dragging&&state.dragging.moved)save=true;state.drawing=null;state.dragging=null;state.handStart=null;renderCanvas();if(save)changed();};
    canvas.addEventListener("pointerup",finish);canvas.addEventListener("pointercancel",finish);
    canvas.addEventListener("keydown",e=>{if((e.ctrlKey||e.metaKey)&&e.key.toLowerCase()==="z"){e.preventDefault();undoFn();}else if((e.ctrlKey||e.metaKey)&&(e.key.toLowerCase()==="y"||(e.shiftKey&&e.key.toLowerCase()==="z"))){e.preventDefault();redoFn();}else if((e.key==="Delete"||e.key==="Backspace")&&state.selected){e.preventDefault();deleteSelected();}});
  }
  window.addEventListener("message",event=>{
    const msg=event.data;if(!msg||msg.type!=="streamlit:render"||!msg.args)return;
    const args=msg.args;
    if(state.pending && args.ack_event_id===state.pending.event_id){state.pending=null;state.board=clone(args.board);state.pageId=args.page_id;state.ack_event_id=args.ack_event_id;status("Saved to Vocogni");}
    else if(!state.pending){state.board=clone(args.board);state.pageId=args.page_id;state.ack_event_id=args.ack_event_id||null;}
    if(!state.board||!Array.isArray(state.board.pages)||!state.board.pages.length){status("No board data received");return;}
    if(!state.board.pages.some(p=>p.id===state.pageId))state.pageId=state.board.pages[0].id;
    if(!state.initialized){wireControls();state.initialized=true;}
    renderCanvas();send("streamlit:setFrameHeight",{height:Math.max(430,document.body.scrollHeight)});
    if(state.pending && args.ack_event_id!==state.pending.event_id)status("Save pending — use Save now to retry if needed.");
  });
  send("streamlit:componentReady",{apiVersion:1});
  send("streamlit:setFrameHeight",{height:500});
})();
