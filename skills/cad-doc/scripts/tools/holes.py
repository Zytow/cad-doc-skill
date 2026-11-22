"""Lists holes (cylindrical inner faces) of a STEP part: diameter, axis, center, length.

Usage:
    freecadcmd tools/holes.py <file.step> [max_diameter_mm]
"""
import sys
from collections import defaultdict

import Part

path = sys.argv[-2] if len(sys.argv) > 2 and sys.argv[-1].replace(".", "").isdigit() else sys.argv[-1]
dmax = float(sys.argv[-1]) if sys.argv[-1].replace(".", "").isdigit() else 12.0
shape = Part.read(path)
rows = []
for f in shape.Faces:
    s = f.Surface
    if not isinstance(s, Part.Cylinder):
        continue
    d = 2 * s.Radius
    if d > dmax:
        continue
    # inner face (hole): the normal points towards the axis
    u0, u1, v0, v1 = f.ParameterRange
    pt = f.valueAt((u0 + u1) / 2, (v0 + v1) / 2)
    n = f.normalAt((u0 + u1) / 2, (v0 + v1) / 2)
    ax = s.Axis
    to_axis = s.Center + ax * ((pt - s.Center).dot(ax)) - pt
    if to_axis.Length > 1e-9 and n.dot(to_axis) <= 0:
        continue
    c = f.BoundBox.Center
    rows.append((round(d, 2), tuple(round(abs(a), 2) for a in (ax.x, ax.y, ax.z)), tuple(round(v, 1) for v in (c.x, c.y, c.z)),
                 round(max(f.BoundBox.XLength, f.BoundBox.YLength, f.BoundBox.ZLength), 1)))

groups = defaultdict(list)
for d, ax, c, l in rows:
    groups[(d, ax)].append((c, l))
for (d, ax), items in sorted(groups.items()):
    print(f"D {d} mm  axis {ax}  count {len(items)}")
    for c, l in sorted(set(items)):
        print(f"    center {c}  extent {l}")
