"""Dataset-to-Scene Adapter Layer for RR-10 Spaceflight Neurobiology.

Translates NASA GeneLab / Rodent Research-10 benchmark findings into
scientifically grounded, cinematic simulation recipes for the
Murine Neuro-Adaptation Proxy.
"""

import argparse
import json
import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Spaceflight Mission Palette Regimes
PALETTE_REGIMES = {
    "flight_adapted": {
        "murine_clay": {
            "base_color": [0.46, 0.32, 0.28, 1.0],
            "metallic": 0.01,
            "roughness": 0.55,
            "subsurface_weight": 0.35,
            "emission_color": [0.88, 0.26, 0.14, 1.0],
            "emission_strength": 0.04
        },
        "hippocampal_core": {
            "base_color": [0.02, 0.12, 0.18, 1.0],
            "emission_color": [0.0, 0.95, 1.0, 1.0],
            "emission_strength": 4.5
        },
        "telemetry_hull": {
            "base_color": [0.11, 0.13, 0.17, 1.0],
            "metallic": 0.94,
            "roughness": 0.18,
            "emission_color": [0.0, 0.85, 1.0, 1.0],
            "emission_strength": 0.5
        },
        "sensor_optic": {
            "base_color": [0.01, 0.05, 0.12, 1.0],
            "metallic": 0.2,
            "roughness": 0.1,
            "emission_color": [0.0, 0.95, 1.0, 1.0],
            "emission_strength": 6.5
        },
        "orbital_tracks": {
            "base_color": [0.78, 0.82, 0.88, 1.0],
            "metallic": 0.98,
            "roughness": 0.12,
            "emission_color": [0.0, 0.9, 0.85, 1.0],
            "emission_strength": 0.5
        },
        "telemetry_cage": {
            "base_color": [0.10, 0.12, 0.16, 1.0],
            "metallic": 0.92,
            "roughness": 0.3,
            "emission_color": [0.0, 0.8, 1.0, 1.0],
            "emission_strength": 0.25
        }
    },
    "flight_optimal": {
        "murine_clay": {
            "base_color": [0.50, 0.35, 0.30, 1.0],
            "metallic": 0.01,
            "roughness": 0.52,
            "subsurface_weight": 0.38,
            "emission_color": [0.82, 0.24, 0.12, 1.0],
            "emission_strength": 0.03
        },
        "hippocampal_core": {
            "base_color": [0.02, 0.14, 0.2, 1.0],
            "emission_color": [0.1, 0.98, 1.0, 1.0],
            "emission_strength": 5.0
        },
        "telemetry_hull": {
            "base_color": [0.12, 0.15, 0.2, 1.0],
            "metallic": 0.95,
            "roughness": 0.16,
            "emission_color": [0.0, 0.9, 1.0, 1.0],
            "emission_strength": 0.6
        },
        "sensor_optic": {
            "base_color": [0.02, 0.08, 0.15, 1.0],
            "metallic": 0.2,
            "roughness": 0.1,
            "emission_color": [0.1, 0.95, 1.0, 1.0],
            "emission_strength": 7.0
        },
        "orbital_tracks": {
            "base_color": [0.82, 0.86, 0.92, 1.0],
            "metallic": 0.98,
            "roughness": 0.1,
            "emission_color": [0.0, 0.95, 0.9, 1.0],
            "emission_strength": 0.6
        },
        "telemetry_cage": {
            "base_color": [0.08, 0.1, 0.14, 1.0],
            "metallic": 0.92,
            "roughness": 0.28,
            "emission_color": [0.0, 0.85, 1.0, 1.0],
            "emission_strength": 0.3
        }
    },
    "flight_stressed": {
        "murine_clay": {
            "base_color": [0.42, 0.26, 0.22, 1.0],
            "metallic": 0.01,
            "roughness": 0.60,
            "subsurface_weight": 0.25,
            "emission_color": [1.0, 0.25, 0.08, 1.0],
            "emission_strength": 0.10
        },
        "hippocampal_core": {
            "base_color": [0.2, 0.05, 0.02, 1.0],
            "emission_color": [1.0, 0.42, 0.1, 1.0],
            "emission_strength": 5.5
        },
        "telemetry_hull": {
            "base_color": [0.18, 0.13, 0.11, 1.0],
            "metallic": 0.88,
            "roughness": 0.24,
            "emission_color": [1.0, 0.3, 0.08, 1.0],
            "emission_strength": 0.6
        },
        "sensor_optic": {
            "base_color": [0.15, 0.04, 0.02, 1.0],
            "metallic": 0.15,
            "roughness": 0.12,
            "emission_color": [1.0, 0.32, 0.08, 1.0],
            "emission_strength": 6.5
        },
        "orbital_tracks": {
            "base_color": [0.55, 0.48, 0.45, 1.0],
            "metallic": 0.88,
            "roughness": 0.22,
            "emission_color": [1.0, 0.35, 0.1, 1.0],
            "emission_strength": 0.6
        },
        "telemetry_cage": {
            "base_color": [0.13, 0.09, 0.08, 1.0],
            "metallic": 0.85,
            "roughness": 0.35,
            "emission_color": [1.0, 0.35, 0.1, 1.0],
            "emission_strength": 0.3
        }
    },
    "ground_control": {
        "murine_clay": {
            "base_color": [0.48, 0.34, 0.28, 1.0],
            "metallic": 0.01,
            "roughness": 0.54,
            "subsurface_weight": 0.30,
            "emission_color": [0.08, 0.95, 0.62, 1.0],
            "emission_strength": 0.02
        },
        "hippocampal_core": {
            "base_color": [0.02, 0.15, 0.1, 1.0],
            "emission_color": [0.1, 0.98, 0.65, 1.0],
            "emission_strength": 4.2
        },
        "telemetry_hull": {
            "base_color": [0.1, 0.14, 0.15, 1.0],
            "metallic": 0.92,
            "roughness": 0.2,
            "emission_color": [0.1, 0.9, 0.6, 1.0],
            "emission_strength": 0.4
        },
        "sensor_optic": {
            "base_color": [0.02, 0.12, 0.08, 1.0],
            "metallic": 0.2,
            "roughness": 0.1,
            "emission_color": [0.1, 0.98, 0.65, 1.0],
            "emission_strength": 5.5
        },
        "orbital_tracks": {
            "base_color": [0.85, 0.85, 0.65, 1.0],
            "metallic": 0.96,
            "roughness": 0.15,
            "emission_color": [0.15, 0.9, 0.6, 1.0],
            "emission_strength": 0.5
        },
        "telemetry_cage": {
            "base_color": [0.1, 0.14, 0.12, 1.0],
            "metallic": 0.9,
            "roughness": 0.3,
            "emission_color": [0.15, 0.9, 0.6, 1.0],
            "emission_strength": 0.25
        }
    }
}

