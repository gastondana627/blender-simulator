import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';

// DOM Elements
const container = document.getElementById('viewport-container');
const loadingOverlay = document.getElementById('loading-overlay');
const loadingText = document.getElementById('loading-text');
const valVerts = document.getElementById('val-verts');
const valFaces = document.getElementById('val-faces');
const valObjects = document.getElementById('val-objects');
const valFps = document.getElementById('val-fps');
const metadataJson = document.getElementById('metadata-json');
const btnPlay = document.getElementById('btn-play');
const btnReset = document.getElementById('btn-reset');
const speedSlider = document.getElementById('speed-slider');
const speedLabel = document.getElementById('speed-label');
const toggleXray = document.getElementById('toggle-xray');
const rowToggleXray = document.getElementById('row-toggle-xray');
const toggleWireframe = document.getElementById('toggle-wireframe');
const toggleOrbit = document.getElementById('toggle-orbit');
const toggleGrid = document.getElementById('toggle-grid');
const fileInput = document.getElementById('glb-file-input');

// Inspector Collapse Elements
const inspectorPanel = document.getElementById('inspector-panel');
const btnToggleInspector = document.getElementById('btn-toggle-inspector');
const btnCloseInspector = document.getElementById('btn-close-inspector');

// Pipeline Branch Elements
const btnBranchTechnical = document.getElementById('btn-branch-technical');
const btnBranchMedia = document.getElementById('btn-branch-media');

// Mode Switcher Elements
const btnModePresentation = document.getElementById('btn-mode-presentation');
const btnModeAnnotated = document.getElementById('btn-mode-annotated');
const btnModeDiagnostic = document.getElementById('btn-mode-diagnostic');
const annotationLayer = document.getElementById('annotation-layer');
const annotationTooltip = document.getElementById('annotation-tooltip');
const tooltipClose = document.getElementById('tooltip-close');
const btnCopyCitation = document.getElementById('btn-copy-citation');

// Mission Context Elements
const ctxDatasetId = document.getElementById('ctx-dataset-id');
const ctxMissionName = document.getElementById('ctx-mission-name');
const ctxNotebookRef = document.getElementById('ctx-notebook-ref');
const ctxFindingsText = document.getElementById('ctx-findings-text');
const citationQuote = document.getElementById('citation-quote');

// Analytics Drawer Elements (Notebook Figures A & B + RR-10 v1.1 Corpus)
const btnToggleAnalytics = document.getElementById('btn-toggle-analytics');
const analyticsDrawer = document.getElementById('analytics-drawer');
const btnCloseAnalytics = document.getElementById('btn-close-analytics');
const pcaChartViewport = document.getElementById('pca-chart-viewport');
const pcaHoverReadout = document.getElementById('pca-hover-readout');
const qcChartViewport = document.getElementById('qc-chart-viewport');
const tabPcaCerebellum = document.getElementById('tab-pca-cerebellum');
const tabPcaHippocampus = document.getElementById('tab-pca-hippocampus');
const tabPcaBoth = document.getElementById('tab-pca-both');
const drawerTabFigures = document.getElementById('drawer-tab-figures');
const drawerTabV11 = document.getElementById('drawer-tab-v1-1');
const drawerPanelFigures = document.getElementById('drawer-panel-figures');
const drawerPanelV11 = document.getElementById('drawer-panel-v1-1');
const btnCopyV11Sha = document.getElementById('btn-copy-v11-sha');
const v11ShaDisplay = document.getElementById('v11-sha-display');
const v11ShaCopyTag = document.getElementById('v11-sha-copy-tag');
const v11VerifiedBanner = document.getElementById('v11-verified-banner');
const v11ContextsBars = document.getElementById('v11-contexts-bars');
const v11ScoreboardTbody = document.getElementById('v11-scoreboard-tbody');
const v11AblationNote = document.getElementById('v11-ablation-note');
const v11RoadmapNote = document.getElementById('v11-roadmap-note');
let v11SummaryLoaded = false;
let currentPcaMode = 'cerebellum';

// Single Source of Truth: hydrated from ../data/processed/notebook_figures_data.json (fallback inline if offline)
let NOTEBOOK_ANALYTICS_DATA = {
  pca: {
    cerebellum: {
      datasetId: 'OSD-563',
      name: 'Cerebellum',
      pc1Var: '25.6%',
      pc2Var: '18.5%',
      xDomain: [-120, 195],
      yDomain: [-125, 150],
      samples: [
        { id: 'F1', cond: 'FLT', pc1: 177.0, pc2: -111.0 },
        { id: 'F3', cond: 'FLT', pc1: 12.0, pc2: 35.0 },
        { id: 'F5', cond: 'FLT', pc1: 42.0, pc2: 130.0 },
        { id: 'F7', cond: 'FLT', pc1: -76.0, pc2: -57.0 },
        { id: 'F9', cond: 'FLT', pc1: -63.0, pc2: -25.0 },
        { id: 'G1', cond: 'GC', pc1: 73.0, pc2: 6.0 },
        { id: 'G3', cond: 'GC', pc1: -108.0, pc2: -79.0 },
        { id: 'G5', cond: 'GC', pc1: -48.0, pc2: 11.0 },
        { id: 'G7', cond: 'GC', pc1: -17.0, pc2: 49.0 },
        { id: 'G9', cond: 'GC', pc1: 2.0, pc2: 42.0 },
      ],
    },
    hippocampus: {
      datasetId: 'OSD-564',
      name: 'Hippocampus',
      pc1Var: '28.3%',
      pc2Var: '15.7%',
      xDomain: [-135, 135],
      yDomain: [-125, 160],
      samples: [
        { id: 'F1', cond: 'FLT', pc1: -119.0, pc2: -38.0 },
        { id: 'F3', cond: 'FLT', pc1: -62.0, pc2: 6.0 },
        { id: 'F5', cond: 'FLT', pc1: -16.0, pc2: 144.0 },
        { id: 'F7', cond: 'FLT', pc1: -39.0, pc2: -29.0 },
        { id: 'F9', cond: 'FLT', pc1: -68.0, pc2: 3.0 },
        { id: 'G1', cond: 'GC', pc1: 73.0, pc2: 22.0 },
        { id: 'G3', cond: 'GC', pc1: 117.0, pc2: -110.0 },
        { id: 'G5', cond: 'GC', pc1: 108.0, pc2: 23.0 },
        { id: 'G7', cond: 'GC', pc1: 87.0, pc2: 26.0 },
        { id: 'G9', cond: 'GC', pc1: -85.0, pc2: -46.0 },
      ],
    },
  },
  qc: {
    datasetId: 'OSD-563',
    tissue: 'Cerebellum',
    rValue: '1.000',
    agreementPoints: [
      [5.0, 5.0], [7.5, 7.5], [10.0, 10.0], [12.5, 12.5],
      [15.0, 15.0], [17.5, 17.5], [20.0, 20.0], [22.5, 22.5], [24.5, 24.5],
    ],
    bins: [
      { x: 0.005, freq: 14100 }, { x: 0.012, freq: 17150 }, { x: 0.018, freq: 14600 },
      { x: 0.025, freq: 11500 }, { x: 0.032, freq: 9300 }, { x: 0.039, freq: 7950 },
      { x: 0.046, freq: 6700 }, { x: 0.053, freq: 5600 }, { x: 0.060, freq: 4600 },
      { x: 0.068, freq: 3950 }, { x: 0.076, freq: 3200 }, { x: 0.085, freq: 2600 },
      { x: 0.095, freq: 2200 }, { x: 0.108, freq: 1750 }, { x: 0.122, freq: 1450 },
      { x: 0.138, freq: 1400 }, { x: 0.155, freq: 1380 }, { x: 0.172, freq: 1420 },
      { x: 0.190, freq: 1500 }, { x: 0.208, freq: 1650 }, { x: 0.225, freq: 1850 },
      { x: 0.242, freq: 2100 }, { x: 0.258, freq: 2450 }, { x: 0.272, freq: 2650 },
      { x: 0.285, freq: 3100 }, { x: 0.298, freq: 3350 }, { x: 0.308, freq: 4200 },
      { x: 0.318, freq: 3450 }, { x: 0.328, freq: 2400 }, { x: 0.338, freq: 320 },
      { x: 0.355, freq: 16000 },
    ],
  },
};

