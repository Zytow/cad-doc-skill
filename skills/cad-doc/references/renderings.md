# Renderings

Renderings show how an assembly is built and how it is mounted on the product. The procedure was developed on three electronics enclosures and applies to any part of the product.

Tool chain: geometry as STEP -> FreeCAD converts to STL -> Blender (Cycles) renders from a JSON configuration. The NX connector only simplifies the export. Every step also works by hand, and with ready-made STEP files you start directly at step 3.

## Requirements

Agreed with the team and implemented on the first enclosures:

- **Studio, photorealistic:** soft studio light, cyclorama as the background, no scene around it.
- **3D-printed parts light grey** with fine layer lines (0.2 mm). The lid is a touch lighter than the housing, so that the parts can be told apart. **No orange.**
- **Background dark grey,** so that the light parts have contrast.
- **Highlights in the accent colour,** e.g. a bracket or the part the section is about. Otherwise there is no accent colour in the image. The accent colour is configurable via the `accent` setting, default `#D62F2F`.
- **Overview images opaque,** the accent-coloured part as the eye-catcher.
- **Close-ups with a translucent environment:** enclosure and frame tubes almost transparent, so that the detail stays freely visible.
- **Side views orthographic** against a flat grey with enough margin. The part never touches the image edge.
- **Purchased parts as one block** with a fitting material (computer, receiver, board). At most a rough exploded view of their own.
- **Frame tubes from the real geometry** (point, direction, radius), not estimated. A substitute envelope instead of the frame is only a stopgap and is named as such.
- **Format:** PNG 2400 x 1600 px. Display size and space in the documentation as in `references/images.md` (cover image 600, overview 500, standard 400, detail 300).

## Colours

### Accent colour

| Name | Hex | Use |
|---|---|---|
| Accent | `#D62F2F` (configurable via the `accent` setting) | highlight in renderings, identification letters in drawings, headings in the PDF |
| Black | `#000000` | text |
| White | `#FFFFFF` | background of location images, drawings and PDF |

### Materials in the rendering

Blender calculates with linear colour values. The hex values are the sRGB equivalent of the base colour. In the finished image they look slightly different because of light and exposure.

| Material | Use | Blender linear (R, G, B) | sRGB |
|---|---|---|---|
| `print` | 3D-printed part (housing) | 0.33 · 0.34 · 0.36 | `#9B9EA2` |
| `print_lid` | 3D-printed part, light (lid) | 0.40 · 0.41 · 0.43 | `#AAACAF` |
| `accent` | highlight, accent colour (default; follows the `accent` setting) | 0.672 · 0.028 · 0.028 | `#D62F2F` |
| `backdrop` | cyclorama of the studio images | 0.13 · 0.135 · 0.145 | `#65676A` |
| Side background | flat grey of the orthographic sides | 0.20 · 0.205 · 0.215 | `#7C7D80` |
| `frame` | frame tubes | 0.06 · 0.065 · 0.07 | `#45484B` |
| `ghost` | translucent environment (alpha 0.14) | 0.62 · 0.64 · 0.67 | `#CED1D6` |
| `alu` | aluminium, heat sink, sheet-metal bracket | 0.78 · 0.79 · 0.81 | `#E5E6E8` |
| `steel` | steel, screws | 0.62 · 0.62 · 0.64 | `#CECED1` |
| `rubber` | seal, rubber | 0.018 · 0.018 · 0.02 | `#242427` |
| `pa_black` | black plastic (connectors, fans, fittings) | 0.03 · 0.03 · 0.032 | `#303032` |
| `pcb_green` | circuit board | 0.03 · 0.22 · 0.09 | `#308155` |
| `peek` | PEEK natural (cell holder, discs) | 0.66 · 0.60 · 0.47 | `#D4CBB7` |
| `nickel` | nickel-plated sheet (busbars) | 0.60 · 0.58 · 0.54 | `#CBC7C2` |
| `gold` | gold-plated pads (ENIG) | 0.72 · 0.42 · 0.12 | `#DCAD61` |
| `nylon` | polyamide natural (plastic screws, white connectors) | 0.80 · 0.78 · 0.72 | `#E7E5DD` |
| `cell` | cell wrap (shrink sleeve), end faces automatically `cell_cap` | 0.78 · 0.76 · 0.70 | `#E5E1D9` |
| `cell_cap` | cell terminals, nickel-plated | 0.66 · 0.66 · 0.67 | `#D4D4D5` |

Choose colours from photos, not by feeling: colour the parts the way they look on the product. For cells, `render_assembly.py` sets the end faces (normal along `cell_axis` in the configuration) to the terminal material.

