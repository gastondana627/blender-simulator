#!/usr/bin/env python3
"""Render docs/Orbiting_Minds_RR10_Technical_Report_v1.1.pdf using Playwright Chromium.

Generates a print-ready, Zenodo-depositable US Letter academic PDF directly from
the public-safe aggregate JSON data and embedded high-DPI PNG figures, with zero
external network requests required.
"""

from __future__ import annotations

import base64
import html
import json
from pathlib import Path

from playwright.sync_api import sync_playwright

REPO_ROOT = Path(__file__).resolve().parent.parent
SUMMARY_PATH = REPO_ROOT / "data" / "processed" / "rr10_v1_1_public_summary.json"
CONTRACT_PATH = REPO_ROOT / "data" / "processed" / "rr10_guardrail_contract.json"
FIG_FUNNEL_PATH = REPO_ROOT / "project-site" / "assets" / "figures" / "rr10_v1_1_corpus_and_11_contexts.png"
FIG_CALIB_PATH = REPO_ROOT / "project-site" / "assets" / "figures" / "rr10_v1_1_before_after_calibration.png"
OUTPUT_PDF_PATH = REPO_ROOT / "docs" / "Orbiting_Minds_RR10_Technical_Report_v1.1.pdf"


def img_to_data_uri(path: Path) -> str:
    b64 = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{b64}"


def pct(val: float) -> str:
    return f"{val * 100:.2f}%"


