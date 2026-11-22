# Images in the documentation: selection, placement, size, demand

An image appears in the documentation because it shows something the text alone explains badly. It sits where the reader is reading exactly that, and as large as needed to recognise it. These rules apply to every assembly and equally to renderings, photos, location images and drawings.

Read this file before you insert images or restructure a page.

## 1. Principle: text leads, image proves

- **Every image has a statement.** Before inserting, formulate in one sentence what the reader should recognise in it ("the two mounting lugs on the end faces"). If no sentence comes to mind, the image does not go into the documentation.
- **The paragraph directly before describes exactly what the image shows.** Image and paragraph deal with the same part, the same side, the same feature. An image of the cable gland belongs under the sentence about the cable gland, not under the sentence about cooling.
- **The text refers to the image** when something is to be looked for in it: "on the right in the image the cable tie instead of the screw".
- **No image without text.** Every image follows a paragraph or bullet that introduces it. No image strips, no heading with only one image below it.
- **At most two image rows in a row,** then text again. More images on the same point are placed side by side or reduced.

## 2. Selecting: do not duplicate

Before an image is inserted, check whether an image with the same statement already exists.

| Situation | Rule |
|---|---|
| Rendering and photo show the same thing | side by side only if the comparison says something (deviation CAD ↔ product, as-built state). Otherwise choose one: photo for the as-built state, rendering for geometry and hidden parts |
| several photos of the same spot | the sharpest with the best crop; the rest stays unused in `images/` or is deleted |
| six side views | only sides with their own features (openings, connections, lugs). Mention closed sides in the text only |
| cover image and overview | different images: cover image shows the whole, overview the exploded view or the contents |
| drawing and rendering of the same view | drawing only in the drawing section, in the text the rendering |
| the same image in two places | never. At the second place, refer to the first (`see [[#Mounting <GEN-A>]]`) |

## 3. Placing: order per section

Images follow the reading flow from coarse to fine. For enclosures and housings (`assets/enclosure-skeleton.md`):

| Section | Images in this order |
|---|---|
| Head | Cover image: the whole, obliquely from the front, rendering or best photo |
| Overview | Exploded view or open state, so that the parts are known before the table comes |
| As-built state | no images, the table stands on its own |
| Mounting | Location image → overall mounting (rendering, next to it photo from the product) → close-up of bracket on the part → bracket on the structure → joint |
| Structure | open (contents visible) → sides with features in one row → contents and connections |
| Contents / connections | purchased part alone, photo of the connectors |
| Technical drawings | own section at the end of Structure, see section 5 |

For other assemblies the same logic applies: location → overall image → function → details → drawings.

## 4. Size: as small as possible, as large as necessary

The first number in `" =WxH"` is the display width in pixels. The second follows from the aspect ratio of the image.

| Image type | Width |
|---|---|
| Cover image | 600 |
| Location image in the complete product | 700 (900 only if the target is very small) |
| Overview, exploded view, overall mounting | 500 |
| Standard image, photo | 400 |
| Close-up, detail, connector | 300 |
| two images side by side | 350 each |
| three images side by side (e.g. side views) | 250 each |
| Drawing preview | 400, the PDF as a link next to it |
| Drawing at full size | 900, only in the drawing section and only the first sheet per part |

At most three images in one row.

## 5. Drawings

- Own section `### Technical drawings` at the end of Structure, not scattered over Mounting and Structure.
- Per part **one** preview (first sheet) with one sentence on what the drawing shows, and links to all sheets as PDF:
  `Shell, 3 sheets, scale 1:1: [Sheet 1](drawings/SPK-Shell-A3-GenA-1.pdf) · [Sheet 2](…) · [Sheet 3](…)`
- In Mounting at most one reference to the detail drawing of the bracket, no second image of it.

## 6. Recognising and requesting image demand

After every working step on a page, check where an image is missing. An image is needed when

- the text describes a location, shape, mounting, opening or connection and no image exists for it,
- a statement is "unresolved" and a photo could settle it (e.g. attachment to the structure),
- text and existing image contradict each other and a new photo must prove the as-built state,
- a photo is blurry, obscured or wrongly cropped,
- the reader cannot understand without an image where something sits (location image, location in the module).

**Every demand is requested explicitly,** never silently skipped:

1. On the page under `## To-dos` as its own line:
   `- [ ] Photo: attachment of the enclosure to the structure, from below, for [[#Mounting <GEN-A>]]`
   `- [ ] Rendering: enclosure open with board, for [[#Enclosure structure]]`
2. Name them to the user, collected at the end of the working session, per image: **type** (photo, rendering, location image, drawing), **motif**, **perspective**, **purpose** (which statement it proves, which section).
3. Propose renderings and location images that can be generated from NX yourself (`references/renderings.md`, `references/location-images-nx.md`). Photos of the product are requested from the user.

## 7. Checklist before finishing a page

- [ ] Every image has an introducing sentence directly before it that describes the same thing.
- [ ] No image twice, no two images with the same statement.
- [ ] No side view of a closed side.
- [ ] Sizes per table, at most three images per row, at most two image rows at a stretch.
- [ ] Drawings collected in one section, one preview per part.
- [ ] Alt text says what you see, including anomalies.
- [ ] Image demand entered as to-dos and named to the user.

`check_page.py` warns about duplicate images, image strips without text, images directly under headings, more than three images per row and too wide images outside location images and drawings.