function loadNotebookFiguresJson() {
  fetch('../data/processed/notebook_figures_data.json')
    .then((res) => (res.ok ? res.json() : null))
    .then((raw) => {
      if (!raw || !raw.figure_a_pca || !raw.figure_a_pca.tissues) return;
      const t = raw.figure_a_pca.tissues;
      if (t.cerebellum && t.hippocampus) {
        NOTEBOOK_ANALYTICS_DATA.pca.cerebellum = {
          datasetId: t.cerebellum.dataset_id,
          name: t.cerebellum.tissue_name,
          pc1Var: `${t.cerebellum.pc1_variance_pct}%`,
          pc2Var: `${t.cerebellum.pc2_variance_pct}%`,
          xDomain: [t.cerebellum.pc1_range[0], t.cerebellum.pc1_range[1] + 5],
          yDomain: [t.cerebellum.pc2_range[0], t.cerebellum.pc2_range[1] + 5],
          samples: t.cerebellum.samples.map((s) => ({ id: s.id, cond: s.condition, pc1: s.pc1, pc2: s.pc2 })),
        };
        NOTEBOOK_ANALYTICS_DATA.pca.hippocampus = {
          datasetId: t.hippocampus.dataset_id,
          name: t.hippocampus.tissue_name,
          pc1Var: `${t.hippocampus.pc1_variance_pct}%`,
          pc2Var: `${t.hippocampus.pc2_variance_pct}%`,
          xDomain: [t.hippocampus.pc1_range[0], t.hippocampus.pc1_range[1] + 5],
          yDomain: [t.hippocampus.pc2_range[0] - 5, t.hippocampus.pc2_range[1] + 5],
          samples: t.hippocampus.samples.map((s) => ({ id: s.id, cond: s.condition, pc1: s.pc1, pc2: s.pc2 })),
        };
      }
      if (raw.figure_b_qc) {
        NOTEBOOK_ANALYTICS_DATA.qc = {
          datasetId: raw.figure_b_qc.dataset_id,
          tissue: raw.figure_b_qc.tissue,
          rValue: Number(raw.figure_b_qc.agreement_panel.correlation_r).toFixed(3),
          agreementPoints: raw.figure_b_qc.agreement_panel.points,
          bins: raw.figure_b_qc.shift_distribution_panel.bins,
        };
      }
      if (analyticsDrawer && !analyticsDrawer.classList.contains('hidden')) {
        updatePcaDisplay(currentPcaMode);
        renderQcPanels();
      }
    })
    .catch(() => {
      // Inline fallback remains active offline
    });
}

// Branch Definitions & Authentic OSDR Hotspots
const PIPELINE_BRANCHES = {
  technical: {
    name: 'Technical Benchmark',
    glbUrl: '../exports/simulation.glb',
    metaUrl: '../exports/simulation.json',
    datasetId: 'OSD-563 / OSD-564',
    mission: 'Rodent Research-10 (SpaceX-21)',
    ref: 'cerebellum-vs-hippocampus-rr-10-spaceflight-mice.ipynb',
    status: 'Cerebellum PC1 25.6% | Hippocampus PC1 28.3% | VST r=1.000',
    citation: 'NASA OSDR OSD-563 & OSD-564: Cerebellum and Hippocampus Transcriptomics from RR-10 Spaceflight Mice (SpaceX-21).',
    cameraPos: new THREE.Vector3(5.6, 3.6, 6.4),
    cameraTarget: new THREE.Vector3(0, 0, 0),
    defaultGrid: true,
    hotspots: [
      {
        id: 'cortex',
        num: 1,
        tag: 'ANATOMICAL PROXY',
        targetNames: ['Murine_Cortex_Left', 'Murine_Cortex_Right'],
        title: 'Bilateral Murine Cortex',
        metric: 'Derived Proxy | Lissencephalic Bilateral Lobes',
        desc: 'Smooth-surfaced rodent cerebral hemispheres divided along the longitudinal fissure. Toggle Cortex X-Ray (X) to inspect the deep hippocampal synaptic core inside.',
        dataset: 'OSD-563 / OSD-564',
        defaultOffset: new THREE.Vector3(-0.6, 0.2, 0.6),
      },
      {
        id: 'olfactory',
        num: 2,
        tag: 'ROSTRAL POLE',
        targetNames: ['Murine_Olfactory_Left', 'Murine_Olfactory_Right'],
        title: 'Rostral Olfactory Bulbs',
        metric: 'Anterior Pole | Murine Chemosensory Proxy',
        desc: 'Elongated paired anterior olfactory bulbs anchoring the rostral axis of the murine neural proxy.',
        dataset: 'OSD-564',
        defaultOffset: new THREE.Vector3(0, 0.0, 1.15),
      },
      {
        id: 'hippocampus',
        num: 3,
        tag: 'SYNAPTIC CORE',
        targetNames: ['Hippocampal_Synaptic_Core'],
        title: 'Deep Hippocampal Synaptic Core',
        metric: 'OSD-564 PC1: 28.3% | PC2: 15.7% Variance',
        desc: 'Internal limbic proxy nestled within the sagittal fissure representing hippocampal synaptic plasticity and cognitive stress response under orbital flight.',
        dataset: 'OSD-564 (GLDS-569)',
        defaultOffset: new THREE.Vector3(0, 0.08, 0.1),
      },
      {
        id: 'cerebellum',
        num: 4,
        tag: 'VESTIBULAR NODE',
        targetNames: ['Murine_Cerebellar_Node'],
        title: 'Caudal Cerebellar Anchor',
        metric: 'OSD-563 PC1: 25.6% | VST rRNA QC r = 1.000',
        desc: 'Posterior cerebellar proxy capturing vestibular and sensorimotor transcriptomic adaptation across spaceflight (FLT) vs. ground control (GC) mice.',
        dataset: 'OSD-563 (GLDS-568)',
        defaultOffset: new THREE.Vector3(0, -0.1, -1.15),
      },
      {
        id: 'telemetry',
        num: 5,
        tag: 'HABITAT INSTRUMENTATION',
        targetNames: ['BioTelemetry_Probe_1_A_Hull', 'BioTelemetry_Probe_2_A_Hull', 'BioTelemetry_Probe_1_B_Hull'],
        title: 'Orbital Bio-Telemetry Sensor Probe',
        metric: '4 Gimbal Tracks | 8 Directional Sensor Probes',
        desc: 'Concentric aerospace guidance tracks and optical/radiation sensor probes encoding transcriptomic cluster dimensionality around the neural proxy.',
        dataset: 'OSD-563 / OSD-564',
        defaultOffset: new THREE.Vector3(1.9, 1.2, 0.8),
      },
    ],
  },
  media: {
    name: 'Media Storytelling Companion',
    glbUrl: '../exports/media_simulation.glb',
    metaUrl: '../exports/media_simulation.json',
    datasetId: 'OUTREACH COMPANION',
    mission: 'Astro-Mice Zero-G Odyssey (Commander Pip)',
    ref: 'media_astro_mouse.json',
    status: 'Commander Pip | Stylized Zero-G Habitat | 150 Frames',
    citation: 'Orbiting Minds Media Companion: "Commander Pip: Zero-G Orbital Habitat" (Stylized outreach storytelling companion inspired by NASA RR-10).',
    cameraPos: new THREE.Vector3(2.85, 1.05, 3.85),
    cameraTarget: new THREE.Vector3(0, 0.12, 0),
    defaultGrid: false,
    hotspots: [
      {
        id: 'pip_suit',
        num: 1,
        tag: 'ASTRONAUT EVA SUIT',
        targetNames: ['Commander_Pip_Torso', 'Commander_Pip_Harness_Buckle', 'Commander_Pip_Mission_Patch'],
        title: 'Commander Pip EVA Spacesuit',
        metric: 'Aerospace Matte Composite | 4-Point Cross Harness',
        desc: 'Tailored matte-white EVA micro-suit with burnt-orange harness straps, brushed-metal buckle, and RR-10 mission shoulder insignia for zero-G habitat storytelling.',
        dataset: 'Media Companion',
        defaultOffset: new THREE.Vector3(0, 0.1, 0.35),
      },
      {
        id: 'pip_visor',
        num: 2,
        tag: 'HELMET & AVIONICS',
        targetNames: ['Commander_Pip_Visor', 'Commander_Pip_Helmet_Bezel', 'Commander_Pip_Head_Cranium'],
        title: 'Gold Reflective Bubble Visor',
        metric: 'Warm-Gold Metallic Finish | Orbital Glare Shield',
        desc: 'Electroplated gold reflective bubble visor with silver bezel and side pivot discs catching studio environment reflections in real-time WebGL PBR.',
        dataset: 'Media Companion',
        defaultOffset: new THREE.Vector3(0, 0.55, 0.3),
      },
      {
        id: 'pip_tail',
        num: 3,
        tag: 'T-WING STABILIZER',
        targetNames: ['Commander_Pip_Tail_T_Wing', 'Commander_Pip_Tail_T_Collar', 'Commander_Pip_Tail_Seg_5'],
        title: 'Articulated Tail & T-Wing Thruster',
        metric: '5-Segment Articulation | Micro-Attitude Control',
        desc: 'Articulated murine tail terminating in an aerodynamic white-and-orange T-wing stabilizer for stylized zero-G pitch and yaw balance.',
        dataset: 'Media Companion',
        defaultOffset: new THREE.Vector3(0, 0.5, -0.7),
      },
      {
        id: 'nutrient_sphere',
        num: 4,
        tag: 'ZERO-G ENRICHMENT',
        targetNames: ['ZeroG_Nutrient_Sphere', 'ZeroG_Nutrient_Nucleus'],
        title: 'Zero-G Nutrient Sphere',
        metric: 'Surface Tension | Floating Orbital Droplet',
        desc: 'Suspended luminescent nutrient bubble floating weightlessly in front of Pip, illustrating microgravity fluid surface tension.',
        dataset: 'Media Companion',
        defaultOffset: new THREE.Vector3(0.36, 0.15, 0.65),
      },
      {
        id: 'earth_porthole',
        num: 5,
        tag: 'ORBITAL OBSERVATION',
        targetNames: ['Habitat_Earth_Horizon', 'Habitat_Porthole_Frame'],
        title: 'Earth Observation Porthole',
        metric: '408 km LEO | Stylized Atmospheric Limb',
        desc: 'Habitat observation cupola framing Earth curvature and atmospheric horizon glow during orbital sunrise passes.',
        dataset: 'Media Companion',
        defaultOffset: new THREE.Vector3(0, 0.5, -1.5),
      },
    ],
  },
};

