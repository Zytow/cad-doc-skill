# Contributing

Issues and pull requests are welcome.

- Run `python scripts/selftest.py` before you push. It compiles every script, checks that every path named in the skill exists, runs the checker on the example page and the unit tests.
- Keep the skill generic: no product, team or company data in `skills/`, `templates/` or `examples/`.
- A new rule in `check_page.py` comes with a test in `tests/test_check_page.py`.
- A new tool is added to `skills/cad-doc/scripts/tools/README.md` and, if it changes the workflow, to `SKILL.md`.
- Images in the repository are renders only, no CAD files, and carry no metadata with personal paths.
