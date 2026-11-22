# Baseline survey and engineering process for enclosures and housings

This reference describes the process by which an assembly of the previous generation is surveyed, evaluated and carried over into the new generation. It was developed on two electronics enclosures (<GEN-A> → <GEN-B>) and applies to all housings, enclosures and brackets. For electronics or mechanics without a housing, take over the building blocks that fit.

Principle: measure first, then write. Every number in the documentation comes from the geometry, a datasheet, a rule or an interview. What cannot be substantiated is written as "unresolved" or `TBD`.

## The process at a glance

| Phase | Result | Quality gate |
|---|---|---|
| 0 Context and plan | NX mapping (name and path per part), plan with image, drawing and data list | mapping and plan confirmed by the user, anything not found asked for |
| 1 Capture geometry | bill of materials, STEP per part, volume, holes | every dimension measured from the geometry, not estimated |
| 2 Present | renderings, location image and drawings | every image looked at, no tilted or cropped view |
| 2b Check on the product | photos of the real product next to the renderings | every contradiction between photo and text reported to the user and worked in after approval |
| 3 Evaluate | weight, rule check, datasheets | every rule marked met / not met / unresolved, with reason |
| 4 Ask | interview note with the previous team | answers worked into the text, the rest marked "unresolved" |
| 5 Transition | takeaways (by the user), requirements with target values, to-dos | every requirement with source and measurable target |
| 6 New generation | design decisions per `engineering.md` | chain target → variants → evaluation → dimensioning → risk → proof |

## Phase 0: Plan before writing

First determine the NX mapping per `references/nx-mapping.md`: top-level assembly, name and path of every component, role of each part. What cannot be found unambiguously is looked up by hand by the user. The mapping is confirmed and entered as a table under Overview before anything is exported.

Then agree a plan with the user before the first text is written (plan mode). It contains:

1. **Geometry source:** confirmed NX mapping, STEP export per part, purchased parts as a single body.
2. **Image list:** shots per `references/renderings.md`.
3. **Drawing list:** one drawing per made part, none for purchased parts. A detail drawing for critical spots such as mounting lugs.
4. **Weight calculation:** volume per part, infill 100 %, density from the material (placeholder until it is known), purchased parts per datasheet.
5. **Rule check:** download the current rulebook and any supplementary handbook and pick out the affected chapters.
6. **Datasheets:** identify purchased parts, download the datasheet as PDF into `datasheets/`.
7. **Load assumptions for the new generation:** e.g. a 40 g shock for the attachment, proof by FEM.
8. **Questions for the predecessors:** everything the geometry does not reveal (material, installed or not, problems in operation).

## Phase 1: Capture and verify geometry

- **Bill of materials:** part, designation (part key from NX), type (printed part, sheet metal, purchased part), outer dimensions.
- **Volume** per part from the solid body (`scripts/tools/volume.py`).
- **Holes:** find them automatically (`scripts/tools/holes.py`), group them by diameter and axis, and give every group a purpose.
- **Verify instead of assuming:**
  - Fillets are not holes. A cylindrical face only counts if its partial faces add up to at least a semicircle.
  - Four equal radii in a rectangle are usually the corners of a rectangular opening. On one enclosure, 4x "Ø 10" turned out to be a single connector opening of 27.3 x 15.9 mm with R5: measure, do not assume.
  - Do not state several height steps (lip, plate, lettering) as one thickness; measure them or give only the overall height.
  - Compare parts that look alike (volume, contour). On one enclosure, one of four brackets was different.
- **Coordinates:** The coordinate system of a sub-assembly is not the product coordinate system. Take location data in the product only from the top-level assembly.

## Phase 2: Present

- **Renderings** per `references/renderings.md`.
- **Drawings** per `references/drawings.md`.
- **Location image** in the complete product per `references/photos-and-location.md`.
- **Look at every result:** contact sheet of all images, views not tilted or cropped, marks in the right places.

## Phase 2b: Check on the product

Renderings show the CAD, not the built product. Therefore every enclosure is photographed on the real product (overview, attachment, connectors, open). Storage, cropping and integration are governed by `references/photos-and-location.md`.

- Photos are placed next to the matching rendering.
- Assemblies without an NX model get the overview photo as cover image and are still structured per `assets/enclosure-skeleton.md`.
- Report contradictions between photo and text (different mounting, different cooling) to the user. After approval the text describes the as-built state and names the target state, and the rule table is evaluated against the as-built state.
- Enter blurry or missing photos as a to-do "photograph again".

## Phase 3: Evaluate

### Weight

| Part | Volume | Density | Mass |
|---|---|---|---|
| Printed part | from geometry | material or TBD | volume x density |
| Purchased part | – | – | per datasheet |
| Screws | – | – | TBD or catalogue value |
| **Total** | | | |

