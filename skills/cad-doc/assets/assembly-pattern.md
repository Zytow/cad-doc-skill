---
assembly: <short name, e.g. speaker-shell>
area: <area>
generation: <GEN-B>
nx_assembly: <NX assembly of the previous generation>
owner_<gen-a>: <name>
owner_<gen-b>: <name>
contact: <name from the previous team>
material_<gen-a>: <main material>
---

:::info
**Pattern page:** This page shows the structure used to document every assembly. It applies to any assembly, not only enclosures. To set up: create the folder `doc/<short name>/` with `images/`, `drawings/` and `datasheets/`, copy this page as `doc/<short name>/<short name>.md`, delete the hint lines (`> ...`) and replace everything in `<...>`. Unknown values become `TBD`, questions without an answer become "unresolved". Finished examples: see `examples/`.

:::

![<assembly> <GEN-A>, product image](images/<prefix>-<gen-a>-product.png " =600x400")

# Overview

> Two to three sentences: what the assembly is, what it does in the product and what it consists of. Below it a rough exploded view.

<What the assembly is, what its task is, what it consists of.>

![<assembly> <GEN-A>, exploded view](images/<prefix>-<gen-a>-explosion.png " =500x333")

### NX mapping

> Determine before any other work and have the user confirm it, see `references/nx-mapping.md`.

Top-level assembly: `<file and revision>`. Confirmed on <date>.

| Part | Role | Name in NX | Path in the assembly |
|---|---|---|---|
| Assembly | <role> | `<NX name>` | `<path>` |
| <part> | <role> | `<NX name>` or unresolved | `<path>` |

# <GEN-A> generation

> Baseline survey of the previous generation. Every number comes from the geometry, a datasheet, a rule or the interview with the previous team.

* Owner <GEN-A>: <name>
* Material <GEN-A>: <materials per part>

## As-built <GEN-A>

| Part | Designation | Type | Dimensions |
|---|---|---|---|
| <part 1> | `<part key from NX>` | <printed part, milled part, sheet metal, board, purchased part> | <L x W x H mm> |
| <part 2> | `<...>` | <...> | <...> |

## Structure and function

> How the assembly works and what each part is for. Put images directly at the point they show. For electronics: circuit sections, connectors, pin assignment. For mechanics: load path, bearing, fits.

* <part 1>: <task>
  * <detail or reasoning>

![<What is visible>](images/<prefix>-<gen-a>-<view>.png " =400x267")

### Interfaces

| Interface | Partner | Type | Data |
|---|---|---|---|
| mechanical | <structure, other assembly> | <screws, rivets, glued> | <M4, 4 pieces> |
| electrical | <cable> | <connector> | <type, pins> |
| thermal / fluidic | <...> | <...> | <...> |

### Purchased parts

> Model, manufacturer, weight and characteristics per datasheet. The datasheet is in `datasheets/`.

| Purchased part | Model | Weight | Characteristics |
|---|---|---|---|
| <part> | <manufacturer, type> | <g, datasheet> | <connectors, power> |

## Mounting <GEN-A>

> The load path from the part to the structure in four steps. It is also the basis for the FEM of the new generation.

**Location in the product:** side view of the complete <GEN-A> product, direction of travel to the left.

![<assembly> in the product, side view <GEN-A>, <assembly> highlighted dark](images/<prefix>-<gen-a>-location.png " =700x344")

> If the assembly belongs to a module (wheel, motor, battery pack), add `**Location in the module:**` with `images/<prefix>-<gen-a>-location-<module>.png`, see `references/location-images-nx.md`.

**Mounting concept:** <how the assembly as a whole is attached to the product>

![Mounting on the product, bracket highlighted](images/<prefix>-<gen-a>-mounting.png " =500x333")

**Bracket on the part:** <lugs, holes, ribs, with close-up and drawing>

**Brackets on the structure:** <bracket, welded or bolted, material, or "unresolved">

**Joint between part and bracket:** <screw size, count, direction>

## Technical drawings

> One drawing per made part on the A3 drawing sheet, target 1:1, prefer several sheets over small views. Each sheet as a full-width image, the PDF with the same name next to it.

<part>, 2 sheets, scale 1:1: <what the drawing shows>. [Sheet 1](drawings/<part>-A3-<GEN-A>-1.pdf) · [Sheet 2](drawings/<part>-A3-<GEN-A>-2.pdf)

![Drawing <part>, scale 1:1, sheet 1 of 2](drawings/<part>-A3-<GEN-A>-1.png " =400x283")

## Weight <GEN-A>

| Part | Volume | Density | Mass |
|---|---|---|---|
| <printed part> | <mm³ from the geometry> | <g/cm³ or TBD> | <volume x density> |
| <purchased part> | - | - | <g per datasheet> |
| Fasteners | - | - | <TBD> |
| **Total** | | | **<g>** |

