"""Procedural illustrative neural sculpture; not a clinical anatomy model."""

import json
import math
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parent
C = json.loads((ROOT / "neural-scene.json").read_text())
scene = bpy.data.scenes.new(C["name"])
bpy.context.window.scene = scene


def material(name, emission=False):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    node = mat.node_tree.nodes.get("Principled BSDF")
    node.inputs["Base Color"].default_value = C["material"]["color"]
    node.inputs["Metallic"].default_value = C["material"]["metallic"]
    node.inputs["Roughness"].default_value = C["material"]["roughness"]
    if emission:
        node.inputs["Emission Color"].default_value = C["signal"]["color"]
        node.inputs["Emission Strength"].default_value = C["signal"]["strength"]
    return mat


metal = material("Titanium neural fibers")
signal = material("Illuminated neural pathways", True)
params = C["lobes"]
for side in [-1, 1]:
    for track in range(params["tracks"]):
        latitude = (track + 0.5) / params["tracks"] * math.pi
        data = bpy.data.curves.new("Cortical fiber", "CURVE")
        data.dimensions = "3D"
        data.bevel_depth = params["tube"]
        data.bevel_resolution = 3
        spline = data.splines.new("POLY")
        spline.points.add(params["segments"] - 1)
        for index, point in enumerate(spline.points):
            angle = index / params["segments"] * math.tau
            fold = math.sin(angle * params["folds"] + latitude * 8) * params["amplitude"]
            fold += math.cos(angle * 7 - latitude * 14) * params["amplitude"] * 0.45
            phi = latitude + fold
            radius = 1 + 0.07 * math.sin(angle * 5 + latitude * 11)
            x = side * (params["offset"] + params["radii"][0] * math.cos(phi))
            y = params["radii"][1] * math.sin(phi) * math.cos(angle) * radius
            z = params["radii"][2] * math.sin(phi) * math.sin(angle) * radius
            z += 0.14 * math.cos(y)
            point.co = (x, y, z, 1)
        spline.use_cyclic_u = True
        obj = bpy.data.objects.new("Neural fiber", data)
        scene.collection.objects.link(obj)
        data.materials.append(signal if track % C["signal"]["every"] == 0 else metal)

for values in C["lights"]:
    data = bpy.data.lights.new("Neural studio light", "AREA")
    data.energy = values["energy"]
    data.color = values["color"]
    data.shape = "DISK"
    data.size = values["size"]
    obj = bpy.data.objects.new(data.name, data)
    scene.collection.objects.link(obj)
    obj.location = values["location"]
    obj.rotation_euler = (-obj.location).to_track_quat("-Z", "Y").to_euler()

world = bpy.data.worlds.new("Dark studio")
world.use_nodes = True
world.node_tree.nodes["Background"].inputs[0].default_value = (0.04, 0.06, 0.09, 1)
world.node_tree.nodes["Background"].inputs[1].default_value = C["world_strength"]
scene.world = world
camera = bpy.data.objects.new("Neural camera", bpy.data.cameras.new("Neural camera"))
scene.collection.objects.link(camera)
camera.location = C["camera"]["location"]
camera.rotation_euler = (Vector(C["camera"]["target"]) - camera.location).to_track_quat("-Z", "Y").to_euler()
camera.data.type = "ORTHO"
camera.data.ortho_scale = C["camera"]["scale"]
scene.camera = camera
scene.render.engine = "CYCLES"
scene.cycles.samples = C["samples"]
scene.cycles.use_denoising = True
scene.render.resolution_x, scene.render.resolution_y = C["resolution"]
scene.render.resolution_percentage = 100
scene.render.film_transparent = True
scene.render.image_settings.file_format = "PNG"
scene.render.image_settings.color_mode = "RGBA"
scene.view_settings.view_transform = "AgX"
scene.render.filepath = str((ROOT / C["output"]).resolve())
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / C["blend"]))
bpy.ops.render.render(write_still=True)
