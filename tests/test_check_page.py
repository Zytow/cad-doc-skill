"""Tests for check_page.py: every check fires on a bad page and stays silent on a good page.

Run with: python -m unittest discover -s tests -v
"""
from __future__ import annotations

import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
CANDIDATES = [
    HERE.parent / "build" / "out" / "scripts" / "check_page.py",
    HERE.parent / "skills" / "cad-doc" / "scripts" / "check_page.py",
]
SCRIPT = next((p for p in CANDIDATES if p.exists()), CANDIDATES[0])
_spec = importlib.util.spec_from_file_location("check_page", SCRIPT)
check_page = importlib.util.module_from_spec(_spec)
sys.modules["check_page"] = check_page
_spec.loader.exec_module(check_page)

PHOTO = "images/bracket-gen-a-product.png"

MATRIX = """| Criterion | Weighting | Variant A | Variant B |
|-----------|-----------|-----------|-----------|
| Mass | 40 % | 4 | 2 |
| Cost | 20 % | 3 | 5 |
| Risk | 40 % | 5 | 3 |
| Availability | k.o. | yes | yes |
| Total | 100 % | 4.2 | 3.0 |
"""

FMEA = """| Failure mode | Effect | Cause | S | O | D | RPN | Measure | S new | O new | D new | RPN new |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Screw loosens | housing shifts | vibration | 8 | 6 | 9 | 432 | thread locker | 8 | 3 | 2 | 48 |
"""


def good(extra: str = "", status: str = "decided", matrix: str = MATRIX, fmea: str = FMEA) -> str:
    """A page that passes with 0 errors and 0 warnings."""
    status_line = f"**Status:** {status}\n\n" if status else ""
    return f"""# Widget Bracket

The bracket holds the sensor housing on the frame.

![Bracket on the bench, seen from the front]({PHOTO} " =600x400")

# Overview

* The bracket carries the sensor housing and takes the vibration load.
{extra}
### Relevant links

* Sensor datasheet: [sensor](datasheets/sensor.pdf)

# Design

## Design decision #1: Plate thickness

{status_line}### Variants

* Variant A uses 8 mm plate, variant B uses 10 mm plate.

### Evaluation

{matrix}
### Decision

* Variant A, because it is lighter and still stiff enough.

### Risks

{fmea}
### History

| Date | Change | Reason |
|------|--------|--------|
| 2026-01-05 | Decision created | Design start |

# History

## Conclusion

* The bracket worked as planned.
"""


TEMPLATE_GOOD = f"""# Widget Bracket

The bracket holds the sensor housing on the frame.

![Bracket on the bench, seen from the front]({PHOTO} " =600x400")

# Overview

* The bracket carries the sensor housing.

### Relevant links

* Sensor datasheet: [sensor](datasheets/sensor.pdf)

# Concept

## Requirements

### Previous generations

* The old bracket had to hold 20 g.

### This generation

* The new bracket has to hold 40 g.

## Concept decision

### Previous generations

* A printed bracket was used.

### This generation

* The printed bracket stays.

# Design

## Design decision #1: Plate thickness

**Status:** open

### Previous generations

* The plate was 6 mm.

### This generation

* TBD

### History

| Date | Change | Reason |
|------|--------|--------|
| 2026-01-05 | Decision created | Design start |

# Manufacturing

### Previous generations

* Printed in two hours.

### This generation

Printing the bracket in the new orientation worked.

![Printed bracket on the build plate](images/print.png " =400x300")

# Validation

### Previous generations

* No test was made.

### This generation

* TBD

# History

## Generation A

Owner: Alex Example

### Conclusion

* The bracket worked.

### Potential for generation B

* TBD
"""


class CheckPageTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name).resolve()
        self.dir = self.root / "doc" / "widget"
        self.page = self.dir / "widget.md"
        self.files(PHOTO, "datasheets/sensor.pdf")

    def files(self, *names: str):
        for name in names:
            p = self.dir / name
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(b"\x89PNG\r\n")

    def run_check(self, md: str, **kw):
        if kw.get("template"):
            self.files("images/print.png")
        self.dir.mkdir(parents=True, exist_ok=True)
        self.page.write_text(md, encoding="utf-8")
        return check_page.check(self.page, **kw)

    def assertHas(self, items, part):
        self.assertTrue(any(part in i for i in items), f"'{part}' not in {items}")

    def assertNotHas(self, items, part):
        self.assertFalse(any(part in i for i in items), f"'{part}' unexpectedly in {items}")

    # ---- good pages ---------------------------------------------------------------------

    def test_good_page_is_clean(self):
        r = self.run_check(good())
        self.assertEqual(r.errors, [])
        self.assertEqual(r.warnings, [])
        self.assertEqual(r.open, [])

    def test_good_template_page_passes_with_template_flag(self):
        r = self.run_check(TEMPLATE_GOOD, template=True)
        self.assertEqual(r.errors, [])
        self.assertEqual(r.warnings, [])
        self.assertEqual(len(r.open), 3)

    def test_cli_passed_and_exit_code_zero(self):
        self.run_check(good())
        p = subprocess.run([sys.executable, str(SCRIPT), str(self.page)], capture_output=True, text=True)
        self.assertEqual(p.returncode, 0, p.stdout)
        self.assertEqual(p.stdout.strip().splitlines()[-1], "RESULT: PASSED (0 errors, 0 warnings, 0 open)")

    def test_cli_failed_and_exit_code_one(self):
        self.run_check(good(status=""))
        p = subprocess.run([sys.executable, str(SCRIPT), str(self.page), "--legacy", "--template"],
                           capture_output=True, text=True)
        self.assertEqual(p.returncode, 1, p.stdout)
        self.assertIn("ERROR  ", p.stdout)
        self.assertTrue(p.stdout.strip().splitlines()[-1].startswith("RESULT: FAILED ("))

    def test_cli_without_argument_returns_two(self):
        p = subprocess.run([sys.executable, str(SCRIPT)], capture_output=True, text=True)
        self.assertEqual(p.returncode, 2)

    # ---- frontmatter and location image -------------------------------------------------

    def test_invalid_frontmatter_colon(self):
        r = self.run_check("---\nassembly: Ex: value\n---\n" + good())
        self.assertHas(r.errors, "Frontmatter invalid")

    def test_valid_frontmatter_and_title_from_assembly_key(self):
        self.files("images/widget-gen-a-location.png")
        body = good().split("\n", 1)[1]  # drop the H1, the title comes from the frontmatter
        body += "\n![Widget in the product](images/widget-gen-a-location.png \" =700x344\")\n"
        body = body.replace("# History\n\n## Conclusion", "# History\n\n## Conclusion\n\nSee the location below.\n")
        r = self.run_check("---\nassembly: Widget Bracket\narea: demo\n---\n" + body)
        self.assertNotHas(r.errors, "Frontmatter")
        self.assertNotHas(r.errors, "title is missing")

    def test_frontmatter_line_without_key(self):
        r = self.run_check("---\nthis is not yaml\n---\n" + good())
        self.assertHas(r.errors, "not 'key: value'")

    def test_missing_location_image_with_assembly_key(self):
        r = self.run_check("---\nassembly: Widget Bracket\n---\n" + good())
        self.assertHas(r.warnings, "Location image of the complete product is missing")

    def test_missing_location_image_with_mounting_heading(self):
        r = self.run_check(good(extra="\n## Mounting\n\n* Four screws.\n"))
        self.assertHas(r.warnings, "Location image")

    def test_no_location_warning_without_mounting_or_assembly(self):
        r = self.run_check(good())
        self.assertNotHas(r.warnings, "Location image")

    # ---- images -------------------------------------------------------------------------

    def test_duplicate_image(self):
        extra = f'\nThe same view again.\n\n![Bracket again, seen from the front]({PHOTO} " =400x300")\n'
        r = self.run_check(good(extra=extra))
        self.assertHas(r.warnings, "Image embedded twice")

    def test_image_directly_under_heading(self):
        self.files("images/a.png")
        extra = '\n### Detail\n![Close-up of the lug](images/a.png " =300x200")\n'
        r = self.run_check(good(extra=extra))
        self.assertHas(r.warnings, "Image directly under a heading")

    def test_image_under_text_is_fine(self):
        self.files("images/a.png")
        extra = '\n### Detail\n\nThe lug is on the left.\n\n![Close-up of the lug](images/a.png " =300x200")\n'
        r = self.run_check(good(extra=extra))
        self.assertNotHas(r.warnings, "Image directly")

    def test_image_directly_under_table(self):
        self.files("images/a.png")
        extra = '\n| A | B |\n|---|---|\n| 1 | 2 |\n![Close-up of the lug](images/a.png " =300x200")\n'
        r = self.run_check(good(extra=extra))
        self.assertHas(r.warnings, "Image directly under a table")

    def test_three_consecutive_image_lines(self):
        self.files("images/a.png", "images/b.png", "images/c.png")
        extra = ('\nThree views follow.\n\n![View one of the lug](images/a.png " =300x200")\n'
                 '![View two of the lug](images/b.png " =300x200")\n'
                 '![View three of the lug](images/c.png " =300x200")\n')
        r = self.run_check(good(extra=extra))
        self.assertHas(r.warnings, "More than two image lines in a row")

    def test_four_images_in_one_line(self):
        self.files(*[f"images/{c}.png" for c in "abcd"])
        row = " ".join(f'![View {c} of the lug](images/{c}.png " =150x100")' for c in "abcd")
        r = self.run_check(good(extra=f"\nFour views follow.\n\n{row}\n"))
        self.assertHas(r.warnings, "4 images in one line")

    def test_too_wide_image(self):
        self.files("images/a.png")
        extra = '\nThe lug in detail.\n\n![Close-up of the lug](images/a.png " =800x600")\n'
        r = self.run_check(good(extra=extra))
        self.assertHas(r.warnings, "800 px wide")

    def test_wide_location_image_is_allowed(self):
        self.files("images/widget-gen-a-location.png")
        extra = '\nWhere it sits.\n\n![Widget in the product](images/widget-gen-a-location.png " =900x400")\n'
        r = self.run_check(good(extra=extra))
        self.assertNotHas(r.warnings, "px wide")

    def test_drawing_outside_drawings_section(self):
        self.files("drawings/bracket.png")
        extra = '\nThe bracket drawing.\n\n![Drawing of the bracket](drawings/bracket.png " =900x600")\n'
        r = self.run_check(good(extra=extra))
        self.assertHas(r.warnings, "Drawing outside the section Technical drawings")

    def test_drawing_inside_drawings_section(self):
        self.files("drawings/bracket.png")
        extra = ('\n### Technical drawings\n\nThe bracket drawing.\n\n'
                 '![Drawing of the bracket](drawings/bracket.png " =900x600")\n')
        r = self.run_check(good(extra=extra))
        self.assertNotHas(r.warnings, "Drawing outside")
        self.assertNotHas(r.warnings, "px wide")

    def test_weak_alt_text(self):
        self.files("images/a.png")
        extra = '\nThe lug.\n\n![IMG_2041](images/a.png " =300x200")\n'
        r = self.run_check(good(extra=extra))
        self.assertHas(r.errors, "Image needs a description")

    def test_image_without_size(self):
        self.files("images/a.png")
        extra = "\nThe lug.\n\n![Close-up of the lug](images/a.png)\n"
        r = self.run_check(good(extra=extra))
        self.assertHas(r.warnings, "Image without a size")

    def test_missing_image_file(self):
        extra = '\nThe lug.\n\n![Close-up of the lug](images/none.png " =300x200")\n'
        r = self.run_check(good(extra=extra))
        self.assertHas(r.errors, "Image file is missing")

    def test_oversized_image_file(self):
        self.files("images/big.png")
        (self.dir / "images" / "big.png").write_bytes(b"0" * 10_000_001)
        extra = '\nThe lug.\n\n![Close-up of the lug](images/big.png " =300x200")\n'
        r = self.run_check(good(extra=extra))
        self.assertHas(r.warnings, "larger than 10 MB")

    # ---- attachments and links ----------------------------------------------------------

    def test_unused_attachment(self):
        self.files("images/unused.png")
        r = self.run_check(good())
        self.assertHas(r.warnings, "Attachment is not used: images/unused.png")

    def test_png_counts_as_used_when_pdf_is_linked(self):
        self.files("drawings/part.png", "drawings/part.pdf")
        extra = "\nSheet: [Sheet 1](drawings/part.pdf)\n"
        r = self.run_check(good(extra=extra))
        self.assertNotHas(r.warnings, "Attachment is not used")

    def test_broken_link(self):
        r = self.run_check(good(extra="\nSee [the plan](datasheets/missing.pdf).\n"))
        self.assertHas(r.errors, "Link target is missing: datasheets/missing.pdf")

    def test_link_without_target(self):
        r = self.run_check(good(extra="\nSee [the plan]().\n"))
        self.assertHas(r.errors, "Link without a target")

    def test_file_outside_assembly_folder(self):
        (self.root / "doc" / "stray.pdf").write_bytes(b"x")
        r = self.run_check(good(extra="\nSee [stray](../stray.pdf).\n"))
        self.assertHas(r.warnings, "outside the assembly folder")

    def test_sibling_rules_folder_is_allowed(self):
        (self.root / "doc" / "rules").mkdir()
        (self.root / "doc" / "rules" / "rulebook.pdf").write_bytes(b"x")
        r = self.run_check(good(extra="\nSee [rulebook](../rules/rulebook.pdf).\n"))
        self.assertNotHas(r.warnings, "outside the assembly folder")

    # ---- numeric checks -----------------------------------------------------------------

    def test_matrix_wrong_weight_sum(self):
        bad = MATRIX.replace("| Cost | 20 % |", "| Cost | 30 % |")
        r = self.run_check(good(matrix=bad))
        self.assertHas(r.errors, "Weights add up to 110 % instead of 100 %")

    def test_matrix_wrong_total(self):
        bad = MATRIX.replace("| 4.2 | 3.0 |", "| 4.5 | 3.0 |")
        r = self.run_check(good(matrix=bad))
        self.assertHas(r.errors, "total is 4.5, computed 4.20")

    def test_matrix_points_out_of_range(self):
        bad = MATRIX.replace("| Mass | 40 % | 4 | 2 |", "| Mass | 40 % | 7 | 2 |")
        r = self.run_check(good(matrix=bad))
        self.assertHas(r.errors, "points must be between 1 and 5")

    def test_matrix_without_total_row(self):
        bad = MATRIX.replace("| Total | 100 % | 4.2 | 3.0 |\n", "")
        r = self.run_check(good(matrix=bad))
        self.assertHas(r.errors, "without a row 'Total'")

    def test_fmea_wrong_rpn(self):
        bad = FMEA.replace("| 432 |", "| 400 |")
        r = self.run_check(good(fmea=bad))
        self.assertHas(r.errors, "RPN is 400, computed 432")

    def test_fmea_wrong_rpn_after_measure(self):
        bad = FMEA.replace("| 48 |", "| 40 |")
        r = self.run_check(good(fmea=bad))
        self.assertHas(r.errors, "RPN new is 40, computed 48")

    def test_fmea_rating_out_of_range(self):
        bad = FMEA.replace("| 8 | 6 | 9 | 432 |", "| 11 | 6 | 9 | 594 |")
        r = self.run_check(good(fmea=bad))
        self.assertHas(r.errors, "must be between 1 and 10")

    def test_utilisation_wrong(self):
        table = ("\n| Variant | Thickness [mm] | Max stress [MPa] | Limit [MPa] | Utilisation [%] | Result |\n"
                 "|---|---|---|---|---|---|\n| V1 | 8 | 122 | 100 | 90 | does not hold |\n")
        r = self.run_check(good(extra=table))
        self.assertHas(r.errors, "utilisation is 90 %, computed 122 %")

    def test_utilisation_correct(self):
        table = ("\n| Variant | Thickness [mm] | Max stress [MPa] | Limit [MPa] | Utilisation [%] | Result |\n"
                 "|---|---|---|---|---|---|\n| V1 | 8 | 122 | 100 | 122 | does not hold |\n")
        r = self.run_check(good(extra=table))
        self.assertEqual(r.errors, [])

    def test_table_column_count(self):
        r = self.run_check(good(extra="\n| A | B |\n|---|---|\n| 1 | 2 | 3 |\n"))
        self.assertHas(r.errors, "Table row has 3 instead of 2 columns")

    # ---- decisions ----------------------------------------------------------------------

    def test_missing_status_in_design_decision(self):
        r = self.run_check(good(status=""))
        self.assertHas(r.errors, "'**Status:**")
        self.assertHas(r.errors, "is missing")

    def test_status_present_is_silent(self):
        r = self.run_check(good(status="in progress"))
        self.assertNotHas(r.errors, "Status")

    def test_legacy_skips_status_check(self):
        r = self.run_check(good(status=""), legacy=True)
        self.assertNotHas(r.errors, "Status")

    def test_decided_without_decision_text(self):
        md = good().replace("* Variant A, because it is lighter and still stiff enough.", "* TBD")
        r = self.run_check(md)
        self.assertHas(r.errors, "section 'Decision' is empty")

    def test_validated_without_verification(self):
        r = self.run_check(good(status="validated"))
        self.assertHas(r.errors, "verification is missing")

    def test_history_date_in_future(self):
        r = self.run_check(good().replace("2026-01-05", "2999-01-05"))
        self.assertHas(r.errors, "is in the future")

    def test_history_without_date(self):
        r = self.run_check(good().replace("| 2026-01-05 | Decision created | Design start |", "| TBD | TBD | TBD |"))
        self.assertHas(r.errors, "section 'History' with a date is missing")

    # ---- simulation ---------------------------------------------------------------------

    def test_simulation_card_with_missing_fields(self):
        extra = ("\n#### Simulation: bracket under 40 g\n\n| Item | Entry |\n|---|---|\n"
                 "| Question | Which thickness holds? |\n| Screenshot | TBD |\n")
        r = self.run_check(good(extra=extra))
        self.assertHas(r.errors, "card row 'Tool' is missing")
        self.assertHas(r.errors, "card row 'Assessment' is missing")
        self.assertNotHas(r.errors, "card row 'Question'")

    def test_complete_simulation_card(self):
        rows = "\n".join(f"| {f} | entry |" for f in check_page.SIM_FIELDS)
        self.assertEqual(len(check_page.SIM_FIELDS), 12)
        extra = f"\n#### Simulation: bracket under 40 g\n\n| Item | Entry |\n|---|---|\n{rows}\n| Screenshot | TBD |\n"
        r = self.run_check(good(extra=extra))
        self.assertEqual(r.errors, [])

    # ---- text rules ---------------------------------------------------------------------

    def test_meta_phrase(self):
        for phrase in ("The part is presumably PETG.", "It is probably fine.", "The value is derived from the STEP.",
                       "Not present in CAD.", "Taken from the STEP export.", "According to Alex it is loose."):
            with self.subTest(phrase=phrase):
                r = self.run_check(good(extra=f"\n{phrase}\n"))
                self.assertHas(r.warnings, "Meta phrase")

    def test_evidenced_source_is_not_a_meta_phrase(self):
        r = self.run_check(good(extra="\nAccording to the datasheet the limit is 100 MPa.\n"))
        self.assertNotHas(r.warnings, "Meta phrase")
        r = self.run_check(good(extra="\nAccording to Rulebook 4.2 the cover must close.\n"))
        self.assertNotHas(r.warnings, "Meta phrase")

    def test_unresolved_is_allowed_and_tbd_is_open(self):
        r = self.run_check(good(extra="\nThe fastening to the frame is unresolved.\n\n* Torque: TBD\n"))
        self.assertNotHas(r.warnings, "Meta phrase")
        self.assertEqual(len(r.open), 1)
        self.assertHas(r.open, "Torque: TBD")

    def test_unclosed_info_box(self):
        r = self.run_check(good(extra="\n:::info\nKeep the screws short.\n"))
        self.assertHas(r.errors, "Info box ':::' is not closed")

    def test_closed_info_box(self):
        r = self.run_check(good(extra="\n:::info\nKeep the screws short.\n:::\n"))
        self.assertNotHas(r.errors, "Info box")

    def test_obsidian_embed(self):
        r = self.run_check(good(extra="\n![[photo.jpg|400]]\n"))
        self.assertHas(r.errors, "Obsidian image")

    def test_anchor_link_without_heading(self):
        r = self.run_check(good(extra="\nSee [[#Nonexistent heading]].\n"))
        self.assertHas(r.errors, "Reference without a matching heading")

    def test_anchor_link_with_heading(self):
        r = self.run_check(good(extra="\nSee [[#Design decision #1: Plate thickness]] and [[#Variants]].\n"))
        self.assertNotHas(r.errors, "Reference without")

    def test_unreplaced_placeholder(self):
        r = self.run_check(good(extra="\nCreated on {{DATE}}.\n"))
        self.assertHas(r.errors, "Placeholder not replaced")

    def test_template_text_left_over(self):
        r = self.run_check(good(extra="\n*insert a photo of the assembly here*\n"))
        self.assertHas(r.errors, "Placeholder from the template")

    def test_heading_too_deep(self):
        r = self.run_check(good(extra="\n####### Too deep\n"))
        self.assertHas(r.errors, "deeper than ######")

    def test_long_bullet_and_long_paragraph(self):
        r = self.run_check(good(extra="\n* " + "word " * 70 + "\n\n" + "word " * 120 + "\n"))
        self.assertHas(r.warnings, "Bullet is very long")
        self.assertHas(r.warnings, "Paragraph is very long")

    def test_deeply_nested_bullet(self):
        r = self.run_check(good(extra="\n* a\n  * b\n    * c\n      * d\n        * e\n"))
        self.assertHas(r.warnings, "deeper than four levels")

    def test_empty_heading(self):
        r = self.run_check(good(extra="\n### Empty section\n\n### Next section\n\n* text\n"))
        self.assertHas(r.errors, "'Empty section' is empty")

    def test_missing_title(self):
        r = self.run_check(good().split("\n", 1)[1])
        self.assertHas(r.errors, "title is missing")

    # ---- template mode ------------------------------------------------------------------

    def test_template_chapters_mismatch(self):
        md = TEMPLATE_GOOD.replace("# Validation", "# Testing")
        r = self.run_check(md, template=True)
        self.assertHas(r.errors, "Chapters differ from the template")

    def test_free_page_fails_template_mode_but_not_free_mode(self):
        md = good()
        self.assertNotHas(self.run_check(md).errors, "Chapters differ")
        self.assertHas(self.run_check(md, template=True).errors, "Chapters differ")

    def test_template_empty_pair_subsection(self):
        md = TEMPLATE_GOOD.replace("* The old bracket had to hold 20 g.", "")
        r = self.run_check(md, template=True)
        self.assertHas(r.errors, "'Requirements' > 'Previous generations' is empty")

    def test_template_history_without_owner(self):
        md = TEMPLATE_GOOD.replace("Owner: Alex Example", "Owner:")
        r = self.run_check(md, template=True)
        self.assertHas(r.errors, "'Owner' without a name")

    def test_template_history_without_potential(self):
        md = TEMPLATE_GOOD.replace("### Potential for generation B\n\n* TBD\n", "")
        r = self.run_check(md, template=True)
        self.assertHas(r.errors, "'Potential for <next generation>' is missing")


if __name__ == "__main__":
    unittest.main()