# Alias standard states to mission states
STATE_ALIASES = {
    "optimal": "flight_optimal",
    "converged": "flight_adapted",
    "volatile": "flight_stressed"
}


def is_raw_benchmark_data(data):
    """Detects whether a JSON object represents raw benchmark metrics or a scene recipe."""
    if not isinstance(data, dict):
        return False
    if "generator" in data and "materials" in data:
        return False
    if "metrics" in data or "experiment_name" in data or "mission" in data or "primary_score" in data:
        return True
    return False


def adapt_benchmark_to_recipe(benchmark_data):
    """Maps structured RR-10 spaceflight benchmark metrics into a simulation recipe.

    Args:
        benchmark_data (dict): Structured benchmark/notebook data.

    Returns:
        dict: Standardized Blender scene recipe for the murine neural proxy.
    """
    metrics = benchmark_data.get("metrics", {})
    run_id = benchmark_data.get("run_id", "rr10_run_default")
    exp_name = benchmark_data.get("experiment_name", "RR-10 Spaceflight Neuro-Adaptation")
    mission = benchmark_data.get("mission", "NASA Rodent Research-10")

    # Extract metrics with semantic spaceflight fallbacks
    score = float(metrics.get("adaptation_index", metrics.get("primary_score", 0.88)))
    loss = float(metrics.get("microvascular_stress", metrics.get("loss", 0.12)))
    volatility = float(metrics.get("intracranial_volatility", metrics.get("volatility", 0.25)))
    cluster_count = int(metrics.get("transcriptomic_clusters", metrics.get("cluster_count", 3)))
    raw_state = str(metrics.get("convergence_state", "flight_adapted")).lower()
    state = STATE_ALIASES.get(raw_state, raw_state)
    if state not in PALETTE_REGIMES:
        state = "flight_adapted"

    flight_days = int(metrics.get("flight_duration_days", 60))
    total_epochs = int(metrics.get("total_epochs", 150))

    # 1. Murine Anteroposterior Scale
    scale = round(0.85 + (score * 0.42), 3)
    core_radius = round(0.72 + (score * 0.26), 3)

    # 2. Murine Anatomical Proportions
    olfactory_scale = round(0.36 + (score * 0.12), 3)
    cerebellar_scale = round(0.48 + (score * 0.14), 3)
    asymmetry = round(1.0 + (volatility * 0.20), 3)

    # 3. Microvascular Remodeling & Capillary Fissures
    capillary_depth = round(0.08 + (loss * 0.22), 3)
    capillary_freq = round(max(0.28, 0.46 - (score * 0.14)), 3)

    # 4. Cephalic Fluid Shift & ICP Breathing Pulse
    fluid_shift_amp = round(max(0.06, min(0.32, volatility * 0.68)), 3)
    animation_frames = max(60, min(240, total_epochs))

    # 5. Habitat Telemetry Apparatus
    rings_count = max(2, min(5, cluster_count))
    probes_per_ring = 2 if cluster_count >= 3 else 1
    cage_radius = round(2.7 + (score * 0.4), 3)

    # 6. Material State
    palette = PALETTE_REGIMES.get(state, PALETTE_REGIMES["flight_adapted"])
    murine_mat = dict(palette["murine_clay"])
    # Synaptic / microvascular luminescence
    murine_mat["emission_strength"] = round(1.8 + (score * 4.2) - (loss * 2.2), 2)

    recipe = {
        "name": f"Murine Neural Proxy: {exp_name}",
        "version": "3.0.0",
        "mission_metadata": {
            "mission": mission,
            "run_id": run_id,
            "flight_subject": benchmark_data.get("flight_subject", "Mus musculus"),
            "flight_duration_days": flight_days,
            "adaptation_index": score,
            "microvascular_stress": loss,
            "intracranial_volatility": volatility,
            "mission_regime": state
        },
        "seed": abs(hash(run_id)) % 100000,
        "generator": {
            "type": "murine_neural_proxy",
            "scale": scale,
            "core_radius": core_radius,
            "olfactory_scale": olfactory_scale,
            "cerebellar_scale": cerebellar_scale,
            "cage_radius": cage_radius,
            "asymmetry": asymmetry,
            "capillary_depth": capillary_depth,
            "capillary_frequency": capillary_freq,
            "rings_count": rings_count,
            "pods_per_ring": probes_per_ring,
            "wireframe_thickness": 0.012,
            "animation_frames": animation_frames,
            "breathing_amplitude": fluid_shift_amp
        },
        "materials": {
            "murine_clay": murine_mat,
            "telemetry_hull": palette["telemetry_hull"],
            "sensor_optic": palette["sensor_optic"],
            "orbital_tracks": palette["orbital_tracks"],
            "telemetry_cage": palette["telemetry_cage"]
        },
        "scene": {
            "fps": 30,
            "frame_start": 1,
            "frame_end": animation_frames,
            "camera": {
                "focal_length": 55.0,
                "distance_multiplier": 2.7,
                "elevation_angle": 24.0,
                "azimuth_angle": 42.0
            },
            "lighting": {
                "preset": f"rr10_{state}",
                "key_intensity": round(820.0 + (score * 250.0), 1),
                "fill_intensity": 380.0,
                "rim_intensity": round(1150.0 + (score * 450.0), 1)
            }
        },
        "export": {
            "glb_path": "exports/simulation.glb",
            "metadata_path": "exports/simulation.json",
            "export_animations": True,
            "export_materials": True,
            "apply_modifiers": True
        }
    }

    return recipe


