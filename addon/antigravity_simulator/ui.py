"""UI Panel and Property definitions for Antigravity Blender Add-on."""

import bpy
from bpy.props import (
    StringProperty,
    IntProperty,
    FloatProperty,
    BoolProperty,
    PointerProperty
)


class AntigravitySceneProperties(bpy.types.PropertyGroup):
    """Configuration settings exposed in Blender 3D Viewport."""
    asset_name: StringProperty(
        name="Asset Name",
        default="Kinetic Gyroid Core"
    )
    seed: IntProperty(
        name="Random Seed",
        default=42,
        min=0
    )
    scale: FloatProperty(
        name="Scale",
        default=1.0,
        min=0.1,
        max=10.0
    )
    cage_radius: FloatProperty(
        name="Cage Radius",
        default=2.2,
        min=0.5,
        max=10.0
    )
    core_radius: FloatProperty(
        name="Core Radius",
        default=0.8,
        min=0.2,
        max=5.0
    )
    rings_count: IntProperty(
        name="Orbital Rings",
        default=3,
        min=1,
        max=6
    )
    subdivisions: IntProperty(
        name="Cage Subdivisions",
        default=3,
        min=1,
        max=5
    )
    wireframe_thickness: FloatProperty(
        name="Wireframe Thickness",
        default=0.04,
        min=0.005,
        max=0.5
    )
    breathing_amplitude: FloatProperty(
        name="Breathing Amplitude",
        default=0.15,
        min=0.0,
        max=1.0
    )
    animation_frames: IntProperty(
        name="Animation Frames",
        default=120,
        min=30,
        max=600
    )
    camera_focal_length: FloatProperty(
        name="Focal Length",
        default=55.0,
        min=15.0,
        max=200.0
    )
    clear_before_gen: BoolProperty(
        name="Clear Scene Before Gen",
        default=True
    )
    export_animations: BoolProperty(
        name="Export Animation Tracks",
        default=True
    )
    export_path: StringProperty(
        name="Export Path",
        default="exports/simulation.glb"
    )
    dataset_file: StringProperty(
        name="Dataset File",
        default="data/processed/sample_scene.json",
        subtype='FILE_PATH'
    )


class VIEW3D_PT_antigravity_panel(bpy.types.Panel):
    """Antigravity Simulator Sidebar Panel in 3D Viewport."""
    bl_label = "Antigravity Simulator"
    bl_idname = "VIEW3D_PT_antigravity_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Antigravity'

    def draw(self, context):
        layout = self.layout
        props = context.scene.antigravity_props

        # Section A: Dataset-Driven Adapter
        data_box = layout.box()
        data_box.label(text="Dataset-to-Scene Adapter", icon='FILE_SCRIPT')
        data_box.prop(props, "dataset_file", text="")
        data_box.operator("antigravity.generate_from_data", text="Generate from Dataset", icon='FORCE_DRAG')

        layout.separator()

        # Section B: Media Companion Mode (Storytelling)
        media_box = layout.box()
        media_box.label(text="Media Companion Mode", icon='COMMUNITY')
        media_box.operator("antigravity.generate_media", text="Generate Astro-Mouse (Pip)", icon='OUTLINER_OB_ARMATURE')

        layout.separator()

        # Section C: Manual / Procedural Controls
        header = layout.box()
        header.label(text="Procedural Parameters", icon='SHADERFX')
        header.prop(props, "asset_name", text="")

        col = layout.column(align=True)
        col.prop(props, "seed")
        col.prop(props, "scale")
        col.prop(props, "cage_radius")
        col.prop(props, "core_radius")
        col.prop(props, "rings_count")
        col.prop(props, "wireframe_thickness")
        col.prop(props, "breathing_amplitude")
        col.prop(props, "animation_frames")

        layout.separator()

        # Action 1: Generate Manual
        gen_box = layout.box()
        gen_box.prop(props, "clear_before_gen")
        gen_box.operator("antigravity.generate_scene", text="Generate Scene", icon='MESH_ICOSPHERE')

        layout.separator()

        # Action 2: Export
        exp_box = layout.box()
        exp_box.label(text="Export Pipeline", icon='EXPORT')
        exp_box.prop(props, "export_path", text="")
        exp_box.prop(props, "export_animations")
        exp_box.operator("antigravity.export_glb", text="Export GLB + Metadata", icon='FILE_3D')

        layout.separator()

        # Action 3: All-in-one
        layout.operator("antigravity.run_all", text="Generate & Export All", icon='PLAY')


classes = (
    AntigravitySceneProperties,
    VIEW3D_PT_antigravity_panel,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.antigravity_props = PointerProperty(type=AntigravitySceneProperties)


def unregister():
    del bpy.types.Scene.antigravity_props
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
