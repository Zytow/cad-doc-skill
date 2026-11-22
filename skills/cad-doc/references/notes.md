# Notes: external list for everything declared relevant

In the course of the work, the user or the team keeps saying things like "this is important", "remember this", "watch out for this", "this is relevant for later". Such notes do not necessarily belong in the assembly documentation, but must not get lost. They go in a separate, external notes list.

## Location

`context/notes.md` next to the vault, one file for the whole project. It is deliberately **outside** the assembly documentation: the documentation describes the assembly, the notes list collects what to watch for during the work.

## When an entry is created

- The user explicitly declares something relevant or important.
- An insight concerns several assemblies or the next generation ("direction of travel to the left in all location images").
- A stumbling block occurred that can happen again ("the Blender device query blocks the graphics driver").
- A decision about the way of working was made that is not a design decision ("photos are only cropped, no AI cut-outs").
- A contact person or a source was named that will be needed later.

Open questions (`references/open-questions.md`) and work (to-dos) do not belong here.

## Format

```markdown
## General

- **Location images always with the direction of travel to the left.** So that all images are comparable. 2026-11-21, user.

## Sensor housing

- **One bracket in <GEN-A> was fastened only with a cable tie.** For <GEN-B>, make sure to use a screwed joint, otherwise R 4.2 of <Rulebook> <year> is not met. 2026-11-20, photo of the product.
```

Per note:

- **Core statement** in bold, one sentence
- **Why** it is relevant or what follows from it
- **Date** and **source** (who said it, where it comes from)
- organised by assembly, plus "General" and, if needed, "Tools"

## Procedure

1. **Enter immediately** as soon as something is declared relevant, in the user's words, paraphrased.
2. **Before working on an assembly**, read the notes of that assembly and the general ones.
3. **Delete nothing.** If a note is outdated, it is struck through (`~~...~~`) and supplemented with date and reason.
4. **Transfer into the documentation** only if the note describes the assembly itself (then propose it as takeaway or requirement, do not adopt it silently).
5. **At the end of a work session**, briefly mention new notes.
