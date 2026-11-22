# NX connector

The skill uses [skyf0l/siemens-nx-mcp](https://github.com/skyf0l/siemens-nx-mcp) (MIT) when it is configured. It is a separate project with its own installation; follow its README. This page only covers how the skill uses it.

## Configuration

`.mcp.json.example` in this repository shows the entry. Adjust the path to your checkout; `python install.py --mcp <project>` writes it for you. NX must be running with the connector's journal loaded.

## Tools the skill uses

| Task | Tools |
|---|---|
| Find assembly and parts | `nx_list_parts`, `nx_list_components`, `nx_list_objects` |
| Open a part read-only | `nx_open_part` |
| Measure | `nx_get_model_summary`, `nx_measure_distance` |
| Export | the export tools found via `nx_find_tools` |
| Images in NX | `nx_capture_view` |

Without the connector the skill asks for the part list and the STEP files.

## Things to know

- **Never save the session.** Display changes are reset, exports change nothing.
- **Find parts by reading the references of the top-level part,** not by name search. Housings and boards often carry names that no search term hits.
- **A modal dialog in NX blocks the connector** ("engineer busy"). Close it in NX.
- **Partially loaded assemblies** break whole-assembly hide operations. Work per component.
- **Exporting a whole sub-assembly can include hidden helper bodies** and omit housings. Export per component through the visible bodies.
- **Very large assemblies** (tens of GB in memory) make NX and Blender compete for RAM. Work in a session that holds only what you need.
- **Parts with hundreds of bodies** (populated boards) are better exported from the part file and placed with `place_in_assembly.py` using the installed position of the component.