An example value with a named material (e.g. PETG 1.27 g/cm³) shows the order of magnitude and is marked as an example.

### Rule check

One row per relevant rule: number, content in one sentence, met / not met / unresolved, reason. The built product is evaluated: if an enclosure is screwed on in the CAD but fixed with a cable tie on the product, the rule is not met. Typical for enclosures:

- Mounting (R 4.1)
- Surface envelope and clearance to surroundings
- Water ingress test (R 9.1)
- Antennas (R 5.3)
- Materials (flame-retardant only where required)
- High-voltage housing: warning label (R 7.2), location and ground clearance (R 7.4), touch protection (R 7.5), isolation monitoring (R 7.8), data logger (R 7.6)
- Operating elements: main switches (R 6.2, R 6.3), test points (R 7.7)
- Protective circuit (R 6.6)

The numbers are placeholders from "<Rulebook> <year>"; use the real numbers of the rulebook in force. Every rule number is checked in the PDF. The column layout in the PDF separates number and text, so read the text with `pdftotext -layout` and cite sub-items only when the assignment is unambiguous, otherwise the section (e.g. "R 7.6").

### Compare the rules of the previous generation with the new generation

For every assembly, each rule used in the previous generation is compared with the same rule of the new generation, word for word (e.g. with `difflib` over the text of both PDFs). The result is written as `### Comparison with <Rulebook> <new year>` directly below the rule table:

- **All equal:** one sentence "All rules of this assembly are unchanged in content for <year>" with the list of rules compared. Pure changes in wording (tense, spelling) are named in brackets.
- **Changed:** in the accent colour (configurable, default #D62F2F; `<span style="color:#D62F2F">…</span>`):
  - Heading "Changed: <rule, topic>"
  - the old rule as a quote with year
  - the new rule as a quote with year
  - "What changes" in plain language: what applied before, what applies now, what this means for the assembly
- **New number:** If a rule only changed its number (e.g. main switch R 7.5 → R 7.6), say so, and the requirements use the new number.

The requirements of the new generation always cite the numbers of the new rules.

### Mounting in four steps

0. **Location in the product:** location image of the side view of the complete product, direction of travel named.
1. **Mounting concept:** how the enclosure hangs on the product as a whole.
2. **Bracket on the part:** geometry, holes, ribs, with close-up and detail drawing.
3. **Brackets on the structure:** design, welded or bolted, material, drawing. If there are none, write "unresolved".
4. **Joint between part and bracket:** screw size, number, direction.

This chain is also the load path for the FEM of the new generation.

## Phase 4: Ask

The interview with the previous team is filed as a note in `doc/sources/` and linked. Answers flow into the text. What stays open becomes "unresolved".

## Phase 5: Transition into the new generation

- **Takeaways for the new generation:** filled in by the user. The section stays with `TBD`.
- **Requirements:** from rules, interview and team specifications, each with source and measurable target. An example is "Enclosure and attachment withstand 40 g, proof by FEM, safety factor TBD".
- **To-dos:** checkboxes. The dashboard reads them.

## Phase 6: New generation

From here on `references/engineering.md` applies:

1. Make targets measurable (mass, load case, tightness, installation space).
2. Describe variants with the same characteristics.
3. Evaluate per VDI 2225.
4. Dimension. FEM per `references/simulation.md` with load case, support, mesh convergence and limit value.
5. Record risks as an FMEA.
6. Manufacture and validate, with plan and reality.

## Structure of the note

Template: `assets/enclosure-skeleton.md`.

```
Frontmatter (assembly, area, generation, nx_assembly, owner_<gen-a>, owner_next, contact, material_<gen-a>)
Cover image                       rendering, without an NX model the best photo
# Overview                       rough exploded view, 2–3 sentences
# <GEN-A> generation
  Team and material
  ## As-built state <GEN-A>      table Part | Designation | Type | Dimensions
  ## Mounting <GEN-A>            location image, then four paragraphs with images, photos and drawings
  ## Enclosure structure         sides with purpose of every opening, drawings, lid concept, contents with connections
  ## Weight <GEN-A>
  ## Rules <GEN-A>
  ## Datasheets <GEN-A>          local PDFs in datasheets/, source as second link
  ### relevant links
# Takeaways for <GEN-B>
# Working state <GEN-B>
  ## Requirements
  ## Datasheets <GEN-B>
  ## To-dos
```

There is no duplicate H1 title; the title is in the frontmatter. The frontmatter must be valid YAML: no ": " inside a value, otherwise use quotation marks.

All enclosures of a generation follow this structure, even if only photos and a few facts exist for some of them. Missing content stays in its place as `TBD` or "unresolved" so that every page reads the same.
