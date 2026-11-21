#!/usr/bin/env python3
"""Public/Private Firewall Boundary Checker for blender-simulator.

Ensures private RR-10 v1.1 evaluation data, per-item payloads, raw provenance rows,
and credentials remain strictly quarantined inside private_eval/ and never enter
git tracking or public-facing directories (data/, exports/, web-viewer/, project-site/).
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

PUBLIC_SCAN_DIRS = ("data", "exports", "web-viewer", "project-site")
TEXT_EXTENSIONS = {
    ".json",
    ".js",
    ".mjs",
    ".cjs",
    ".html",
    ".htm",
    ".css",
    ".md",
    ".txt",
    ".py",
    ".yml",
    ".yaml",
    ".csv",
    ".tsv",
    ".svg",
}

# Build sensitive marker patterns programmatically to avoid self-matching
FRAG_ITEM_RE = re.compile(r"\bFRAG-\d{5}\b")
CTRL_ITEM_RE = re.compile(r"\bCTRL-\d{5}\b")
FORBIDDEN_LITERALS = (
    "private_" + "eval/",
    "benchmark_" + "full.jsonl",
    "FRAG-" + "00001",
    "CTRL-" + "00001",
)
# Indicators of leaked raw per-item provenance rows from the canonical JSONL
RAW_PROVENANCE_PATTERNS = (
    re.compile(r'"provenance"\s*:\s*\[\s*\{[^}]*"(?:osd|ensembl|gene_id|log2fc|log2FC_SF_vs_GC|log2FoldChange|padj|p_adj)"', re.IGNORECASE),
    re.compile(r'"log2FC_SF_vs_GC"\s*:'),
    re.compile(r'"item_id"\s*:\s*"(?:OSDR-)?(?:FRAG|CTRL)-\d{5}"'),
    re.compile(r'"id"\s*:\s*"OSDR-(?:FRAG|CTRL)-\d{5}"'),
    re.compile(r'"gold_label"\s*:\s*"(?:UP|DOWN|INDETERMINATE|CONCORDANT|FRAGILE)"', re.IGNORECASE),
)

FORBIDDEN_GIT_PATH_PATTERNS = (
    re.compile(r"(^|/)private_eval(/|$)"),
    re.compile(r"\.jsonl$", re.IGNORECASE),
    re.compile(r"(^|/)benchmark_full", re.IGNORECASE),
    re.compile(r"(^|/)\.env($|\.)", re.IGNORECASE),
    re.compile(r"\.env$", re.IGNORECASE),
    re.compile(r"(^|/)kaggle\.json$", re.IGNORECASE),
)


def run_git(repo_root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=str(repo_root),
        capture_output=True,
        text=True,
        check=False,
    )


def check_gitignore_enforcement(repo_root: Path) -> list[str]:
    errors: list[str] = []
    probes = [
        "private_eval/data/benchmark_full.jsonl",
        "private_eval/.env",
        "predictions.jsonl",
    ]
    for probe in probes:
        res = run_git(repo_root, "check-ignore", "-q", probe)
        if res.returncode != 0:
            errors.append(f"[GITIGNORE] Path is NOT ignored by git: {probe}")
    return errors


def check_git_paths(repo_root: Path) -> list[str]:
    errors: list[str] = []

    # 1. Check git status --porcelain (untracked non-ignored, modified, staged)
    status_res = run_git(repo_root, "status", "--porcelain", "-uall")
    if status_res.returncode != 0:
        errors.append(f"[GIT] `git status --porcelain` failed: {status_res.stderr.strip()}")
    else:
        for line in status_res.stdout.splitlines():
            if not line.strip():
                continue
            # Format: XY PATH or XY ORIG -> PATH
            path_part = line[3:].strip()
            if " -> " in path_part:
                path_part = path_part.split(" -> ", 1)[1].strip()
            path_part = path_part.strip('"')
            for pat in FORBIDDEN_GIT_PATH_PATTERNS:
                if pat.search(path_part):
                    errors.append(f"[GIT STATUS] Forbidden private path visible to git: {line}")
                    break

    # 2. Check git ls-files (already tracked or staged in index)
    ls_res = run_git(repo_root, "ls-files")
    if ls_res.returncode != 0:
        errors.append(f"[GIT] `git ls-files` failed: {ls_res.stderr.strip()}")
    else:
        for rel_path in ls_res.stdout.splitlines():
            rel_path = rel_path.strip()
            if not rel_path:
                continue
            for pat in FORBIDDEN_GIT_PATH_PATTERNS:
                if pat.search(rel_path):
                    errors.append(f"[GIT INDEX] Forbidden private path is tracked in git: {rel_path}")
                    break

    return errors


def scan_public_directories(repo_root: Path) -> list[str]:
    errors: list[str] = []
    for dirname in PUBLIC_SCAN_DIRS:
        base = repo_root / dirname
        if not base.exists():
            continue
        for root, dirs, files in os.walk(base):
            # Prune hidden/cache dirs
            dirs[:] = [d for d in dirs if d not in {".git", "__pycache__", "node_modules"}]
            for fname in files:
                fpath = Path(root) / fname
                rel = fpath.relative_to(repo_root).as_posix()

                # Block any .jsonl or benchmark_full file dropped into public dirs
                for pat in FORBIDDEN_GIT_PATH_PATTERNS:
                    if pat.search(rel):
                        errors.append(f"[PUBLIC DIR] Forbidden filename in public tree: {rel}")
                        break

                if fpath.suffix.lower() not in TEXT_EXTENSIONS:
                    continue

                try:
                    content = fpath.read_text(encoding="utf-8", errors="ignore")
                except OSError as exc:
                    errors.append(f"[PUBLIC DIR] Could not read {rel}: {exc}")
                    continue

                for literal in FORBIDDEN_LITERALS:
                    if literal in content:
                        errors.append(f"[CONTENT LEAK] Forbidden literal '{literal}' found in {rel}")

                if FRAG_ITEM_RE.search(content):
                    errors.append(f"[CONTENT LEAK] Private FRAG item ID pattern found in {rel}")
                if CTRL_ITEM_RE.search(content):
                    errors.append(f"[CONTENT LEAK] Private CTRL item ID pattern found in {rel}")

                for prov_re in RAW_PROVENANCE_PATTERNS:
                    if prov_re.search(content):
                        errors.append(f"[CONTENT LEAK] Raw provenance/item payload pattern found in {rel}")
                        break

    return errors


def run_boundary_check(repo_root: Path = REPO_ROOT) -> list[str]:
    errors: list[str] = []
    errors.extend(check_gitignore_enforcement(repo_root))
    errors.extend(check_git_paths(repo_root))
    errors.extend(scan_public_directories(repo_root))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify public/private firewall boundary for RR-10 v1.1 evaluation."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=REPO_ROOT,
        help="Repository root directory to audit (default: detected repo root).",
    )
    args = parser.parse_args()

    errors = run_boundary_check(args.repo_root.resolve())
    if errors:
        print("❌ PUBLIC/PRIVATE BOUNDARY CHECK FAILED:", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        return 1

    print("✅ PUBLIC/PRIVATE BOUNDARY CHECK PASSED (0 leaks, private_eval/ and *.jsonl quarantined).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
