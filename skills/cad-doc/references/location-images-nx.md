# Creating location images with NX

A location image shows where a part or assembly sits in the product: the environment light, the target highlighted dark, always from the same camera. The procedure applies to any part of the product, whether enclosure, motor, brake, aero part, battery pack, suspension, cooling or cable run. The images are created through the NX connector (`mcp__nx__*`). By hand in NX the steps are the same.

Storage, format and embedding are covered in `references/photos-and-location.md`.

## Terms

- **Target:** what the documentation is about. One component, several instances (four uprights) or a whole system made of many components (brake system, cooling circuit).
- **Module:** the next larger unit in which the target is sensibly placed. It follows from the NX structure: in the path from `nx_list_components`, go up until the assembly is recognizable on its own (a wheel, the battery housing, the front wing).
- **Environment:** everything that stays visible in the image but is not the target.
- **Obstruction:** everything that hides the view of the target. It depends on the target: for an enclosure inside a side pod, the body panel is an obstruction; for an aero part, the body panel is environment.

## Levels

| Level | When | Environment | File |
|---|---|---|---|
| 1 whole product | always | the whole product from the top-level assembly | `<prefix>-<gen>-location.png` |
| 2 module | the target is small or hidden in the overall view, or belongs to a module | only the module, centred and filling the frame | `<prefix>-<gen>-location-<module>.png` |
| further view | the side view does not show the location unambiguously | as in the level, different viewing direction | suffix `-top`, `-front`, `-iso` |

Level 1 is never omitted; it shows where the target or module sits in the product. Level 2 can repeat when a module sits inside a larger one (cell -> segment -> battery housing); then one image per level, from large to small.

Rule of thumb for level 2: if the target is smaller than about one twentieth of the product length, or if it is hidden inside a module, level 2 is added.

### Typical modules and views

| Area | Example targets | Module for level 2 | Useful additional view |
|---|---|---|---|
| Electronics | enclosures, control units, sensors | usually none; for sensors, the part they are mounted on | `-top` if the enclosure sits centrally |
| Suspension | upright, wishbone, spring-damper, anti-roll bar | one wheel with upright and links | `-front` for link geometry |
| Brake | brake caliper, disc, master cylinder, lines | one wheel (caliper, disc) or the pedal box (master cylinder) | `-top` for the routing of the lines |
| Drive | motor, gearbox, inverter, drive shaft | wheel with motor and gearbox, or the drivetrain | `-iso` |
| Battery | cell holder, segment, fuse, battery management board | battery housing, if needed a segment | `-top` into the open housing |
| Aero | front wing, rear wing, diffuser, side pod | the aero package or the wing itself | `-top` and `-front`, wings extend across the width |
| Cooling | radiator, pump, hoses | cooling circuit (system) | `-top` |
| Cockpit | steering wheel, pedal box, seat | cockpit assembly | `-iso` |
| Structure, frame | nodes, brackets, inserts | frame section | `-iso` |

The table is a template. What matters is that a reader unfamiliar with the product understands the location from two images.

## Principles

- **Never save.** Hiding and colouring change only the display. After every image, everything is reset with `nx_restore_display`. If the assembly were saved, the colours would stay for the whole team.
- **Highlight through colour, not through selection.** The NX selection highlight (`nx_set_highlight`) is only visible live in the window, never in the image. The target is coloured dark with `nx_set_appearance`.
- **One camera per level and view.** The camera is set once for the whole product (or module) and reused for every target. That way the product stands identically in all images and only the highlighted target changes. This applies across all areas of a generation, so that location images of an enclosure, a brake and a battery can be compared directly.
- **Direction of travel to the left** in every side view. In the top view the front also points to the left.
- **Whole instances and systems.** If the target exists several times (four uprights), all instances are coloured dark, unless the documentation covers only one. For systems (brake system, cooling circuit, cable runs), all components of the system are coloured.
- **Always look at the first image.** According to the connector, the tools are not tested for NX 2506.

## Colours

| What | Colour | Transparency |
|---|---|---|
| Target | dark grey `#3C3C3C` | 0 (opaque) |
| Environment | light grey `#D9D9D9` | 0, with a hidden target 50-70 |
| Background | white | - |

The same colours for all areas and generations. The accent colour is reserved for highlights in renderings (`references/renderings.md`).

## Procedure level 1: whole product

