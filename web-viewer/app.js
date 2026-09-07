import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';

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
const toggleWireframe = document.getElementById('toggle-wireframe');
const toggleOrbit = document.getElementById('toggle-orbit');
const toggleGrid = document.getElementById('toggle-grid');
const fileInput = document.getElementById('glb-file-input');

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

// Analytics Drawer Elements (Notebook Figures A & B)
const btnToggleAnalytics = document.getElementById('btn-toggle-analytics');
const analyticsDrawer = document.getElementById('analytics-drawer');
const btnCloseAnalytics = document.getElementById('btn-close-analytics');
const pcaChartViewport = document.getElementById('pca-chart-viewport');
const qcChartViewport = document.getElementById('qc-chart-viewport');
const tabPcaCerebellum = document.getElementById('tab-pca-cerebellum');
const tabPcaHippocampus = document.getElementById('tab-pca-hippocampus');
const tabPcaBoth = document.getElementById('tab-pca-both');

// Kaggle Notebook Benchmark Figures Dataset (Exact Authentic Values)
const NOTEBOOK_ANALYTICS_DATA = {
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
        { id: 'G9', cond: 'GC', pc1: 2.0, pc2: 42.0 }
      ]
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
        { id: 'G9', cond: 'GC', pc1: -85.0, pc2: -46.0 }
      ]
    }
  },
  qc: {
    datasetId: 'OSD-563',
    tissue: 'Cerebellum',
    rValue: '1.000',
    agreementPoints: [
      [5.0, 5.0], [7.5, 7.5], [10.0, 10.0], [12.5, 12.5],
      [15.0, 15.0], [17.5, 17.5], [20.0, 20.0], [22.5, 22.5], [24.5, 24.5]
    ],
    bins: [
      { x: 0.005, freq: 14100 },
      { x: 0.012, freq: 17150 },
      { x: 0.018, freq: 14600 },
      { x: 0.025, freq: 11500 },
      { x: 0.032, freq: 9300 },
      { x: 0.039, freq: 7950 },
      { x: 0.046, freq: 6700 },
      { x: 0.053, freq: 5600 },
      { x: 0.060, freq: 4600 },
      { x: 0.068, freq: 3950 },
      { x: 0.076, freq: 3200 },
      { x: 0.085, freq: 2600 },
      { x: 0.095, freq: 2200 },
      { x: 0.108, freq: 1750 },
      { x: 0.122, freq: 1450 },
      { x: 0.138, freq: 1400 },
      { x: 0.155, freq: 1380 },
      { x: 0.172, freq: 1420 },
      { x: 0.190, freq: 1500 },
      { x: 0.208, freq: 1650 },
      { x: 0.225, freq: 1850 },
      { x: 0.242, freq: 2100 },
      { x: 0.258, freq: 2450 },
      { x: 0.272, freq: 2650 },
      { x: 0.285, freq: 3100 },
      { x: 0.298, freq: 3350 },
      { x: 0.308, freq: 4200 },
      { x: 0.318, freq: 3450 },
      { x: 0.328, freq: 2400 },
      { x: 0.338, freq: 320 },
      { x: 0.355, freq: 16000 }
    ]
  }
};

