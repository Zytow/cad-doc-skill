#!/usr/bin/env python3
"""Layout engine for a PDF documentation of an assembly (reportlab + Pillow + PyMuPDF).

A4 portrait, Arial. The script sets spacing, numbering, captions, bookmarks and the
footer itself. The caller only supplies content in the order of the template.

Usage:

    from doc_style import Doc
    d = Doc(target="out/doc.pdf", title="Title", subtitle="Subtitle",
            short="<GEN-B>-<assembly>", date="18.11.2026", cover_image="images/cover.jpg",
            meta={"Project": "..."}, accent="#1f3b57", footer="")
    d.h1("Overview")
    d.p("Text")
    d.build()

Required packages: pip install reportlab pymupdf pillow
"""
from __future__ import annotations

import os
import re
import tempfile
from pathlib import Path

try:
    import fitz
except ImportError as exc:
    raise ImportError("doc_style.py needs PyMuPDF. Install it with: pip install pymupdf") from exc
try:
    from PIL import Image as PILImage
except ImportError as exc:
    raise ImportError("doc_style.py needs Pillow. Install it with: pip install pillow") from exc
try:
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_LEFT
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.pdfgen import canvas
    from reportlab.platypus import (
        BaseDocTemplate, Frame, Image, KeepTogether, PageBreak, PageTemplate,
        Paragraph, Spacer, Table, TableStyle,
    )
except ImportError as exc:
    raise ImportError("doc_style.py needs reportlab. Install it with: pip install reportlab") from exc

DEFAULT_ACCENT = "#1f3b57"
GREY_TEXT = colors.HexColor("#333333")
GREY_CAPTION = colors.HexColor("#555555")
GREY_FOOTER = colors.HexColor("#666666")
LINE = colors.HexColor("#9aa7b3")
HEAD_BG = colors.HexColor("#edf2f6")
ZEBRA = colors.HexColor("#f8f9fb")
OPEN_COLOR = "#b45309"

PAGE_W, PAGE_H = A4
MARGIN_X = 51
MARGIN_TOP = 50
MARGIN_BOTTOM = 56
WIDTH = PAGE_W - 2 * MARGIN_X
IMAGE_DPI = 220
MIN_DPI = 150

_ALLOWED = r"/?(?:b|i|u|sub|super|br|font|a)\b"


def _fonts() -> None:
    """Register Arial (or the metric-compatible Liberation Sans) as family 'Arial'."""
    if "Arial" in pdfmetrics.getRegisteredFontNames():
        return
    candidates = [
        ("C:/Windows/Fonts", "arial.ttf", "arialbd.ttf", "ariali.ttf", "arialbi.ttf"),
        ("/System/Library/Fonts/Supplemental", "Arial.ttf", "Arial Bold.ttf",
         "Arial Italic.ttf", "Arial Bold Italic.ttf"),
        ("/usr/share/fonts/truetype/liberation", "LiberationSans-Regular.ttf",
         "LiberationSans-Bold.ttf", "LiberationSans-Italic.ttf",
         "LiberationSans-BoldItalic.ttf"),
    ]
    for base, *files in candidates:
        paths = [os.path.join(base, f) for f in files]
        if all(os.path.exists(p) for p in paths):
            names = ["Arial", "Arial-Bold", "Arial-Italic", "Arial-BoldItalic"]
            for name, path in zip(names, paths):
                pdfmetrics.registerFont(TTFont(name, path))
            pdfmetrics.registerFontFamily(
                "Arial", normal="Arial", bold="Arial-Bold",
                italic="Arial-Italic", boldItalic="Arial-BoldItalic")
            return
    raise RuntimeError("Neither Arial nor Liberation Sans was found.")


