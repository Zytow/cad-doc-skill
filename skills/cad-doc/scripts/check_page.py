#!/usr/bin/env python3
"""Check a documentation page (markdown) against the template and the style rules.

Usage: python check_page.py <page.md> [--legacy] [--template]
Chapters are freely chosen. The checks cover title, decisions, simulations and calculations.
--legacy skips status and history, for old pages that were migrated afterwards.
--template additionally requires exactly the chapters of the assembly documentation template.
Exit code 0 = passed, 1 = at least one error.
"""
from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path

CHAPTERS = ["Overview", "Concept", "Design", "Manufacturing", "Validation", "History"]
PAIR = ("Previous generations", "This generation")
PLACEHOLDER = re.compile(
    r"<insert|\*insert |insert (a photo|an introduction|links) here|how did the generation go|"
    r"what potential is there|how the (concept|design) decision changed|"
    r"(Concept|Design) decision of the previous generation|"
    r"Requirements that changed (in previous generations|this generation)|"
    r"History of the manufacturing of the previous|"
    r"Validation of the previous generation", re.I)
IMAGE = re.compile(r'!\[([^\]]*)\]\(([^)\s]+)(?:\s+"([^"]*)")?\)')
WEAK_ALT = re.compile(r"^(image|picture|photo|screenshot|img[_ -]?\d*|dsc[_ -]?\d*|\d+)$|\.(jpe?g|png)$", re.I)
MAX_BULLET = 300
MAX_PARAGRAPH = 500
MAX_DEPTH = 3
MAX_MB = 10
SIM_FIELDS = ("Question", "Tool", "Model", "Material", "Load case", "Supports", "Contacts", "Mesh",
              "Mesh convergence", "Limit", "Result", "Assessment")
# Meta phrases: write about the matter, not about how the statement came about.
META = re.compile(
    r"\bpresumably\b|\bprobably\b|\bderived\b|\bin CAD\b|\b(STEP )?export\b|"
    r"\baccording to (?!(the )?(datasheet|manufacturer|rule|standard|catalog|handbook))(?-i:[A-Z][a-z]+)",
    re.I)
LINK = re.compile(r"(?<!!)\[[^\]]*\]\(([^)\s]+)\)")
STATUS = re.compile(r"\*\*Status:\*\*\s*(open|in progress|decided|validated|rejected)", re.I)
WEIGHT_KEYS = {"weighting"}
TOTAL_KEYS = ("total", "overall", "sum")
DATE_RE = re.compile(r"\b\d{4}-\d{2}-\d{2}\b|\b\d{2}\.\d{2}\.\d{4}\b")
ATTACHMENT_DIRS = ("attachments", "images", "drawings", "datasheets")


@dataclass
class Heading:
    level: int
    text: str
    line: int
    content: list[str] = field(default_factory=list)
    children: list["Heading"] = field(default_factory=list)


class Report:
    def __init__(self):
        self.errors, self.warnings, self.open = [], [], []
        self.fm_title = False

    def err(self, line, text):
        self.errors.append(f"Line {line}: {text}" if line else text)

    def warn(self, line, text):
        self.warnings.append(f"Line {line}: {text}" if line else text)


