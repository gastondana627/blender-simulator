# Orbiting Minds: Future Missions & Research Roadmap

> **Milestone Snapshot (September 2026)**  
> Initial sprint completed: NASA OSDR RR-10 (OSD-563 / OSD-564) multi-tissue transcriptomics analyzed, count-level QC verified ($r = 1.000$), 6-model frontier AI reasoning benchmark deployed on Kaggle, and real-time 3D WebGL simulation published on production.

This document serves as an archival memory and technical roadmap for extending the *Orbiting Minds* architecture to upcoming space missions, complementary NASA OSDR datasets, and next-generation multi-modal capabilities.

---

## 1. Future & Ongoing Missions to Ingest

The primary finding from our Kaggle benchmark was **Epistemic Caution**—the fundamental failure of frontier LLMs to distinguish short-duration Low Earth Orbit (LEO) microgravity from deep-space radiation. Upcoming missions provide the exact empirical ground truth needed to stress-test this boundary.

### A. The Artemis Program (Beyond LEO & Lunar Transit)
* **BioSentinel (Artemis I CubeSat)**:
  * *Why it matters*: Flew past the Van Allen radiation belts into interplanetary deep space to measure real Galactic Cosmic Radiation (GCR) DNA damage.
  * *Integration*: Cross-referencing LEO rodent brain stress with actual deep-space yeast/biosensor survival curves to test whether AI models can quantitatively differentiate LEO vs. Interplanetary radiation regimes.
* **Artemis II & III Biological Payloads**:
  * *Why it matters*: Returning biological specimens from beyond Earth's protective magnetosphere. When Artemis multi-omics data lands on OSDR, this pipeline can ingest lunar surface vs. orbital transcriptomics.

### B. Commercial Spaceflight & High-Radiation LEO
* **Polaris Dawn & Polaris Program**:
  * *Why it matters*: Flew through the inner Van Allen radiation belt (highest orbital apogee since Apollo). Incorporates human spaceflight health data, cognitive readouts, and space adaptation syndrome biomarkers.
  * *Integration*: Bridging rodent neural transcriptomics with human astronaut neuro-ocular and cognitive performance telemetry.
* **Axiom Space Missions (Ax-2, Ax-3, Ax-4)**:
  * *Why it matters*: Routine commercial LEO research payloads generating rapid-turnaround human blood, saliva, and physiological biomarker datasets deposited directly into NASA OSDR.

### C. Complementary Rodent Research Missions in OSDR
* **OSD-102 (Rodent Research-1)**: Multi-tissue baseline assessing muscle atrophy and hepatic metabolic stress over 37 days aboard the ISS.
* **OSD-254 (Extended LEO CNS Profiles)**: Long-duration central nervous system readouts to test whether our PCA variance curves hold across extended orbital stays.
* **Spatial & Single-Cell Transcriptomics**: As NASA OSDR begins publishing 10x Genomics Visium and single-cell RNA-seq (scRNA-seq) datasets, the 3D WebGL viewer can transition from regional proxy pins to single-cell voxel clusters.

---

## 2. Technical & Architecture Extensions

### A. 3D WebGL Viewer Enhancements
- [ ] **Allen Brain Atlas Voxel Registration**: Overlay regional transcriptomic variance directly onto standard CCFv3 (Common Coordinate Framework) voxel coordinates.
- [ ] **Temporal Animation of Spaceflight Exposure**: Enable a timeline slider interpolating between Day 0 (Launch), Day 15 (Adaptation), and Day 30 (Landing) based on longitudinal models.
- [ ] **Volumetric Shaders**: Implement raymarched volumetric density shaders in Three.js representing estimated intracranial fluid shift pressure.

### B. AI Reasoning Benchmark Suite (V2)
- [ ] **Multi-Dataset Synthesis Task**: Present models with conflicting datasets (e.g., LEO microgravity vs. Ground-based Hindlimb Suspension vs. Particle Accelerator heavy-ion radiation) to test if they can identify confounding variables.
- [ ] **Code Execution Sandboxing**: Upgrade the Kaggle benchmark to automatically run and verify model-generated Bioconductor/R analysis scripts against live count tables.
- [ ] **Synthetic Biology & Countermeasure Proposing**: Benchmark whether frontier models can propose realistic radioprotective or neuroprotective countermeasures based on differentially expressed gene targets without hallucinating biochemical pathways.

### C. Commander Pip Educational Universe
- [ ] **Interactive Orbital Habitat Mode**: Expand the Blender/WebGL companion branch into an explorable 3D cupola with clickable educational hotspots explaining life support systems, animal enclosure modules (AEM), and zero-G fluid dynamics.
- [ ] **Student Science Communication Module**: A lightweight web interface allowing K-12 students and non-specialists to toggle spaceflight variables (gravity, radiation shielding, mission duration) and watch Pip's habitat and telemetry adapt in real time.

---

## 3. Retrospective Notes & Lessons Learned

1. **Empirical Rigor First**: Never compromise on raw data verification ($r = 1.000$ QC match was the anchor that made this project unassailable to academic critics).
2. **Decouple Science from Mascot**: Maintaining a strict wall between the *Technical Benchmark* (murine proxy) and the *Media Companion* (Commander Pip) allowed the project to be scientifically credible while remaining culturally engaging.
3. **The Multi-Modal Edge**: In 2026, the biggest advantage a lone technologist has is breadth without bureaucracy—connecting bioinformatics, agentic coding, 3D WebGL, and communication faster than an institutional committee can schedule a meeting.