def _styles(accent) -> dict[str, ParagraphStyle]:
    base = ParagraphStyle("base", fontName="Arial", fontSize=9.4, leading=12.4,
                          textColor=colors.black, alignment=TA_LEFT,
                          allowWidows=0, allowOrphans=0)

    def s(name, **kw):
        return ParagraphStyle(name, parent=base, **kw)

    return {
        "p": s("p", spaceAfter=6),
        "li": s("li", leftIndent=12, bulletIndent=2, spaceAfter=3,
                bulletFontName="Arial", bulletFontSize=9.4),
        "h1": s("h1", fontName="Arial-Bold", fontSize=15, leading=18, textColor=accent,
                spaceBefore=14, spaceAfter=7, keepWithNext=1),
        "h2": s("h2", fontName="Arial-Bold", fontSize=11.5, leading=14, textColor=accent,
                spaceBefore=10, spaceAfter=5, keepWithNext=1),
        "h3": s("h3", fontName="Arial-Bold", fontSize=9.8, leading=12.5, textColor=accent,
                spaceBefore=7, spaceAfter=3, keepWithNext=1),
        "title": s("title", fontName="Arial-Bold", fontSize=22, leading=26.5,
                   textColor=accent, spaceAfter=8),
        "subtitle": s("subtitle", fontSize=12, leading=15, textColor=GREY_TEXT, spaceAfter=14),
        "cap": s("cap", fontName="Arial-Italic", fontSize=8, leading=10,
                 textColor=GREY_CAPTION, spaceBefore=3, spaceAfter=9),
        "tabtitle": s("tabtitle", fontName="Arial-Italic", fontSize=8, leading=10,
                      textColor=GREY_CAPTION, spaceBefore=4, spaceAfter=3, keepWithNext=1),
        "td": s("td", fontSize=8, leading=10),
        "th": s("th", fontName="Arial-Bold", fontSize=8, leading=10),
    }


def _fmt(text: object) -> str:
    """Escape stray '&' and '<'; allow a few inline tags; highlight TBD."""
    t = str(text)
    t = re.sub(r"&(?!#?\w+;)", "&amp;", t)
    t = re.sub(rf"<(?!{_ALLOWED})", "&lt;", t)
    return re.sub(r"\bTBD\b", f'<font color="{OPEN_COLOR}"><b>TBD</b></font>', t)


def _plain(text: str) -> str:
    return re.sub(r"<[^>]+>", "", text).replace("&lt;", "<").replace("&amp;", "&")


class _Template(BaseDocTemplate):
    def afterFlowable(self, f):
        mark = getattr(f, "_bookmark", None)
        if mark:
            title, level, key = mark
            self.canv.bookmarkPage(key)
            self.canv.addOutlineEntry(title, key, level=level, closed=False)


def _canvas_class(footer_text: str):
    class Numbered(canvas.Canvas):
        def __init__(self, *a, **kw):
            super().__init__(*a, **kw)
            self._pages = []

        def showPage(self):
            self._pages.append(dict(self.__dict__))
            self._startPage()

        def save(self):
            total = len(self._pages)
            for state in self._pages:
                self.__dict__.update(state)
                self.setStrokeColor(LINE)
                self.setLineWidth(0.4)
                self.line(MARGIN_X, 44, PAGE_W - MARGIN_X, 44)
                self.setFont("Arial", 7.5)
                self.setFillColor(GREY_FOOTER)
                self.drawString(MARGIN_X, 33, footer_text)
                self.drawRightString(PAGE_W - MARGIN_X, 33,
                                     f"Page {self._pageNumber}/{total}")
                super().showPage()
            super().save()
    return Numbered


def _next_generation(name: str) -> str:
    """'<prefix>26' -> '<prefix>27'; anything else -> 'the next generation'."""
    m = re.search(r"(\d+)$", name or "")
    if not m:
        return "the next generation"
    number = m.group(1)
    return name[:m.start()] + str(int(number) + 1).zfill(len(number))


