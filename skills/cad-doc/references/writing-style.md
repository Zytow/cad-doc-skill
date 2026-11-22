# Reference documentation style

The style of a good reference documentation is the model for "very good". It consists almost only of bullets (in the model: 349 bullets, 11 lines of running text), has 40 photos, 64 links and 3 lookup tables. Its strength: you can work directly from it.

## The ten patterns

### 1. Bullets with sub-bullets

The statement comes first, the reason or detail below it. Two levels are usually enough, four are the limit.

```markdown
* The side cover should be removable without undoing any solder joints
  * a broken cover can be swapped quickly this way
```

### 2. State plan and reality

Write down what was planned and what actually happened. This deviation is what helps the next generation.

```markdown
* The connectors were supposed to be mounted on an L-bracket
  * did not happen, they were simply taped down every time
```

### 3. Assess experience

Say clearly whether something proved itself, and give a recommendation.

```markdown
* in hindsight it was counterproductive to plug all cables straight into the connectors
* next time: crimp all cables first, then plug them into the housings one by one
* worked very well and I would recommend it again
```

### 4. Name mistakes openly

An honestly described mistake is more useful than a smooth success story. The first person is explicitly allowed. Write about the matter and do not blame anybody.

```markdown
* I did not consider that a second bus interface is needed
  * so the logger moved to the back
```

### 5. So concrete that you can reorder

Give manufacturer, part number with link, quantity, catalogue page, supplier and storage location.

| Weak | Good |
|---|---|
| ordered matching contacts | `[1060-16-0622](link)` (nickel), 50 pieces each sampled |
| used thin cable | 0.35 mm², because 0.22 mm² was hard to crimp with the large contacts |
| connectors are still in stock | about 20 pieces in the spares box, so nothing was reordered |

### 6. Show assumptions and calculation

Values come with their assumptions so that they can be reassessed later.

```markdown
* voltage drop per connection designed for not much above 300 mV
  * the sensor line may have more: 0.25 mm², 10 m, 1 A → 750 mV
```

### 7. Rules with practical relevance

Name the rule number and content. Add below what it means for the assembly. Check every number in the current rulebook before you take it over (for example "R 4.2 of <Rulebook> <year>").

### 8. Photos at the work step

- Put the photo directly under the bullet it supports.
- Show procedures as an image sequence: before, intermediate state, result.
- Place related images side by side.
- Describe in the alt text what you see: `Contact crimped`, not `IMG_2041`.
- Real photos from the workshop are explicitly welcome, even if they do not look perfect. Renderings complement them.

### 9. Tables for lookup

Use tables for values that you search for while working, for example connector, cross-section, strip length and crimping tool. Reasons belong in bullets.

### 10. Warnings where they are needed

- Short warning in bold directly at the step: `**these crimping pliers are rather unsuitable for inline crimps**`
- Fixed practical rule in an `:::info` box
- Do not write knowledge twice, link it with `[[#Heading]]`

## What you do not take over

The model is strong in content but has spots that a new documentation does better:

- **Catch-all chapters:** dedicated chapters are welcome, but items from "random points" belong to the matching topic.
- **Obsidian images:** `![[image.jpg|400]]` is not displayed in the wiki.
- **Dead links:** the text in `[[#…]]` must match the heading exactly.
- **Notes to oneself:** items such as "check again" are done or marked as `TBD`.
- **Typos:** correct them before the handover.

## Placing content in the template

This table applies when you work with the template chapters. With custom chapters it serves as orientation.

| Content | Place in the template |
|---|---|
| Links, plans, catalogues, repos | Overview › relevant links |
| Rule requirements, requirements per subsystem | Concept › Requirements |
| System plan, solution comparison, analysis of the old part | Concept › Concept decision |
| Design calculation, material choice, part choice, tolerances | Design › one design decision #n each |
| Preparation, work steps, crimp tables, assembly | Manufacturing |
| Suppliers, orders, stock | Manufacturing, or at the matching design decision |
| Tests, measurements, scrutineering, failures | Validation |
| Task distribution, generation course | Generation history › Conclusion |
| open items, "next time" | Generation history › Potential for <GEN-B> |
| Items without a topic | file them under the matching chapter |

## "previous generations" and "this generation"

- **previous generations** summarises the old state briefly and links older documents.
- **this generation** describes what changed, why and how it went.
- If nothing changed, that is stated there with a reason.
- Write numbers uniformly within a documentation and always with a unit.

## Voice: as if the responsible person had written it

The documentation talks about the matter, not about how it came about.

- **No meta remarks.** Not "according to <name>", "presumably", "probably", "assumption", "derived from the STEP", "not present in CAD", "export". Evidenced sources (datasheet, rule, interview) are named, working routes are not. `check_page.py` flags these phrases: "presumably", "probably", "derived", "in CAD", "STEP export" or "export" as a source claim, "according to <person>".
- **Name open items briefly:** "unresolved" for questions that nobody could answer, `TBD` for values that are still to come.
- **Terms:** "computer" instead of "machine" for the PC, part names as in NX, rules with number.
- **Takeaways** are written by the responsible person. The section stays with `TBD` until they do it.
- **Replies in the user's language**, also follow-up questions and summaries in the chat.
