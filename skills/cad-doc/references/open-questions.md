# Open questions: a running list

During the work, questions keep appearing that nobody has confirmed: What is inside the amplifier enclosure? Is the air duct installed? What is the controller board's full name? In the documentation they are scattered as "unresolved" or `TBD`, in the chat they get lost. That is why there is a separate, running list.

The list is **not a to-do list.** To-dos are work that somebody does (render, photograph, enter). An open question is knowledge that is missing, and it is context for any further work, even when nobody is working on it at the moment.

## Location

`context/open-questions.md` next to the vault (same folder as the internal context document). One file for the whole project, organised by assembly, plus a section "General".

## What belongs in it

Every statement that is **not confirmed by the user** and does not come from a documented source (geometry, datasheet, rule, interview note):

- "unresolved" and `TBD` from the documentation, if a question stands behind it (not for pure gaps like "dimension TBD" that are filled by measuring)
- contradictions between photo, CAD, text and interview
- assumptions that are being worked with until somebody confirms them ("direction of travel x positive")
- questions that the user left open in the chat
- queries that are to go to the previous team

## Format

```markdown
## Power box

- [ ] **What belongs to the power box?** In NX, `<GEN-A>-PW-ASM` contains only the connector and the current sensor, no housing. Since 2026-11-21. Source: NX mapping. Who can answer: <GEN-A> power team.
- [x] **What is the data box called in NX?** `<GEN-A>-DT-ASM`. Resolved 2026-11-21 by the user (confirmation of the NX mapping).
```

One line per question:

- **Question** in bold, phrased as a real question
- **State:** what is known and why it is open
- **since** date, **source** (photo, NX, interview, chat)
- **who** can answer, if known
- optionally the section of the documentation that depends on the answer: `[[Power box#As-built state <GEN-A>]]`

## Procedure

1. **Enter immediately** when a question arises. Do not collect.
2. **Before any work on an assembly**, read the questions of that assembly. Nothing that is open there is written in the documentation as fact.
3. **At the end of every work session**, tell the user the new questions.
4. **A question is resolved** only by the user or a documented source. Then tick it off, add the answer and the date, and update the documentation. Resolved questions stay, so the path remains traceable.
5. **Avoid duplicates:** before entering, search for an identical question and extend it.

## Delimitation

| List | Content | Location |
|---|---|---|
| To-dos | work that gets done | `## To-dos` in the assembly documentation |
| Open questions | knowledge that is missing, not confirmed | `context/open-questions.md` |
| Notes | knowledge that was declared relevant | `context/notes.md`, see `references/notes.md` |
| Context | what an assembly does, NX names | `context/assembly-context.md` |
