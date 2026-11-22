# Optional PDF export

## Page directly as PDF

If a finished page (for example an enclosure documentation) is to be handed on as a PDF, the converter `scripts/tools/md2pdf.py` is enough. It takes the page without rewriting: frontmatter as a header table, images with their width, images side by side, tables, tasks and info boxes. Wiki links become the title of the linked note. Layout: A4 portrait, Arial, configurable accent colour (default `#1f3b57`) and configurable footer text. Printing goes through Edge headless.

```bash
python tools/md2pdf.py doc/<assembly>/<assembly>.md            # → doc/<assembly>/<assembly>.pdf
python tools/md2pdf.py doc/<assembly>/<assembly>.md --accent "#1f3b57" --footer "<footer text>"
```

The PDF is an output format and is not committed to the repository. Afterwards look at the pages, especially nearly empty pages and cut-off images.

## Custom PDF documentation per template

Use this route only if a PDF is explicitly needed, for example for a submission. The default remains the page. The PDF check `check_pdf.py` still requires the chapters of the template. The layout is a clean reference-document look: A4 portrait, Arial, accent blue `#1f3b57` (configurable), footer text configurable.

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path.home() / ".claude/skills/cad-doc/scripts/tools"))
from doc_style import Doc

d = Doc(
    target="out/<GEN-B>-<assembly>_Documentation.pdf",
    title="Name of the assembly",
    subtitle="Part key and short classification",
    short="<GEN-B>-<assembly>",
    date="18.11.2026",
    cover_image="images/cover.jpg",
    meta={"Project": "…", "Created by": "…", "Date / state": "…"},
    accent="#1f3b57",            # configurable accent colour
    footer="<footer text>",      # configurable footer text
)

d.h1("Overview")
d.p("What the assembly does and where it sits.")
d.h3("Relevant links")
d.bullets(['<a href="https://…" color="#1f3b57">Requirement sheet</a>'])

d.h1("Concept")
d.h2("Requirements")
d.generations(previous="…", current=["Change 1", "Change 2"])
d.h2("Concept decision")
d.generations(previous="…", current="…")

d.h1("Design")
d.h2("Design decision #1: Seal")
d.generations(previous="…", current="…")
d.image("images/section.jpg", "Section through the seal, locked")
d.images([("a.jpg", "Variant A"), ("b.jpg", "Variant B")])
d.table([["Feature", "<GEN-A>", "<GEN-B>", "Reason"],
         ["Wall", "3.0 mm", "1.5 mm", "…"]], widths=[2, 1, 1, 3])

d.h1("Manufacturing")
d.generations(previous="…", current="…")
d.h1("Validation")
d.generations(previous="…", current="…")

d.h1("Generation history")
d.generation("<GEN-B>", "Name", ["Conclusion"], ["Potential"])

d.build(appendix={"Drawing set": "out/drawings/drawing-set.pdf"})
```

- Empty content (`None`, `""`, `[]`) is set as `TBD`.
- `d.table` aborts if a word does not fit into its column. Then make the column wider or shorten the header.
- `reportlab`, `pymupdf` and `pillow` are required.

Check the result and then look at every page as an image:

```bash
python3 ~/.claude/skills/cad-doc/scripts/tools/check_pdf.py out/<GEN-B>-<assembly>_Documentation.pdf
```