def build_html() -> str:
    summary = json.loads(SUMMARY_PATH.read_text(encoding="utf-8"))
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    fig_funnel_uri = img_to_data_uri(FIG_FUNNEL_PATH)
    fig_calib_uri = img_to_data_uri(FIG_CALIB_PATH)

    runs_full = {r["model"]: r for r in summary["scoreboard"]["full_5630_neutral_runs"]}
    gpt_oss = runs_full["openai/gpt-oss-120b"]
    gem_lite = runs_full["google/gemini-3.5-flash-lite"]
    gpt_nano = runs_full["openai/gpt-5.4-nano-2026-03-17"]

    # Sort 11 contexts descending by pair count
    contexts_sorted = sorted(summary["contexts"], key=lambda c: c["pairs"], reverse=True)
    ctx_rows_html = []
    for c in contexts_sorted:
        key = c["context"]
        g_o = gpt_oss["per_context"][key]
        g_l = gem_lite["per_context"][key]
        g_n = gpt_nano["per_context"][key]
        spike_cls = ' class="highlight-row"' if key == "arabidopsis_thaliana::seedlings" else ""
        ctx_rows_html.append(
            f"<tr{spike_cls}>"
            f"<td><code>{html.escape(key)}</code></td>"
            f"<td class='num'>{c['items']:,}</td>"
            f"<td class='num'>{c['pairs']:,}</td>"
            f"<td class='num'>{pct(g_o['trap_overclaim_rate'])} / {pct(g_o['pdr'])}</td>"
            f"<td class='num'>{pct(g_l['trap_overclaim_rate'])} / {pct(g_l['pdr'])}</td>"
            f"<td class='num'>{pct(g_n['trap_overclaim_rate'])} / {pct(g_n['pdr'])}</td>"
            f"</tr>"
        )

    all_scoreboard_runs = [
        ("openai/gpt-oss-120b", "Full 5,630 Neutral", gpt_oss),
        ("google/gemini-3.5-flash-lite", "Full 5,630 Neutral", gem_lite),
        ("openai/gpt-5.4-nano-2026-03-17", "Full 5,630 Neutral", gpt_nano),
        (
            "google/gemini-3-flash-preview",
            "440 Neutral Pilot",
            summary["scoreboard"]["stratified_440_neutral_runs"][0],
        ),
        (
            "google/gemini-3.5-flash-lite",
            "440 Caution Ablation",
            summary["scoreboard"]["caution_coached_ablation_440"]["runs"][1],
        ),
        (
            "openai/gpt-5.4-nano-2026-03-17",
            "440 Caution Ablation",
            summary["scoreboard"]["caution_coached_ablation_440"]["runs"][0],
        ),
    ]
    score_rows_html = []
    for model_name, proto, r in all_scoreboard_runs:
        m = r["metrics"]
        t = r["telemetry"]
        ablation_cls = ' class="ablation-row"' if "Ablation" in proto else ""
        score_rows_html.append(
            f"<tr{ablation_cls}>"
            f"<td><code>{html.escape(model_name)}</code></td>"
            f"<td>{html.escape(proto)}</td>"
            f"<td class='num'>{r['n_items']:,} ({r['n_pairs']:,})</td>"
            f"<td class='num bold'>{pct(m['pdr'])}</td>"
            f"<td class='num'>{pct(m['trap_overclaim_rate'])}</td>"
            f"<td class='num'>{pct(m['control_accuracy'])}</td>"
            f"<td class='num'>{pct(m['control_abstention_rate'])}</td>"
            f"<td class='num'>{m['macro_f1']:.4f}</td>"
            f"<td class='num'>{t['avg_latency_ms']:,.1f} ms</td>"
            f"</tr>"
        )

    rule_rows_html = []
    for rule in contract["epistemic_caution_rules"]:
        sev = rule["severity"].upper()
        badge_cls = "sev-crit" if sev == "CRITICAL" else "sev-high"
        rule_rows_html.append(
            f"<tr>"
            f"<td class='center'><code>{html.escape(rule['id'])}</code></td>"
            f"<td class='center'><span class='sev-badge {badge_cls}'>{sev}</span></td>"
            f"<td>{html.escape(rule['rule'])}</td>"
            f"</tr>"
        )

    sha256 = summary["canonical_sha256"]

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Orbiting Minds and the RR-10 v1.1 Directional Fragility Audit (OM-TR-2026-01)</title>
  <style>
    @page {{
      size: letter;
      margin: 0.64in 0.65in 0.66in 0.65in;
    }}
    * {{
      box-sizing: border-box;
    }}
    body {{
      margin: 0;
      padding: 0;
      color: #141923;
      background: #ffffff;
      font-family: "Georgia", "Times New Roman", serif;
      font-size: 9.2pt;
      line-height: 1.41;
    }}
    h1, h2, h3, .sans, th, .meta-box, .kpi-grid, .sev-badge, .caption-label {{
      font-family: -apple-system, BlinkMacSystemFont, "Helvetica Neue", Arial, sans-serif;
    }}
    code, pre, .mono {{
      font-family: "SFMono-Regular", Menlo, Consolas, monospace;
      font-size: 7.9pt;
    }}
    code {{
      background: #f1f5f9;
      color: #0f172a;
      padding: 0.5px 3.5px;
      border-radius: 3px;
    }}
    th code {{
      background: rgba(255, 255, 255, 0.16);
      color: #f8fafc;
    }}
    a {{
      color: #0b57a4;
      text-decoration: none;
    }}

    /* Title Banner */
    .report-header {{
      border-top: 4px solid #0b2545;
      border-bottom: 1.5px solid #cbd5e1;
      padding: 10px 0 11px 0;
      margin-bottom: 11px;
    }}
    .report-kicker {{
      font-family: -apple-system, BlinkMacSystemFont, "Helvetica Neue", Arial, sans-serif;
      font-size: 7.4pt;
      font-weight: 700;
      letter-spacing: 1.05px;
      text-transform: uppercase;
      color: #c2410c;
      margin-bottom: 4px;
    }}
    h1.doc-title {{
      font-size: 15.2pt;
      line-height: 1.2;
      font-weight: 800;
      color: #0b192c;
      margin: 0 0 7px 0;
      letter-spacing: -0.015em;
    }}
    .author-line {{
      font-size: 9.6pt;
      font-weight: 600;
      color: #1e293b;
      margin-bottom: 2px;
    }}
    .affiliation-line {{
      font-size: 8.2pt;
      color: #475569;
      margin-bottom: 8px;
    }}
    .meta-grid {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 4px 14px;
      background: #f8fafc;
      border: 1px solid #dbe2ea;
      border-radius: 6px;
      padding: 7px 11px;
      font-family: -apple-system, BlinkMacSystemFont, "Helvetica Neue", Arial, sans-serif;
      font-size: 7.6pt;
      color: #334155;
    }}
    .meta-grid strong {{
      color: #0f172a;
    }}
    .sha-bar {{
      grid-column: 1 / -1;
      border-top: 1px dashed #cbd5e1;
      padding-top: 4px;
      margin-top: 1px;
      font-size: 7.4pt;
    }}

    /* Abstract Box */
    .abstract-box {{
      background: #f8fafc;
      border-left: 3.5px solid #0b57a4;
      padding: 9px 13px;
      margin: 0 0 11px 0;
      border-radius: 0 6px 6px 0;
      break-inside: avoid;
      page-break-inside: avoid;
    }}
    .abstract-box h2 {{
      margin: 0 0 4px 0;
      font-size: 8.8pt;
      text-transform: uppercase;
      letter-spacing: 0.7px;
      color: #0b57a4;
      border: none;
      padding: 0;
    }}
    .abstract-box p {{
      margin: 0 0 5px 0;
      font-size: 8.65pt;
      line-height: 1.38;
      text-align: justify;
    }}
    .abstract-box p:last-child {{
      margin-bottom: 0;
    }}
    .keywords {{
      font-family: -apple-system, BlinkMacSystemFont, "Helvetica Neue", Arial, sans-serif;
      font-size: 7.6pt;
      color: #475569;
      margin-top: 5px;
    }}

    /* KPI Strip */
    .kpi-grid {{
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 8px;
      margin: 8px 0 12px 0;
      break-inside: avoid;
      page-break-inside: avoid;
    }}
    .kpi-card {{
      background: #0f172a;
      color: #f8fafc;
      border-radius: 6px;
      padding: 8px 9px;
      border-top: 3px solid #ea580c;
      break-inside: avoid;
      page-break-inside: avoid;
    }}
    .kpi-card.cyan {{
      border-top-color: #0284c7;
    }}
    .kpi-card.green {{
      border-top-color: #059669;
    }}
    .kpi-card.amber {{
      border-top-color: #d97706;
    }}
    .kpi-val {{
      font-size: 12pt;
      font-weight: 800;
      line-height: 1.15;
    }}
    .kpi-lbl {{
      font-size: 7pt;
      color: #cbd5e1;
      margin-top: 3px;
      line-height: 1.24;
    }}

    /* Headings & Prose */
    h2 {{
      font-size: 11.1pt;
      font-weight: 800;
      color: #0b2545;
      border-bottom: 1.2px solid #cbd5e1;
      padding-bottom: 2.5px;
      margin: 13px 0 6px 0;
      page-break-after: avoid;
      break-after: avoid;
    }}
    h3 {{
      font-size: 9.4pt;
      font-weight: 700;
      color: #1e3a5f;
      margin: 9px 0 4px 0;
      page-break-after: avoid;
      break-after: avoid;
    }}
    p {{
      margin: 0 0 6px 0;
      text-align: justify;
    }}
    ul, ol {{
      margin: 3px 0 7px 0;
      padding-left: 17px;
    }}
    li {{
      margin-bottom: 3px;
    }}

    /* Tables */
    table {{
      width: 100%;
      border-collapse: collapse;
      margin: 6px 0 9px 0;
      font-size: 7.8pt;
      line-height: 1.3;
      page-break-inside: avoid;
      break-inside: avoid;
    }}
    thead {{
      display: table-header-group;
    }}
    th {{
      background: #0f172a;
      color: #f8fafc;
      font-weight: 700;
      text-align: left;
      padding: 4.5px 5.5px;
      border: 1px solid #1e293b;
      font-size: 7.25pt;
    }}
    td {{
      padding: 4px 5.5px;
      border: 1px solid #cbd5e1;
      vertical-align: top;
    }}
    tbody tr:nth-child(even) {{
      background: #f8fafc;
    }}
    tr.highlight-row {{
      background: #fff7ed !important;
      font-weight: 600;
    }}
    tr.ablation-row {{
      background: #fef2f2 !important;
    }}
    td.num, th.num {{
      text-align: right;
      font-variant-numeric: tabular-nums;
      white-space: nowrap;
    }}
    td.center, th.center {{
      text-align: center;
      white-space: nowrap;
    }}
    td.bold {{
      font-weight: 700;
    }}

    .sev-badge {{
      display: inline-block;
      padding: 1.5px 5px;
      border-radius: 3px;
      font-size: 6.7pt;
      font-weight: 700;
      letter-spacing: 0.4px;
    }}
    .sev-crit {{
      background: #fee2e2;
      color: #991b1b;
      border: 1px solid #fca5a5;
    }}
    .sev-high {{
      background: #fef3c7;
      color: #92400e;
      border: 1px solid #fcd34d;
    }}

    /* Figures */
    .figure-block {{
      margin: 7px 0 9px 0;
      padding: 7px;
      border: 1px solid #cbd5e1;
      border-radius: 6px;
      background: #f8fafc;
      page-break-inside: avoid;
      break-inside: avoid;
    }}
    .figure-block img {{
      width: 98%;
      margin: 0 auto;
      height: auto;
      display: block;
      border-radius: 4px;
      border: 1px solid #0f172a;
    }}
    .figure-caption {{
      margin-top: 5px;
      font-size: 7.75pt;
      line-height: 1.35;
      color: #334155;
      text-align: left;
    }}
    .caption-label {{
      font-weight: 700;
      color: #0b2545;
    }}

    /* Callouts & Pipeline Box */
    .pipeline-box {{
      background: #0f172a;
      color: #e2e8f0;
      border-radius: 6px;
      padding: 8px 11px;
      margin: 6px 0 8px 0;
      font-family: "SFMono-Regular", Menlo, Consolas, monospace;
      font-size: 7.45pt;
      line-height: 1.44;
      white-space: pre;
      page-break-inside: avoid;
      break-inside: avoid;
    }}
    .callout {{
      background: #fffbeb;
      border-left: 3.5px solid #d97706;
      padding: 7px 10px;
      margin: 6px 0 9px 0;
      border-radius: 0 5px 5px 0;
      font-size: 8.45pt;
      line-height: 1.38;
      page-break-inside: avoid;
      break-inside: avoid;
    }}
    .callout.blue {{
      background: #eff6ff;
      border-left-color: #1d4ed8;
    }}
    .formula-box {{
      text-align: center;
      font-family: "Georgia", serif;
      font-style: italic;
      font-size: 10pt;
      padding: 5px 10px;
      background: #f8fafc;
      border: 1px solid #cbd5e1;
      border-radius: 5px;
      margin: 5px auto 7px auto;
      width: 64%;
      page-break-inside: avoid;
      break-inside: avoid;
    }}

    /* References */
    .ref-list {{
      font-size: 7.6pt;
      line-height: 1.34;
      padding-left: 17px;
      margin-top: 5px;
    }}
    .ref-list li {{
      margin-bottom: 3.2px;
      text-align: left;
    }}
    .bibtex-box {{
      background: #f8fafc;
      border: 1px solid #cbd5e1;
      border-radius: 5px;
      padding: 7px 10px;
      font-family: "SFMono-Regular", Menlo, Consolas, monospace;
      font-size: 7pt;
      line-height: 1.35;
      white-space: pre-wrap;
      page-break-inside: avoid;
      break-inside: avoid;
    }}
  </style>
