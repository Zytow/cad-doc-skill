---
assembly: {{ASSEMBLY}}
area: <area>
generation: <GEN-B>
nx_assembly: {{NX_ASSEMBLY}}
owner_<gen-a>: TBD
owner_<gen-b>: TBD
contact: TBD
material_<gen-a>: TBD
---

:::info
Live documentation <GEN-B>, created on {{DATE}}

:::

![{{ASSEMBLY}} <GEN-A>](images/{{prefix}}-<gen-a>-product.png " =600x400")
<without an NX model: use the best overview photo images/{{prefix}}-<gen-a>-photo-<content>.jpg as the title image>

# Overview

<2-3 sentences: what the enclosure is, what is inside, what it is for.>

![{{ASSEMBLY}} <GEN-A>, exploded view](images/{{prefix}}-<gen-a>-explosion.png " =500x333")

### NX mapping

Top-level assembly: `{{NX_TOP}}`. Confirmed on TBD.

| Part | Role | Name in NX | Path in the assembly |
|---|---|---|---|
| Assembly | whole enclosure | `{{NX_ASSEMBLY}}` | TBD |
| Shell | printed part | TBD | TBD |
| Amplifier board | purchased part | TBD | TBD |

# <GEN-A> generation

* Owner <GEN-A>: TBD
* Material <GEN-A>: TBD

## As-built <GEN-A>

| Part | Designation | Type | Dimensions |
|---|---|---|---|
| Shell | `...` | printed part | ... x ... x ... mm |

## Mounting <GEN-A>

**Location in the product:** side view of the complete <GEN-A> product, direction of travel to the left.

![{{ASSEMBLY}} in the product, side view <GEN-A>, {{ASSEMBLY}} highlighted dark](images/{{prefix}}-<gen-a>-location.png " =700x344")

**Mounting concept:** <one sentence on the principle>

![Mounting](images/{{prefix}}-<gen-a>-mounting.png " =350x233")![<Photo: what is visible>](images/{{prefix}}-<gen-a>-photo-mounting.jpg " =350x<height>")

**Bracket on the part:** <geometry, holes, image and drawing>

**Brackets on the structure:** <shape, welded/bolted, image and drawing, or "unresolved">

**Joint between part and bracket:** <screws, count>

## Structure of the enclosure

<one sentence: what the enclosure consists of and what is visible when open>

![{{ASSEMBLY}} open](images/{{prefix}}-<gen-a>-open.png " =500x333")

### Sides of the enclosure

**Front / Rear / Left / Right / Top / Bottom:** <openings and their purpose>. Images only for sides with their own features, at most three per row with `" =250x167"`. Closed sides in text only.

### Technical drawings

One drawing per part on the A3 drawing sheet (`tools/part_drawing.py`), PDF and PNG per sheet in `drawings/`. One sentence per part and a preview of the first sheet (`" =400x283"`), all sheets as PDF links. All drawings only here, not under Mounting.

### Lid concept

<screws, gasket, clamping>

### Contents

<board, computer or receiver: model, weight per datasheet, use, connectors>

## Weight <GEN-A>

| Part | Volume | Density | Mass |
|---|---|---|---|
| Shell | ... mm³ | TBD | TBD |
| **Total** | | | **TBD** |

## Rules <GEN-A>

Source: <Rulebook> <year-a>, `rules/<Rulebook>_<year-a>.pdf`.

The as-built state on the product (photos) is assessed, not only the CAD.

| Rule | Content | Met | Reasoning |
|---|---|---|---|

### Comparison with <Rulebook> <GEN-B>

<All rules identical: one sentence with the list. Otherwise, per change, in red (`<span style="color:#D62F2F">`): old rule quoted, new rule quoted, "What changes" in plain language. See `references/baseline-survey.md`.>

## Datasheets <GEN-A>

* TBD

### Relevant links

* TBD

# Takeaways for <GEN-B>

* TBD

# Working state <GEN-B>

## Requirements

| Requirement | Source | Target / value |
|---|---|---|

## Datasheets <GEN-B>

* TBD

## To-dos

- [ ] TBD

Image needs per `references/images.md`, one line each with type, subject, perspective and section:

- [ ] Photo: TBD
