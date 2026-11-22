---
name: cad-doc
description: Documents a mechanical or electromechanical assembly as living Markdown while it is being designed, with real engineering content (measurable goals, variants, weighted evaluation matrix, design calculation, FMEA, simulation, validation), CAD-derived renders, exploded views, location images, drawings, weight and rule checks, open questions, and an optional PDF export. Works with the Siemens NX MCP connector when present and by hand when not. Use whenever an assembly is being designed, calculated, simulated, decided, manufactured or tested, even if documentation is not mentioned, and whenever someone says "document", "design decision", "exploded view", "drawing", "evaluate the simulation", "weigh it", or "preserve knowledge for the next generation".
---

# Document an assembly while you design it

Documentation is written during design, not afterwards. Every assumption, variant, calculation and decision goes into one Markdown file at the moment it happens. The reason for each decision survives, and the next generation of the product does not have to rediscover it.

| Reference | Defines | File |
|---|---|---|
| Documentation template | starting point for the outline | `assets/doc-template.md` |
| Engineering | deriving decisions: goals, variants, evaluation, design calculation, FMEA | `references/engineering.md` |
| Simulation | fact sheet for every simulation | `references/simulation.md` |
| Writing style | voice, wording, photos | `references/writing-style.md` |
| Baseline survey | surveying the previous generation and the process up to the new one | `references/baseline-survey.md` |
| Renderings | requirements, colours, shot list, workflow from export to image | `references/renderings.md` |
| Image review | checking every render before it goes into the page | `references/image-control.md` |
| Images in the documentation | selection, space, size, no duplicates, requesting missing images | `references/images.md` |
| Photos and location | location image, photos of the real product, conflicts between photo and documentation | `references/photos-and-location.md` |
| Location images with NX | location of every part in the whole product and in its module | `references/location-images-nx.md` |
| Drawings | drawings in NX and by script | `references/drawings.md` |
| NX mapping | step 0: how assembly and parts are named in NX, confirmed by the user | `references/nx-mapping.md` |
| CAD archive | part files and STEP per part, stored once under `doc/<assembly>/cad/` | `references/cad-archive.md` |
| Open questions | running list of everything unconfirmed, not a to-do list | `references/open-questions.md` |
| Notes | external list for everything the user declares relevant | `references/notes.md` |
| PDF export | on request only | `references/pdf-export.md` |

Format, outline, writing style, renderings, drawings and the rule check come from this skill. The tools are in `scripts/tools/` (see `scripts/tools/README.md`).

## Plan before you start

**Build context first.** Find out how the assembly and each part are named in NX (top-level assembly, name, path, role) following `references/nx-mapping.md`. If something is not unambiguous, ask the user to look it up by hand instead of guessing. Have the mapping confirmed before anything is exported, rendered or drawn. Afterwards it lives on the page as the table "NX mapping" under Overview.

When the `nx_*` tools of the NX MCP connector are available (`nx_list_components`, `nx_list_objects`, `nx_export_model`, `nx_open_part`, ...), use them for the mapping, measurements and exports. When they are not, ask the user for the part list and STEP files and continue by hand. Everything downstream works from the STEP files.

**Read and maintain the context.** Before any work on an assembly, read the `context/` folder next to the vault: open questions (`open-questions.md`), notes (`notes.md`) and the context document (`assembly-context.md`). A new unconfirmed question goes into the open questions immediately (`references/open-questions.md`). When the user declares something relevant, it goes into the notes immediately (`references/notes.md`). At the end of every working session, name the new questions and notes.

**Store geometry once.** The part folder and one STEP per part live permanently under `doc/<assembly>/cad/` (`references/cad-archive.md`). Every later step works from this archive.

Before the first sentence is written, agree on a plan with the user (plan mode). It saves rework and makes sure every number has a source. The plan answers:

1. **Which outline?** Default for every assembly: `assets/assembly-pattern.md` (previous generation, takeaways, new generation with design decisions). For enclosures: `assets/enclosure-skeleton.md`. For a new development without predecessor: `assets/live-skeleton.md`. The process is described in `references/baseline-survey.md`.
2. **Geometry:** confirmed NX mapping, CAD archive with one STEP per part, purchased parts.
3. **Images:** shot list per `references/renderings.md`, location image and photos per `references/photos-and-location.md`. If the assembly is not in NX, the photo carries the page.
4. **Drawings:** one per made part, with the required views and detail drawings per `references/drawings.md`.
5. **Evaluation:** weight (volume x density, 100 % infill, purchased parts per datasheet), rule check against the current rulebook.
6. **Datasheets and rules:** download them into the documentation folder.
7. **Requirements of the new generation:** including load assumptions, for example a shock load with a finite-element proof.
8. **Questions:** to the user and to the previous team before anything is assumed.

Afterwards the process and the quality gate per phase are described in `references/baseline-survey.md`. Decisions of the new generation follow `references/engineering.md`.

## Folder structure

Everything that belongs to the documentation lives in the folder of the assembly, so it can be exported as a whole.

```
doc/<assembly>/<assembly>.md
doc/<assembly>/images/          renders and photos
doc/<assembly>/drawings/        PDF and PNG per drawing sheet
doc/<assembly>/datasheets/      datasheets as PDF
doc/<assembly>/cad/nx/          NX folder of the assembly, copied (.prt, not in git)
doc/<assembly>/cad/step/        one STEP per part in assembly coordinates
../context/                     context document, open questions, notes (outside the vault)
doc/rules/                      rulebook (shared)
doc/sources/                    interview notes
```

