"""Multi-view drawing of a part on an A3 sheet (FreeCAD, headless).

Usage:
    freecadcmd tools/part_drawing.py <config.json>

Configuration keys:
    step             STEP file of the part (in assembly coordinates)
    output           path without extension (writes <output>-<n>.svg and <output>.json)
    fields           title block (see sheet_a3.Sheet): part_name, part_number, drawn_by, phone,
                     email, date, material, quantity
    organisation     optional, name in the logo field of the title block (default "Organisation")
    project          optional, project name in the title block (default "Project")
    logo             optional path to a PNG logo for the title block
    accent           optional hex colour for hole markers (default "#D62F2F")
    views            list of "front", "back", "left", "right", "top", "bottom" (default: all)
    front_direction  direction from which "front" is viewed: "-y" (default), "+y", "-x", "+x"
    purposes         list of {d, axis: x|y|z, purpose} labelling the hole groups
    dmax             largest diameter that counts as a hole (default 40)
    ignore           optional list of {d, axis}: hole groups left out of the table
    openings         optional list of {size, axis, purpose, c: [[x, y, z], ...]} for non-round openings
    cutout           optional [xmin, ymin, zmin, xmax, ymax, zmax] for a detail drawing
    area             optional drawing area [x0, y0, x1, y1] in mm (default: left of the table)
    notes            optional list of note lines printed next to the table
    sheets           optional list of lists of view names to fix the distribution over sheets
    max_sheets       maximum number of sheets (default 3)
    target_scale     target scale as a factor (default 1.0)

Hidden edges are not drawn. Holes are grouped by diameter, axis and side, marked with
letters in the views and listed in a table. The output JSON lists scale, sheets, view
sizes ("sizes") and the hole table ("holes": id, d, size, axis, count, purpose).
"""
import itertools
import json
import math
import sys
from collections import defaultdict
from pathlib import Path

import FreeCAD as App
import Part

TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))
from sheet_a3 import Sheet, Y  # noqa: E402

cfg = json.loads(Path(sys.argv[-1]).read_text(encoding="utf-8"))
shape = Part.read(cfg["step"])
if cfg.get("cutout"):  # detail: cut the part to a box [xmin, ymin, zmin, xmax, ymax, zmax]
    a = cfg["cutout"]
    shape = shape.common(Part.makeBox(a[3] - a[0], a[4] - a[1], a[5] - a[2], App.Vector(a[0], a[1], a[2])))
bb = shape.BoundBox
C = bb.Center

# views: name -> (direction towards the viewer, X direction in the image)
V = App.Vector
basis = {
    "-y": {"front": (V(0, -1, 0), V(1, 0, 0)), "back": (V(0, 1, 0), V(-1, 0, 0)),
           "left": (V(-1, 0, 0), V(0, -1, 0)), "right": (V(1, 0, 0), V(0, 1, 0)),
           "top": (V(0, 0, 1), V(1, 0, 0)), "bottom": (V(0, 0, -1), V(1, 0, 0))},
}
VIEWS = basis["-y"]
if cfg.get("front_direction", "-y") != "-y":
    rot = {"+y": 180, "-x": -90, "+x": 90}[cfg["front_direction"]]
    m = App.Rotation(V(0, 0, 1), rot)
    VIEWS = {k: (m.multVec(d), m.multVec(x)) for k, (d, x) in VIEWS.items()}
wanted = cfg.get("views", ["front", "back", "left", "right", "top", "bottom"])

doc = App.newDocument("z")
pf = doc.addObject("Part::Feature", "p")
pf.Shape = shape
page = doc.addObject("TechDraw::DrawPage", "page")
page.Template = doc.addObject("TechDraw::DrawSVGTemplate", "tpl")


def project(name):
    d, x = VIEWS[name]
    v = doc.addObject("TechDraw::DrawViewPart", "v_" + name)
    page.addView(v)
    v.Source = [pf]
    v.Direction = d
    v.XDirection = x
    v.Scale = 1.0
    doc.recompute()
    polys = [[(p.x, -p.y) for p in e.discretize(Deflection=0.02)] for e in v.getVisibleEdges()]
    yv = d.cross(x)
    corners = [V(a, b, c) for a in (bb.XMin, bb.XMax) for b in (bb.YMin, bb.YMax) for c in (bb.ZMin, bb.ZMax)]
    us = [(p - C).dot(x) for p in corners]
    vs = [(p - C).dot(yv) for p in corners]
    return {"polys": polys, "d": d, "x": x, "y": yv, "w": max(us) - min(us), "h": max(vs) - min(vs),
            "umin": min(us), "vmin": min(vs)}


