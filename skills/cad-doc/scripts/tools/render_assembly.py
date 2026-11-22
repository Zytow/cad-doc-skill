"""Photorealistic studio renderings of an assembly made of STL parts (Blender, Cycles).

Usage (in the project folder):
    blender --background --factory-startup --python tools/render_assembly.py -- tools/render/<assembly>.json [shot ...]

Without shot names all shots of the configuration are rendered.
Environment variables: QUICK=1 (preview: 30 % resolution, 24 samples), SAMPLES=<n>,
GPU=OPTIX|CUDA, DENOISE=0, EXPOSURE=<ev>, GHOST_ALPHA=<0..1>, LIGHT=<factor>, WORLD=<strength>.
Output: doc/<folder>/images/<prefix>-<shot>.png

Configuration (JSON):
    folder        assembly folder under doc/, e.g. "speaker"
    prefix        file prefix of the images, e.g. "speaker-a"
    stl_dir       folder with the STL parts (relative to the project)
    parts         {part_name: material_name}
    accent        optional accent colour as hex, default "#D62F2F" (material "accent")
    tubes         optional frame tubes [{p:[x,y,z], d:[x,y,z], r, t:[from,to]}] in mm
    states        {state: {part_name: [dx,dy,dz] mm}} e.g. "open", "explosion" (assembly coordinates)
    align         optional {up: [x,y,z], along: [x,y,z]}: rotate the assembly onto its own axes (tools/axes.py)
    cell_axis     optional axis ("x", "y", "z") of cylindrical cells for parts with material "cell" (default "z")
    shots         list of {name, state, hide[], only[], ghost[], ghost_tubes, tubes, az, el, margin, lens, focus[], focus_mm[6],
                  fstop, ortho, no_background, light_below, materials{part: material},
                  style ("line": technical outline drawing + <shot>.json with part anchors), line_width, crease, anchors{part: [x,y,z] mm}}
"""
import json
import math
import os
import sys
from pathlib import Path

import bmesh
import bpy
from mathutils import Matrix, Vector

S = 0.001  # mm -> m
root = Path(__file__).resolve().parent.parent
args = sys.argv[sys.argv.index("--") + 1:]
cfg = json.loads((root / args[0]).read_text(encoding="utf-8"))
wanted = args[1:]
QUICK = bool(os.environ.get("QUICK"))
SAMPLES = int(os.environ.get("SAMPLES", "24" if QUICK else "192"))
HDRI = Path(bpy.utils.resource_path("LOCAL")) / "datafiles" / "studiolights" / "world" / "studio.exr"

# ---------------------------------------------------------------- materials

def hex_to_linear(h):
    """Hex colour (#RRGGBB) to linear RGB tuple."""
    h = h.lstrip("#")
    out = []
    for i in (0, 2, 4):
        c = int(h[i:i + 2], 16) / 255
        out.append(c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4)
    return tuple(out)


def principled(name, base, rough=0.5, metallic=0.0, spec=0.5, coat=0.0, aniso=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*base, 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metallic
    b.inputs["Specular IOR Level"].default_value = spec
    b.inputs["Coat Weight"].default_value = coat
    if aniso:
        b.inputs["Anisotropic"].default_value = aniso
    return m, b


def add_layer_lines(m, b, layer_mm=0.2, strength=0.25):
    """Fine layer lines of an FDM print as a bump along the print direction (z)."""
    nt = m.node_tree
    coord = nt.nodes.new("ShaderNodeTexCoord")
    wave = nt.nodes.new("ShaderNodeTexWave")
    wave.wave_type = "BANDS"
    wave.bands_direction = "Z"
    wave.inputs["Scale"].default_value = 1.0 / (layer_mm * S)  # bands per meter in object space
    wave.inputs["Distortion"].default_value = 0.0
    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = strength
    bump.inputs["Distance"].default_value = 0.00004
    nt.links.new(coord.outputs["Object"], wave.inputs["Vector"])
    nt.links.new(wave.outputs["Fac"], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], b.inputs["Normal"])