def norm(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().casefold()


def read_lines(lines: list[str]) -> tuple[list[tuple[int, str]], list[Heading]]:
    """Return text lines outside code blocks and all headings."""
    text, headings, code = [], [], False
    for nr, z in enumerate(lines, 1):
        if z.lstrip().startswith("```"):
            code = not code
            continue
        if code:
            continue
        m = re.match(r"(#{1,6})\s+(.*\S)\s*$", z)
        if m:
            headings.append(Heading(len(m.group(1)), m.group(2), nr))
        else:
            text.append((nr, z))
            if headings and z.strip():
                headings[-1].content.append(z)
    return text, headings


def chapter_tree(headings: list[Heading]) -> tuple[list[Heading], Heading | None]:
    h1 = [k for k in headings if k.level == 1]
    title = h1[0] if h1 and norm(h1[0].text) not in {norm(x) for x in CHAPTERS} else None
    tree = [k for k in h1 if k is not title]
    current = None
    for k in headings:
        if k.level == 1:
            current = k if k is not title else None
        elif current:
            current.children.append(k)
    return tree, title


def section(chap: Heading, start: int) -> list[Heading]:
    """Headings below chap.children[start], up to the next heading of the same or a higher level."""
    base = chap.children[start].level
    out = []
    for k in chap.children[start + 1:]:
        if k.level <= base:
            break
        out.append(k)
    return out


def has_content(k: Heading, below: list[Heading]) -> bool:
    return bool(k.content) or any(x.content for x in below)


def pair(name: str, line: int, headings: list[Heading], r: Report):
    for want in PAIR:
        hits = [i for i, k in enumerate(headings) if norm(k.text) == norm(want)]
        if not hits:
            r.err(line, f"'{name}': subsection '{want}' is missing")
            continue
        i = hits[0]
        below = []
        for k in headings[i + 1:]:
            if k.level <= headings[i].level:
                break
            below.append(k)
        if not has_content(headings[i], below):
            r.err(headings[i].line, f"'{name}' > '{want}' is empty (enter content or TBD)")


def live(d: Heading, below: list[Heading], r: Report):
    """A design decision must show its status and its history."""
    m = STATUS.search(" ".join(d.content))
    if not m:
        r.err(d.line, f"'{d.text}': line '**Status:** open|in progress|decided|validated|rejected' is missing")

    def filled(word):
        return any(word in norm(k.text) and k.content and not all("TBD" in z for z in k.content) for k in below)

    history = [k for k in below if norm(k.text) == "history"]
    dates = [x for k in history for z in k.content for x in DATE_RE.findall(z)]
    if not dates:
        r.err(d.line, f"'{d.text}': section 'History' with a date is missing")
    for x in dates:
        try:
            fmt = "%Y-%m-%d" if "-" in x else "%d.%m.%Y"
            if datetime.strptime(x, fmt).date() > date.today():
                r.err(d.line, f"'{d.text}': date {x} is in the future")
        except ValueError:
            r.err(d.line, f"'{d.text}': invalid date {x}")
    state = m.group(1).casefold() if m else ""
    if state in ("decided", "validated"):
        if not (filled("variants") or filled("evaluation")):
            r.err(d.line, f"'{d.text}': marked as {state}, but variants or evaluation are missing")
        if not any(norm(k.text) == "decision" and k.content and not all("TBD" in z for z in k.content)
                   for k in below):
            r.err(d.line, f"'{d.text}': marked as {state}, but section 'Decision' is empty")
    if state == "validated" and not (filled("verification") or filled("simulation:")):
        r.err(d.line, f"'{d.text}': marked as validated, but the verification is missing")


def simulation(k: Heading, r: Report):
    """The simulation card makes a simulation traceable."""
    fields = {norm(cells(z)[0]) for z in k.content if z.strip().startswith("|")}
    for want in SIM_FIELDS:
        if norm(want) not in fields:
            r.err(k.line, f"'{k.text}': card row '{want}' is missing")
    if not IMAGE.search("\n".join(k.content)) and "screenshot" not in fields:
        r.err(k.line, f"'{k.text}': result image or row 'Screenshot | TBD' is missing")


def utilisation(nr: int, rows: list[list[str]], r: Report):
    head = [norm(c) for c in rows[0]]

    def col(word):
        return next((i for i, c in enumerate(head) if word in c), None)

    s = col("stress")
    g = col("limit")
    a = col("utilisation")
    if a is None:
        a = col("utilization")
    if None in (s, g, a):
        return
    for row in rows[1:]:
        w = [number(row[i]) for i in (s, g, a)]
        if None not in w and w[1] != 0 and abs(w[0] / w[1] * 100 - w[2]) > 1:
            r.err(nr, f"Variant '{row[0]}': utilisation is {row[a]} %, computed {w[0] / w[1] * 100:.0f} %")


def cells(z: str) -> list[str]:
    return [c.strip() for c in re.split(r"(?<!\\)\|", z.strip().strip("|"))]


def number(c: str) -> float | None:
    try:
        return float(c.replace("%", "").replace(",", ".").strip())
    except ValueError:
        return None


def matrix(nr: int, rows: list[list[str]], r: Report):
    head = [norm(c) for c in rows[0]]
    g = next(i for i, c in enumerate(head) if c in WEIGHT_KEYS)
    total = [row for row in rows[1:] if norm(row[0]) in TOTAL_KEYS]
    if not total:
        r.err(nr, "Evaluation matrix without a row 'Total'")
        return
    # rows without a numeric weighting (for example k.o.) are not scored
    crit = [row for row in rows[1:] if row not in total and number(row[g]) is not None]
    weights = sum(number(row[g]) for row in crit)
    if abs(weights - 100) > .01:
        r.err(nr, f"Weights add up to {weights:g} % instead of 100 %")
    for s in range(g + 1, len(head)):
        values = [number(row[s]) for row in crit]
        if any(w is None or not 1 <= w <= 5 for w in values):
            r.err(nr, f"Column '{rows[0][s]}': points must be between 1 and 5")
            continue
        want = sum(w * number(row[g]) / 100 for w, row in zip(values, crit))
        got = number(total[0][s])
        if got is None or abs(got - want) > .011:
            r.err(nr, f"Column '{rows[0][s]}': total is {total[0][s]}, computed {want:.2f}")


def fmea(nr: int, rows: list[list[str]], r: Report):
    head = [norm(c) for c in rows[0]]
    for suffix in ("", " new"):
        names = [x + suffix for x in ("s", "o", "d", "rpn")]
        if not all(n in head for n in names):
            if not suffix:
                r.err(nr, "FMEA needs the columns S, O, D and RPN")
            continue
        s, o, d, p = (head.index(n) for n in names)
        for row in rows[1:]:
            w = [number(row[i]) for i in (s, o, d)]
            if any(x is None or not 1 <= x <= 10 for x in w):
                r.err(nr, f"FMEA '{row[0]}': S, O and D must be between 1 and 10")
            elif number(row[p]) != w[0] * w[1] * w[2]:
                r.err(nr, f"FMEA '{row[0]}': RPN{suffix} is {row[p]}, computed {w[0] * w[1] * w[2]:g}")


def tables(text: list[tuple[int, str]], r: Report):
    group: list[tuple[int, str]] = []
    for nr, z in text + [(0, "")]:
        if z.strip().startswith("|"):
            group.append((nr, z))
            continue
        if len(group) >= 2:
            rows = [cells(x) for _, x in group if not re.fullmatch(r"[\s|:\-]+", x)]
            if len({len(row) for row in rows}) == 1:
                head = [norm(c) for c in rows[0]]
                if WEIGHT_KEYS & set(head):
                    matrix(group[0][0], rows, r)
                if "rpn" in head:
                    fmea(group[0][0], rows, r)
                utilisation(group[0][0], rows, r)
        group = []


def below_of(headings: list[Heading], i: int) -> list[Heading]:
    out = []
    for k in headings[i + 1:]:
        if k.level <= headings[i].level:
            break
        out.append(k)
    return out


def free(headings: list[Heading], tree: list[Heading], title: Heading | None, lines: list[str],
         r: Report, legacy: bool):
    """Free structure: chapter names do not matter, the building blocks inside them do."""
    if title is None and not r.fm_title:
        r.err(1, "Assembly title is missing as the first heading (or frontmatter 'assembly')")
    if not tree:
        r.err(0, "The page has no chapter yet")
    elif not IMAGE.search("\n".join(lines[(title.line if title else 0):tree[0].line - 1])):
        r.warn(title.line if title else 1, "Title photo is missing before the first chapter")
    names = [norm(k.text) for k in headings]
    if not any("links" in n for n in names):
        r.warn(0, "Section with relevant links is missing")
    if not any((k.level <= 2 and norm(k.text) == "history") or
               any(w in norm(k.text) for w in ("conclusion", "potential", "takeaways")) for k in headings):
        r.warn(0, "Conclusion or potential for the next generation is missing")
    for i, k in enumerate(headings):
        below = below_of(headings, i)
        if k is not title and not k.content and not below:
            r.err(k.line, f"'{k.text}' is empty (enter content or TBD)")
        if norm(k.text).startswith("design decision") and not legacy:
            live(k, below, r)


def structure(tree: list[Heading], title: Heading | None, lines: list[str], r: Report, legacy: bool = False):
    have = [k.text for k in tree]
    if [norm(x) for x in have] != [norm(x) for x in CHAPTERS]:
        r.err(0, f"Chapters differ from the template. Expected: {CHAPTERS}. Found: {have}")
    k = {norm(x.text): x for x in tree}
    if title is None and not r.fm_title:
        r.err(1, "Assembly title is missing as the first heading")
    ov = k.get("overview")
    if ov:
        before = "\n".join(lines[title.line:ov.line - 1]) if title else ""
        if title and not IMAGE.search(before) and "TBD" not in before:
            r.err(title.line, "Title photo of the assembly is missing before the Overview")
        if not ov.content:
            r.err(ov.line, "Overview has no introduction")
        if not any("links" in norm(x.text) for x in ov.children):
            r.err(ov.line, "'Relevant links' is missing in the Overview")
    con = k.get("concept")
    if con:
        for name in ("Requirements", "Concept decision"):
            idx = [i for i, x in enumerate(con.children) if norm(x.text).startswith(norm(name))]
            if idx:
                pair(name, con.children[idx[0]].line, section(con, idx[0]), r)
            else:
                r.err(con.line, f"Section '{name}' is missing")
    des = k.get("design")
    if des:
        idx = [i for i, x in enumerate(des.children) if norm(x.text).startswith("design decision #")]
        if not idx:
            r.err(des.line, "No 'Design decision #1' found")
        for i in idx:
            pair(des.children[i].text, des.children[i].line, section(des, i), r)
            if not legacy:
                live(des.children[i], section(des, i), r)
    for name in ("manufacturing", "validation"):
        if name in k:
            pair(k[name].text, k[name].line, k[name].children, r)
    if "manufacturing" in k:
        start = k["manufacturing"].line
        end = k["validation"].line if "validation" in k else len(lines)
        if not IMAGE.search("\n".join(lines[start:end])):
            r.warn(start, "Manufacturing without a photo")
    his = k.get("history")
    if his:
        gens = [x for x in his.children if x.level == his.level + 1]
        if not gens:
            r.err(his.line, "No generation entered in the History")
        for s in gens:
            idx = his.children.index(s)
            below = section(his, idx)
            names = [norm(x.text) for x in below]
            if "conclusion" not in names:
                r.err(s.line, f"{s.text}: 'Conclusion' is missing")
            if not any(n.startswith("potential for") for n in names):
                r.err(s.line, f"{s.text}: 'Potential for <next generation>' is missing")
            m = re.search(r"\bOwner\b[^:]*:\**\s*(\S.*)?", " ".join(s.content))
            if not m or not m.group(1):
                r.err(s.line, f"{s.text}: 'Owner' without a name (enter a name or TBD)")
            for x in below:
                if not x.content:
                    r.err(x.line, f"{s.text} > '{x.text}' is empty (enter content or TBD)")


def exportable(file: Path, page: Path) -> bool:
    """In the folder of the page or in the shared sibling folders rules/ and sources/."""
    base = page.parent.resolve()
    allowed = [base, base.parent / "rules", base.parent / "sources"]
    return any(file == e or e in file.parents for e in allowed)


def content(text: list[tuple[int, str]], headings: list[Heading], page: Path, r: Report):
    anchors = {norm(k.text) for k in headings}
    used, boxes, table = set(), 0, None
    for nr, z in text:
        s = z.strip()
        if re.match(r"#{7,}\s", z):
            r.err(nr, "Heading deeper than ###### is not rendered")
        if "{{" in z:
            r.err(nr, f"Placeholder not replaced: '{s[:50]}'")
        if PLACEHOLDER.search(z):
            r.err(nr, f"Placeholder from the template: '{s[:50]}'")
        if re.search(r"\bTBD\b", z):
            r.open.append(f"Line {nr}: {s[:80]}")
        if s.startswith(":::"):
            boxes += 1
        for m in re.finditer(r"!\[\[([^\]]+)\]\]", z):
            r.err(nr, f"Obsidian image is not displayed in the wiki: {m.group(1)}")
        for m in re.finditer(r"(?<!!)\[\[#([^\]]+)\]\]", z):
            if norm(m.group(1)) not in anchors:
                r.err(nr, f"Reference without a matching heading: #{m.group(1)}")
        if re.search(r"(?<!!)\[[^\]]+\]\(\s*\)", z):
            r.err(nr, "Link without a target")
        if META.search(z) and not s.startswith("|"):
            r.warn(nr, f"Meta phrase, better write about the matter: '{META.search(z).group(0)}'")
        for target in LINK.findall(z):
            if re.match(r"(https?|mailto):|#", target):
                continue
            file = (page.parent / target.split("#")[0]).resolve()
            used.add(file)
            if not file.exists():
                r.err(nr, f"Link target is missing: {target}")
            elif not exportable(file, page):
                r.warn(nr, f"File lies outside the assembly folder (not exportable): {target}")
        for alt, target, title in IMAGE.findall(z):
            if not alt.strip() or WEAK_ALT.search(alt.strip()):
                r.err(nr, f"Image needs a description: '{alt or target}'")
            if re.match(r"https?:", target):
                continue
            file = (page.parent / target).resolve()
            used.add(file)
            if not file.exists():
                r.err(nr, f"Image file is missing: {target}")
            elif not exportable(file, page):
                r.warn(nr, f"Image lies outside the assembly folder (not exportable): {target}")
            elif file.stat().st_size > MAX_MB * 1e6:
                r.warn(nr, f"Image larger than {MAX_MB} MB: {target}")
            if not re.search(r"=\d+x\d+", title or ""):
                r.warn(nr, f"Image without a size: {target}")
        m = re.match(r"(\s*)[*-] (.*)", z)
        if m:
            if len(m.group(1)) // 2 > MAX_DEPTH:
                r.warn(nr, "Bullet nested deeper than four levels")
            if len(IMAGE.sub("", re.sub(r"\]\([^)]*\)", "]", m.group(2)))) > MAX_BULLET:
                r.warn(nr, "Bullet is very long, better split it into sub-bullets")
        elif s and not s.startswith(("|", ":::", "!", "[^")) and len(s) > MAX_PARAGRAPH:
            r.warn(nr, "Paragraph is very long, better write it as bullets")
        if s.startswith("|"):
            columns = len(re.findall(r"(?<!\\)\|", s)) - 1
            if table is not None and columns != table:
                r.err(nr, f"Table row has {columns} instead of {table} columns")
            table = columns if table is None else table
        else:
            table = None
    if boxes % 2:
        r.err(0, "Info box ':::' is not closed")
    for other in page.parent.glob("*.md"):  # subpages in the same folder share the attachments
        if other.resolve() == page.resolve():
            continue
        for z in other.read_text(encoding="utf-8").splitlines():
            for target in LINK.findall(z) + [m[1] for m in IMAGE.findall(z)]:
                if not re.match(r"(https?|mailto):|#", target):
                    used.add((page.parent / target.split("#")[0]).resolve())
    for name in ATTACHMENT_DIRS:
        folder = page.parent / name
        if not folder.is_dir():
            continue
        for d in sorted(folder.iterdir()):
            if d.is_file() and d.name != ".DS_Store" and d.resolve() not in used \
                    and not (d.suffix.lower() == ".pdf" and d.with_suffix(".png").resolve() in used) \
                    and not (d.suffix.lower() == ".png" and d.with_suffix(".pdf").resolve() in used):
                r.warn(0, f"Attachment is not used: {name}/{d.name}")


def image_rules(lines: list[str], r: Report):
    """Rules from references/images.md: no duplicates, text before image, sizes, drawings collected."""
    seen, heading, last, run, code = {}, "", "", 0, False
    for nr, z in enumerate(lines, 1):
        s = z.strip()
        if s.startswith("```"):
            code = not code
            continue
        if code or not s:
            continue
        m = re.match(r"(#{1,6})\s+(.*)", s)
        if m:
            heading, last, run = m.group(2), "heading", 0
            continue
        images = IMAGE.findall(s) if s.startswith("![") else []
        if not images:
            last, run = ("table" if s.startswith("|") else "text"), 0
            continue
        run += 1
        if last == "table":
            r.warn(nr, "Image directly under a table, first one sentence saying what it shows")
        if run == 3:
            r.warn(nr, "More than two image lines in a row, put explanatory text in between")
        if last == "heading":
            r.warn(nr, "Image directly under a heading, first one sentence saying what it shows")
        if len(images) > 3:
            r.warn(nr, f"{len(images)} images in one line, at most three")
        for alt, target, title in images:
            if target in seen:
                r.warn(nr, f"Image embedded twice (first on line {seen[target]}): {target}")
            seen.setdefault(target, nr)
            width = re.search(r"=(\d+)x", title or "")
            width = int(width.group(1)) if width else 0
            limit = 900 if "drawings/" in target else 900 if re.search(r"-location", target) else 600
            if width > limit:
                r.warn(nr, f"Image is {width} px wide, guideline at most {limit}: {target}")
            if "drawings/" in target and "drawing" not in norm(heading):
                r.warn(nr, f"Drawing outside the section Technical drawings: {target}")
        last = "image"


def frontmatter(lines: list[str], r: Report):
    """Simple YAML check: Obsidian discards the whole frontmatter when one value is invalid."""
    for nr, z in enumerate(lines, 2):
        if not z.strip() or z.lstrip().startswith(("#", "- ")):
            continue
        m = re.match(r"([A-Za-z0-9_\-]+):(?:\s+(.*))?$", z)
        if not m:
            r.err(nr, f"Frontmatter line is not 'key: value': '{z.strip()[:50]}'")
            continue
        value = (m.group(2) or "").strip()
        if value[:1] in ("'", '"') and value[-1:] == value[:1]:
            continue
        if ": " in value or " #" in value or (value and value[0] in "[]{}&*!|>%@`"):
            r.err(nr, f"Frontmatter invalid, put the value in quotes or rephrase: '{z.strip()[:60]}'")


def check(page: Path, legacy: bool = False, template: bool = False) -> Report:
    r = Report()
    lines = page.read_text(encoding="utf-8").splitlines()
    lines_fm = []
    if lines and lines[0].strip() == "---":  # frontmatter: title from 'assembly', lines are not checked as text
        end = next((i for i, z in enumerate(lines[1:], 1) if z.strip() == "---"), 0)
        lines_fm = lines[1:end]
        r.fm_title = any(re.match(r"assembly:\s*\S", z) for z in lines[1:end])
        frontmatter(lines[1:end], r)
        lines = [""] * (end + 1) + lines[end + 1:]
    text, headings = read_lines(lines)
    standalone = any(re.match(r"level:\s*product\b", z) for z in lines_fm)
    if not standalone and (r.fm_title or any(norm(k.text).startswith("mounting") for k in headings)) \
            and not any(re.search(r"-location\.\w+", z) for _, z in text):
        r.warn(0, "Location image of the complete product is missing "
                  "(images/<prefix>-<gen>-location.png, see references/location-images-nx.md)")
    tree, title = chapter_tree(headings)
    if template:
        structure(tree, title, lines, r, legacy)
    else:
        free(headings, tree, title, lines, r, legacy)
    content(text, headings, page, r)
    image_rules(lines, r)
    tables(text, r)
    for k in headings:
        if norm(k.text).startswith("simulation:"):
            simulation(k, r)
    return r


def main() -> int:
    args = [a for a in sys.argv[1:] if a not in ("--legacy", "--template")]
    if len(args) != 1:
        print(__doc__)
        return 2
    r = check(Path(args[0]), "--legacy" in sys.argv, "--template" in sys.argv)
    for label, items in (("ERROR", r.errors), ("WARNING", r.warnings), ("OPEN", r.open)):
        for item in items:
            print(f"{label}  {item}")
    print(f"RESULT: {'FAILED' if r.errors else 'PASSED'} "
          f"({len(r.errors)} errors, {len(r.warnings)} warnings, {len(r.open)} open)")
    return 1 if r.errors else 0


if __name__ == "__main__":
    sys.exit(main())
