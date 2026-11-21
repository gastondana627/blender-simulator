"""Blender Operators for Antigravity Simulator Add-on.

Directly bridges Blender UI interactions to the core scripts:
- scripts.generate_scene.generate_scene
- scripts.export_scene.export_scene
"""

import os
import sys
import bpy

# Ensure repository root is on sys.path
ADDON_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(ADDON_DIR))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from scripts.generate_scene import generate_scene
from scripts.generate_media_scene import generate_media_scene
from scripts.export_scene import export_scene


def _build_recipe_from_props(props):
    """Translates UI property group into a v3 murine_neural_proxy recipe dictionary."""
    return {
        "name": props.asset_name,
        "version": "3.0.0",
        "seed": props.seed,
        "generator": {
            "type": "murine_neural_proxy",
            "scale": props.scale,
            "core_radius": props.core_radius,
            "olfactory_scale": props.olfactory_scale,
            "cerebellar_scale": props.cerebellar_scale,
            "cage_radius": props.cage_radius,
            "asymmetry": props.asymmetry,
            "capillary_depth": props.capillary_depth,
            "rings_count": props.rings_count,
            "pods_per_ring": props.pods_per_ring,
            "wireframe_thickness": props.wireframe_thickness,
            "animation_frames": props.animation_frames,
            "breathing_amplitude": props.breathing_amplitude
        },
        "scene": {
            "fps": 30,
            "camera": {
                "focal_length": props.camera_focal_length
            }
        },
        "export": {
            "export_animations": props.export_animations,
            "export_materials": True,
            "apply_modifiers": True
        }
    }


def _resolve_metadata_path(glb_path):
    """Derives the paired metadata JSON path from the target GLB path."""
    base, _ = os.path.splitext(glb_path)
    return f"{base}.json"


class ANTIGRAVITY_OT_generate_scene(bpy.types.Operator):
    """Generate procedural asset, camera, and lighting in the current scene."""
    bl_idname = "antigravity.generate_scene"
    bl_label = "Generate Scene"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.scene.antigravity_props
        recipe = _build_recipe_from_props(props)

        try:
            objs = generate_scene(recipe=recipe, keep_scene=not props.clear_before_gen)
            self.report({'INFO'}, f"Generated procedural scene with {len(objs)} objects.")
            return {'FINISHED'}
        except Exception as e:
            self.report({'ERROR'}, f"Generation failed: {e}")
            return {'CANCELLED'}


class ANTIGRAVITY_OT_generate_media(bpy.types.Operator):
    """Generate the Astro-Mice Zero-G Odyssey media companion scene."""
    bl_idname = "antigravity.generate_media"
    bl_label = "Generate Media Companion"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.scene.antigravity_props
        try:
            generate_media_scene(keep_scene=not props.clear_before_gen)
            self.report({'INFO'}, "Generated Astro-Mice Zero-G Odyssey media scene.")
            return {'FINISHED'}
        except Exception as e:
            self.report({'ERROR'}, f"Media generation failed: {e}")
            return {'CANCELLED'}


class ANTIGRAVITY_OT_export_glb(bpy.types.Operator):
    """Export current scene to GLB and JSON metadata."""
    bl_idname = "antigravity.export_glb"
    bl_label = "Export GLB + Metadata"
    bl_options = {'REGISTER'}

    def execute(self, context):
        props = context.scene.antigravity_props
        recipe = _build_recipe_from_props(props)

        glb_path = os.path.join(PROJECT_ROOT, props.export_path)
        meta_path = _resolve_metadata_path(glb_path)

        try:
            final_glb, meta = export_scene(
                glb_path=glb_path,
                metadata_path=meta_path,
                recipe=recipe
            )
            self.report({'INFO'}, f"Exported: {os.path.basename(final_glb)} ({meta['export']['glb_size_kb']} KB)")
            return {'FINISHED'}
        except Exception as e:
            self.report({'ERROR'}, f"Export failed: {e}")
            return {'CANCELLED'}


class ANTIGRAVITY_OT_run_all(bpy.types.Operator):
    """Generate procedural scene and immediately export GLB and metadata."""
    bl_idname = "antigravity.run_all"
    bl_label = "Generate & Export All"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.scene.antigravity_props
        recipe = _build_recipe_from_props(props)

        glb_path = os.path.join(PROJECT_ROOT, props.export_path)
        meta_path = _resolve_metadata_path(glb_path)

        try:
            generate_scene(recipe=recipe, keep_scene=not props.clear_before_gen)
            final_glb, meta = export_scene(glb_path=glb_path, metadata_path=meta_path, recipe=recipe)
            self.report({'INFO'}, f"Pipeline complete: {os.path.basename(final_glb)} ({meta['export']['glb_size_kb']} KB)")
            return {'FINISHED'}
        except Exception as e:
            self.report({'ERROR'}, f"Pipeline failed: {e}")
            return {'CANCELLED'}


class ANTIGRAVITY_OT_generate_from_data(bpy.types.Operator):
    """Generate scene directly from a benchmark/notebook dataset JSON file."""
    bl_idname = "antigravity.generate_from_data"
    bl_label = "Generate from Dataset"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.scene.antigravity_props
        data_path = props.dataset_file
        if not os.path.isabs(data_path):
            data_path = os.path.join(PROJECT_ROOT, data_path)

        if not os.path.exists(data_path):
            self.report({'ERROR'}, f"Dataset file not found: {data_path}")
            return {'CANCELLED'}

        try:
            objs = generate_scene(recipe=data_path, keep_scene=not props.clear_before_gen)
            self.report({'INFO'}, f"Generated data-driven scene from {os.path.basename(data_path)} ({len(objs)} objects).")
            return {'FINISHED'}
        except Exception as e:
            self.report({'ERROR'}, f"Generation failed: {e}")
            return {'CANCELLED'}


classes = (
    ANTIGRAVITY_OT_generate_scene,
    ANTIGRAVITY_OT_generate_media,
    ANTIGRAVITY_OT_generate_from_data,
    ANTIGRAVITY_OT_export_glb,
    ANTIGRAVITY_OT_run_all,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
