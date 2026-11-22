"""Principal axes of a part, used to orient it in a rendering (FreeCAD).

Usage:
    freecadcmd tools/axes.py <part.step>

Prints the normal of the largest planar face ("up", pointing away from the
volume) and the direction of the longest straight edge perpendicular to it
("along"). Both go into the render configuration (tools/render/<assembly>.json)
as "align": {"up": [...], "along": [...]}.
"""
import sys
import Part

path = [a for a in sys.argv if a.lower().endswith((".step", ".stp"))][-1]
shape = Part.read(path)
center = shape.BoundBox.Center

faces = [f for f in shape.Faces if f.Surface.__class__.__name__ == "Plane"]
largest = max(faces, key=lambda f: f.Area)
n = largest.normalAt(0, 0)
if (largest.CenterOfMass - center).dot(n) < 0:  # flip the normal to point outwards
    n = -n

edges = [e for e in shape.Edges if e.Curve.__class__.__name__ in ("Line", "LineSegment")]
edges = [e for e in edges if abs((e.Vertexes[-1].Point - e.Vertexes[0].Point).normalize().dot(n)) < 0.05]
longest = max(edges, key=lambda e: e.Length)
l = (longest.Vertexes[-1].Point - longest.Vertexes[0].Point).normalize()

r = lambda v: [round(x, 4) for x in (v.x, v.y, v.z)]
print("AXES", path.split("/")[-1], "up", r(n), "along", r(l), "area", round(largest.Area))