</head>
<body>

  <header class="report-header">
    <div class="report-kicker">Technical Report OM-TR-2026-01 · Version 1.1.0 · Zenodo DOI: 10.5281/zenodo.24439497</div>
    <h1 class="doc-title">Orbiting Minds and the RR-10 v1.1 Directional Fragility Audit: Deterministic Spaceflight Multi-Omics Visualization, Epistemic Calibration Guardrails, and Exploratory World-Model Evaluation</h1>
    <div class="author-line">Gaston Dana</div>
    <div class="affiliation-line">Independent Computational Space Biology Researcher · NASA OSDR Analysis Working Group Contributor · November 22, 2026</div>
    <div class="meta-grid">
      <div><strong>Primary Repository:</strong> <a href="https://github.com/gastondana627/blender-simulator">github.com/gastondana627/blender-simulator</a></div>
      <div><strong>Live 3D Viewer:</strong> <a href="https://orbiting-minds.vercel.app/">orbiting-minds.vercel.app</a></div>
      <div><strong>Companion Consumer:</strong> <a href="https://osdr-chatbot-kappa.vercel.app">OSDR ChatBot v1.0.0</a></div>
      <div><strong>ORCID / Scholar:</strong> <a href="https://orcid.org/0009-0007-1011-860X">0009-0007-1011-860X</a> · Google Scholar Verified</div>
      <div><strong>AWG Source Thread:</strong> <a href="https://awg.osdr.space/t/can-frontier-llms-accurately-interpret-spaceflight-biology-rr-10-benchmark-interactive-3d-viewer/4569">awg.osdr.space/t/4569</a></div>
      <div><strong>Zenodo DOI:</strong> <a href="https://doi.org/10.5281/zenodo.24439497">10.5281/zenodo.24439497</a> · <a href="https://zenodo.org/records/24439497">Record #24439497</a></div>
      <div><strong>License:</strong> MIT (Code) · CC-BY-4.0 (Report &amp; Aggregate Figures)</div>
      <div class="sha-bar"><strong>Verified Frozen RR-10 v1.1 Canonical SHA-256:</strong> <code>{sha256}</code> (5,630 items / 2,815 matched pairs / 34 OSD studies)</div>
    </div>
  </header>

  <section class="abstract-box">
    <h2>Abstract</h2>
    <p>Spaceflight multi-omics portals maintained by the NASA Open Science Data Repository (OSDR) remain predominantly two-dimensional, while frontier large language models (LLMs) deployed to interpret spaceflight transcriptomics frequently overclaim consistent directional gene regulation across studies that empirically contradict one another at FDR <em>q</em> &lt; 0.05. This report documents a strictly decoupled two-tier architecture built between September and November 2026 to address both gaps without compromising provenance.</p>
    <p><strong>Tier 1</strong> comprises <em>Orbiting Minds</em> (released September 6, 2026), a deterministic SHA-256 JSON-to-Blender-to-WebGL pipeline translating NASA Rodent Research-10 (RR-10) murine cerebellum (<code>OSD-563</code>, PC1 = 25.6%, rRNA-removal VST concordance <em>r</em> = 1.000) and hippocampus (<code>OSD-564</code>, PC1 = 28.3%) transcriptomics into compact GLB assets paired with an external vector SVG Analytic Evidence Drawer, alongside an independent full-corpus verification of OMROSLAB's frozen <strong>RR-10 v1.1 Directional Fragility Benchmark</strong> (<code>5,630</code> items, <code>11</code> <code>organism::tissue</code> contexts, <code>34</code> OSD studies, <code>11,711</code> provenance rows). Neutral closed-book sweeps expose a hard <strong>~10% Paired Directional Robustness (PDR) ceiling</strong> (<code>10.44%</code> for <code>openai/gpt-oss-120b</code>; <code>10.27%</code> for <code>google/gemini-3.5-flash-lite</code>; <code>0.53%</code> for <code>openai/gpt-5.4-nano-2026-03-17</code>). A 440-item caution-coached ablation demonstrates the <strong>Epistemic Caution Trap</strong>: prompt-only caution cuts <code>gemini-3.5-flash-lite</code> trap overclaiming from <code>44.65%</code> to <code>1.36%</code> but collapses control accuracy (<code>20.89% -&gt; 0.00%</code>) and PDR (<code>10.27% -&gt; 0.00%</code>), with all <code>3</code> remaining directional claims being false trap overclaims. We bridge this finding to production via a machine-readable guardrail contract (<code>EC-01..EC-06</code>) consumed by <strong>OSDR ChatBot v1.0.0</strong>.</p>
    <p><strong>Tier 2</strong> reports a controlled 10-second live WebRTC evaluation of Google DeepMind's real-time interactive world model (<code>genie-4</code>, <code>1280x720 @ 24 fps</code>, <code>48 kHz</code> stereo audio) seeded with a <code>31.9 KB</code> 16:9 image. While mid-stream event steering works reliably (<code>10x / 150 ms</code> impulses), observed frame-1 close-up subject morphing, ~8-10 s spatial permanence drift, and illegible in-frame text confirm that generative world models must remain strictly isolated to outreach behind production construction locks in compliance with the NASA OSDR Synthetic Intelligence Charter.</p>
    <div class="keywords"><strong>Keywords:</strong> NASA OSDR · Rodent Research-10 · Spaceflight Transcriptomics · LLM Epistemic Calibration · Directional Fragility Benchmark · Deterministic 3D Scientific Visualization · Interactive World Models · Synthetic Intelligence Governance</div>
  </section>

  <div class="kpi-grid">
    <div class="kpi-card cyan">
      <div class="kpi-val">5,630 / 2,815</div>
      <div class="kpi-lbl">Canonical v1.1 items &amp; 1:1 matched pairs across 34 OSD studies (11,711 provenance rows)</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-val">10.44% PDR</div>
      <div class="kpi-lbl">Best full-corpus neutral closed-book ceiling (gpt-oss-120b); Gemini 3.5 Flash-Lite: 10.27%</div>
    </div>
    <div class="kpi-card amber">
      <div class="kpi-val">44.65% -&gt; 0%</div>
      <div class="kpi-lbl">Caution Trap: prompt caution cuts traps to 1.36% yet collapses valid controls &amp; PDR to 0.00%</div>
    </div>
    <div class="kpi-card green">
      <div class="kpi-val">r = 1.000 QC</div>
      <div class="kpi-lbl">OSD-563/564 deterministic Tier 1 pipeline (Sept 6, 2026) + EC-01..EC-06 guardrail contract</div>
    </div>
  </div>

  <h2>1. Introduction and 2024-2026 Research Landscape</h2>
  <p>Open-science spaceflight archives curated by the NASA Open Science Data Repository (OSDR; Gebre et al., 2024/2025) and human astronaut cohorts such as the Space Omics and Medical Atlas (SOMA; Overbey et al., 2024) have accelerated computational space biology. Recent NASA OSDR Analysis Working Group (AWG) publications apply causal machine learning ensembles to murine spaceflight phenotypes (Casaletto et al., 2025), representation learning to plant transcriptomics (<code>GLARE</code>; Seo et al., 2025), and molecular pathway discovery to spaceflown murine retinal damage (Casaletto et al., 2026).</p>
  <p>Across 2025-2026 AI literature, however, "world models" have diverged across two disconnected tracks: biological perturbation models in expression latent space (Arc Institute's <em>State</em>, Adduri et al., 2025; CZI's <em>TranscriptFormer</em>, Pearce et al., 2025) versus real-time action-conditioned video and physical-AI simulators (Google DeepMind's <em>Genie</em> lineage, Bruce et al., 2024; Genie 4 API, 2026; NVIDIA <em>Cosmos</em>, 2025, 2026). Through November 2026, NASA OSDR spaceflight biology visualization has remained 2D, while exploratory hybrid pipelines linking deterministic 3D assets and generative world models only began appearing in non-spaceflight literature in November 2026 (Mohapatra, November 4, 2026). <em>Orbiting Minds</em> was released publicly on <strong>September 6, 2026</strong> (commit <code>1dc2781</code>) - two months earlier - pairing a deterministic spaceflight data-to-3D pipeline with rigorous LLM calibration audits and strict generative governance boundaries.</p>

  <h2>2. Tier 1: Deterministic Data-to-3D Pipeline (Orbiting Minds)</h2>
  <h3>2.1 NASA Rodent Research-10 (RR-10) Biological Foundation</h3>
  <p>Tier 1 anchors on the NASA Rodent Research-10 (RR-10) ISS mission (SpaceX-21, December 5, 2020 - January 13, 2021), comparing spaceflight (<code>FLT</code>, <em>n</em> = 5) and ground control (<code>GC</code>, <em>n</em> = 5) female C57BL/6J mouse brain transcriptomes processed via DESeq2 variance-stabilized transformation (VST; Love et al., 2014):</p>

  <table>
    <thead>
      <tr>
        <th>OSDR Study</th>
        <th>Legacy ID</th>
        <th>Brain Region</th>
        <th>Verified DataCite DOI</th>
        <th class="center">Samples</th>
        <th class="num">PC1 / PC2 Variance</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td class="bold">OSD-563</td>
        <td><code>GLDS-568</code></td>
        <td>Cerebellum</td>
        <td><code>10.26030/ycn8-v994</code></td>
        <td class="center">10 (5 FLT / 5 GC)</td>
        <td class="num">25.6% / 18.5%</td>
      </tr>
      <tr>
        <td class="bold">OSD-564</td>
        <td><code>GLDS-569</code></td>
        <td>Hippocampus</td>
        <td><code>10.26030/48p5-yy05</code></td>
        <td class="center">10 (5 FLT / 5 GC)</td>
        <td class="num">28.3% / 15.7%</td>
      </tr>
    </tbody>
  </table>

  <p>In <code>OSD-563</code> preprocessing quality-control checks comparing rRNA-included versus rRNA-removed counts, per-value VST linear concordance reaches <strong><em>r</em> = 1.000</strong> across the <code>[5.0, 24.5]</code> VST domain, with a modal positive shift at <code>0.012</code> (frequency <code>17,150</code>) and a library-filtering truncation spike at <code>0.355</code> (frequency <code>16,000</code>). This preprocessing invariant is surfaced inside the viewer's external SVG Analytic Evidence Drawer and explicitly distinguished from biological effects.</p>

  <h3>2.2 Reproducible Headless Blender-to-WebGL Architecture</h3>
  <div class="pipeline-box">data/processed/*.json  --&gt;  scripts/data_adapter.py (SHA-256 deterministic seed)
                       --&gt;  data/recipes/*.json (v3 murine_neural_proxy | media_astro_mouse)
                       --&gt;  Headless Blender 4.1.1 (generate_scene.py | generate_media_scene.py)
                       --&gt;  exports/simulation.glb (47 objs, 19,032 verts, 1.12 MB)
                            exports/media_simulation.glb (100 objs, 11,670 verts, 688 KB)
                       --&gt;  Three.js WebGL Viewer + External SVG Evidence Drawer (web-viewer/)</div>

  <p>Automated unit tests (<code>tests/test_pipeline_fixes.py</code>) confirm SHA-256 seed invariance across varying <code>PYTHONHASHSEED</code> processes, complete isolation between the Technical Benchmark and Media Companion (<em>Commander Pip: Zero-G Odyssey</em>) branches, and strict provenance boundaries:</p>

  <table>
    <thead>
      <tr>
        <th style="width:27%">Source Input / Derived Metric</th>
        <th style="width:31%">3D Visual Encoding</th>
        <th style="width:42%">Strict Scientific Interpretation Boundary</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><code>OSD-563</code> / <code>OSD-564</code> PCA coordinates (20 samples)</td>
        <td>Left &amp; right background constellation nodes (<code>#ff5252</code> FLT, <code>#40c4ff</code> GC)</td>
        <td>Graph-derived statistical variance motif; <strong>not</strong> physical anatomical coordinates inside mouse brain tissue.</td>
      </tr>
      <tr>
        <td><code>OSD-563</code> rRNA-removal QC (<em>r</em> = 1.000)</td>
        <td>External vector SVG scatter + shift histogram in Evidence Drawer</td>
        <td>Bioinformatics preprocessing QC check; <strong>not</strong> a biological phenotype or differential outcome.</td>
      </tr>
      <tr>
        <td>Derived neuro-adaptation, stress &amp; volatility indices</td>
        <td>Central proxy scale (<code>0.85x-1.30x</code>), synaptic emission, cortical pulse, gimbal rings</td>
        <td>Qualitative visual proxy controls synchronized to summary metrics; <strong>not</strong> clinical MRI, brain edema, or ICP measurement.</td>
      </tr>
      <tr>
        <td><em>Commander Pip: Zero-G Odyssey</em></td>
        <td>Stylized PBR astronaut mouse + zero-G orbital habitat</td>
        <td>Outreach narrative inspired by RR-10 context; <strong>not</strong> a scientific or historical reconstruction.</td>
      </tr>
    </tbody>
  </table>

  <h2>3. Independent Verification of the RR-10 v1.1 Directional Fragility Benchmark</h2>
  <p>We conducted an independent structural audit and full-corpus evaluation of <strong>OMROSLAB's frozen RR-10 v1.1 Directional Fragility Benchmark</strong> (authored by Omar Rafael Perez Gallardo; NASA OSDR AWG Discourse Thread <code>#4569</code>). Filtering <code>244</code> initial OSDR differential expression tables down to <code>95</code> clean tables (excluding <code>17</code> confounded-only 1G/duration studies, <code>118</code> tables lacking clean SF-vs-GC contrasts, <code>12</code> missing exact <code>Material Type</code> keys, and <code>2</code> missing <code>SYMBOL</code> columns) and enforcing 1:1 matching without replacement yields <strong><code>5,630</code> canonical items</strong> (<code>2,815</code> multi-study fragility traps labeled <code>indeterminate</code> + <code>2,815</code> matched concordant controls: <code>1,459</code> <code>upregulated</code>, <code>1,356</code> <code>downregulated</code>) across <code>11</code> exact <code>organism::tissue</code> contexts, <code>34</code> OSD studies, and <code>11,711</code> provenance rows.</p>
  <p>Four verification gates passed inside a quarantined evaluation workspace prior to model sweeps: (1) schema validation passed <code>5,630 / 5,630</code> (<code>0</code> errors); (2) the Paired Directional Robustness (PDR) denominator audit verified dynamic pair counting (<code>2,815</code> pairs, replacing legacy hardcoded <code>100</code>-pair denominators, proven via partial-pair check <code>1,407 / 2,815 = 0.499822380107</code>); (3) Gold Oracle (<code>PDR = 1.0000</code>) and All-Indeterminate (<code>PDR = 0.0000</code>, raw item accuracy <code>50.0%</code>) baselines confirmed immunity to blanket-abstention gaming; and (4) <code>5</code> canonical files matched bit-for-bit across local and private internet-disabled Kaggle verification.</p>

  <figure class="figure-block">
    <img src="{fig_funnel_uri}" alt="RR-10 v1.1 Corpus Filter Funnel and 11-Context Breakdown">
    <figcaption class="figure-caption"><span class="caption-label">Figure 1.</span> Confound-filtered corpus reduction (244 OSDR DE tables -&gt; 95 clean tables -&gt; 5,630 canonical items, 2,815 matched pairs, 34 OSD studies, 11,711 provenance rows) and per-context Trap Overclaim Rate versus Paired Directional Robustness (PDR) across all 11 exact <code>organism::tissue</code> contexts for <code>openai/gpt-oss-120b</code> and <code>google/gemini-3.5-flash-lite</code>.</figcaption>
  </figure>

  <table>
    <thead>
      <tr>
        <th>Exact <code>organism::tissue</code> Context</th>
        <th class="num">Items</th>
        <th class="num">Pairs</th>
        <th class="num">gpt-oss-120b<br>TrapOver / PDR</th>
        <th class="num">gemini-3.5-flash-lite<br>TrapOver / PDR</th>
        <th class="num">gpt-5.4-nano<br>TrapOver / PDR</th>
      </tr>
    </thead>
    <tbody>
      {"".join(ctx_rows_html)}
    </tbody>
  </table>

  <p>Cross-context vulnerability is sharply heterogeneous: <code>arabidopsis_thaliana::seedlings</code> (<code>380</code> matched pairs) triggers a <strong><code>78.68%</code> Trap Overclaim Rate</strong> identically on both <code>gpt-oss-120b</code> and <code>gemini-3.5-flash-lite</code>, more than double the rate observed in <code>homo_sapiens::cells</code> (<code>28.83%</code> and <code>31.11%</code> across <code>1,006</code> pairs).</p>

  <h2>4. Model Calibration Results and the Epistemic Caution Trap</h2>
  <p>All models were evaluated under a <strong>Neutral Zero-Nudge Closed-Book</strong> protocol (bare OMROSLAB question + strict 3-label JSON enum, <code>temperature = 0</code>, zero caution coaching). Full-corpus runs (<code>5,630</code> items, <code>2,815</code> matched pairs) achieved <code>100.0%</code> parse coverage and <code>0</code> API errors. To test whether prompt engineering alone resolves multi-study overclaiming, we conducted a <strong>440-item stratified Caution-Coached Ablation</strong> (<code>220</code> matched pairs spanning all <code>11</code> contexts) on <code>gemini-3.5-flash-lite</code> and <code>gpt-5.4-nano</code>:</p>

  <table>
    <thead>
      <tr>
        <th>Model</th>
        <th>Protocol</th>
        <th class="num">Items (Pairs)</th>
        <th class="num">PDR</th>
        <th class="num">Trap Overclaim</th>
        <th class="num">Control Acc</th>
        <th class="num">Control Abst.</th>
        <th class="num">Macro F1</th>
        <th class="num">Avg Latency</th>
      </tr>
    </thead>
    <tbody>
      {"".join(score_rows_html)}
    </tbody>
  </table>

  <figure class="figure-block">
    <img src="{fig_calib_uri}" alt="Before vs After Model Calibration and Caution Trap">
    <figcaption class="figure-caption"><span class="caption-label">Figure 2.</span> Left: Full-corpus 5,630-item neutral zero-nudge closed-book scoreboard (plus the 440-item <code>gemini-3-flash-preview</code> pilot showing <code>99.55%</code> trap overclaiming and <code>0.00%</code> PDR). Right: Prompt-only caution ablation on <code>gemini-3.5-flash-lite</code> demonstrating the Epistemic Caution Trap (trap overclaim drops <code>44.65% -&gt; 1.36%</code> while valid control accuracy and PDR both collapse to <code>0.00%</code>).</figcaption>
  </figure>

  <div class="callout">
    <strong>Core Finding - The Epistemic Caution Trap:</strong> Under closed-book conditions, models exhibit a hard <strong>~10% PDR ceiling</strong> (<code>10.44%</code> best). Aggressive guessing (<code>gemini-3-flash-preview</code>) zeroes PDR via <code>99.55%</code> trap overclaiming, while neutral conservatism (<code>gpt-5.4-nano</code>) collapses control accuracy to <code>0.53%</code> via <code>98.86%</code> abstention. Most critically, adding prompt-only epistemic caution to <code>gemini-3.5-flash-lite</code> eliminated <code>100%</code> of valid control recall (<code>20.89% -&gt; 0.00%</code>), and <strong>all 3 directional claims it still emitted (out of 440 items) were false overclaims on fragility traps</strong>. Breaking the ~10% PDR ceiling therefore requires grounded OSDR tool retrieval rather than prompt wording alone.
  </div>

  <h2>5. Machine-Readable Epistemic Guardrail Contract &amp; v1.2 Roadmap</h2>
  <p>To operationalize these diagnostics across space-biology assistants, <em>Orbiting Minds</em> publishes <code>data/processed/rr10_guardrail_contract.json</code> (schema <code>1.1.0</code>, zero raw item leakage) for direct runtime consumption by <strong>OSDR ChatBot v1.0.0</strong> (<code>https://osdr-chatbot-kappa.vercel.app</code>):</p>

  <table>
    <thead>
      <tr>
        <th class="center" style="width:10%">Rule ID</th>
        <th class="center" style="width:12%">Severity</th>
        <th>Runtime Epistemic Guardrail Specification</th>
      </tr>
    </thead>
    <tbody>
      {"".join(rule_rows_html)}
    </tbody>
  </table>

  <p><strong>Planned v1.2 Secondary Diagnostic:</strong> Credited to NASA OSDR AWG contributor <code>@Mym04Tak14</code>, v1.2 will incorporate a scale-invariant natural-log viscoelastic trajectory diagnostic to quantify low-replicate (<em>n</em> = 5) temporal directional instability and hysteresis across varying flight durations once v1.1 baseline sign-off closes:</p>
  <div class="formula-box">&Delta;<sub>visc</sub>(t) = ln[ S(t) / S<sub>0</sub> ]</div>

  <h2>6. Tier 2 Exploratory Case Study: Real-Time World Models (<code>genie-4</code>)</h2>
  <h3>6.1 WebRTC Architecture, Budget Guardrails, and Controlled Live Test</h3>
  <p>To empirically assess whether interactive generative world models can augment deterministic 3D outreach without degrading scientific reliability, we implemented a localhost R&amp;D WebRTC client (<code>web-viewer/pip-world.html</code>, <code>scripts/genie_local_server.py</code>, <code>api/genie-session.js</code>, <code>api/genie-stop.js</code>) targeting Google DeepMind's <code>models/genie-4</code> via the Gemini Interactions API (<code>v1beta</code>, <code>@google/genai@3.6.1</code>). Single-session ephemeral <code>auth_tokens</code> are minted server-side; the 16:9 seed image (<code>960x540</code> JPEG, <code>32,681 B</code> / <code>31.9 KB</code>) stays strictly below Genie 4's <code>48 KB</code> raw JPEG / <code>64 KB</code> WebRTC SCTP ceiling; and a client-side <code>MediaRecorder</code> captures clean <code>1280x720 @ 24 fps</code> + <code>48 kHz</code> stereo streams directly from <code>srcObject</code> with zero HUD clutter. Billing (~$0.10/s at 5,760 video output tok/s) is bounded by selectable 10-90 s hard caps calling <code>session.complete()</code>, a 10 s hidden-tab auto-stop, and <code>sendBeacon</code> unload cancellation.</p>
  <p>A single user-approved <strong>10-second live WebRTC session</strong> (~$1.00 spend, <code>0</code> console or page errors) established clear empirical boundaries for Tier 2 usage:</p>

  <table>
    <thead>
      <tr>
        <th style="width:22%">Evaluation Axis</th>
        <th style="width:41%">Empirical Observation (10 s Live WebRTC Capture)</th>
        <th style="width:37%">Governance &amp; Engineering Rule</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td class="bold">Transport &amp; Foley Audio</td>
        <td>Connected at <code>1280x720 @ 24 fps</code> (<code>readyState = 4</code>) after ~5-9 s warmup with synchronized broadband Foley audio.</td>
        <td>Viable for short 15-30 s budgeted outreach clips when protected by hard client auto-stop caps.</td>
      </tr>
      <tr>
        <td class="bold">Mid-Stream Steering</td>
        <td>Sending <code>10x / 150 ms</code> text impulses (<code>2 s</code> cooldown) crossed the 4-frame planner; pressing <code>E</code> (<em>Open Earth Cupola</em>) generated a sunlit Earth-horizon porthole on the bulkhead.</td>
        <td>Effective for scripted narrative transitions and live audience interaction during outreach showcases.</td>
      </tr>
      <tr>
        <td class="bold">Frame-1 Foreground Morphing</td>
        <td>Close-up character framing near the lens triggered severe geometry morphing on frame-1 forward input (<code>W</code>) before stabilizing down the corridor.</td>
        <td>Require wide-angle/distant framing or first-person habitat POV seeds; never treat visual geometry as anatomical ground truth.</td>
      </tr>
      <tr>
        <td class="bold">Permanence &amp; In-Frame Text</td>
        <td>Off-screen geometry drifts after ~8-10 s of camera panning; rendered instrument-panel text is visually decorative rather than legible.</td>
        <td><strong>Hard Boundary:</strong> Zero empirical metrics or gene counts inside generative pixels; keep all data in Tier 1 HTML/SVG overlays.</td>
      </tr>
    </tbody>
  </table>

  <div class="callout blue">
    <strong>NASA OSDR Synthetic Intelligence Charter Alignment &amp; Production Lock:</strong> Consistent with the NASA OSDR AWG Synthetic Intelligence Charter (revised September 2025), zero restricted rodent behavioral video (e.g., <code>OSD-952</code>) or human clinical SOMA data is transmitted to external generative world-model APIs. On public production hosts (<code>orbiting-minds.vercel.app</code>), <code>pip-world.html</code> displays a full-viewport diagonal construction-tape <strong>"UNDER CONSTRUCTION - COMING SOON"</strong> X-barrier locking all controls, reinforced by server-side <code>HTTP 503</code> rejection unless explicitly unlocked via <code>GENIE_ENABLE_PROD=true</code>.
  </div>

  <h2>7. Public/Private Boundary Firewall, Reproducibility &amp; Acknowledgments</h2>
  <p>Pending formal OSDR/OMROSLAB licensing sign-off for raw benchmark redistribution, an automated firewall script (<code>scripts/check_public_boundary.py</code>) audits <code>.gitignore</code> enforcement, git index/working-tree status, and every public directory (<code>data/</code>, <code>exports/</code>, <code>web-viewer/</code>, <code>project-site/</code>) to guarantee <strong>zero</strong> leaked per-item identifiers, raw provenance rows, or API credentials. Public artifacts remain strictly aggregate summaries, the <code>EC-01..EC-06</code> guardrail contract, and deterministic Tier 1 3D assets.</p>
  <p><strong>Acknowledgments:</strong> We gratefully credit <strong>OMROSLAB (Omar Rafael Perez Gallardo)</strong> for authoring the frozen RR-10 v1.1 Directional Fragility benchmark specification (AWG Discourse <code>#4569</code>), NASA OSDR AWG contributor <code>@Mym04Tak14</code> for the planned v1.2 viscoelastic trajectory framework, and the NASA OSDR Brain and AI/ML Analysis Working Groups. NASA, OSDR, and GeneLab are cited solely for factual scientific attribution; this work is an independent contribution not affiliated with or endorsed by NASA.</p>

  <h2>8. Verified References</h2>
  <ol class="ref-list">
    <li>Gebre, S. G., Scott, R. T., Saravia-Butler, A. M., Lopez, D. K., Sanders, L. M., &amp; Costes, S. V. (2024/2025). NASA open science data repository: open science for life in space. <em>Nucleic Acids Research</em>, 53(D1), D1697-D1710. DOI: <code>10.1093/nar/gkae1116</code></li>
    <li>Galazka, J. M., Giacomello, S., Almeida, E., Costes, S. V., Gebre, S. G., Frapard, S., et al. (2022). Bulk RNA sequencing and spatially resolved transcriptional profiling of cerebellums from mice flown on the RR-10 mission (OSD-563 / GLDS-568, v9). NASA GeneLab / OSDR. DOI: <code>10.26030/ycn8-v994</code></li>
    <li>Galazka, J. M., Giacomello, S., Almeida, E., Costes, S. V., Gebre, S. G., Frapard, S., et al. (2022). Bulk RNA sequencing and spatially resolved transcriptional profiling of hippocampi from mice flown on the RR-10 mission (OSD-564 / GLDS-569, v8). NASA GeneLab / OSDR. DOI: <code>10.26030/48p5-yy05</code></li>
    <li>Love, M. I., Huber, W., &amp; Anders, S. (2014). Moderated estimation of fold change and dispersion for RNA-seq data with DESeq2. <em>Genome Biology</em>, 15(12), 550. DOI: <code>10.1186/s13059-014-0550-8</code></li>
    <li>Overbey, E. G., Kim, J., Tierney, B. T., Park, J., Houerbi, N., Lucaci, A. G., et al. (2024). The Space Omics and Medical Atlas (SOMA) and international astronaut biobank. <em>Nature</em>, 632(8027), 1145-1154. DOI: <code>10.1038/s41586-024-07639-y</code></li>
    <li>Casaletto, J. A., Scott, R. T., Myrick, M., Mackintosh, G., Chok, H., Saravia-Butler, A., et al. (2025). Analyzing the relationship between gene expression and phenotype in space-flown mice using a causal inference machine learning ensemble. <em>Scientific Reports</em>, 15(1). DOI: <code>10.1038/s41598-024-81394-y</code></li>
    <li>Seo, D., Strickland, H. F., Zhou, M., Barker, R., Ferl, R. J., Paul, A.-L., et al. (2025). GLARE: discovering hidden patterns in spaceflight transcriptome using representation learning. <em>npj Microgravity</em>, 11(1). DOI: <code>10.1038/s41526-025-00525-5</code></li>
    <li>Casaletto, J. A., Scott, R. T., Rathod, A., Jain, A., Chandar, A., Adapala, A., et al. (2026). Machine learning ensemble reveals distinct molecular pathways of retinal damage in spaceflown mice. <em>npj Microgravity</em>, 12(1). DOI: <code>10.1038/s41526-026-00625-w</code></li>
    <li>Adduri, A. K., Gautam, D., Bevilacqua, B., Imran, A., Shah, R., Naghipourfar, M., et al. (2025). Predicting cellular responses to perturbation across diverse contexts with State. <em>bioRxiv / openRxiv</em>. DOI: <code>10.1101/2025.06.26.661135</code></li>
    <li>Pearce, J. D., Simmonds, S. E., Mahmoudabadi, G., Krishnan, L., Palla, G., Istrate, A.-M., et al. (2025). A Cross-Species Generative Cell Atlas Across 1.5 Billion Years of Evolution: The TranscriptFormer Single-cell Model. <em>bioRxiv / openRxiv</em>. DOI: <code>10.1101/2025.04.25.650731</code></li>
    <li>Bruce, J., Dennis, M., Edwards, A., Parker-Holder, J., Shi, Y., Hughes, E., et al. (2024). Genie: Generative Interactive Environments. <em>arXiv preprint</em> <code>arXiv:2402.15391</code>.</li>
    <li>NVIDIA (Agarwal, N., Ali, A., Bala, M., Balaji, Y., et al.). (2025). Cosmos World Foundation Model Platform for Physical AI. <em>arXiv preprint</em> <code>arXiv:2501.03575</code>.</li>
    <li>NVIDIA (Ahmad, A., Allen, J., Anwar, M. A., Archer, J., et al.). (2026). Interactive World Simulation with Cosmos for Physical AI. <em>arXiv preprint</em> <code>arXiv:2611.06627</code>.</li>
    <li>Mohapatra, S. (2026). From Video to Digital Twin: An Exploratory Study of World Models and Gaussian Splatting on In-the-Wild Video. <em>arXiv preprint</em> <code>arXiv:2611.10013</code>.</li>
    <li>Google DeepMind / Gemini API Documentation. (2026). Genie 4 Interactive World Model (<code>models/genie-4</code>, Interactions API <code>v1beta</code>). <code>https://aistudio.google.com/docs/genie</code></li>
    <li>Dana, G. (2026). Orbiting Minds: An RR-10 Data-to-3D Simulation Experience (released September 6, 2026; v1.1.0 November 2026). GitHub: <code>https://github.com/gastondana627/blender-simulator</code>; Live Viewer: <code>https://orbiting-minds.vercel.app/</code>; Companion Consumer: <code>https://osdr-chatbot-kappa.vercel.app</code>; AWG Thread #4569: <code>https://awg.osdr.space/t/can-frontier-llms-accurately-interpret-spaceflight-biology-rr-10-benchmark-interactive-3d-viewer/4569</code></li>
  </ol>

  <h3>BibTeX Deposition Template</h3>
  <div class="bibtex-box">@techreport{{dana2026orbitingminds,
  author      = {{Dana, Gaston}},
  title       = {{Orbiting Minds and the RR-10 v1.1 Directional Fragility Audit: Deterministic Spaceflight Multi-Omics Visualization, Epistemic Calibration Guardrails, and Exploratory World-Model Evaluation}},
  institution = {{Independent Computational Space Biology Research / NASA OSDR AWG Community Contribution}},
  year        = {{2026}},
  month       = {{November}},
  number      = {{OM-TR-2026-01}},
  version     = {{1.1.0}},
  doi         = {{10.5281/zenodo.24439497}},
  url         = {{https://zenodo.org/records/24439497}}
}}</div>

</body>
</html>
"""


def render_pdf(output_path: Path = OUTPUT_PDF_PATH) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if output_path.exists():
        output_path.unlink()
    html_content = build_html()

    header_tpl = (
        '<div style="width:100%;font-family:-apple-system,Helvetica,Arial,sans-serif;'
        'font-size:7pt;color:#64748b;padding:0 0.72in;display:flex;justify-content:space-between;">'
        '<span>Orbiting Minds &amp; RR-10 v1.1 Technical Report (OM-TR-2026-01)</span>'
        '<span>G. Dana · November 2026</span>'
        '</div>'
    )
    footer_tpl = (
        '<div style="width:100%;font-family:-apple-system,Helvetica,Arial,sans-serif;'
        'font-size:7pt;color:#64748b;padding:0 0.72in;display:flex;justify-content:space-between;">'
        '<span>Public-Safe Aggregate Report · MIT / CC-BY-4.0 · orbiting-minds.vercel.app</span>'
        '<span>Page <span class="pageNumber"></span> of <span class="totalPages"></span></span>'
        '</div>'
    )

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.set_content(html_content, wait_until="load")
        page.pdf(
            path=str(output_path),
            format="Letter",
            print_background=True,
            display_header_footer=True,
            header_template=header_tpl,
            footer_template=footer_tpl,
            margin={
                "top": "0.64in",
                "bottom": "0.66in",
                "left": "0.62in",
                "right": "0.62in",
            },
        )
        browser.close()
    return output_path


if __name__ == "__main__":
    out = render_pdf()
    print(f"Rendered PDF: {out} ({out.stat().st_size:,} bytes)")
