"""Media-Mode Scene Generator: Astro-Mice Zero-G Odyssey

Constructs a polished, stylized 3D character and zero-G habitat scene inspired by
the NASA RR-10 mission, using the turnaround and hero reference images as the visual source of truth:
- Commander Pip: Intrepid murine astronaut in tailored matte-white EVA suit
  - Oversized translucent pink ears with warm subsurface scattering
  - Expressive dark glossy eyes, soft pink nose, muzzle smile, fine whisker array
  - Large warm-gold reflective bubble visor with silver helmet rim and side pivot discs
  - Aerospace burnt-orange harness straps with central brushed-metal buckle
  - Dedicated knee pads and heavy-duty moon boots with charcoal sole tread
  - Compact PLSS life-support backpack with inset metallic maintenance hatches
  - Articulated pink tail terminating in the signature white-and-orange T-wing stabilizer thruster with ion plume
  - Stylized original "RR-10 Astro-Mice" mission shoulder patch
- Zero-G Floating Props: Suspended nutrient sphere and hydration droplets
- Research Habitat Staging: Cylindrical module, orbital guidance rail, and Earth observation porthole
- Seamless 5-second (150 frames @ 30 fps) weightless drifting animation loop
"""

import argparse
import json
import math
import os
import sys

# Ensure repository root is on sys.path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import bpy
from mathutils import Euler, Vector

from scripts.core.materials import (
    create_pbr_material,
    create_eva_suit_material,
    create_suit_harness_material,
    create_gold_visor_material,
    create_mouse_tissue_material,
    create_mouse_fur_material,
    create_metal_hardware_material,
    create_boot_sole_material,
    create_mouse_eye_material,
    create_whisker_material,
    create_ion_plume_material,
    create_mission_patch_material,
    create_zero_g_bubble_material,
    create_habitat_wall_material,
    create_earth_porthole_material,
    create_flight_telemetry_hull_material,
    create_bio_sensor_optic_material,
    create_hippocampal_core_material,
)
from scripts.core.camera import setup_camera
from scripts.core.lighting import setup_lighting


def clear_scene():
    """Purges objects, meshes, materials, and custom collections for a clean run."""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

    for coll in list(bpy.data.collections):
        if coll.name != "Scene Collection":
            bpy.data.collections.remove(coll)

    for mesh in list(bpy.data.meshes):
        bpy.data.meshes.remove(mesh)

    for mat in list(bpy.data.materials):
        bpy.data.materials.remove(mat)


def make_cyclic_linear(fcurve):
    """Sets F-Curve extrapolation to linear for seamless cyclic looping."""
    fcurve.extrapolation = 'LINEAR'
    for kp in fcurve.keyframe_points:
        kp.interpolation = 'LINEAR'


def set_smooth_shading(obj):
    """Marks all polygons in a mesh as smooth."""
    if obj and obj.type == 'MESH':
        for poly in obj.data.polygons:
            poly.use_smooth = True


def create_subdivided_sphere(name, radius, segments, rings, coll, location=(0, 0, 0), scale=(1, 1, 1), rotation=(0, 0, 0)):
    """Helper to create a UV sphere with smooth shading."""
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=segments,
        ring_count=rings,
        radius=radius,
        location=location,
        rotation=rotation
    )
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = Vector(scale)
    set_smooth_shading(obj)
    if coll and obj.name not in coll.objects:
        coll.objects.link(obj)
    return obj


def create_subdivided_cylinder(name, radius, depth, vertices, coll, location=(0, 0, 0), rotation=(0, 0, 0), scale=(1, 1, 1)):
    """Helper to create a cylinder with smooth shading."""
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=vertices,
        radius=radius,
        depth=depth,
        location=location,
        rotation=rotation
    )
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = Vector(scale)
    set_smooth_shading(obj)
    if coll and obj.name not in coll.objects:
        coll.objects.link(obj)
    return obj


def create_torus_mesh(name, major_rad, minor_rad, major_seg, minor_seg, coll, location=(0, 0, 0), rotation=(0, 0, 0), scale=(1, 1, 1)):
    """Helper to create a torus with smooth shading."""
    bpy.ops.mesh.primitive_torus_add(
        major_radius=major_rad,
        minor_radius=minor_rad,
        major_segments=major_seg,
        minor_segments=minor_seg,
        location=location,
        rotation=rotation
    )
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = Vector(scale)
    set_smooth_shading(obj)
    if coll and obj.name not in coll.objects:
        coll.objects.link(obj)
    return obj


