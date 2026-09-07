"""Reusable studio lighting and world environment staging utilities."""

import bpy
from mathutils import Vector


def setup_world_environment(color=(0.012, 0.014, 0.02, 1.0), strength=0.4):
    """Configures the background radiance and ambient world tone."""
    world = bpy.context.scene.world
    if not world:
        world = bpy.data.worlds.new("Antigravity_World")
        bpy.context.scene.world = world

    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs["Color"].default_value = color
        bg.inputs["Strength"].default_value = strength
    return world


def setup_lighting(recipe=None):
    """Sets up a balanced 3-point studio lighting rig targeting scene origin.

    Args:
        recipe (dict, optional): Scene recipe configuration.

    Returns:
        list[bpy.types.Object]: Created light objects.
    """
    if recipe is None:
        recipe = {}

    light_cfg = recipe.get("scene", {}).get("lighting", {})
    key_power = light_cfg.get("key_intensity", 800.0)
    fill_power = light_cfg.get("fill_intensity", 350.0)
    rim_power = light_cfg.get("rim_intensity", 1200.0)

    # Clean existing lights
    for obj in list(bpy.data.objects):
        if obj.type == 'LIGHT':
            bpy.data.objects.remove(obj, do_unlink=True)

    coll_name = "Studio_Lighting"
    if coll_name in bpy.data.collections:
        coll = bpy.data.collections[coll_name]
    else:
        coll = bpy.data.collections.new(coll_name)
        bpy.context.scene.collection.children.link(coll)

    lights = []

    # 1. Key Light (Upper Right Front - Warm White)
    key_data = bpy.data.lights.new(name="Light_Key", type='AREA')
    key_data.energy = key_power
    key_data.color = (1.0, 0.95, 0.88)
    key_data.size = 3.0
    key_obj = bpy.data.objects.new("Light_Key", key_data)
    key_obj.location = Vector((4.5, -4.0, 5.0))
    coll.objects.link(key_obj)
    lights.append(key_obj)

    # 2. Fill Light (Left Front - Cool Blue/Cyan)
    fill_data = bpy.data.lights.new(name="Light_Fill", type='AREA')
    fill_data.energy = fill_power
    fill_data.color = (0.75, 0.85, 1.0)
    fill_data.size = 5.0
    fill_obj = bpy.data.objects.new("Light_Fill", fill_data)
    fill_obj.location = Vector((-5.0, -3.5, 3.0))
    coll.objects.link(fill_obj)
    lights.append(fill_obj)

    # 3. Rim / Accent Back Light (Back Right High - Electric Cyan)
    rim_data = bpy.data.lights.new(name="Light_Rim", type='AREA')
    rim_data.energy = rim_power
    rim_data.color = (0.2, 0.8, 1.0)
    rim_data.size = 2.0
    rim_obj = bpy.data.objects.new("Light_Rim", rim_data)
    rim_obj.location = Vector((2.0, 5.5, 4.0))
    coll.objects.link(rim_obj)
    lights.append(rim_obj)

    # Orient lights toward tracking target or origin
    target = bpy.data.objects.get("Camera_Track_Target")
    for light in lights:
        track = light.constraints.new(type='TRACK_TO')
        if target:
            track.target = target
        track.track_axis = 'TRACK_NEGATIVE_Z'
        track.up_axis = 'UP_Y'

    setup_world_environment()
    return lights
