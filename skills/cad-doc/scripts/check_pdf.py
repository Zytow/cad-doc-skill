#!/usr/bin/env python3
"""Check a documentation PDF against the template and layout rules.

Usage: python3 check_pdf.py <doc.pdf>
Exit code 0 = passed, 1 = at least one error, 2 = wrong usage.

Required package: pip install pymupdf
"""
from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

try:
    import fitz
except ImportError as exc:
    raise ImportError("check_pdf.py needs PyMuPDF. Install it with: pip install pymupdf") from exc

CHAPTERS = ["Overview", "Concept", "Design", "Manufacturing", "Validation", "History"]
PLACEHOLDER = re.compile(r"<here|insert .{0,40}here|how was this generation|what potential", re.I)
FOOTER_Y = 790
MARGIN_L, MARGIN_R = 49, 546.5
MIN_DPI = 150
MAX_MB = 20


@dataclass
class Line:
    page: int
    rect: fitz.Rect
    text: str
    level: int = 0


@dataclass
class Section:
    title: str
    page: int
    h3: list[str] = field(default_factory=list)
    text: str = ""
    children: list["Section"] = field(default_factory=list)


class Report:
    def __init__(self):
        self.errors, self.warnings, self.todo = [], [], []

    def e(self, page, text):
        self.errors.append(f"p.{page}: {text}" if page else text)

    def w(self, text):
        self.warnings.append(text)


def is_doc_page(page: fitz.Page) -> bool:
    """A documentation page is portrait and carries 'Page n/N' in the footer area."""
    if page.rect.width > page.rect.height:
        return False
    footer = page.get_text("text", clip=fitz.Rect(0, FOOTER_Y, page.rect.width, page.rect.height))
    return re.search(r"Page \d+/\d+", footer) is not None


def read_lines(page: fitz.Page, nr: int, rep: Report) -> list[Line]:
    out = []
    for block in page.get_text("dict")["blocks"]:
        if block["type"] != 0:
            continue
        for l in block["lines"]:
            spans = [s for s in l["spans"] if s["text"].strip()]
            if not spans:
                continue
            for s in spans:
                if not re.search(r"Arial|Liberation", s["font"]):
                    rep.e(nr, f"Font {s['font']} instead of Arial at '{s['text'].strip()[:25]}'")
            s = spans[0]
            level = 0
            # The accent colour is configurable, so headings are recognised by
            # bold weight and size only.
            if "Bold" in s["font"]:
                for size, lv in ((15, 1), (11.5, 2), (9.8, 3)):
                    if abs(s["size"] - size) < .2:
                        level = lv
            out.append(Line(nr, fitz.Rect(l["bbox"]), "".join(x["text"] for x in l["spans"]).strip(), level))
    return sorted(out, key=lambda z: (round(z.rect.y0), z.rect.x0))


def tree(lines: list[Line]) -> list[Section]:
    root, h1, h2 = [], None, None
    for z in lines:
        name = re.sub(r"^\d+(\.\d+)*\s+", "", z.text)
        if z.level == 1:
            h1, h2 = Section(name, z.page), None
            root.append(h1)
        elif z.level == 2 and h1:
            h2 = Section(name, z.page)
            h1.children.append(h2)
        elif z.level == 3 and h1:
            (h2 or h1).h3.append(name)
        elif h1:
            (h2 or h1).text += " " + z.text
    return root


def pair(a: Section, rep: Report):
    for name in ("Previous generations", "This generation"):
        if name not in a.h3:
            rep.e(a.page, f"'{a.title}': sub-heading '{name}' is missing")


def structure(root: list[Section], rep: Report):
    titles = [a.title for a in root]
    if titles != CHAPTERS:
        rep.e(0, f"Chapters differ from the template. Expected: {CHAPTERS}. Found: {titles}")
    k = {a.title: a for a in root}
    if "Overview" in k and not any(h.lower() == "relevant links" for h in k["Overview"].h3):
        rep.e(k["Overview"].page, "'Relevant links' is missing in Overview")
    if "Concept" in k:
        for name in ("Requirements", "Concept decision"):
            hits = [a for a in k["Concept"].children if a.title.startswith(name)]
            if hits:
                pair(hits[0], rep)
            else:
                rep.e(k["Concept"].page, f"Section '{name}' is missing")
    if "Design" in k:
        d = [a for a in k["Design"].children if a.title.startswith("Design decision #")]
        if not d:
            rep.e(k["Design"].page, "No 'Design decision #1' found")
        for a in d:
            pair(a, rep)
    for name in ("Manufacturing", "Validation"):
        if name in k:
            pair(k[name], rep)
    if "History" in k:
        gens = k["History"].children
        if not gens:
            rep.e(k["History"].page, "No generation entered in History")
        for a in gens:
            if "Conclusion" not in a.h3:
                rep.e(a.page, f"{a.title}: 'Conclusion' is missing")
            if not any(h.startswith("Potential for ") for h in a.h3):
                rep.e(a.page, f"{a.title}: 'Potential for <next generation>' is missing")
            if "Owner" not in a.text:
                rep.e(a.page, f"{a.title}: 'Owner' is missing")


