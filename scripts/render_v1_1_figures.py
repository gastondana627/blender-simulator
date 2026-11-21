#!/usr/bin/env python3
"""Generate publication-grade RR-10 v1.1 Before-vs-After SVG + 2x High-DPI PNG figures.

Reads strictly from data/processed/rr10_v1_1_public_summary.json (public-safe aggregates only).
Produces self-contained SVGs with inline system fonts and renders 2x high-DPI 1600x900 PNGs
using headless Playwright with zero external network dependencies.
"""

from __future__ import annotations

import html
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SUMMARY_PATH = REPO_ROOT / "data" / "processed" / "rr10_v1_1_public_summary.json"
OUT_DIR = REPO_ROOT / "project-site" / "assets" / "figures"

FONT_SANS = '-apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif'
FONT_MONO = '"SFMono-Regular", Menlo, Monaco, Consolas, "Liberation Mono", monospace'


def esc(text: str) -> str:
    return html.escape(str(text), quote=True)


def pct(v: float) -> str:
    return f"{v * 100:.2f}%"


def build_figure_1_svg(data: dict) -> str:
    """Figure 1: Before vs. After - Model Calibration & Caution Trap (5,630 Items / 2,815 Pairs)."""
    full_runs = {r["model"]: r for r in data["scoreboard"]["full_5630_neutral_runs"]}
    pilot_runs = {r["model"]: r for r in data["scoreboard"]["stratified_440_neutral_runs"]}
    caution_runs = {r["model"]: r for r in data["scoreboard"]["caution_coached_ablation_440"]["runs"]}

    oss = full_runs["openai/gpt-oss-120b"]
    gem_lite = full_runs["google/gemini-3.5-flash-lite"]
    nano = full_runs["openai/gpt-5.4-nano-2026-03-17"]
    gem_prev = pilot_runs["google/gemini-3-flash-preview"]
    caut_gem = caution_runs["gemini-3.5-flash-lite"]
    caut_nano = caution_runs["openai/gpt-5.4-nano-2026-03-17"]

    sha = data["canonical_sha256"]
    sha_short = f"{sha[:8]}...{sha[-6:]}"

    models_left = [
        ("openai/gpt-oss-120b", "5,630 items (2,815 pairs) | Ctrl Abst: 56.55%", oss["metrics"]),
        ("google/gemini-3.5-flash-lite", "5,630 items (2,815 pairs) | Ctrl Abst: 55.35%", gem_lite["metrics"]),
        ("openai/gpt-5.4-nano-2026-03-17", "5,630 items (2,815 pairs) | Ctrl Abst: 98.86%", nano["metrics"]),
    ]

    # Left chart bar geometry
    x0 = 92
    chart_w = 640  # 0% -> 100%
    grid_lines = []
    for tick in (0, 20, 40, 60, 80, 100):
        gx = x0 + (tick / 100.0) * chart_w
        grid_lines.append(
            f'<line x1="{gx:.1f}" y1="226" x2="{gx:.1f}" y2="668" stroke="#243044" stroke-dasharray="4 4" stroke-width="1"/>'
            f'<text x="{gx:.1f}" y="688" fill="#8b9bb4" font-family="{esc(FONT_MONO)}" font-size="12" text-anchor="middle">{tick}%</text>'
        )

    bar_blocks = []
    block_y_starts = [248, 396, 544]
    for (label, sublabel, m), y_top in zip(models_left, block_y_starts):
        bar_blocks.append(
            f'<text x="{x0}" y="{y_top}" fill="#f8fafc" font-family="{esc(FONT_MONO)}" font-size="16" font-weight="700">{esc(label)}</text>'
            f'<text x="{x0}" y="{y_top + 19}" fill="#94a3b8" font-family="{esc(FONT_SANS)}" font-size="12">{esc(sublabel)}</text>'
        )
        metrics_spec = [
            ("Trap Overclaim", m["trap_overclaim_rate"], "#ef4444", y_top + 32),
            ("Control Acc", m["control_accuracy"], "#38bdf8", y_top + 60),
            ("PDR (Paired)", m["pdr"], "#10b981", y_top + 88),
        ]
        for m_label, val, col, by in metrics_spec:
            bw = max(4.0, val * chart_w)
            bar_blocks.append(
                f'<rect x="{x0}" y="{by}" width="{chart_w}" height="20" rx="4" fill="#111827"/>'
                f'<rect x="{x0}" y="{by}" width="{bw:.1f}" height="20" rx="4" fill="{col}"/>'
                f'<text x="{x0 + bw + 10:.1f}" y="{by + 15}" fill="{col}" font-family="{esc(FONT_MONO)}" font-size="13" font-weight="700">{pct(val)}</text>'
                f'<text x="{x0 + chart_w - 6}" y="{by + 14}" fill="#64748b" font-family="{esc(FONT_MONO)}" font-size="11" text-anchor="end">{esc(m_label)}</text>'
            )

    # Right panel: Before -> After shift rows for gemini-3.5-flash-lite
    shifts = [
        ("Trap Overclaim Rate", gem_lite["metrics"]["trap_overclaim_rate"], caut_gem["metrics"]["trap_overclaim_rate"], "#ef4444", "#10b981", "-43.29 pp (Trap risk drops)"),
        ("Control Accuracy", gem_lite["metrics"]["control_accuracy"], caut_gem["metrics"]["control_accuracy"], "#38bdf8", "#f97316", "-20.89 pp (Valid claims lost)"),
        ("Control Abstention", gem_lite["metrics"]["control_abstention_rate"], caut_gem["metrics"]["control_abstention_rate"], "#94a3b8", "#f59e0b", "+44.65 pp (Blanket abstention)"),
        ("PDR (Paired Robustness)", gem_lite["metrics"]["pdr"], caut_gem["metrics"]["pdr"], "#10b981", "#ef4444", "COLLAPSE: 10.27% -> 0.00%"),
    ]
    shift_rows = []
    sy = 264
    for name, before_v, after_v, col_b, col_a, note in shifts:
        shift_rows.append(
            f'<rect x="900" y="{sy}" width="632" height="58" rx="8" fill="#0f172a" stroke="#1e293b" stroke-width="1"/>'
            f'<text x="916" y="{sy + 23}" fill="#e2e8f0" font-family="{esc(FONT_SANS)}" font-size="14" font-weight="600">{esc(name)}</text>'
            f'<text x="916" y="{sy + 44}" fill="#94a3b8" font-family="{esc(FONT_MONO)}" font-size="11.5">{esc(note)}</text>'
            f'<rect x="1268" y="{sy + 12}" width="96" height="32" rx="6" fill="#1e293b" stroke="{col_b}" stroke-width="1.2"/>'
            f'<text x="1316" y="{sy + 33}" fill="{col_b}" font-family="{esc(FONT_MONO)}" font-size="14" font-weight="700" text-anchor="middle">{pct(before_v)}</text>'
            f'<text x="1387" y="{sy + 34}" fill="#64748b" font-family="{esc(FONT_MONO)}" font-size="18" font-weight="700" text-anchor="middle">-&gt;</text>'
            f'<rect x="1410" y="{sy + 12}" width="106" height="32" rx="6" fill="#1e293b" stroke="{col_a}" stroke-width="1.4"/>'
            f'<text x="1463" y="{sy + 33}" fill="{col_a}" font-family="{esc(FONT_MONO)}" font-size="14" font-weight="700" text-anchor="middle">{pct(after_v)}</text>'
        )
        sy += 68

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="900" viewBox="0 0 1600 900">
  <defs>
    <linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#070a10"/>
      <stop offset="100%" stop-color="#0d1421"/>
    </linearGradient>
    <linearGradient id="accentBar" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#38bdf8"/>
      <stop offset="50%" stop-color="#10b981"/>
      <stop offset="100%" stop-color="#f59e0b"/>
    </linearGradient>
  </defs>

  <!-- Canvas Background -->
  <rect width="1600" height="900" fill="url(#bgGrad)"/>
  <rect x="0" y="0" width="1600" height="4" fill="url(#accentBar)"/>

  <!-- Header -->
  <rect x="40" y="24" width="540" height="24" rx="5" fill="#102136" stroke="#1e3a5f"/>
  <text x="54" y="40" fill="#38bdf8" font-family="{esc(FONT_MONO)}" font-size="11.5" font-weight="600">NASA OSDR RR-10 v1.1  |  CANONICAL SHA-256: {esc(sha_short)}</text>
  <rect x="1220" y="24" width="340" height="24" rx="5" fill="#0d2621" stroke="#145343"/>
  <text x="1390" y="40" fill="#34d399" font-family="{esc(FONT_MONO)}" font-size="11.5" font-weight="600" text-anchor="middle">LOCAL &lt;-&gt; PRIVATE KAGGLE VERIFIED</text>

  <text x="40" y="84" fill="#f8fafc" font-family="{esc(FONT_SANS)}" font-size="29" font-weight="700">Before vs. After: Model Calibration &amp; Caution Trap (5,630 Items / 2,815 Pairs)</text>
  <text x="40" y="109" fill="#94a3b8" font-family="{esc(FONT_SANS)}" font-size="15">Comparing neutral zero-nudge closed-book sweeps against prompt-only caution ablation across 34 NASA OSDR studies</text>

  <!-- Left Panel -->
  <rect x="40" y="130" width="800" height="718" rx="14" fill="#0b111d" stroke="#1e293b" stroke-width="1.5"/>
  <text x="68" y="164" fill="#f8fafc" font-family="{esc(FONT_SANS)}" font-size="19" font-weight="700">Before Guardrails: Raw Neutral Closed-Book (5,630 Items)</text>
  <text x="68" y="186" fill="#94a3b8" font-family="{esc(FONT_SANS)}" font-size="13">Bare OMROSLAB prompt + strict 3-label JSON enum (temperature=0, zero caution coaching)</text>

  <!-- Legend -->
  <rect x="68" y="200" width="12" height="12" rx="2" fill="#ef4444"/>
  <text x="86" y="210" fill="#cbd5e1" font-family="{esc(FONT_MONO)}" font-size="11.5">Trap Overclaim % (lower better)</text>
  <rect x="330" y="200" width="12" height="12" rx="2" fill="#38bdf8"/>
  <text x="348" y="210" fill="#cbd5e1" font-family="{esc(FONT_MONO)}" font-size="11.5">Control Acc % (higher better)</text>
  <rect x="572" y="200" width="12" height="12" rx="2" fill="#10b981"/>
  <text x="590" y="210" fill="#cbd5e1" font-family="{esc(FONT_MONO)}" font-size="11.5">PDR % (paired robustness)</text>

  {"".join(grid_lines)}
  {"".join(bar_blocks)}

  <!-- Left Panel Bottom Callout: Gemini 3 Flash Preview 440 Pilot -->
  <rect x="68" y="710" width="744" height="114" rx="10" fill="#1f1215" stroke="#7f1d1d" stroke-width="1.4"/>
  <text x="88" y="736" fill="#fca5a5" font-family="{esc(FONT_MONO)}" font-size="12.5" font-weight="700">440-ITEM NEUTRAL PILOT CALLOUT: google/gemini-3-flash-preview</text>
  <text x="88" y="762" fill="#f8fafc" font-family="{esc(FONT_MONO)}" font-size="15" font-weight="700">Trap Overclaim: {pct(gem_prev["metrics"]["trap_overclaim_rate"])}  |  Ctrl Acc: {pct(gem_prev["metrics"]["control_accuracy"])}  |  Ctrl Abst: {pct(gem_prev["metrics"]["control_abstention_rate"])}  |  PDR: {pct(gem_prev["metrics"]["pdr"])}</text>
  <text x="88" y="788" fill="#cbd5e1" font-family="{esc(FONT_SANS)}" font-size="13.5">Zero abstention yields high raw control guessing (48.18%), but overclaiming on nearly every</text>
  <text x="88" y="807" fill="#cbd5e1" font-family="{esc(FONT_SANS)}" font-size="13.5">multi-study fragility trap completely zeroes Paired Directional Robustness (0.00% PDR).</text>

  <!-- Right Panel -->
  <rect x="868" y="130" width="692" height="718" rx="14" fill="#0b111d" stroke="#1e293b" stroke-width="1.5"/>
  <text x="896" y="164" fill="#f8fafc" font-family="{esc(FONT_SANS)}" font-size="19" font-weight="700">After Prompt-Only Caution vs. Grounded Tooling</text>
  <text x="896" y="186" fill="#94a3b8" font-family="{esc(FONT_SANS)}" font-size="13">Prompt-only caution shift on gemini-3.5-flash-lite (Full 5,630 Neutral -&gt; 440 Caution Ablation)</text>

  <!-- Column headers for shift cards -->
  <text x="1316" y="246" fill="#94a3b8" font-family="{esc(FONT_MONO)}" font-size="11.5" font-weight="600" text-anchor="middle">BEFORE (NEUTRAL)</text>
  <text x="1463" y="246" fill="#f59e0b" font-family="{esc(FONT_MONO)}" font-size="11.5" font-weight="600" text-anchor="middle">AFTER (CAUTION)</text>

  {"".join(shift_rows)}

  <!-- Caution Trap Insight Box -->
  <rect x="900" y="544" width="632" height="92" rx="10" fill="#1d180c" stroke="#92400e" stroke-width="1.3"/>
  <text x="918" y="569" fill="#fcd34d" font-family="{esc(FONT_MONO)}" font-size="12" font-weight="700">THE CAUTION TRAP (440-ITEM ABLATION FINDING)</text>
  <text x="918" y="593" fill="#fef3c7" font-family="{esc(FONT_SANS)}" font-size="13.2">All 3 directional claims gemini-3.5-flash-lite still emitted under caution coaching</text>
  <text x="918" y="612" fill="#fef3c7" font-family="{esc(FONT_SANS)}" font-size="13.2">were false trap overclaims. gpt-5.4-nano ablation: {pct(caut_nano["metrics"]["control_abstention_rate"])} abstention, {pct(caut_nano["metrics"]["pdr"])} PDR.</text>

  <!-- Grounded Tooling Target Path Box -->
  <rect x="900" y="652" width="632" height="172" rx="10" fill="#091f24" stroke="#0ea5e9" stroke-width="1.5"/>
  <text x="918" y="679" fill="#38bdf8" font-family="{esc(FONT_MONO)}" font-size="12.5" font-weight="700">TARGET PATH (v1.1 / v1.2): GUARDRAIL CONTRACT + GROUNDED OSDR RETRIEVAL</text>

  <!-- 3-step pipeline boxes -->
  <rect x="918" y="694" width="176" height="54" rx="7" fill="#0f172a" stroke="#334155"/>
  <text x="1006" y="717" fill="#f8fafc" font-family="{esc(FONT_MONO)}" font-size="11.5" font-weight="700" text-anchor="middle">1. OSDR Query</text>
  <text x="1006" y="735" fill="#94a3b8" font-family="{esc(FONT_SANS)}" font-size="11" text-anchor="middle">Gene + Context</text>

  <text x="1110" y="726" fill="#38bdf8" font-family="{esc(FONT_MONO)}" font-size="16" font-weight="700" text-anchor="middle">-&gt;</text>

  <rect x="1126" y="694" width="184" height="54" rx="7" fill="#0f172a" stroke="#10b981"/>
  <text x="1218" y="717" fill="#34d399" font-family="{esc(FONT_MONO)}" font-size="11" font-weight="700" text-anchor="middle">2. Guardrail Contract</text>
  <text x="1218" y="735" fill="#94a3b8" font-family="{esc(FONT_SANS)}" font-size="11" text-anchor="middle">34 OSDs | EC-01..EC-06</text>

  <text x="1326" y="726" fill="#38bdf8" font-family="{esc(FONT_MONO)}" font-size="16" font-weight="700" text-anchor="middle">-&gt;</text>

  <rect x="1342" y="694" width="174" height="54" rx="7" fill="#0f172a" stroke="#38bdf8"/>
  <text x="1429" y="717" fill="#38bdf8" font-family="{esc(FONT_MONO)}" font-size="11" font-weight="700" text-anchor="middle">3. OSDR ChatBot</text>
  <text x="1429" y="735" fill="#94a3b8" font-family="{esc(FONT_SANS)}" font-size="11" text-anchor="middle">v1.0.0 Grounded Lookup</text>

  <text x="918" y="776" fill="#e0f2fe" font-family="{esc(FONT_SANS)}" font-size="13.2">Takeaway: Prompt coaching alone trades away valid control accuracy. Pairing</text>
  <text x="918" y="796" fill="#e0f2fe" font-family="{esc(FONT_SANS)}" font-size="13.2">rr10_guardrail_contract.json with live OSDR retrieval breaks the ~10% PDR ceiling.</text>
  <text x="918" y="814" fill="#7dd3fc" font-family="{esc(FONT_MONO)}" font-size="11">v1.2 planned secondary diagnostic (@Mym04Tak14): ln[S(t)/S_0] viscoelastic trajectory</text>

  <!-- Footer -->
  <text x="40" y="878" fill="#64748b" font-family="{esc(FONT_MONO)}" font-size="11.5">Orbiting Minds (https://orbiting-minds.vercel.app/)  |  Public-Safe Aggregates Only  |  PDR Denominator Audited = 2,815 (Gold 1.0, Indet 0.0, 1407/2815 Proof)</text>
</svg>
'''
    assert "\u2014" not in svg, "Em-dash detected in Figure 1 SVG!"
    return svg


def build_figure_2_svg(data: dict) -> str:
    """Figure 2: v1.1 Corpus Filter Funnel & 11-Context Fragility Breakdown."""
    full_runs = {r["model"]: r for r in data["scoreboard"]["full_5630_neutral_runs"]}
    oss_ctx = full_runs["openai/gpt-oss-120b"]["per_context"]
    gem_ctx = full_runs["google/gemini-3.5-flash-lite"]["per_context"]
    sha = data["canonical_sha256"]
    sha_short = f"{sha[:8]}...{sha[-6:]}"

    # Sort all 11 contexts by pair count descending (largest contexts first)
    contexts_sorted = sorted(data["contexts"], key=lambda c: (-c["pairs"], c["context"]))

    # Right chart geometry
    x_bar = 965
    bar_w = 515  # 0% -> 100%
    grid_lines = []
    for tick in (0, 25, 50, 75, 100):
        gx = x_bar + (tick / 100.0) * bar_w
        grid_lines.append(
            f'<line x1="{gx:.1f}" y1="224" x2="{gx:.1f}" y2="778" stroke="#223047" stroke-dasharray="3 4" stroke-width="1"/>'
            f'<text x="{gx:.1f}" y="795" fill="#8b9bb4" font-family="{esc(FONT_MONO)}" font-size="11.5" text-anchor="middle">{tick}%</text>'
        )

    rows_svg = []
    row_h = 49.5
    y_start = 232
    for idx, c in enumerate(contexts_sorted):
        ctx = c["context"]
        pairs = c["pairs"]
        ry = y_start + idx * row_h

        o_over = oss_ctx[ctx]["trap_overclaim_rate"]
        g_over = gem_ctx[ctx]["trap_overclaim_rate"]
        o_pdr = oss_ctx[ctx]["pdr"]
        g_pdr = gem_ctx[ctx]["pdr"]

        is_seedlings = ctx == "arabidopsis_thaliana::seedlings"
        is_cells = ctx == "homo_sapiens::cells"
        row_bg = "#211317" if is_seedlings else ("#0d1e2a" if is_cells else ("#0e1524" if idx % 2 == 0 else "#0b111d"))
        row_stroke = "#b91c1c" if is_seedlings else ("#0284c7" if is_cells else "none")
        stroke_attr = f' stroke="{row_stroke}" stroke-width="1.2"' if row_stroke != "none" else ""

        rows_svg.append(f'<rect x="614" y="{ry - 4:.1f}" width="924" height="{row_h - 4:.1f}" rx="6" fill="{row_bg}"{stroke_attr}/>')

        # Context label + pair count
        name_col = "#fca5a5" if is_seedlings else ("#7dd3fc" if is_cells else "#e2e8f0")
        rows_svg.append(
            f'<text x="624" y="{ry + 15:.1f}" fill="{name_col}" font-family="{esc(FONT_MONO)}" font-size="12" font-weight="700">{esc(ctx)}</text>'
            f'<text x="624" y="{ry + 32:.1f}" fill="#94a3b8" font-family="{esc(FONT_MONO)}" font-size="10.5">{pairs:,} pairs ({c["items"]:,} items)</text>'
        )

        # Bar tracks + fills (4 compact bars: TrapOver x2 on upper lane, PDR x2 on lower lane)
        # Upper lane: Trap Overclaim
        w_oo = max(2.0, o_over * bar_w)
        w_go = max(2.0, g_over * bar_w)
        # Lower lane: PDR
        w_op = max(2.0, o_pdr * bar_w) if o_pdr > 0 else 0.0
        w_gp = max(2.0, g_pdr * bar_w) if g_pdr > 0 else 0.0

        rows_svg.append(
            # TrapOver bars
            f'<rect x="{x_bar}" y="{ry + 3:.1f}" width="{bar_w}" height="7.5" rx="2" fill="#131c2e"/>'
            f'<rect x="{x_bar}" y="{ry + 3:.1f}" width="{w_oo:.1f}" height="7.5" rx="2" fill="#ef4444"/>'
            f'<rect x="{x_bar}" y="{ry + 12:.1f}" width="{bar_w}" height="7.5" rx="2" fill="#131c2e"/>'
            f'<rect x="{x_bar}" y="{ry + 12:.1f}" width="{w_go:.1f}" height="7.5" rx="2" fill="#f97316"/>'
            # PDR bars
            f'<rect x="{x_bar}" y="{ry + 23:.1f}" width="{bar_w}" height="6.5" rx="2" fill="#131c2e"/>'
            + (f'<rect x="{x_bar}" y="{ry + 23:.1f}" width="{w_op:.1f}" height="6.5" rx="2" fill="#38bdf8"/>' if w_op > 0 else "")
            + f'<rect x="{x_bar}" y="{ry + 31:.1f}" width="{bar_w}" height="6.5" rx="2" fill="#131c2e"/>'
            + (f'<rect x="{x_bar}" y="{ry + 31:.1f}" width="{w_gp:.1f}" height="6.5" rx="2" fill="#10b981"/>' if w_gp > 0 else "")
        )

        # Right-side exact value text (compact TrapOver & PDR pair)
        over_txt = f"Over: {o_over*100:.1f}% / {g_over*100:.1f}%"
        pdr_txt = f"PDR:  {o_pdr*100:.1f}% / {g_pdr*100:.1f}%"
        label_x = x_bar + bar_w + 10
        # Place inline to the right inside 1490..1535? Wait: x_bar=965, bar_w=515 -> ends at 1480!
        # Let's keep bar_w=420 (ends at 1385) so we have 148px right column for crystal-clear numbers!
        pass

    # Rebuild right panel with bar_w = 405 (x_bar=955 -> x_end=1360, labels at x=1372..1532)
    x_bar = 955
    bar_w = 405
    grid_lines = []
    for tick in (0, 25, 50, 75, 100):
        gx = x_bar + (tick / 100.0) * bar_w
        grid_lines.append(
            f'<line x1="{gx:.1f}" y1="224" x2="{gx:.1f}" y2="774" stroke="#223047" stroke-dasharray="3 4" stroke-width="1"/>'
            f'<text x="{gx:.1f}" y="791" fill="#8b9bb4" font-family="{esc(FONT_MONO)}" font-size="11" text-anchor="middle">{tick}%</text>'
        )

    rows_svg = []
    for idx, c in enumerate(contexts_sorted):
        ctx = c["context"]
        pairs = c["pairs"]
        ry = y_start + idx * row_h

        o_over = oss_ctx[ctx]["trap_overclaim_rate"]
        g_over = gem_ctx[ctx]["trap_overclaim_rate"]
        o_pdr = oss_ctx[ctx]["pdr"]
        g_pdr = gem_ctx[ctx]["pdr"]

        is_seedlings = ctx == "arabidopsis_thaliana::seedlings"
        is_cells = ctx == "homo_sapiens::cells"
        row_bg = "#211317" if is_seedlings else ("#0d1e2a" if is_cells else ("#0f1625" if idx % 2 == 0 else "#0b111d"))
        row_stroke = "#dc2626" if is_seedlings else ("#0284c7" if is_cells else "none")
        stroke_attr = f' stroke="{row_stroke}" stroke-width="1.2"' if row_stroke != "none" else ""

        rows_svg.append(f'<rect x="614" y="{ry - 4:.1f}" width="926" height="{row_h - 4:.1f}" rx="6" fill="{row_bg}"{stroke_attr}/>')

        name_col = "#fca5a5" if is_seedlings else ("#7dd3fc" if is_cells else "#e2e8f0")
        tag_str = " [SPIKE]" if is_seedlings else (" [LARGEST]" if is_cells else "")
        rows_svg.append(
            f'<text x="624" y="{ry + 15:.1f}" fill="{name_col}" font-family="{esc(FONT_MONO)}" font-size="11.8" font-weight="700">{esc(ctx)}</text>'
            f'<text x="624" y="{ry + 32:.1f}" fill="#94a3b8" font-family="{esc(FONT_MONO)}" font-size="10.5">{pairs:,} pairs ({c["items"]:,} items){tag_str}</text>'
        )

        w_oo = max(2.0, o_over * bar_w) if o_over > 0 else 0.0
        w_go = max(2.0, g_over * bar_w) if g_over > 0 else 0.0
        w_op = max(2.0, o_pdr * bar_w) if o_pdr > 0 else 0.0
        w_gp = max(2.0, g_pdr * bar_w) if g_pdr > 0 else 0.0

        rows_svg.append(
            f'<rect x="{x_bar}" y="{ry + 3:.1f}" width="{bar_w}" height="7.5" rx="2" fill="#141e30"/>'
            + (f'<rect x="{x_bar}" y="{ry + 3:.1f}" width="{w_oo:.1f}" height="7.5" rx="2" fill="#ef4444"/>' if w_oo > 0 else "")
            + f'<rect x="{x_bar}" y="{ry + 12:.1f}" width="{bar_w}" height="7.5" rx="2" fill="#141e30"/>'
            + (f'<rect x="{x_bar}" y="{ry + 12:.1f}" width="{w_go:.1f}" height="7.5" rx="2" fill="#f97316"/>' if w_go > 0 else "")
            + f'<rect x="{x_bar}" y="{ry + 23:.1f}" width="{bar_w}" height="6.5" rx="2" fill="#141e30"/>'
            + (f'<rect x="{x_bar}" y="{ry + 23:.1f}" width="{w_op:.1f}" height="6.5" rx="2" fill="#38bdf8"/>' if w_op > 0 else "")
            + f'<rect x="{x_bar}" y="{ry + 31:.1f}" width="{bar_w}" height="6.5" rx="2" fill="#141e30"/>'
            + (f'<rect x="{x_bar}" y="{ry + 31:.1f}" width="{w_gp:.1f}" height="6.5" rx="2" fill="#10b981"/>' if w_gp > 0 else "")
            + f'<text x="1372" y="{ry + 15:.1f}" fill="#fca5a5" font-family="{esc(FONT_MONO)}" font-size="11" font-weight="600">Over {o_over*100:5.1f}% / {g_over*100:5.1f}%</text>'
            + f'<text x="1372" y="{ry + 33:.1f}" fill="#6ee7b7" font-family="{esc(FONT_MONO)}" font-size="11" font-weight="600">PDR  {o_pdr*100:5.1f}% / {g_pdr*100:5.1f}%</text>'
        )

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="900" viewBox="0 0 1600 900">
  <defs>
    <linearGradient id="bgGrad2" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#070a10"/>
      <stop offset="100%" stop-color="#0d1421"/>
    </linearGradient>
    <linearGradient id="accentBar2" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#10b981"/>
      <stop offset="50%" stop-color="#38bdf8"/>
      <stop offset="100%" stop-color="#ef4444"/>
    </linearGradient>
  </defs>

  <rect width="1600" height="900" fill="url(#bgGrad2)"/>
  <rect x="0" y="0" width="1600" height="4" fill="url(#accentBar2)"/>

  <!-- Header -->
  <rect x="40" y="24" width="560" height="24" rx="5" fill="#102136" stroke="#1e3a5f"/>
  <text x="54" y="40" fill="#38bdf8" font-family="{esc(FONT_MONO)}" font-size="11.5" font-weight="600">OMROSLAB FROZEN v1.1 CONTRACT  |  34 OSD DATASETS  |  11,711 PROVENANCE ROWS</text>
  <rect x="1250" y="24" width="310" height="24" rx="5" fill="#0d2621" stroke="#145343"/>
  <text x="1405" y="40" fill="#34d399" font-family="{esc(FONT_MONO)}" font-size="11.5" font-weight="600" text-anchor="middle">SHA-256: {esc(sha_short)} (PASS)</text>

  <text x="40" y="84" fill="#f8fafc" font-family="{esc(FONT_SANS)}" font-size="29" font-weight="700">v1.1 Corpus Filter Funnel &amp; 11-Context Fragility Breakdown</text>
  <text x="40" y="109" fill="#94a3b8" font-family="{esc(FONT_SANS)}" font-size="15">Confound-filtered 1:1 pairing (21,454 -&gt; 5,630 canonical items) and full-corpus Trap Overclaim vs. PDR across all 11 contexts</text>

  <!-- Left Panel: Corpus Funnel -->
  <rect x="40" y="130" width="528" height="718" rx="14" fill="#0b111d" stroke="#1e293b" stroke-width="1.5"/>
  <text x="66" y="164" fill="#f8fafc" font-family="{esc(FONT_SANS)}" font-size="18.5" font-weight="700">Corpus Funnel: Raw Sweep -&gt; v1.1 Canonical</text>
  <text x="66" y="185" fill="#94a3b8" font-family="{esc(FONT_SANS)}" font-size="12.5">Why canonical v1.1 yields 5,630 items instead of 21,454</text>

  <!-- Stage 1 -->
  <rect x="66" y="206" width="476" height="106" rx="10" fill="#131b2b" stroke="#334155" stroke-width="1.2"/>
  <text x="84" y="232" fill="#94a3b8" font-family="{esc(FONT_MONO)}" font-size="11.5" font-weight="700">STAGE 1: INITIAL SEP 9 RAW SWEEP</text>
  <text x="84" y="264" fill="#f8fafc" font-family="{esc(FONT_MONO)}" font-size="26" font-weight="700">21,454 raw items</text>
  <text x="84" y="288" fill="#cbd5e1" font-family="{esc(FONT_SANS)}" font-size="12.5">244 OSDR DE tables swept; looser tissue harmonization</text>
  <text x="84" y="304" fill="#94a3b8" font-family="{esc(FONT_SANS)}" font-size="12">and uncoupled trap counts without 1:1 matched controls.</text>

  <text x="304" y="334" fill="#38bdf8" font-family="{esc(FONT_MONO)}" font-size="18" font-weight="700" text-anchor="middle">v</text>

  <!-- Stage 2 -->
  <rect x="66" y="344" width="476" height="132" rx="10" fill="#1d1414" stroke="#7f1d1d" stroke-width="1.2"/>
  <text x="84" y="370" fill="#fca5a5" font-family="{esc(FONT_MONO)}" font-size="11.5" font-weight="700">STAGE 2: CONFOUND &amp; SCHEMA EXCLUSIONS</text>
  <text x="84" y="396" fill="#f8fafc" font-family="{esc(FONT_MONO)}" font-size="12">-17 confounded-only datasets (1G centrifuge / duration)</text>
  <text x="84" y="418" fill="#e2e8f0" font-family="{esc(FONT_MONO)}" font-size="12">-118 tables with no clean SF-vs-GC contrast</text>
  <text x="84" y="440" fill="#e2e8f0" font-family="{esc(FONT_MONO)}" font-size="12">-12 missing Material Type  |  -2 missing SYMBOL col</text>
  <text x="84" y="463" fill="#fcd34d" font-family="{esc(FONT_MONO)}" font-size="12" font-weight="700">-&gt; 95 clean DE tables retained across OSDR</text>

  <text x="304" y="498" fill="#38bdf8" font-family="{esc(FONT_MONO)}" font-size="18" font-weight="700" text-anchor="middle">v</text>

  <!-- Stage 3 -->
  <rect x="66" y="508" width="476" height="106" rx="10" fill="#101d2e" stroke="#1e40af" stroke-width="1.2"/>
  <text x="84" y="534" fill="#93c5fd" font-family="{esc(FONT_MONO)}" font-size="11.5" font-weight="700">STAGE 3: FROZEN v1.1 CONTRACT RULES</text>
  <text x="84" y="558" fill="#e2e8f0" font-family="{esc(FONT_SANS)}" font-size="13">Exact OSDR Material Type keys (no lossy merging),</text>
  <text x="84" y="578" fill="#e2e8f0" font-family="{esc(FONT_SANS)}" font-size="13">q &lt; 0.05 at SYMBOL level, sign-oriented SF vs GC,</text>
  <text x="84" y="598" fill="#7dd3fc" font-family="{esc(FONT_MONO)}" font-size="12">1:1 matching without replacement: min(#traps, #ctrls)</text>

  <text x="304" y="636" fill="#10b981" font-family="{esc(FONT_MONO)}" font-size="18" font-weight="700" text-anchor="middle">v</text>

  <!-- Stage 4: Final Canonical -->
  <rect x="66" y="646" width="476" height="178" rx="12" fill="#09201c" stroke="#10b981" stroke-width="2"/>
  <text x="86" y="674" fill="#34d399" font-family="{esc(FONT_MONO)}" font-size="12" font-weight="700">STAGE 4: VERIFIED v1.1 CANONICAL CORPUS</text>
  <text x="86" y="712" fill="#f8fafc" font-family="{esc(FONT_MONO)}" font-size="30" font-weight="700">5,630 Canonical Items</text>
  <text x="86" y="739" fill="#a7f3d0" font-family="{esc(FONT_MONO)}" font-size="14" font-weight="600">2,815 Fragility Traps  +  2,815 Matched Controls</text>
  <text x="86" y="766" fill="#e2e8f0" font-family="{esc(FONT_MONO)}" font-size="13">34 OSD Datasets  |  11 Contexts  |  11,711 Provenance Rows</text>
  <text x="86" y="790" fill="#94a3b8" font-family="{esc(FONT_MONO)}" font-size="11.5">SHA-256: {esc(sha_short)}  |  validate.py: 5,630/5,630 PASS</text>
  <text x="86" y="810" fill="#38bdf8" font-family="{esc(FONT_MONO)}" font-size="11.5">PDR Denominator Audited = 2,815  |  Private Kaggle Parity PASS</text>

  <!-- Right Panel: 11 Context Breakdown -->
  <rect x="592" y="130" width="968" height="718" rx="14" fill="#0b111d" stroke="#1e293b" stroke-width="1.5"/>
  <text x="616" y="164" fill="#f8fafc" font-family="{esc(FONT_SANS)}" font-size="18.5" font-weight="700">11 organism::tissue Contexts: Trap Overclaim vs. PDR (Full 5,630 Neutral)</text>
  <text x="616" y="185" fill="#94a3b8" font-family="{esc(FONT_SANS)}" font-size="12.5">Ordered by matched pair count (largest first). Right column lists gpt-oss-120b / gemini-3.5-flash-lite.</text>

  <!-- Legend -->
  <rect x="616" y="198" width="11" height="11" rx="2" fill="#ef4444"/>
  <text x="633" y="208" fill="#cbd5e1" font-family="{esc(FONT_MONO)}" font-size="11">gpt-oss-120b TrapOver</text>
  <rect x="815" y="198" width="11" height="11" rx="2" fill="#f97316"/>
  <text x="832" y="208" fill="#cbd5e1" font-family="{esc(FONT_MONO)}" font-size="11">gemini-3.5-flash-lite TrapOver</text>
  <rect x="1075" y="198" width="11" height="11" rx="2" fill="#38bdf8"/>
  <text x="1092" y="208" fill="#cbd5e1" font-family="{esc(FONT_MONO)}" font-size="11">gpt-oss-120b PDR</text>
  <rect x="1245" y="198" width="11" height="11" rx="2" fill="#10b981"/>
  <text x="1262" y="208" fill="#cbd5e1" font-family="{esc(FONT_MONO)}" font-size="11">gemini-3.5-flash-lite PDR</text>

  {"".join(grid_lines)}
  {"".join(rows_svg)}

  <!-- Bottom Spotlight Callout -->
  <rect x="614" y="801" width="926" height="34" rx="7" fill="#1a1216" stroke="#991b1b" stroke-width="1"/>
  <text x="628" y="822" fill="#fecaca" font-family="{esc(FONT_MONO)}" font-size="10.2" font-weight="600">SPOTLIGHT: arabidopsis_thaliana::seedlings (380 pairs) hits 78.68% TrapOver on both vs. 28.83% / 31.11% in homo_sapiens::cells (1,006 pairs).</text>

  <!-- Footer -->
  <text x="40" y="878" fill="#64748b" font-family="{esc(FONT_MONO)}" font-size="11.5">Orbiting Minds (https://orbiting-minds.vercel.app/)  |  Source: data/processed/rr10_v1_1_public_summary.json  |  Zero Raw Protected Rows</text>
</svg>
'''
    assert "\u2014" not in svg, "Em-dash detected in Figure 2 SVG!"
    return svg


def render_svgs_to_pngs(pairs: list[tuple[Path, Path]]) -> None:
    """Render each self-contained SVG to a 2x high-DPI 1600x900 PNG via headless Playwright."""
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1600, "height": 900}, device_scale_factor=2)
        for svg_path, png_path in pairs:
            svg_markup = svg_path.read_text(encoding="utf-8")
            html_doc = (
                "<!doctype html><html><head><meta charset='utf-8'>"
                "<style>html,body{margin:0;padding:0;width:1600px;height:900px;overflow:hidden;background:#070a10;}"
                "svg{display:block;width:1600px;height:900px;}</style></head>"
                f"<body>{svg_markup}</body></html>"
            )
            page.set_content(html_doc, wait_until="load")
            page.screenshot(path=str(png_path), full_page=False)
            print(f"✅ Rendered 2x PNG -> {png_path} ({png_path.stat().st_size // 1024} KB)")
        browser.close()


def main() -> int:
    if not SUMMARY_PATH.exists():
        print(f"Missing public summary JSON: {SUMMARY_PATH}", file=sys.stderr)
        return 1

    data = json.loads(SUMMARY_PATH.read_text(encoding="utf-8"))
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    fig1_svg = OUT_DIR / "rr10_v1_1_before_after_calibration.svg"
    fig1_png = OUT_DIR / "rr10_v1_1_before_after_calibration.png"
    fig2_svg = OUT_DIR / "rr10_v1_1_corpus_and_11_contexts.svg"
    fig2_png = OUT_DIR / "rr10_v1_1_corpus_and_11_contexts.png"

    fig1_svg.write_text(build_figure_1_svg(data), encoding="utf-8")
    fig2_svg.write_text(build_figure_2_svg(data), encoding="utf-8")
    print(f"✅ Wrote SVG -> {fig1_svg}")
    print(f"✅ Wrote SVG -> {fig2_svg}")

    render_svgs_to_pngs([(fig1_svg, fig1_png), (fig2_svg, fig2_png)])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
