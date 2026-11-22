"""Render a note (Markdown) as PDF: python tools/md2pdf.py doc/<assembly>/<assembly>.md [target.pdf]

Small Markdown converter for the documentation format (frontmatter, :::info, images
with " =WxH", tables, lists, tasks) and printing through headless Edge (A4 portrait).

The accent colour of headings, links and the title rule is read from the environment
variable MD2PDF_ACCENT (hex, default #1f3b57).
"""
import html, os, re, subprocess, sys, tempfile
from pathlib import Path

EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
ACCENT = os.environ.get("MD2PDF_ACCENT", "#1f3b57")

CSS = """
@page { size: A4; margin: 16mm 15mm 16mm 15mm; }
body { font-family: Arial, Helvetica, sans-serif; font-size: 10pt; color: #222; line-height: 1.4; }
h1 { font-size: 17pt; color: @ACCENT@; border-bottom: 2px solid @ACCENT@; padding-bottom: 3px; margin: 22px 0 10px; break-after: avoid; }
h2 { font-size: 13pt; margin: 18px 0 6px; break-after: avoid; }
h3 { font-size: 11pt; margin: 14px 0 4px; break-after: avoid; }
h4, h5 { font-size: 10pt; margin: 10px 0 4px; break-after: avoid; }
p { margin: 5px 0; }
code { font-family: Consolas, monospace; font-size: 9pt; background: #f1f1f1; padding: 0 3px; }
a { color: @ACCENT@; text-decoration: none; }
table { border-collapse: collapse; width: 100%; margin: 6px 0 10px; font-size: 9pt; break-inside: auto; }
th, td { border: 1px solid #bbb; padding: 3px 5px; text-align: left; vertical-align: top; }
th { background: #eee; }
tr { break-inside: avoid; }
ul { margin: 4px 0; padding-left: 20px; }
li { margin: 2px 0; }
li.task { list-style: none; margin-left: -16px; }
.info { border-left: 4px solid @ACCENT@; background: #f6f6f6; padding: 6px 10px; margin: 8px 0; }
.images { display: flex; gap: 8px; margin: 8px 0; break-inside: avoid; }
figure { margin: 0; flex: 1; break-inside: avoid; text-align: center; }
figure img { width: 100%; }
figure.single { margin: 8px auto; }
figure.drawing { width: 100%; }
figcaption { font-size: 8.5pt; color: #555; margin-top: 2px; }
.head { display: flex; justify-content: space-between; align-items: flex-end; border-bottom: 2px solid @ACCENT@; padding-bottom: 6px; margin-bottom: 10px; }
.head .title { font-size: 24pt; font-weight: bold; }
.head .sub { font-size: 10pt; color: #555; }
.meta td:first-child { width: 32%; background: #f6f6f6; }
""".replace("@ACCENT@", ACCENT)

LABELS = {"assembly": "Assembly", "area": "Area", "generation": "Generation",
          "nx_assembly": "Assembly in NX", "owner_next": "Owner (next generation)",
          "contact": "Contact"}


def frontmatter_label(key):
    """Label for a frontmatter key; owner_<gen> and material_<gen> carry the generation in the key."""
    if key in LABELS:
        return LABELS[key]
    for prefix, text in (("owner_", "Owner"), ("material_", "Material")):
        if key.startswith(prefix):
            return f"{text} {key[len(prefix):]}"
    return key


def note_title(name, base):
    """Title of a linked note (first H1), otherwise the name."""
    root = next((p for p in [base, *base.parents] if (p / "doc").is_dir()), base)
    for f in root.rglob(name + ".md"):
        for line in f.read_text(encoding="utf-8").splitlines():
            if line.startswith("# "):
                return line[2:].strip()
    return name


def inline(t, base):
    t = html.escape(t, quote=False)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    t = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", t)
    t = re.sub(r"\[\[([^\]|#]*)#?([^\]|]*)\|?([^\]]*)\]\]",
               lambda m: m.group(3) or m.group(2) or note_title(m.group(1), base), t)

    def link(m):
        txt, target = m.group(1), m.group(2)
        if not re.match(r"[a-z]+:", target):
            target = (base / target).resolve().as_uri()
        return f'<a href="{target}">{txt}</a>'
    return re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", link, t)


IMAGE = re.compile(r'!\[([^\]]*)\]\(([^)\s]+)(?:\s+"([^"]*)")?\)')


def images(line, base):
    found = IMAGE.findall(line)
    figs = []
    for alt, path, opt in found:
        width = re.search(r"=(\d+)x", opt or "")
        b = int(width.group(1)) if width else 600
        src = (base / path).resolve().as_uri()
        cls = "drawing" if b >= 900 else "single"
        style = "" if len(found) > 1 or b >= 900 else f' style="width:{min(100, b / 6.6):.0f}%"'
        figs.append(f'<figure class="{cls}"{style}><img src="{src}"><figcaption>{html.escape(alt)}</figcaption></figure>')
    if len(figs) > 1:
        return '<div class="images">' + "".join(figs) + "</div>"
    return figs[0]