// Three.js State
let scene, camera, renderer, controls, mixer, pmremGenerator;
let currentModel = null;
let gridHelper = null;
let starField = null;
let keyLight = null;
let rimLight = null;
let isPlaying = true;
let playbackSpeed = 1.0;
let isXrayEnabled = false;
let clock = new THREE.Clock();
let currentBranch = 'technical';
let currentViewMode = 'presentation';
let hotspotElements = [];
let originalMaterialProps = new Map();
let diagnosticMaterialCache = new Map();
let earthHorizonTexture = null;

// Smooth Camera Focus Animation State
let cameraTransition = null;

// Pre-allocated Scratch Vectors (zero per-frame GC churn in updateHotspots)
const _tempV = new THREE.Vector3();
const _worldPos = new THREE.Vector3();
const _toPoint = new THREE.Vector3();
const _toCam = new THREE.Vector3();
const _proj = new THREE.Vector3();

// FPS Calculation
let frameCount = 0;
let lastFpsUpdate = performance.now();

function createEarthPortholeTexture() {
  if (earthHorizonTexture) return earthHorizonTexture;
  const canvas = document.createElement('canvas');
  canvas.width = 512;
  canvas.height = 512;
  const ctx = canvas.getContext('2d');

  // Deep orbital space gradient transitioning to Earth limb
  const bg = ctx.createRadialGradient(256, 360, 40, 256, 360, 340);
  bg.addColorStop(0.0, '#0c4a6e');
  bg.addColorStop(0.38, '#0284c7');
  bg.addColorStop(0.56, '#38bdf8');
  bg.addColorStop(0.66, '#e0f2fe');
  bg.addColorStop(0.76, '#0f172a');
  bg.addColorStop(1.0, '#020617');
  ctx.fillStyle = bg;
  ctx.fillRect(0, 0, 512, 512);

  // Subtle stylized cloud wisps over ocean hemisphere
  ctx.save();
  ctx.globalAlpha = 0.22;
  ctx.fillStyle = '#ffffff';
  for (let i = 0; i < 18; i++) {
    const cx = 80 + ((i * 73) % 350);
    const cy = 230 + ((i * 41) % 190);
    const rx = 28 + (i % 5) * 14;
    const ry = 7 + (i % 3) * 4;
    ctx.beginPath();
    ctx.ellipse(cx, cy, rx, ry, (i % 4) * 0.2 - 0.3, 0, Math.PI * 2);
    ctx.fill();
  }
  ctx.restore();

  // Subtle star dots in upper black sky region
  ctx.fillStyle = 'rgba(255,255,255,0.7)';
  for (let i = 0; i < 40; i++) {
    const sx = (i * 97 + 19) % 512;
    const sy = (i * 53 + 11) % 150;
    const r = (i % 3 === 0) ? 1.5 : 0.9;
    ctx.beginPath();
    ctx.arc(sx, sy, r, 0, Math.PI * 2);
    ctx.fill();
  }

  earthHorizonTexture = new THREE.CanvasTexture(canvas);
  earthHorizonTexture.colorSpace = THREE.SRGBColorSpace;
  return earthHorizonTexture;
}

function createStarfield() {
  const count = 650;
  const positions = new Float32Array(count * 3);
  const colors = new Float32Array(count * 3);
  for (let i = 0; i < count; i++) {
    // Deterministic pseudo-random spherical shell (radius 18..42)
    const u = ((i * 2654435761) >>> 0) / 4294967295;
    const v = (((i + 137) * 2246822519) >>> 0) / 4294967295;
    const w = (((i + 911) * 3266489917) >>> 0) / 4294967295;
    const theta = u * Math.PI * 2;
    const phi = Math.acos(2 * v - 1);
    const r = 18 + w * 24;
    positions[i * 3] = r * Math.sin(phi) * Math.cos(theta);
    positions[i * 3 + 1] = r * Math.cos(phi);
    positions[i * 3 + 2] = r * Math.sin(phi) * Math.sin(theta);

    const tint = i % 5 === 0 ? [0.65, 0.88, 1.0] : i % 7 === 0 ? [1.0, 0.86, 0.72] : [0.88, 0.92, 0.98];
    colors[i * 3] = tint[0];
    colors[i * 3 + 1] = tint[1];
    colors[i * 3 + 2] = tint[2];
  }
  const geom = new THREE.BufferGeometry();
  geom.setAttribute('position', new THREE.BufferAttribute(positions, 3));
  geom.setAttribute('color', new THREE.BufferAttribute(colors, 3));
  const mat = new THREE.PointsMaterial({
    size: 0.09,
    vertexColors: true,
    transparent: true,
    opacity: 0.65,
    depthWrite: false,
  });
  return new THREE.Points(geom, mat);
}

function init() {
  scene = new THREE.Scene();
  scene.background = new THREE.Color(0x07090f);
  scene.fog = new THREE.FogExp2(0x07090f, 0.026);

  camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.1, 120);
  camera.position.copy(PIPELINE_BRANCHES.technical.cameraPos);

  renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false, powerPreference: 'high-performance' });
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.05;
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  container.appendChild(renderer.domElement);

  // Studio IBL reflections so metallic probes, rings, and Commander Pip's gold visor gleam instead of rendering black
  pmremGenerator = new THREE.PMREMGenerator(renderer);
  const envTex = pmremGenerator.fromScene(new RoomEnvironment(), 0.04).texture;
  scene.environment = envTex;
  if ('environmentIntensity' in scene) {
    scene.environmentIntensity = 0.65;
  }

  controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.dampingFactor = 0.06;
  controls.autoRotate = true;
  controls.autoRotateSpeed = 0.65;
  controls.minDistance = 1.6;
  controls.maxDistance = 18.0;
  controls.target.set(0, 0, 0);

  // Cancel scripted camera transition if user manually grabs orbit controls
  controls.addEventListener('start', () => {
    cameraTransition = null;
  });

  setupLighting();

  gridHelper = new THREE.GridHelper(20, 40, 0x38bdf8, 0x162033);
  gridHelper.position.y = -2.5;
  gridHelper.material.transparent = true;
  gridHelper.material.opacity = 0.45;
  scene.add(gridHelper);

  starField = createStarfield();
  scene.add(starField);

  window.addEventListener('resize', onWindowResize);
  document.addEventListener('visibilitychange', () => {
    if (!document.hidden) {
      clock.getDelta();
    }
  });

  setupUIHandlers();
  loadNotebookFiguresJson();

  // Default collapsed Inspector on narrow screens so mobile/tablet users see the 3D scene immediately
  if (window.innerWidth < 1100) {
    setInspectorOpen(false);
  }

  // Parse branch & drawer intent from URL query, hash, or sessionStorage
  let initialBranch = 'technical';
  let initialDrawer = null;
  try {
    const urlParams = new URLSearchParams(window.location.search);
    const paramBranch = urlParams.get('branch');
    const paramDrawer = urlParams.get('drawer');
    const hashLower = window.location.hash.toLowerCase();
    const hashBranch = hashLower.includes('media') || hashLower.includes('pip');
    const storedBranch = sessionStorage.getItem('preferred_branch');
    if (paramBranch === 'media' || hashBranch || storedBranch === 'media') {
      initialBranch = 'media';
      sessionStorage.removeItem('preferred_branch');
    }
    if (paramDrawer === 'v1-1' || paramDrawer === 'figures') {
      initialDrawer = paramDrawer;
    }
  } catch (_) {
    // Graceful fallback
  }

  // Always route initial load through switchBranch so Dataset ID & camera defaults sync cleanly
  switchBranch(initialBranch);

  if (initialBranch === 'technical' && initialDrawer) {
    toggleAnalyticsDrawer(true);
    selectDrawerTab(initialDrawer, false);
  }

  animate();
}

function setupLighting() {
  const hemi = new THREE.HemisphereLight(0x9bc4ff, 0x1f1410, 0.36);
  scene.add(hemi);

  keyLight = new THREE.DirectionalLight(0xfff1e4, 1.35);
  keyLight.position.set(7.5, 9.5, 4.5);
  keyLight.castShadow = true;
  keyLight.shadow.mapSize.width = 2048;
  keyLight.shadow.mapSize.height = 2048;
  keyLight.shadow.bias = -0.0005;
  scene.add(keyLight);

  const fillLight = new THREE.DirectionalLight(0x6ea8fe, 0.55);
  fillLight.position.set(-7, 2.5, -3);
  scene.add(fillLight);

  rimLight = new THREE.DirectionalLight(0x40c4ff, 1.45);
  rimLight.position.set(-1.5, -3.5, -7);
  scene.add(rimLight);
}

