#!/usr/bin/env python3
"""Checks that the repository is consistent: scripts compile, every path the skill names exists,
the example page passes the checker, and the unit tests run."""
import py_compile
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "skills" / "cad-doc"
failures = []


def fail(msg):
    failures.append(msg)
    print("FAIL", msg)


pyc = str(Path(tempfile.gettempdir()) / "cad-doc-selftest.pyc")
for f in ROOT.rglob("*.py"):
    if "build" in f.parts or ".git" in f.parts:
        continue
    try:
        py_compile.compile(str(f), doraise=True, cfile=pyc)
    except py_compile.PyCompileError as e:
        fail(f"compile {f}: {e}")

pat = re.compile(r"`((?:references|assets|scripts)/[A-Za-z0-9_./-]+\.(?:md|py|json))`")
for md in SKILL.rglob("*.md"):
    for m in pat.finditer(md.read_text(encoding="utf-8")):
        if not (SKILL / m.group(1)).exists():
            fail(f"{md.relative_to(ROOT)} names missing file {m.group(1)}")

r = subprocess.run([sys.executable, "-I", "-X", "utf8", str(SKILL / "scripts" / "check_page.py"),
                    str(ROOT / "examples" / "speaker" / "Speaker.md"), "--legacy"], capture_output=True, text=True)
print(r.stdout.strip().splitlines()[-1] if r.stdout.strip() else r.stderr)
if "0 errors, 0 warnings" not in r.stdout:
    fail("example page does not pass the checker")

r = subprocess.run([sys.executable, "-I", "-X", "utf8", "-m", "unittest", "discover", "-s", str(ROOT / "tests")],
                   capture_output=True, text=True, cwd=ROOT)
print(r.stderr.strip().splitlines()[-1])
if r.returncode != 0:
    fail("unit tests")

print("selftest:", "FAILED" if failures else "OK")
sys.exit(1 if failures else 0)
