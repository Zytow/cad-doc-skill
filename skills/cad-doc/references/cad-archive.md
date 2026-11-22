# CAD archive: part and STEP files permanently in the documentation

Renderings, location images, drawings, weight and FEM need the geometry of the assembly. So that it does not have to be exported from NX again for every step and the state stays tied to the documentation, the geometry is kept permanently in the folder of the assembly.

## Folder

```
doc/<assembly>/cad/
  README.md        state, source, contents (written when archiving)
  nx/              NX folder of the assembly copied 1:1 (.prt), state of the top-level assembly
  step/            STEP per part in coordinates of the top-level assembly (product coordinates)
```

Derived files stay outside `doc/`: STL for Blender in `nx/export/<area>-<gen>/<assembly>/`, intermediate drawing files in `nx/drawings/`.

## Rules

1. **Archive once, then work only from the archive.** Renderings (`references/renderings.md`), drawings and volumes read the STEP files from `cad/step/`. Export again only if the CAD has changed.
2. **Part files as a folder copy.** The NX folder of the assembly is copied completely from the folder of the top-level assembly, with subfolders (made parts, purchased parts). This keeps the references of the sub-assembly valid and it can be opened from the copy. Rename nothing.
3. **STEP per part in product coordinates.** One file per component of the NX mapping (`references/nx-mapping.md`), exported from the top-level assembly, not from the sub-assembly. File name = NX name of the component, e.g. `SPK-ENCLOSURE.step`. Parts installed several times (four identical brackets) as one file with all instances. Purchased parts with many individual parts (computer) as one file.
4. **Record the state.** `cad/README.md` names:
   - top-level assembly and folder (e.g. `GEN-A-ASM.prt` in `GEN-A-ASM-260312`)
   - date of the copy and of the export
   - list of the STEP files with role
   - what is missing and why (e.g. export aborted, part not in NX)
5. **Never write back.** The copy is an archive. Changes to the CAD happen on the shared team drive; afterwards the archive is regenerated and the date in the README is updated.
6. **New generation, new state.** For <GEN-B> a separate archive is created (`cad-<gen-b>/` or a new state in the README); the <GEN-A> archive stays unchanged.

## With and without NX connector

| Step | With connector | By hand |
|---|---|---|
| Copy folder | – (file copy) | Explorer: copy the folder of the assembly from the shared team drive |
| Find bodies per component | `nx_list_objects` with `kind: "body"`, `owner: <component>` | select the part in the navigator |
| Export STEP | `nx_export_model` with `bodies` and `path: "cad-<gen>/<assembly>/<NX-name>.step"`, then copy from `NX_MCP_WORKSPACE` to `doc/<assembly>/cad/step/` | File → Export → STEP, "Selected objects", coordinate system absolute |

The export does not change the assembly. If NX shows "modified" afterwards, close without saving.

## Version control

Part files are large (the <GEN-A> enclosures together about 335 MB, single files above 50 MB) and binary. Therefore:

- `doc/*/cad/nx/` is in `.gitignore` and exists only locally in the vault. The source stays the shared team drive.
- `doc/*/cad/step/` and `cad/README.md` are checked in as long as every file stays below 50 MB. Larger STEP files also go into `.gitignore`, the README names them.
- GitHub rejects files above 100 MB.