def make_materials():
    mats = {}
    m, b = principled("print", (0.33, 0.34, 0.36), rough=0.62, spec=0.35)
    add_layer_lines(m, b)
    mats["print"] = m
    m, b = principled("print_lid", (0.40, 0.41, 0.43), rough=0.58, spec=0.35)
    add_layer_lines(m, b)
    mats["print_lid"] = m
    mats["rubber"] = principled("rubber", (0.018, 0.018, 0.02), rough=0.75, spec=0.3)[0]
    mats["pa_black"] = principled("pa_black", (0.03, 0.03, 0.032), rough=0.45, spec=0.45)[0]
    mats["nuc_plastic"] = principled("nuc_plastic", (0.035, 0.037, 0.042), rough=0.32, spec=0.5, coat=0.15)[0]
    mats["steel"] = principled("steel", (0.62, 0.62, 0.64), rough=0.28, metallic=1.0)[0]
    mats["film"] = principled("film", (0.012, 0.012, 0.014), rough=0.2, spec=0.6)[0]
    mats["alu"] = principled("alu", (0.78, 0.79, 0.81), rough=0.32, metallic=1.0, aniso=0.5)[0]
    mats["pcb_green"] = principled("pcb_green", (0.03, 0.22, 0.09), rough=0.28, spec=0.6, coat=0.35)[0]
    mats["carbon"] = principled("carbon", (0.045, 0.047, 0.052), rough=0.22, spec=0.55, coat=0.6, aniso=0.3)[0]  # visible carbon
    mats["frame"] = principled("frame", (0.06, 0.065, 0.07), rough=0.38, metallic=0.35)[0]
    mats["backdrop"] = principled("backdrop", (0.13, 0.135, 0.145), rough=0.85, spec=0.25)[0]
    m, b = principled("ghost", (0.62, 0.64, 0.67), rough=0.4, spec=0.4)
    b.inputs["Alpha"].default_value = float(os.environ.get("GHOST_ALPHA", "0.14"))
    mats["ghost"] = m
    # accent colour: configurable, hex converted to linear RGB
    mats["accent"] = principled("accent", hex_to_linear(cfg.get("accent", "#D62F2F")), rough=0.32, metallic=0.0, spec=0.5, coat=0.3)[0]
    # battery pack: realistic materials after a photo
    mats["peek"] = principled("peek", (0.66, 0.60, 0.47), rough=0.42, spec=0.4, coat=0.05)[0]  # PEEK natural, cream
    mats["nickel"] = principled("nickel", (0.60, 0.58, 0.54), rough=0.22, metallic=1.0)[0]  # nickel-plated sheet
    mats["gold"] = principled("gold", (0.72, 0.42, 0.12), rough=0.3, metallic=1.0)[0]  # ENIG pads of the board
    mats["nylon"] = principled("nylon", (0.80, 0.78, 0.72), rough=0.5, spec=0.35)[0]  # polyamide natural/white
    mats["cell"] = principled("cell", (0.78, 0.76, 0.70), rough=0.35, spec=0.5, coat=0.2)[0]  # cell jacket (shrink sleeve)
    mats["cell_cap"] = principled("cell_cap", (0.66, 0.66, 0.67), rough=0.25, metallic=1.0)[0]  # cell terminals, nickel-plated
    return mats


def split_cell_caps(o, mats, axis):
    """The end faces of a cell (normal along the cell axis) get the terminal material."""
    o.data.materials.append(mats["cell_cap"])
    i = "xyz".index(axis)
    for p in o.data.polygons:
        if abs(p.normal[i]) > 0.95:
            p.material_index = 1


# ---------------------------------------------------------------- scene