def build_astro_mouse(name="Commander_Pip", config=None, coll=None):
    """Constructs high-fidelity Commander Pip: the charismatic murine astronaut."""
    if config is None:
        config = {}

    scale = config.get("scale", 1.0)
    suit_col = config.get("suit_base_color", [0.93, 0.93, 0.95, 1.0])
    harness_col = config.get("harness_accent_color", [0.88, 0.28, 0.04, 1.0])
    fur_col = config.get("fur_color", [0.93, 0.90, 0.84, 1.0])
    ear_col = config.get("ear_tissue_color", [0.95, 0.65, 0.62, 1.0])
    ear_ss_weight = config.get("ear_subsurface_weight", 0.55)

    # Instantiate Materials
    mat_suit = create_eva_suit_material(base_color=suit_col)
    mat_harness = create_suit_harness_material(base_color=harness_col)
    mat_visor = create_gold_visor_material()
    mat_fur = create_mouse_fur_material(base_color=fur_col)
    mat_tissue = create_mouse_tissue_material(base_color=ear_col, subsurface_weight=ear_ss_weight)
    mat_metal = create_metal_hardware_material()
    mat_sole = create_boot_sole_material()
    mat_eye = create_mouse_eye_material()
    mat_whisker = create_whisker_material()
    mat_plume = create_ion_plume_material()
    mat_patch = create_mission_patch_material()
    mat_optic = create_bio_sensor_optic_material()

    # Root Empty
    pip_root = bpy.data.objects.new(name, None)
    pip_root.empty_display_size = 0.25 * scale
    coll.objects.link(pip_root)

    # =========================================================================
    # 1. TORSO & SUIT ANATOMY
    # =========================================================================
    # Aerodynamic Pear-Shaped EVA Spacesuit Hull
    torso = create_subdivided_sphere(
        name=f"{name}_Torso",
        radius=0.38 * scale,
        segments=28,
        rings=20,
        coll=coll,
        location=(0, 0, 0.44 * scale),
        scale=(0.92, 0.94, 1.18)
    )
    torso.parent = pip_root
    torso.data.materials.append(mat_suit)

    # Suit Neck Docking Collar Ring
    neck_collar = create_subdivided_cylinder(
        name=f"{name}_Neck_Collar",
        radius=0.28 * scale,
        depth=0.07 * scale,
        vertices=24,
        coll=coll,
        location=(0.0, -0.02 * scale, 0.74 * scale),
        rotation=(math.radians(8), 0, 0)
    )
    neck_collar.parent = pip_root
    neck_collar.data.materials.append(mat_suit)

    neck_collar_trim = create_torus_mesh(
        name=f"{name}_Neck_Collar_Trim",
        major_rad=0.285 * scale,
        minor_rad=0.016 * scale,
        major_seg=24,
        minor_seg=8,
        coll=coll,
        location=(0.0, -0.02 * scale, 0.76 * scale),
        rotation=(math.radians(8), 0, 0)
    )
    neck_collar_trim.parent = pip_root
    neck_collar_trim.data.materials.append(mat_metal)

    # Orange Aerospace Harness: 4-Point Harness with Central Buckle
    # Central Brushed-Metal Hexagonal/Disc Harness Buckle
    harness_buckle = create_subdivided_cylinder(
        name=f"{name}_Harness_Buckle",
        radius=0.052 * scale,
        depth=0.022 * scale,
        vertices=16,
        coll=coll,
        location=(0.0, -0.365 * scale, 0.50 * scale),
        rotation=(math.radians(78), 0, 0)
    )
    harness_buckle.parent = pip_root
    harness_buckle.data.materials.append(mat_metal)

    # Status Optic on Chest Buckle
    buckle_optic = create_subdivided_sphere(
        name=f"{name}_Buckle_Optic",
        radius=0.016 * scale,
        segments=12,
        rings=8,
        coll=coll,
        location=(0.0, -0.378 * scale, 0.50 * scale)
    )
    buckle_optic.parent = pip_root
    buckle_optic.data.materials.append(mat_optic)

    # Upper Shoulder Straps (Left & Right from neck/shoulders to center buckle)
    for side, sign in [("Left", -1), ("Right", 1)]:
        strap_top = create_subdivided_cylinder(
            name=f"{name}_Harness_Strap_Top_{side}",
            radius=0.022 * scale,
            depth=0.22 * scale,
            vertices=12,
            coll=coll,
            location=(sign * 0.10 * scale, -0.32 * scale, 0.59 * scale),
            rotation=(math.radians(38), sign * math.radians(22), sign * math.radians(-12)),
            scale=(1.25, 0.12, 1.0)
        )
        strap_top.parent = pip_root
        strap_top.data.materials.append(mat_harness)

        # Lower Waist Straps (From buckle down toward hips)
        strap_bot = create_subdivided_cylinder(
            name=f"{name}_Harness_Strap_Bot_{side}",
            radius=0.022 * scale,
            depth=0.20 * scale,
            vertices=12,
            coll=coll,
            location=(sign * 0.10 * scale, -0.34 * scale, 0.40 * scale),
            rotation=(math.radians(45), sign * math.radians(-24), sign * math.radians(14)),
            scale=(1.25, 0.12, 1.0)
        )
        strap_bot.parent = pip_root
        strap_bot.data.materials.append(mat_harness)

    # Waist Belt Band (Burnt-orange)
    waist_belt = create_torus_mesh(
        name=f"{name}_Waist_Belt",
        major_rad=0.345 * scale,
        minor_rad=0.018 * scale,
        major_seg=28,
        minor_seg=10,
        coll=coll,
        location=(0.0, 0.0, 0.29 * scale),
        scale=(0.94, 0.96, 0.8)
    )
    waist_belt.parent = pip_root
    waist_belt.data.materials.append(mat_harness)

    # Mission Shoulder Patch (Right Arm/Shoulder)
    mission_patch = create_subdivided_cylinder(
        name=f"{name}_Mission_Patch",
        radius=0.056 * scale,
        depth=0.012 * scale,
        vertices=18,
        coll=coll,
        location=(0.33 * scale, -0.05 * scale, 0.56 * scale),
        rotation=(0, math.radians(72), math.radians(-15))
    )
    mission_patch.parent = pip_root
    mission_patch.data.materials.append(mat_patch)

    # =========================================================================
    # 2. HEAD RIG & FACIAL IDENTITY
    # =========================================================================
    head_root = bpy.data.objects.new(f"{name}_Head_Rig", None)
    head_root.location = Vector((0.0, -0.02 * scale, 0.88 * scale))
    head_root.empty_display_size = 0.15 * scale
    coll.objects.link(head_root)
    head_root.parent = pip_root

    # Cranial volume inside helmet
    head = create_subdivided_sphere(
        name=f"{name}_Head_Cranium",
        radius=0.28 * scale,
        segments=24,
        rings=18,
        coll=coll,
        location=(0, 0, 0),
        scale=(0.96, 1.05, 0.94)
    )
    head.parent = head_root
    head.data.materials.append(mat_fur)

    # Soft Muzzle / Snout
    snout = create_subdivided_sphere(
        name=f"{name}_Muzzle",
        radius=0.15 * scale,
        segments=20,
        rings=14,
        coll=coll,
        location=(0.0, -0.22 * scale, -0.05 * scale),
        scale=(0.78, 1.28, 0.68)
    )
    snout.parent = head_root
    snout.data.materials.append(mat_fur)

    # Soft Pink Nose Tip
    nose = create_subdivided_sphere(
        name=f"{name}_Nose_Tip",
        radius=0.036 * scale,
        segments=14,
        rings=10,
        coll=coll,
        location=(0.0, -0.38 * scale, -0.04 * scale),
        scale=(1.1, 0.9, 0.8)
    )
    nose.parent = head_root
    nose.data.materials.append(mat_tissue)

    # Expressive Dark Glossy Eyes & Highlights
    for side, sign in [("Left", -1), ("Right", 1)]:
        eye = create_subdivided_sphere(
            name=f"{name}_Eye_{side}",
            radius=0.046 * scale,
            segments=16,
            rings=12,
            coll=coll,
            location=(sign * 0.15 * scale, -0.21 * scale, 0.05 * scale),
            scale=(0.85, 1.0, 1.1)
        )
        eye.parent = head_root
        eye.data.materials.append(mat_eye)

        # Specular glint highlight on eye
        glint = create_subdivided_sphere(
            name=f"{name}_Eye_Glint_{side}",
            radius=0.012 * scale,
            segments=8,
            rings=6,
            coll=coll,
            location=(sign * 0.145 * scale, -0.252 * scale, 0.068 * scale)
        )
        glint.parent = head_root
        glint.data.materials.append(mat_suit)

    # Fine Whiskers (3 on each cheek curving outward)
    whisker_angles = [(-8, -14), (0, 0), (8, 14)]
    for side, sign in [("Left", -1), ("Right", 1)]:
        for w_idx, (w_pitch, w_yaw) in enumerate(whisker_angles):
            whisker = create_subdivided_cylinder(
                name=f"{name}_Whisker_{side}_{w_idx+1}",
                radius=0.0032 * scale,
                depth=0.22 * scale,
                vertices=8,
                coll=coll,
                location=(sign * 0.14 * scale, -0.26 * scale, (-0.05 + w_idx * 0.02) * scale),
                rotation=(
                    math.radians(w_pitch),
                    math.radians(sign * (75 + w_yaw)),
                    math.radians(sign * -15)
                )
            )
            whisker.parent = head_root
            whisker.data.materials.append(mat_whisker)

    # Oversized Cupped Mouse Ears
    for side, sign in [("Left", -1), ("Right", 1)]:
        # Outer ear shell (cream fur)
        ear_outer = create_subdivided_sphere(
            name=f"{name}_Ear_{side}",
            radius=0.22 * scale,
            segments=20,
            rings=14,
            coll=coll,
            location=(sign * 0.30 * scale, 0.06 * scale, 0.18 * scale),
            scale=(0.95, 0.16, 1.22)
        )
        ear_outer.rotation_euler = Euler((math.radians(14), sign * math.radians(-26), sign * math.radians(18)), 'XYZ')
        ear_outer.parent = head_root
        ear_outer.data.materials.append(mat_fur)

        # Inner ear cup dish (warm translucent pink tissue with subsurface warmth)
        ear_inner = create_subdivided_sphere(
            name=f"{name}_EarInner_{side}",
            radius=0.17 * scale,
            segments=16,
            rings=10,
            coll=coll,
            location=(sign * 0.29 * scale, 0.02 * scale, 0.18 * scale),
            scale=(0.88, 0.10, 1.12)
        )
        ear_inner.rotation_euler = ear_outer.rotation_euler
        ear_inner.parent = head_root
        ear_inner.data.materials.append(mat_tissue)

    # Helmet Dome & White Shell (covers back and top of cranium)
    helmet_shell = create_subdivided_sphere(
        name=f"{name}_Helmet_Dome",
        radius=0.34 * scale,
        segments=28,
        rings=20,
        coll=coll,
        location=(0.0, 0.04 * scale, 0.02 * scale),
        scale=(1.02, 0.95, 1.04)
    )
    helmet_shell.parent = head_root
    helmet_shell.data.materials.append(mat_suit)

    # Helmet Bezel / Face Opening Ring (Silver metal rim)
    helmet_bezel = create_torus_mesh(
        name=f"{name}_Helmet_Bezel",
        major_rad=0.34 * scale,
        minor_rad=0.022 * scale,
        major_seg=32,
        minor_seg=10,
        coll=coll,
        location=(0.0, -0.06 * scale, 0.02 * scale),
        rotation=(math.radians(15), 0, 0),
        scale=(1.0, 1.05, 1.0)
    )
    helmet_bezel.parent = head_root
    helmet_bezel.data.materials.append(mat_metal)

    # Warm-Gold Electroplated Reflective Bubble Visor (Transparent gold glass)
    visor = create_subdivided_sphere(
        name=f"{name}_Visor",
        radius=0.35 * scale,
        segments=32,
        rings=24,
        coll=coll,
        location=(0.0, -0.08 * scale, 0.02 * scale),
        scale=(1.04, 1.14, 1.02)
    )
    visor.parent = head_root
    visor.data.materials.append(mat_visor)

    # Side Pivot Discs / Earcups on Helmet Sides
    for side, sign in [("Left", -1), ("Right", 1)]:
        pivot = create_subdivided_cylinder(
            name=f"{name}_Helmet_Pivot_{side}",
            radius=0.062 * scale,
            depth=0.026 * scale,
            vertices=18,
            coll=coll,
            location=(sign * 0.34 * scale, 0.02 * scale, 0.04 * scale),
            rotation=(0, math.radians(90), 0)
        )
        pivot.parent = head_root
        pivot.data.materials.append(mat_metal)

    # =========================================================================
    # 3. ARMS, SLEEVES & GLOVED PAWS (Natural relaxed astronaut posture)
    # =========================================================================
    for side, sign in [("Left", -1), ("Right", 1)]:
        # Shoulder Accordion Bellow Ring
        shoulder_bellow = create_torus_mesh(
            name=f"{name}_Shoulder_Bellow_{side}",
            major_rad=0.092 * scale,
            minor_rad=0.020 * scale,
            major_seg=18,
            minor_seg=8,
            coll=coll,
            location=(sign * 0.28 * scale, -0.01 * scale, 0.58 * scale),
            rotation=(math.radians(15), sign * math.radians(-15), 0)
        )
        shoulder_bellow.parent = pip_root
        shoulder_bellow.data.materials.append(mat_suit)

        # Upper Arm (Extending downward along suit flank)
        upper_arm = create_subdivided_cylinder(
            name=f"{name}_UpperArm_{side}",
            radius=0.078 * scale,
            depth=0.20 * scale,
            vertices=16,
            coll=coll,
            location=(sign * 0.32 * scale, -0.04 * scale, 0.46 * scale),
            rotation=(math.radians(18), sign * math.radians(-12), sign * math.radians(8))
        )
        upper_arm.parent = pip_root
        upper_arm.data.materials.append(mat_suit)

        # Forearm (Angled forward)
        forearm = create_subdivided_cylinder(
            name=f"{name}_Forearm_{side}",
            radius=0.074 * scale,
            depth=0.20 * scale,
            vertices=16,
            coll=coll,
            location=(sign * 0.33 * scale, -0.12 * scale, 0.34 * scale),
            rotation=(math.radians(35), sign * math.radians(-8), sign * math.radians(12))
        )
        forearm.parent = pip_root
        forearm.data.materials.append(mat_suit)

        # Orange Wrist Cuff Ring
        wrist_ring = create_torus_mesh(
            name=f"{name}_Wrist_Ring_{side}",
            major_rad=0.075 * scale,
            minor_rad=0.015 * scale,
            major_seg=16,
            minor_seg=8,
            coll=coll,
            location=(sign * 0.33 * scale, -0.18 * scale, 0.26 * scale),
            rotation=(math.radians(35), sign * math.radians(-8), sign * math.radians(12))
        )
        wrist_ring.parent = pip_root
        wrist_ring.data.materials.append(mat_harness)

        # Technical EVA Gloved Paw (White glove palm)
        palm = create_subdivided_sphere(
            name=f"{name}_Glove_Palm_{side}",
            radius=0.065 * scale,
            segments=16,
            rings=12,
            coll=coll,
            location=(sign * 0.32 * scale, -0.22 * scale, 0.22 * scale),
            scale=(0.95, 1.15, 0.75)
        )
        palm.parent = pip_root
        palm.data.materials.append(mat_suit)

        # Angled Thumb (Gripper pad)
        thumb = create_subdivided_cylinder(
            name=f"{name}_Glove_Thumb_{side}",
            radius=0.018 * scale,
            depth=0.052 * scale,
            vertices=10,
            coll=coll,
            location=(sign * 0.27 * scale, -0.23 * scale, 0.23 * scale),
            rotation=(math.radians(20), sign * math.radians(-35), 0)
        )
        thumb.parent = pip_root
        thumb.data.materials.append(mat_metal)

        # Curving Fingers Pad
        finger_pad = create_subdivided_sphere(
            name=f"{name}_Glove_Fingers_{side}",
            radius=0.048 * scale,
            segments=14,
            rings=10,
            coll=coll,
            location=(sign * 0.31 * scale, -0.26 * scale, 0.19 * scale),
            scale=(1.1, 0.7, 0.9)
        )
        finger_pad.parent = pip_root
        finger_pad.data.materials.append(mat_metal)

    # =========================================================================
    # 4. LEGS, KNEE PADS & MOON BOOTS
    # =========================================================================
    for side, sign in [("Left", -1), ("Right", 1)]:
        # Thigh Segment
        thigh = create_subdivided_cylinder(
            name=f"{name}_Thigh_{side}",
            radius=0.105 * scale,
            depth=0.24 * scale,
            vertices=16,
            coll=coll,
            location=(sign * 0.15 * scale, 0.02 * scale, 0.20 * scale),
            rotation=(math.radians(-12), sign * math.radians(6), 0)
        )
        thigh.parent = pip_root
        thigh.data.materials.append(mat_suit)

        # Dedicated Oval Knee Armor Pad
        knee_pad = create_subdivided_sphere(
            name=f"{name}_KneePad_{side}",
            radius=0.065 * scale,
            segments=14,
            rings=10,
            coll=coll,
            location=(sign * 0.15 * scale, -0.09 * scale, 0.10 * scale),
            scale=(1.1, 0.55, 1.35)
        )
        knee_pad.parent = pip_root
        knee_pad.data.materials.append(mat_suit)

        # Orange Accent Rim on Knee Pad
        knee_rim = create_torus_mesh(
            name=f"{name}_KneeRim_{side}",
            major_rad=0.068 * scale,
            minor_rad=0.012 * scale,
            major_seg=16,
            minor_seg=8,
            coll=coll,
            location=(sign * 0.15 * scale, -0.095 * scale, 0.10 * scale),
            rotation=(math.radians(82), 0, 0),
            scale=(1.05, 1.25, 0.8)
        )
        knee_rim.parent = pip_root
        knee_rim.data.materials.append(mat_harness)

        # Lower Leg / Calf
        calf = create_subdivided_cylinder(
            name=f"{name}_Calf_{side}",
            radius=0.092 * scale,
            depth=0.20 * scale,
            vertices=16,
            coll=coll,
            location=(sign * 0.15 * scale, 0.0 * scale, -0.04 * scale),
            rotation=(math.radians(6), 0, 0)
        )
        calf.parent = pip_root
        calf.data.materials.append(mat_suit)

        # Ankle Orange Band
        ankle_band = create_torus_mesh(
            name=f"{name}_Ankle_Band_{side}",
            major_rad=0.096 * scale,
            minor_rad=0.015 * scale,
            major_seg=18,
            minor_seg=8,
            coll=coll,
            location=(sign * 0.15 * scale, -0.01 * scale, -0.12 * scale),
            rotation=(math.radians(6), 0, 0)
        )
        ankle_band.parent = pip_root
        ankle_band.data.materials.append(mat_harness)

        # Heavy-Duty Moon Boot Upper & Toe Bumper
        boot_upper = create_subdivided_cylinder(
            name=f"{name}_Boot_Upper_{side}",
            radius=0.106 * scale,
            depth=0.12 * scale,
            vertices=18,
            coll=coll,
            location=(sign * 0.15 * scale, -0.04 * scale, -0.18 * scale),
            rotation=(math.radians(4), 0, 0),
            scale=(1.0, 1.28, 1.0)
        )
        boot_upper.parent = pip_root
        boot_upper.data.materials.append(mat_suit)

        # Front Toe Bumper
        toe_bumper = create_subdivided_sphere(
            name=f"{name}_Boot_Toe_{side}",
            radius=0.074 * scale,
            segments=14,
            rings=10,
            coll=coll,
            location=(sign * 0.15 * scale, -0.14 * scale, -0.21 * scale),
            scale=(1.1, 1.1, 0.65)
        )
        toe_bumper.parent = pip_root
        toe_bumper.data.materials.append(mat_suit)

        # Thick Charcoal Rubber Sole Tread
        boot_sole = create_subdivided_cylinder(
            name=f"{name}_Boot_Sole_{side}",
            radius=0.114 * scale,
            depth=0.035 * scale,
            vertices=18,
            coll=coll,
            location=(sign * 0.15 * scale, -0.05 * scale, -0.23 * scale),
            scale=(1.02, 1.34, 1.0)
        )
        boot_sole.parent = pip_root
        boot_sole.data.materials.append(mat_sole)

        # Orange Heel Stripe / Clamp
        heel_clamp = create_subdivided_cylinder(
            name=f"{name}_Boot_HeelClamp_{side}",
            radius=0.110 * scale,
            depth=0.02 * scale,
            vertices=14,
            coll=coll,
            location=(sign * 0.15 * scale, 0.05 * scale, -0.21 * scale),
            scale=(0.95, 0.4, 0.8)
        )
        heel_clamp.parent = pip_root
        heel_clamp.data.materials.append(mat_harness)

    # =========================================================================
    # 5. DORSAL LIFE-SUPPORT BACKPACK (PLSS)
    # =========================================================================
    # Main Hard-Shell Housing (Chamfered capsule)
    backpack_body = create_subdivided_cylinder(
        name=f"{name}_PLSS_Housing",
        radius=0.18 * scale,
        depth=0.40 * scale,
        vertices=20,
        coll=coll,
        location=(0.0, 0.30 * scale, 0.48 * scale),
        rotation=(0, 0, 0),
        scale=(0.82, 0.52, 1.0)
    )
    backpack_body.parent = pip_root
    backpack_body.data.materials.append(mat_suit)

    # Recessed Metallic Maintenance Panel on Back Face
    plss_panel = create_subdivided_cylinder(
        name=f"{name}_PLSS_Panel",
        radius=0.12 * scale,
        depth=0.02 * scale,
        vertices=16,
        coll=coll,
        location=(0.0, 0.40 * scale, 0.48 * scale),
        rotation=(math.radians(90), 0, 0),
        scale=(0.85, 1.35, 1.0)
    )
    plss_panel.parent = pip_root
    plss_panel.data.materials.append(mat_metal)

    # Horizontal Orange Accent Stripe on Backpack
    plss_stripe = create_torus_mesh(
        name=f"{name}_PLSS_Stripe",
        major_rad=0.182 * scale,
        minor_rad=0.014 * scale,
        major_seg=20,
        minor_seg=8,
        coll=coll,
        location=(0.0, 0.30 * scale, 0.40 * scale),
        scale=(0.84, 0.54, 1.0)
    )
    plss_stripe.parent = pip_root
    plss_stripe.data.materials.append(mat_harness)

    # Twin Side Oxygen Canisters
    for side, sign in [("Left", -1), ("Right", 1)]:
        canister = create_subdivided_cylinder(
            name=f"{name}_PLSS_Canister_{side}",
            radius=0.046 * scale,
            depth=0.32 * scale,
            vertices=14,
            coll=coll,
            location=(sign * 0.15 * scale, 0.30 * scale, 0.50 * scale),
            rotation=(0, 0, 0)
        )
        canister.parent = pip_root
        canister.data.materials.append(mat_suit)

        # Metallic Canister Top Valve
        valve = create_subdivided_sphere(
            name=f"{name}_PLSS_Valve_{side}",
            radius=0.036 * scale,
            segments=12,
            rings=8,
            coll=coll,
            location=(sign * 0.15 * scale, 0.30 * scale, 0.67 * scale)
        )
        valve.parent = pip_root
        valve.data.materials.append(mat_metal)

    # Twin Bottom Thruster Bells on PLSS
    for side, sign in [("Left", -1), ("Right", 1)]:
        plss_thruster = create_subdivided_cylinder(
            name=f"{name}_PLSS_Thruster_{side}",
            radius=0.034 * scale,
            depth=0.060 * scale,
            vertices=14,
            coll=coll,
            location=(sign * 0.08 * scale, 0.34 * scale, 0.26 * scale),
            rotation=(math.radians(12), 0, 0)
        )
        plss_thruster.parent = pip_root
        plss_thruster.data.materials.append(mat_metal)

    # =========================================================================
    # 6. ARTICULATED TAIL & T-WING STABILIZER THRUSTER
    # =========================================================================
    # Suit Tail Exit Grommet (Reinforced collar)
    tail_grommet = create_torus_mesh(
        name=f"{name}_Tail_Grommet",
        major_rad=0.050 * scale,
        minor_rad=0.015 * scale,
        major_seg=16,
        minor_seg=8,
        coll=coll,
        location=(0.0, 0.22 * scale, 0.20 * scale),
        rotation=(math.radians(35), 0, 0)
    )
    tail_grommet.parent = pip_root
    tail_grommet.data.materials.append(mat_suit)

    # 5 Articulated Pink Tail Segments seamlessly curving backward and upward
    tail_segments = []
    tail_curve_data = [
        (0.28, 0.21, 0.13, 80.5, 0.038),
        (0.39, 0.245, 0.12, 63.4, 0.034),
        (0.485, 0.31, 0.13, 48.4, 0.030),
        (0.565, 0.405, 0.13, 32.5, 0.026),
        (0.62, 0.52, 0.13, 18.4, 0.022),
    ]

    for i, (cy, cz, length, pitch_deg, s_rad) in enumerate(tail_curve_data):
        seg = create_subdivided_cylinder(
            name=f"{name}_Tail_Seg_{i+1}",
            radius=s_rad * scale,
            depth=length * scale,
            vertices=14,
            coll=coll,
            location=(0.0, cy * scale, cz * scale),
            rotation=(math.radians(pitch_deg), 0, 0)
        )
        seg.parent = pip_root
        seg.data.materials.append(mat_tissue)
        tail_segments.append(seg)

    # Seamless spherical joint caps between segments
    joint_coords = [
        (0.22, 0.20, 0.039),
        (0.34, 0.22, 0.036),
        (0.44, 0.27, 0.032),
        (0.53, 0.35, 0.028),
        (0.60, 0.46, 0.024),
        (0.64, 0.58, 0.022),
    ]
    for j_idx, (jy, jz, j_rad) in enumerate(joint_coords):
        joint = create_subdivided_sphere(
            name=f"{name}_Tail_Joint_{j_idx+1}",
            radius=j_rad * scale,
            segments=12,
            rings=8,
            coll=coll,
            location=(0.0, jy * scale, jz * scale)
        )
        joint.parent = pip_root
        joint.data.materials.append(mat_tissue)

    # T-Wing Attitude Stabilizer Unit at Tail Tip
    # Central Collar Sleeve
    t_collar = create_subdivided_cylinder(
        name=f"{name}_Tail_T_Collar",
        radius=0.028 * scale,
        depth=0.08 * scale,
        vertices=14,
        coll=coll,
        location=(0.0, 0.65 * scale, 0.61 * scale),
        rotation=(math.radians(18.4), 0, 0)
    )
    t_collar.parent = pip_root
    t_collar.data.materials.append(mat_suit)

    # Horizontal Swept Aerodynamic Stabilizer Wing (White body)
    t_wing = create_subdivided_cylinder(
        name=f"{name}_Tail_T_Wing",
        radius=0.020 * scale,
        depth=0.30 * scale,
        vertices=14,
        coll=coll,
        location=(0.0, 0.66 * scale, 0.63 * scale),
        rotation=(0, math.radians(90), 0),
        scale=(1.0, 3.2, 0.4)
    )
    t_wing.parent = pip_root
    t_wing.data.materials.append(mat_suit)

    # Orange Leading Edge & Wingtip Accents
    for side, sign in [("Left", -1), ("Right", 1)]:
        wingtip = create_subdivided_cylinder(
            name=f"{name}_Tail_T_Wingtip_{side}",
            radius=0.021 * scale,
            depth=0.065 * scale,
            vertices=12,
            coll=coll,
            location=(sign * 0.16 * scale, 0.66 * scale, 0.63 * scale),
            rotation=(0, math.radians(90), 0),
            scale=(1.05, 3.4, 0.45)
        )
        wingtip.parent = pip_root
        wingtip.data.materials.append(mat_harness)

    # Dual Micro-Nozzle Thruster Bells
    for side, sign in [("Left", -1), ("Right", 1)]:
        nozzle = create_subdivided_cylinder(
            name=f"{name}_Tail_T_Nozzle_{side}",
            radius=0.016 * scale,
            depth=0.040 * scale,
            vertices=12,
            coll=coll,
            location=(sign * 0.055 * scale, 0.69 * scale, 0.62 * scale),
            rotation=(math.radians(98), 0, 0)
        )
        nozzle.parent = pip_root
        nozzle.data.materials.append(mat_metal)

        # Emissive Cyan-White Ion Exhaust Plumes
        plume = create_subdivided_cylinder(
            name=f"{name}_Tail_Ion_Plume_{side}",
            radius=0.014 * scale,
            depth=0.10 * scale,
            vertices=10,
            coll=coll,
            location=(sign * 0.055 * scale, 0.76 * scale, 0.61 * scale),
            rotation=(math.radians(98), 0, 0),
            scale=(0.8, 0.8, 1.2)
        )
        plume.parent = pip_root
        plume.data.materials.append(mat_plume)

    return {
        "root": pip_root,
        "head": head_root,
        "tail_segments": tail_segments,
        "torso": torso,
        "visor": visor
    }


