# Tools for baseline survey, renderings and drawings

Copy this folder once as `tools/` into the documentation project (vault). The scripts resolve paths relative to the vault (`tools/..`).

| Script | Runtime | Purpose |
|---|---|---|
| `step2stl.py` | `freecadcmd` | STEP parts to STL for Blender |
| `volume.py` | `freecadcmd` | volume per part for the weight table |
| `holes.py` | `freecadcmd` | list the holes of a part |
| `part_drawing.py` | `freecadcmd` | multi-view drawing on an A3 sheet, several sheets, hole table (example: `example-drawing.json`) |
| `sheet_a3.py` | - | rebuilt A3 drawing sheet, used by `part_drawing.py` |
| `export_drawing.py` | `python` + Edge | SVG to PDF and PNG in `doc/<assembly>/drawings/` |
| `place_in_assembly.py` | `freecadcmd` | place a part from its part file (part coordinates) via the installed position from `nx_list_components` into product coordinates, for parts with more than 200 bodies (boards) |
| `fit_onto.py` | `freecadcmd` | put a model onto a placeholder and check that the outlines fit (e.g. a populated board onto a PCB placeholder) |
| `axes.py` | `freecadcmd` | principal axes of a part ("up", "long") for `"align"` in the render configuration |
| `render_assembly.py` | `blender -b --python` | studio renderings per `references/renderings.md` (example: `example-assembly.json`) |
| `callouts.py` | `python` + Edge | technical exploded drawing: takes a `"style": "line"` shot of `render_assembly.py` (Freestyle outlines on white, part anchors as JSON) and adds numbered balloons, a parts list and a title block from the `sheet` block of the render configuration |
| `md2pdf.py` | `python` + Edge | finished wiki page as A4 PDF (frontmatter as header table, images, tables, info boxes, accent red `#D62F2F`): `python tools/md2pdf.py doc/<assembly>/<assembly>.md` |
| `dashboard.py` | `python` | `Dashboard.md` from the frontmatter and to-dos of all `doc/<assembly>/<assembly>.md` |

## Programs

- FreeCAD 1.1 (`freecadcmd`). A traceback from the FEM importer at startup when called with a JSON argument is harmless.
- Blender 5.x, Cycles. Set `GPU=CUDA` or `GPU=OPTIX` before the call, with `DENOISE=0`; without the variable it runs on the CPU. Never call a general device query (`refresh_devices`), it can block the graphics driver.
- Microsoft Edge headless for the PDF export.

## Folder structure in the vault

```
doc/<assembly>/<assembly>.md
doc/<assembly>/images/           renderings, photos
doc/<assembly>/drawings/         PDF + PNG per sheet
doc/<assembly>/datasheets/       manufacturer PDFs
doc/<assembly>/cad/{nx,step}     CAD archive
doc/rules/                       rulebooks
doc/sources/                     interview notes
context/                         open questions, notes, assembly context
nx/drawings/                     intermediate files (SVG, JSON)
nx/export/<area>-<gen>/<assembly>/  STL per part (from STEP), next to it nx/export-data-<assembly>.json with volumes and dimensions
tools/render/, tools/drawings/   configurations
```