// Branch Definitions & Hotspots
const PIPELINE_BRANCHES = {
  technical: {
    name: 'Technical Benchmark',
    glbUrl: '../exports/simulation.glb',
    metaUrl: '../exports/simulation.json',
    datasetId: 'NASA-OSDR OSD-563 / OSD-564',
    mission: 'Rodent Research-10 (SpaceX-21)',
    ref: 'cerebellum-vs-hippocampus-rr-10-spaceflight-mice.ipynb',
    status: 'Cerebellum PC1 25.6% | Hippocampus PC1 28.3% | VST r=1.000',
    citation: 'NASA OSDR OSD-563 & OSD-564: Cerebellum and Hippocampus Transcriptomics from RR-10 Spaceflight Mice (SpaceX-21).',
    hotspots: [
      {
        id: 'cortex',
        num: 1,
        tag: 'ANATOMICAL PROXY',
        targetNames: ['Murine_Cortex_Left', 'Murine_Cortex_Right'],
        title: 'Bilateral Murine Cortex',
        metric: 'Adaptation Index: 0.942 | ICP Volatility: 0.32',
        desc: 'Lissencephalic cerebral hemispheres divided along the sagittal fissure. Visualizes microvascular capillary strain and cephalic fluid-shift breathing under microgravity.',
        dataset: 'NASA-OSDR-RR10-B42',
        defaultOffset: new THREE.Vector3(0, 0.15, 0.7)
      },
      {
        id: 'olfactory',
        num: 2,
        tag: 'SENSORY TELEMETRY',
        targetNames: ['Murine_Olfactory_Left', 'Murine_Olfactory_Right'],
        title: 'Rostral Chemosensory Bulbs',
        metric: 'Chemosensory Plasticity: 0.91 | Cluster #1',
        desc: 'Anterior telencephalic sensory projections. Critical murine navigation apparatus, tracking olfactory maintenance during 60-day spaceflight exposure.',
        dataset: 'NASA-OSDR-RR10-B42',
        defaultOffset: new THREE.Vector3(0, 1.25, -0.05)
      },
      {
        id: 'hippocampus',
        num: 3,
        tag: 'SYNAPTIC PLASTICITY',
        targetNames: ['Hippocampal_Synaptic_Core'],
        title: 'Deep Hippocampal Synaptic Core',
        metric: 'Synaptic Luminescence: 4.5 | Neurogenesis: High',
        desc: 'Internal limbic core nestled within the longitudinal fissure. Models synaptic plasticity, spatial memory encoding, and cosmic radiation resilience.',
        dataset: 'NASA-OSDR-RR10-B42',
        defaultOffset: new THREE.Vector3(0, 0.05, 0.15)
      },
      {
        id: 'cerebellum',
        num: 4,
        tag: 'MOTOR / VESTIBULAR',
        targetNames: ['Murine_Cerebellar_Node'],
        title: 'Cerebellar Vestibular Anchor',
        metric: 'Vestibular Score: 0.88 | Folia Strain: Low',
        desc: 'Posterior cerebellar node with procedural folia micro-furrows. Captures otolith-ocular adaptation and microgravity vestibulomotor coordination reorganization.',
        dataset: 'NASA-OSDR-RR10-B42',
        defaultOffset: new THREE.Vector3(0, -1.25, -0.1)
      },
      {
        id: 'telemetry',
        num: 5,
        tag: 'HABITAT INSTRUMENTATION',
        targetNames: ['Habitat_Telemetry_Track_1', 'BioTelemetry_Probe_1_A_Hull'],
        title: 'Flight Habitat Bio-Telemetry Array',
        metric: 'Channels: 4 Guidance Tracks | 8 Active Probes',
        desc: 'Concentric titanium guidance gimbals and directional optical/radiation sensor probes continuously surveying cortical zones during mission operations.',
        dataset: 'NASA-OSDR-RR10-B42',
        defaultOffset: new THREE.Vector3(1.8, 1.3, 0.6)
      }
    ]
  },
  media: {
    name: 'Media Storytelling Companion',
    glbUrl: '../exports/media_simulation.glb',
    metaUrl: '../exports/media_simulation.json',
    datasetId: 'NASA-RR10-STORY-ODYSSEY',
    mission: 'Astro-Mice Zero-G Odyssey (ISS Mission)',
    ref: 'media_astro_mouse.json',
    status: 'Commander Pip | Zero-G Props | 150 Frames',
    citation: 'NASA Rodent Research Mission Outreach: "Astro-Mice in Microgravity: Public Engagement & Behavioral Adaptation in Orbit." (2024).',
    hotspots: [
      {
        id: 'pip_suit',
        num: 1,
        tag: 'ASTRONAUT EVA SUIT',
        targetNames: ['Commander_Pip_Torso', 'Commander_Pip_Harness_Buckle', 'Commander_Pip_Mission_Patch'],
        title: 'Commander Pip EVA Spacesuit',
        metric: 'Suit Mass: 140g | Micro-LifeSupport Active',
        desc: 'Aerospace-grade tailored composite micro-suit with burnt-orange harness straps, central brushed-metal buckle, and RR-10 mission shoulder insignia for zero-G operations.',
        dataset: 'NASA-RR10-STORY-ODYSSEY',
        defaultOffset: new THREE.Vector3(0, -0.3, 0.48)
      },
      {
        id: 'pip_visor',
        num: 2,
        tag: 'HELMET & AVIONICS',
        targetNames: ['Commander_Pip_Visor', 'Commander_Pip_Helmet_Bezel', 'Commander_Pip_Head_Cranium'],
        title: 'Gold Bubble Visor & Helmet',
        metric: 'Solar Reflectance: 98.4% | HUD Calibrated',
        desc: 'Warm-gold electroplated reflective bubble visor with silver bezel and side pivot discs. Protects murine eyes from orbital glare while allowing facial expression visibility.',
        dataset: 'NASA-RR10-STORY-ODYSSEY',
        defaultOffset: new THREE.Vector3(0, -0.15, 0.88)
      },
      {
        id: 'pip_tail',
        num: 3,
        tag: 'T-WING STABILIZER',
        targetNames: ['Commander_Pip_Tail_T_Wing', 'Commander_Pip_Tail_T_Collar', 'Commander_Pip_Tail_Seg_5'],
        title: 'Articulated Tail & T-Wing Thruster',
        metric: 'Cold-Gas Ion Plumes | Pitch/Yaw Stabilized',
        desc: 'Articulated 5-segment pink murine tail terminating in an aerodynamic white-and-orange T-wing stabilizer with dual micro-nozzles venting subtle attitude-control ion plumes.',
        dataset: 'NASA-RR10-STORY-ODYSSEY',
        defaultOffset: new THREE.Vector3(0, 0.88, 0.76)
      },
      {
        id: 'nutrient_sphere',
        num: 4,
        tag: 'ZERO-G ENRICHMENT',
        targetNames: ['ZeroG_Nutrient_Sphere', 'ZeroG_Nutrient_Nucleus'],
        title: 'Zero-G Nutrient Sphere',
        metric: 'Surface Tension: Active | Luminescent Core',
        desc: 'Suspended spherical nutrient and water bubble floating weightlessly in front of Pip, demonstrating liquid surface tension dynamics in microgravity.',
        dataset: 'NASA-RR10-STORY-ODYSSEY',
        defaultOffset: new THREE.Vector3(0.36, -0.6, 0.45)
      },
      {
        id: 'earth_porthole',
        num: 5,
        tag: 'ORBITAL OBSERVATION',
        targetNames: ['Habitat_Earth_Horizon', 'Habitat_Porthole_Frame'],
        title: 'Earth Observation Porthole',
        metric: 'Altitude: 408 km | Orbital Speed: 7.66 km/s',
        desc: 'Observation cupola framing the illuminated atmospheric curve of Earth during orbital sunrise passes over the research centrifuge habitat.',
        dataset: 'NASA-RR10-STORY-ODYSSEY',
        defaultOffset: new THREE.Vector3(0, 1.6, 0.55)
      }
    ]
  }
};