views = {n: project(n) for n in wanted}

# ------------------------------------------------------------ holes
dmax = cfg.get("dmax", 40)
# collect partial faces of the same hole (same axis, same radius) and add up the angles
cyl = defaultdict(lambda: {"span": 0.0, "pts": [], "lo": 1e9, "hi": -1e9})
for f in shape.Faces:
    s = f.Surface
    if not isinstance(s, Part.Cylinder) or 2 * s.Radius > dmax:
        continue
    u0, u1, v0, v1 = f.ParameterRange
    pt = f.valueAt((u0 + u1) / 2, (v0 + v1) / 2)
    n = f.normalAt((u0 + u1) / 2, (v0 + v1) / 2)
    ax = s.Axis
    foot = s.Center + ax * ((pt - s.Center).dot(ax))
    if (foot - pt).Length > 1e-9 and n.dot(foot - pt) <= 0:
        continue  # outer face (pin), not a hole
    a = max("xyz", key=lambda k: abs(getattr(ax, k)))
    cross = tuple(round(getattr(foot, k) / 0.2) for k in "xyz" if k != a)
    z = cyl[(round(2 * s.Radius, 1), a, cross)]
    z["span"] += u1 - u0
    z["pts"].append(foot)
    z["lo"] = min(z["lo"], getattr(f.BoundBox, a.upper() + "Min"))
    z["hi"] = max(z["hi"], getattr(f.BoundBox, a.upper() + "Max"))
holes = []
for (d, a, _), z in cyl.items():
    if z["span"] < 0.9 * math.pi:
        continue  # fillet (quarter circle or similar), not a hole
    c = V(sum(p.x for p in z["pts"]) / len(z["pts"]), sum(p.y for p in z["pts"]) / len(z["pts"]),
          sum(p.z for p in z["pts"]) / len(z["pts"]))
    holes.append({"d": d, "axis": a, "c": c, "lo": z["lo"], "hi": z["hi"]})
# merge duplicate faces of the same hole
uniq = []
for h in holes:
    if not any(h["d"] == u["d"] and h["axis"] == u["axis"] and (h["c"] - u["c"]).Length < 1.0 for u in uniq):
        uniq.append(h)


def sides(h):
    """Sides (+1/-1 along the axis) from which the hole is open: line of sight free beyond the hole end."""
    a = h["axis"]
    lo, hi = getattr(bb, a.upper() + "Min"), getattr(bb, a.upper() + "Max")
    if "lo" not in h:
        return {1 if getattr(h["c"], a) > (lo + hi) / 2 else -1}
    e = V(*(1 if k == a else 0 for k in "xyz"))
    c0 = h["c"] - e * (getattr(h["c"], a))
    out = set()
    for sgn, start, end in ((1, h["hi"], hi), (-1, h["lo"], lo)):
        free = True
        for i in range(1, 13):
            t = start + (end - start) * i / 12 + sgn * 0.05
            if shape.isInside(c0 + e * t, 1e-3, False):
                free = False
                break
        if free:
            out.add(sgn)
    return out or {1 if getattr(h["c"], a) > (lo + hi) / 2 else -1}


groups = defaultdict(list)
for h in uniq:
    groups[(h["d"], h["axis"])].append(h)
purposes = cfg.get("purposes", [])
table = []
ign = [(g["d"], g["axis"]) for g in cfg.get("ignore", [])]
groups = {k: v for k, v in groups.items() if not any(abs(k[0] - d) < 0.15 and k[1] == a for d, a in ign)}
for i, ((d, a), hs) in enumerate(sorted(groups.items(), key=lambda kv: (-kv[0][0], kv[0][1]))):
    z = next((t["purpose"] for t in purposes if abs(t["d"] - d) < 0.15 and t["axis"] == a), "")
    table.append({"id": chr(65 + i), "d": d, "axis": a, "count": len(hs), "purpose": z, "holes": hs})