def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def import_parts(mats, only=None):
    """only: part names to load (saves memory for single-part shots)."""
    objs = {}
    stl_dir = root / cfg["stl_dir"]
    for name, matname in cfg["parts"].items():
        if only and name not in only:
            continue
        bpy.ops.wm.stl_import(filepath=str(stl_dir / f"{name}.stl"))
        o = bpy.context.selected_objects[0]
        o.name = name
        # merge duplicate points of the STL so that smoothing by angle works across edges
        bm = bmesh.new()
        bm.from_mesh(o.data)
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-4)
        bm.to_mesh(o.data)
        bm.free()
        o.data.transform(Matrix.Scale(S, 4))
        bpy.context.view_layer.objects.active = o
        o.select_set(True)
        bpy.ops.object.shade_auto_smooth(angle=math.radians(35))
        o.data.materials.append(mats[matname])
        if matname == "cell":
            split_cell_caps(o, mats, cfg.get("cell_axis", "z"))
        objs[name] = o
    return objs


def make_tubes(mats):
    tubes = []
    for i, t in enumerate(cfg.get("tubes", [])):
        p, d = Vector(t["p"]), Vector(t["d"]).normalized()
        a, b = p + d * t["t"][0], p + d * t["t"][1]
        mid, length = (a + b) / 2 * S, (b - a).length * S
        bpy.ops.mesh.primitive_cylinder_add(vertices=96, radius=t["r"] * S, depth=length, location=mid)
        o = bpy.context.object
        o.name = f"tube{i}"
        o.rotation_euler = d.to_track_quat("Z", "Y").to_euler()
        bpy.ops.object.shade_smooth()
        o.data.materials.append(mats["frame"])
        tubes.append(o)
    return tubes


def bounds(objs):
    pts = [o.matrix_world @ Vector(c) for o in objs for c in o.bound_box]
    lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    return lo, hi


def backdrop(lo, hi, size, mats):
    """Cove: floor with a soft transition into a back wall."""
    ctr = (lo + hi) / 2
    w, depth, height, radius = size * 14, size * 7, size * 6, size * 2.0
    verts, faces = [], []
    prof = []
    n = 24
    for i in range(n + 1):  # floor towards the front
        prof.append((-depth + i * (depth / n), 0.0))
    for i in range(1, n + 1):  # quarter circle
        a = i / n * (math.pi / 2)
        prof.append((radius * math.sin(a), radius * (1 - math.cos(a))))
    for i in range(1, n + 1):  # wall
        prof.append((radius, radius + i * (height / n)))
    for j, x in enumerate((-w / 2, w / 2)):
        for (py, pz) in prof:
            verts.append((x, py, pz))
    k = len(prof)
    for i in range(k - 1):
        faces.append((i, i + 1, k + i + 1, k + i))
    me = bpy.data.meshes.new("cove")
    me.from_pydata(verts, [], faces)
    o = bpy.data.objects.new("cove", me)
    bpy.context.collection.objects.link(o)
    for p in me.polygons:
        p.use_smooth = True
    o.location = (ctr.x, hi.y + size * 1.2, lo.z - 0.0005)
    o.data.materials.append(mats["backdrop"])
    return o


def lights(ctr, size):
    def area(name, loc, energy, sz, shape="RECTANGLE", sy=None):
        ld = bpy.data.lights.new(name, "AREA")
        ld.shape = shape
        ld.size = sz
        if sy:
            ld.size_y = sy
        ld.energy = energy
        o = bpy.data.objects.new(name, ld)
        bpy.context.collection.objects.link(o)
        o.location = ctr + Vector(loc) * size
        o.rotation_euler = (ctr - o.location).to_track_quat("-Z", "Y").to_euler()
        return o

    def e(base, loc):  # scale the energy with the squared distance
        return base * (Vector(loc).length * size) ** 2

    k = float(os.environ.get("LIGHT", "1"))
    area("key", (-2.2, -2.0, 2.6), e(40 * k, (-2.2, -2.0, 2.6)), size * 2.4, sy=size * 1.6)
    area("fill", (2.6, -1.4, 1.2), e(14 * k, (2.6, -1.4, 1.2)), size * 3.0, sy=size * 2.0)
    area("rim", (0.6, 2.6, 2.2), e(25 * k, (0.6, 2.6, 2.2)), size * 1.2, sy=size * 3.0)
    area("top", (0.0, 0.0, 3.6), e(12 * k, (0.0, 0.0, 3.6)), size * 3.0)


