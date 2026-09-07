"""Reusable PBR material creation utilities compatible with Blender 4.x."""

import bpy


def set_socket_value(node, socket_names, value):
    """Safely set a socket value on a shader node across different Blender versions.

    Args:
        node (bpy.types.Node): Shader node (e.g. Principled BSDF).
        socket_names (list[str]): Candidate input socket names.
        value: Value to set (color, float, etc.).
    """
    if not node:
        return
    for name in socket_names:
        if name in node.inputs:
            try:
                node.inputs[name].default_value = value
                return
            except Exception:
                pass


def create_pbr_material(name, base_color=(0.8, 0.8, 0.8, 1.0), metallic=0.0,
                        roughness=0.5, emission_color=(0, 0, 0, 1),
                        emission_strength=0.0, specular=0.5,
                        subsurface_weight=0.0, subsurface_radius=(1.0, 0.4, 0.2)):
    """Creates a Principled BSDF material configured for Blender 4.x."""
    if name in bpy.data.materials:
        mat = bpy.data.materials[name]
    else:
        mat = bpy.data.materials.new(name=name)

    mat.use_nodes = True
    tree = mat.node_tree
    bsdf = tree.nodes.get("Principled BSDF")

    if bsdf:
        set_socket_value(bsdf, ["Base Color"], base_color)
        set_socket_value(bsdf, ["Metallic"], metallic)
        set_socket_value(bsdf, ["Roughness"], roughness)
        set_socket_value(bsdf, ["Emission Color", "Emission"], emission_color)
        set_socket_value(bsdf, ["Emission Strength"], emission_strength)
        set_socket_value(bsdf, ["Specular IOR Level", "Specular"], specular)
        set_socket_value(bsdf, ["Subsurface Weight", "Subsurface"], subsurface_weight)
        set_socket_value(bsdf, ["Subsurface Radius"], subsurface_radius)

    return mat


def create_murine_neural_clay_material(name="Mat_Murine_Neural_Tissue",
                                       base_color=(0.68, 0.52, 0.45, 1.0),
                                       roughness=0.55,
                                       emission_color=(0.85, 0.25, 0.12, 1.0),
                                       emission_strength=0.08,
                                       subsurface_weight=0.35):
    """Creates organic murine neural tissue / sculpting clay material with subsurface warmth and subtle microvascular blush."""
    return create_pbr_material(
        name=name,
        base_color=base_color,
        metallic=0.01,
        roughness=roughness,
        emission_color=emission_color,
        emission_strength=emission_strength,
        specular=0.45,
        subsurface_weight=subsurface_weight,
        subsurface_radius=(1.0, 0.35, 0.18)
    )


def create_hippocampal_core_material(name="Mat_Hippocampal_Core",
                                     emission_color=(0.0, 0.95, 1.0, 1.0),
                                     emission_strength=4.5):
    """Creates luminous synaptic / neurogenesis core material radiating from deep sagittal fissure."""
    return create_pbr_material(
        name=name,
        base_color=(0.02, 0.12, 0.18, 1.0),
        metallic=0.1,
        roughness=0.15,
        emission_color=emission_color,
        emission_strength=emission_strength,
        specular=0.8
    )


def create_flight_telemetry_hull_material(name="Mat_Flight_Telemetry_Hull",
                                          base_color=(0.11, 0.13, 0.17, 1.0),
                                          metallic=0.94,
                                          roughness=0.18):
    """Creates spaceflight-grade anodized titanium/beryllium alloy for habitat telemetry hulls."""
    return create_pbr_material(
        name=name,
        base_color=base_color,
        metallic=metallic,
        roughness=roughness,
        specular=0.75
    )


def create_bio_sensor_optic_material(name="Mat_BioSensor_Optic",
                                     emission_color=(0.0, 0.95, 1.0, 1.0),
                                     emission_strength=6.0):
    """Creates high-intensity telemetry optical/radiation sensor aperture material."""
    return create_pbr_material(
        name=name,
        base_color=(0.0, 0.04, 0.08, 1.0),
        metallic=0.15,
        roughness=0.1,
        emission_color=emission_color,
        emission_strength=emission_strength
    )


