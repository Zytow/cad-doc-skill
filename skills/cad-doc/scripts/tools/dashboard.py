"""Generates Dashboard.md from the notes in doc/.

Sources are the frontmatter (assembly, area, generation, nx_assembly, owner_<gen>,
owner_next, contact, material_<gen>) and the checkboxes (- [ ] / - [x]) in each
note. The folders doc/rules and doc/sources are skipped. Dashboard.md is rewritten
completely on every run and is not edited by hand. Run it in the project folder:

    python -I tools/dashboard.py
"""
import re
import sys
from datetime import date
from pathlib import Path

root = Path(__file__).resolve().parent.parent
doc = root / "doc"
SKIP = {"rules", "sources"}

TASK = re.compile(r"^\s*- \[( |x|X)\] (.+)$")


def parse(path):
    text = path.read_text(encoding="utf-8").replace("\r\n", "\n")
    meta = {}
    body = text
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if m:
        for line in m.group(1).splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip()] = v.strip()
        body = text[m.end():]
    tasks = []
    section = ""
    for line in body.splitlines():
        h = re.match(r"^#{1,6}\s+(.*)$", line)
        if h:
            section = h.group(1).strip()
        t = TASK.match(line)
        if t:
            tasks.append((t.group(1) != " ", t.group(2).strip(), section))
    return meta, tasks, body.count("TBD")


def bar(done, total, width=10):
    if total == 0:
        return ""
    n = round(width * done / total)
    return "█" * n + "░" * (width - n)


def label(key):
    """Column label for a frontmatter key, e.g. owner_26 -> Owner 26."""
    return key.replace("_", " ").capitalize().replace("Nx ", "NX ")


rows = []
for p in sorted(q for q in doc.glob("*/*.md") if q.stem == q.parent.name and q.parent.name not in SKIP):
    meta, tasks, tbd = parse(p)
    rows.append((p.stem, meta, tasks, tbd))

# owner_* and material_* keys differ per generation, so collect the ones that occur
owner_keys = sorted({k for _, m, _, _ in rows for k in m if k.startswith("owner_")})
material_keys = sorted({k for _, m, _, _ in rows for k in m if k.startswith("material_")})
columns = ["area", "nx_assembly", *owner_keys, "contact", *material_keys]

out = []
out.append("# Dashboard")
out.append("")
out.append(
    f"*Generated automatically on {date.today():%Y-%m-%d} with `tools/dashboard.py`. "
    "Do not edit by hand: changes belong in the notes under `doc/`.*"
)
out.append("")

total_done = sum(1 for _, _, t, _ in rows for d, _, _ in t if d)
total_all = sum(len(t) for _, _, t, _ in rows)
out.append(
    f"**Total:** {len(rows)} assemblies, {total_done} of {total_all} to-dos done "
    f"({bar(total_done, total_all)})"
)
out.append("")

out.append("## Overview")
out.append("")
out.append("| Assembly | " + " | ".join(label(c) for c in columns) + " | To-dos | Progress | Open TBD |")
out.append("|---|" + "---|" * len(columns) + "---|---|---|")
for name, meta, tasks, tbd in rows:
    done = sum(1 for d, _, _ in tasks if d)
    cells = " | ".join(meta.get(c, "") for c in columns)
    out.append(f"| [[{name}]] | {cells} | {done}/{len(tasks)} | {bar(done, len(tasks))} | {tbd} |")
out.append("")

out.append("## Next step per assembly")
out.append("")
out.append("| Assembly | Next open to-do |")
out.append("|---|---|")
for name, meta, tasks, _ in rows:
    nxt = next((t for d, t, _ in tasks if not d), "all done")
    out.append(f"| [[{name}]] | {nxt} |")
out.append("")

out.append("## Open to-dos")
out.append("")
areas = sorted({r[1].get("area") for r in rows if r[1].get("area")})
for area in areas:
    group = [r for r in rows if r[1].get("area") == area]
    out.append(f"### {area}")
    out.append("")
    for name, meta, tasks, _ in group:
        open_tasks = [(t, s) for d, t, s in tasks if not d]
        if not open_tasks:
            continue
        out.append(f"**[[{name}]]**")
        for t, s in open_tasks:
            out.append(f"- [ ] {t} *({s})*")
        out.append("")

other = [r for r in rows if r[1].get("area") not in areas]
if other:
    out.append("### Other")
    out.append("")
    for name, meta, tasks, _ in other:
        for d, t, s in tasks:
            if not d:
                out.append(f"- [ ] [[{name}]]: {t}")
    out.append("")

(root / "Dashboard.md").write_text("\n".join(out) + "\n", encoding="utf-8", newline="\n")
print(f"Dashboard.md written ({len(rows)} assemblies, {total_done}/{total_all} to-dos)")