def world(flat_bg=None):
    """HDRI for light and reflections; with flat_bg the camera sees a uniform surface."""
    w = bpy.data.worlds.new("w")
    w.use_nodes = True
    nt = w.node_tree
    bg = nt.nodes["Background"]
    if HDRI.exists():
        env = nt.nodes.new("ShaderNodeTexEnvironment")
        env.image = bpy.data.images.load(str(HDRI))
        nt.links.new(env.outputs["Color"], bg.inputs["Color"])
    bg.inputs["Strength"].default_value = float(os.environ.get("WORLD", "0.25"))
    if flat_bg is not None:
        out = nt.nodes["World Output"]
        flat = nt.nodes.new("ShaderNodeBackground")
        flat.inputs["Color"].default_value = (*flat_bg, 1)
        flat.inputs["Strength"].default_value = 1.0
        lp = nt.nodes.new("ShaderNodeLightPath")
        mix = nt.nodes.new("ShaderNodeMixShader")
        nt.links.new(lp.outputs["Is Camera Ray"], mix.inputs["Fac"])
        nt.links.new(bg.outputs["Background"], mix.inputs[1])
        nt.links.new(flat.outputs["Background"], mix.inputs[2])
        nt.links.new(mix.outputs["Shader"], out.inputs["Surface"])
    bpy.context.scene.world = w


def camera(target_objs, az, el, margin=1.15, lens=85, fstop=11, ortho=False):
    lo, hi = bounds(target_objs)
    ctr = (lo + hi) / 2
    radius = (hi - lo).length / 2
    cd = bpy.data.cameras.new("cam")
    cd.lens = lens
    cd.sensor_width = 36
    sc = bpy.context.scene
    aspect = sc.render.resolution_x / sc.render.resolution_y
    fov_v = 2 * math.atan((36 / aspect) / 2 / lens)
    dist = radius * margin / math.sin(fov_v / 2)
    cam = bpy.data.objects.new("cam", cd)
    bpy.context.collection.objects.link(cam)
    a, e = math.radians(az), math.radians(el)
    cam.location = ctr + Vector((math.cos(e) * math.sin(a), -math.cos(e) * math.cos(a), math.sin(e))) * dist
    cam.rotation_euler = (ctr - cam.location).to_track_quat("-Z", "Y").to_euler()
    if ortho:  # straight-on view without perspective
        cd.type = "ORTHO"
        cd.ortho_scale = radius * 2 * margin
        cd.dof.use_dof = False
        cam.location = ctr + (cam.location - ctr).normalized() * radius * 4
        cam.rotation_euler = (ctr - cam.location).to_track_quat("-Z", "Y" if abs(el) < 80 else "X").to_euler()
        sc.camera = cam
        return
    cd.dof.use_dof = True
    cd.dof.focus_distance = (ctr - cam.location).length
    cd.dof.aperture_fstop = fstop
    sc.camera = cam