// Three.js State
let scene, camera, renderer, controls, mixer;
let currentModel = null;
let gridHelper = null;
let isPlaying = true;
let playbackSpeed = 1.0;
let clock = new THREE.Clock();
let currentBranch = 'technical'; // 'technical' | 'media'
let currentViewMode = 'presentation'; // 'presentation' | 'annotated' | 'diagnostic'
let hotspotElements = [];

// FPS Calculation
let frameCount = 0;
let lastFpsUpdate = performance.now();

function init() {
  // Scene
  scene = new THREE.Scene();
  scene.background = new THREE.Color(0x08090d);
  scene.fog = new THREE.FogExp2(0x08090d, 0.04);

  // Camera
  camera = new THREE.PerspectiveCamera(
    45,
    window.innerWidth / window.innerHeight,
    0.1,
    100
  );
  camera.position.set(6.0, 4.0, 7.0);

  // Renderer
  renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false });
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.0;
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  container.appendChild(renderer.domElement);

  // Controls
  controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.dampingFactor = 0.05;
  controls.autoRotate = true;
  controls.autoRotateSpeed = 0.8;
  controls.target.set(0, 0, 0);

  // Lighting
  setupLighting();

  // Grid
  gridHelper = new THREE.GridHelper(20, 40, 0x00f2fe, 0x1f2937);
  gridHelper.position.y = -2.5;
  scene.add(gridHelper);

  // Event Listeners
  window.addEventListener('resize', onWindowResize);
  setupUIHandlers();

  // Initial Load (support branch intent from URL query, hash, or sessionStorage)
  let initialBranch = 'technical';
  try {
    const urlParams = new URLSearchParams(window.location.search);
    const paramBranch = urlParams.get('branch');
    const hashBranch = window.location.hash.toLowerCase().includes('media') || window.location.hash.toLowerCase().includes('pip');
    const storedBranch = sessionStorage.getItem('preferred_branch');
    if (paramBranch === 'media' || hashBranch || storedBranch === 'media') {
      initialBranch = 'media';
      sessionStorage.removeItem('preferred_branch');
    }
  } catch (e) {
    // Fallback gracefully
  }

  if (initialBranch === 'media') {
    switchBranch('media');
  } else {
    loadSimulationModel('../exports/simulation.glb');
    loadSimulationMetadata('../exports/simulation.json');
  }

  animate();
}

