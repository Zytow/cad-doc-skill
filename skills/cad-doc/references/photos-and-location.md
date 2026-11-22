# Photos of the product and location images

Renderings show the state in the CAD. Photos of the real product show what is actually installed. Only both together give a reliable as-built state. Developed on a set of electronics enclosures, <GEN-A> → <GEN-B>.

## Location image: where does the assembly sit in the product?

Every part and every assembly of the product gets a location image, regardless of the area (electronics, drive, brake, aero, battery, suspension). If there is a Mounting section, it is the first image there, even before the mounting concept. Otherwise it stands as "Location in the product" under Overview. Parts inside a module (wheel, motor, battery pack) additionally get a location image in the module.

- **Content:** side view of the complete product from the NX top-level assembly, frame and surroundings light, the assembly highlighted dark. All location images of a generation from the same camera, so that they can be compared.
- **Creating:** with the NX connector per `references/location-images-nx.md`. That file also holds the second stage for parts in a module (a single wheel, a battery pack), `…-location-<module>.png`.
- **Format:** 2000 x 982 px, white margin instead of distortion. Embed with `" =700x344"`, for a very small target `" =900x442"`. Sizes and placement of all images are governed by `references/images.md`.
- **File name:** `images/<prefix>-<gen>-location.png`.
- **Text before it:** name the view and direction of travel, and if needed one sentence on the position (e.g. "low in the front section, directly next to the amplifier enclosure").

```markdown
**Location in the product:** side view of the complete product <GEN-A>, direction of travel to the left.

![Motor mount in the product, side view <GEN-A>, motor mount highlighted dark](images/motor-mount-gen-a-location.png " =700x344")
```

Crop to the uniform format:

```bash
ffmpeg -i "Motor mount side view.png" -vf "scale=2000:982:force_original_aspect_ratio=decrease,pad=2000:982:(ow-iw)/2:(oh-ih)/2:white" doc/motor-mount/images/motor-mount-gen-a-location.png
```

If the location image is still missing, write `**Location in the product:** TBD`, and `check_page.py` warns.

### Securing the assignment

Location images look very similar. A swapped image is hardly noticed when reading.

- Use only files with the assembly name (`Motor mount side view.png`). Images without names, e.g. from a chat, are assigned first before they are inserted.
- If images arrive again, compare them with the installed ones: an identical checksum is unambiguous, otherwise look at both images side by side as a contact sheet.
- Check whether the highlighted part matches the photo (shape, position, neighbours).

## Photos of the product

### Storage and name

- `doc/<assembly>/images/<prefix>-<gen>-photo-<content>.jpg`, e.g. `spk-gen-a-photo-mounting-cable-tie.jpg`.
- The content in the name says what is to be seen (`installed`, `lid`, `connector-close`, `mounting`, `open`).

### Editing: only what is necessary

No cut-outs, no AI tools. This is enough:

1. **Crop** to the relevant area, enclosure and its attachment, little surroundings.
2. **Rotate** if the photo lies sideways.
3. **Downscale** to at most 1800 px on the long side, JPEG.

```bash
# Crop in percent: left L, top T, width W, height H
ffmpeg -i IMG_6383.jpg -vf "crop=iw*W/100:ih*H/100:iw*L/100:ih*T/100,scale='min(1800,iw)':-2" -q:v 3 images/spk-gen-a-photo-lid.jpg
# rotate 90° clockwise: transpose=1
```

Blurred photos and duplicates are dropped. They go on a "photograph again" list in the to-dos.

With many photos: first look at all of them as a contact sheet, clarify the assignment to the assembly, then crop. A subagent can take over the image analysis.

### Embedding

- **Next to the matching rendering**, in the same row, if the comparison says something (deviation, as-built state). If photo and rendering show the same thing without a new statement, only one of them (`references/images.md`):
  `![Enclosure on the frame tubes](images/spk-gen-a-mounting.png " =350x233")![Enclosure in the product from above](images/spk-gen-a-photo-lid.jpg " =350x205")`
- **If there is no rendering** (assembly not in NX), the best overview photo becomes the cover image. Further photos go under Mounting and Structure.
- **Height** in the size field is calculated from the aspect ratio of the cropped photo.
- **Alt text** describes what you see, including anomalies: "Bracket on the enclosure with cable tie instead of screw".

## Photo and documentation contradict each other

The photo shows the as-built state on the product. If it deviates from the CAD or the text, the following applies:

1. **Report, do not change silently.** Name the contradiction to the user, with photo and text passage.
2. **Adjust after approval:** the text describes what was installed. The target state from the CAD stays as a sentence ("four M4 screws are intended; on the product one bracket was attached with a cable tie only").
3. **Evaluate the rule table against the as-built state.** A rule is only "met" if the product meets it, not just the CAD.
4. **What the photo does not settle** becomes "unresolved" (e.g. which fan draws air in).

Examples: an enclosure with three fans instead of the planned vent grille; an enclosure with a cable tie on one bracket (mounting rule R 4.1 therefore not met).

## Background knowledge outside the documentation

What an assembly does electrically (boards, buses, long forms of the abbreviations) does not have to go into the assembly documentation. It belongs in an internal context document next to the vault, e.g. `context/assembly-context.md` with sources in `context/sources/`. Read it before working on an assembly and add new findings there.