## Rules <GEN-A>

Source: <Rulebook> <year-a>, `rules/<Rulebook>_<year-a>.pdf`.

| Rule | Content | Met | Reasoning |
|---|---|---|---|
| <R 4.2 of <Rulebook> <year-a>> | <content in one sentence> | <met / not met / unresolved> | <why> |

## Datasheets <GEN-A>

* <purchased part>: [<file>.pdf](datasheets/<file>.pdf) ([source](<manufacturer page>))

### Relevant links

* Interview with the previous team: <note in `doc/sources`>
* NX: `<assembly>.prt`
* Rules: `rules/<Rulebook>_<year-b>.pdf`
* Git repo: <link>

# Takeaways for <GEN-B>

> Written by the responsible person: what worked, what did not, what would be done differently.

* TBD

# <GEN-B> generation

> From here on the engineering process applies: goal, variants, evaluation, decision, design calculation, risk, verification. Every decision gets its own "Design decision #n".

## Requirements

| Requirement | Source | <GEN-A> | Target <GEN-B> | Current |
|---|---|---|---|---|
| <mass of the assembly> | <team specification> | <g> | <g> | TBD |
| <withstands <N> g shock, verified by FEM> | <team specification> | - | <safety factor> | TBD |
| <rule requirement> | <R 4.2 of <Rulebook> <year-b>> | - | <value> | TBD |

## Concept

> Overall solution of the generation and why. If needed as its own design decision.

* <concept in bullet points>

## Design decision #1: <topic>

**Status:** open

> Status is open, in progress, decided, validated or rejected. Rejected variants stay in place.

### Previous generations

* <solution of the previous generation in one sentence, reference to [[#<GEN-A> generation]]>

### This generation

#### Goals and constraints

| Quantity | Previous | Target | Current | Source |
|----------|----------|--------|---------|--------|
| <quantity> | <value <GEN-A>> | <value <GEN-B>> | TBD | <requirement, rule> |

#### Variants

| Variant | <quantity 1> | <quantity 2> | Result |
|---|---|---|---|
| A: <name> | <value> | <value> | <chosen / rejected, why> |
| B: <name> | <value> | <value> | <...> |

#### Evaluation

> Evaluation matrix per VDI 2225: fix criteria and weighting beforehand, scores 1 to 5, total = weighted sum. A knock-out criterion is marked `k.o.` in the weighting.

| Criterion | Weighting | Variant A | Variant B |
|-----------|-----------|-----------|-----------|
| Mass | 40 % | 4 | 2 |
| Cost | 20 % | 3 | 5 |
| Manufacturability | 40 % | 5 | 3 |
| Total | 100 % | 4.2 | 3.0 |

#### Decision

* <chosen variant and reasoning>

#### Design calculation and verification

> Every calculation with load case, assumptions and result. Every simulation with a complete data sheet.

##### Simulation: <name, e.g. mounting under <N> g shock>

| Item | Details |
|------|---------|
| Question | <what the simulation should answer> |
| Tool | <Ansys Mechanical, Fusion> |
| Model | <geometry, simplifications, CAD revision> |
| Material | <material, property, source> |
| Load case | <e.g. <N> g in x, y and z, calculation with units> |
| Supports | <fixed faces, justified> |
| Contacts | <type of contacts> |
| Mesh | <element type, size, count> |
| Mesh convergence | <peak value with coarser and finer mesh> |
| Limit | <allowable value, safety factor> |
| Result | <maximum value with unit and location> |
| Assessment | <holds or does not hold, consequence for the design> |
| Screenshot | TBD |

#### Risks

> FMEA: severity (S), occurrence (O), detection (D) from 1 to 10, RPN = S x O x D, before and after the action.

| Failure mode | Effect | Cause | S | O | D | RPN | Action | S new | O new | D new | RPN new |
|--------------|--------|-------|---|---|---|-----|--------|-------|-------|-------|---------|
| <bracket breaks> | <assembly comes loose> | <fatigue> | 8 | 3 | 4 | 96 | <verification by FEM> | 8 | 2 | 2 | 32 |

#### History

| Date | Change | Reason |
|------|--------|--------|
| <date> | Decision created | Design start |

## Manufacturing

> Plan and reality, with photos at the work step.

* TBD

## Validation

> Tests, measurements, inspection, with plan and result.

* TBD

## Datasheets <GEN-B>

* TBD

## To-dos

- [ ] Record the bill of materials of the previous generation
- [ ] Renderings and drawings of the previous generation
- [ ] Interview with the previous team
- [ ] Rule check against the current rulebook
- [ ] Clarify materials, fill the weight table
- [ ] Define requirements with measurable target values
- [ ] Evaluate variants, make the decision
- [ ] Design calculation and FEM
- [ ] Manufacturing
- [ ] Validation
