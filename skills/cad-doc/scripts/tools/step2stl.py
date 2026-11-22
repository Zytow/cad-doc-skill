"""Converts all STEP files of a folder into fine STL meshes (FreeCAD).

Usage:
    freecadcmd tools/step2stl.py <source-folder> <target-folder>

The whole shape is meshed (including surface bodies without volume).
"""
import sys
from pathlib import Path

import Mesh
import MeshPart
import Part

src, dst = Path(sys.argv[-2]), Path(sys.argv[-1])
dst.mkdir(parents=True, exist_ok=True)
for step in sorted(src.glob("*.step")):
    shape = Part.read(str(step))
    mesh = Mesh.Mesh()
    parts = shape.Solids if shape.Solids else [shape]
    # additionally mesh surface bodies that have no solid
    shells = [s for s in shape.Shells if not any(s.isSame(x) for so in shape.Solids for x in so.Shells)]
    for p in list(parts) + shells:
        mesh.addMesh(MeshPart.meshFromShape(Shape=p, LinearDeflection=0.015, AngularDeflection=0.1, Relative=False))
    out = dst / (step.stem + ".stl")
    mesh.write(str(out))
    bb = shape.BoundBox
    print("OK", step.name, "solids", len(shape.Solids), "shells", len(shells), "facets", mesh.CountFacets,
          "bbox", round(bb.XLength, 1), round(bb.YLength, 1), round(bb.ZLength, 1))
