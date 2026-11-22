"""Unit tests for Orbiting Minds surgical pipeline fixes & public/private boundary firewall."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import types
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.check_public_boundary import run_boundary_check
from scripts.data_adapter import PALETTE_REGIMES, adapt_benchmark_to_recipe


def test_data_adapter_deterministic_sha256_seed():
    """Verify adapt_benchmark_to_recipe produces identical seeds across different PYTHONHASHSEED processes."""
    sample_path = REPO_ROOT / "data" / "processed" / "sample_scene.json"
    code = (
        "import json; from scripts.data_adapter import load_data_or_recipe; "
        f"print(load_data_or_recipe({str(sample_path)!r})['seed'])"
    )
    seeds = set()
    for hash_seed in ("1", "42", "999999"):
        env = dict(os.environ, PYTHONHASHSEED=hash_seed)
        proc = subprocess.run(
            [sys.executable, "-c", code],
            cwd=str(REPO_ROOT),
            env=env,
            capture_output=True,
            text=True,
            check=True,
        )
        seeds.add(int(proc.stdout.strip().splitlines()[-1]))
    assert len(seeds) == 1, f"Non-deterministic seed across hash seeds: {seeds}"


def test_data_adapter_includes_hippocampal_core_for_all_regimes():
    """Verify every mission regime includes hippocampal_core in recipe['materials']."""
    for regime in ("flight_adapted", "flight_optimal", "flight_stressed", "ground_control"):
        raw = {
            "run_id": f"test_{regime}",
            "experiment_name": f"Test {regime}",
            "metrics": {
                "adaptation_index": 0.9,
                "microvascular_stress": 0.1,
                "intracranial_volatility": 0.25,
                "transcriptomic_clusters": 3,
                "convergence_state": regime,
            },
        }
        recipe = adapt_benchmark_to_recipe(raw)
        assert "hippocampal_core" in recipe["materials"], f"Missing hippocampal_core for {regime}"
        assert recipe["materials"]["hippocampal_core"] == PALETTE_REGIMES[regime]["hippocampal_core"]


def test_lighting_honors_recipe_colors(monkeypatch):
    """Verify scripts/core/lighting.py applies key_color, fill_color, and rim_color from recipes."""

    class FakeLightData:
        def __init__(self, name):
            self.name = name
            self.energy = 0.0
            self.color = (0.0, 0.0, 0.0)
            self.size = 1.0

    class FakeConstraint:
        def __init__(self):
            self.target = None
            self.track_axis = ""
            self.up_axis = ""

    class FakeConstraints(list):
        def new(self, type):
            c = FakeConstraint()
            self.append(c)
            return c

    class FakeObject:
        def __init__(self, name, data):
            self.name = name
            self.data = data
            self.type = "LIGHT" if isinstance(data, FakeLightData) else "EMPTY"
            self.location = None
            self.constraints = FakeConstraints()

    class FakeCollectionObjects:
        def __init__(self):
            self.items = []

        def link(self, obj):
            self.items.append(obj)

    class FakeCollection:
        def __init__(self, name):
            self.name = name
            self.objects = FakeCollectionObjects()

    class FakeCollections(dict):
        def new(self, name):
            c = FakeCollection(name)
            self[name] = c
            return c

    class FakeObjects(list):
        def new(self, name, data):
            obj = FakeObject(name, data)
            self.append(obj)
            return obj

        def get(self, name):
            return None

        def remove(self, obj, do_unlink=True):
            self.remove(obj) if obj in self else None

    class FakeLights:
        def new(self, name, type):
            return FakeLightData(name)

    fake_bg = types.SimpleNamespace(
        inputs={
            "Color": types.SimpleNamespace(default_value=None),
            "Strength": types.SimpleNamespace(default_value=None),
        }
    )
    fake_world = types.SimpleNamespace(
        use_nodes=False,
        node_tree=types.SimpleNamespace(nodes={"Background": fake_bg}),
    )
    fake_scene = types.SimpleNamespace(
        world=fake_world,
        collection=types.SimpleNamespace(children=types.SimpleNamespace(link=lambda c: None)),
    )
    fake_bpy = types.SimpleNamespace(
        context=types.SimpleNamespace(scene=fake_scene),
        data=types.SimpleNamespace(
            objects=FakeObjects(),
            collections=FakeCollections(),
            lights=FakeLights(),
            worlds=types.SimpleNamespace(new=lambda name: fake_world),
        ),
    )
    fake_mathutils = types.SimpleNamespace(Vector=lambda v: tuple(v))

    monkeypatch.setitem(sys.modules, "bpy", fake_bpy)
    monkeypatch.setitem(sys.modules, "mathutils", fake_mathutils)
    sys.modules.pop("scripts.core.lighting", None)

    from scripts.core import lighting

    recipe = {
        "scene": {
            "lighting": {
                "key_color": [1.0, 0.96, 0.90],
                "fill_color": [0.25, 0.55, 0.95],
                "rim_color": [1.0, 0.85, 0.60],
                "key_intensity": 900.0,
                "fill_intensity": 420.0,
                "rim_intensity": 1400.0,
            }
        }
    }
    lights = lighting.setup_lighting(recipe=recipe)
    by_name = {l.name: l.data for l in lights}
    assert by_name["Light_Key"].color == (1.0, 0.96, 0.90)
    assert by_name["Light_Fill"].color == (0.25, 0.55, 0.95)
    assert by_name["Light_Rim"].color == (1.0, 0.85, 0.60)
    assert by_name["Light_Key"].energy == 900.0


def test_run_pipeline_discovers_vendor_build_pattern():
    """Verify run_pipeline.py includes vendor/build_* in Blender binary lookup."""
    src = (REPO_ROOT / "run_pipeline.py").read_text(encoding="utf-8")
    assert '"vendor", "build_*"' in src


def test_public_boundary_passes_on_repo():
    """Verify the active repository passes the public/private firewall cleanly."""
    errors = run_boundary_check(REPO_ROOT)
    assert errors == [], f"Boundary violations detected: {errors}"


def test_public_boundary_catches_leak(tmp_path: Path):
    """Verify check_public_boundary flags leaked private markers in public directories."""
    subprocess.run(["git", "init", "-q"], cwd=str(tmp_path), check=True)
    (tmp_path / ".gitignore").write_text("private_eval/\n*.jsonl\n.env\n", encoding="utf-8")
    leak_dir = tmp_path / "data" / "processed"
    leak_dir.mkdir(parents=True)
    (leak_dir / "leak.json").write_text(json.dumps({"id": "OSDR-" + "FRAG-" + "00001"}), encoding="utf-8")
    errors = run_boundary_check(tmp_path)
    assert errors, "Expected boundary checker to catch leaked FRAG item ID in data/processed/"


def test_recipes_use_v3_murine_schema():
    """Verify default_simulation.json and adapted_sample.json use the v3 murine_neural_proxy schema."""
    for rel in ("data/recipes/default_simulation.json", "data/recipes/adapted_sample.json"):
        recipe = json.loads((REPO_ROOT / rel).read_text(encoding="utf-8"))
        assert recipe["generator"]["type"] == "murine_neural_proxy", f"Legacy schema in {rel}"
        for mat_key in ("murine_clay", "hippocampal_core", "telemetry_hull", "sensor_optic"):
            assert mat_key in recipe["materials"], f"Missing material {mat_key} in {rel}"


def test_vercel_config_and_no_fabricated_osdr_id():
    """Verify vercel.json is valid JSON and web-viewer contains zero fabricated NASA-OSDR-RR10-B42 IDs."""
    vcfg = json.loads((REPO_ROOT / "vercel.json").read_text(encoding="utf-8"))
    assert vcfg["redirects"][0]["destination"] == "/project-site/"
    for rel in ("web-viewer/index.html", "web-viewer/app.js"):
        txt = (REPO_ROOT / rel).read_text(encoding="utf-8")
        assert "NASA-OSDR-RR10-B42" not in txt, f"Fabricated accession ID still present in {rel}"


def test_notebook_figures_json_has_all_20_pca_samples():
    """Verify single-source notebook_figures_data.json contains all 20 Figure A PCA samples."""
    data = json.loads((REPO_ROOT / "data" / "processed" / "notebook_figures_data.json").read_text(encoding="utf-8"))
    tissues = data["figure_a_pca"]["tissues"]
    assert len(tissues["cerebellum"]["samples"]) == 10
    assert len(tissues["hippocampus"]["samples"]) == 10


def _read_jpeg_dimensions(data: bytes) -> tuple[int, int]:
    """Read (width, height) from a baseline/progressive JPEG header using stdlib only."""
    assert data[:2] == b"\xff\xd8", "Not a valid JPEG file"
    idx = 2
    while idx < len(data):
        while idx < len(data) and data[idx] == 0xFF:
            idx += 1
        marker = data[idx]
        idx += 1
        if marker in (0xC0, 0xC1, 0xC2):
            height = int.from_bytes(data[idx + 3 : idx + 5], "big")
            width = int.from_bytes(data[idx + 5 : idx + 7], "big")
            return width, height
        seg_len = int.from_bytes(data[idx : idx + 2], "big")
        idx += seg_len
    raise AssertionError("JPEG SOF header not found")


def test_genie4_pip_world_assets_and_guardrails():
    """Verify Commander Pip Genie 4 WebRTC seed stays <48KB (16:9) and enforces billing/auth guardrails."""
    seed_path = REPO_ROOT / "web-viewer" / "assets" / "pip_genie_seed.jpg"
    assert seed_path.exists(), "Missing web-viewer/assets/pip_genie_seed.jpg"
    raw = seed_path.read_bytes()
    assert len(raw) < 48000, f"Seed JPEG ({len(raw)}B) exceeds 48 KB WebRTC SCTP limit"
    w, h = _read_jpeg_dimensions(raw)
    assert abs((w / h) - (16 / 9)) < 0.02, f"Seed image must be 16:9, got {w}x{h}"

    client_src = (REPO_ROOT / "web-viewer" / "pip-world.js").read_text(encoding="utf-8")
    assert "event_type: 'world_setup'" in client_src
    assert "reference_image" in client_src
    assert "session.complete()" in client_src
    assert "HIDDEN_TAB_AUTOSTOP_MS" in client_src
    assert "sendBeacon" in client_src

    session_api = (REPO_ROOT / "api" / "genie-session.js").read_text(encoding="utf-8")
    stop_api = (REPO_ROOT / "api" / "genie-stop.js").read_text(encoding="utf-8")
    world_html = (REPO_ROOT / "web-viewer" / "pip-world.html").read_text(encoding="utf-8")
    assert "GENIE_ACCESS_CODE" in session_api
    assert "GENIE_ENABLE_PROD" in session_api
    assert "GENIE_ENABLE_PROD" in stop_api
    assert "construction-tape-overlay" in world_html
    assert "applyComingSoonLock" in client_src
    assert "auth_tokens" in session_api
    assert "timingSafeEqual" in session_api
    assert "/cancel" in stop_api
    assert "AIzaSy" not in session_api and "AIzaSy" not in stop_api