# non-round openings from the configuration: {size, axis, purpose, c: [[x, y, z], ...]}
for o in cfg.get("openings", []):
    hs = [{"c": V(*c), "axis": o["axis"]} for c in o["c"]]
    table.append({"id": chr(65 + len(table)), "d": 0, "size": o["size"], "axis": o["axis"], "count": len(hs),
                  "purpose": o["purpose"], "holes": hs})

# ------------------------------------------------------------ layout
# Sheet 1 carries the table and the notes at the bottom left, the views lie above across the full width.
# Further sheets have no table: there the area may also extend to the bottom edge left of the title block.
AREA_T = tuple(cfg.get("area", (15, 75, 405, 286)))
AREAS_FREE = [(15, 75, 405, 286), (15, 15, 225, 286)]
names = [n for n in ["top", "bottom", "front", "back", "left", "right"] if n in views]
DL, DT, DB, GX, GY = 13, 7, 13, 6, 3  # room for dimension left, title top, dimension bottom, gaps
SCALES = [(5, "5:1"), (4, "4:1"), (3, "3:1"), (2.5, "2.5:1"), (2, "2:1"), (1.5, "1.5:1"), (1, "1:1"),
          (1 / 1.5, "1:1.5"), (0.5, "1:2"), (0.4, "1:2.5"), (1 / 3, "1:3"), (0.25, "1:4"), (0.2, "1:5")]


def layout(scale, order, area):
    """Arrange the views in columns (greedy). Returns positions or None."""
    hmax = area[3] - area[1]
    cols = []  # per column: [width, height, [names]]
    for n in order:
        cw, ch = views[n]["w"] * scale + DL, views[n]["h"] * scale + DT + DB
        if ch > hmax:
            return None
        if cols and cols[-1][1] + GY + ch <= hmax:
            c = cols[-1]
            c[0] = max(c[0], cw); c[1] += GY + ch; c[2].append(n)
        else:
            cols.append([cw, ch, [n]])
    total = sum(c[0] for c in cols) + GX * (len(cols) - 1)
    if total > area[2] - area[0]:
        return None
    x = area[0] + (area[2] - area[0] - total) / 2
    pos = {}
    tallest = max(c[1] for c in cols)
    for cw, ch, ns in cols:
        top = area[3] - (hmax - tallest) / 2
        for n in ns:
            h = views[n]["h"] * scale
            pos[n] = (x + DL, top - DT - h)
            top -= DT + h + DB + GY
        x += cw + GX
    return pos


_cache = {}


def sheet_layout(subset, scale, with_table):
    """Returns (positions, table location) or None. Table location: "bottom" (bottom left) or "right" (column above the title block)."""
    key = (tuple(subset), scale, with_table)
    if key not in _cache:
        res = None
        spots = [(AREA_T, "bottom"), ((15, 15, 225, 286), "right")] if with_table else [(a, None) for a in AREAS_FREE]
        for area, spot in spots:
            for order in itertools.permutations(subset):
                pos = layout(scale, order, area)
                if pos:
                    res = (pos, spot)
                    break
            if res:
                break
        _cache[key] = res
    return _cache[key]


def splits(ns, k):
    """Distributions of the views over k non-empty sheets; the first view always lies on sheet 1."""
    if k == 1:
        yield [list(ns)]
        return
    for assign in itertools.product(range(k), repeat=len(ns) - 1):
        bl = [[ns[0]]] + [[] for _ in range(k - 1)]
        for n, i in zip(ns[1:], assign):
            bl[i].append(n)
        if all(bl) and all(min(map(ns.index, bl[i])) < min(map(ns.index, bl[i + 1])) for i in range(1, k - 1)):
            yield bl


def place_table(bl, scale_):
    """The table goes on the sheet where it fits; the last one is preferred (small views)."""
    for t in reversed(range(len(bl))):
        lay = [sheet_layout(b, scale_, i == t) for i, b in enumerate(bl)]
        if all(lay):
            return t, lay
    return None


def best(k):
    for scale_, mst_ in SCALES:
        for bl in splits(names, k):
            r = place_table(bl, scale_)
            if r:
                return scale_, mst_, bl, r[1], r[0]
    return None


