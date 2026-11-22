# Image review: are perspective and content of every rendering sensible?

A rendering can be technically clean and still useless: the enclosure hangs at an angle in space, the exploded view flies towards the camera, the highlighted part is hidden. Therefore every rendering is checked against this list after rendering, before it goes into the documentation. The result is kept as a log in `context/image-control.md`.

Developed when the first renderings of several electronics enclosures stood in their oblique installed position and looked tilted and floating.

## Procedure

0. **Check completeness:** Are all parts of the NX mapping in the image? Report placeholders (empty board, missing housing) to the user and look for the real model: list all components under the assembly, do not just filter by name, and read the references of the assembly file.

1. **Render a preview** (`QUICK=1`), all shots of an assembly.
2. **Look at the contact sheet** of all shots side by side (ffmpeg `hstack`/`vstack`).
3. **Check every shot against the criteria below**, in the log per image: OK / adjust, with a concrete measure.
4. **Adjust** (orientation, viewing angle, explosion direction, margin, materials), preview again.
5. **Only then render in full.** After the full render, look at the contact sheet once more.
6. **Remove duplicate statements** (`references/images.md`): if two shots show the same thing, one goes.

## Criteria for all shots

| Criterion | Good | Bad |
|---|---|---|
| Orientation | recognisable as in the product: enclosures that lie flat, with lid on top; panels and enclosures on a side wall (e.g. a triangular panel, a side panel) upright as installed, outer side towards the camera, only the tilt in space straightened | enclosure in oblique installed position, looks tilted or floating; or a vertical panel laid flat so that it cannot be recognised |
| Framing | assembly fills 60–80 % of the image width, nothing cut off | tiny in the middle or pushed to the edge |
| Viewing angle | obliquely from front above (azimuth 30–50°, elevation 20–35°), three sides visible | exactly frontal without depth, from below, backlight |
| Visibility | the side with the most features (connectors, openings, brackets) faces the camera | features on the far side |
| Ground contact | shadow on the ground, assembly rests on it | assembly floats without reference |
| Light and contrast | light parts against a dark background, dark parts clearly separated by rim light | parts blur into the background |

## Criteria per shot

| Shot | Purpose | What to look for |
|---|---|---|
| product | cover image, this is what the assembly looks like | closed, main side with connectors visible, nothing in the accent colour |
| explosion | what it consists of, in which order it is assembled | parts **along the assembly axis** (lid normal), the axis lies **in the image plane** and does not point at the camera; gaps large enough that nothing overlaps; contents (board, computer) visible; small parts (screws, brackets) stay close to their seat |
| open | what is inside | only if it shows something the exploded view does not (e.g. position of the contents in the installed state) |
| mounting | how it hangs on the product | brackets in the accent colour and **not hidden**, view onto the side of the brackets, frame tubes if needed |
| mounting-detail | one bracket in detail | surroundings translucent, bracket fills the image |
| side-… | features of one side | orthographic, only sides with features |
| contents | purchased part alone | in installed position or aligned, parts close together |
| location | where in the product | see `references/location-images-nx.md` |

## Establishing orientation

Parts that are installed obliquely in the top-level assembly are rotated onto their own axes for all shots except the location in the product:

```bash
freecadcmd scripts/tools/axes.py doc/<assembly>/cad/step/<lid-or-housing>.step
```

The script prints the normal of the largest planar face ("up") and the longest edge ("along"). Both go into the configuration:

```json
"align": {"up": [-0.058, 0.9455, 0.3204], "along": [-0.8046, -0.2342, 0.5457]}
```

- **Upright in installed position** (panels, enclosures on a side wall): "up" is then the vertical in the plane of the plate (world Z, freed of the normal of the outer side), "along" the cross product such that the outer side faces the camera. Example, a triangular panel: lying flat it was not recognisable, upright immediately. The explosion then runs across the plate, and the camera looks obliquely from the front (azimuth about 70°) so that the parts separate sideways.
- For thin plates both sides have the same area. If "up" points to the inside, flip the sign so that the lettering or the lid points up.
- Offsets in `states` stay in product coordinates, `render_assembly.py` rotates them along.
- Parts that are already modelled axis-parallel need no alignment.

## Log

`context/image-control.md`, one table per assembly:

```markdown
## Amplifier enclosure (YYYY-MM-DD)

| Shot | Result | Measure |
|---|---|---|
| product | adjusted | oblique and floating in installed position, aligned to lid axis |
| explosion | OK | lid and board upward, board visible |
```