function disposeModel(model) {
  if (!model) return;
  model.traverse((child) => {
    if (child.isMesh) {
      if (child.geometry) child.geometry.dispose();
      const mats = Array.isArray(child.material) ? child.material : [child.material];
      mats.forEach((mat) => {
        if (!mat) return;
        for (const key of Object.keys(mat)) {
          const val = mat[key];
          if (val && val.isTexture && val !== earthHorizonTexture) {
            val.dispose();
          }
        }
        mat.dispose();
      });
    }
  });
  diagnosticMaterialCache.forEach((m) => m.dispose());
  diagnosticMaterialCache.clear();
  originalMaterialProps.clear();
}

function enhanceLoadedSceneMaterials(model, branchKey) {
  originalMaterialProps.clear();

  model.traverse((child) => {
    if (!child.isMesh || !child.material) return;
    const mat = child.material;
    const name = child.name || '';

    // Improve sculptural PBR readability on Technical neural tissue & metals
    if (branchKey === 'technical') {
      if (name.startsWith('Murine_Cortex') || name.startsWith('Murine_Olfactory') || name === 'Murine_Cerebellar_Node') {
        if (mat.color) {
          // Deepen washed-out pale peach into warm sculpted terracotta-clay so contour shadows read clearly
          mat.color.setRGB(0.64, 0.42, 0.35);
        }
        // Dampen GLB's high baked emission (~5.4) so directional lighting & shadows sculpt the lobes
        if (mat.emissive) {
          mat.emissive.setRGB(0.35, 0.10, 0.06);
          mat.emissiveIntensity = 0.08;
        }
        mat.roughness = 0.56;
        mat.metalness = 0.05;
        mat.envMapIntensity = 0.55;
        mat.needsUpdate = true;
      } else if (name === 'Hippocampal_Synaptic_Core') {
        if (mat.emissive) {
          mat.emissive.setHex(0x00e5ff);
          mat.emissiveIntensity = 1.8;
        }
        mat.roughness = 0.25;
        mat.needsUpdate = true;
      } else if (name.includes('Probe') || name.includes('Track') || name.includes('Scaffold')) {
        mat.envMapIntensity = 1.2;
        mat.needsUpdate = true;
      }
    } else if (branchKey === 'media') {
      if (name === 'Habitat_Earth_Horizon') {
        mat.map = createEarthPortholeTexture();
        if (mat.color) mat.color.setHex(0xffffff);
        if (mat.emissive) {
          mat.emissive.setHex(0x1e6091);
          mat.emissiveIntensity = 0.32;
        }
        mat.roughness = 0.45;
        mat.metalness = 0.05;
        mat.needsUpdate = true;
      } else if (name.includes('Visor')) {
        mat.metalness = 0.92;
        mat.roughness = 0.12;
        mat.envMapIntensity = 1.35;
        mat.needsUpdate = true;
      }
    }

    // Snapshot pristine material state for clean X-Ray / Diagnostic toggling
    originalMaterialProps.set(child.uuid, {
      material: mat,
      transparent: mat.transparent,
      opacity: mat.opacity,
      depthWrite: mat.depthWrite,
      wireframe: mat.wireframe,
    });
  });
}

function applyCortexXray(enabled) {
  isXrayEnabled = enabled;
  if (toggleXray) toggleXray.checked = enabled;
  if (!currentModel || currentBranch !== 'technical' || currentViewMode === 'diagnostic') return;

  currentModel.traverse((child) => {
    if (!child.isMesh || !child.material) return;
    const name = child.name || '';
    if (name.startsWith('Murine_Cortex') || name.startsWith('Murine_Olfactory') || name === 'Murine_Cerebellar_Node') {
      const snap = originalMaterialProps.get(child.uuid);
      if (!snap) return;
      if (enabled) {
        child.material.transparent = true;
        child.material.opacity = 0.30;
        child.material.depthWrite = false;
      } else {
        child.material.transparent = snap.transparent;
        child.material.opacity = snap.opacity;
        child.material.depthWrite = snap.depthWrite;
      }
      child.material.needsUpdate = true;
    }
  });
}

function loadSimulationModel(url, branchKey) {
  loadingOverlay.style.display = 'flex';
  loadingOverlay.style.opacity = '1';
  loadingText.textContent = 'Loading GLB Asset...';

  const loader = new GLTFLoader();
  loader.load(
    url,
    (gltf) => {
      if (currentModel) {
        scene.remove(currentModel);
        disposeModel(currentModel);
      }

      currentModel = gltf.scene;

      const box = new THREE.Box3().setFromObject(currentModel);
      const center = box.getCenter(new THREE.Vector3());
      currentModel.position.sub(center);
      scene.add(currentModel);

      if (gltf.animations && gltf.animations.length > 0) {
        mixer = new THREE.AnimationMixer(currentModel);
        gltf.animations.forEach((clip) => {
          mixer.clipAction(clip).play();
        });
      } else {
        mixer = null;
      }

      // Authoritative live Three.js geometry stats (eliminates async overwrite race with simulation.json)
      let totalV = 0;
      let totalF = 0;
      let objCount = 0;

      currentModel.traverse((child) => {
        if (child.isMesh) {
          child.castShadow = true;
          child.receiveShadow = true;
          objCount++;
          const geom = child.geometry;
          if (geom.attributes.position) {
            totalV += geom.attributes.position.count;
          }
          if (geom.index) {
            totalF += geom.index.count / 3;
          } else if (geom.attributes.position) {
            totalF += geom.attributes.position.count / 3;
          }
        }
      });

      valVerts.textContent = totalV.toLocaleString();
      valFaces.textContent = Math.round(totalF).toLocaleString();
      valObjects.textContent = objCount;

      enhanceLoadedSceneMaterials(currentModel, branchKey);
      setupHotspotElements();
      setViewMode(currentViewMode);
      if (branchKey === 'technical' && isXrayEnabled) {
        applyCortexXray(true);
      }

      loadingOverlay.style.opacity = '0';
      setTimeout(() => {
        loadingOverlay.style.display = 'none';
      }, 360);
    },
    (xhr) => {
      if (xhr.lengthComputable) {
        const percent = Math.round((xhr.loaded / xhr.total) * 100);
        loadingText.textContent = `Loading GLB Asset: ${percent}%`;
      }
    },
    (err) => {
      console.warn('Could not load GLB URL, waiting for local file input:', err);
      loadingText.textContent = 'Ready (Load GLB via Inspector button)';
      setTimeout(() => {
        loadingOverlay.style.display = 'none';
      }, 900);
    }
  );
}

function loadSimulationMetadata(url) {
  fetch(url)
    .then((res) => {
      if (!res.ok) throw new Error('Metadata not found');
      return res.json();
    })
    .then((data) => {
      metadataJson.textContent = JSON.stringify(data, null, 2);
    })
    .catch(() => {
      metadataJson.textContent = '// Serve repository via HTTP (python3 run_pipeline.py --serve) to inspect recipe JSON.';
    });
}

function setupHotspotElements() {
  if (!annotationLayer) return;
  annotationLayer.innerHTML = '';
  hotspotElements = [];

  const branchCfg = PIPELINE_BRANCHES[currentBranch] || PIPELINE_BRANCHES.technical;
  branchCfg.hotspots.forEach((config) => {
    const el = document.createElement('button');
    el.type = 'button';
    el.className = 'hotspot-marker';
    el.dataset.id = config.id;
    el.setAttribute('aria-label', `${config.num}. ${config.title}`);
    el.innerHTML = `
      <div class="hotspot-pulse"></div>
      <div class="hotspot-dot">${config.num}</div>
    `;

    el.addEventListener('mouseenter', () => showTooltipForConfig(config, el));
    el.addEventListener('focus', () => showTooltipForConfig(config, el));
    el.addEventListener('click', (e) => {
      e.stopPropagation();
      showTooltipForConfig(config, el);
      focusCameraOnHotspot(config);
    });

    annotationLayer.appendChild(el);
    hotspotElements.push({ config, element: el });
  });
}