Images are embedded with relative paths (`images/...`, `drawings/...`). A datasheet is a local link, the manufacturer page a second link. Intermediate files (SVG, JSON, STL) stay outside `doc/`.

File names: `<prefix>-<gen>-<shot>.png` for renders, `<prefix>-<gen>-photo-<what>.jpg` for photos, `<prefix>-<gen>-location.png` for the location image.

Background knowledge that does not belong on the page (what a board does, long forms, buses) lives in an internal context document outside the vault (`../context/`), see `references/photos-and-location.md`.

**Frontmatter must be valid YAML.** A value containing ": " or " #" invalidates the whole frontmatter and the viewer shows no properties. Reword such values or put them in quotes.

## Start

1. Look for the documentation of the assembly at `doc/<assembly>/<assembly>.md`. If it exists, read it first, it is the current state.
2. If it does not, plan as above, copy the matching skeleton there, replace every `{{...}}` and create the subfolders.
3. Enter the generation goal, requirements and measurable target values before you design.

`examples/speaker/` in the repository shows a filled page with every image type.

## Live rule

Update the documentation in the same step as the change. Do not collect anything for later.

| Event | Entry |
|---|---|
| new requirement or rule | Requirements, with source or rule number |
| new idea or variant | Variants, with the same figures as the others |
| comparison of several solutions | Evaluation as a matrix |
| calculation or simulation | Design calculation and verification, with load case, assumptions and result |
| decision made | Decision, status and history |
| decision changed | new history entry with reason, the old variant stays |
| risk recognised | Risks as an FMEA row |
| CAD state, photo, screenshot | immediately into `images/`, below the paragraph that describes exactly that, per `references/images.md` |
| text describes something hard to follow without an image | image need as a to-do (kind, subject, perspective, purpose), and tell the user |
| photo contradicts text or CAD | report to the user, after approval state as-built and intended state, assess the rule table by the as-built state |
| manufacturing or test | Manufacturing or Validation, with plan and reality |
| open question | `TBD` where the answer belongs |

Do not delete rejected paths. Do not invent values, test results or experience. Ask, or write `TBD`. Every value appears once with its source, elsewhere the page refers to it.

End every working session with the check and name the open points.

## Structure of a design decision

```markdown
## Design decision #1: Topic

**Status:** open

### Previous generations
### This generation
#### Goals and constraints
#### Variants
#### Evaluation
#### Decision
#### Design calculation and verification
##### Simulation: Name
#### Risks
#### History
```

- **Status** is `open`, `in progress`, `decided`, `validated` or `rejected`.
- `decided` requires variants or an evaluation and a filled decision.
- `validated` additionally requires a proof.
- **History** is a table with date (YYYY-MM-DD), change and reason.
- Read `references/engineering.md` before evaluation, design calculation or risks, and `references/simulation.md` before every simulation.

## Outline

Choose the chapters to fit the assembly. The template and `assets/live-skeleton.md` are a starting point, not a fixed form. A cable harness needs chapters such as planning, manufacturing, material and bus, a gearbox rather design calculation, bearings, lubrication and test bench.

These building blocks belong in every page, whatever chapter they sit in:

- title and title image
- relevant links
- requirements with measurable targets
- every decision as `Design decision #n: Topic`, with status and history
- proofs and simulations
- conclusion and potential for the next generation

Use *Previous generations* and *This generation* when there is a predecessor to compare with. A new development drops the pair.

Name chapters after what a reader looks for. Avoid catch-all chapters such as "Miscellaneous"; sort the points under the matching topic.

## Markdown formats

| Element | Syntax |
|---|---|
| Image | `![What you see](images/file.jpg " =400x300")` |
| Images side by side | images directly after each other on one line, no spaces |
| Image left or right | `"left-50 =400x300"` or `"right-50 =400x300"` |
| Info box | `:::info`, text, blank line, `:::` |
| Link to a section | `[[#Heading name]]` |
| Person | `[[First Last]]` |

The first number is the display width: title image 600, overview 500, default 400, detail 300, side by side 350 each (three: 250 each), location image 700. The second follows from the aspect ratio. Where an image belongs, how to avoid duplicates and when an image is missing is governed by `references/images.md`. Read it before embedding images.

## Check

```bash
python3 ~/.claude/skills/cad-doc/scripts/check_page.py doc/<assembly>/<assembly>.md
```

- **ERROR** must be fixed: empty section, missing status or history, wrongly computed matrix or RPN, incomplete simulation fact sheet, missing image, dead link, invalid frontmatter.
- **WARNING** when an assembly page lacks the location image (`...-location.png`).
- **WARNING** should be reviewed, for example missing links, missing title image or missing conclusion.
- **WARNING** also reports meta phrases ("presumably", "derived", "export", "according to <name>") and files outside the assembly folder that would be missing on export. A title in the frontmatter (`assembly:`) replaces the H1 heading.
- **OPEN** lists every `TBD`.

For old pages there is `--legacy`, which drops status and history. If the exact template outline is requested, add `--template`.

The check only sees form and arithmetic. Whether an assumption or a decision is technically right remains your job.

## Further material

- Technical drawings (NX and by script): `references/drawings.md`
- Renderings: `references/renderings.md`
- Location image and photos of the product: `references/photos-and-location.md`, location images in NX: `references/location-images-nx.md`
- Tools: `scripts/tools/README.md`
- PDF on request only: `references/pdf-export.md`, for a finished page `scripts/tools/md2pdf.py`
