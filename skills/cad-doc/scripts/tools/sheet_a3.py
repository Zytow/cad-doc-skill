"""Rebuilds an A3 drawing sheet (DIN A3 landscape) as SVG, with frame, zones and title block.

Positions of frame, zones and title block follow a standard A3 template. Coordinates
are in mm, origin bottom left as in NX; the output flips y for SVG.

The title block is neutral. Everything that identifies an organisation comes from the
caller:

    organisation   name shown in the logo field (default "Organisation")
    project        project name below it (default "Project")
    logo           optional path to a PNG; if given and the file exists it is embedded
                   in the logo field instead of the two text lines
    accent         hex colour used by callers for markers (default "#D62F2F")

Title-block fields (dict, all optional):
    part_name, part_number, drawn_by, phone, email, date, material, quantity, scale, sheet

Each of organisation / project / logo / accent can be passed as constructor argument or
as key of the fields dict; the constructor argument wins.

Usage:
    from sheet_a3 import Sheet
    s = Sheet(fields={...}, organisation="Acme Racing", project="Roadster")
    s.add(svg_fragment_in_mm_y_up)   # content in SVG coordinates (y down)
    s.write("file.svg")
"""
import base64
from pathlib import Path

W, H = 420.0, 297.0
DEFAULT_ACCENT = "#D62F2F"


def Y(y):
    """NX y (0 at the bottom) to SVG y (0 at the top)."""
    return H - y