function renderPcaScatterPlot(tissueKey, width = 420, height = 220) {
  const data = NOTEBOOK_ANALYTICS_DATA.pca[tissueKey];
  if (!data) return '';

  const padLeft = 45;
  const padRight = 20;
  const padTop = 28;
  const padBottom = 35;
  const plotW = width - padLeft - padRight;
  const plotH = height - padTop - padBottom;

  const [xMin, xMax] = data.xDomain;
  const [yMin, yMax] = data.yDomain;
  const scaleX = (val) => padLeft + ((val - xMin) / (xMax - xMin)) * plotW;
  const scaleY = (val) => padTop + ((yMax - val) / (yMax - yMin)) * plotH;
  const zeroX = scaleX(0);
  const zeroY = scaleY(0);

  let svg = `<svg class="svg-chart" viewBox="0 0 ${width} ${height}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="PCA scatter plot for ${data.name} (${data.datasetId})">`;
  svg += `<rect x="${padLeft}" y="${padTop}" width="${plotW}" height="${plotH}" fill="rgba(0,0,0,0.3)" stroke="rgba(255,255,255,0.12)" stroke-width="1" />`;

  if (zeroX >= padLeft && zeroX <= padLeft + plotW) {
    svg += `<line x1="${zeroX}" y1="${padTop}" x2="${zeroX}" y2="${padTop + plotH}" stroke="rgba(255,255,255,0.22)" stroke-width="1" />`;
  }
  if (zeroY >= padTop && zeroY <= padTop + plotH) {
    svg += `<line x1="${padLeft}" y1="${zeroY}" x2="${padLeft + plotW}" y2="${zeroY}" stroke="rgba(255,255,255,0.22)" stroke-width="1" />`;
  }

  [-100, -50, 0, 50, 100, 150].forEach((tick) => {
    if (tick >= xMin && tick <= xMax) {
      const tx = scaleX(tick);
      svg += `<line x1="${tx}" y1="${padTop}" x2="${tx}" y2="${padTop + plotH}" class="chart-grid" />`;
      svg += `<text x="${tx}" y="${padTop + plotH + 13}" class="chart-label" text-anchor="middle">${tick}</text>`;
    }
    if (tick >= yMin && tick <= yMax) {
      const ty = scaleY(tick);
      svg += `<line x1="${padLeft}" y1="${ty}" x2="${padLeft + plotW}" y2="${ty}" class="chart-grid" />`;
      svg += `<text x="${padLeft - 6}" y="${ty + 3}" class="chart-label" text-anchor="end">${tick}</text>`;
    }
  });

  svg += `<text x="${padLeft + 4}" y="${padTop - 10}" class="chart-title">${data.name} (${data.datasetId})</text>`;
  svg += `<text x="${padLeft + plotW / 2}" y="${height - 6}" class="chart-label" text-anchor="middle">PC1 (${data.pc1Var} variance)</text>`;
  svg += `<text x="12" y="${padTop + plotH / 2}" class="chart-label" text-anchor="middle" transform="rotate(-90 12 ${padTop + plotH / 2})">PC2 (${data.pc2Var} variance)</text>`;

  data.samples.forEach((s) => {
    const cx = scaleX(s.pc1);
    const cy = scaleY(s.pc2);
    const color = s.cond === 'FLT' ? '#e04b4b' : '#3b82f6';
    const tip = `${data.name} ${s.id} [${s.cond}] · PC1: ${s.pc1.toFixed(1)}, PC2: ${s.pc2.toFixed(1)}`;
    svg += `<g class="sample-group" tabindex="0" data-tooltip="${tip}">
      <title>${tip}</title>
      <circle cx="${cx}" cy="${cy}" r="5.5" fill="${color}" stroke="#ffffff" stroke-width="1.2" class="chart-dot" />
      <text x="${cx + 6}" y="${cy - 4}" class="chart-dot-label">${s.id}</text>
    </g>`;
  });

  svg += `</svg>`;
  return svg;
}

function bindPcaSampleReadout() {
  if (!pcaChartViewport || !pcaHoverReadout) return;
  pcaChartViewport.querySelectorAll('.sample-group').forEach((grp) => {
    const show = () => {
      pcaHoverReadout.textContent = grp.getAttribute('data-tooltip') || '';
    };
    grp.addEventListener('mouseenter', show);
    grp.addEventListener('focus', show);
  });
}

function updatePcaDisplay(mode = 'cerebellum') {
  if (!pcaChartViewport) return;
  currentPcaMode = mode;

  [tabPcaCerebellum, tabPcaHippocampus, tabPcaBoth].forEach((tab) => {
    if (!tab) return;
    tab.classList.toggle('active', tab.dataset.target === mode);
  });

  if (mode === 'cerebellum') {
    pcaChartViewport.innerHTML = renderPcaScatterPlot('cerebellum');
  } else if (mode === 'hippocampus') {
    pcaChartViewport.innerHTML = renderPcaScatterPlot('hippocampus');
  } else {
    pcaChartViewport.innerHTML = renderPcaScatterPlot('cerebellum') + renderPcaScatterPlot('hippocampus');
  }
  bindPcaSampleReadout();
}

function renderQcPanels(width = 420) {
  if (!qcChartViewport) return;
  const qcData = NOTEBOOK_ANALYTICS_DATA.qc;

  const h1 = 150;
  const padLeft = 45;
  const padRight = 20;
  const padTop = 26;
  const padBottom = 32;
  const pW = width - padLeft - padRight;
  const pH = h1 - padTop - padBottom;
  const [vMin, vMax] = [5.0, 25.0];
  const scaleV = (v) => padLeft + ((v - vMin) / (vMax - vMin)) * pW;
  const scaleVY = (v) => padTop + ((vMax - v) / (vMax - vMin)) * pH;

  let svg1 = `<div class="qc-subpanel">
    <svg class="svg-chart" viewBox="0 0 ${width} ${h1}" xmlns="http://www.w3.org/2000/svg">
      <rect x="${padLeft}" y="${padTop}" width="${pW}" height="${pH}" fill="rgba(0,0,0,0.3)" stroke="rgba(255,255,255,0.12)" stroke-width="1" />
      <line x1="${scaleV(5.0)}" y1="${scaleVY(5.0)}" x2="${scaleV(24.5)}" y2="${scaleVY(24.5)}" stroke="#ef4444" stroke-dasharray="3 3" stroke-width="1.4" />`;

  [5.0, 10.0, 15.0, 20.0, 25.0].forEach((t) => {
    const tx = scaleV(t);
    const ty = scaleVY(t);
    svg1 += `<line x1="${tx}" y1="${padTop}" x2="${tx}" y2="${padTop + pH}" class="chart-grid" />`;
    svg1 += `<text x="${tx}" y="${padTop + pH + 12}" class="chart-label" text-anchor="middle">${t.toFixed(1)}</text>`;
    svg1 += `<line x1="${padLeft}" y1="${ty}" x2="${padLeft + pW}" y2="${ty}" class="chart-grid" />`;
    svg1 += `<text x="${padLeft - 6}" y="${ty + 3}" class="chart-label" text-anchor="end">${t.toFixed(1)}</text>`;
  });

  qcData.agreementPoints.forEach(([x, y]) => {
    svg1 += `<circle cx="${scaleV(x)}" cy="${scaleVY(y)}" r="2.8" fill="#38bdf8" />`;
  });

  svg1 += `
      <text x="${padLeft + 4}" y="${padTop - 8}" class="chart-title">Cerebellum: Per-Value Agreement (r = ${qcData.rValue})</text>
      <text x="${padLeft + pW / 2}" y="${h1 - 6}" class="chart-label" text-anchor="middle">VST counts (rRNA included)</text>
      <text x="12" y="${padTop + pH / 2}" class="chart-label" text-anchor="middle" transform="rotate(-90 12 ${padTop + pH / 2})">VST (rRNA removed)</text>
      <text x="${padLeft + 10}" y="${padTop + 16}" fill="#ef4444" font-size="8px" font-family="var(--font-mono)">--- y = x</text>
    </svg>
  </div>`;

  const h2 = 160;
  const pW2 = width - padLeft - padRight;
  const pH2 = h2 - padTop - padBottom;
  const [dMin, dMax] = [0.0, 0.36];
  const maxFreq = 18000;
  const scaleDX = (d) => padLeft + ((d - dMin) / (dMax - dMin)) * pW2;
  const scaleDY = (f) => padTop + ((maxFreq - f) / maxFreq) * pH2;

  let svg2 = `<div class="qc-subpanel">
    <svg class="svg-chart" viewBox="0 0 ${width} ${h2}" xmlns="http://www.w3.org/2000/svg">
      <rect x="${padLeft}" y="${padTop}" width="${pW2}" height="${pH2}" fill="rgba(0,0,0,0.3)" stroke="rgba(255,255,255,0.12)" stroke-width="1" />`;

  [0, 5000, 10000, 15000].forEach((freq) => {
    const fy = scaleDY(freq);
    svg2 += `<line x1="${padLeft}" y1="${fy}" x2="${padLeft + pW2}" y2="${fy}" class="chart-grid" />`;
    svg2 += `<text x="${padLeft - 6}" y="${fy + 3}" class="chart-label" text-anchor="end">${freq}</text>`;
  });

  [0.0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35].forEach((dt) => {
    const dx = scaleDX(dt);
    svg2 += `<line x1="${dx}" y1="${padTop}" x2="${dx}" y2="${padTop + pH2}" class="chart-grid" />`;
    svg2 += `<text x="${dx}" y="${padTop + pH2 + 12}" class="chart-label" text-anchor="middle">${dt.toFixed(2)}</text>`;
  });

  const barW = Math.max(2, pW2 / qcData.bins.length - 1);
  qcData.bins.forEach((b) => {
    const bx = scaleDX(b.x);
    const by = scaleDY(b.freq);
    const bH = scaleDY(0) - by;
    svg2 += `<rect x="${bx}" y="${by}" width="${barW}" height="${Math.max(1, bH)}" fill="#ea580c" stroke="rgba(255,255,255,0.2)" stroke-width="0.5" />`;
  });

  svg2 += `
      <text x="${padLeft + 4}" y="${padTop - 8}" class="chart-title">Distribution of rRNA-Removal Shift</text>
      <text x="${padLeft + pW2 / 2}" y="${h2 - 6}" class="chart-label" text-anchor="middle">Difference (rRNA-removed minus rRNA-included)</text>
      <text x="12" y="${padTop + pH2 / 2}" class="chart-label" text-anchor="middle" transform="rotate(-90 12 ${padTop + pH2 / 2})">Frequency</text>
    </svg>
  </div>`;

  qcChartViewport.innerHTML = svg1 + svg2;
}