def render_settings():
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    if os.environ.get("GPU"):  # GPU=OPTIX or GPU=CUDA; without the variable it stays on the CPU
        prefs = bpy.context.preferences.addons["cycles"].preferences
        prefs.compute_device_type = os.environ["GPU"] if os.environ["GPU"] in ("OPTIX", "CUDA") else "OPTIX"
        prefs.get_devices_for_type(prefs.compute_device_type)
        gpus = [d for d in prefs.devices if d.type == prefs.compute_device_type]
        for d in prefs.devices:
            d.use = d in gpus
        if gpus:
            sc.cycles.device = "GPU"
        print("RENDER_DEVICE", sc.cycles.device, prefs.compute_device_type, [d.name for d in gpus])
    sc.cycles.samples = SAMPLES
    sc.cycles.use_adaptive_sampling = True
    sc.cycles.use_denoising = os.environ.get("DENOISE", "1") != "0"  # DENOISE=0 when memory is tight, then use more SAMPLES
    sc.render.resolution_x = 2400
    sc.render.resolution_y = 1600
    sc.render.resolution_percentage = 30 if QUICK else 100
    sc.render.film_transparent = False
    sc.view_settings.view_transform = "AgX"
    sc.view_settings.look = "AgX - Punchy"
    sc.view_settings.exposure = float(os.environ.get("EXPOSURE", "-0.8"))
    sc.render.image_settings.file_format = "PNG"



def align(objs):
    """Rotates the assembly onto its own axes: "up" to +Z, "along" to +X.

    Otherwise the pose in the assembly is kept. Returns the rotation matrix, which
    is also used to rotate the offsets of the states (open, explosion).
    """
    a = cfg.get("align")
    if not a:
        return Matrix.Identity(3)
    z = Vector(a["up"]).normalized()
    x = Vector(a["along"])
    x = (x - z * x.dot(z)).normalized()
    y = z.cross(x)
    R = Matrix((x, y, z))  # rows: world vector -> local axes
    pts = [o.matrix_world @ Vector(c) for o in objs for c in o.bound_box]
    ctr = sum(pts, Vector()) / len(pts)
    T = Matrix.Translation(ctr) @ R.to_4x4() @ Matrix.Translation(-ctr)
    for o in objs:
        o.data.transform(o.matrix_world.inverted() @ T @ o.matrix_world)
    return R


# ---------------------------------------------------------------- shots

def line_style(objs, shot, out):
    """Technical-drawing look: light flat shading, black Freestyle outlines, white background.

    Also writes <out>.json with the screen position of every visible part (bounding-box centre or the
    point given in shot["anchors"] = {part: [x, y, z] mm}). tools/callouts.py turns it into numbered balloons.
    """
    import bpy_extras
    sc = bpy.context.scene
    sc.render.engine = "BLENDER_WORKBENCH"
    sh = sc.display.shading
    sh.light = "STUDIO"
    sh.color_type = "SINGLE"
    sh.single_color = (0.94, 0.94, 0.94)
    sh.show_shadows = False
    sh.show_cavity = False
    sc.display.render_aa = "8"
    sc.view_settings.view_transform = "Standard"
    sc.view_settings.look = "None"
    sc.view_settings.exposure = 0.0
    sc.render.use_freestyle = True
    sc.render.line_thickness_mode = "ABSOLUTE"
    sc.render.line_thickness = float(shot.get("line_width", 1.6))
    vl = bpy.context.view_layer
    vl.use_freestyle = True
    fs = vl.freestyle_settings
    fs.crease_angle = math.radians(float(shot.get("crease", 38)))
    ls = fs.linesets.new("outline")
    ls.select_silhouette = True
    ls.select_border = True
    ls.select_crease = True
    ls.linestyle.color = (0.04, 0.04, 0.06)
    w = bpy.data.worlds.new("white")
    w.use_nodes = False
    w.color = (1.0, 1.0, 1.0)
    sc.world = w
    sc.camera.data.dof.use_dof = False
    # Freestyle is slow on dense meshes (scanned or board models): decimate those for the line pass only.
    for o in (objs.values() if isinstance(objs, dict) else objs):
        if o.type == "MESH" and len(o.data.polygons) > 120000:
            md = o.modifiers.new("lines_decimate", "DECIMATE")
            md.ratio = 120000 / len(o.data.polygons)
    bpy.context.view_layer.update()
    W, H = sc.render.resolution_x, sc.render.resolution_y
    anchors = []
    for name, o in objs.items():
        if o.hide_render:
            continue
        if name in shot.get("anchors", {}):
            ctr = Vector(shot["anchors"][name]) * S
        else:
            pts = [o.matrix_world @ Vector(c) for c in o.bound_box]
            ctr = sum(pts, Vector()) / len(pts)
        v = bpy_extras.object_utils.world_to_camera_view(sc, sc.camera, ctr)
        anchors.append({"name": name, "x": round(v.x * W, 1), "y": round((1 - v.y) * H, 1), "depth": round(v.z, 4)})
    out.with_suffix(".json").write_text(json.dumps({"width": W, "height": H, "anchors": anchors}, indent=1), encoding="utf-8")


