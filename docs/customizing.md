# Customizing

- **Accent colour and logo.** `accent` in drawing configurations and the `sheet` block, `logo` and `organisation` in drawing configurations, the accent constant at the top of `doc_style.py` and `md2pdf.py`.
- **Materials and colours of renders.** The `materials` mapping in the render configuration; see `scripts/tools/example-assembly.json`.
- **Outline.** Edit or replace the skeletons in `assets/`. Chapter names the checker expects are listed at the top of `scripts/check_page.py` (`CHAPTERS`, `PAIR`).
- **Language.** The skill is English. The checker's phrases and chapter names are constants and can be replaced to check pages in another language.
- **Folder names.** Documented in `SKILL.md`; the tools resolve them relative to the project.
- **Different CAD system.** The pipeline starts at STEP. Provide `doc/<assembly>/cad/step/` yourself and skip the NX mapping.
- **Other browsers.** `callouts.py`, `export_drawing.py` and `md2pdf.py` look for Edge or Chromium at fixed paths; adjust the constants.
