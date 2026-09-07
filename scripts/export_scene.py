"""Scene Export Module for Blender.

Can be run:
1. Headless CLI:
   blender -b --python scripts/export_scene.py -- --output exports/simulation.glb
2. Imported as a module:
   from scripts.export_scene import export_scene
   export_scene(glb_path, metadata_path, recipe)
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone

# Ensure repository root is on sys.path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import bpy
from mathutils import Vector


def export_glb_binary(filepath, recipe=None):
    """Exports the scene to a binary GLTF (.glb) file."""
    if recipe is None:
        recipe = {}

    exp_cfg = recipe.get("export", {})
    abs_path = os.path.abspath(filepath)
    os.makedirs(os.path.dirname(abs_path), exist_ok=True)

    export_kwargs = {
        "filepath": abs_path,
        "check_existing": False,
        "export_format": 'GLB',
        "export_apply": exp_cfg.get("apply_modifiers", True),
        "export_animations": exp_cfg.get("export_animations", True),
        "export_materials": 'EXPORT' if exp_cfg.get("export_materials", True) else 'NONE',
        "export_cameras": False,
        "export_lights": False,
        "export_extras": True,
        "export_yup": True
    }

    print(f"[export_scene] Exporting GLB -> {abs_path}")
    bpy.ops.export_scene.gltf(**export_kwargs)

    if not os.path.exists(abs_path):
        raise RuntimeError(f"GLB export failed: file not found at {abs_path}")

    size_kb = round(os.path.getsize(abs_path) / 1024.0, 2)
    print(f"[export_scene] GLB export successful ({size_kb} KB)")
    return abs_path


def gather_and_save_metadata(filepath, recipe=None, glb_path=None):
    """Extracts evaluated scene telemetry and writes simulation.json."""
    if recipe is None:
        recipe = {}

    abs_path = os.path.abspath(filepath)
    os.makedirs(os.path.dirname(abs_path), exist_ok=True)

    mesh_objects = [obj for obj in bpy.context.scene.objects if obj.type == 'MESH']
    depsgraph = bpy.context.evaluated_depsgraph_get()

    total_verts = 0
    total_faces = 0
    object_summaries = []
    all_points = []
    materials_used = set()

    for obj in mesh_objects:
        eval_obj = obj.evaluated_get(depsgraph)
        eval_mesh = eval_obj.to_mesh()

        v_count = len(eval_mesh.vertices)
        f_count = len(eval_mesh.polygons)
        total_verts += v_count
        total_faces += f_count

        for corner in obj.bound_box:
            all_points.append(obj.matrix_world @ Vector(corner))

        for slot in obj.material_slots:
            if slot.material:
                materials_used.add(slot.material.name)

        object_summaries.append({
            "name": obj.name,
            "vertices": v_count,
            "faces": f_count,
            "modifiers": [m.name for m in obj.modifiers]
        })

        eval_obj.to_mesh_clear()

    if all_points:
        min_x = min(p.x for p in all_points)
        max_x = max(p.x for p in all_points)
        min_y = min(p.y for p in all_points)
        max_y = max(p.y for p in all_points)
        min_z = min(p.z for p in all_points)
        max_z = max(p.z for p in all_points)
        bbox = {
            "min": [round(min_x, 4), round(min_y, 4), round(min_z, 4)],
            "max": [round(max_x, 4), round(max_y, 4), round(max_z, 4)],
            "dimensions": [
                round(max_x - min_x, 4),
                round(max_y - min_y, 4),
                round(max_z - min_z, 4)
            ]
        }
    else:
        bbox = {"min": [0, 0, 0], "max": [0, 0, 0], "dimensions": [0, 0, 0]}

    scene = bpy.context.scene
    fps = scene.render.fps
    frame_count = max(scene.frame_end - scene.frame_start + 1, 1)

    glb_size_bytes = os.path.getsize(glb_path) if glb_path and os.path.exists(glb_path) else 0

    metadata = {
        "pipeline": "Antigravity-Blender Creative Simulator",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "blender_version": ".".join(str(v) for v in bpy.app.version),
        "recipe_name": recipe.get("name", "Procedural Asset"),
        "seed": recipe.get("seed", 0),
        "statistics": {
            "total_objects": len(mesh_objects),
            "total_vertices": total_verts,
            "total_faces": total_faces,
            "bounding_box": bbox
        },
        "animation": {
            "frame_start": scene.frame_start,
            "frame_end": scene.frame_end,
            "fps": fps,
            "total_frames": frame_count,
            "duration_seconds": round(frame_count / fps, 3)
        },
        "materials": sorted(list(materials_used)),
        "objects": object_summaries,
        "export": {
            "glb_path": glb_path,
            "glb_size_bytes": glb_size_bytes,
            "glb_size_kb": round(glb_size_bytes / 1024.0, 2)
        },
        "recipe_snapshot": recipe
    }

    with open(abs_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    print(f"[export_scene] Metadata saved -> {abs_path}")
    return metadata


def export_scene(glb_path=None, metadata_path=None, recipe=None):
    """Master export function for GLB model and scene telemetry metadata.

    Args:
        glb_path (str, optional): Target GLB path.
        metadata_path (str, optional): Target JSON metadata path.
        recipe (dict, optional): Active recipe.

    Returns:
        tuple[str, dict]: (exported_glb_path, metadata_dict)
    """
    if recipe is None:
        recipe = {}

    target_glb = glb_path or recipe.get("export", {}).get("glb_path", "exports/simulation.glb")
    if not os.path.isabs(target_glb):
        target_glb = os.path.join(PROJECT_ROOT, target_glb)

    target_meta = metadata_path or recipe.get("export", {}).get("metadata_path", "exports/simulation.json")
    if not os.path.isabs(target_meta):
        target_meta = os.path.join(PROJECT_ROOT, target_meta)

    # 1. Export GLB
    final_glb = export_glb_binary(target_glb, recipe=recipe)

    # 2. Export Metadata
    meta = gather_and_save_metadata(target_meta, recipe=recipe, glb_path=final_glb)

    print(f"\n[export_scene] Complete: {meta['recipe_name']}")
    print(f" -> GLB: {final_glb} ({meta['export']['glb_size_kb']} KB)")
    print(f" -> Meta: {target_meta}")
    return final_glb, meta


def parse_args():
    argv = sys.argv
    args_after_dash = argv[argv.index("--") + 1:] if "--" in argv else []
    parser = argparse.ArgumentParser(description="Antigravity Scene Exporter")
    parser.add_argument(
        "--output",
        type=str,
        default=os.path.join(PROJECT_ROOT, "exports", "simulation.glb"),
        help="Target GLB output path"
    )
    parser.add_argument(
        "--metadata",
        type=str,
        default=os.path.join(PROJECT_ROOT, "exports", "simulation.json"),
        help="Target metadata JSON output path"
    )
    parser.add_argument(
        "--recipe",
        type=str,
        default=None,
        help="Optional path to recipe JSON for metadata enrichment"
    )
    return parser.parse_args(args_after_dash)


if __name__ == "__main__":
    args = parse_args()
    loaded_recipe = {}
    if args.recipe and os.path.exists(args.recipe):
        with open(args.recipe, "r", encoding="utf-8") as f:
            loaded_recipe = json.load(f)

    export_scene(
        glb_path=args.output,
        metadata_path=args.metadata,
        recipe=loaded_recipe
    )