def layout(page: fitz.Page, nr: int, lines: list[Line], rep: Report) -> int:
    content = [z for z in lines if z.rect.y0 < FOOTER_Y]
    images = [i for i in page.get_image_info()] if nr > 1 else []
    rects = [fitz.Rect(i["bbox"]) for i in images]
    for z in content:
        if z.rect.x0 < MARGIN_L or z.rect.x1 > MARGIN_R:
            rep.e(nr, f"Text outside the type area: '{z.text[:35]}'")
    for z in content:
        if z.level:
            after = [x for x in content if x.rect.y0 > z.rect.y1 - 1 and not x.level]
            image_after = [r for r in rects if r.y0 > z.rect.y0]
            if not after and not image_after:
                rep.e(nr, f"Heading alone at the bottom of the page: '{z.text[:40]}'")
    rules = [fitz.Rect(g["rect"]) for g in page.get_drawings()]
    for i, r in zip(images, rects):
        dpi = i["width"] / max(r.width, 1) * 72
        if dpi < MIN_DPI:
            rep.e(nr, f"Image with only {dpi:.0f} dpi")
        if r.x0 < MARGIN_L or r.x1 > MARGIN_R:
            rep.e(nr, "Image outside the type area")
        near = [z.rect for z in content] + [l for l in rules if l.y1 < FOOTER_Y]
        for n in near:
            horizontal = min(n.x1, r.x1) - max(n.x0, r.x0) > 1
            if horizontal and n.y0 < r.y0 + 1 and n.y1 > r.y0 - 3:
                rep.e(nr, "Image touches the element above it (at least 3 pt gap required)")
                break
        if not any(z.text.startswith("Figure ") and 0 <= z.rect.y0 - r.y1 < 18 for z in content):
            rep.e(nr, "Image without caption 'Figure N – ...'")
    return len(images)


def check(path: Path) -> Report:
    rep = Report()
    pdf = fitz.open(path)
    pages = [i for i in range(pdf.page_count) if is_doc_page(pdf[i])]
    if not pages:
        rep.e(0, "No page with a 'Page n/N' footer found")
        return rep
    allines, total = [], len(pages)
    for i in pages:
        nr = i + 1
        z = read_lines(pdf[i], nr, rep)
        layout(pdf[i], nr, z, rep)
        allines += z
        footer = " ".join(x.text for x in z if x.rect.y0 >= FOOTER_Y)
        if f"Page {nr}/{total}" not in footer:
            rep.e(nr, f"Footer should contain 'Page {nr}/{total}'")
    structure(tree([z for z in allines if z.page > 1 and z.rect.y0 < FOOTER_Y]), rep)
    numbers = [int(m.group(1)) for z in allines if (m := re.match(r"Figure (\d+) –", z.text))]
    if numbers != list(range(1, len(numbers) + 1)):
        rep.e(0, f"Figure numbers are not consecutive: {numbers}")
    for z in allines:
        if PLACEHOLDER.search(z.text):
            rep.e(z.page, f"Placeholder left from the template: '{z.text[:45]}'")
        if re.search(r"\bTBD\b", z.text):
            rep.todo.append(f"p.{z.page}: {z.text[:70]}")
    if not pdf.get_toc():
        rep.e(0, "PDF has no bookmarks")
    if not pdf.metadata.get("title"):
        rep.w("PDF title is missing in the metadata")
    mb = path.stat().st_size / 1e6
    if mb > MAX_MB:
        rep.w(f"File is {mb:.0f} MB (target: at most {MAX_MB} MB)")
    return rep


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    rep = check(Path(sys.argv[1]))
    for label, items in (("ERROR", rep.errors), ("WARNING", rep.warnings), ("TODO", rep.todo)):
        for entry in dict.fromkeys(items):
            print(f"{label}  {entry}")
    print(f"RESULT: {'FAILED' if rep.errors else 'PASSED'} "
          f"({len(set(rep.errors))} errors, {len(set(rep.warnings))} warnings, {len(set(rep.todo))} todo)")
    return 1 if rep.errors else 0


if __name__ == "__main__":
    sys.exit(main())
