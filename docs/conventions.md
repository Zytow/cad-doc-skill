# Conventions

- **Voice.** First person, no meta remarks. Uncertain values are `TBD` or "unresolved", never "presumably". Details in `references/writing-style.md`.
- **Source for every number.** A value appears once with its source; elsewhere the page links to it.
- **Decisions.** `Design decision #n: Topic` with status (`open`, `in progress`, `decided`, `validated`, `rejected`) and a history table. Rejected variants stay.
- **Images.** One image directly under the text it supports, no duplicates, display width 250 to 700 by role. Names: `<prefix>-<gen>-{product,explosion,open,mounting,location}.png`, photos `<prefix>-<gen>-photo-<what>.jpg`.
- **Render style.** Printed parts light grey on a grey studio background, one accent colour (default `#D62F2F`), configurable.
- **Orientation.** Location images show the whole product from the side with the direction of travel to the left; parts in modules additionally show their place in the module. Vertical parts are rendered upright as installed.
- **Files.** Everything of an assembly lives in its folder so it exports as a whole. Intermediate files (SVG, JSON, STL) stay outside `doc/`.
- **Dates.** `YYYY-MM-DD`.