def build_floating_props(coll=None):
    """Constructs zero-gravity floating nutrient sphere and hydration droplets."""
    mat_bubble = create_zero_g_bubble_material()
    mat_core = create_hippocampal_core_material(
        name="Mat_Nutrient_Core",
        emission_color=(1.0, 0.65, 0.12, 1.0),
        emission_strength=4.0
    )

    # Primary Nutrient Sphere floating in front of Pip's reach
    nutrient_root = bpy.data.objects.new("ZeroG_Nutrient_Root", None)
    nutrient_root.location = Vector((0.36, -0.62, 0.46))
    coll.objects.link(nutrient_root)

    outer_sphere = create_subdivided_sphere(
        name="ZeroG_Nutrient_Sphere",
        radius=0.13,
        segments=24,
        rings=16,
        coll=coll,
        location=(0, 0, 0)
    )
    outer_sphere.parent = nutrient_root
    outer_sphere.data.materials.append(mat_bubble)

    inner_seed = create_subdivided_sphere(
        name="ZeroG_Nutrient_Nucleus",
        radius=0.065,
        segments=16,
        rings=12,
        coll=coll,
        location=(0, 0, 0)
    )
    inner_seed.parent = nutrient_root
    inner_seed.data.materials.append(mat_core)

    # Secondary micro hydration droplet floating above
    droplet_root = bpy.data.objects.new("ZeroG_Hydration_Root", None)
    droplet_root.location = Vector((-0.34, -0.48, 0.88))
    coll.objects.link(droplet_root)

    droplet = create_subdivided_sphere(
        name="ZeroG_Hydration_Droplet",
        radius=0.058,
        segments=16,
        rings=12,
        coll=coll,
        location=(0, 0, 0)
    )
    droplet.parent = droplet_root
    droplet.data.materials.append(mat_bubble)

    return {
        "nutrient_root": nutrient_root,
        "droplet_root": droplet_root
    }


