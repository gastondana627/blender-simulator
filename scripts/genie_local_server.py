#!/usr/bin/env python3
"""
Local Static + Genie 4 Ephemeral Token Dev Server for Orbiting Minds.

Serves the repository statically on 127.0.0.1 and exposes the same
`/api/genie-session` and `/api/genie-stop` endpoints as Vercel Serverless
Functions using only the Python standard library (zero extra installs).

Security:
- Binds strictly to 127.0.0.1 (localhost only).
- Keeps GEMINI_API_KEY strictly server-side; returns only `{interactionId, authToken}`.
- Supports optional GENIE_ACCESS_CODE and stateless BYOK (`userApiKey`).
"""

import argparse
import hmac
import json
import os
import re
import socket
import sys
import urllib.error
import urllib.parse
import urllib.request
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GEMINI_API_BASE = "https://generativelanguage.googleapis.com/v1beta"
MODEL_ID = "genie-4"
INTERACTION_ID_RE = re.compile(r"^[A-Za-z0-9_.-]{4,128}$")
BLOCKED_HTTP_SEGMENTS = {".env", ".env.local", ".git", "private_eval"}


def _read_dotenv_values() -> dict[str, str]:
    """Read key=value pairs from private_eval/.env, .env, and .env.local (stdlib only)."""
    loaded: dict[str, str] = {}
    for rel_path in (os.path.join("private_eval", ".env"), ".env", ".env.local"):
        fpath = os.path.join(PROJECT_ROOT, rel_path)
        if not os.path.isfile(fpath):
            continue
        try:
            with open(fpath, "r", encoding="utf-8", errors="ignore") as fh:
                for raw_line in fh:
                    line = raw_line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    if line.startswith("export "):
                        line = line[7:].strip()
                    key, val = line.split("=", 1)
                    key = key.strip()
                    val = val.strip().strip('"').strip("'")
                    if key and val:
                        loaded[key] = val
        except OSError:
            continue
    return loaded


def _get_config_var(name: str) -> str:
    """Resolve config var from process env first, falling back to .env / .env.local."""
    env_val = os.environ.get(name, "").strip()
    if env_val:
        return env_val
    return _read_dotenv_values().get(name, "").strip()


def _extract_gemini_error(payload, fallback: str) -> str:
    first = payload[0] if isinstance(payload, list) and payload else payload
    if isinstance(first, dict):
        err_obj = first.get("error")
        if isinstance(err_obj, dict) and err_obj.get("message"):
            return str(err_obj["message"])
        if first.get("message"):
            return str(first["message"])
    return fallback


def _call_gemini_post(path: str, api_key: str, payload: dict) -> tuple[int, dict | list]:
    url = f"{GEMINI_API_BASE}{path}"
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "x-goog-api-key": api_key,
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=25) as resp:
            raw = resp.read().decode("utf-8")
            return resp.status, (json.loads(raw) if raw else {})
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="ignore")
        try:
            body = json.loads(raw) if raw else {}
        except Exception:
            body = {"error": {"message": raw or f"HTTP {exc.code}"}}
        return exc.code, body


class OrbitingMindsHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=PROJECT_ROOT, **kwargs)

    def _send_json(self, status: int, payload: dict) -> None:
        encoded = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def _read_json_body(self) -> dict:
        length = int(self.headers.get("Content-Length", "0") or 0)
        if length <= 0:
            return {}
        raw = self.rfile.read(min(length, 131072)).decode("utf-8", errors="ignore").strip()
        return json.loads(raw) if raw else {}

    def _resolve_api_key(self, body: dict) -> tuple[str | None, str | None, int, str]:
        user_key = str(body.get("userApiKey") or "").strip()
        if user_key:
            return user_key, "byok", 200, ""

        server_key = _get_config_var("GEMINI_API_KEY")
        if not server_key:
            return (
                None,
                None,
                503,
                "GEMINI_API_KEY is not set. Add GEMINI_API_KEY=... to .env at the repo root, export it in your shell, or paste it in BYOK below.",
            )

        access_code = _get_config_var("GENIE_ACCESS_CODE")
        if access_code:
            provided = str(body.get("passcode") or "").strip()
            if not hmac.compare_digest(provided, access_code):
                return None, None, 401, "Invalid or missing GENIE_ACCESS_CODE passcode."

        return server_key, "server", 200, ""

    def do_GET(self) -> None:
        parsed = urllib.parse.urlsplit(self.path)
        segments = [seg for seg in parsed.path.split("/") if seg]
        if any(seg in BLOCKED_HTTP_SEGMENTS or seg.startswith(".env") for seg in segments):
            self.send_error(404, "Not Found")
            return

        if parsed.path == "/api/genie-session":
            has_server_key = bool(_get_config_var("GEMINI_API_KEY"))
            requires_passcode = bool(_get_config_var("GENIE_ACCESS_CODE"))
            self._send_json(
                200,
                {
                    "model": MODEL_ID,
                    "apiVersion": "v1beta",
                    "serverKeyConfigured": has_server_key,
                    "requiresPasscode": requires_passcode,
                    "acceptsByok": True,
                    "localDevServer": True,
                    "estimatedCostPerSecUsd": 0.10,
                    "defaultDurationSec": 45,
                    "maxDurationSec": 90,
                    "hardLimitSec": 120,
                },
            )
            return

        if parsed.path == "/":
            self.send_response(307)
            self.send_header("Location", "/project-site/")
            self.end_headers()
            return

        super().do_GET()

    def do_POST(self) -> None:
        parsed = urllib.parse.urlsplit(self.path)
        if parsed.path not in ("/api/genie-session", "/api/genie-stop"):
            self._send_json(404, {"error": "Unknown API endpoint."})
            return

        try:
            body = self._read_json_body()
        except Exception:
            self._send_json(400, {"error": "Invalid JSON body."})
            return

        api_key, auth_mode, err_code, err_msg = self._resolve_api_key(body)
        if not api_key:
            self._send_json(err_code, {"error": err_msg})
            return

        if parsed.path == "/api/genie-stop":
            interaction_id = str(body.get("interactionId") or "").strip()
            if not INTERACTION_ID_RE.match(interaction_id):
                self._send_json(400, {"error": "Invalid or missing interactionId."})
                return
            status, resp = _call_gemini_post(
                f"/interactions/{urllib.parse.quote(interaction_id, safe='')}/cancel",
                api_key,
                {},
            )
            self._send_json(
                200 if 200 <= status < 300 else status,
                {"stopped": 200 <= status < 300, "interactionId": interaction_id, "detail": resp},
            )
            return

        # POST /api/genie-session -> create interaction + mint ephemeral auth_token
        try:
            status1, interaction = _call_gemini_post("/interactions", api_key, {"model": MODEL_ID})
            if not (200 <= status1 < 300) or not isinstance(interaction, dict) or not interaction.get("id"):
                msg = _extract_gemini_error(interaction, f"Failed to create interaction (HTTP {status1})")
                if status1 in (400, 403, 429):
                    msg += " (Paste a valid paid-tier Gemini API key from aistudio.google.com/api-keys in BYOK, or export GEMINI_API_KEY.)"
                self._send_json(status1 if 400 <= status1 < 600 else 502, {"error": msg})
                return

            interaction_id = interaction["id"]
            status2, token_resp = _call_gemini_post(
                f"/interactions/{urllib.parse.quote(interaction_id, safe='')}/auth_tokens",
                api_key,
                {},
            )
            if not (200 <= status2 < 300) or not isinstance(token_resp, dict) or not token_resp.get("auth_token"):
                msg = _extract_gemini_error(token_resp, f"Failed to mint auth_token (HTTP {status2})")
                self._send_json(status2 if 400 <= status2 < 600 else 502, {"error": msg})
                return

            self._send_json(
                200,
                {
                    "interactionId": interaction_id,
                    "authToken": token_resp["auth_token"],
                    "model": MODEL_ID,
                    "apiVersion": "v1beta",
                    "authMode": auth_mode,
                },
            )
        except Exception as exc:
            self._send_json(502, {"error": f"Upstream Gemini API error: {exc}"})


def pick_open_port(preferred: int) -> int:
    for candidate in range(preferred, preferred + 25):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                s.bind(("127.0.0.1", candidate))
                return candidate
            except OSError:
                continue
    raise RuntimeError(f"No open port found in range {preferred}-{preferred + 24}.")


def serve(preferred_port: int = 8080) -> None:
    port = pick_open_port(preferred_port)
    if port != preferred_port:
        print(f"[Orbiting Minds] Port {preferred_port} is busy; using open port {port}.")
    has_key = bool(_get_config_var("GEMINI_API_KEY"))
    print(f"[Orbiting Minds] Local server running on http://localhost:{port}/")
    print(f"  Project Site:        http://localhost:{port}/project-site/")
    print(f"  3D Technical Viewer: http://localhost:{port}/web-viewer/")
    print(f"  Pip 3D Companion:    http://localhost:{port}/web-viewer/index.html?branch=media")
    print(f"  Pip Genie 4 World:   http://localhost:{port}/web-viewer/pip-world.html")
    print(f"  Genie 4 API key:     {'DETECTED (server-side)' if has_key else 'NOT SET (BYOK mode available)'}")
    server = ThreadingHTTPServer(("127.0.0.1", port), OrbitingMindsHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[Orbiting Minds] Server stopped.")
    finally:
        server.server_close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Local static + Genie 4 dev server for Orbiting Minds")
    parser.add_argument("--port", type=int, default=8080, help="Preferred localhost port (default: 8080)")
    args = parser.parse_args()
    try:
        serve(args.port)
    except RuntimeError as err:
        print(f"Error: {err}", file=sys.stderr)
        sys.exit(1)
