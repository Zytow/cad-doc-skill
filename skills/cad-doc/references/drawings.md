# Technical drawings

## In NX

There are no bundled drawing templates. Bring your own NX drawing template (sheet sizes A4 to A0 landscape, metric units, with frame and title block), or use the Python sheet described below.

- Whoever draws in NX does not rebuild frame and title block by hand but uses the template.
- Keep the template files together with their palette file and preview images in one folder so that the palette still finds them.

## By script outside NX (default for the baseline survey)

`scripts/tools/part_drawing.py` (FreeCAD, headless) creates multi-view drawings from a STEP file on the rebuilt A3 sheet (`sheet_a3.py`: frame, zones, title block, optional logo). `export_drawing.py` turns them into PDF and PNG.

The sheet is neutral and configurable: title block fields, optional logo and accent colour are set in the configuration (see below), not hard-coded.

```bash
freecadcmd scripts/tools/part_drawing.py tools/drawings/<part>.json
python scripts/tools/export_drawing.py nx/drawings/<Part>-A3-<GEN>-*.svg doc/<assembly>/drawings
```

### Rules

- **Show parts large:** the target is 1:1 for parts up to about 200 mm, otherwise the largest standard scale (5:1 … 1:5).
- **Prefer several sheets to small views:** the script distributes the views over up to three sheets itself ("Sheet 1/3").
- **Only necessary views:** main view and the views with their own features. Closed, mirror-symmetric or very thin edge views are dropped (`views`). Their values then appear as a note on the drawing.
- **Hidden edges** are not drawn. Every view is labelled ("View from top"), with overall dimensions.
- **Hole table** large, bottom left or right above the title block:
  - columns identifier letter, Ø or dimension, count, axis, purpose
  - identifier letters in red `#C90000` in every view from which the hole is open (line of sight along the axis is free)
- **No fillets as holes:** only the partial faces of a hole together make at least a semicircle.
- **Non-round openings** (rectangular openings, slots) via `openings` with measured dimension and location.
- **Notes:** material, infill and special features, without derivation or assumptions. Every value is measured.
- **Look at every sheet** before it goes into the documentation:
  - scale
  - nothing cut off
  - every hole of the table has markers
  - no marker without a hole

### Configuration

| Key | Meaning |
|---|---|
| `step` | STEP file of the part |
| `output` | base name without extension (intermediate files in `nx/drawings/`) |
| `fields` | title block: part_name, part_key, created_by, date, material, quantity |
| `views` | necessary views |
| `sheets` | optional fixed distribution, e.g. `[["top"], ["front", "left"]]` |
| `target_scale`, `max_sheets` | optional, default 1:1 and 3 |
| `purposes` | `{d, axis, purpose}` per hole group |
| `openings` | `{size, axis, purpose, c: [[x, y, z]]}` |
| `ignore` | `{d, axis}` for cut holes in detail drawings |
| `cutout` | box for a detail drawing |
| `notes` | lines of text |
| `logo`, `accent` | optional, logo image and accent colour of the sheet |

### Including in the documentation

- Every sheet as a full-width PNG: `![Drawing … scale 1:1, sheet 1 of 3](drawings/<Part>-A3-<GEN>-1.png " =900x637")`.
- The PDF lies next to it with the same name. You do not write path lines to the PDF into the text.
- Dimensions are in the drawing and are mentioned in the text only if they justify a decision.