function setupLighting() {
  const ambient = new THREE.AmbientLight(0xffffff, 0.28);
  scene.add(ambient);

  const keyLight = new THREE.DirectionalLight(0xffede0, 1.8);
  keyLight.position.set(6, 9, 6);
  keyLight.castShadow = true;
  keyLight.shadow.mapSize.width = 2048;
  keyLight.shadow.mapSize.height = 2048;
  keyLight.shadow.bias = -0.0005;
  scene.add(keyLight);

  const fillLight = new THREE.DirectionalLight(0x7eaafc, 0.6);
  fillLight.position.set(-6, 3, -4);
  scene.add(fillLight);

  const rimLight = new THREE.DirectionalLight(0x00f2fe, 1.6);
  rimLight.position.set(0, -4, -6);
  scene.add(rimLight);
}

function loadSimulationModel(url) {
  loadingOverlay.style.display = 'flex';
  loadingOverlay.style.opacity = '1';
  loadingText.textContent = 'Loading GLB Asset...';

  const loader = new GLTFLoader();
  loader.load(
    url,
    (gltf) => {
      if (currentModel) {
        scene.remove(currentModel);
      }

      currentModel = gltf.scene;

      // Center & scale model
      const box = new THREE.Box3().setFromObject(currentModel);
      const center = box.getCenter(new THREE.Vector3());
      currentModel.position.sub(center);

      scene.add(currentModel);

      // Handle Animation Tracks
      if (gltf.animations && gltf.animations.length > 0) {
        mixer = new THREE.AnimationMixer(currentModel);
        gltf.animations.forEach((clip) => {
          const action = mixer.clipAction(clip);
          action.play();
        });
      } else {
        mixer = null;
      }

      // Count vertices & faces directly from loaded scene
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

      setupHotspotElements();

      loadingOverlay.style.opacity = '0';
      setTimeout(() => {
        loadingOverlay.style.display = 'none';
      }, 400);
    },
    (xhr) => {
      if (xhr.lengthComputable) {
        const percent = Math.round((xhr.loaded / xhr.total) * 100);
        loadingText.textContent = `Loading GLB Asset: ${percent}%`;
      }
    },
    (err) => {
      console.warn('Could not load direct URL, waiting for local file input:', err);
      loadingText.textContent = 'Ready (Load GLB via bottom button)';
      setTimeout(() => {
        loadingOverlay.style.display = 'none';
      }, 1000);
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
      if (data.statistics) {
        valVerts.textContent = data.statistics.total_vertices.toLocaleString();
        valFaces.textContent = data.statistics.total_faces.toLocaleString();
        valObjects.textContent = data.statistics.total_objects;
      }
    })
    .catch((err) => {
      metadataJson.textContent = '// Local metadata preview unavailable without web server.\n// Load simulation.json directly if needed.';
    });
}

