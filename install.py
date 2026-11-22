#!/usr/bin/env python3
"""Installs the cad-doc skill and, optionally, a documentation project around it.

    python install.py                      skill into ~/.claude/skills/cad-doc, prerequisites table
    python install.py --project <dir>      additionally the vault template and tools/ in <dir>
    python install.py --mcp <dir>          additionally a .mcp.json entry for siemens-nx-mcp in <dir>
"""
import argparse
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SKILL = ROOT / "skills" / "cad-doc"

PREREQ = [
    ("python", ["python", "python3"], "required: check_page.py and the tools"),
    ("freecadcmd", ["freecadcmd", "FreeCADCmd"], "STEP to STL, volumes, drawings"),
    ("blender", ["blender"], "renderings"),
    ("edge/chromium", ["msedge", "microsoft-edge", "chromium", "google-chrome"], "PDF export and exploded-drawing sheet"),
    ("uv", ["uv"], "runs siemens-nx-mcp (optional, NX only)"),
]
EDGE_PATHS = [r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
              r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"]


def found(names):
    return any(shutil.which(n) for n in names)


def prerequisites():
    print("\nPrerequisites")
    for label, names, why in PREREQ:
        ok = found(names)
        if not ok and label.startswith("edge"):
            ok = any(Path(p).exists() for p in EDGE_PATHS)
        if not ok and label == "freecadcmd":
            ok = bool(list(Path.home().glob("AppData/Local/Programs/FreeCAD*/bin/freecadcmd.exe"))
                      or list(Path("C:/Program Files").glob("FreeCAD*/bin/freecadcmd.exe")))
        if not ok and label == "blender":
            ok = bool(list(Path("C:/Program Files/Blender Foundation").glob("Blender*/blender.exe")))
        print(f"  [{'x' if ok else ' '}] {label:14} {why}")


def copy_tree(src, dst):
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst, ignore=shutil.ignore_patterns("__pycache__"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", type=Path)
    ap.add_argument("--mcp", type=Path)
    ap.add_argument("--skills-dir", type=Path, default=Path.home() / ".claude" / "skills")
    a = ap.parse_args()

    target = a.skills_dir / "cad-doc"
    copy_tree(SKILL, target)
    print(f"Skill installed: {target}")

    if a.project:
        a.project.mkdir(parents=True, exist_ok=True)
        for item in (ROOT / "templates" / "vault").iterdir():
            dst = a.project / item.name
            if item.is_dir():
                shutil.copytree(item, dst, dirs_exist_ok=True)
            elif not dst.exists():
                shutil.copy2(item, dst)
        copy_tree(SKILL / "scripts" / "tools", a.project / "tools")
        snippet = (ROOT / "CLAUDE.md.snippet").read_text(encoding="utf-8")
        claude = a.project / "CLAUDE.md"
        if not claude.exists() or "cad-doc" not in claude.read_text(encoding="utf-8"):
            with open(claude, "a", encoding="utf-8") as f:
                f.write(("\n" if claude.exists() else "") + snippet)
        print(f"Project prepared: {a.project}")

    if a.mcp:
        a.mcp.mkdir(parents=True, exist_ok=True)
        f = a.mcp / ".mcp.json"
        data = json.loads(f.read_text(encoding="utf-8")) if f.exists() else {"mcpServers": {}}
        example = json.loads((ROOT / ".mcp.json.example").read_text(encoding="utf-8"))
        data.setdefault("mcpServers", {}).setdefault("nx", example["mcpServers"]["nx"])
        f.write_text(json.dumps(data, indent=2), encoding="utf-8")
        print(f"MCP entry written: {f} (edit the path to your siemens-nx-mcp checkout)")

    prerequisites()
    print("\nDone. Start Claude Code in your project and say which assembly you are documenting.")


if __name__ == "__main__":
    sys.exit(main())