**Boards from NX:** The circuit board is often not called "PCB" in NX, but sits e.g. under "PAD". Separate circuit board, pads and components by size: the largest body is the circuit board (green), small pads gold, components black, leave out the silkscreen. Export duplicate bodies (e.g. two congruent bonds) only once, otherwise the surfaces flicker.

**Check for overlaps before rendering:** intersect all parts pairwise (FreeCAD `common`), remove duplicates, and report small overlaps as a CAD finding in the documentation.

Location images from NX use their own colours (target `#3C3C3C`, environment `#D9D9D9`, white), see `references/location-images-nx.md`.

### Light and camera

| Setting | Value |
|---|---|
| Renderer | Cycles, denoising on; GPU with `GPU=CUDA` (on an 8 GB GTX 1070: preview in 20 s instead of several minutes), otherwise CPU |
| Colour management | AgX, look "AgX - Punchy", exposure -0.8 |
| Light | Studio HDRI from Blender plus four area lights (key, fill, rim, top), strength via `LIGHT`, additional light from below for views from below |
| Samples | 192 full, 24 in the trial run (`SAMPLES` overrides) |
| Lens | 85 mm standard, 70 mm for the mounting, 90 mm with aperture 64 for close-ups |

## Shot list per assembly

| Shot | Content |
|---|---|
| product | cover image, closed, obliquely from the front |
| rear | obliquely from behind |
| open | lid and seal lifted, contents visible |
| explosion | rough exploded view of all parts along the assembly axis |
| side-front/-rear/-left/-right/-top/-bottom | orthographic, flat background, without brackets |
| mounting | assembly on the structure, bracket in the accent colour |
| mounting-detail-... | close-up per bracket type, environment translucent |
| contents | purchased part alone, e.g. computer with connectors |
| location | side view of the whole product from NX, see `references/location-images-nx.md` |
| location-<module> | for parts in a module: only the module (wheel, battery housing), see `references/location-images-nx.md` |

For parts without a lid (bracket, wing, upright), `open` and the side views that show nothing new are omitted. Photos of the real product stand next to the matching rendering (`references/photos-and-location.md`).

## Workflow

| Step | With NX connector | By hand |
|---|---|---|
| 1 Identify the assembly | `nx_list_components` | Assembly navigator in NX |
| 2 Export STEP per part | `nx_export_model` | File -> Export -> STEP |
| 3 Analyse the parts | `nx_measure_bounds`, `nx_measure_mass` as a cross-check | FreeCAD scripts, photos, interview |
| 4 Create STL | - | `step2stl.py` |
| 5 Create configuration | - | JSON in `tools/render/` |
| 6 Render | - | `render_assembly.py` in Blender |
| 7 Check | - | Look at the contact sheet |
| 8 Embed | - | Note of the assembly |

### 1. Identify the assembly

The basis is the confirmed NX mapping under Overview (`references/nx-mapping.md`). If it is missing, it is created and confirmed here first. Parts that were not found are looked up by the user by hand.

- Find the component in the top-level assembly: `nx_list_components` with `name_contains` (e.g. `Amp`, `Sensor`) or search in the assembly navigator. Note part names and path, e.g. `<GEN-A>-EL-SPK-ASM`.
- List all parts below it and give each a **role**: housing, lid, seal, bracket, board, purchased part, screws.
- Check that everything is loaded (column load state). Parts that are not loaded or only partially loaded are otherwise missing from the export.
- If an assembly is called something different in NX than in the team, search via its location in the whole product and record the NX name in the documentation (`nx_assembly`).

### 2. Export STEP per part

**Look in the CAD archive first** (`doc/<assembly>/cad/step/`, `references/cad-archive.md`). If the STEP files are there, the export is not needed. If they are missing, they are exported as described in `cad-archive.md` and stored there, not only for the rendering.

One STEP file per part (or per material group of a purchased part), **in coordinates of the top-level assembly**. Only this way do parts and frame tubes fit together without rework.

- **With connector:** `nx_export_model` with `path: "export/<assembly>/<part>.step"` per component or body selection. The files land in the NX working folder (`NX_MCP_WORKSPACE`) and are copied into the vault to `nx/export/<area>-<gen>/<assembly>/`.
- **By hand:** In NX select the parts, File -> Export -> STEP (AP214), "Selected objects", coordinate system absolute. Or take existing STEP files from the team drive.
- **Split purchased parts by material,** not by individual part. The computer of an amplifier enclosure consists e.g. of `amp-plastic`, `amp-metal`, `amp-foil`, `amp-rubber`, `amp-heatsink`, `amp-fan`. This way a few materials are enough for a credible image.
- **Never save.** The export does not change the assembly. If `modified` in NX is true, close the assembly without saving.
- **File names** are the part names from the configuration, lower case, without spaces (`housing.step`, `bracket.step`).

