#!/usr/bin/env python3
"""Antigravity Orchestrator: Blender Pipeline Runner

Serves as the primary control layer between Antigravity and Blender:
- Dispatches headless or interactive Blender executions
- Selects target Blender runtime ($BLENDER_BIN, vendor/blender, /Applications/Blender.app)
- Supports granular stages: full pipeline, --generate-only, --export-only, --interactive
- Supports local web viewer serving
"""

import argparse
import glob
import os
import shutil
import subprocess
import sys
import time

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))


def find_blender_binary():
    """Locates the best available Blender executable.

    Priority:
    1. BLENDER_BIN environment variable
    2. Local compiled vendor/blender build
    3. macOS system application (/Applications/Blender.app)
    4. PATH lookup
    """
    # 1. User specified environment variable
    if os.environ.get("BLENDER_BIN"):
        candidate = os.path.expanduser(os.environ["BLENDER_BIN"])
        if os.path.isfile(candidate) and os.access(candidate, os.X_OK):
            return candidate

    # 2. Local vendor build directory (when custom compile succeeds)
    vendor_patterns = [
        os.path.join(PROJECT_ROOT, "vendor", "blender", "build_*", "bin", "Blender.app", "Contents", "MacOS", "Blender"),
        os.path.join(PROJECT_ROOT, "vendor", "blender", "build_*", "bin", "blender"),
        os.path.join(PROJECT_ROOT, "vendor", "blender", "bin", "blender"),
    ]
    for pattern in vendor_patterns:
        matches = glob.glob(pattern)
        if matches:
            for match in matches:
                if os.path.isfile(match) and os.access(match, os.X_OK):
                    return match

    # 3. macOS standard application installations
    mac_apps = [
        "/Applications/Blender.app/Contents/MacOS/Blender",
        os.path.expanduser("~/Applications/Blender.app/Contents/MacOS/Blender"),
    ]
    for app in mac_apps:
        if os.path.isfile(app) and os.access(app, os.X_OK):
            return app

    # 4. PATH lookup
    path_bin = shutil.which("blender")
    if path_bin:
        return path_bin

    return None


def run_blender_headless(blender_bin, script_path, script_args):
    """Executes a Blender Python script in background headless mode."""
    cmd = [blender_bin, "-b", "--python", script_path, "--"] + script_args

    print(f"\n[Antigravity Orchestrator] Executing Headless Blender:")
    print(f" Binary: {blender_bin}")
    print(f" Script: {os.path.relpath(script_path, PROJECT_ROOT)}")
    print(f" Args:   {' '.join(script_args)}\n")

    start_time = time.time()
    result = subprocess.run(cmd, cwd=PROJECT_ROOT)
    elapsed = time.time() - start_time

    if result.returncode == 0:
        print(f"\n✨ [Antigravity Orchestrator] Step completed in {elapsed:.2f}s!")
    else:
        print(f"\n❌ [Antigravity Orchestrator] Blender exited with error code {result.returncode}")
        sys.exit(result.returncode)


def run_blender_interactive(blender_bin, recipe=None, mode="technical"):
    """Launches Blender GUI with procedural scene generated upon startup."""
    if mode == "media":
        gen_script = os.path.join(PROJECT_ROOT, "scripts", "generate_media_scene.py")
    else:
        gen_script = os.path.join(PROJECT_ROOT, "scripts", "generate_scene.py")

    script_args = []
    if recipe:
        script_args.extend(["--recipe", recipe])

    cmd = [blender_bin, "--python", gen_script, "--"] + script_args

    print(f"\n[Antigravity Orchestrator] Launching Interactive Blender GUI ({mode.upper()} mode):")
    print(f" Binary: {blender_bin}")
    print(f" Script: {gen_script}\n")

    subprocess.Popen(cmd, cwd=PROJECT_ROOT)