Prerequisite: the top-level assembly of the generation (e.g. `<GEN-A>-ASM`) is open in NX and the components are loaded.

1. **Find target and obstructions:** The components of the target are in the confirmed NX mapping (`references/nx-mapping.md`). Find obstructions with `nx_list_components` and `name_contains` (e.g. `Cover`, `Brake`, `Wing`); for systems use several search terms. Note the IDs.
   - Decide the obstructions based on the target: everything that lies between camera and target and is not needed for orientation. Typical: body panels, side pods, seat, driver dummy, cable sleeves. What helps as a reference (frame, wheels) stays.
   - Components that are not loaded (column load state) are missing from the image. Load them first.
2. **Hide obstructions:** `nx_set_visibility` with `mode: "hide"`. Note the `restore_id`. If an obstruction has to stay visible as a reference, set it to 50-70 % transparency in step 3 instead.
3. **Colour the environment light:** `nx_set_appearance` for all visible components except the target. Note the `restore_id`.
4. **Colour the target dark:** `nx_set_appearance` for all components of the target, transparency 0. Note the `restore_id`.
5. **Set the camera (only for the first image of the generation):** `nx_set_camera` with a view from the side and `fit: true`. Then read `origin` and `scale` with `nx_get_camera`, note them and reuse them for all further targets.
   - The viewing direction depends on the coordinate system. In <GEN-A>, x positive = front, so the front is on the left when looking from +Y: `view_from: [0, 1, 0]`, `up: [0, 0, 1]`. The top view accordingly from +Z with the front on the left.
6. **Capture the image:** `nx_capture_view` with
   - `width: 2000`, `height: 982`
   - `background: "white"`
   - `style: "shaded_with_edges"`
   - `path: "location/<prefix>-<gen>-location.png"`, then copy to `doc/<assembly>/images/`
7. **Reset:** `nx_restore_display` in reverse order (target, environment, visibility).
8. **Next target:** with the same obstructions, from step 3; otherwise from step 2. The camera stays.

Several targets of one generation run in one pass. Group targets with the same obstructions, so that hiding happens only once.

## Procedure level 2: location in the module

1. **Determine the module:** Read the path of the target from `nx_list_components` and choose the matching parent assembly (table above). Note all components of the module including the target.
2. **Show only the module:** `nx_set_visibility` with `mode: "isolate"` and the IDs of the module. Everything else is hidden. Note the `restore_id`.
3. **Colour** as in level 1: module light grey, target dark grey. If the target is inside (cell holder in the battery housing, gears in the upright), set the shell of the module to 50-70 % transparency.
4. **Camera on the module:** `nx_set_camera` with `fit: true`. `fit` frames only the visible bodies and centres them, so the module fills the image.
   - Choose the viewing direction according to what shows the location best (table above). Reuse the same camera for all targets in the same module (`nx_get_camera`).
   - For mirrored modules (wheel front left and right) always take the same side and state it in the text.
5. **Capture** as in level 1, file `...-location-<module>.png`, additional views with a suffix (`...-location-battery-top.png`).
6. **Reset** with `nx_restore_display` in reverse order.

## Checking

- Is exactly the intended target dark, and for systems complete? Compare with file names, the bill of materials and a photo of the product.
- Is nothing cut off, and is the format 2000 x 982?
- Do all images of one level and view stand identically? Look at them all side by side as a contact sheet.
- Is everything reset in NX? `nx_get_appearance` for an environment component shows the original colour.

## Embedding

The location images go in every documentation where the mounting position is described: for enclosures as the first image under Mounting, for other parts in a section "Location in the product" before the first design chapter. The levels follow from large to small, each with one sentence on view and viewing direction:

```markdown
**Location in the product:** Side view of the whole product <GEN-A>, direction of travel to the left.

![Brake caliper in the product, side view <GEN-A>, calipers highlighted dark](images/bc-<gen>-location.png " =700x344")

**Location at the wheel:** Wheel front left with upright, view from outside.

![Brake caliper at the wheel front left, caliper highlighted dark](images/bc-<gen>-location-wheel.png " =700x344")
```

## By hand in NX

The same steps without the connector: hide obstructions (Ctrl+B), colour environment and target via "Edit Object Display" (Ctrl+J), orient and fit the view (F), export the image via File -> Export -> PNG at 2000 x 982 with a white background. Afterwards **close the assembly without saving**.
