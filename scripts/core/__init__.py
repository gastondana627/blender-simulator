"""Core reusable utilities for Blender scene generation, materials, camera, and lighting."""
from .materials import (
    create_pbr_material,
    create_murine_neural_clay_material,
    create_hippocampal_core_material,
    create_flight_telemetry_hull_material,
    create_bio_sensor_optic_material,
    set_socket_value,
)
from .camera import setup_camera, compute_bounding_sphere
from .lighting import setup_lighting, setup_world_environment

__all__ = [
    "create_pbr_material",
    "create_murine_neural_clay_material",
    "create_hippocampal_core_material",
    "create_flight_telemetry_hull_material",
    "create_bio_sensor_optic_material",
    "set_socket_value",
    "setup_camera",
    "compute_bounding_sphere",
    "setup_lighting",
    "setup_world_environment",
]