def build_habitat_environment(coll=None):
    """Constructs orbital habitat guidance track and Earth observation porthole."""
    mat_wall = create_habitat_wall_material()
    mat_porthole = create_earth_porthole_material()
    mat_metal = create_metal_hardware_material()

    # 1. Circular Porthole Bezel Frame on Module Wall
    porthole_ring = create_torus_mesh(
        name="Habitat_Porthole_Frame",
        major_rad=1.85,
        minor_rad=0.08,
        major_seg=48,
        minor_seg=16,
        coll=coll,
        location=(0.0, 1.65, 0.55),
        rotation=(math.radians(90), 0, 0)
    )
    porthole_ring.data.materials.append(mat_metal)

    # 2. Glowing Curved Earth Horizon Disc (visible through porthole)
    earth_disc = create_subdivided_cylinder(
        name="Habitat_Earth_Horizon",
        radius=1.75,
        depth=0.04,
        vertices=48,
        coll=coll,
        location=(0.0, 1.75, 0.55),
        rotation=(math.radians(90), 0, 0)
    )
    earth_disc.data.materials.append(mat_porthole)

    # 3. Orbital Guidance Rail / Centrifuge Track running alongside habitat
    guidance_rail = create_torus_mesh(
        name="Habitat_Centrifuge_Rail",
        major_rad=2.65,
        minor_rad=0.035,
        major_seg=64,
        minor_seg=12,
        coll=coll,
        location=(0.0, 0.0, 0.15),
        rotation=(math.radians(18), math.radians(25), 0)
    )
    guidance_rail.data.materials.append(mat_wall)


