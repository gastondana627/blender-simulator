"""Studio Reference Renderer for Commander Pip

Renders three clean, high-aesthetic studio reference views of Commander Pip:
1. Full-Body Front View
2. Three-Quarter Hero View
3. Side Profile View

Saves renders directly to the artifacts directory for inclusion in walkthrough.md.
"""

import math
import os
import sys

import bpy
from mathutils import Euler, Vector

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from scripts.generate_media_scene import generate_media_scene

ARTIFACT_DIR = os.environ.get("ARTIFACT_DIR", os.path.join(PROJECT_ROOT, "exports", "renders"))


def setup_studio_environment():
    """Sets up a clean studio lighting environment and infinite ground plane."""
    world = bpy.context.scene.world
    if not world:
        world = bpy.data.worlds.new("Studio_World")
        bpy.context.scene.world = world

    world.use_nodes = True
    bg_node = world.node_tree.nodes.get("Background")
    if bg_node:
        bg_node.inputs[0].default_value = (0.42, 0.44, 0.48, 1.0)
        bg_node.inputs[1].default_value = 1.0

    # Clean studio floor
    bpy.ops.mesh.primitive_plane_add(size=30, location=(0, 0, -0.32))
    floor = bpy.context.active_object
    floor.name = "Studio_Floor"

    floor_mat = bpy.data.materials.new(name="Mat_Studio_Floor")
    floor_mat.use_nodes = True
    bsdf = floor_mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs[0].default_value = (0.38, 0.40, 0.44, 1.0)
        bsdf.inputs["Roughness"].default_value = 0.55
    floor.data.materials.append(floor_mat)

    # Key light
    bpy.ops.object.light_add(type='AREA', location=(2.5, -3.2, 3.2))
    key_light = bpy.context.active_object
    key_light.data.energy = 850.0
    key_light.data.size = 2.5
    key_light.data.color = (1.0, 0.98, 0.95)

    # Fill light
    bpy.ops.object.light_add(type='AREA', location=(-3.0, -2.4, 2.0))
    fill_light = bpy.context.active_object
    fill_light.data.energy = 380.0
    fill_light.data.size = 3.0
    fill_light.data.color = (0.88, 0.93, 1.0)

    # Rim / Hair light
    bpy.ops.object.light_add(type='AREA', location=(0.0, 3.5, 3.2))
    rim_light = bpy.context.active_object
    rim_light.data.energy = 850.0
    rim_light.data.size = 2.0
    rim_light.data.color = (1.0, 0.92, 0.82)


def render_view(cam_obj, output_path, resolution=(1440, 1080)):
    """Renders scene from specified camera to output_path using Cycles."""
    scene = bpy.context.scene
    scene.camera = cam_obj
    scene.render.resolution_x = resolution[0]
    scene.render.resolution_y = resolution[1]
    scene.render.image_settings.file_format = 'PNG'
    scene.render.filepath = output_path
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = 64
    scene.cycles.use_denoising = True
    bpy.ops.render.render(write_still=True)
    print(f"[render_character_views] Rendered -> {output_path}")


def main():
    # 1. Generate Pip in media scene
    generate_media_scene()

    # Hide background habitat walls, rail, and floating bubbles so Pip is the clear hero
    for obj in bpy.data.objects:
        if any(token in obj.name for token in [
            "Habitat_Centrifuge_Rail",
            "Habitat_Porthole_Frame",
            "Habitat_Earth_Horizon",
            "ZeroG_Nutrient",
            "ZeroG_Hydration"
        ]):
            obj.hide_render = True

    # 2. Add studio floor and lights
    setup_studio_environment()

    # Configure render engine
    scene = bpy.context.scene
    scene.frame_set(1)  # Frame 1 default pose

    # Target point at character center of mass (Z ~ 0.38)
    target = Vector((0.0, 0.0, 0.38))

    # Views specification: (name, distance, azimuth_deg, elevation_deg, filename)
    # Framed full-body from boots (z=-0.25) to ear tips (z=1.25)
    views = [
        ("Front View", 3.8, 0.0, 4.0, "pip_front_view.png"),
        ("Three-Quarter Hero View", 3.9, 32.0, 12.0, "pip_three_quarter_hero.png"),
        ("Side View", 3.9, 90.0, 4.0, "pip_side_view.png"),
    ]

    for view_name, dist, az_deg, el_deg, filename in views:
        az_rad = math.radians(az_deg)
        el_rad = math.radians(el_deg)

        cx = target.x + dist * math.cos(el_rad) * math.sin(az_rad)
        cy = target.y - dist * math.cos(el_rad) * math.cos(az_rad)
        cz = target.z + dist * math.sin(el_rad)

        cam_data = bpy.data.cameras.new(f"Camera_{view_name}")
        cam_data.lens = 55.0  # Natural focal length for character turnaround
        cam_obj = bpy.data.objects.new(f"Camera_{view_name}", cam_data)
        bpy.context.scene.collection.objects.link(cam_obj)
        cam_obj.location = Vector((cx, cy, cz))

        # Look at target
        direction = target - cam_obj.location
        rot_quat = direction.to_track_quat('-Z', 'Y')
        cam_obj.rotation_euler = rot_quat.to_euler()

        out_path = os.path.join(ARTIFACT_DIR, filename)
        render_view(cam_obj, out_path)


if __name__ == "__main__":
    main()
