# Workflow

A typical session for one assembly.

1. **Context.** The agent reads `context/open-questions.md`, `notes.md` and `assembly-context.md`, then the existing page if there is one.
2. **NX mapping.** With the connector: list components, read the references of the top-level part, propose a table. Without: ask for the part list. You confirm it. Nothing is exported before that.
3. **CAD archive.** One STEP per part in assembly coordinates under `doc/<assembly>/cad/step/`. Export once, reuse.
4. **Plan.** The agent proposes outline, shot list, drawings and open questions and agrees them with you.
5. **Images.** `step2stl.py` -> `render_assembly.py`. Every image goes through the image review (orientation, viewing angle, explosion direction, nothing hidden, nothing missing) before it is embedded.
6. **Drawings.** `part_drawing.py` per made part, `export_drawing.py` to PDF and PNG.
7. **Page.** Text is written in the same step as each change. Decisions carry status and history. Unknowns are `TBD`.
8. **Check.** `check_page.py` must report no errors. Warnings are reviewed, `OPEN` lists every `TBD`.
9. **Close.** The agent names new open questions and notes and writes them to `context/`.

## Exploded drawing

Add a `"style": "line"` shot with an explosion state to the render configuration and a `sheet` block with the parts list, render it, then run `python tools/callouts.py tools/render/<assembly>.json <shot>`. The renderer writes the screen position of every part next to the image; `callouts.py` places numbered balloons above and below and builds the table. For parts whose bounding-box centre is hidden behind others, give a point in `"anchors"` in the shot.

## Rules and generations

Pages compare the previous generation with the new one. Rulebooks of both years are compared per assembly; each change is quoted old and new and explained in plain language (`references/baseline-survey.md`).