# =========================================================================
# MEDIA-MODE COMPANION SHADERS (Astro-Mouse "Commander Pip" & Habitat)
# =========================================================================

def create_eva_suit_material(name="Mat_EVA_Suit",
                             base_color=(0.93, 0.93, 0.95, 1.0),
                             roughness=0.72):
    """Creates clean matte-white composite space suit material for murine astronaut."""
    return create_pbr_material(
        name=name,
        base_color=base_color,
        metallic=0.02,
        roughness=roughness,
        specular=0.5,
        subsurface_weight=0.08,
        subsurface_radius=(0.5, 0.5, 0.5)
    )


def create_suit_harness_material(name="Mat_Suit_Harness",
                                 base_color=(0.88, 0.28, 0.04, 1.0),
                                 roughness=0.58):
    """Creates aerospace safety-orange webbing harness straps and accent bands."""
    return create_pbr_material(
        name=name,
        base_color=base_color,
        metallic=0.02,
        roughness=roughness,
        specular=0.45
    )


def create_gold_visor_material(name="Mat_Gold_Visor",
                               base_color=(1.0, 0.82, 0.35, 1.0),
                               transmission=0.82,
                               roughness=0.08):
    """Creates warm-gold tinted reflective bubble visor through which Pip's face is visible."""
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name=name)
    mat.use_nodes = True
    tree = mat.node_tree
    bsdf = tree.nodes.get("Principled BSDF")
    if bsdf:
        set_socket_value(bsdf, ["Base Color"], base_color)
        set_socket_value(bsdf, ["Metallic"], 0.18)
        set_socket_value(bsdf, ["Roughness"], roughness)
        set_socket_value(bsdf, ["IOR"], 1.45)
        set_socket_value(bsdf, ["Transmission Weight", "Transmission"], transmission)
        set_socket_value(bsdf, ["Specular IOR Level", "Specular"], 0.95)
    return mat


def create_mouse_tissue_material(name="Mat_Mouse_Tissue",
                                 base_color=(0.95, 0.65, 0.62, 1.0),
                                 roughness=0.42,
                                 subsurface_weight=0.55):
    """Creates warm organic ear and snout tissue with biological subsurface scattering."""
    return create_pbr_material(
        name=name,
        base_color=base_color,
        metallic=0.0,
        roughness=roughness,
        specular=0.5,
        subsurface_weight=subsurface_weight,
        subsurface_radius=(1.2, 0.6, 0.3)
    )


def create_mouse_fur_material(name="Mat_Mouse_Fur",
                              base_color=(0.93, 0.90, 0.84, 1.0),
                              roughness=0.82):
    """Creates stylized velvety cream/off-white murine fur with soft subsurface warmth."""
    return create_pbr_material(
        name=name,
        base_color=base_color,
        metallic=0.0,
        roughness=roughness,
        specular=0.35,
        subsurface_weight=0.22,
        subsurface_radius=(0.9, 0.6, 0.4)
    )


def create_metal_hardware_material(name="Mat_Metal_Hardware",
                                   base_color=(0.82, 0.84, 0.87, 1.0)):
    """Creates brushed aerospace silver/titanium for buckles, helmet rim, and fittings."""
    return create_pbr_material(
        name=name,
        base_color=base_color,
        metallic=0.88,
        roughness=0.24,
        specular=0.85
    )


def create_boot_sole_material(name="Mat_Boot_Sole",
                              base_color=(0.18, 0.19, 0.21, 1.0)):
    """Creates heavy-duty charcoal rubber boot tread material."""
    return create_pbr_material(
        name=name,
        base_color=base_color,
        metallic=0.05,
        roughness=0.88,
        specular=0.25
    )


def create_mouse_eye_material(name="Mat_Mouse_Eye",
                              base_color=(0.04, 0.04, 0.05, 1.0)):
    """Creates glossy dark mouse eye with sharp specular reflection."""
    return create_pbr_material(
        name=name,
        base_color=base_color,
        metallic=0.0,
        roughness=0.04,
        specular=0.98
    )


