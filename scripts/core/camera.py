"""Reusable camera framing and tracking utilities."""

import math
import bpy
from mathutils import Vector


def compute_bounding_sphere(objects):
    """Computes the center and approximate bounding radius for a list of objects.

    Args:
        objects (list[bpy.types.Object]): Evaluated objects.

    Returns:
        tuple[Vector, float]: (center_vector, radius)
    """
    points = []
    for obj in objects:
        if obj.type == 'MESH':
            for corner in obj.bound_box:
                points.append(obj.matrix_world @ Vector(corner))

    if not points:
        return Vector((0.0, 0.0, 0.0)), 2.5

    center = sum(points, Vector((0.0, 0.0, 0.0))) / len(points)
    radius = max((p - center).length for p in points)
    return center, max(radius, 1.0)


def setup_camera(target_objects=None, recipe=None):
    """Creates or updates a cinematic camera auto-framed around target objects.

    Args:
        target_objects (list[bpy.types.Object], optional): Objects to frame.
        recipe (dict, optional): Scene recipe configuration.

    Returns:
        bpy.types.Object: Active camera object.
    """
    if recipe is None:
        recipe = {}

    cam_cfg = recipe.get("scene", {}).get("camera", {})
    focal_length = cam_cfg.get("focal_length", 55.0)
    dist_mult = cam_cfg.get("distance_multiplier", 2.6)
    elevation = math.radians(cam_cfg.get("elevation_angle", 25.0))
    azimuth = math.radians(cam_cfg.get("azimuth_angle", 45.0))

    # Remove existing cameras to prevent conflicting viewports
    for obj in list(bpy.data.objects):
        if obj.type == 'CAMERA':
            bpy.data.objects.remove(obj, do_unlink=True)

    center, radius = compute_bounding_sphere(target_objects or [])
    distance = max(radius * dist_mult, 4.0)

    # Spherical to Cartesian positioning
    cam_x = center.x + distance * math.cos(elevation) * math.sin(azimuth)
    cam_y = center.y - distance * math.cos(elevation) * math.cos(azimuth)
    cam_z = center.z + distance * math.sin(elevation)

    cam_data = bpy.data.cameras.new(name="Main_Camera")
    cam_data.lens = focal_length
    cam_data.clip_start = 0.1
    cam_data.clip_end = 250.0

    cam_obj = bpy.data.objects.new("Main_Camera", cam_data)
    cam_obj.location = Vector((cam_x, cam_y, cam_z))
    bpy.context.scene.collection.objects.link(cam_obj)

    # Center tracking target
    target_name = "Camera_Track_Target"
    if target_name in bpy.data.objects:
        target_empty = bpy.data.objects[target_name]
        target_empty.location = center
    else:
        target_empty = bpy.data.objects.new(target_name, None)
        target_empty.location = center
        target_empty.empty_display_size = 0.2
        target_empty.empty_display_type = 'PLAIN_AXES'
        bpy.context.scene.collection.objects.link(target_empty)

    # Track-To constraint
    track = cam_obj.constraints.new(type='TRACK_TO')
    track.target = target_empty
    track.track_axis = 'TRACK_NEGATIVE_Z'
    track.up_axis = 'UP_Y'

    bpy.context.scene.camera = cam_obj
    return cam_obj
