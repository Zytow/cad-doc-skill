"""Numbered balloons and a parts list on a line rendering: a technical exploded-view sheet.

Usage (project folder):
    python tools/callouts.py tools/render/<assembly>.json <shot> [--out doc/<folder>/images/<name>.png]

Reads
    doc/<folder>/images/<prefix>-<shot>.png    line rendering (render_assembly.py, shot style "line")
    doc/<folder>/images/<prefix>-<shot>.json   part anchors written by the same run
and the "sheet" block of the render configuration:

    "sheet": {
      "title": "Bluetooth speaker",
      "subtitle": "Exploded view",
      "drawing_no": "SPK-V1-EXP-01",
      "author": "Name",
      "date": "2026-11-22",
      "accent": "#D62F2F",
      "bom": [ {"part": "grille", "label": "Grille", "qty": 1, "material": "perforated steel"}, ... ]
    }

The numbering follows the order of "bom". Balloons sit above or below the drawing, leader lines end in a dot
at the part anchor. The sheet is laid out as HTML and printed to PNG with Microsoft Edge (headless).
"""
import html
import json
import subprocess
import sys
import tempfile
import time
from pathlib import Path

EDGE_CANDIDATES = [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    "/usr/bin/microsoft-edge",
    "/usr/bin/chromium",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
]

BALLOON_R = 26
MIN_GAP = 2 * BALLOON_R + 10
MARGIN = 150


def find_browser():
    for c in EDGE_CANDIDATES:
        if Path(c).exists():
            return c
    sys.exit("callouts.py needs Microsoft Edge or Chromium (set the path in EDGE_CANDIDATES).")


def spread(xs, lo, hi):
    """Moves sorted x positions apart so that neighbours keep MIN_GAP, staying inside [lo, hi]."""
    xs = list(xs)
    for i in range(1, len(xs)):
        xs[i] = max(xs[i], xs[i - 1] + MIN_GAP)
    over = xs[-1] - hi if xs else 0
    if over > 0:
        xs = [x - over for x in xs]
        for i in range(len(xs) - 2, -1, -1):
            xs[i] = min(xs[i], xs[i + 1] - MIN_GAP)
    return [max(x, lo) for x in xs]