### 3. Analyse the parts

Before rendering, it must be clear what each part is and does.

- **Dimensions and bodies:** `step2stl.py` outputs the number of bodies and the outer dimensions per file. `volume.py` delivers the volume for the weight table. Store the result as `nx/export-data-<assembly>.json`.
- **Holes:** `holes.py`, grouped by diameter and axis, each group with its purpose.
- **Function:** from geometry, photos of the product and interviews with the previous team. Background knowledge on the electronics is in the internal context document.
- **Define the material per part** (table above). Unknown means `print` for printed parts; the question goes into the to-dos.
- **Frame tubes:** For each tube read point, direction and radius from NX (with the connector via the cylinder faces of the tubes, by hand with "Measure" in NX or in FreeCAD) and write them with length `t: [from, to]` in mm into the configuration.
- **Cross-check with NX:** `nx_measure_bounds` and `nx_measure_mass` for dimensions and volume. If they deviate, a body is missing or a sheet body was counted.

### 4. Create STL

```bash
freecadcmd tools/step2stl.py nx/export/<area>-<gen>/<assembly>-step nx/export/<area>-<gen>/<assembly>
```

Fine meshing (0.015 mm); sheet bodies without volume are meshed as well.

### 5. Create the configuration

`tools/render/<assembly>.json`, template `scripts/tools/example-assembly.json`:

| Field | Content |
|---|---|
| `folder`, `prefix` | target folder under `doc/` and file prefix, e.g. `speaker`, `spk-<gen>` |
| `stl_dir` | folder of the STL files |
| `parts` | `{part: material}` |
| `tubes` | frame tubes `{p, d, r, t}` in mm |
| `states` | displacements for `open` and `explosion`, `{part: [dx, dy, dz]}` in mm |
| `shots` | per image: `name`, `az`, `el`, `state`, `hide`, `only`, `ghost`, `tubes`, `materials` (e.g. bracket `accent`), `margin`, `lens`, `fstop`, `focus_mm`, `ortho`, `no_background`, `light_below` |

Highlighting per shot via `materials: {"bracket": "accent"}`, translucent environment via `ghost` and `ghost_tubes`.

### 6. Render

```bash
QUICK=1 blender --background --factory-startup --python tools/render_assembly.py -- tools/render/<assembly>.json
blender --background --factory-startup --python tools/render_assembly.py -- tools/render/<assembly>.json [shot ...]
```

First the trial run (30 % resolution, 24 samples), look at it, then full. Individual shots can be re-rendered selectively. Output: `doc/<folder>/images/<prefix>-<shot>.png`.

### 7. Check

Every image is checked as described in `references/image-control.md` (alignment, framing, viewing angle, exploded direction, visibility of the brackets), first as a preview, then after the full render. The result goes into the log `context/image-control.md`. Obliquely installed assemblies are rotated onto their own axes with `"align"` (`tools/axes.py`).


- Look at all images side by side as a contact sheet.
- Nothing cut off, nothing overexposed, no view tilted.
- Accent colour only on the intended part, purchased parts recognizable as a block.
- Compare with the photos of the product. Report deviations between CAD and product to the user (`references/photos-and-location.md`).

### 8. Embed

- Cover image `product` at the top of the note, `explosion` under Overview, `mounting` and details under Mounting, `open`, sides and `contents` under Build.
- Alt text describes what is seen. Put photos in the same line next to the matching rendering.

## Programs

- FreeCAD 1.1 (`freecadcmd`) for STL, volume, holes. A traceback of the FEM importer at startup is harmless.
- Blender 5.x, Cycles. GPU via the environment variable `GPU=CUDA` (or `GPU=OPTIX` on RTX cards): `render_assembly.py` then queries only the devices of that type (`get_devices_for_type`) and switches to GPU. **Never call the general device query (`refresh_devices`),** it blocked the graphics driver once. Test a new machine first with `QUICK=1` and a time limit (`timeout 240`). On an 8 GB GTX 1070 the GPU was barely faster than the CPU, and the denoising ran out of memory on large scenes ("OIDN error: out of memory"). Render the missing shots afterwards on the CPU without `GPU`, or switch denoising off with `DENOISE=0`.
- ffmpeg for contact sheets and cropping.

## Pitfalls

- **Coordinate system:** An export from a subassembly lies in its own system, not in the product system. Then tubes and parts do not fit together.
- **Partially loaded assemblies:** Some NX tools abort then. Load the component completely or export by hand.
- **Hidden bodies** are exported as well and distort dimensions and volume. Check before the export.
- **Sheet bodies** (foils, stickers) have no volume. They are meshed but do not count toward the weight.