def load_data_or_recipe(input_source):
    """Loads a JSON file or dict, automatically adapting if it represents raw benchmark metrics."""
    if isinstance(input_source, str):
        if not os.path.exists(input_source):
            raise FileNotFoundError(f"Input configuration not found: {input_source}")
        with open(input_source, "r", encoding="utf-8") as f:
            data = json.load(f)
    elif isinstance(input_source, dict):
        data = input_source
    else:
        raise ValueError(f"Unsupported input type: {type(input_source)}")

    if is_raw_benchmark_data(data):
        print(f"[data_adapter] Adapting RR-10 spaceflight run: {data.get('run_id', 'unknown')}")
        return adapt_benchmark_to_recipe(data)

    return data


def main():
    parser = argparse.ArgumentParser(description="Antigravity RR-10 Dataset-to-Scene Adapter")
    parser.add_argument(
        "--input", "-i",
        type=str,
        required=True,
        help="Path to raw benchmark JSON or recipe"
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        default=None,
        help="Optional path to write the adapted recipe JSON"
    )

    args = parser.parse_args()
    recipe = load_data_or_recipe(args.input)

    if args.output:
        out_path = os.path.abspath(args.output)
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(recipe, f, indent=2)
        print(f"✨ Successfully wrote adapted RR-10 recipe to: {out_path}")
    else:
        print(json.dumps(recipe, indent=2))


if __name__ == "__main__":
    main()