class Doc:
    """Builds an assembly documentation. Order of calls = order in the PDF."""

    def __init__(self, target, title, subtitle="", short="", date="", cover_image=None,
                 meta=None, accent=DEFAULT_ACCENT, footer="", logo=None, author=""):
        _fonts()
        self.target = Path(target)
        self.title, self.short, self.date, self.author = title, short, date, author
        self.accent = colors.HexColor(accent or DEFAULT_ACCENT)
        self.footer = footer or " · ".join(x for x in (short, date) if x)
        self.st = _styles(self.accent)
        self._tmp = tempfile.TemporaryDirectory()
        self.n_h1 = self.n_h2 = self.n_image = self.n_table = self._n_file = 0
        self.story = []
        self.notes = []
        self._cover(title, subtitle, meta or {}, cover_image, logo)

    # ---------- Images ----------
    def _image(self, path, width_pt):
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Image missing: {path}")
        im = PILImage.open(path)
        if im.mode in ("RGBA", "LA", "P"):
            im = im.convert("RGBA")
            background = PILImage.new("RGB", im.size, "white")
            background.paste(im, mask=im.getchannel("A"))
            im = background
        im = im.convert("RGB")
        dpi = im.width / (width_pt / 72)
        if dpi < MIN_DPI:
            self.notes.append(f"{path.name}: only {dpi:.0f} dpi, please render larger")
        target_px = round(width_pt / 72 * IMAGE_DPI)
        if im.width > target_px:
            im = im.resize((target_px, round(im.height * target_px / im.width)),
                           PILImage.LANCZOS)
        self._n_file += 1
        out = Path(self._tmp.name) / f"b{self._n_file}.jpg"
        im.save(out, "JPEG", quality=88, optimize=True)
        return str(out)

    @staticmethod
    def _ratio(path):
        if not Path(path).exists():
            raise FileNotFoundError(f"Image missing: {path}")
        with PILImage.open(path) as im:
            return im.height / im.width

    def _cover(self, title, subtitle, meta, cover_image, logo):
        s = self.story
        if logo and Path(logo).exists():
            s += [Image(str(logo), 199, 199 * self._ratio(logo), hAlign="CENTER"),
                  Spacer(1, 26)]
        else:
            s.append(Spacer(1, 40))
        s += [Paragraph(_fmt(title), self.st["title"]),
              Paragraph(_fmt(subtitle), self.st["subtitle"])]
        if cover_image:
            b = 425
            h = b * self._ratio(cover_image)
            if h > 300:
                b, h = b * 300 / h, 300
            s.append(Image(self._image(cover_image, b), b, h, hAlign="CENTER"))
        else:
            box = Table([[Paragraph(_fmt("TBD: insert photo of the assembly"), self.st["p"])]],
                        colWidths=[425], rowHeights=[260], hAlign="CENTER")
            box.setStyle(TableStyle([("BOX", (0, 0), (-1, -1), 0.4, LINE),
                                     ("BACKGROUND", (0, 0), (-1, -1), ZEBRA),
                                     ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                                     ("VALIGN", (0, 0), (-1, -1), "MIDDLE")]))
            s.append(box)
        s.append(Spacer(1, 20))
        if meta:
            rows = [[Paragraph(_fmt(k), self.st["td"]), Paragraph(_fmt(v), self.st["td"])]
                    for k, v in meta.items()]
            t = Table(rows, colWidths=[WIDTH * .22, WIDTH * .78], hAlign="LEFT")
            t.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.4, LINE),
                                   ("BACKGROUND", (0, 0), (0, -1), ZEBRA),
                                   ("VALIGN", (0, 0), (-1, -1), "TOP"),
                                   ("TOPPADDING", (0, 0), (-1, -1), 3),
                                   ("BOTTOMPADDING", (0, 0), (-1, -1), 3)]))
            s.append(t)
        s.append(PageBreak())

    # ---------- Headings and text ----------
    def _heading(self, text, style, level):
        p = Paragraph(_fmt(text), self.st[style])
        if level is not None:
            p._bookmark = (_plain(_fmt(text)), level, f"k{len(self.story)}")
        self.story.append(p)

    def h1(self, text):
        self.n_h1 += 1
        self.n_h2 = 0
        self._heading(f"{self.n_h1} {text}", "h1", 0)

    def h2(self, text):
        self.n_h2 += 1
        self._heading(f"{self.n_h1}.{self.n_h2} {text}", "h2", 1)

    def h3(self, text):
        self._heading(text, "h3", None)

    def p(self, text):
        self.story.append(Paragraph(_fmt(text), self.st["p"]))

    def bullets(self, items):
        for item in items:
            self.story.append(Paragraph(_fmt(item), self.st["li"], bulletText="•"))
        self.story.append(Spacer(1, 3))

    def _content(self, value):
        if value is None or value == "" or value == []:
            self.p("TBD")
        elif isinstance(value, str):
            self.p(value)
        else:
            self.bullets(value)

    def generations(self, previous, current):
        """The pair from the template: 'Previous generations' and 'This generation'."""
        self.h3("Previous generations")
        self._content(previous)
        self.h3("This generation")
        self._content(current)

    def generation(self, name, owner, conclusion, potential, next_name=None):
        """One entry of the generation history, e.g. name='<GEN-B>'.

        next_name names the following generation for the 'Potential for ...' heading;
        by default the trailing number of name is incremented.
        """
        self.h2(name)
        self.p(f"<b>Owner:</b> {owner or 'TBD'}")
        self.h3("Conclusion")
        self._content(conclusion)
        self.h3(f"Potential for {next_name or _next_generation(name)}")
        self._content(potential)

    # ---------- Images and tables ----------
    def image(self, path, text, width=.72, max_height=300):
        b = WIDTH * width
        h = b * self._ratio(path)
        if h > max_height:
            b, h = b * max_height / h, max_height
        self.n_image += 1
        self.story.append(KeepTogether([
            Spacer(1, 4), Image(self._image(path, b), b, h, hAlign="LEFT"),
            Paragraph(_fmt(f"Figure {self.n_image} – {text}"), self.st["cap"])]))

    def images(self, pairs, max_height=220):
        """Two or three images side by side: [(path, text), ...]."""
        n = len(pairs)
        gap = 10
        cell = (WIDTH - gap * (n - 1)) / n
        h = min([max_height] + [cell * self._ratio(p) for p, _ in pairs])
        row_img, row_cap = [], []
        for path, text in pairs:
            b = h / self._ratio(path)
            self.n_image += 1
            row_img.append(Image(self._image(path, b), b, h, hAlign="LEFT"))
            row_cap.append(Paragraph(_fmt(f"Figure {self.n_image} – {text}"), self.st["cap"]))
        widths = [cell + gap] * (n - 1) + [cell]
        t = Table([row_img, row_cap], colWidths=widths, hAlign="LEFT")
        t.setStyle(TableStyle([("LEFTPADDING", (0, 0), (-1, -1), 0),
                               ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                               ("TOPPADDING", (0, 0), (-1, -1), 0),
                               ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                               ("VALIGN", (0, 0), (-1, -1), "TOP")]))
        self.story.append(KeepTogether([Spacer(1, 4), t]))

    def table(self, rows, widths=None, title=None):
        """First row = header. widths are relative shares, e.g. [2, 3, 3]."""
        n = len(rows[0])
        shares = widths or [1] * n
        cols = [WIDTH * a / sum(shares) for a in shares]
        data = []
        for i, row in enumerate(rows):
            style = self.st["th" if i == 0 else "td"]
            for j, cell in enumerate(row):
                for word in re.split(r"[\s/\-–]+", _plain(_fmt(cell))):
                    if pdfmetrics.stringWidth(word, style.fontName, style.fontSize) > cols[j] - 12:
                        raise ValueError(f"'{word}' does not fit into column {j + 1}. "
                                         "Make the column wider or shorten the header.")
            data.append([Paragraph(_fmt(c), style) for c in row])
        t = Table(data, colWidths=cols, repeatRows=1, hAlign="LEFT",
                  spaceBefore=3, spaceAfter=11)
        style = [("GRID", (0, 0), (-1, -1), 0.4, LINE),
                 ("BACKGROUND", (0, 0), (-1, 0), HEAD_BG),
                 ("VALIGN", (0, 0), (-1, -1), "TOP"),
                 ("LEFTPADDING", (0, 0), (-1, -1), 5), ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                 ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5)]
        style += [("BACKGROUND", (0, r), (-1, r), ZEBRA) for r in range(2, len(data), 2)]
        t.setStyle(TableStyle(style))
        if title:
            self.n_table += 1
            self.story.append(Paragraph(_fmt(f"Table {self.n_table} – {title}"),
                                        self.st["tabtitle"]))
        self.story.append(t)

    # ---------- Output ----------
    def build(self, appendix=None):
        """Write the PDF. appendix: {bookmark name: path to a PDF to append}."""
        self.target.parent.mkdir(parents=True, exist_ok=True)
        frame = Frame(MARGIN_X, MARGIN_BOTTOM, WIDTH, PAGE_H - MARGIN_TOP - MARGIN_BOTTOM,
                      leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
        template = _Template(str(self.target), pagesize=A4, title=self.title,
                             author=self.author,
                             pageTemplates=[PageTemplate(id="page", frames=[frame])])
        template.build(self.story, canvasmaker=_canvas_class(self.footer))
        if appendix:
            pdf = fitz.open(self.target)
            toc = pdf.get_toc()
            for name, path in appendix.items():
                toc.append([1, f"Appendix: {name}", pdf.page_count + 1])
                with fitz.open(path) as extra:
                    pdf.insert_pdf(extra)
            pdf.set_toc(toc)
            temp = self.target.with_suffix(".tmp.pdf")
            pdf.save(temp, garbage=3, deflate=True)
            pdf.close()
            temp.replace(self.target)
        self._tmp.cleanup()
        for note in self.notes:
            print("NOTE:", note)
        print("PDF:", self.target)
        return self.target