def build_html(img_path, img_w, img_h, anchors, sheet):
    bom = sheet["bom"]
    accent = sheet.get("accent", "#D62F2F")
    number = {row["part"]: i + 1 for i, row in enumerate(bom)}
    by_name = {a["name"]: a for a in anchors}
    items = [(number[r["part"]], by_name[r["part"]]) for r in bom if r["part"] in by_name]
    cy = img_h / 2
    top = sorted([(n, a) for n, a in items if a["y"] < cy], key=lambda t: t[1]["x"])
    bottom = sorted([(n, a) for n, a in items if a["y"] >= cy], key=lambda t: t[1]["x"])
    x0 = MARGIN
    canvas_w = img_w + 2 * MARGIN
    draw_h = img_h + 2 * MARGIN
    svg = []
    for group, y_balloon, y_edge in ((top, 60, 60 + BALLOON_R), (bottom, draw_h - 60, draw_h - 60 - BALLOON_R)):
        xs = spread([x0 + a["x"] for _, a in group], 60, canvas_w - 60)
        for (n, a), bx in zip(group, xs):
            ax, ay = x0 + a["x"], MARGIN + a["y"]
            svg.append(f'<line x1="{bx:.1f}" y1="{y_edge}" x2="{ax:.1f}" y2="{ay:.1f}" stroke="#222" stroke-width="2"/>')
            svg.append(f'<circle cx="{ax:.1f}" cy="{ay:.1f}" r="6" fill="#222"/>')
            svg.append(f'<circle cx="{bx:.1f}" cy="{y_balloon}" r="{BALLOON_R}" fill="#fff" stroke="#222" stroke-width="3"/>')
            svg.append(f'<text x="{bx:.1f}" y="{y_balloon + 9}" text-anchor="middle" font-size="26" font-weight="700" '
                       f'font-family="Arial, Helvetica, sans-serif" fill="#111">{n}</text>')
    rows = "".join(
        f"<tr><td class='n'>{i + 1}</td><td>{html.escape(str(r.get('label', r['part'])))}</td>"
        f"<td class='q'>{r.get('qty', 1)}</td><td>{html.escape(str(r.get('material', '')))}</td></tr>"
        for i, r in enumerate(bom))
    half = (len(bom) + 1) // 2
    left_rows = "".join(rows.split("</tr>")[i] + "</tr>" for i in range(half))
    right_rows = "".join(rows.split("</tr>")[i] + "</tr>" for i in range(half, len(bom)))
    head = "<tr><th>Pos.</th><th>Part</th><th>Qty</th><th>Material</th></tr>"
    css = f"""
    body {{ margin:0; background:#fff; font-family: Arial, Helvetica, sans-serif; color:#111; }}
    .sheet {{ width:{canvas_w}px; border:4px solid #222; box-sizing:border-box; padding:0; }}
    .draw {{ position:relative; width:{canvas_w}px; height:{draw_h}px; }}
    .draw img {{ position:absolute; left:{x0}px; top:{MARGIN}px; width:{img_w}px; height:{img_h}px; }}
    .draw svg {{ position:absolute; left:0; top:0; }}
    .foot {{ display:flex; border-top:3px solid #222; }}
    .parts {{ display:flex; gap:40px; padding:26px 30px; flex:1; }}
    table {{ border-collapse:collapse; font-size:22px; }}
    th, td {{ border:1.5px solid #222; padding:5px 12px; text-align:left; }}
    th {{ background:#eee; }}
    td.n {{ font-weight:700; text-align:center; width:56px; }}
    td.q {{ text-align:center; width:50px; }}
    .block {{ width:560px; border-left:3px solid #222; padding:22px 28px; box-sizing:border-box; }}
    .block .t {{ font-size:40px; font-weight:700; }}
    .block .s {{ font-size:26px; margin-top:6px; }}
    .block .m {{ font-size:20px; margin-top:18px; line-height:1.5; color:#333; }}
    .bar {{ height:8px; width:120px; background:{accent}; margin-bottom:16px; }}
    """
    meta = " · ".join(x for x in (sheet.get("drawing_no"), sheet.get("date"), sheet.get("author")) if x)
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{css}</style></head><body>
<div class="sheet">
 <div class="draw"><img src="{img_path.as_uri()}"><svg width="{canvas_w}" height="{draw_h}">{''.join(svg)}</svg></div>
 <div class="foot">
  <div class="parts"><table>{head}{left_rows}</table><table>{head}{right_rows}</table></div>
  <div class="block"><div class="bar"></div><div class="t">{html.escape(sheet.get('title', ''))}</div>
   <div class="s">{html.escape(sheet.get('subtitle', ''))}</div><div class="m">{html.escape(meta)}<br>Scale: not to scale</div></div>
 </div>
</div></body></html>"""


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    root = Path(__file__).resolve().parent.parent
    cfg = json.loads((root / sys.argv[1]).read_text(encoding="utf-8"))
    shot = sys.argv[2]
    out = None
    if "--out" in sys.argv:
        out = root / sys.argv[sys.argv.index("--out") + 1]
    base = root / "doc" / cfg["folder"] / "images" / f"{cfg['prefix']}-{shot}"
    png, meta = base.with_suffix(".png"), base.with_suffix(".json")
    data = json.loads(meta.read_text(encoding="utf-8"))
    from struct import unpack
    with open(png, "rb") as f:
        head = f.read(24)
    img_w, img_h = unpack(">II", head[16:24])
    scale = img_w / data["width"]
    anchors = [{"name": a["name"], "x": a["x"] * scale, "y": a["y"] * scale} for a in data["anchors"]]
    page = build_html(png, img_w, img_h, anchors, cfg["sheet"])
    out = out or base.parent / f"{cfg['prefix']}-{shot}-sheet.png"
    width = img_w + 2 * MARGIN
    parts_rows = (len(cfg["sheet"]["bom"]) + 1) // 2
    height = img_h + 2 * MARGIN + 80 + parts_rows * 41
    work = Path(tempfile.gettempdir()) / "cad-doc-callouts"
    work.mkdir(exist_ok=True)
    h = work / "sheet.html"
    h.write_text(page, encoding="utf-8")
    out = Path(out).resolve()
    if out.exists():
        out.unlink()
    subprocess.run([find_browser(), "--headless", "--disable-gpu", "--hide-scrollbars", "--no-first-run",
                    f"--user-data-dir={work / 'profile'}", f"--window-size={width},{height}",
                    f"--screenshot={out}", h.resolve().as_uri()], check=True, capture_output=True, timeout=180)
    for _ in range(60):  # the browser may hand the write to a child process
        if out.exists() and out.stat().st_size > 0:
            break
        time.sleep(1)
    else:
        sys.exit("browser produced no screenshot")
    print(out)


if __name__ == "__main__":
    main()
