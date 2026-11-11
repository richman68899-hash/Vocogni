"""Self-contained SVG graphs used by the Quadratics and Graphs course.

No image assets or plotting dependencies are required: curves and regions are
computed from the lesson functions and embedded as responsive SVG.
"""
from __future__ import annotations

import html
import math


INK = "#23323D"
MUTED = "#647682"
GRID = "#E5EBEE"
TEAL = "#147D7E"
BLUE = "#3973AC"
AMBER = "#C58A2B"
CORAL = "#C85A4B"
PURPLE = "#7C69A9"
PALE_TEAL = "#B7E0D9"


def _coord(x, low, high, start, span):
    return start + (x - low) / (high - low) * span


def _curve_path(fn, xr, yr, plot, samples=220):
    left, top, width, height = plot
    points = []
    for i in range(samples + 1):
        x = xr[0] + (xr[1] - xr[0]) * i / samples
        try:
            y = float(fn(x))
        except (ValueError, OverflowError, ZeroDivisionError):
            continue
        if not math.isfinite(y):
            continue
        px = _coord(x, xr[0], xr[1], left, width)
        py = _coord(y, yr[1], yr[0], top, height)
        points.append((px, py))
    return " ".join((("M" if i == 0 else "L") + f"{x:.2f},{y:.2f}") for i, (x, y) in enumerate(points))


def _fmt(n):
    if abs(n - round(n)) < 1e-8:
        return str(int(round(n)))
    return f"{n:.1f}".rstrip("0").rstrip(".")


