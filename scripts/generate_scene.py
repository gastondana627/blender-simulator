"""Scene and Procedural Asset Generation Module for Blender.

Constructs an authentic RR-10 Spaceflight Murine Neural Proxy Core
with biological clay tissue, intracranial fluid-shift pulsation, and
habitat bio-telemetry sensor arrays.

Can be run:
1. Headless CLI:
   blender -b --python scripts/generate_scene.py -- --recipe data/processed/sample_scene.json
2. Combined generation + export:
   blender -b --python scripts/generate_scene.py -- --recipe data/processed/sample_scene.json --export
3. Imported as a module:
   from scripts.generate_scene import generate_scene
   generate_scene(recipe)
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
    create_murine_neural_clay_material,
    create_hippocampal_core_material,
    create_flight_telemetry_hull_material,
    create_bio_sensor_optic_material,
    create_pca_flt_material,
    create_pca_gc_material,
)
from scripts.core.camera import setup_camera
from scripts.core.lighting import setup_lighting
from scripts.data_adapter import load_data_or_recipe


def clear_scene():
    """Purges objects, meshes, materials, textures, and custom collections for a clean run."""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

    for coll in list(bpy.data.collections):
        if coll.name != "Scene Collection":
            bpy.data.collections.remove(coll)

    for mesh in list(bpy.data.meshes):
        bpy.data.meshes.remove(mesh)

    for mat in list(bpy.data.materials):
        bpy.data.materials.remove(mat)

    for tex in list(bpy.data.textures):
        bpy.data.textures.remove(tex)


def make_cyclic_linear(fcurve):
    """Sets F-Curve extrapolation to linear for seamless cyclic looping."""
    fcurve.extrapolation = 'LINEAR'
    for kp in fcurve.keyframe_points:
        kp.interpolation = 'LINEAR'


def set_smooth_shading(obj):
    """Marks all polygons in a mesh as smooth."""
    if obj.type == 'MESH':
        for poly in obj.data.polygons:
            poly.use_smooth = True


def build_telemetry_probe(name, ring_radius, angle_rad, scale, coll, parent_ring, mat_hull, mat_optic):
    """Constructs a flight habitat bio-telemetry probe aimed at the murine neural core."""
    probe_root = bpy.data.objects.new(name, None)
    probe_root.empty_display_size = 0.08 * scale
    coll.objects.link(probe_root)
    probe_root.parent = parent_ring

    # Position on ring circumference
    pos_x = ring_radius * math.cos(angle_rad)
    pos_y = ring_radius * math.sin(angle_rad)
    probe_root.location = Vector((pos_x, pos_y, 0.0))

    # Aerospace sensor hull: streamlined probe body
    probe_len = 0.32 * scale
    probe_rad = 0.085 * scale
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=8,
        radius=probe_rad,
        depth=probe_len
    )
    hull = bpy.context.active_object
    hull.name = f"{name}_Hull"
    hull.parent = probe_root
    coll.objects.link(hull)
    bpy.context.scene.collection.objects.unlink(hull)
    hull.data.materials.append(mat_hull)
    set_smooth_shading(hull)

    # Orient inward toward the central murine neural core
    hull.rotation_euler = Euler((0, math.radians(90.0), angle_rad + math.pi), 'XYZ')

    # Optical / radiation sensor aperture facing the murine core
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=16,
        ring_count=12,
        radius=probe_rad * 0.55
    )
    optic = bpy.context.active_object
    optic.name = f"{name}_Optic"
    optic.parent = hull
    optic.location = Vector((0, 0, probe_len * 0.48))
    coll.objects.link(optic)
    bpy.context.scene.collection.objects.unlink(optic)
    optic.data.materials.append(mat_optic)
    set_smooth_shading(optic)

    return probe_root, [hull, optic]


def build_murine_neural_scene(recipe, collection):
    """Builds the authentic RR-10 Murine Neural Proxy Core & Spaceflight Telemetry Array."""
    gen_cfg = recipe.get("generator", {})
    mat_cfg = recipe.get("materials", {})

    frames = gen_cfg.get("animation_frames", 150)
    scale = gen_cfg.get("scale", 1.0)
    core_rad = gen_cfg.get("core_radius", 0.75) * scale
    olfactory_scale = gen_cfg.get("olfactory_scale", 0.38) * scale
    cerebellar_scale = gen_cfg.get("cerebellar_scale", 0.48) * scale
    cage_rad = gen_cfg.get("cage_radius", 2.8) * scale
    asym = gen_cfg.get("asymmetry", 1.05)
    cap_depth = gen_cfg.get("capillary_depth", 0.1) * scale
    cap_freq = gen_cfg.get("capillary_frequency", 0.38)
    wire_thick = gen_cfg.get("wireframe_thickness", 0.012) * scale
    fluid_shift_amp = gen_cfg.get("breathing_amplitude", 0.16)
    rings_count = gen_cfg.get("rings_count", 4)
    pods_per_ring = gen_cfg.get("pods_per_ring", 2)

    # Master Root
    root = bpy.data.objects.new("RR10_Simulation_Root", None)
    root.empty_display_type = 'ARROWS'
    root.empty_display_size = 0.5 * scale
    collection.objects.link(root)

    # Materials
    clay_cfg = mat_cfg.get("murine_clay", {})
    mat_clay = create_murine_neural_clay_material(
        name="Mat_Murine_Neural_Tissue",
        base_color=clay_cfg.get("base_color", (0.68, 0.52, 0.46, 1.0)),
        roughness=clay_cfg.get("roughness", 0.55),
        emission_color=clay_cfg.get("emission_color", (0.88, 0.26, 0.14, 1.0)),
        emission_strength=clay_cfg.get("emission_strength", 0.08),
        subsurface_weight=clay_cfg.get("subsurface_weight", 0.35)
    )

    hippo_cfg = mat_cfg.get("hippocampal_core", {})
    mat_hippocampal = create_hippocampal_core_material(
        name="Mat_Hippocampal_Core",
        emission_color=hippo_cfg.get("emission_color", (0.0, 0.95, 1.0, 1.0)),
        emission_strength=hippo_cfg.get("emission_strength", 4.5)
    )

    hull_cfg = mat_cfg.get("telemetry_hull", {})
    mat_hull = create_flight_telemetry_hull_material(
        name="Mat_Flight_Telemetry_Hull",
        base_color=hull_cfg.get("base_color", (0.11, 0.13, 0.17, 1.0)),
        metallic=hull_cfg.get("metallic", 0.94),
        roughness=hull_cfg.get("roughness", 0.18)
    )

    optic_cfg = mat_cfg.get("sensor_optic", {})
    mat_optic = create_bio_sensor_optic_material(
        name="Mat_BioSensor_Optic",
        emission_color=optic_cfg.get("emission_color", (0.0, 0.95, 1.0, 1.0)),
        emission_strength=optic_cfg.get("emission_strength", 6.5)
    )

    track_cfg = mat_cfg.get("orbital_tracks", {})
    mat_track = create_pbr_material(
        name="Mat_Telemetry_Track",
        base_color=track_cfg.get("base_color", (0.78, 0.82, 0.88, 1.0)),
        metallic=track_cfg.get("metallic", 0.98),
        roughness=track_cfg.get("roughness", 0.12),
        emission_color=track_cfg.get("emission_color", (0.0, 0.9, 0.85, 1.0)),
        emission_strength=track_cfg.get("emission_strength", 0.5)
    )

    cage_cfg = mat_cfg.get("telemetry_cage", {})
    mat_cage = create_pbr_material(
        name="Mat_Habitat_Scaffold",
        base_color=cage_cfg.get("base_color", (0.10, 0.12, 0.16, 1.0)),
        metallic=cage_cfg.get("metallic", 0.92),
        roughness=cage_cfg.get("roughness", 0.3),
        emission_color=cage_cfg.get("emission_color", (0.0, 0.8, 1.0, 1.0)),
        emission_strength=cage_cfg.get("emission_strength", 0.25)
    )

    created_objects = []

    # =========================================================
    # 1. MURINE NEURAL CORE (ANTEROPOSTERIOR ELONGATION)
    # =========================================================
    core_root = bpy.data.objects.new("Murine_Neural_Core_Root", None)
    core_root.parent = root
    collection.objects.link(core_root)

    # Procedural microvascular capillary texture
    capillary_tex = bpy.data.textures.new("Murine_Capillary_Noise", type='CLOUDS')
    capillary_tex.noise_scale = cap_freq
    capillary_tex.noise_depth = 4

    # 1A. Dual Cerebral Hemispheres (Lissencephalic ovoids with distinct sagittal fissure)
    cortex_specs = [
        ("Murine_Cortex_Left", -0.56, (0.64, 1.24, 0.72), 2.0),
        ("Murine_Cortex_Right", +0.56, (0.64 * asym, 1.24 / asym, 0.72 * asym), -2.0),
    ]

    for lobe_name, x_offset, scale_vec, z_tilt in cortex_specs:
        bpy.ops.mesh.primitive_uv_sphere_add(
            segments=48,
            ring_count=32,
            radius=core_rad
        )
        lobe = bpy.context.active_object
        lobe.name = lobe_name
        lobe.parent = core_root
        collection.objects.link(lobe)
        bpy.context.scene.collection.objects.unlink(lobe)

        # Sagittal offset creating murine longitudinal fissure
        lobe.location = Vector((x_offset * core_rad, 0.0, 0.0))
        lobe.scale = Vector(scale_vec)
        lobe.rotation_euler = Euler((0, 0, math.radians(z_tilt)), 'XYZ')

        # Microvascular surface displacement
        disp = lobe.modifiers.new(name="Microvascular_Strain", type='DISPLACE')
        disp.texture = capillary_tex
        disp.strength = cap_depth
        disp.mid_level = 0.5

        sub = lobe.modifiers.new(name="Subsurf", type='SUBSURF')
        sub.levels = 1
        sub.render_levels = 1

        lobe.data.materials.append(mat_clay)
        set_smooth_shading(lobe)
        created_objects.append(lobe)

    # 1B. Anterior Olfactory Bulbs (Distinctive Murine Feature along +Y)
    olfactory_specs = [
        ("Murine_Olfactory_Left", -0.28, 1.0),
        ("Murine_Olfactory_Right", +0.28, -1.0),
    ]
    for bulb_name, x_offset, z_tilt in olfactory_specs:
        bpy.ops.mesh.primitive_uv_sphere_add(
            segments=24,
            ring_count=16,
            radius=olfactory_scale
        )
        bulb = bpy.context.active_object
        bulb.name = bulb_name
        bulb.parent = core_root
        collection.objects.link(bulb)
        bpy.context.scene.collection.objects.unlink(bulb)

        # Frontal projection forward
        bulb.location = Vector((x_offset * core_rad, core_rad * 1.20, -0.06 * core_rad))
        bulb.scale = Vector((0.44, 0.88, 0.44))
        bulb.rotation_euler = Euler((math.radians(14.0), 0, math.radians(z_tilt * 4.0)), 'XYZ')

        bulb.data.materials.append(mat_clay)
        set_smooth_shading(bulb)
        created_objects.append(bulb)

    # 1C. Caudal Cerebellar Anchor (Posterior node at -Y)
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=32,
        ring_count=20,
        radius=cerebellar_scale
    )
    cerebellum = bpy.context.active_object
    cerebellum.name = "Murine_Cerebellar_Node"
    cerebellum.parent = core_root
    collection.objects.link(cerebellum)
    bpy.context.scene.collection.objects.unlink(cerebellum)

    cerebellum.location = Vector((0.0, -core_rad * 1.18, -0.12 * core_rad))
    cerebellum.scale = Vector((0.98, 0.60, 0.58))

    disp_c = cerebellum.modifiers.new(name="Folia_Displace", type='DISPLACE')
    disp_c.texture = capillary_tex
    disp_c.strength = cap_depth * 0.75

    cerebellum.data.materials.append(mat_clay)
    set_smooth_shading(cerebellum)
    created_objects.append(cerebellum)

    # 1D. Deep Hippocampal Synaptic Core (Sagittal Fissure Bridge)
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=24,
        ring_count=16,
        radius=core_rad * 0.52
    )
    hippocampus = bpy.context.active_object
    hippocampus.name = "Hippocampal_Synaptic_Core"
    hippocampus.parent = core_root
    collection.objects.link(hippocampus)
    bpy.context.scene.collection.objects.unlink(hippocampus)

    hippocampus.scale = Vector((0.26, 0.96, 0.42))
    hippocampus.data.materials.append(mat_hippocampal)
    set_smooth_shading(hippocampus)
    created_objects.append(hippocampus)

    # Initial aesthetic presentation angle for murine axis
    core_root.rotation_euler = Euler((math.radians(-14.0), 0, math.radians(28.0)), 'XYZ')

    # 1E. Animate Intracranial Pressure (ICP) Cephalic Fluid Shift Pulse
    for f in range(1, frames + 2):
        phase = ((f - 1) / frames) * 2 * math.pi
        pulse_s = 1.0 + fluid_shift_amp * math.sin(phase)
        # Anteroposterior breathing
        core_root.scale = Vector((pulse_s * 0.98, pulse_s * 1.03, pulse_s))
        core_root.keyframe_insert(data_path="scale", frame=f)

        # Microvascular core pulse
        hippocampus.rotation_euler.z = math.sin(phase) * 0.06
        hippocampus.keyframe_insert(data_path="rotation_euler", frame=f)

    # =========================================================
    # 2. FLIGHT HABITAT TELEMETRY GIMBALS & PROBES
    # =========================================================
    track_radii = [
        core_rad * 1.85,
        core_rad * 2.25,
        core_rad * 2.65,
        core_rad * 3.05
    ][:rings_count]

    rot_multipliers = [1, -1, 2, -2]

    for i, r in enumerate(track_radii):
        bpy.ops.mesh.primitive_torus_add(
            major_radius=r,
            minor_radius=0.015 * scale,
            major_segments=54,
            minor_segments=10
        )
        track = bpy.context.active_object
        track.name = f"Habitat_Telemetry_Track_{i+1}"
        track.parent = root
        collection.objects.link(track)
        bpy.context.scene.collection.objects.unlink(track)

        track.data.materials.append(mat_track)
        created_objects.append(track)

        # Bio-telemetry probes measuring neural zones
        step_angle = (2 * math.pi) / max(pods_per_ring, 1)
        for p in range(pods_per_ring):
            angle = p * step_angle + (i * 0.6)
            probe_name = f"BioTelemetry_Probe_{i+1}_{chr(65+p)}"
            probe_empty, probe_meshes = build_telemetry_probe(
                name=probe_name,
                ring_radius=r,
                angle_rad=angle,
                scale=scale,
                coll=collection,
                parent_ring=track,
                mat_hull=mat_hull,
                mat_optic=mat_optic
            )
            created_objects.extend(probe_meshes)

        # Multi-axis orbital tracking animation
        tilt = math.radians(26.0 * (i + 1))
        track.rotation_mode = 'XYZ'
        mult = rot_multipliers[i % len(rot_multipliers)]

        if i % 3 == 0:
            track.rotation_euler = Euler((tilt, 0, 0), 'XYZ')
            track.keyframe_insert(data_path="rotation_euler", frame=1)
            track.rotation_euler = Euler((tilt, 0, math.radians(360.0 * mult)), 'XYZ')
            track.keyframe_insert(data_path="rotation_euler", frame=frames + 1)
        elif i % 3 == 1:
            track.rotation_euler = Euler((0, tilt, 0), 'XYZ')
            track.keyframe_insert(data_path="rotation_euler", frame=1)
            track.rotation_euler = Euler((math.radians(360.0 * mult), tilt, 0), 'XYZ')
            track.keyframe_insert(data_path="rotation_euler", frame=frames + 1)
        else:
            track.rotation_euler = Euler((tilt, 0, tilt), 'XYZ')
            track.keyframe_insert(data_path="rotation_euler", frame=1)
            track.rotation_euler = Euler((tilt, math.radians(360.0 * mult), tilt), 'XYZ')
            track.keyframe_insert(data_path="rotation_euler", frame=frames + 1)

        if track.animation_data and track.animation_data.action:
            for fcurve in track.animation_data.action.fcurves:
                make_cyclic_linear(fcurve)

    # =========================================================
    # 3. MICROGRAVITY HABITAT TELEMETRY SCAFFOLD
    # =========================================================
    # Refined icosahedral geodesic telemetry envelope (subdivisions=1: clean, un-cluttered aerospace frame)
    bpy.ops.mesh.primitive_ico_sphere_add(
        subdivisions=1,
        radius=core_rad * 3.4
    )
    cage = bpy.context.active_object
    cage.name = "Habitat_Radiation_Scaffold"
    cage.parent = root
    collection.objects.link(cage)
    bpy.context.scene.collection.objects.unlink(cage)

    wf = cage.modifiers.new(name="Habitat_Wire", type='WIREFRAME')
    wf.thickness = 0.0035 * scale
    wf.use_replace = True

    cage.data.materials.append(mat_cage)
    created_objects.append(cage)

    # Slow continuous cosmic telemetry rotation
    cage.rotation_mode = 'XYZ'
    cage.keyframe_insert(data_path="rotation_euler", frame=1)
    cage.rotation_euler.z = math.radians(180.0)
    cage.keyframe_insert(data_path="rotation_euler", frame=frames + 1)

    if cage.animation_data and cage.animation_data.action:
        for fcurve in cage.animation_data.action.fcurves:
            make_cyclic_linear(fcurve)

    # Timeline setup
    bpy.context.scene.frame_start = 1
    bpy.context.scene.frame_end = frames
    bpy.context.scene.render.fps = recipe.get("scene", {}).get("fps", 30)

    return created_objects


def build_pca_background_constellation(coll):
    """Constructs a subtle, low-opacity 3D background constellation derived from Figure A PCA coordinates.

    IMPORTANT: This is a visually secondary, graph-derived background motif positioned safely
    behind the central murine neural proxy. It is NOT a literal spatial anatomical model.
    """
    mat_flt = create_pca_flt_material()
    mat_gc = create_pca_gc_material()

    root = bpy.data.objects.new("PCA_Constellation_Root", None)
    root.empty_display_size = 0.1
    coll.objects.link(root)
    # Position in background behind the neural core (Y = 2.4, Z = 0.2)
    root.location = Vector((0.0, 2.4, 0.2))

    # Actual normalized sample coordinates from Figure A:
    # Cerebellum (OSD-563) and Hippocampus (OSD-564)
    samples_data = [
        # Cerebellum (OSD-563) - left cluster
        {"id": "OSD563_F1", "cond": "FLT", "x": -1.2 + 0.006 * 177.0, "z": 0.006 * -111.0},
        {"id": "OSD563_F3", "cond": "FLT", "x": -1.2 + 0.006 * 12.0, "z": 0.006 * 35.0},
        {"id": "OSD563_F5", "cond": "FLT", "x": -1.2 + 0.006 * 42.0, "z": 0.006 * 130.0},
        {"id": "OSD563_F7", "cond": "FLT", "x": -1.2 + 0.006 * -76.0, "z": 0.006 * -57.0},
        {"id": "OSD563_F9", "cond": "FLT", "x": -1.2 + 0.006 * -63.0, "z": 0.006 * -25.0},
        {"id": "OSD563_G1", "cond": "GC",  "x": -1.2 + 0.006 * 73.0, "z": 0.006 * 6.0},
        {"id": "OSD563_G3", "cond": "GC",  "x": -1.2 + 0.006 * -108.0, "z": 0.006 * -79.0},
        {"id": "OSD563_G5", "cond": "GC",  "x": -1.2 + 0.006 * -48.0, "z": 0.006 * 11.0},
        {"id": "OSD563_G7", "cond": "GC",  "x": -1.2 + 0.006 * -17.0, "z": 0.006 * 49.0},
        {"id": "OSD563_G9", "cond": "GC",  "x": -1.2 + 0.006 * 2.0, "z": 0.006 * 42.0},

        # Hippocampus (OSD-564) - right cluster
        {"id": "OSD564_F1", "cond": "FLT", "x": 1.2 + 0.006 * -119.0, "z": 0.006 * -38.0},
        {"id": "OSD564_F3", "cond": "FLT", "x": 1.2 + 0.006 * -62.0, "z": 0.006 * 6.0},
        {"id": "OSD564_F5", "cond": "FLT", "x": 1.2 + 0.006 * -16.0, "z": 0.006 * 144.0},
        {"id": "OSD564_F7", "cond": "FLT", "x": 1.2 + 0.006 * -39.0, "z": 0.006 * -29.0},
        {"id": "OSD564_F9", "cond": "FLT", "x": 1.2 + 0.006 * -68.0, "z": 0.006 * 3.0},
        {"id": "OSD564_G1", "cond": "GC",  "x": 1.2 + 0.006 * 73.0, "z": 0.006 * 22.0},
        {"id": "OSD564_G3", "cond": "GC",  "x": 1.2 + 0.006 * 117.0, "z": 0.006 * -110.0},
        {"id": "OSD564_G5", "cond": "GC",  "x": 1.2 + 0.006 * 108.0, "z": 0.006 * 23.0},
        {"id": "OSD564_G7", "cond": "GC",  "x": 1.2 + 0.006 * 87.0, "z": 0.006 * 26.0},
        {"id": "OSD564_G9", "cond": "GC",  "x": 1.2 + 0.006 * -85.0, "z": 0.006 * -46.0},
    ]

    node_objects = []
    for s in samples_data:
        bpy.ops.mesh.primitive_uv_sphere_add(
            segments=10,
            ring_count=8,
            radius=0.024,
            location=(s["x"], 0.0, s["z"])
        )
        node = bpy.context.active_object
        node.name = f"PCA_Node_{s['id']}"
        set_smooth_shading(node)
        node.parent = root
        node.data.materials.append(mat_flt if s["cond"] == "FLT" else mat_gc)
        if coll and node.name not in coll.objects:
            coll.objects.link(node)
        node_objects.append(node)

    return root, node_objects


def generate_scene(recipe=None, keep_scene=False):
    """Master generation and staging function for the RR-10 Murine Neural Proxy.

    Args:
        recipe (dict | str, optional): Parameter dictionary, recipe path, or raw benchmark data path.
        keep_scene (bool): If True, preserves existing scene elements.

    Returns:
        list[bpy.types.Object]: Created procedural objects.
    """
    if recipe is not None:
        recipe = load_data_or_recipe(recipe)
    else:
        recipe = {}

    if not keep_scene:
        clear_scene()

    coll_name = "Antigravity_Simulation"
    if coll_name in bpy.data.collections:
        coll = bpy.data.collections[coll_name]
    else:
        coll = bpy.data.collections.new(coll_name)
        bpy.context.scene.collection.children.link(coll)

    # 1. Build Murine Neural Core & Habitat Telemetry
    print(f"[generate_scene] Building RR-10 Murine Neural Proxy ({recipe.get('name', 'Murine Neural Proxy')})...")
    created_objects = build_murine_neural_scene(recipe, coll)

    # 1b. Build Subtle PCA Background Constellation Motif
    pca_root, pca_nodes = build_pca_background_constellation(coll)
    created_objects.extend([pca_root] + pca_nodes)

    # 2. Camera Auto-Framing
    print("[generate_scene] Auto-framing camera on murine neural axis...")
    setup_camera(target_objects=created_objects, recipe=recipe)

    # 3. Cinematic Spaceflight Lighting Rig
    print("[generate_scene] Staging cinematic spaceflight 3-point lighting...")
    setup_lighting(recipe=recipe)

    print(f"[generate_scene] Scene generated successfully ({len(created_objects)} objects created).")
    return created_objects


def parse_args():
    argv = sys.argv
    args_after_dash = argv[argv.index("--") + 1:] if "--" in argv else []
    parser = argparse.ArgumentParser(description="Antigravity RR-10 Murine Scene Generator")
    parser.add_argument(
        "--recipe", "--data",
        dest="recipe",
        type=str,
        default=os.path.join(PROJECT_ROOT, "data", "recipes", "default_simulation.json"),
        help="Path to recipe JSON or raw benchmark data JSON"
    )
    parser.add_argument(
        "--keep-scene",
        action="store_true",
        help="Preserve existing scene objects"
    )
    parser.add_argument(
        "--export",
        action="store_true",
        help="Automatically trigger GLB and metadata export after scene generation"
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Custom GLB output path if --export is set"
    )
    parser.add_argument(
        "--metadata-output",
        type=str,
        default=None,
        help="Custom metadata output path if --export is set"
    )
    return parser.parse_args(args_after_dash)


if __name__ == "__main__":
    args = parse_args()
    loaded_recipe = {}
    if args.recipe and os.path.exists(args.recipe):
        loaded_recipe = load_data_or_recipe(args.recipe)

    generate_scene(recipe=loaded_recipe, keep_scene=args.keep_scene)

    if args.export:
        from scripts.export_scene import export_scene
        export_scene(
            glb_path=args.output,
            metadata_path=args.metadata_output,
            recipe=loaded_recipe
        )