def apply_media_animations(character_rig, props_rig, anim_cfg):
    """Sets up synchronized zero-G weightless drift and floating animations."""
    total_frames = anim_cfg.get("timeline_frames", 150)
    amplitude = anim_cfg.get("zero_g_float_amplitude", 0.14)

    pip_root = character_rig["root"]
    head_root = character_rig["head"]
    tail_segments = character_rig["tail_segments"]
    nutrient_root = props_rig["nutrient_root"]
    droplet_root = props_rig["droplet_root"]

    # Configure scene timeline
    bpy.context.scene.frame_start = 1
    bpy.context.scene.frame_end = total_frames
    bpy.context.scene.render.fps = anim_cfg.get("fps", 30)

    # Keyframe sample points (0, 0.25, 0.5, 0.75, 1.0 of cycle)
    sample_frames = [1, int(total_frames * 0.25), int(total_frames * 0.5), int(total_frames * 0.75), total_frames + 1]

    # 1. Commander Pip Root Floating Animation
    for f in sample_frames:
        theta = 2.0 * math.pi * ((f - 1) % total_frames) / float(total_frames)

        # Sinusoidal zero-G translation
        pos_z = amplitude * math.sin(theta)
        pos_y = 0.04 * math.cos(theta)
        pos_x = 0.02 * math.sin(theta * 2.0)
        pip_root.location = Vector((pos_x, pos_y, pos_z))
        pip_root.keyframe_insert(data_path="location", frame=f)

        # Subtle natural attitude pitch and roll oscillation
        rot_x = math.radians(3.0) * math.cos(theta)
        rot_y = math.radians(2.0) * math.sin(theta)
        rot_z = math.radians(3.5) * math.sin(theta * 0.5)
        pip_root.rotation_euler = Euler((rot_x, rot_y, rot_z), 'XYZ')
        pip_root.keyframe_insert(data_path="rotation_euler", frame=f)

        # 2. Inquisitive Head Scanning Turn
        head_rot_z = math.radians(6.5) * math.sin(theta)
        head_rot_x = math.radians(2.5) * math.cos(theta)
        head_root.rotation_euler = Euler((head_rot_x, 0, head_rot_z), 'XYZ')
        head_root.keyframe_insert(data_path="rotation_euler", frame=f)

        # 3. Chained Harmonic Tail Undulation
        for idx, seg in enumerate(tail_segments):
            seg_phase = theta - idx * 0.40
            seg_pitch = math.radians(3.5) * math.sin(seg_phase)
            seg_yaw = math.radians(2.5) * math.cos(seg_phase)
            seg.rotation_euler = Euler((seg_pitch, seg_yaw, 0), 'XYZ')
            seg.keyframe_insert(data_path="rotation_euler", frame=f)

        # 4. Zero-G Nutrient Sphere Bobbing (90 deg out of phase with Pip)
        nut_z = 0.46 + 0.06 * math.sin(theta + math.pi * 0.5)
        nut_y = -0.62 + 0.025 * math.cos(theta + math.pi * 0.5)
        nutrient_root.location = Vector((0.36, nut_y, nut_z))
        nutrient_root.keyframe_insert(data_path="location", frame=f)

        # 5. Secondary Hydration Droplet Bobbing
        drop_z = 0.88 + 0.045 * math.sin(theta + math.pi * 0.25)
        droplet_root.location = Vector((-0.34, -0.48, drop_z))
        droplet_root.keyframe_insert(data_path="location", frame=f)

    # Set cyclic linear extrapolation on all animated objects
    for animated_obj in [pip_root, head_root, nutrient_root, droplet_root] + tail_segments:
        if animated_obj.animation_data and animated_obj.animation_data.action:
            for fcurve in animated_obj.animation_data.action.fcurves:
                make_cyclic_linear(fcurve)