def main():
    parser = argparse.ArgumentParser(description="Antigravity ↔ Blender Pipeline Orchestrator")
    parser.add_argument(
        "--mode",
        choices=["technical", "media"],
        default="technical",
        help="Simulation branch: 'technical' (RR-10 Murine Neural Core) or 'media' (Astro-Mice Companion)"
    )
    parser.add_argument(
        "--media",
        action="store_true",
        help="Shorthand for --mode media (Astro-Mice Zero-G Odyssey Companion)"
    )
    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="Launch interactive Blender GUI with the scene generated"
    )
    parser.add_argument(
        "--generate-only",
        action="store_true",
        help="Run procedural scene generation and staging only (no export)"
    )
    parser.add_argument(
        "--export-only",
        action="store_true",
        help="Run export module only on the currently staged scene"
    )
    parser.add_argument(
        "--recipe", "-r",
        type=str,
        default=None,
        help="Path to recipe JSON"
    )
    parser.add_argument(
        "--data", "-d",
        type=str,
        default=None,
        help="Path to raw benchmark/notebook output JSON (e.g. from data/processed/)"
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        default=None,
        help="Target GLB output path (defaults to simulation.glb or media_simulation.glb)"
    )
    parser.add_argument(
        "--metadata", "-m",
        type=str,
        default=None,
        help="Target metadata JSON output path"
    )
    parser.add_argument(
        "--blender-bin",
        type=str,
        default=None,
        help="Explicit path to Blender executable"
    )
    parser.add_argument(
        "--keep-scene",
        action="store_true",
        help="Preserve existing objects in the scene during generation"
    )
    parser.add_argument(
        "--serve",
        action="store_true",
        help="Start local HTTP server on port 8080 for the web-viewer"
    )

    args = parser.parse_args()

    if args.serve:
        print("[Antigravity] Starting local web server on port 8080...")
        print("Open: http://localhost:8080/web-viewer/")
        subprocess.run([sys.executable, "-m", "http.server", "8080"], cwd=PROJECT_ROOT)
        return

    # Determine simulation branch mode
    sim_mode = "media" if args.media or args.mode == "media" else "technical"

    blender_bin = args.blender_bin or find_blender_binary()
    if not blender_bin:
        print("❌ Error: Could not locate a working Blender executable.")
        print("Set BLENDER_BIN env var, specify --blender-bin, or install Blender in /Applications.")
        sys.exit(1)

    # Resolve mode-specific defaults
    if sim_mode == "media":
        gen_script = os.path.join(PROJECT_ROOT, "scripts", "generate_media_scene.py")
        default_recipe = os.path.join(PROJECT_ROOT, "data", "recipes", "media_astro_mouse.json")
        default_output = os.path.join(PROJECT_ROOT, "exports", "media_simulation.glb")
        default_metadata = os.path.join(PROJECT_ROOT, "exports", "media_simulation.json")
    else:
        gen_script = os.path.join(PROJECT_ROOT, "scripts", "generate_scene.py")
        default_recipe = os.path.join(PROJECT_ROOT, "data", "recipes", "default_simulation.json")
        default_output = os.path.join(PROJECT_ROOT, "exports", "simulation.glb")
        default_metadata = os.path.join(PROJECT_ROOT, "exports", "simulation.json")

    input_source = args.data or args.recipe or default_recipe
    output_path = args.output or default_output
    metadata_path = args.metadata or default_metadata

    # 1. Interactive Mode
    if args.interactive:
        run_blender_interactive(blender_bin, recipe=input_source, mode=sim_mode)
        return

    # 2. Headless Export Only
    if args.export_only:
        export_script = os.path.join(PROJECT_ROOT, "scripts", "export_scene.py")
        export_args = ["--output", output_path, "--metadata", metadata_path]
        if input_source:
            export_args.extend(["--recipe", input_source])
        run_blender_headless(blender_bin, export_script, export_args)
        return

    # 3. Headless Generate Only
    if args.generate_only:
        gen_args = ["--recipe", input_source]
        if args.keep_scene:
            gen_args.append("--keep-scene")
        run_blender_headless(blender_bin, gen_script, gen_args)
        return

    # 4. Full Pipeline (Generate + Export chained in single Blender session)
    pipeline_args = [
        "--recipe", input_source,
        "--export",
        "--output", output_path,
        "--metadata-output", metadata_path
    ]
    if args.keep_scene:
        pipeline_args.append("--keep-scene")

    run_blender_headless(blender_bin, gen_script, pipeline_args)


if __name__ == "__main__":
    main()
