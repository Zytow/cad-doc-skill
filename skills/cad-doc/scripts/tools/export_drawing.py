"""Export an SVG drawing (A3) with Edge as PDF and PNG preview.

Usage (regular Python):
    python tools/export_drawing.py <file.svg> [...] <target-folder>

PDF and PNG take the name of the SVG and end up in the target folder,
e.g. doc/<assembly>/drawings/.
"""
import subprocess
import sys
import time
from pathlib import Path

EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
target = Path(sys.argv[-1]).resolve()
target.mkdir(parents=True, exist_ok=True)
for a in sys.argv[1:-1]:
    svg = Path(a).resolve()
    png, pdf = target / (svg.stem + ".png"), target / (svg.stem + ".pdf")
    html = svg.with_suffix(".html")
    html.write_text('<!doctype html><html><head><meta charset="utf-8"><style>@page{size:420mm 297mm;margin:0}'
                    'html,body{margin:0;padding:0}img{display:block;width:420mm;height:297mm}</style></head>'
                    f'<body><img src="{svg.name}"></body></html>', encoding="utf-8")
    subprocess.run([EDGE, "--headless", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=1.5",
                    "--window-size=1587,1123", f"--screenshot={png}", svg.as_uri()], capture_output=True)
    subprocess.run([EDGE, "--headless", "--disable-gpu", "--no-pdf-header-footer",
                    f"--print-to-pdf={pdf}", html.as_uri()], capture_output=True)
    for _ in range(30):  # the browser may finish writing after the call returns
        if pdf.exists() and png.exists():
            break
        time.sleep(1)
    time.sleep(1)
    html.unlink(missing_ok=True)
    print("OK", png.name, pdf.name)
