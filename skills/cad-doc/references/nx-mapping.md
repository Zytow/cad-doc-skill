# NX mapping: build the context before working

Before anything is exported, measured, rendered or drawn, it must be settled what the assembly and each of its parts are called in NX. In a team, a part is often called something different than in NX, boards are missing or are called `PCB` or `BOARD`, and purchased parts sit as unnamed bodies in a subassembly. Whoever guesses here renders the wrong part or later searches in the wrong place.

The mapping is therefore **step 0 of any work on an assembly**. It serves two purposes:

1. **Context for the work:** every further step (export, location image, drawing, weight) relies on exactly these names.
2. **Knowledge for the team:** the table goes in the documentation under Overview, so that the next generation finds the part in NX immediately.

## Procedure

| Step | With NX connector | By hand |
|---|---|---|
| 1 Determine the top-level assembly | `nx_get_status` (open assembly, path) | Name the file and revision, e.g. `<GEN-A>-ASM-260312/<GEN-A>-ASM.prt` |
| 2 Search for candidates | `nx_list_components` with `name_contains`, several search terms | Assembly navigator, search field |
| 3 List the parts below | `nx_list_components` from the path of the assembly, note the columns load state and suppression | Expand the navigator |
| 4 Assign a role to each part | dimensions (`nx_measure_bounds`), location, image (`nx_capture_view`) | Click the part, look at it |
| 5 Write the table | - | into the documentation under Overview |
| 6 Have it confirmed | - | The user checks the table, only then does work continue |

### Search terms

Do not search only for the team's own name for the part. What has proven useful:

- Abbreviation and long form: `Amp`, `Amplifier`, `PD`, `PowerDelivery`
- Generation tag and area from the part key: `<GEN-A>-EL-`, `<GEN-A>-ME-`
- Function words: `Housing`, `Lowerhousing`, `Lid`, `Cover`, `Bracket`, `Holder`, `PCB`, `Board`
- English and German, upper or lower case does not matter
- Neighbours: if the photo shows the part next to another enclosure, look at the components near it

**The name search finds only the assembly, not reliably its parts.** Parts are often named quite differently from the assembly (for example `<ABBR>_lower_bend_singlepiece`, a vendor product name, connectors named after the manufacturer). Therefore, once the assembly is found, list **all** components below it completely, without a name filter, via the path. Cross-check without NX: the assembly file (`...-ASM.prt`) contains the file names of all installed parts as text; they can be read out with a short script and compared with the table. If the folder contains parts that are not installed (e.g. a populated board next to a placeholder), note this in the table and report it to the user.

### If you cannot find it

If an assembly or part is not found unambiguously, **do not guess and do not continue working**; ask the user to look it up in NX by hand. The question states:

- what is being searched for (enclosure, board, bracket),
- which search terms already gave no hit,
- which candidates exist, with path,
- what is needed: component name and path in the navigator.

Until the answer arrives, the table says "unresolved", and all steps that need the part wait.

### Always have it confirmed

Even a mapping that was found is shown to the user and confirmed before the first export, location image or rendering. Only then does it count. The confirmation goes in the table with the date.

## Table in the documentation

Under `# Overview` of every assembly documentation, directly after the introduction:

```markdown
### NX mapping

Top-level assembly: `<GEN-A>-ASM.prt` (revision 2026-03-12). Confirmed on 2026-11-21.

| Part | Role | Name in NX | Path in the top-level assembly |
|---|---|---|---|
| Assembly | whole enclosure | `<GEN-A>-EL-SPK-ASM` | `<GEN-A>-ASM / <GEN-A>-EL-Electronics / <GEN-A>-EL-SPK-Speaker` |
| Housing | 3D-printed part | `<GEN-A>-EL-SPK-LOWERHOUSING` | under `<GEN-A>-EL-SPK-ASM` |
| Board | purchased part, carried over from <GEN-B> | `<GEN-B>_AMP` | under `<GEN-A>-EL-SPK-ASM` |
| Bracket on the structure | - | unresolved | - |
```

- **Part:** the term as used in the documentation.
- **Role:** housing, lid, seal, bracket, board, purchased part, screws.
- **Name in NX:** exact, in code notation. If the part is missing in NX, write "not in NX".
- **Path:** far enough that it can be found in the navigator.
- The NX name of the assembly is also in the frontmatter as `nx_assembly`.

## Internal context document

The mapping of all assemblies of an area is additionally collected in the internal context document (`../context/`), column "in NX". Read it there before working on an assembly, and add new findings there and in the documentation.

## Checking

- Every row has an NX name or "unresolved" or "not in NX".
- The table is confirmed (date in the sentence above it).
- The names match the file names of the exports and the components of the location images.
