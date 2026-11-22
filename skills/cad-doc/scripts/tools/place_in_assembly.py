"""Places a part exported in part coordinates into its assembly pose (FreeCAD).

Usage:
    freecadcmd tools/place_in_assembly.py <part.step> <target.step> "<rotation>" "<translation>" "<reference-bbox>"

rotation:     3x3 matrix from nx_list_components (include_poses), as JSON
translation:  [x, y, z] from nx_list_components, as JSON
reference:    bounding box of one body of the part in assembly coordinates
              [xmin, ymin, zmin, xmax, ymax, zmax] (from nx_list_objects)

NX reports the rotation as a matrix without stating the convention. The script
tries the matrix and its transpose and keeps the one for which a body matches
the reference bounding box.
"""
import json
import sys
import Part
from FreeCAD import Matrix, Vector

args = sys.argv[sys.argv.index("tools/place_in_assembly.py") + 1:] if "tools/place_in_assembly.py" in sys.argv else sys.argv[-5:]
source, target, rot, trans, ref = args[-5:]
R = json.loads(rot)
t = json.loads(trans)
ref = json.loads(ref)

shape = Part.read(source)


def matrix(R, transposed):
    m = Matrix()
    for i in range(3):
        for j in range(3):
            v = R[j][i] if transposed else R[i][j]
            setattr(m, f"A{i + 1}{j + 1}", v)
    m.A14, m.A24, m.A34 = t
    return m


def distance(shape, m):
    best = 1e9
    for s in shape.Solids:
        b = s.copy()
        b.transformShape(m)
        bb = b.BoundBox
        d = sum(abs(a - c) for a, c in zip((bb.XMin, bb.YMin, bb.ZMin, bb.XMax, bb.YMax, bb.ZMax), ref))
        best = min(best, d)
    return best


candidates = [(distance(shape, matrix(R, tr)), tr) for tr in (False, True)]
error, tr = min(candidates)
moved = shape.copy()
moved.transformShape(matrix(R, tr))
moved.exportStep(target)
bb = moved.BoundBox
print("PLACED", "transposed" if tr else "as reported", "deviation", round(error, 3), "mm",
      [round(v, 1) for v in (bb.XMin, bb.YMin, bb.ZMin, bb.XMax, bb.YMax, bb.ZMax)])
