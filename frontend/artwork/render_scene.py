"""Create the project-owned Evidence Atlas scene inside Blender."""

import json
import math
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parent
CONFIG = json.loads((ROOT / "scene.json").read_text())
scene = bpy.data.scenes.new(CONFIG["collection"])
bpy.context.window.scene = scene


def material(name, values):
    result = bpy.data.materials.new(name)
    result.use_nodes = True
    bsdf = result.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = values["color"]
    bsdf.inputs["Metallic"].default_value = values["metallic"]
    bsdf.inputs["Roughness"].default_value = values["roughness"]
    bsdf.inputs["Transmission Weight"].default_value = values["transmission"]
    bsdf.inputs["IOR"].default_value = values["ior"]
    return result


materials = {key: material(key, values) for key, values in CONFIG["materials"].items()}


def curve(name, points, width, mat, parent=None, cyclic=False):
    data = bpy.data.curves.new(name, "CURVE")
    data.dimensions = "3D"
    data.bevel_depth = width
    data.bevel_resolution = 3
    spline = data.splines.new("POLY")
    spline.points.add(len(points) - 1)
    for point, coordinate in zip(spline.points, points, strict=True):
        point.co = (*coordinate, 1)
    spline.use_cyclic_u = cyclic
    obj = bpy.data.objects.new(name, data)
    scene.collection.objects.link(obj)
    obj.data.materials.append(mat)
    obj.parent = parent
    return obj


plate = CONFIG["plate"]
for index in range(plate["count"]):
    pivot = bpy.data.objects.new(f"Analysis layer {index + 1}", None)
    scene.collection.objects.link(pivot)
    pivot.location = (index * plate["offset_x"], index * plate["offset_y"], index * plate["spacing"])
    pivot.rotation_euler.z = plate["rotation"]
    bpy.ops.mesh.primitive_cube_add(size=1)
    obj = bpy.context.object
    obj.name = f"Optical glass {index + 1}"
    obj.dimensions = plate["size"]
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bevel = obj.modifiers.new("Polished corners", "BEVEL")
    bevel.width = plate["bevel"]
    bevel.segments = 8
    obj.modifiers.new("Surface normals", "WEIGHTED_NORMAL")
    obj.data.materials.append(materials["glass"])
    obj.parent = pivot
    for x, y in CONFIG["dots"]:
        bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=12, radius=CONFIG["dot_radius"])
        dot = bpy.context.object
        dot.name = "Registration point"
        dot.parent = pivot
        dot.location = (x, y, plate["size"][2])
        dot.data.materials.append(materials["gold"])
        for polygon in dot.data.polygons:
            polygon.use_smooth = True
    rings = CONFIG["rings"]
    if index % 2 == 0:
        for ring in range(rings["count"]):
            radius = rings["radius"] + ring * rings["gap"]
            points = [
                (
                    math.cos(a * math.tau / rings["segments"]) * radius,
                    math.sin(a * math.tau / rings["segments"]) * radius,
                    plate["size"][2],
                )
                for a in range(rings["segments"])
            ]
            curve("Evidence contour", points, rings["width"], materials["line"], pivot, True)
    else:
        trace = CONFIG["trace"]
        for row in range(trace["count"]):
            points = []
            for n in range(trace["samples"]):
                x = (n / (trace["samples"] - 1) - 0.5) * trace["length"]
                y = (row - trace["count"] / 2) * trace["spacing"] + math.sin(x * math.tau + row) * trace["amplitude"]
                points.append((x, y, plate["size"][2]))
            curve("Signal trace", points, trace["width"], materials["line"], pivot)

for values in CONFIG["lights"]:
    data = bpy.data.lights.new("Studio softbox", "AREA")
    data.energy = values["energy"]
    data.shape = "DISK"
    data.size = values["size"]
    data.color = values["color"]
    obj = bpy.data.objects.new("Studio softbox", data)
    scene.collection.objects.link(obj)
    obj.location = values["location"]
    obj.rotation_euler = (Vector(CONFIG["camera"]["target"]) - obj.location).to_track_quat("-Z", "Y").to_euler()

world = bpy.data.worlds.new("Neutral studio")
world.use_nodes = True
world.node_tree.nodes["Background"].inputs[0].default_value = (*CONFIG["world"][:3], 1)
world.node_tree.nodes["Background"].inputs[1].default_value = CONFIG["world"][3]
scene.world = world
camera = bpy.data.objects.new("Editorial camera", bpy.data.cameras.new("Editorial camera"))
scene.collection.objects.link(camera)
camera.location = CONFIG["camera"]["location"]
camera.rotation_euler = (Vector(CONFIG["camera"]["target"]) - camera.location).to_track_quat("-Z", "Y").to_euler()
camera.data.type = "ORTHO"
camera.data.ortho_scale = CONFIG["camera"]["scale"]
scene.camera = camera
scene.render.engine = CONFIG["engine"]
scene.cycles.samples = CONFIG["samples"]
scene.cycles.use_denoising = True
scene.render.resolution_x, scene.render.resolution_y = CONFIG["resolution"]
scene.render.resolution_percentage = 100
scene.render.film_transparent = True
scene.render.image_settings.file_format = "PNG"
scene.render.image_settings.color_mode = "RGBA"
scene.view_settings.view_transform = "AgX"
output = (ROOT / CONFIG["output"]).resolve()
output.parent.mkdir(parents=True, exist_ok=True)
scene.render.filepath = str(output)
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / CONFIG["blend"]))
bpy.ops.render.render(write_still=True)
print("Evidence Atlas artwork saved.")