def line(x1, y1, x2, y2, w=0.35, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<line x1="{x1:.3f}" y1="{Y(y1):.3f}" x2="{x2:.3f}" y2="{Y(y2):.3f}" stroke="#000" stroke-width="{w}"{d}/>'


def text(x, y, s, size=2.5, anchor="start", weight="normal"):
    return (f'<text x="{x:.3f}" y="{Y(y):.3f}" font-family="Arial, Helvetica, sans-serif" font-size="{size}" '
            f'text-anchor="{anchor}" font-weight="{weight}">{s}</text>')


class Sheet:
    def __init__(self, fields, organisation=None, project=None, logo=None, accent=None):
        self.fields = fields
        self.organisation = organisation or fields.get("organisation") or "Organisation"
        self.project = project or fields.get("project") or "Project"
        self.logo = logo or fields.get("logo")
        self.accent = accent or fields.get("accent") or DEFAULT_ACCENT
        self.content = []

    def add(self, frag):
        self.content.append(frag)

    def frame(self):
        o = []
        # dashed outer edge, drawing frame 10 mm
        o.append(f'<rect x="0.2" y="0.2" width="{W-0.4}" height="{H-0.4}" fill="none" stroke="#000" stroke-width="0.25" stroke-dasharray="6 3"/>')
        o.append(f'<rect x="10" y="10" width="{W-20}" height="{H-20}" fill="none" stroke="#000" stroke-width="0.7"/>')
        # black corner squares (like the hatch in the template)
        for x, y in ((0, 0), (W - 10, 0), (0, H - 10), (W - 10, H - 10)):
            o.append(f'<rect x="{x}" y="{y}" width="10" height="10" fill="#000"/>')
            o.append(f'<rect x="{x+2.5}" y="{y+2.5}" width="5" height="5" fill="#fff"/>')
        # zones 1-6 and A-D
        for i, xs in enumerate(range(70, 420, 70)):
            if xs < 420:
                o.append(line(xs, 0.2, xs, 10, 0.25))
                o.append(line(xs, H - 10, xs, H - 0.2, 0.25))
        for i in range(6):
            xc = 35 + 70 * i
            o.append(text(xc, 3.6, str(i + 1), 3.5, "middle"))
            o.append(text(xc, H - 6.4, str(i + 1), 3.5, "middle"))
        for yy in (74.25, 148.5, 222.75):
            o.append(line(0.2, yy, 10, yy, 0.25))
            o.append(line(W - 10, yy, W - 0.2, yy, 0.25))
        for j, yc in enumerate((259.875, 185.625, 111.375, 37.125)):
            ch = "ABCD"[j]
            o.append(text(5, yc - 1.2, ch, 3.5, "middle"))
            o.append(text(W - 5, yc - 1.2, ch, 3.5, "middle"))
        # centering marks
        o.append(line(210, H - 10, 210, H - 15, 0.5))
        o.append(line(210, 10, 210, 15, 0.5))
        o.append(line(10, 148.5, 15, 148.5, 0.5))
        o.append(line(W - 10, 148.5, W - 15, 148.5, 0.5))
        return o

    def title_block(self):
        f = self.fields
        o = []
        x0, x1, x2, x3, x4 = 229.9, 254.6, 311.3, 392.4, 410.0
        y0, y1, y2, y3, y4 = 10.0, 21.7, 33.9, 46.0, 70.1
        o.append(f'<rect x="{x0}" y="{Y(y4)}" width="{x4-x0}" height="{y4-y0}" fill="#fff" stroke="#000" stroke-width="0.5"/>')
        o.append(line(x2, y0, x2, y4, 0.35))
        o.append(line(x3, y0, x3, y4, 0.35))
        o.append(line(x0, y3, x2, y3, 0.35))
        o.append(line(x0, y2, x2, y2, 0.25))
        o.append(line(x0, y1, x2, y1, 0.25))
        o.append(line(x1, y0, x1, y3, 0.25))
        o.append(line(x2, 50.4, x4, 50.4, 0.35))
        o.append(line(x2, 30.4, x4, 30.4, 0.35))
        o.append(line(343.5, y0, 343.5, 30.4, 0.25))
        o.append(line(379.4, y0, 379.4, 30.4, 0.25))
        # logo field: embedded logo if given, otherwise organisation and project as text
        logo = Path(self.logo) if self.logo else None
        if logo is not None and logo.exists():
            b64 = base64.b64encode(logo.read_bytes()).decode()
            o.append(f'<image x="244.0" y="{Y(69.0)}" width="55.0" height="21.0" preserveAspectRatio="xMidYMid meet" href="data:image/png;base64,{b64}"/>')
        else:
            o.append(text(271.5, 57.0, self.organisation, 5.0, "middle", "bold"))
            o.append(text(271.5, 49.5, self.project, 3.5, "middle"))
        # field labels (positions as in the template)
        lab = 2.2
        o.append(text(312.7, 64.6, "Part name", lab))
        o.append(text(312.7, 44.2, "Part number", lab))
        o.append(text(231.3, 38.6, "Drawn by", lab))
        o.append(text(230.8, 26.4, "Phone", lab))
        o.append(text(231.7, 14.5, "Email", lab))
        o.append(text(312.8, 25.1, "Date", lab))
        o.append(text(344.9, 24.8, "Material", lab))
        o.append(text(380.7, 25.3, "Quantity", lab))
        o.append(text(401.0, 65.1, "Scale", lab, "middle"))
        o.append(text(401.2, 46.2, "Format", lab, "middle"))
        o.append(text(400.7, 25.5, "Sheet", lab, "middle"))
        o.append(text(218.0, 18.8, "ALL DIMENSIONS IN MM", 2.5, "end"))
        # values
        o.append(text(351.9, 56.0, f.get("part_name", ""), 3.5, "middle"))
        o.append(text(351.9, 36.6, f.get("part_number", ""), 3.5, "middle"))
        o.append(text(256.5, 38.6, f.get("drawn_by", ""), 3.0))
        o.append(text(256.5, 26.4, f.get("phone", ""), 3.0))
        o.append(text(256.5, 14.5, f.get("email", ""), 3.0))
        o.append(text(327.4, 16.6, f.get("date", ""), 3.0, "middle"))
        o.append(text(361.4, 16.6, f.get("material", ""), 3.0, "middle"))
        o.append(text(385.9, 16.6, f.get("quantity", ""), 3.0, "middle"))
        o.append(text(401.2, 56.6, f.get("scale", "1:1"), 5.0, "middle"))
        o.append(text(401.2, 35.8, "A3", 5.0, "middle"))
        o.append(text(401.2, 17.0, f.get("sheet", "1/1"), 5.0, "middle"))
        return o

    def svg(self):
        parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}mm" height="{H}mm" viewBox="0 0 {W} {H}">',
                 f'<rect width="{W}" height="{H}" fill="#fff"/>']
        parts += self.frame()
        parts += self.content
        parts += self.title_block()
        parts.append("</svg>")
        return "\n".join(parts)

    def write(self, path):
        Path(path).write_text(self.svg(), encoding="utf-8")