if cfg.get("sheets"):
    given = [[n for n in b if n in views] for b in cfg["sheets"]]
    for scale_, mst_ in SCALES:
        r = place_table(given, scale_)
        if r:
            choice = (scale_, mst_, given, r[1], r[0])
            break
else:
    # target 1:1 (or target_scale); if not reached, the best with at most 3 sheets, with as few sheets as possible
    cand = [r for r in (best(k) for k in range(1, min(cfg.get("max_sheets", 3), len(names)) + 1)) if r]
    target = min(cfg.get("target_scale", 1.0), max(r[0] for r in cand))
    choice = next(r for r in cand if r[0] >= target - 1e-9)
scale, mst, sheets, layouts, table_sheet = choice
TITLES = {"front": "Front view", "back": "Back view", "left": "Left view", "right": "Right view",
          "top": "Top view", "bottom": "Bottom view"}


def fmt(v):
    s = f"{v:.1f}"
    return s[:-2] if s.endswith(".0") else s


def ln(x1, y1, x2, y2, w=0.25):
    return f'<line x1="{x1:.3f}" y1="{Y(y1):.3f}" x2="{x2:.3f}" y2="{Y(y2):.3f}" stroke="#000" stroke-width="{w}"/>'


def txt(x, y, s, size=3.0, anchor="middle", rot=0, weight="normal"):
    tr = f' transform="rotate({rot} {x:.3f} {Y(y):.3f})"' if rot else ""
    return (f'<text x="{x:.3f}" y="{Y(y):.3f}" font-family="Arial, Helvetica, sans-serif" font-size="{size}" '
            f'text-anchor="{anchor}" font-weight="{weight}"{tr}>{s}</text>')


def arrow(x, y, dx, dy, s=1.8):
    n = math.hypot(dx, dy)
    ux, uy = dx / n, dy / n
    px, py = -uy, ux
    pts = [(x, y), (x - ux * s + px * s * 0.3, y - uy * s + py * s * 0.3), (x - ux * s - px * s * 0.3, y - uy * s - py * s * 0.3)]
    return '<polygon points="' + " ".join(f"{a:.3f},{Y(b):.3f}" for a, b in pts) + '" fill="#000"/>'


def view_on_sheet(sheet, n, pos):
    v = views[n]
    ox, oy = pos[n]
    cx, cy = ox - v["umin"] * scale, oy - v["vmin"] * scale  # origin: bottom left of the bounding box
    sheet.add(txt(ox, oy + v["h"] * scale + 3.2, TITLES[n], 4.0, "start", weight="bold"))
    for pts in v["polys"]:
        sheet.add('<polyline points="' + " ".join(f"{cx + a * scale:.3f},{Y(cy + b * scale):.3f}" for a, b in pts)
                  + '" fill="none" stroke="#000" stroke-width="0.3" stroke-linejoin="round"/>')
    W, H = v["w"] * scale, v["h"] * scale
    yd = oy - 7
    sheet.add(ln(ox, oy, ox, yd - 1.2, 0.18)); sheet.add(ln(ox + W, oy, ox + W, yd - 1.2, 0.18))
    sheet.add(ln(ox, yd, ox + W, yd)); sheet.add(arrow(ox, yd, -1, 0)); sheet.add(arrow(ox + W, yd, 1, 0))
    sheet.add(txt(ox + W / 2, yd - 4.6, fmt(v["w"]), 3.5))
    xd = ox - 8
    sheet.add(ln(ox, oy, xd - 1.2, oy, 0.18)); sheet.add(ln(ox, oy + H, xd - 1.2, oy + H, 0.18))
    sheet.add(ln(xd, oy, xd, oy + H)); sheet.add(arrow(xd, oy, 0, -1)); sheet.add(arrow(xd, oy + H, 0, 1))
    sheet.add(txt(xd - 1.8, oy + H / 2, fmt(v["h"]), 3.5, rot=-90))
    # hole markers in every view from which the hole is open
    for t in table:
        for h in t["holes"]:
            axv = V(*(1 if k == t["axis"] else 0 for k in "xyz"))
            if not any(abs(v["d"].dot(axv) - sgn) < 1e-6 for sgn in sides(h)):
                continue
            u = (h["c"] - C).dot(v["x"]) * scale + cx
            w_ = (h["c"] - C).dot(v["y"]) * scale + cy
            sheet.add(f'<circle cx="{u:.3f}" cy="{Y(w_ + 3.2):.3f}" r="2.2" fill="#fff" stroke="{sheet.accent}" stroke-width="0.25"/>')
            sheet.add(f'<text x="{u:.3f}" y="{Y(w_ + 2.05):.3f}" font-family="Arial" font-size="3.1" font-weight="bold" fill="{sheet.accent}" text-anchor="middle">{t["id"]}</text>')


