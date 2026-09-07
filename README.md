# Orbiting Minds
### An RR-10 Data-to-3D Simulation Experience

Orbiting Minds is a dual-mode data-to-3D simulation experience connecting NASA Rodent Research-10 (RR-10) spaceflight mouse-brain transcriptomics, Kaggle reasoning benchmark findings, a headless procedural Blender generation pipeline, GLB export, and an interactive Three.js/WebGL inspection viewer. The system translates spaceflight differential gene expression patterns and bioinformatics quality-control metrics into interactive 3D assets while preserving strict empirical interpretation boundaries.

The repository provides two strictly decoupled experience branches:
- **Technical Benchmark**: A benchmark-informed, data-synchronized murine neural proxy accompanied by an interactive vector SVG analytic evidence drawer.
- **Media Companion**: A stylized cinematic narrative experience following **Commander Pip: Zero-G Odyssey**, inspired by the RR-10 mission context for science communication and public engagement.

---

## 1. Title and Project Identity

- **Title**: Orbiting Minds
- **Subtitle**: An RR-10 Data-to-3D Simulation Experience

Orbiting Minds bridges computational space biology and real-time 3D computer graphics. By taking structured transcriptomic outputs from the NASA RR-10 mission, the project procedurally generates data-synchronized 3D environments suitable for both analytical exploration and public-facing visual storytelling.

### Dual-Mode Design
1. **Technical Benchmark**: Focuses on scientific context, bio-digital proxy geometry, and analytical transparency. It synchronizes murine neural proxy anatomy with actual benchmark scores, sample conditions, PCA projections, and quality-control distributions without claiming to be a clinical or cellular reconstruction.
2. **Media Companion (Commander Pip: Zero-G Odyssey)**: A stylized, charismatic cinematic narrative that humanizes the heroic legacy of spaceflight rodent research. It features an astronaut mouse exploring microgravity inside a space habitat module, completely separated from the technical benchmark pipeline.

---

## 2. Project Highlights

- **Data-to-3D Procedural Blender Pipeline**: Automated parameter mapping translating raw transcriptomic analysis summaries and benchmark outputs into 3D scene geometry, materials, and motion.
- **Headless CLI & Optional Interactive Workflow**: Full headless execution via `run_pipeline.py` with automatic Blender binary discovery, alongside an optional interactive Blender GUI mode and a dedicated 3D Viewport N-Panel add-on.
- **Web-Optimized GLB Export & JSON Telemetry**: Generates compact, self-contained binary GLTF (.glb) assets (< 1.2 MB) accompanied by structured scene telemetry JSON files containing bounding boxes, vertex counts, and object registries.
- **Three.js/WebGL Browser Viewer**: Real-time browser-based exploration featuring orbit navigation, animated timeline playback, speed scaling, and drag-and-drop model inspection.
- **Three Distinct Inspection Modes**:
  - **Presentation Mode**: Clean, visual-first 3D viewing with curated studio lighting and subtle rotation.
  - **Annotated Mode**: Interactive hover and click hotspots connecting anatomical proxy landmarks to mission metrics and dataset IDs.
  - **Diagnostic Mode**: Instant wireframe overlay for verifying mesh topology, subdivision density, and geometry.
- **Interactive Analytic Evidence Drawer**: Embedded vector graphics panel directly reproducing empirical principal component analysis (PCA) plots and rRNA-removal quality control distributions from the source notebook.
- **Data-Driven Background PCA Constellation**: Background coordinate constellation directly mapped to spaceflight (`FLT`) versus ground control (`GC`) sample variance in 3D space.
- **Decoupled Dual-Branch Architecture**: Complete isolation between the Technical Benchmark and Media Companion branches across recipes, generation scripts, export targets, and viewer tabs.
- **Clean, Reproducible Configuration**: Driven by human-readable JSON recipes and processed benchmark data files.

---

## 3. Scientific and Data Context

The biological foundation of this project is based on the **NASA Rodent Research-10 (RR-10)** mission, which investigated physiological, microvascular, and transcriptomic adaptations of female C57BL/6J mice during spaceflight aboard the International Space Station (ISS):