def run_shot(shot):
    reset()
    render_settings()
    mats = make_materials()
    objs = import_parts(mats, shot.get("only"))
    tubes = make_tubes(mats) if shot.get("tubes") else []
    R = align(list(objs.values()) + tubes)
    for name, off in cfg.get("states", {}).get(shot.get("state", ""), {}).items():
        objs[name].location += (R @ Vector(off)) * S
    for name, matname in shot.get("materials", {}).items():  # override the material per shot, e.g. accent
        objs[name].data.materials.clear()
        objs[name].data.materials.append(mats[matname])
    for name in shot.get("ghost", []):  # slightly transparent so the focus lies on other parts
        objs[name].data.materials.clear()
        objs[name].data.materials.append(mats["ghost"])
    if shot.get("ghost_tubes"):
        for tb in tubes:
            tb.data.materials.clear()
            tb.data.materials.append(mats["ghost"])
    for name in shot.get("hide", []):
        if name in objs:
            objs[name].hide_render = True
    if shot.get("only"):
        for name, o in objs.items():
            if name not in shot["only"]:
                o.hide_render = True
    bpy.context.view_layer.update()
    visible = [o for o in objs.values() if not o.hide_render] + tubes
    focus = [objs[n] for n in shot["focus"]] if shot.get("focus") else visible
    if shot.get("focus_mm"):  # section in mm (xmin, ymin, zmin, xmax, ymax, zmax), invisible helper box
        a = Vector(shot["focus_mm"][:3]) * S
        b = Vector(shot["focus_mm"][3:]) * S
        bpy.ops.mesh.primitive_cube_add(size=1, location=(a + b) / 2)
        hb = bpy.context.object
        hb.scale = b - a
        hb.hide_render = True
        bpy.context.view_layer.update()
        focus = [hb]
    lo, hi = bounds(visible)
    size = max((hi - lo).length, 0.05)
    line = shot.get("style") == "line"
    if not shot.get("no_background") and not line:
        backdrop(lo, hi, size, mats)
    lights((lo + hi) / 2, size)
    if shot.get("light_below"):  # bottom view: additional light from below
        ld = bpy.data.lights.new("below", "AREA")
        ld.size = size * 2.5
        ld.energy = 30 * (size * 2.5) ** 2
        lo_obj = bpy.data.objects.new("below", ld)
        bpy.context.collection.objects.link(lo_obj)
        c0 = (lo + hi) / 2
        lo_obj.location = c0 + Vector((0.3, -0.4, -2.5)) * size
        lo_obj.rotation_euler = (c0 - lo_obj.location).to_track_quat("-Z", "Y").to_euler()
    world((0.20, 0.205, 0.215) if shot.get("no_background") else None)
    camera(focus, shot.get("az", -35), shot.get("el", 22), shot.get("margin", 0.92), shot.get("lens", 85), shot.get("fstop", 11), shot.get("ortho", False))
    out = root / "doc" / cfg["folder"] / "images" / f"{cfg['prefix']}-{shot['name']}.png"
    if line:
        line_style(objs, shot, out)
    bpy.context.scene.render.filepath = str(out)
    bpy.ops.render.render(write_still=True)
    print("RENDER", shot["name"], out)


for shot in cfg["shots"]:
    if not wanted or shot["name"] in wanted:
        run_shot(shot)