def generate_media_scene(recipe=None, keep_scene=False):
    """Orchestrates procedural generation of the RR-10 Media Companion scene."""
    if recipe is None:
        recipe_path = os.path.join(PROJECT_ROOT, "data", "recipes", "media_astro_mouse.json")
        if os.path.exists(recipe_path):
            with open(recipe_path, "r") as f:
                recipe = json.load(f)
        else:
            recipe = {}

    if not keep_scene:
        clear_scene()

    media_coll = bpy.data.collections.new("Media_Simulation_Collection")
    bpy.context.scene.collection.children.link(media_coll)

    # 1. Build Commander Pip
    char_cfg = recipe.get("character", {})
    character_rig = build_astro_mouse("Commander_Pip", config=char_cfg, coll=media_coll)

    # 2. Build Zero-G Floating Props
    props_rig = build_floating_props(coll=media_coll)

    # 3. Build Habitat Staging & Earth Porthole
    build_habitat_environment(coll=media_coll)

    # 4. Apply Animations
    anim_cfg = recipe.get("animation", {})
    apply_media_animations(character_rig, props_rig, anim_cfg)

    # 5. Setup Camera & Lighting Rigs
    scene_cfg = recipe.get("scene", {})
    setup_camera(recipe=recipe)
    setup_lighting(recipe=recipe)

    created_count = len(media_coll.objects)
    print(f"[generate_media_scene] Media companion scene generated ({created_count} objects in collection).")
    return character_rig


