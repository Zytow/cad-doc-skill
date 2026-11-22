"""Volume (mm³) of all STEP parts in a folder, summed over the solid bodies.

Usage:
    freecadcmd tools/volume.py <folder> <output.json>

Output keys per part: volume_mm3, bodies, size_mm (bounding box extents).
"""
import json
import sys
from pathlib import Path

import Part

src, out = Path(sys.argv[-2]), Path(sys.argv[-1])
res = {}
for step in sorted(src.glob("*.step")):
    s = Part.read(str(step))
    vol = sum(so.Volume for so in s.Solids)
    bb = s.BoundBox
    res[step.stem] = {"volume_mm3": round(vol, 1), "bodies": len(s.Solids),
                      "size_mm": [round(bb.XLength, 1), round(bb.YLength, 1), round(bb.ZLength, 1)]}
    print("VOL", step.stem, res[step.stem])
out.write_text(json.dumps(res, indent=1), encoding="utf-8")