def create_whisker_material(name="Mat_Whisker",
                            base_color=(0.96, 0.94, 0.90, 0.85)):
    """Creates fine semi-translucent cream-white mouse whiskers."""
    return create_pbr_material(
        name=name,
        base_color=base_color,
        metallic=0.0,
        roughness=0.3,
        specular=0.8
    )


def create_ion_plume_material(name="Mat_Ion_Plume"):
    """Creates glowing cyan-white ion exhaust plume for attitude-control micro-thrusters."""
    return create_pbr_material(
        name=name,
        base_color=(0.3, 0.85, 1.0, 1.0),
        metallic=0.0,
        roughness=0.2,
        emission_color=(0.35, 0.88, 1.0, 1.0),
        emission_strength=4.5,
        specular=0.5
    )


def create_mission_patch_material(name="Mat_Mission_Patch"):
    """Creates dark mission shoulder patch with orange trajectory arc and star accents."""
    return create_pbr_material(
        name=name,
        base_color=(0.08, 0.09, 0.11, 1.0),
        metallic=0.05,
        roughness=0.6,
        specular=0.4
    )


def create_zero_g_bubble_material(name="Mat_ZeroG_Bubble"):
    """Creates refractive translucent nutrient or water droplet floating in microgravity."""
    if name in bpy.data.materials:
        mat = bpy.data.materials[name]
    else:
        mat = bpy.data.materials.new(name=name)

    mat.use_nodes = True
    tree = mat.node_tree
    bsdf = tree.nodes.get("Principled BSDF")

    if bsdf:
        set_socket_value(bsdf, ["Base Color"], (0.85, 0.94, 1.0, 1.0))
        set_socket_value(bsdf, ["Roughness"], 0.05)
        set_socket_value(bsdf, ["IOR"], 1.33)
        set_socket_value(bsdf, ["Transmission Weight", "Transmission"], 0.92)
        set_socket_value(bsdf, ["Specular IOR Level", "Specular"], 0.8)
        set_socket_value(bsdf, ["Emission Color", "Emission"], (0.2, 0.7, 1.0, 1.0))
        set_socket_value(bsdf, ["Emission Strength"], 0.4)

    return mat


def create_habitat_wall_material(name="Mat_Habitat_Wall",
                                 base_color=(0.88, 0.89, 0.92, 1.0)):
    """Creates padded white acoustic module wall panels with sleek aerospace finish."""
    return create_pbr_material(
        name=name,
        base_color=base_color,
        metallic=0.08,
        roughness=0.42,
        specular=0.5
    )


def create_earth_porthole_material(name="Mat_Earth_Porthole"):
    """Creates glowing curved Earth horizon disc seen through the observation porthole."""
    return create_pbr_material(
        name=name,
        base_color=(0.04, 0.12, 0.28, 1.0),
        metallic=0.05,
        roughness=0.2,
        emission_color=(0.12, 0.48, 0.85, 1.0),
        emission_strength=1.8,
        specular=0.7
    )


# =========================================================================
# PCA CONSTELLATION BACKGROUND MOTIF SHADERS
# =========================================================================

def create_pca_flt_material(name="Mat_PCA_FLT"):
    """Creates faint crimson emissive material for flight condition (FLT) PCA nodes."""
    return create_pbr_material(
        name=name,
        base_color=(0.88, 0.29, 0.29, 1.0),
        metallic=0.1,
        roughness=0.3,
        emission_color=(0.95, 0.35, 0.35, 1.0),
        emission_strength=1.5,
        specular=0.6
    )


def create_pca_gc_material(name="Mat_PCA_GC"):
    """Creates faint sky-blue emissive material for ground control (GC) PCA nodes."""
    return create_pbr_material(
        name=name,
        base_color=(0.23, 0.51, 0.96, 1.0),
        metallic=0.1,
        roughness=0.3,
        emission_color=(0.28, 0.62, 1.0, 1.0),
        emission_strength=1.5,
        specular=0.6
    )