def wrap(s, n):
    lines, z = [], ""
    for w in s.split():
        if z and len(z) + 1 + len(w) > n:
            lines.append(z); z = w
        else:
            z = (z + " " + w).strip()
    return lines + [z]


def table_and_notes(sheet, spot):
    tx, ty = (18, 67) if spot == "bottom" else (236, 280)
    cols = [(tx, "ID"), (tx + 10, "Ø / Size [mm]"), (tx + 37, "Qty"), (tx + 50, "Axis"), (tx + 65, "Purpose")]
    x_end = (155 if cfg.get("notes") else 225) if spot == "bottom" else 405
    if table:
        sheet.add(txt(tx, ty, "Holes and openings", 4.0, "start", weight="bold"))
        ty -= 6.5
        for x, h in cols:
            sheet.add(txt(x, ty, h, 3.3, "start", weight="bold"))
        sheet.add(ln(tx, ty - 1.6, x_end, ty - 1.6, 0.3))
        for t in table:
            ty -= 5.6
            if ty < (14 if spot == "bottom" else 80):
                sheet.add(txt(tx, ty + 1, "… more in the JSON", 3.0, "start"))
                break
            for (x, _), val in zip(cols, [t["id"], t.get("size") or fmt(t["d"]), str(t["count"]), t["axis"], t["purpose"]]):
                frag = txt(x, ty, val, 3.3, "start", weight="bold" if x == tx else "normal")
                sheet_frag = frag.replace("<text ", f'<text fill="{sheet.accent}" ', 1) if x == tx else frag
                sheet.add(sheet_frag)
            sheet.add(ln(tx, ty - 1.6, x_end, ty - 1.6, 0.1))
    if spot == "bottom":
        hx, hy, width = (162, 67, 34) if table else (18, 67, 100)
    else:
        hx, hy, width = 236, (ty - 12 if table else 280), 80
    if cfg.get("notes"):
        sheet.add(txt(hx, hy, "Notes", 4.0, "start", weight="bold"))
        hy -= 6.5
        for s_ in cfg["notes"]:
            for i, z in enumerate(wrap(s_, width)):
                sheet.add(txt(hx + (0 if i == 0 else 3), hy, ("• " if i == 0 else "") + z, 3.2, "start"))
                hy -= 4.8
            hy -= 1


out = Path(cfg["output"])
out.parent.mkdir(parents=True, exist_ok=True)
for old in out.parent.glob(out.name + "*.svg"):
    old.unlink()
nb = len(sheets)
for i, (bl, (pos, spot)) in enumerate(zip(sheets, layouts), 1):
    sheet = Sheet({**cfg.get("fields", {}), "scale": mst, "sheet": f"{i}/{nb}"},
                  organisation=cfg.get("organisation"), project=cfg.get("project"),
                  logo=cfg.get("logo"), accent=cfg.get("accent"))
    for n in bl:
        view_on_sheet(sheet, n, pos)
    if i - 1 == table_sheet:
        table_and_notes(sheet, spot)
    sheet.write(f"{out}-{i}.svg")
info = {"scale": mst, "sheets": sheets, "sizes": {n: [round(v["w"], 1), round(v["h"], 1)] for n, v in views.items()},
        "holes": [{k: t.get(k) for k in ("id", "d", "size", "axis", "count", "purpose")} for t in table]}
Path(str(out) + ".json").write_text(json.dumps(info, indent=1, ensure_ascii=False), encoding="utf-8")
print("OK", out.name, mst, nb, "sheet(s)", json.dumps(sheets))