- **OSD-563 (Cerebellum)**: Transcriptomic profiling of murine cerebellar tissue assessing vestibular adaptation, motor coordination, and microvascular stress under microgravity conditions.
- **OSD-564 (Hippocampus)**: Transcriptomic profiling of murine hippocampal tissue examining neuroplasticity, cognitive stress response, and fluid-shift regulation.
- **Related Identifiers**: NASA GeneLab accessions **GLDS-568** and **GLDS-569** serve as related historical repository identifiers within the NASA Open Science Data Repository (OSDR).

> [!IMPORTANT]
> **Scientific Framing and Interpretation Boundary**
> The Technical Benchmark scene is a **benchmark-informed, data-synchronized visual proxy**. It is **not** a literal mouse-brain reconstruction, clinical visualization, validated physiological simulator, or official NASA product.
> Similarly, the Media Companion is a **stylized cinematic narrative inspired by RR-10 mission context**; it is not a scientific reconstruction.
> Source data and notebook findings are strictly decoupled from derived visualization parameters and creative visual encodings.

---

## 4. Data Sources and Project Resources

### NASA OSDR / RR-10 Source Studies
- [RR-10 Rodent Research 10 payload — NASA OSDR](https://osdr.nasa.gov/bio/repo/data/payloads/RR-10)
- [OSD-563 — Cerebellum transcriptomics from RR-10 mice](https://osdr.nasa.gov/bio/repo/data/studies/OSD-563)
- [OSD-564 — Hippocampus transcriptomics from RR-10 mice](https://osdr.nasa.gov/bio/repo/data/studies/OSD-564)
- [SpaceX-21 mission record — NASA OSDR](https://osdr.nasa.gov/bio/repo/data/missions/SpaceX-21)
- [NASA GeneLab / Open Science for Life in Space](https://genelab.nasa.gov/)

### Kaggle Analysis and Benchmark

| Resource | Description | Link |
| :--- | :--- | :--- |
| **Benchmark** | Official reasoning benchmark task evaluating models on RR-10 spaceflight transcriptomics. | [https://www.kaggle.com/benchmarks/tasks/gastondana/rr-10-transcriptomics-reasoning-benchmark/2](https://www.kaggle.com/benchmarks/tasks/gastondana/rr-10-transcriptomics-reasoning-benchmark/2) |
| **Benchmark Code** | Reference evaluation harness and metric scoring implementation. | [https://www.kaggle.com/code/gastondana/rr-10-transcriptomics-reasoning-benchmark-task](https://www.kaggle.com/code/gastondana/rr-10-transcriptomics-reasoning-benchmark-task) |
| **Notebook Findings** | In-depth comparative transcriptomics analysis of Cerebellum (`OSD-563`) vs. Hippocampus (`OSD-564`). | [https://www.kaggle.com/code/gastondana/cerebellum-vs-hippocampus-rr-10-spaceflight-mice](https://www.kaggle.com/code/gastondana/cerebellum-vs-hippocampus-rr-10-spaceflight-mice) |
| **Dataset** | Normalized gene expression counts, variance-stabilized values, and sample metadata. | [https://www.kaggle.com/datasets/gastondana/osd-563564-cerebellum-vs-hippocampus-rr-10/data](https://www.kaggle.com/datasets/gastondana/osd-563564-cerebellum-vs-hippocampus-rr-10/data) |

- [RR-10 Transcriptomics Reasoning Benchmark](https://www.kaggle.com/benchmarks/tasks/gastondana/rr-10-transcriptomics-reasoning-benchmark/2)
- [Benchmark code](https://www.kaggle.com/code/gastondana/rr-10-transcriptomics-reasoning-benchmark-task)
- [Cerebellum vs Hippocampus RR-10 Spaceflight Mice — analysis notebook](https://www.kaggle.com/code/gastondana/cerebellum-vs-hippocampus-rr-10-spaceflight-mice)
- [OSD-563/564 Cerebellum vs Hippocampus RR-10 — Kaggle dataset](https://www.kaggle.com/datasets/gastondana/osd-563564-cerebellum-vs-hippocampus-rr-10/data)

### Community
- [NASA OSDR Analysis Working Groups](https://science.nasa.gov/citizen-science/osdr-awg/)
- [OSDR AWG Forum](https://awg.osdr.space/top)
- [AI/ML AWG Topics](https://awg.osdr.space/c/awg-discussions/ai-ml/11)
- [AI/ML AWG GitHub](https://github.com/OpenScienceDataRepo/AI-ML_AWG)
- [AWG Projects](https://awg.osdr.space/c/awg-projects/20)

### Project
- [Source code — GitHub](https://github.com/gastondana627/blender-simulator)
- [Google Scholar Profile](https://scholar.google.com/citations?view_op=view_citation&hl=en&user=juOv0f0AAAAJ&citation_for_view=juOv0f0AAAAJ:d1gkVwhDpl0C)
- Brain AWG project post — add direct URL after publication
- AI/ML AWG project post — add direct URL after publication

---

## 5. Technical Benchmark Experience

The Technical Benchmark experience transforms quantitative findings from the RR-10 mission into an interactive, data-synchronized 3D proxy:

### Murine Neural Proxy Geometry
- **Lissencephalic Bilateral Cortex**: Smooth-surfaced left and right cerebral hemispheres with a defined longitudinal fissure, reflecting rodent brain macro-morphology.
- **Rostral Olfactory Structures**: Elongated anterior olfactory bulb structures anchoring the rostral pole.
- **Hippocampal / Synaptic Core**: Inset deep synaptic core with controlled subsurface bioluminescent warm glow, modulated by neural stress indices.
- **Caudal Cerebellar Node**: Posterior cerebellar mass with subtle transverse foliation folds.
- **Telemetry Tracks and Sensor Probes**: Concentric orbital gimbal rings and sensor probes representing data acquisition passes and monitoring axes.

### Viewing Modes
- **Presentation Mode**: Clean, visual-first 3D viewing with soft contact shadows, dynamic auto-orbit, and curated studio key/fill lighting.
- **Annotated Mode**: Interactive screen-projected hotspots positioned at the Murine Cortex, Olfactory Bulbs, Synaptic Core, Cerebellar Node, and Telemetry Apparatus, providing instant derived-data summaries and dataset IDs upon hover or click.
- **Diagnostic Mode**: Instant wireframe overlay displaying polygon topology, subdivision density, and asset geometry.
- **Analytic Evidence Drawer (`[ 📊 ANALYTIC EVIDENCE ]`)**: A slide-out panel containing interactive vector SVG graphics directly reproducing primary Kaggle notebook figures:
  - **PCA of Gene Expression (Figure A)**: Sample separation across PC1 and PC2 for Cerebellum and Hippocampus with interactive tissue tabs and dual-comparison views.
  - **rRNA Removal QC (Figure B)**: Per-value variance-stabilized transformation (VST) concordance ($r = 1.000$) and rRNA-removal shift distribution histogram.

---

## 6. Evidence and Visual Mappings

The table below explicitly details the boundary between empirical scientific source inputs, procedural visual encodings, and their valid analytical interpretations:

| Source / Derived Input | Visual Encoding | Interpretation Boundary |
| :--- | :--- | :--- |
| **Cerebellum PCA (`OSD-563`)**<br>• PC1: 25.6% variance<br>• PC2: 18.5% variance | 3D coordinate distribution of left background constellation micro-spheres (`#ff5252` FLT, `#40c4ff` GC). | **Graph-derived background motif, not anatomical locations.** Depicts empirical mathematical sample variance; does not indicate physical spatial positions in brain tissue. |
| **Hippocampus PCA (`OSD-564`)**<br>• PC1: 28.3% variance<br>• PC2: 15.7% variance | 3D coordinate distribution of right background constellation micro-spheres (`#ff5252` FLT, `#40c4ff` GC). | **Graph-derived background motif, not anatomical locations.** Depicts empirical mathematical sample variance; does not indicate physical spatial positions in brain tissue. |
| **Sample Condition Context**<br>(`FLT` vs. `GC`) | Dual-color sample markers (Crimson/Coral for Flight `FLT`, Sky Blue for Ground Control `GC`). | Categorical experimental grouping identifier from NASA spaceflight mission metadata. |
| **rRNA-Removal QC Agreement**<br>• Linear concordance: $r = 1.000$<br>• Identity line $y = x$ across VST range | Vector scatter diagram with identity reference line and sample points. | **Bioinformatics data-processing QC metric.** Validates pipeline consistency across filtering steps; does not indicate biological phenomena. |
| **rRNA-Removal Shift Distribution**<br>• Peak at $\approx 0.012$<br>• Truncation spike at $0.355$ | Binned histogram showing transcript shift frequency post-ribosomal RNA depletion. | **Bioinformatics data-processing QC metric.** Characterizes library preparation impact on read density. |
| **Neuro-Adaptation Score**<br>(Derived aggregate metric) | Central neural proxy **Scale** (`0.85x` to `1.30x`). | **Derived visualization control, not a direct physiological measurement.** Stylized abstraction of aggregate response magnitude; not a measurement of brain volume or edema. |
| **Microvascular Stress Index**<br>(Derived endothelial marker response) | Deep synaptic core **Emission** intensity and subsurface warmth. | **Derived visualization control, not a direct physiological measurement.** Visual metaphor for metabolic stress; not a histological model of capillary perfusion. |
| **Cephalic Fluid Shift Indicator**<br>(Derived fluid-distribution index) | Rhythmic **Pulse** displacement rate and amplitude on the cortical surface. | **Derived visualization control, not a direct physiological measurement.** Stylized temporal kinetic effect representing cephalic fluid shifts; not an intracranial pressure transducer measurement. |
| **Hemispheric Differential Variance**<br>(Derived inter-tissue contrast) | Bilateral **Asymmetry** offset between left and right cortical lobes. | **Derived visualization control, not a direct physiological measurement.** Qualitative visual indicator of regional transcriptomic divergence. |
| **Transcriptomic Cluster Dimensionality** | Orbital **Ring Count** (2 to 4 concentric gimbal tracks) and sensor probes. | **Derived visualization control, not a direct physiological measurement.** Abstract interface metaphor for analytic dimensionality; not physical instruments orbiting brain tissue. |
| **Sample Timeline Duration** | Animation loop cycle **Timeline** length (120 to 240 frames). | **Derived visualization control, not a direct physiological measurement.** Standard temporal frame loop for real-time visualization playback. |

---

## 7. Media Companion: Commander Pip

The **Media Companion** branch presents **Commander Pip: Zero-G Odyssey**, a stylized cinematic narrative inspired by the historical and scientific context of the RR-10 mission.

- **Creative Narrative**: Follows Commander Pip, an intrepid murine astronaut on an orbital mission, designed for public engagement, outreach, and visual worldbuilding.
- **Strict Decoupling**: Driven by a separate recipe (`data/recipes/media_astro_mouse.json`), a dedicated procedural generator (`scripts/generate_media_scene.py`), and a distinct export path (`exports/media_simulation.glb`). It does not alter or contaminate the technical benchmark pipeline.
- **Real-Time PBR Assets**: The character and habitat use web-optimized, physically-based rendering (PBR) assets:
  - **Commander Pip**: Aerodynamic cream-furred silhouette, oversized translucent pink ears, electroplated gold bubble visor, 4-point aerospace-orange cross-harness, heavy-duty moon boots, dorsal life-support backpack (PLSS), and an articulated 5-segment tail with a T-wing attitude stabilizer thruster.
  - **Zero-G Habitat**: Cylindrical research habitat with an orbital centrifuge guidance rail, Earth observation porthole with atmospheric blue horizon glow, and floating nutrient spheres.
- **Non-Scientific Status**: This is a stylized narrative piece and is **not a literal historical or scientific reconstruction**.
- **Cinematic Sequence**:
  > *Cinematic companion showcase:* [Commander-Pip-orbital-habitat-cinematic-sequence.mp4](assets/Commander-Pip-orbital-habitat-cinematic-sequence.mp4)

---

## 8. Architecture

The repository adheres to a clean, modular structure verified against the active workspace:

```
blender-simulator/
├── run_pipeline.py                 # Primary CLI orchestrator (binary discovery, headless dispatch, local web server)
├── scripts/
│   ├── data_adapter.py             # Adapter mapping RR-10 benchmark JSON outputs to scene recipes
│   ├── generate_scene.py           # Technical Benchmark procedural generator (Murine Neural Proxy & PCA constellation)
│   ├── generate_media_scene.py     # Media Companion procedural generator (Commander Pip & Zero-G Habitat)
│   ├── export_scene.py             # Standalone GLB exporter and scene telemetry metadata extractor
│   ├── render_character_views.py    # Headless Cycles studio reference renderer for character turnarounds
│   └── core/                       # Modular Blender Python utility package
│       ├── __init__.py             # Package initializer
│       ├── camera.py               # Dynamic framing, sensor sizing, and Track-To constraint helpers
│       ├── lighting.py             # Three-point studio lighting rigs and atmospheric rim lights
│       └── materials.py            # PBR Principled BSDF shader constructors (Clay, Tissue, Gold Visor, Optics)
├── data/
│   ├── processed/
│   │   ├── notebook_figures_data.json  # Ground-truth PCA coordinates and QC shift distribution tables
│   │   └── sample_scene.json           # Normalized sample benchmark output
│   └── recipes/
│       ├── default_simulation.json     # Base recipe for technical neural core
│       ├── adapted_sample.json         # Adapted recipe generated from sample_scene.json
│       └── media_astro_mouse.json      # Configuration recipe for Commander Pip media scene
├── exports/
│   ├── simulation.glb              # Technical Benchmark interactive 3D asset (binary GLTF, ~1.1 MB)
│   ├── simulation.json             # Technical scene telemetry and bounding box metadata
│   ├── media_simulation.glb        # Media Companion interactive 3D asset (Commander Pip, ~688 KB)
│   └── media_simulation.json       # Media scene telemetry and object count metadata
├── project-site/                   # Public-facing research-creative project landing page
│   ├── index.html                  # Main project page entry point
│   ├── 404.html                    # Static 404 fallback page
│   ├── app.js                      # Video component, citation copy, and interactive logic
│   ├── style.css                   # Responsive space-bioscience editorial stylesheet
│   └── assets/                     # Verified reference renders and WebGL captures
├── web-viewer/                     # Interactive Three.js WebGL inspection viewer
│   ├── index.html                  # Viewer DOM layout, HUD controls, and Analytic Evidence drawer
│   ├── app.js                      # Three.js runtime, orbit controls, hotspot projection, and SVG rendering
│   └── style.css                   # Responsive styles, glassmorphic HUD, and drawer animations
├── addon/
│   └── antigravity_simulator/      # Blender 3D Viewport N-Panel integration add-on
│       ├── __init__.py             # Add-on registration and metadata
│       ├── operators.py            # Operators to generate, adapt, and export scenes
│       └── ui.py                   # Custom N-Panel UI tab layout
├── README.md                       # Public-facing project documentation
└── walkthrough.md                  # Comprehensive development walkthrough, verification logs, and renders
```

---

## 9. Quick Start

Instructions below are tailored for macOS environments (Apple Silicon or Intel).

### Prerequisites
- macOS 13+
- **Blender 4.0+** installed in `/Applications/Blender.app` (or configure the `BLENDER_BIN` environment variable)
- **Python 3.10+** (standard macOS command-line tools)

### 1. Clone the Repository
```bash
git clone https://github.com/gastondana627/blender-simulator.git
cd blender-simulator
```

### 2. Run Technical Benchmark (Generate & Export)
Run the complete technical pipeline using processed benchmark data:
```bash
./run_pipeline.py --data data/processed/sample_scene.json
```
*Outputs `exports/simulation.glb` and `exports/simulation.json` in ~2.5 seconds.*

To run procedural scene generation only (staging without GLB export):
```bash
./run_pipeline.py --generate-only --data data/processed/sample_scene.json
```

### 3. Run Media Companion (Commander Pip)
Generate and export the Commander Pip media narrative scene:
```bash
./run_pipeline.py --mode media
# Shorthand alias:
./run_pipeline.py --media
```
*Outputs `exports/media_simulation.glb` and `exports/media_simulation.json`.*

### 4. Interactive Blender Mode
To launch the full Blender desktop application with the procedural scene generated directly in the viewport:
```bash
# Open Technical Benchmark in Blender GUI:
./run_pipeline.py --interactive --data data/processed/sample_scene.json

# Open Media Companion in Blender GUI:
./run_pipeline.py --interactive --media
```

### 5. Launch the WebGL Viewer
Serve the repository via the built-in orchestrator flag:
```bash
./run_pipeline.py --serve
```
*Alternatively, start a standard Python web server:*
```bash
python3 -m http.server 8080
```
Open your browser and navigate to:
**[http://localhost:8080/web-viewer/](http://localhost:8080/web-viewer/)**

Use the navigation header to switch dynamically between **`[ 🔬 TECHNICAL BENCHMARK ]`** and **`[ 🚀 MEDIA COMPANION ]`**.

### 6. Launch the Public Project Landing Page
With the local server active on port 8080, open the editorial portfolio landing page:
**[http://localhost:8080/project-site/index.html](http://localhost:8080/project-site/index.html)**

This page provides an editorial presentation of the research context, interactive 3D viewer launch panels, factual transcriptomic findings, data-to-3D transformation tables, Commander Pip cinematic media section, and the categorized Mission Console resource hub.

### 7. GitHub Pages Deployment Configuration
- **Expected Publishing Source**: `main` branch → `/project-site` (or `/ (root)` with root redirect to `/project-site/index.html`).
- **Static Entry Point**: `project-site/index.html` (accompanied by `project-site/404.html` and root routing fallbacks).

---

## 10. Outputs

All pipeline executions produce standardized artifacts in the `exports/` directory:

| Output File | Format | Role | Description |
| :--- | :--- | :--- | :--- |
| `exports/simulation.glb` | Binary GLTF | Interactive 3D Asset | Optimized asset containing the Murine Neural Proxy, telemetry rings, background PCA constellation, and baked sinusoidal breathing animations (27,518 vertices, 37,968 faces, ~1.1 MB). |
| `exports/simulation.json` | JSON | Scene Telemetry | Evaluated scene metrics: bounding box dimensions, vertex/face counts, object hierarchy, and timeline configuration (~10 KB). |
| `exports/media_simulation.glb` | Binary GLTF | Interactive 3D Asset | Real-time PBR asset of Commander Pip in EVA suit, habitat centrifuge track, Earth porthole, and 150-frame zero-G drift loop (15,155 vertices, 23,000 faces, ~688 KB). |
| `exports/media_simulation.json` | JSON | Scene Telemetry | Evaluated character hierarchy, component counts, bounding dimensions, and animation track metadata (~15 KB). |

---

## 11. Citation and Attribution

### How to Cite This Project
If you use this data-to-3D pipeline, procedural generation architecture, or visualization proxy in academic work, benchmarks, or creative simulations, please cite:

```text
Gaston Dana. “Orbiting Minds: An RR-10 Data-to-3D Simulation Experience.” GitHub repository, 2026. URL: https://github.com/gastondana627/blender-simulator.
```

### Primary Research & Dataset Attributions
Please cite the original research teams and NASA Open Science Data Repository (OSDR) datasets:

- **NASA Rodent Research-10 (RR-10) Transcriptomics**:
  - Cerebellum Accession: [OSD-563 — Cerebellum transcriptomics from RR-10 mice](https://osdr.nasa.gov/bio/repo/data/studies/OSD-563)
  - Hippocampus Accession: [OSD-564 — Hippocampus transcriptomics from RR-10 mice](https://osdr.nasa.gov/bio/repo/data/studies/OSD-564)
  - Payload Record: [RR-10 Rodent Research 10 payload — NASA OSDR](https://osdr.nasa.gov/bio/repo/data/payloads/RR-10)
  - Mission Record: [SpaceX-21 mission record — NASA OSDR](https://osdr.nasa.gov/bio/repo/data/missions/SpaceX-21)
  - Open Science Platform: [NASA GeneLab / Open Science for Life in Space](https://genelab.nasa.gov/)
  - Legacy GeneLab Records: `[Official GeneLab GLDS-568 record — add URL if applicable]`, `[Official GeneLab GLDS-569 record — add URL if applicable]`
- **Author Profile**:
  - [Google Scholar Profile](https://scholar.google.com/citations?view_op=view_citation&hl=en&user=juOv0f0AAAAJ&citation_for_view=juOv0f0AAAAJ:d1gkVwhDpl0C)

---

## 12. Community and Contact

Inquiries, discussions, and collaborations across spaceflight biology, AI reasoning, and scientific visualization are welcome:

- **Source Code (GitHub)**: [https://github.com/gastondana627/blender-simulator](https://github.com/gastondana627/blender-simulator)
- **NASA OSDR Analysis Working Groups**: [https://science.nasa.gov/citizen-science/osdr-awg/](https://science.nasa.gov/citizen-science/osdr-awg/)
- **OSDR AWG Forum**: [https://awg.osdr.space/top](https://awg.osdr.space/top)
- **AI/ML AWG Topics**: [https://awg.osdr.space/c/awg-discussions/ai-ml/11](https://awg.osdr.space/c/awg-discussions/ai-ml/11)
- **AI/ML AWG GitHub**: [https://github.com/OpenScienceDataRepo/AI-ML_AWG](https://github.com/OpenScienceDataRepo/AI-ML_AWG)
- **AWG Projects**: [https://awg.osdr.space/c/awg-projects/20](https://awg.osdr.space/c/awg-projects/20)
- **Kaggle Profile**: `[Kaggle profile URL]`
- **Google Scholar**: [https://scholar.google.com/citations?view_op=view_citation&hl=en&user=juOv0f0AAAAJ&citation_for_view=juOv0f0AAAAJ:d1gkVwhDpl0C](https://scholar.google.com/citations?view_op=view_citation&hl=en&user=juOv0f0AAAAJ&citation_for_view=juOv0f0AAAAJ:d1gkVwhDpl0C)
- **Brain AWG Project Post**: Brain AWG project post — add direct URL after publication
- **AI/ML AWG Project Post**: AI/ML AWG project post — add direct URL after publication

---

## 13. Limitations

1. **Interactive Visualization Proxy**: The Technical Benchmark scene is an interactive, benchmark-informed visual proxy. It is **not** a validated biomedical model, anatomical reconstruction, or substitute for primary scientific analysis.
2. **Authority of Primary Literature**: Procedural visual controls (such as scale factors, emission warmth, pulsation rates, and telemetry ring counts) are qualitative visual encodings. The original Kaggle notebooks, peer-reviewed publications, and NASA OSDR accessions remain the authoritative data and analytical references.
3. **Media Branch Fictionalization**: The Media Companion (Commander Pip: Zero-G Odyssey) is stylized narrative content created for storytelling and public engagement; it should **not** be interpreted as scientific evidence, historical reconstruction, or biological simulation.

---

## 14. Credits and License

- **Project Creator**: Gaston Dana
- **Data Source**: NASA Open Science Data Repository (OSDR / GeneLab)
- **3D Assets & Pipeline Code**: Procedurally authored in Blender 4.x and Three.js.
- **Third-Party & NASA Attribution**: NASA, NASA OSDR, GeneLab, and mission program names are referenced strictly for factual identification and scientific attribution. This project is an independent computational research and visualization effort and is not affiliated with, endorsed by, or sponsored by NASA.

> [!NOTE]
> **TODO: Repository License**
> A formal open-source license file (such as MIT or Apache 2.0) has not yet been committed to this repository. Review licensing terms before broad code reuse or commercial redistribution.

### Next Steps for Public Release
- [ ] Choose and commit an open-source `LICENSE` file.
- [x] Add your verified public Google Scholar profile URL.
- [ ] Add direct URLs to the Brain AWG and AI/ML AWG project posts after publication.
- [x] Embed the finalized Miris cinematic video showcase in the Media Companion section.
- [ ] Publish the interactive WebGL viewer to GitHub Pages or dedicated project hosting.