def parse_args():
    argv = sys.argv
    args_after_dash = argv[argv.index("--") + 1:] if "--" in argv else []
    parser = argparse.ArgumentParser(description="Antigravity RR-10 Media Companion Generator")
    parser.add_argument(
        "--recipe",
        type=str,
        default=os.path.join(PROJECT_ROOT, "data", "recipes", "media_astro_mouse.json"),
        help="Path to media companion recipe JSON"
    )
    parser.add_argument(
        "--keep-scene",
        action="store_true",
        help="Preserve existing scene objects"
    )
    parser.add_argument(
        "--export",
        action="store_true",
        help="Trigger GLB and metadata export after generation"
    )
    parser.add_argument(
        "--output",
        type=str,
        default=os.path.join(PROJECT_ROOT, "exports", "media_simulation.glb"),
        help="Custom GLB output path"
    )
    parser.add_argument(
        "--metadata-output",
        type=str,
        default=os.path.join(PROJECT_ROOT, "exports", "media_simulation.json"),
        help="Custom metadata output path"
    )
    return parser.parse_args(args_after_dash)


if __name__ == "__main__":
    args = parse_args()
    loaded_recipe = {}
    if args.recipe and os.path.exists(args.recipe):
        with open(args.recipe, "r") as f:
            loaded_recipe = json.load(f)

    generate_media_scene(recipe=loaded_recipe, keep_scene=args.keep_scene)

    if args.export:
        from scripts.export_scene import export_scene
        export_scene(
            glb_path=args.output or os.path.join(PROJECT_ROOT, "exports", "media_simulation.glb"),
            metadata_path=args.metadata_output or os.path.join(PROJECT_ROOT, "exports", "media_simulation.json"),
            recipe=loaded_recipe
        )