def table(lines, base):
    cells = [[c.strip() for c in z.strip().strip("|").split("|")] for z in lines]
    head, body = cells[0], cells[2:]
    h = "<table><tr>" + "".join(f"<th>{inline(c, base)}</th>" for c in head) + "</tr>"
    for r in body:
        h += "<tr>" + "".join(f"<td>{inline(c, base)}</td>" for c in r) + "</tr>"
    return h + "</table>"


def convert(md, base):
    fm = {}
    m = re.match(r"---\n(.*?)\n---\n", md, re.S)
    if m:
        for z in m.group(1).splitlines():
            k, _, v = z.partition(":")
            fm[k.strip()] = v.strip()
        md = md[m.end():]
    lines = md.splitlines()
    out, i, first_h1 = [], 0, True
    title = fm.get("assembly", base.name)
    first = IMAGE.search(md)
    if first and first.group(1).startswith(title):
        generation = fm.get("generation", "")
        if generation:
            title = re.sub(r"\s+" + re.escape(generation) + r".*$", "", first.group(1))
        else:
            title = first.group(1)
    out.append(f'<div class="head"><div><div class="title">{html.escape(title)}</div>'
               f'<div class="sub">{html.escape(fm.get("generation", ""))} · Documentation</div></div></div>')
    if fm:
        out.append('<table class="meta">' + "".join(
            f"<tr><td>{frontmatter_label(k)}</td><td>{html.escape(v)}</td></tr>" for k, v in fm.items()) + "</table>")
    while i < len(lines):
        z = lines[i]
        s = z.strip()
        if not s:
            i += 1
            continue
        if s.startswith(":::"):
            content = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith(":::"):
                if lines[i].strip():
                    content.append(inline(lines[i].strip(), base))
                i += 1
            out.append('<div class="info">' + "<br>".join(content) + "</div>")
            i += 1
            continue
        h = re.match(r"(#{1,5})\s+(.*)", s)
        if h:
            n = len(h.group(1))
            cls = ' class="new"' if n == 1 and not first_h1 else ""
            if n == 1:
                first_h1 = False
            out.append(f"<h{n}{cls}>{inline(h.group(2), base)}</h{n}>")
            i += 1
            continue
        if s.startswith("!["):
            out.append(images(s, base))
            i += 1
            continue
        if s.startswith("|"):
            blk = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                blk.append(lines[i])
                i += 1
            out.append(table(blk, base))
            continue
        if re.match(r"[*-]\s", s):
            items = []
            while i < len(lines) and re.match(r"\s*[*-]\s", lines[i]):
                depth = (len(lines[i]) - len(lines[i].lstrip())) // 2
                text = re.sub(r"^\s*[*-]\s+", "", lines[i])
                items.append((depth, text))
                i += 1
            h_, level = "", -1
            for depth, text in items:
                while level < depth:
                    h_ += "<ul>"
                    level += 1
                while level > depth:
                    h_ += "</ul>"
                    level -= 1
                t = re.match(r"\[([ xX])\]\s+(.*)", text)
                if t:
                    box = "☑" if t.group(1).lower() == "x" else "☐"
                    h_ += f'<li class="task">{box} {inline(t.group(2), base)}</li>'
                else:
                    h_ += f"<li>{inline(text, base)}</li>"
            h_ += "</ul>" * (level + 1)
            out.append(h_)
            continue
        paragraph = []
        while i < len(lines) and lines[i].strip() and not re.match(r"(#|!\[|\||[*-]\s|:::)", lines[i].strip()):
            paragraph.append(lines[i].strip())
            i += 1
        out.append("<p>" + inline(" ".join(paragraph), base) + "</p>")
    return title, "\n".join(out)


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print(__doc__)
        return
    source = Path(sys.argv[1]).resolve()
    target = Path(sys.argv[2]).resolve() if len(sys.argv) > 2 else source.with_suffix(".pdf")
    title, body = convert(source.read_text(encoding="utf-8"), source.parent)
    page = (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>{title}</title>'
            f"<style>{CSS}</style></head><body>{body}</body></html>")
    with tempfile.TemporaryDirectory() as tmp:
        h = Path(tmp) / "page.html"
        h.write_text(page, encoding="utf-8")
        subprocess.run([EDGE, "--headless", "--disable-gpu", "--no-pdf-header-footer",
                        f"--user-data-dir={tmp}\\profile", f"--print-to-pdf={target}", h.as_uri()],
                       check=True, capture_output=True, timeout=180)
    print(target)


if __name__ == "__main__":
    main()