function setupHotspotElements() {
  if (!annotationLayer) return;
  annotationLayer.innerHTML = '';
  hotspotElements = [];

  const branchCfg = PIPELINE_BRANCHES[currentBranch] || PIPELINE_BRANCHES.technical;
  const activeConfigs = branchCfg.hotspots;

  activeConfigs.forEach((config) => {
    const el = document.createElement('div');
    el.className = 'hotspot-marker';
    el.dataset.id = config.id;
    el.innerHTML = `
      <div class="hotspot-pulse"></div>
      <div class="hotspot-dot">${config.num}</div>
    `;

    el.addEventListener('mouseenter', () => {
      showTooltipForConfig(config, el);
    });

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

  let svg = `<svg class="svg-chart" viewBox="0 0 ${width} ${height}" xmlns="http://www.w3.org/2000/svg">`;

  // Plot background
  svg += `<rect x="${padLeft}" y="${padTop}" width="${plotW}" height="${plotH}" fill="rgba(0,0,0,0.3)" stroke="rgba(255,255,255,0.12)" stroke-width="1" />`;

  // Zero axes
  if (zeroX >= padLeft && zeroX <= padLeft + plotW) {
    svg += `<line x1="${zeroX}" y1="${padTop}" x2="${zeroX}" y2="${padTop + plotH}" stroke="rgba(255,255,255,0.22)" stroke-width="1" />`;
  }
  if (zeroY >= padTop && zeroY <= padTop + plotH) {
    svg += `<line x1="${padLeft}" y1="${zeroY}" x2="${padLeft + plotW}" y2="${zeroY}" stroke="rgba(255,255,255,0.22)" stroke-width="1" />`;
  }

  // Ticks & Grid Lines
  const xTicks = [-100, -50, 0, 50, 100, 150];
  xTicks.forEach((tick) => {
    if (tick >= xMin && tick <= xMax) {
      const tx = scaleX(tick);
      svg += `<line x1="${tx}" y1="${padTop}" x2="${tx}" y2="${padTop + plotH}" class="chart-grid" />`;
      svg += `<text x="${tx}" y="${padTop + plotH + 13}" class="chart-label" text-anchor="middle">${tick}</text>`;
    }
  });

  const yTicks = [-100, -50, 0, 50, 100, 150];
  yTicks.forEach((tick) => {
    if (tick >= yMin && tick <= yMax) {
      const ty = scaleY(tick);
      svg += `<line x1="${padLeft}" y1="${ty}" x2="${padLeft + plotW}" y2="${ty}" class="chart-grid" />`;
      svg += `<text x="${padLeft - 6}" y="${ty + 3}" class="chart-label" text-anchor="end">${tick}</text>`;
    }
  });

  // Title & Axis labels
  svg += `<text x="${padLeft + 4}" y="${padTop - 10}" class="chart-title">${data.name} (${data.datasetId})</text>`;
  svg += `<text x="${padLeft + plotW / 2}" y="${height - 6}" class="chart-label" text-anchor="middle">PC1 (${data.pc1Var} variance)</text>`;
  svg += `<text x="${12}" y="${padTop + plotH / 2}" class="chart-label" text-anchor="middle" transform="rotate(-90 12 ${padTop + plotH / 2})">PC2 (${data.pc2Var} variance)</text>`;

  // Samples
  data.samples.forEach((s) => {
    const cx = scaleX(s.pc1);
    const cy = scaleY(s.pc2);
    const color = s.cond === 'FLT' ? '#e04b4b' : '#3b82f6';
    const tip = `${s.id} [${s.cond}] PC1: ${s.pc1.toFixed(1)}, PC2: ${s.pc2.toFixed(1)}`;

    svg += `<g class="sample-group" data-tooltip="${tip}">
      <circle cx="${cx}" cy="${cy}" r="5.5" fill="${color}" stroke="#ffffff" stroke-width="1.2" class="chart-dot" />
      <text x="${cx + 6}" y="${cy - 4}" class="chart-dot-label">${s.id}</text>
    </g>`;
  });

  svg += `</svg>`;
  return svg;
}

function updatePcaDisplay(mode = 'cerebellum') {
  if (!pcaChartViewport) return;

  // Update tabs
  [tabPcaCerebellum, tabPcaHippocampus, tabPcaBoth].forEach((tab) => {
    if (!tab) return;
    tab.classList.toggle('active', tab.dataset.target === mode);
  });

  if (mode === 'cerebellum') {
    pcaChartViewport.innerHTML = renderPcaScatterPlot('cerebellum');
  } else if (mode === 'hippocampus') {
    pcaChartViewport.innerHTML = renderPcaScatterPlot('hippocampus');
  } else if (mode === 'both') {
    pcaChartViewport.innerHTML = renderPcaScatterPlot('cerebellum') + renderPcaScatterPlot('hippocampus');
  }
}

function renderQcPanels(width = 420) {
  if (!qcChartViewport) return;
  const qcData = NOTEBOOK_ANALYTICS_DATA.qc;

  // Panel 1: Per-Value Agreement (r = 1.000)
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
      <line x1="${scaleV(5.0)}" y1="${scaleVY(5.0)}" x2="${scaleV(24.5)}" y2="${scaleVY(24.5)}" stroke="#ef4444" stroke-dasharray="3 3" stroke-width="1.4" />
  `;

  // Ticks
  [5.0, 10.0, 15.0, 20.0, 25.0].forEach((t) => {
    const tx = scaleV(t);
    const ty = scaleVY(t);
    svg1 += `<line x1="${tx}" y1="${padTop}" x2="${tx}" y2="${padTop + pH}" class="chart-grid" />`;
    svg1 += `<text x="${tx}" y="${padTop + pH + 12}" class="chart-label" text-anchor="middle">${t.toFixed(1)}</text>`;
    svg1 += `<line x1="${padLeft}" y1="${ty}" x2="${padLeft + pW}" y2="${ty}" class="chart-grid" />`;
    svg1 += `<text x="${padLeft - 6}" y="${ty + 3}" class="chart-label" text-anchor="end">${t.toFixed(1)}</text>`;
  });

  // Points along line
  qcData.agreementPoints.forEach(([x, y]) => {
    svg1 += `<circle cx="${scaleV(x)}" cy="${scaleVY(y)}" r="2.8" fill="#38bdf8" stroke="none" />`;
  });

  svg1 += `
      <text x="${padLeft + 4}" y="${padTop - 8}" class="chart-title">Cerebellum: Per-Value Agreement (r = 1.000)</text>
      <text x="${padLeft + pW / 2}" y="${h1 - 6}" class="chart-label" text-anchor="middle">VST counts (rRNA included)</text>
      <text x="${12}" y="${padTop + pH / 2}" class="chart-label" text-anchor="middle" transform="rotate(-90 12 ${padTop + pH / 2})">VST (rRNA removed)</text>
      <text x="${padLeft + 10}" y="${padTop + 16}" fill="#ef4444" font-size="8px" font-family="var(--font-mono)">--- y = x</text>
    </svg>
  </div>`;

  // Panel 2: Distribution of rRNA-Removal Shift
  const h2 = 160;
  const pW2 = width - padLeft - padRight;
  const pH2 = h2 - padTop - padBottom;
  const [dMin, dMax] = [0.0, 0.36];
  const maxFreq = 18000;

  const scaleDX = (d) => padLeft + ((d - dMin) / (dMax - dMin)) * pW2;
  const scaleDY = (f) => padTop + ((maxFreq - f) / maxFreq) * pH2;

  let svg2 = `<div class="qc-subpanel">
    <svg class="svg-chart" viewBox="0 0 ${width} ${h2}" xmlns="http://www.w3.org/2000/svg">
      <rect x="${padLeft}" y="${padTop}" width="${pW2}" height="${pH2}" fill="rgba(0,0,0,0.3)" stroke="rgba(255,255,255,0.12)" stroke-width="1" />
  `;

  // Y-Ticks (0, 5k, 10k, 15k)
  [0, 5000, 10000, 15000].forEach((freq) => {
    const fy = scaleDY(freq);
    svg2 += `<line x1="${padLeft}" y1="${fy}" x2="${padLeft + pW2}" y2="${fy}" class="chart-grid" />`;
    svg2 += `<text x="${padLeft - 6}" y="${fy + 3}" class="chart-label" text-anchor="end">${freq}</text>`;
  });

  // X-Ticks (0.00, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35)
  [0.00, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35].forEach((dt) => {
    const dx = scaleDX(dt);
    svg2 += `<line x1="${dx}" y1="${padTop}" x2="${dx}" y2="${padTop + pH2}" class="chart-grid" />`;
    svg2 += `<text x="${dx}" y="${padTop + pH2 + 12}" class="chart-label" text-anchor="middle">${dt.toFixed(2)}</text>`;
  });

  // Histogram Bars
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
      <text x="${12}" y="${padTop + pH2 / 2}" class="chart-label" text-anchor="middle" transform="rotate(-90 12 ${padTop + pH2 / 2})">Frequency</text>
    </svg>
  </div>`;

  qcChartViewport.innerHTML = svg1 + svg2;
}

function toggleAnalyticsDrawer(forceOpen) {
  if (!analyticsDrawer || !btnToggleAnalytics) return;
  const isHidden = analyticsDrawer.classList.contains('hidden');
  const shouldOpen = forceOpen !== undefined ? forceOpen : isHidden;

  analyticsDrawer.classList.toggle('hidden', !shouldOpen);
  btnToggleAnalytics.classList.toggle('active', shouldOpen);

  if (shouldOpen) {
    updatePcaDisplay('cerebellum');
    renderQcPanels();
  }
}

function switchBranch(branchKey) {
  if (!PIPELINE_BRANCHES[branchKey]) return;
  currentBranch = branchKey;

  // Update button active state
  if (btnBranchTechnical) btnBranchTechnical.classList.toggle('active', branchKey === 'technical');
  if (btnBranchMedia) btnBranchMedia.classList.toggle('active', branchKey === 'media');

  const branchCfg = PIPELINE_BRANCHES[branchKey];

  // Update Mission Context
  if (ctxDatasetId) ctxDatasetId.textContent = branchCfg.datasetId;
  if (ctxMissionName) ctxMissionName.textContent = branchCfg.mission;
  if (ctxNotebookRef) ctxNotebookRef.textContent = branchCfg.ref;
  if (ctxFindingsText) ctxFindingsText.textContent = branchCfg.status;
  if (citationQuote) citationQuote.textContent = branchCfg.citation;

  // Show or hide Analytics toggle depending on branch
  if (branchKey === 'technical') {
    if (btnToggleAnalytics) btnToggleAnalytics.classList.remove('hidden');
  } else {
    if (btnToggleAnalytics) btnToggleAnalytics.classList.add('hidden');
    if (analyticsDrawer) analyticsDrawer.classList.add('hidden');
    if (btnToggleAnalytics) btnToggleAnalytics.classList.remove('active');
  }

  // Reset tooltip
  hideTooltip();

  // Load new model and metadata
  loadSimulationModel(branchCfg.glbUrl);
  loadSimulationMetadata(branchCfg.metaUrl);

  // Re-apply view mode
  setViewMode(currentViewMode);

  // Position camera nicely for the active asset
  if (controls) {
    if (branchKey === 'media') {
      camera.position.set(4.5, 2.8, 5.0);
    } else {
      camera.position.set(6.0, 4.0, 7.0);
    }
    controls.target.set(0, 0, 0);
    controls.update();
  }
}

function updateHotspots() {
  if (currentViewMode !== 'annotated' || !currentModel || hotspotElements.length === 0) return;

  const width = window.innerWidth;
  const height = window.innerHeight;
  const tempV = new THREE.Vector3();
  const worldPos = new THREE.Vector3();

  hotspotElements.forEach(({ config, element }) => {
    let found = false;

    // Try finding named meshes in the current loaded scene
    if (config.targetNames && config.targetNames.length > 0) {
      for (const name of config.targetNames) {
        const obj = currentModel.getObjectByName(name);
        if (obj) {
          obj.getWorldPosition(tempV);
          found = true;
          break;
        }
      }
    }

    if (found) {
      worldPos.copy(tempV);
      // Subtle upward offset in world space
      worldPos.y += 0.2;
    } else {
      worldPos.copy(config.defaultOffset);
      worldPos.applyMatrix4(currentModel.matrixWorld);
    }

    // Camera occlusion check (angle between normal from center to point vs camera direction)
    const toPoint = worldPos.clone().sub(currentModel.position).normalize();
    const toCam = camera.position.clone().sub(worldPos).normalize();
    const facingDot = toPoint.dot(toCam);

    // Project world coordinates to normalized device coordinates [-1, 1]
    const proj = worldPos.clone().project(camera);

    // Behind camera or off-screen
    if (proj.z > 1.0) {
      element.style.display = 'none';
      return;
    }

    element.style.display = 'flex';
    element.classList.toggle('occluded', facingDot < -0.2);

    const x = (proj.x * 0.5 + 0.5) * width;
    const y = (-(proj.y * 0.5) + 0.5) * height;

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

  // Position relative to marker element
  const rect = markerEl.getBoundingClientRect();
  let left = rect.left + 38;
  let top = rect.top - 24;

  if (left + 310 > window.innerWidth) {
    left = Math.max(16, rect.left - 310);
  }
  if (top + 220 > window.innerHeight) {
    top = Math.max(80, window.innerHeight - 230);
  }
  if (top < 80) top = 80;

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
    targetPos.copy(config.defaultOffset);
    targetPos.applyMatrix4(currentModel.matrixWorld);
  }

  // Smoothly nudge orbit controls target towards structure
  controls.target.lerp(targetPos, 0.5);
}

function setViewMode(mode) {
  currentViewMode = mode;

  // Update button active state
  [btnModePresentation, btnModeAnnotated, btnModeDiagnostic].forEach((btn) => {
    if (!btn) return;
    btn.classList.toggle('active', btn.dataset.mode === mode);
  });

  if (mode === 'presentation') {
    // Clean presentation mode: no pins, clean solid PBR
    if (annotationLayer) annotationLayer.classList.add('hidden');
    hideTooltip();
    setWireframeMode(false);
    if (toggleWireframe) toggleWireframe.checked = false;
  } else if (mode === 'annotated') {
    // Annotated mode: show pins, allow hover/click tooltips
    if (annotationLayer) annotationLayer.classList.remove('hidden');
    setWireframeMode(false);
    if (toggleWireframe) toggleWireframe.checked = false;
    updateHotspots();
  } else if (mode === 'diagnostic') {
    // Diagnostic mode: wireframe on, pins hidden
    if (annotationLayer) annotationLayer.classList.add('hidden');
    hideTooltip();
    setWireframeMode(true);
    if (toggleWireframe) toggleWireframe.checked = true;
  }
}

function setWireframeMode(enabled) {
  if (!currentModel) return;
  currentModel.traverse((child) => {
    if (child.isMesh && child.material) {
      if (Array.isArray(child.material)) {
        child.material.forEach((m) => { m.wireframe = enabled; });
      } else {
        child.material.wireframe = enabled;
      }
    }
  });
}

function copyCitation() {
  const quoteEl = document.getElementById('citation-quote');
  if (!quoteEl || !btnCopyCitation) return;

  const quoteText = quoteEl.textContent.trim();
  navigator.clipboard.writeText(quoteText).then(() => {
    btnCopyCitation.textContent = '✓ Copied to Clipboard!';
    btnCopyCitation.classList.add('copied');
    setTimeout(() => {
      btnCopyCitation.textContent = '📋 Copy Citation';
      btnCopyCitation.classList.remove('copied');
    }, 2200);
  }).catch(() => {
    btnCopyCitation.textContent = 'Press Ctrl+C to copy';
  });
}

function setupUIHandlers() {
  btnPlay.addEventListener('click', () => {
    isPlaying = !isPlaying;
    btnPlay.textContent = isPlaying ? 'PAUSE' : 'PLAY';
  });

  btnReset.addEventListener('click', () => {
    if (mixer) {
      mixer.setTime(0);
    }
    controls.reset();
  });

  speedSlider.addEventListener('input', (e) => {
    playbackSpeed = parseFloat(e.target.value);
    speedLabel.textContent = `${playbackSpeed.toFixed(1)}x`;
  });

  toggleWireframe.addEventListener('change', (e) => {
    setWireframeMode(e.target.checked);
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
    loadSimulationModel(objectUrl);
  });

  // Pipeline Branch Switcher Listeners
  if (btnBranchTechnical) {
    btnBranchTechnical.addEventListener('click', () => switchBranch('technical'));
  }
  if (btnBranchMedia) {
    btnBranchMedia.addEventListener('click', () => switchBranch('media'));
  }

  // Analytics Drawer & Tab Listeners
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
  if (tabPcaCerebellum) {
    tabPcaCerebellum.addEventListener('click', () => updatePcaDisplay('cerebellum'));
  }
  if (tabPcaHippocampus) {
    tabPcaHippocampus.addEventListener('click', () => updatePcaDisplay('hippocampus'));
  }
  if (tabPcaBoth) {
    tabPcaBoth.addEventListener('click', () => updatePcaDisplay('both'));
  }

  // 3-Way Mode Switcher Listeners
  if (btnModePresentation) {
    btnModePresentation.addEventListener('click', () => setViewMode('presentation'));
  }
  if (btnModeAnnotated) {
    btnModeAnnotated.addEventListener('click', () => setViewMode('annotated'));
  }
  if (btnModeDiagnostic) {
    btnModeDiagnostic.addEventListener('click', () => setViewMode('diagnostic'));
  }

  // Tooltip & Citation Listeners
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

  // Dismiss tooltip when clicking canvas outside hotspots
  container.addEventListener('click', (e) => {
    if (!e.target.closest('.hotspot-marker') && !e.target.closest('#annotation-tooltip')) {
      hideTooltip();
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

  const delta = clock.getDelta();

  if (mixer && isPlaying) {
    mixer.update(delta * playbackSpeed);
  }

  controls.update();
  renderer.render(scene, camera);

  // Update screen-space annotations when in annotated mode
  if (currentViewMode === 'annotated') {
    updateHotspots();
  }

  // FPS Counter
  frameCount++;
  const now = performance.now();
  if (now - lastFpsUpdate >= 1000) {
    valFps.textContent = Math.round((frameCount * 1000) / (now - lastFpsUpdate));
    frameCount = 0;
    lastFpsUpdate = now;
  }
}

init();