function selectDrawerTab(targetKey, shouldFocus = false) {
  const pairs = [
    { key: 'figures', tab: drawerTabFigures, panel: drawerPanelFigures },
    { key: 'v1-1', tab: drawerTabV11, panel: drawerPanelV11 },
  ];
  pairs.forEach(({ key, tab, panel }) => {
    const isActive = key === targetKey;
    if (tab) {
      tab.setAttribute('aria-selected', isActive ? 'true' : 'false');
      tab.toggleAttribute('focusgroupstart', isActive);
      tab.tabIndex = isActive ? 0 : -1;
      if (isActive && shouldFocus) {
        tab.focus();
      }
    }
    if (panel) {
      if (isActive) {
        panel.removeAttribute('hidden');
        panel.setAttribute('tabindex', '0');
      } else {
        panel.hidden = 'until-found';
        panel.removeAttribute('tabindex');
      }
    }
  });

  if (targetKey === 'v1-1' && !v11SummaryLoaded) {
    loadV11PublicSummary();
  }
}

function fmtPct(val) {
  if (typeof val !== 'number' || Number.isNaN(val)) return '--';
  return `${(val * 100).toFixed(1)}%`;
}

function escapeHtml(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function normalizeModelSlug(model) {
  return model === 'gemini-3.5-flash-lite' ? 'google/gemini-3.5-flash-lite' : model;
}

function loadV11PublicSummary() {
  fetch('../data/processed/rr10_v1_1_public_summary.json')
    .then((res) => {
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      return res.json();
    })
    .then((data) => {
      v11SummaryLoaded = true;
      renderV11PublicSummary(data);
    })
    .catch((err) => {
      console.warn('Could not fetch RR-10 v1.1 public summary:', err);
      if (v11ScoreboardTbody) {
        v11ScoreboardTbody.innerHTML =
          '<tr><td colspan="6">Serve repository via HTTP to load v1.1 public summary JSON.</td></tr>';
      }
    });
}

function renderV11PublicSummary(data) {
  const corpus = data.corpus || {};
  const sha = data.canonical_sha256 || '';
  if (v11VerifiedBanner) {
    v11VerifiedBanner.textContent = `v1.1 Verified · ${(corpus.total_items || 5630).toLocaleString()} Items · ${(corpus.matched_pairs || 2815).toLocaleString()} Pairs · ${corpus.n_osd_datasets || 34} OSD Studies`;
  }
  if (btnCopyV11Sha && sha) {
    btnCopyV11Sha.dataset.sha = sha;
    if (v11ShaDisplay) {
      v11ShaDisplay.textContent = `${sha.slice(0, 8)}...${sha.slice(-6)}`;
    }
  }

  if (v11ContextsBars && Array.isArray(data.contexts)) {
    const sortedCtx = [...data.contexts].sort((a, b) => b.pairs - a.pairs);
    const maxPairs = Math.max(...sortedCtx.map((c) => c.pairs), 1);
    v11ContextsBars.innerHTML = sortedCtx
      .map((c) => {
        const pct = Math.max(2, (c.pairs / maxPairs) * 100);
        return `
          <div class="v11-ctx-row">
            <div class="v11-ctx-meta">
              <span class="v11-ctx-name" title="${escapeHtml(c.context)}">${escapeHtml(c.context)}</span>
              <div class="v11-ctx-track"><div class="v11-ctx-fill" style="width:${pct.toFixed(1)}%"></div></div>
            </div>
            <span class="v11-ctx-val">${c.pairs.toLocaleString()} pr · ${c.items.toLocaleString()}</span>
          </div>`;
      })
      .join('');
  }

  if (v11ScoreboardTbody) {
    const rows = [];
    const baselines = (data.verification && data.verification.baselines) || {};
    if (baselines.gold_oracle_5630) {
      const b = baselines.gold_oracle_5630;
      rows.push({
        label: 'Gold Oracle (5,630)',
        n: b.n_items,
        pdr: b.pdr,
        trapOver: b.trap_overclaim_rate,
        ctrlAcc: b.control_accuracy,
        ctrlAbst: b.control_abstention_rate,
        cls: 'v11-row-baseline',
      });
    }
    if (baselines.all_indeterminate_5630) {
      const b = baselines.all_indeterminate_5630;
      rows.push({
        label: 'All-Indeterminate',
        n: b.n_items,
        pdr: b.pdr,
        trapOver: b.trap_overclaim_rate,
        ctrlAcc: b.control_accuracy,
        ctrlAbst: b.control_abstention_rate,
        cls: 'v11-row-baseline',
      });
    }
    const sb = data.scoreboard || {};
    (sb.full_5630_neutral_runs || []).forEach((run) => {
      rows.push({
        label: normalizeModelSlug(run.model).replace(/^google\/|^openai\//, ''),
        n: run.n_items,
        pdr: run.metrics.pdr,
        trapOver: run.metrics.trap_overclaim_rate,
        ctrlAcc: run.metrics.control_accuracy,
        ctrlAbst: run.metrics.control_abstention_rate,
        cls: '',
      });
    });
    (sb.stratified_440_neutral_runs || []).forEach((run) => {
      rows.push({
        label: `${normalizeModelSlug(run.model).replace(/^google\/|^openai\//, '')} (440)`,
        n: run.n_items,
        pdr: run.metrics.pdr,
        trapOver: run.metrics.trap_overclaim_rate,
        ctrlAcc: run.metrics.control_accuracy,
        ctrlAbst: run.metrics.control_abstention_rate,
        cls: '',
      });
    });

    v11ScoreboardTbody.innerHTML = rows
      .map(
        (r) => `
      <tr class="${r.cls}">
        <th scope="row" title="${escapeHtml(r.label)}">${escapeHtml(r.label)}</th>
        <td>${r.n.toLocaleString()}</td>
        <td class="v11-pill-pdr">${fmtPct(r.pdr)}</td>
        <td class="${r.trapOver > 0.25 ? 'v11-pill-warn' : ''}">${fmtPct(r.trapOver)}</td>
        <td>${fmtPct(r.ctrlAcc)}</td>
        <td>${fmtPct(r.ctrlAbst)}</td>
      </tr>`
      )
      .join('');
  }

  if (v11AblationNote && data.scoreboard && data.scoreboard.caution_coached_ablation_440) {
    const ab = data.scoreboard.caution_coached_ablation_440;
    const summaryBits = (ab.runs || [])
      .map(
        (r) =>
          `<strong>${escapeHtml(normalizeModelSlug(r.model))}</strong>: PDR ${fmtPct(r.metrics.pdr)}, TrapOver ${fmtPct(r.metrics.trap_overclaim_rate)}, CtrlAbst ${fmtPct(r.metrics.control_abstention_rate)}`
      )
      .join(' · ');
    v11AblationNote.innerHTML = `<strong>Caution-Coached Ablation (440 items):</strong> ${escapeHtml(ab.note)}<br>${summaryBits}`;
  }

  if (v11RoadmapNote && data.roadmap_v1_2) {
    const rm = data.roadmap_v1_2;
    v11RoadmapNote.innerHTML = `<strong>Planned v1.2 Diagnostic (${escapeHtml(rm.credit)}):</strong> ${escapeHtml(rm.title)} (<code>${escapeHtml(rm.formula)}</code>) - ${escapeHtml(rm.rationale)}`;
  }
}

function setInspectorOpen(open) {
  if (!inspectorPanel || !btnToggleInspector) return;
  inspectorPanel.classList.toggle('collapsed', !open);
  btnToggleInspector.classList.toggle('active', open);
  btnToggleInspector.setAttribute('aria-expanded', open ? 'true' : 'false');

  // Keep viewport spacious on narrower screens when opening Inspector
  if (open && window.innerWidth < 1360 && analyticsDrawer && !analyticsDrawer.classList.contains('hidden')) {
    toggleAnalyticsDrawer(false);
  }
}

function toggleAnalyticsDrawer(forceOpen) {
  if (!analyticsDrawer || !btnToggleAnalytics) return;
  const isHidden = analyticsDrawer.classList.contains('hidden');
  const shouldOpen = forceOpen !== undefined ? forceOpen : isHidden;

  analyticsDrawer.classList.toggle('hidden', !shouldOpen);
  btnToggleAnalytics.classList.toggle('active', shouldOpen);
  btnToggleAnalytics.setAttribute('aria-expanded', shouldOpen ? 'true' : 'false');
  const appRoot = document.getElementById('app');
  if (appRoot) appRoot.classList.toggle('analytics-open', shouldOpen);

  if (shouldOpen) {
    hideTooltip();
    // Auto-collapse right Inspector on laptops/tablets so the 3D viewport is never squeezed into a slit
    if (window.innerWidth < 1360) {
      setInspectorOpen(false);
    }
    updatePcaDisplay(currentPcaMode);
    renderQcPanels();
    if (!v11SummaryLoaded) {
      loadV11PublicSummary();
    }
  }
}

function resetCameraForCurrentBranch(animated = true) {
  const branchCfg = PIPELINE_BRANCHES[currentBranch] || PIPELINE_BRANCHES.technical;
  if (!controls) return;
  if (animated) {
    cameraTransition = {
      startTime: performance.now(),
      duration: 450,
      fromPos: camera.position.clone(),
      toPos: branchCfg.cameraPos.clone(),
      fromTarget: controls.target.clone(),
      toTarget: branchCfg.cameraTarget.clone(),
    };
  } else {
    cameraTransition = null;
    camera.position.copy(branchCfg.cameraPos);
    controls.target.copy(branchCfg.cameraTarget);
    controls.update();
  }
}

function switchBranch(branchKey) {
  if (!PIPELINE_BRANCHES[branchKey]) return;
  currentBranch = branchKey;

  if (btnBranchTechnical) btnBranchTechnical.classList.toggle('active', branchKey === 'technical');
  if (btnBranchMedia) btnBranchMedia.classList.toggle('active', branchKey === 'media');

  const branchCfg = PIPELINE_BRANCHES[branchKey];

  if (ctxDatasetId) ctxDatasetId.textContent = branchCfg.datasetId;
  if (ctxMissionName) ctxMissionName.textContent = branchCfg.mission;
  if (ctxNotebookRef) ctxNotebookRef.textContent = branchCfg.ref;
  if (ctxFindingsText) ctxFindingsText.textContent = branchCfg.status;
  if (citationQuote) citationQuote.textContent = branchCfg.citation;

  // Show/hide Technical-only controls (Analytics Drawer & Cortex X-Ray)
  if (branchKey === 'technical') {
    if (btnToggleAnalytics) btnToggleAnalytics.classList.remove('hidden');
    if (rowToggleXray) rowToggleXray.style.display = 'flex';
    if (rimLight) rimLight.color.setHex(0x40c4ff);
    if (starField) starField.material.opacity = 0.35;
  } else {
    if (btnToggleAnalytics) btnToggleAnalytics.classList.add('hidden');
    if (analyticsDrawer) analyticsDrawer.classList.add('hidden');
    if (btnToggleAnalytics) {
      btnToggleAnalytics.classList.remove('active');
      btnToggleAnalytics.setAttribute('aria-expanded', 'false');
    }
    const appRoot = document.getElementById('app');
    if (appRoot) appRoot.classList.remove('analytics-open');
    if (rowToggleXray) rowToggleXray.style.display = 'none';
    if (rimLight) rimLight.color.setHex(0xffc978);
    if (starField) starField.material.opacity = 0.85;
  }

  // Sync CAD floor grid default per branch (off in Zero-G Media Companion mode)
  if (gridHelper) gridHelper.visible = branchCfg.defaultGrid;
  if (toggleGrid) toggleGrid.checked = branchCfg.defaultGrid;

  hideTooltip();
  loadSimulationModel(branchCfg.glbUrl, branchKey);
  loadSimulationMetadata(branchCfg.metaUrl);
  resetCameraForCurrentBranch(false);
}

function updateHotspots() {
  if (currentViewMode !== 'annotated' || !currentModel || hotspotElements.length === 0) return;

  const width = window.innerWidth;
  const height = window.innerHeight;

  hotspotElements.forEach(({ config, element }) => {
    let found = false;

    if (config.targetNames && config.targetNames.length > 0) {
      for (const name of config.targetNames) {
        const obj = currentModel.getObjectByName(name);
        if (obj) {
          obj.getWorldPosition(_tempV);
          found = true;
          break;
        }
      }
    }

    if (found) {
      _worldPos.copy(_tempV);
      _worldPos.y += 0.16;
    } else {
      _worldPos.copy(config.defaultOffset).applyMatrix4(currentModel.matrixWorld);
    }

    _toPoint.copy(_worldPos).sub(currentModel.position).normalize();
    _toCam.copy(camera.position).sub(_worldPos).normalize();
    const facingDot = _toPoint.dot(_toCam);

    _proj.copy(_worldPos).project(camera);
    if (_proj.z > 1.0) {
      element.style.display = 'none';
      return;
    }

    element.style.display = 'flex';
    element.classList.toggle('occluded', facingDot < -0.25);

    const x = (_proj.x * 0.5 + 0.5) * width;
    const y = (-(_proj.y * 0.5) + 0.5) * height;
    element.style.transform = `translate3d(${x}px, ${y}px, 0)`;
  });
}

function showTooltipForConfig(config, markerEl) {
  if (!annotationTooltip) return;

  const tagEl = document.getElementById('tooltip-tag');
  const titleEl = document.getElementById('tooltip-title');
  const metricEl = document.getElementById('tooltip-metric');
  const descEl = document.getElementById('tooltip-desc');
  const datasetEl = document.getElementById('tooltip-dataset');

  if (tagEl) tagEl.textContent = config.tag;
  if (titleEl) titleEl.textContent = config.title;
  if (metricEl) metricEl.textContent = config.metric;
  if (descEl) descEl.textContent = config.desc;
  if (datasetEl) datasetEl.textContent = config.dataset;

  const rect = markerEl.getBoundingClientRect();
  const inspectorOpen = inspectorPanel && !inspectorPanel.classList.contains('collapsed');
  const rightSafeLimit = inspectorOpen ? window.innerWidth - 340 : window.innerWidth - 16;

  let left = rect.left + 38;
  let top = rect.top - 24;

  if (left + 300 > rightSafeLimit) {
    left = Math.max(16, rect.left - 310);
  }
  if (top + 220 > window.innerHeight) {
    top = Math.max(84, window.innerHeight - 236);
  }
  if (top < 84) top = 84;

  annotationTooltip.style.left = `${left}px`;
  annotationTooltip.style.top = `${top}px`;
  annotationTooltip.classList.remove('hidden');

  hotspotElements.forEach((item) => {
    item.element.classList.toggle('active', item.config.id === config.id);
  });
}

function hideTooltip() {
  if (annotationTooltip) {
    annotationTooltip.classList.add('hidden');
  }
  hotspotElements.forEach((item) => {
    item.element.classList.remove('active');
  });
}

function focusCameraOnHotspot(config) {
  if (!controls || !currentModel) return;

  const targetPos = new THREE.Vector3();
  let found = false;

  for (const name of config.targetNames) {
    const obj = currentModel.getObjectByName(name);
    if (obj) {
      obj.getWorldPosition(targetPos);
      found = true;
      break;
    }
  }
  if (!found) {
    targetPos.copy(config.defaultOffset).applyMatrix4(currentModel.matrixWorld);
  }

  // Smooth eased camera glide toward selected structure
  const viewDir = camera.position.clone().sub(controls.target).normalize();
  const desiredDist = currentBranch === 'media' ? 3.2 : 4.6;
  cameraTransition = {
    startTime: performance.now(),
    duration: 500,
    fromPos: camera.position.clone(),
    toPos: targetPos.clone().addScaledVector(viewDir, desiredDist),
    fromTarget: controls.target.clone(),
    toTarget: targetPos,
  };
}

function getDiagnosticMaterial(meshName) {
  let colorHex = 0x38bdf8;
  let opacity = 0.55;
  if (meshName === 'Hippocampal_Synaptic_Core' || meshName.includes('Optic')) {
    colorHex = 0x00ffaa;
    opacity = 0.9;
  } else if (meshName.includes('Scaffold') || meshName.includes('Track')) {
    colorHex = 0x64748b;
    opacity = 0.35;
  } else if (meshName.includes('PCA_Node')) {
    colorHex = 0xf59e0b;
    opacity = 0.9;
  }
  const key = `${colorHex}_${opacity}`;
  if (!diagnosticMaterialCache.has(key)) {
    diagnosticMaterialCache.set(
      key,
      new THREE.MeshBasicMaterial({
        color: colorHex,
        wireframe: true,
        transparent: true,
        opacity,
      })
    );
  }
  return diagnosticMaterialCache.get(key);
}

function setWireframeMode(enabled, useDiagnosticShader = false) {
  if (!currentModel) return;
  currentModel.traverse((child) => {
    if (!child.isMesh) return;
    const snap = originalMaterialProps.get(child.uuid);
    if (!snap) return;

    if (enabled && useDiagnosticShader) {
      child.material = getDiagnosticMaterial(child.name || '');
    } else {
      child.material = snap.material;
      if (Array.isArray(child.material)) {
        child.material.forEach((m) => { m.wireframe = enabled; });
      } else if (child.material) {
        child.material.wireframe = enabled;
      }
    }
  });
  if (!enabled && currentBranch === 'technical' && isXrayEnabled) {
    applyCortexXray(true);
  }
}

function setViewMode(mode) {
  currentViewMode = mode;

  [btnModePresentation, btnModeAnnotated, btnModeDiagnostic].forEach((btn) => {
    if (!btn) return;
    btn.classList.toggle('active', btn.dataset.mode === mode);
  });

  if (mode === 'presentation') {
    if (annotationLayer) annotationLayer.classList.add('hidden');
    hideTooltip();
    setWireframeMode(false, false);
    if (toggleWireframe) toggleWireframe.checked = false;
  } else if (mode === 'annotated') {
    if (annotationLayer) annotationLayer.classList.remove('hidden');
    setWireframeMode(false, false);
    if (toggleWireframe) toggleWireframe.checked = false;
    updateHotspots();
  } else if (mode === 'diagnostic') {
    if (annotationLayer) annotationLayer.classList.add('hidden');
    hideTooltip();
    setWireframeMode(true, true);
    if (toggleWireframe) toggleWireframe.checked = true;
  }
}

function copyTextWithFallback(text, onSuccess, onFail) {
  if (navigator.clipboard && navigator.clipboard.writeText) {
    navigator.clipboard.writeText(text).then(onSuccess).catch(() => {
      const ta = document.createElement('textarea');
      ta.value = text;
      ta.style.position = 'fixed';
      ta.style.opacity = '0';
      document.body.appendChild(ta);
      ta.select();
      try {
        document.execCommand('copy');
        onSuccess();
      } catch (_) {
        if (onFail) onFail();
      }
      document.body.removeChild(ta);
    });
  } else if (onFail) {
    onFail();
  }
}

function copyCitation() {
  const quoteEl = document.getElementById('citation-quote');
  if (!quoteEl || !btnCopyCitation) return;
  copyTextWithFallback(
    quoteEl.textContent.trim(),
    () => {
      btnCopyCitation.textContent = '✓ Copied to Clipboard!';
      btnCopyCitation.classList.add('copied');
      setTimeout(() => {
        btnCopyCitation.textContent = '📋 Copy Citation';
        btnCopyCitation.classList.remove('copied');
      }, 2200);
    },
    () => {
      btnCopyCitation.textContent = 'Press Ctrl+C to copy';
    }
  );
}

function setupUIHandlers() {
  btnPlay.addEventListener('click', () => {
    isPlaying = !isPlaying;
    btnPlay.textContent = isPlaying ? 'PAUSE' : 'PLAY';
  });

  btnReset.addEventListener('click', () => {
    if (mixer) mixer.setTime(0);
    resetCameraForCurrentBranch(true);
  });

  speedSlider.addEventListener('input', (e) => {
    playbackSpeed = parseFloat(e.target.value);
    speedLabel.textContent = `${playbackSpeed.toFixed(1)}x`;
  });

  if (toggleXray) {
    toggleXray.addEventListener('change', (e) => {
      applyCortexXray(e.target.checked);
    });
  }

  toggleWireframe.addEventListener('change', (e) => {
    setWireframeMode(e.target.checked, currentViewMode === 'diagnostic');
  });

  toggleOrbit.addEventListener('change', (e) => {
    controls.autoRotate = e.target.checked;
  });

  toggleGrid.addEventListener('change', (e) => {
    if (gridHelper) gridHelper.visible = e.target.checked;
  });

  fileInput.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (!file) return;
    const objectUrl = URL.createObjectURL(file);
    loadSimulationModel(objectUrl, currentBranch);
  });

  if (btnToggleInspector) {
    btnToggleInspector.addEventListener('click', (e) => {
      e.stopPropagation();
      const isCollapsed = inspectorPanel && inspectorPanel.classList.contains('collapsed');
      setInspectorOpen(isCollapsed);
    });
  }
  if (btnCloseInspector) {
    btnCloseInspector.addEventListener('click', (e) => {
      e.stopPropagation();
      setInspectorOpen(false);
    });
  }

  if (btnBranchTechnical) {
    btnBranchTechnical.addEventListener('click', () => switchBranch('technical'));
  }
  if (btnBranchMedia) {
    btnBranchMedia.addEventListener('click', () => switchBranch('media'));
  }

  if (btnToggleAnalytics) {
    btnToggleAnalytics.addEventListener('click', (e) => {
      e.stopPropagation();
      toggleAnalyticsDrawer();
    });
  }
  if (btnCloseAnalytics) {
    btnCloseAnalytics.addEventListener('click', (e) => {
      e.stopPropagation();
      toggleAnalyticsDrawer(false);
    });
  }

  if (tabPcaCerebellum) tabPcaCerebellum.addEventListener('click', () => updatePcaDisplay('cerebellum'));
  if (tabPcaHippocampus) tabPcaHippocampus.addEventListener('click', () => updatePcaDisplay('hippocampus'));
  if (tabPcaBoth) tabPcaBoth.addEventListener('click', () => updatePcaDisplay('both'));

  const drawerTabs = [
    { key: 'figures', el: drawerTabFigures, panel: drawerPanelFigures },
    { key: 'v1-1', el: drawerTabV11, panel: drawerPanelV11 },
  ];
  drawerTabs.forEach(({ key, el, panel }, idx) => {
    if (el) {
      el.addEventListener('click', () => selectDrawerTab(key, false));
      el.addEventListener('keydown', (e) => {
        if (e.key === 'ArrowRight' || e.key === 'ArrowLeft') {
          e.preventDefault();
          const nextIdx = (idx + (e.key === 'ArrowRight' ? 1 : -1) + drawerTabs.length) % drawerTabs.length;
          selectDrawerTab(drawerTabs[nextIdx].key, true);
        } else if (e.key === 'Home') {
          e.preventDefault();
          selectDrawerTab(drawerTabs[0].key, true);
        } else if (e.key === 'End') {
          e.preventDefault();
          selectDrawerTab(drawerTabs[drawerTabs.length - 1].key, true);
        }
      });
    }
    if (panel) {
      panel.addEventListener('beforematch', () => selectDrawerTab(key, false));
    }
  });

  if (btnCopyV11Sha) {
    btnCopyV11Sha.addEventListener('click', () => {
      const fullSha = btnCopyV11Sha.dataset.sha || '';
      if (!fullSha) return;
      copyTextWithFallback(
        fullSha,
        () => {
          if (v11ShaCopyTag) {
            v11ShaCopyTag.textContent = 'COPIED ✓';
            setTimeout(() => {
              v11ShaCopyTag.textContent = 'COPY';
            }, 2000);
          }
        },
        () => {
          if (v11ShaCopyTag) v11ShaCopyTag.textContent = 'SHA READY';
        }
      );
    });
  }

  if (btnModePresentation) btnModePresentation.addEventListener('click', () => setViewMode('presentation'));
  if (btnModeAnnotated) btnModeAnnotated.addEventListener('click', () => setViewMode('annotated'));
  if (btnModeDiagnostic) btnModeDiagnostic.addEventListener('click', () => setViewMode('diagnostic'));

  if (tooltipClose) {
    tooltipClose.addEventListener('click', (e) => {
      e.stopPropagation();
      hideTooltip();
    });
  }

  if (btnCopyCitation) {
    btnCopyCitation.addEventListener('click', (e) => {
      e.stopPropagation();
      copyCitation();
    });
  }

  container.addEventListener('click', (e) => {
    if (!e.target.closest('.hotspot-marker') && !e.target.closest('#annotation-tooltip')) {
      hideTooltip();
    }
  });

  // Global Keyboard Shortcuts
  document.addEventListener('keydown', (e) => {
    const tag = (e.target && e.target.tagName) || '';
    if (tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT' || e.metaKey || e.ctrlKey || e.altKey) {
      return;
    }
    if (e.code === 'Space') {
      e.preventDefault();
      isPlaying = !isPlaying;
      btnPlay.textContent = isPlaying ? 'PAUSE' : 'PLAY';
    } else if (e.key === 'r' || e.key === 'R') {
      if (mixer) mixer.setTime(0);
      resetCameraForCurrentBranch(true);
    } else if (e.key === '1') {
      setViewMode('presentation');
    } else if (e.key === '2') {
      setViewMode('annotated');
    } else if (e.key === '3') {
      setViewMode('diagnostic');
    } else if ((e.key === 'x' || e.key === 'X') && currentBranch === 'technical') {
      applyCortexXray(!isXrayEnabled);
    } else if ((e.key === 'a' || e.key === 'A') && currentBranch === 'technical') {
      toggleAnalyticsDrawer();
    } else if (e.key === 'i' || e.key === 'I') {
      const isCollapsed = inspectorPanel && inspectorPanel.classList.contains('collapsed');
      setInspectorOpen(isCollapsed);
    } else if (e.key === 'Escape') {
      hideTooltip();
      if (analyticsDrawer && !analyticsDrawer.classList.contains('hidden')) {
        toggleAnalyticsDrawer(false);
      } else if (window.innerWidth < 1100 && inspectorPanel && !inspectorPanel.classList.contains('collapsed')) {
        setInspectorOpen(false);
      }
    }
  });
}

function onWindowResize() {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
  updateHotspots();
}

function animate() {
  requestAnimationFrame(animate);
  if (document.hidden) return;

  const delta = Math.min(clock.getDelta(), 0.1);
  if (mixer && isPlaying) {
    mixer.update(delta * playbackSpeed);
  }

  if (cameraTransition) {
    const elapsed = performance.now() - cameraTransition.startTime;
    const rawT = Math.min(1, elapsed / cameraTransition.duration);
    // Ease out cubic
    const t = 1 - Math.pow(1 - rawT, 3);
    camera.position.lerpVectors(cameraTransition.fromPos, cameraTransition.toPos, t);
    controls.target.lerpVectors(cameraTransition.fromTarget, cameraTransition.toTarget, t);
    if (rawT >= 1) {
      cameraTransition = null;
    }
  }

  controls.update();
  renderer.render(scene, camera);

  if (currentViewMode === 'annotated') {
    updateHotspots();
  }

  frameCount++;
  const now = performance.now();
  if (now - lastFpsUpdate >= 1000) {
    valFps.textContent = Math.round((frameCount * 1000) / (now - lastFpsUpdate));
    frameCount = 0;
    lastFpsUpdate = now;
  }
}

init();
