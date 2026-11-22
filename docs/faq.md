# FAQ

**Do I need NX?** No. The skill works from STEP files. The NX connector only automates the mapping and the export.

**Do I need Claude Code?** The skill format is Claude Code's. The tools and the checker are plain Python and Blender/FreeCAD scripts and run without it.

**Which Blender and FreeCAD versions?** Developed against Blender 5.x and FreeCAD 1.1 on Windows. Blender 4.x should work. Linux and macOS paths for browsers are listed in the scripts but less tested.

**Why is my render slow or out of memory?** Set `GPU=CUDA` or `GPU=OPTIX` and `DENOISE=0` for many shots in one run (the denoiser can exhaust GPU memory), use `QUICK=1` for previews. Dense meshes such as populated boards are decimated for the line pass.

**The checker warns about a meta phrase.** Rewrite in first person or write `TBD`; see `references/writing-style.md`.

**Can I use it for non-mechanical products?** The outline fits any assembly with parts, decisions and a predecessor. The renders and drawings assume solid CAD.

**Is the example speaker CAD available?** No, only renders and text.