def _chart_svg(title, xr, yr, series, points=None, verticals=None, shades=None, x_label="x", y_label="y"):
    width, height = 760, 430
    left, right, top, bottom = 62, 24, 52, 54
    plot = (left, top, width-left-right, height-top-bottom)
    pl, pt, pw, ph = plot
    px = lambda x: _coord(x, xr[0], xr[1], pl, pw)
    py = lambda y: _coord(y, yr[1], yr[0], pt, ph)
    clip_id = "clip_" + "".join(ch.lower() for ch in title if ch.isalnum())[:24]
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" aria-label="{html.escape(title)}" style="width:100%;height:auto;display:block;background:#FFFFFF;border:1px solid #DEE5E8;border-radius:10px">',
        f'<title>{html.escape(title)}</title>',
        f'<text x="{width/2}" y="27" text-anchor="middle" font-family="Arial,sans-serif" font-size="17" font-weight="600" fill="{INK}">{html.escape(title)}</text>',
        f'<defs><clipPath id="{clip_id}"><rect x="{pl}" y="{pt}" width="{pw}" height="{ph}"/></clipPath></defs>',
    ]
    x_step = 1 if xr[1] - xr[0] <= 8 else 2
    y_step = 1 if yr[1] - yr[0] <= 12 else 2
    start_x = math.ceil(xr[0] / x_step) * x_step
    for x in range(int(start_x), int(xr[1])+1, x_step):
        xx = px(x)
        out.append(f'<line x1="{xx:.2f}" y1="{pt}" x2="{xx:.2f}" y2="{pt+ph}" stroke="{GRID}" stroke-width="1"/>')
        out.append(f'<text x="{xx:.2f}" y="{pt+ph+20}" text-anchor="middle" font-size="11" fill="{MUTED}" font-family="Arial,sans-serif">{_fmt(x)}</text>')
    start_y = math.ceil(yr[0] / y_step) * y_step
    for y in range(int(start_y), int(yr[1])+1, y_step):
        yy = py(y)
        out.append(f'<line x1="{pl}" y1="{yy:.2f}" x2="{pl+pw}" y2="{yy:.2f}" stroke="{GRID}" stroke-width="1"/>')
        if abs(y) > 1e-8:
            out.append(f'<text x="{pl-11}" y="{yy+4:.2f}" text-anchor="end" font-size="11" fill="{MUTED}" font-family="Arial,sans-serif">{_fmt(y)}</text>')
    if xr[0] <= 0 <= xr[1]:
        out.append(f'<line x1="{px(0):.2f}" y1="{pt}" x2="{px(0):.2f}" y2="{pt+ph}" stroke="{MUTED}" stroke-width="1.5"/>')
    if yr[0] <= 0 <= yr[1]:
        out.append(f'<line x1="{pl}" y1="{py(0):.2f}" x2="{pl+pw}" y2="{py(0):.2f}" stroke="{MUTED}" stroke-width="1.5"/>')
    out.append(f'<text x="{pl+pw-4}" y="{height-12}" text-anchor="end" font-family="Arial,sans-serif" font-size="12" fill="{INK}">{html.escape(x_label)}</text>')
    out.append(f'<text x="16" y="{pt+12}" font-family="Arial,sans-serif" font-size="12" fill="{INK}">{html.escape(y_label)}</text>')
    out.append(f'<g clip-path="url(#{clip_id})">')
    for shade in shades or []:
        x0, x1 = shade["x0"], shade["x1"]
        upper, lower = shade["upper"], shade.get("lower", lambda x: 0)
        steps = 100
        top_points = [(px(x0 + (x1-x0)*i/steps), py(upper(x0 + (x1-x0)*i/steps))) for i in range(steps+1)]
        bottom_points = [(px(x0 + (x1-x0)*i/steps), py(lower(x0 + (x1-x0)*i/steps))) for i in reversed(range(steps+1))]
        poly = " ".join(f"{x:.2f},{y:.2f}" for x,y in top_points+bottom_points)
        out.append(f'<polygon points="{poly}" fill="{shade.get("fill", PALE_TEAL)}" fill-opacity="{shade.get("opacity", 0.72)}" stroke="none"/>')
    for line in verticals or []:
        x = line["x"]
        dash = ' stroke-dasharray="6,5"' if line.get("dash") else ""
        out.append(f'<line x1="{px(x):.2f}" y1="{pt}" x2="{px(x):.2f}" y2="{pt+ph}" stroke="{line.get("color", AMBER)}" stroke-width="2"{dash}/>')
    for item in series:
        path = _curve_path(item["fn"], xr, yr, plot)
        dash = ' stroke-dasharray="6,5"' if item.get("dash") else ""
        out.append(f'<path d="{path}" fill="none" stroke="{item.get("color", TEAL)}" stroke-width="{item.get("width", 3)}" stroke-linejoin="round" stroke-linecap="round"{dash}/>')
    for point in points or []:
        cx, cy = px(point["x"]), py(point["y"])
        out.append(f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="4.6" fill="{point.get("color", CORAL)}" stroke="#FFFFFF" stroke-width="1.5"/>')
        dx, dy = point.get("dx", 8), point.get("dy", -8)
        out.append(f'<text x="{cx+dx:.2f}" y="{cy+dy:.2f}" font-family="Arial,sans-serif" font-size="12" font-weight="600" fill="{INK}">{html.escape(point["label"])}</text>')
    out.append("</g>")
    lx, ly = pl+10, 44
    legend_x = lx
    for item in series:
        label = html.escape(item["label"])
        out.append(f'<line x1="{legend_x}" y1="{ly}" x2="{legend_x+23}" y2="{ly}" stroke="{item.get("color", TEAL)}" stroke-width="3"/>')
        out.append(f'<text x="{legend_x+29}" y="{ly+4}" font-family="Arial,sans-serif" font-size="11" fill="{INK}">{label}</text>')
        legend_x += min(215, 37 + 6.5 * len(item["label"]))
    out.append("</svg>")
    return "".join(out)


def _sign_chart_svg():
    width, height = 760, 220
    left, right = 75, 45
    line_y = 115
    x = lambda v: left + (v / 5) * (width-left-right)
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" aria-label="Sign chart for x squared minus 5x plus 6" style="width:100%;height:auto;background:#FFFFFF;border:1px solid #DEE5E8;border-radius:10px">']
    out.append(f'<text x="380" y="27" text-anchor="middle" font-family="Arial,sans-serif" font-size="17" font-weight="600" fill="{INK}">Sign chart: (x − 2)(x − 3)</text>')
    out.append(f'<line x1="{left}" y1="{line_y}" x2="{width-right}" y2="{line_y}" stroke="{MUTED}" stroke-width="2"/>')
    for xx in [left+8, x(2), x(3), width-right-8]:
        out.append(f'<line x1="{xx}" y1="{line_y-7}" x2="{xx}" y2="{line_y+7}" stroke="{MUTED}" stroke-width="2"/>')
    out.append(f'<circle cx="{x(2)}" cy="{line_y}" r="6" fill="#FFFFFF" stroke="{CORAL}" stroke-width="2"/>')
    out.append(f'<circle cx="{x(3)}" cy="{line_y}" r="6" fill="#FFFFFF" stroke="{CORAL}" stroke-width="2"/>')
    for label, xx in [("x < 2", (left+x(2))/2), ("2 < x < 3", (x(2)+x(3))/2), ("x > 3", (x(3)+width-right)/2)]:
        out.append(f'<text x="{xx}" y="77" text-anchor="middle" font-family="Arial,sans-serif" font-size="14" fill="{TEAL}">{html.escape(label)}</text>')
    for label, xx, color in [("+", (left+x(2))/2, TEAL), ("−", (x(2)+x(3))/2, CORAL), ("+", (x(3)+width-right)/2, TEAL)]:
        out.append(f'<text x="{xx}" y="163" text-anchor="middle" font-family="Arial,sans-serif" font-size="22" font-weight="700" fill="{color}">{label}</text>')
    out.append(f'<text x="{x(2)}" y="195" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="{INK}">2 (root)</text>')
    out.append(f'<text x="{x(3)}" y="195" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="{INK}">3 (root)</text>')
    out.append("</svg>")
    return "".join(out)


def _discriminant_visual():
    series = [
        {"label": "D > 0: x² − 1", "fn": lambda x: x*x-1, "color": TEAL},
        {"label": "D = 0: x²", "fn": lambda x: x*x, "color": BLUE},
        {"label": "D < 0: x² + 1", "fn": lambda x: x*x+1, "color": AMBER},
    ]
    return _chart_svg("Discriminant and number of x-intercepts", (-2.4,2.4), (-1.6,5.5), series,
                      points=[{"x":-1,"y":0,"label":"cross","dx":-42,"dy":-10},
                              {"x":1,"y":0,"label":"cross","dx":7,"dy":-10},
                              {"x":0,"y":0,"label":"touch","dx":7,"dy":18}])


def build_visual(visual_key, a=1.0, symmetry_left=1.0):
    if visual_key == "coefficient_family":
        return _chart_svg("Sign and magnitude of a change a parabola", (-2.8,2.8), (-7.5,8.5), [
            {"label":"y = x²", "fn":lambda x:x*x, "color":BLUE},
            {"label":"y = −x²", "fn":lambda x:-x*x, "color":CORAL},
            {"label":"y = 2x²", "fn":lambda x:2*x*x, "color":TEAL},
            {"label":"y = 0.5x²", "fn":lambda x:0.5*x*x, "color":AMBER},
        ])
    if visual_key == "quadratic_family":
        return _chart_svg(f"Interactive curve: y = {a:g}x²", (-3,3), (-8,8), [
            {"label":f"y = {a:g}x²", "fn":lambda x:a*x*x, "color":TEAL},
            {"label":"reference y = x²", "fn":lambda x:x*x, "color":BLUE, "dash":True},
        ], points=[{"x":0,"y":0,"label":"vertex (0, 0)","dx":8,"dy":-10}])
    if visual_key in ("quadratic_features", "completing_square", "symmetry_explorer"):
        fn = lambda x: x*x-5*x+6
        pts = [
            {"x":0,"y":6,"label":"y-intercept (0, 6)","dx":9,"dy":-8},
            {"x":2,"y":0,"label":"root 2","dx":-44,"dy":19},
            {"x":3,"y":0,"label":"root 3","dx":9,"dy":19},
            {"x":2.5,"y":-0.25,"label":"vertex (2.5, −0.25)","dx":10,"dy":23},
        ]
        if visual_key == "symmetry_explorer":
            y = fn(symmetry_left)
            other = 5-symmetry_left
            pts.extend([
                {"x":symmetry_left,"y":y,"label":f"({symmetry_left:g}, {y:g})","dx":-92,"dy":-12,"color":PURPLE},
                {"x":other,"y":y,"label":f"({other:g}, {y:g})","dx":9,"dy":-12,"color":PURPLE},
            ])
        return _chart_svg("The quadratic y = x² − 5x + 6", (-1,5), (-1.4,8), [
            {"label":"y = x² − 5x + 6","fn":fn,"color":BLUE},
        ], points=pts, verticals=[{"x":2.5,"color":AMBER,"dash":True}])
    if visual_key == "discriminant":
        return _discriminant_visual()
    if visual_key == "sign_chart":
        return _sign_chart_svg()
    if visual_key == "inequality_overlap":
        return _chart_svg("Overlap: y ≥ 2x − 1 and y ≤ −x + 5", (-1.5,4.2), (-3.4,7.2), [
            {"label":"y = 2x − 1","fn":lambda x:2*x-1,"color":BLUE},
            {"label":"y = −x + 5","fn":lambda x:-x+5,"color":CORAL},
        ], points=[{"x":2,"y":3,"label":"intersection (2, 3)","dx":9,"dy":-10}],
            shades=[{"x0":-1.5,"x1":2,"upper":lambda x:-x+5,"lower":lambda x:2*x-1,"fill":PALE_TEAL,"opacity":0.58}])
    if visual_key == "line_parabola_intersections":
        return _chart_svg("Intersections satisfy both y = x² and y = x + 2", (-2,3), (-1,9), [
            {"label":"y = x²","fn":lambda x:x*x,"color":BLUE},
            {"label":"y = x + 2","fn":lambda x:x+2,"color":AMBER},
        ], points=[{"x":-1,"y":1,"label":"(−1, 1)","dx":-63,"dy":-9},
                  {"x":2,"y":4,"label":"(2, 4)","dx":8,"dy":-9}])
    if visual_key == "integral_under_curve":
        return _chart_svg("Signed area under y = x² from 0 to 2", (-0.3,2.5), (-0.5,5.5), [
            {"label":"y = x²","fn":lambda x:x*x,"color":BLUE},
        ], points=[{"x":0,"y":0,"label":"0","dx":8,"dy":-9},{"x":2,"y":4,"label":"(2, 4)","dx":8,"dy":-8}],
            shades=[{"x0":0,"x1":2,"upper":lambda x:x*x,"lower":lambda x:0,"fill":PALE_TEAL,"opacity":0.68}])
    if visual_key == "area_between_curves":
        return _chart_svg("Area between y = x + 2 and y = x²", (-1.5,2.5), (-0.7,5.5), [
            {"label":"upper: y = x + 2","fn":lambda x:x+2,"color":AMBER},
            {"label":"lower: y = x²","fn":lambda x:x*x,"color":BLUE},
        ], points=[{"x":-1,"y":1,"label":"(−1, 1)","dx":-67,"dy":-8},
                  {"x":2,"y":4,"label":"(2, 4)","dx":8,"dy":-8}],
            shades=[{"x0":-1,"x1":2,"upper":lambda x:x+2,"lower":lambda x:x*x,"fill":PALE_TEAL,"opacity":0.65}])
    raise ValueError(f"Unknown quadratics visual key: {visual_key}")


def render_lesson_visual(lesson, key_prefix="quadratics"):
    """Render the configured lesson visual, including selected live graph controls."""
    import streamlit as st

    visual_key = lesson.get("visual_key")
    if not visual_key:
        return
    st.markdown("#### Explore the graph")
    if visual_key == "quadratic_family":
        coefficient = st.select_slider(
            "Coefficient a in y = ax²",
            options=[-2.0, -1.0, -0.5, 0.5, 1.0, 2.0],
            value=1.0,
            key=f"{key_prefix}_a_{lesson['id']}",
            help="Negative values open down; a larger absolute value makes the curve narrower.",
        )
        st.markdown(build_visual(visual_key, a=coefficient), unsafe_allow_html=True)
        st.caption("Compare the solid curve with the dashed y = x² reference. a cannot be zero for a quadratic.")
    elif visual_key == "symmetry_explorer":
        left_x = st.slider(
            "Choose an x-coordinate on the left/right of the symmetry axis",
            min_value=-0.5, max_value=2.5, value=1.0, step=0.5,
            key=f"{key_prefix}_symmetry_{lesson['id']}",
            help="The reflected point is equally far from x = 2.5 and has the same y-value.",
        )
        st.markdown(build_visual(visual_key, symmetry_left=left_x), unsafe_allow_html=True)
        st.caption(f"Axis x = 2.5. The partner x-coordinate is {5-left_x:g}; both points have the same y-value.")
    else:
        st.markdown(build_visual(visual_key), unsafe_allow_html=True)
