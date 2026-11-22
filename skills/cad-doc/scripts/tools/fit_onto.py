"""Fits a model (e.g. a populated circuit board) exactly onto a placeholder (FreeCAD).

Usage:
    freecadcmd tools/fit_onto.py <model.step> <placeholder.step> <target.step>

Method: the largest planar face is found in both files (the circuit board).
Their outlines are laid onto each other via centroid, normal and principal
in-plane axis. Of the four possible poses (principal axis and normal each
flipped or not) the one with the smallest mean corner-point distance wins.
The output is the model in the pose of the placeholder.
"""
import sys
import math
import FreeCAD
import Part
from FreeCAD import Vector, Matrix

files = [a for a in sys.argv if a.lower().endswith((".step", ".stp"))]
model_path, holder_path, target = files[-3:]


def plate(shape):
    faces = [f for f in shape.Faces if f.Surface.__class__.__name__ == "Plane"]
    return max(faces, key=lambda f: f.Area)


def axes(f):
    """Centroid, normal, principal in-plane axis (from the vertices)."""
    c = f.CenterOfMass
    n = f.normalAt(0, 0)
    pts = [v.Point for v in f.Vertexes]
    best, best_len = None, -1
    for i in range(len(pts)):
        for j in range(i + 1, len(pts)):
            d = pts[j] - pts[i]
            d = d - n * d.dot(n)
            if d.Length > best_len:
                best, best_len = d, d.Length
    return c, n, best.normalize(), pts


def basis(n, a):
    b = n.cross(a)
    return Matrix(a.x, b.x, n.x, 0, a.y, b.y, n.y, 0, a.z, b.z, n.z, 0, 0, 0, 0, 1)


model = Part.read(model_path)
holder = Part.read(holder_path)
cm, nm, am, _ = axes(plate(model))
ch, nh, ah, ph = axes(plate(holder))

best = None
for sn in (1, -1):
    for sa in (1, -1):
        Bm = basis(nm, am)
        Bh = basis(nh * sn, ah * sa)
        R = Bh.multiply(Bm.inverse())
        T = Matrix()
        T.move(ch)
        T = T.multiply(R)
        V = Matrix()
        V.move(-cm)
        T = T.multiply(V)
        f = plate(model).copy()
        f.transformShape(T)
        q = [v.Point for v in f.Vertexes]
        error = sum(min((p - x).Length for x in q) for p in ph) / len(ph)
        if best is None or error < best[0]:
            best = (error, T)

error, T = best
moved = model.copy()
moved.transformShape(T)
moved.exportStep(target)
print("FITTED", round(error, 2), "mm mean corner distance; model plate", round(plate(model).Area), "mm²",
      "placeholder", round(plate(holder).Area), "mm²")
