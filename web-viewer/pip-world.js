/**
 * Commander Pip Live World - Google DeepMind Genie 4 WebRTC Client
 *
 * Implements the official Gemini Interactions API (`v1beta`, `genie-4`)
 * four-step lifecycle:
 *  1. POST /api/genie-session -> creates interaction + mints single-session auth_token
 *  2. interactions.connect(interactionId, { transport: 'webrtc', api_version: 'v1beta' })
 *  3. Send one `world_setup` event (with optional <48 KB 16:9 JPEG reference_image)
 *     followed by `user_action` (WASD / Arrows) and 10x/150ms mid-session text impulses
 *  4. Always call `await session.complete()` (plus sendBeacon /api/genie-stop fallback)
 *     on user stop, timer cap, 10s hidden-tab guard, or page unload so billing halts.
 */

const GENAI_ESM_URL = 'https://esm.sh/@google/genai@3.6.1';
const SEED_IMAGE_URL = 'assets/pip_genie_seed.jpg';
const LUNAR_TAPIOCA_SEED_URL = 'assets/lunar_pip_tapioca_genie_seed.jpg';
const TAPIOCA_SEED_IMAGE_URL = 'assets/pip_tapioca_genie_seed.jpg';
const TAPIOCA_WIDE_SEED_URL = 'assets/pip_tapioca_corridor_wide_seed.jpg';
const COST_PER_SEC_USD = 0.10;
const IMPULSE_REPEATS = 10;
const IMPULSE_INTERVAL_MS = 150;
const VERB_COOLDOWN_MS = 2000;
const HIDDEN_TAB_AUTOSTOP_MS = 10000;
const MAX_WEBRTC_RAW_BYTES = 48000;
const CUSTOM_SEED_TARGET_MAX_BYTES = 40000;
const RECORDER_MIME_CANDIDATES = [
  'video/mp4;codecs=avc1.42E01E,mp4a.40.2',
  'video/mp4;codecs=avc1,mp4a.40.2',
  'video/mp4',
  'video/webm;codecs=vp9,opus',
  'video/webm;codecs=vp8,opus',
  'video/webm',
];

// Prompts aligned with Genie 4 official prompting rules:
// - Frame-0 visible propulsion
// - Broadband physical contact Foley (no soundtrack / narrowband drone words)
// - Causal Rule: triggers anchored to distant concrete objects ("far away from me")
// - Original stylized aesthetic (no trademarked studio brand names)
const WORLD_PRESETS = {
    lunar_ice_ambush: {
      name: 'Shackleton Crater Ice-Core Ambush',
      useSeedByDefault: true,
      seedUrl: LUNAR_TAPIOCA_SEED_URL,
      seedLabel: 'Moon: Pip vs. Captain Tapioca',
      verbProfile: 'lunar_ambush',
      prompt:
      'Stylized 3D animated lunar space-science comedy unfolding on the sunlit rim of Shackleton Crater under a starry black sky with Earth glowing overhead and a white lunar research dome far away on the horizon. The camera glides steadily forward across gray cratered regolith toward Commander Pip, a focused white lab mouse astronaut in a white-and-orange EVA suit extracting a glowing cyan lunar water-ice core from a tripod drill, while Captain Tapioca, a goofy green zombie astronaut in a quilted butter-yellow suit, lavender-teal rubber clogs, and a cracked glass bubble helmet splashing milk tea and a purple straw, bounds clumsily across the lunar ridge in slow 1/6G lunar gravity kicking up dust plumes and scattering slow-floating black tapioca pearls to interrupt Pip\'s experiment. Rule: Moving closer to the tripod ice-core drill makes Commander Pip startle, fire his orange tail thruster, and leap in low lunar gravity away from Captain Tapioca toward the white lunar base dome far away on the horizon. Audio: Crisp crunchy lunar gravel footsteps, metallic core-drill humming and latch clicks, soft liquid milk-tea splashes, rubbery boba pearls plinking onto the tripod metal, and goofy comical zombie groans.',
    },
    pip_vs_tapioca: {
      name: 'Pip vs. Captain Tapioca (Zero-G Chase v2)',
      useSeedByDefault: true,
      seedUrl: TAPIOCA_SEED_IMAGE_URL,
      seedLabel: 'Corridor: Pip vs. Tapioca v2',
      verbProfile: 'corridor_chase',
      prompt:
        'Stylized 3D animated space-science comedy chase inside a bright pressurized lunar orbital corridor moving forward smoothly down the center aisle between brushed metal handrails toward a sunlit circular Earth-and-Moon cupola far away from me. Commander Pip, a white lab mouse in a white-and-orange spacesuit holding a glowing blue bio-sample sphere, zips agilely forward with cyan micro-thruster puffs from his tail wing while Captain Tapioca, a goofy green zombie astronaut in a quilted butter-yellow spacesuit, lavender-teal rubber clogs, and a cracked glass bubble helmet sloshing with milk tea and a purple straw, tumbles clumsily in zero gravity behind him scattering floating black tapioca pearls and creamy liquid globules. Rule: Reaching the circular cupola hatch far away from me slides open the golden containment barrier and activates zero-gravity air scrubbers that sweep drifting boba pearls into swirling arcs. Audio: Crisp micro-thruster air puffs, liquid milk-tea splashes, soft rubbery boba pearls bouncing off white aluminum walls, squeaky foam clogs tapping handrails, and playful comical zombie groans.',
    },
    pip_vs_tapioca_wide: {
      name: 'Pip vs. Captain Tapioca (Wide Corridor v1)',
      useSeedByDefault: true,
      seedUrl: TAPIOCA_WIDE_SEED_URL,
      seedLabel: 'Corridor: Pip vs. Tapioca v1',
      verbProfile: 'corridor_chase',
      prompt:
        'Wide-angle stylized 3D animated space-science comedy moving steadily down a bright modular orbital corridor lined with brushed silver handrails toward a circular lunar observation cupola far away from me. Commander Pip, a cheerful white mouse astronaut in a white-and-orange EVA suit holding a glowing blue fluid droplet, jets forward with tiny cyan micro-thruster puffs while Captain Tapioca, a goofy green zombie astronaut in a quilted butter-yellow suit, lavender-teal clogs, and a cracked bubble helmet splashing milk tea and black tapioca pearls, tumbles playfully through zero gravity chasing him down the corridor. Rule: Approaching the circular cupola window far away from me slides open the observation shutter revealing golden sunlight sweeping across the lunar craters below. Audio: Soft micro-thruster air bursts, bouncing boba pearls tapping metal bulkheads, squeaky foam clogs on aluminum rails, and goofy joyful zombie laughs.',
    },
    pip_corridor: {
      name: 'Orbital Habitat Corridor',
      useSeedByDefault: true,
      seedUrl: SEED_IMAGE_URL,
      seedLabel: 'Commander Pip',
      verbProfile: 'default',
      prompt:
        'Stylized 3D animated space-science adventure following closely behind Commander Pip, a cheerful white lab mouse in a white-and-orange EVA spacesuit with a clear gold-tinted visor and small articulated orange tail-wing thrusters puffing forward along brushed aluminum handrails down a bright modular orbital research corridor. Translucent floating nutrient droplets drift gently past glowing cyan bio-telemetry panels toward a circular cupola shutter lever far away from me at the end of the corridor. Rule: Approaching the circular cupola shutter lever slides open the viewport revealing bright golden sunrise light over Earth\'s curved blue horizon. Audio: Crisp micro-thruster air bursts, soft gloved fingertips tapping metal handrails, gentle water droplets clinking softly against aluminum bulkheads, and quiet velcro fabric rustling.',
    },
    cupola_sunrise: {
      name: 'Cupola Earth-Sunrise Bay',
      useSeedByDefault: false,
      seedUrl: SEED_IMAGE_URL,
      seedLabel: 'Commander Pip',
      verbProfile: 'default',
      prompt:
        'Immersive first-person EVA POV gripping white padded handrails while gliding slowly forward through a sunlit orbital observation module lined with silver equipment racks, floating water spheres, and an amber mechanical shutter lever on a circular cupola console far away from me. Rule: Pulling the amber shutter lever slides open the heavy cupola blast shields to reveal bright golden sunlight sweeping across Earth\'s curved blue atmosphere and swirling white clouds. Audio: Soft fabric glove friction on painted aluminum rails, crisp metallic latch clicks, gentle pressurized air puffs, and delicate water beads tapping clear glass.',
    },
    botany_dome: {
      name: 'Zero-G Bio-Botany Dome',
      useSeedByDefault: false,
      seedUrl: SEED_IMAGE_URL,
      seedLabel: 'Commander Pip',
      verbProfile: 'default',
      prompt:
        'Stylized 3D animated first-person POV holding a cylindrical white handrail gliding smoothly through a bright zero-gravity orbital botany dome lined with translucent green seedling pods, floating mist beads, and a bright orange watering valve far away from me on the central pedestal. Rule: Turning the orange watering valve releases a shower of sparkling floating water beads drifting across sunlit green leaves. Audio: Crisp rustling plant leaves, water droplets pattering lightly against acrylic pods, metallic handrail taps, and soft mechanical valve clicks.',
    },
  };

  const VERB_PROFILES = {
    lunar_ambush: {
      KeyE: {
        label: 'Tapioca Ambushes Drill',
        text: 'Captain Tapioca leaps clumsily through low lunar gravity straight toward the glowing cyan ice-core drill knocking up a dramatic puff of gray moon dust while Commander Pip jumps back startled',
      },
      KeyQ: {
        label: '1/6G Boba Pearl Shower',
        text: 'Captain Tapioca trips in slow lunar gravity spilling a comical slow-motion fountain of floating black tapioca pearls and creamy milk-tea droplets bouncing across the gray lunar crater dust',
      },
      KeyR: {
        label: 'Pip Thruster Escape',
        text: 'Commander Pip fires his orange tail thruster jetting in a buoyant low-gravity arc across the lunar regolith while clutching the glowing cyan ice sample toward the white lunar base dome',
      },
      KeyF: {
        label: 'Pip & Tapioca Voice',
        text: '"Hey! Captain Tapioca, stay back from my Shackleton Crater water-ice core sample!"',
      },
    },
    corridor_chase: {
      KeyE: {
        label: 'Tapioca Boba Surge',
        text: 'Captain Tapioca lunges clumsily forward in zero gravity scattering a sparkling cloud of floating black tapioca pearls and milk-tea globules down the bright white corridor',
      },
      KeyQ: {
        label: 'Open Earth Cupola',
        text: 'Slide open the circular cupola shutters ahead flooding the orbital corridor with golden sunrise light over Earth and the cratered Moon with crisp metallic latch clicks',
      },
      KeyR: {
        label: 'Pip Tail-Thruster Boost',
        text: 'Commander Pip fires cyan micro-thruster bursts from his orange tail wing spinning playfully down the handrail corridor ahead of Captain Tapioca',
      },
      KeyF: {
        label: 'Chase Comms Line',
        text: '"Mission Control, Captain Tapioca is spilling boba pearls all over the bio-sample corridor!"',
      },
    },
    default: {
      KeyE: {
        label: 'Open Earth Cupola',
        text: 'Slide open the circular cupola blast shields to flood the orbital corridor with bright golden sunrise light across Earth\'s curved blue horizon with crisp metallic latch clicks',
      },
      KeyQ: {
        label: 'Release Zero-G Droplets',
        text: 'Release a sparkling cluster of translucent floating water and nutrient droplets drifting gently down the zero-gravity corridor with soft liquid pops and glass clinks',
      },
      KeyR: {
        label: 'Open Airlock Bay',
        text: 'Slide open the circular white airlock hatch ahead revealing a bright sunlit orbital plant-growth bay with rustling green leaves and crisp mechanical door clicks',
      },
      KeyF: {
        label: 'Pip Voice Line',
        text: '"Commander Pip reporting in! Zero-G thrusters online and ready to explore the orbital habitat!"',
      },
    },
  };

  let activeVerbProfile = VERB_PROFILES.lunar_ambush;

  const NATIVE_KEY_MAP = {
    KeyW: 'key_w',
    KeyA: 'key_a',
    KeyS: 'key_s',
    KeyD: 'key_d',
    ArrowUp: 'arrow_up',
    ArrowDown: 'arrow_down',
    ArrowLeft: 'arrow_left',
    ArrowRight: 'arrow_right',
  };

  // DOM references
  const stageFrame = document.getElementById('stage-frame');
  const seedPreviewImg = document.getElementById('seed-preview-img');
  const worldVideo = document.getElementById('world-video');
  const stageOverlay = document.getElementById('stage-overlay');
  const constructionTapeOverlay = document.getElementById('construction-tape-overlay');
  const overlayTitle = document.getElementById('overlay-title');
  const overlayDesc = document.getElementById('overlay-desc');
  const overlayProgress = document.getElementById('overlay-progress');
  const overlayProgressLabel = document.getElementById('overlay-progress-label');
  const liveHud = document.getElementById('live-hud');
  const hudPresetName = document.getElementById('hud-preset-name');
  const hudRecPill = document.getElementById('hud-rec-pill');
  const hudFocusHint = document.getElementById('hud-focus-hint');

  const clipExportBanner = document.getElementById('clip-export-banner');
  const clipExportMeta = document.getElementById('clip-export-meta');
  const clipPreviewVideo = document.getElementById('clip-preview-video');
  const btnDownloadClip = document.getElementById('btn-download-clip');
  const btnClearClip = document.getElementById('btn-clear-clip');

  const liveStatusPill = document.getElementById('live-status-pill');
  const sessionTimerBadge = document.getElementById('session-timer-badge');
  const errorBanner = document.getElementById('error-banner');
  const politeAnnouncer = document.getElementById('polite-announcer');
  const cooldownIndicator = document.getElementById('cooldown-indicator');

  const presetSelect = document.getElementById('preset-select');
  const worldPromptTextarea = document.getElementById('world-prompt-textarea');
  const toggleUseSeedImage = document.getElementById('toggle-use-seed-image');
  const seedDropzone = document.getElementById('seed-dropzone');
  const customSeedFileInput = document.getElementById('custom-seed-file');
  const seedThumbImg = document.getElementById('seed-thumb-img');
  const seedUploadStatus = document.getElementById('seed-upload-status');
  const btnResetSeed = document.getElementById('btn-reset-seed');
  const durationSelect = document.getElementById('duration-select');
  const toggleAutoRecord = document.getElementById('toggle-auto-record');
  const backendStatusText = document.getElementById('backend-status-text');
  const passcodeGroup = document.getElementById('passcode-group');
  const passcodeInput = document.getElementById('passcode-input');
  const byokKeyInput = document.getElementById('byok-key-input');

  const btnLaunchOverlay = document.getElementById('btn-launch-overlay');
  const btnCopyPromptOverlay = document.getElementById('btn-copy-prompt-overlay');
  const btnStartSession = document.getElementById('btn-start-session');
  const btnStopSession = document.getElementById('btn-stop-session');
  const btnStopHud = document.getElementById('btn-stop-hud');
  const btnMute = document.getElementById('btn-mute');
  const btnFullscreen = document.getElementById('btn-fullscreen');

  const customSteerForm = document.getElementById('custom-steer-form');
  const customSteerInput = document.getElementById('custom-steer-input');
  const verbButtons = Array.from(document.querySelectorAll('.verb-btn'));
  const padButtons = Array.from(document.querySelectorAll('.pad-key'));

  const telSeedSize = document.getElementById('tel-seed-size');
  const telRecStatus = document.getElementById('tel-rec-status');
  const telInteractionId = document.getElementById('tel-interaction-id');
  const telState = document.getElementById('tel-state');

  // Live session state
  let activeSession = null;
  let activeInteractionId = null;
  let activeAuthSnapshot = null; // { passcode, userApiKey } kept only in memory for sendBeacon stop fallback
  let sessionStartMs = 0;
  let sessionCapSec = 20;
  let timerInterval = null;
  let warmupGuardTimeout = null;
  let hiddenTabTimeout = null;
  let isStarting = false;
  let isStopping = false;
  let lastVerbFiredMs = 0;
  let activeImpulseTimer = null;
  let cachedSeedBase64 = null;
  let cachedSeedBytes = 0;
  let activePresetSeedUrl = SEED_IMAGE_URL;
  let activePresetSeedLabel = 'Commander Pip';
  let isCustomSeedActive = false;
  let customSeedObjectUrl = null;
  let mediaRecorder = null;
  let recorderRetryInterval = null;
  let recordedChunks =[];
  let recordedClipUrl = null;
  let recordingStartMs = 0;
  const heldInputs = new Set();
  let isComingSoonLocked = false;

  function isLocalhostHost() {
    const h = window.location.hostname;
return h === 'localhost' || h === '127.0.0.1' || h === '::1';
}

function shouldEnforceComingSoonFromUrl() {
  const params = new URLSearchParams(window.location.search);
  if (params.get('preview') === 'coming-soon') return true;
  return !isLocalhostHost();
}

function applyComingSoonLock() {
  isComingSoonLocked = true;
  document.body.classList.add('coming-soon-locked');
  if (stageOverlay) stageOverlay.classList.add('hidden');
  if (liveHud) liveHud.classList.add('hidden');
  if (constructionTapeOverlay) constructionTapeOverlay.classList.remove('hidden');

  setStatus('coming-soon', 'COMING SOON');
  if (sessionTimerBadge) sessionTimerBadge.textContent = 'R&D PREVIEW · DISABLED';
  if (cooldownIndicator) cooldownIndicator.textContent = 'LOCKED';
  if (backendStatusText) {
    backendStatusText.textContent =
      'Coming Soon: live Genie 4 world generation is disabled on production during exploratory R&D (available on localhost only).';
    backendStatusText.classList.add('warn');
  }

  const controlsToDisable = [
    btnLaunchOverlay,
    btnStartSession,
    btnStopSession,
    presetSelect,
    durationSelect,
    worldPromptTextarea,
    toggleUseSeedImage,
    customSeedFileInput,
    btnResetSeed,
    toggleAutoRecord,
    btnClearClip,
    passcodeInput,
    byokKeyInput,
    customSteerInput,
    document.getElementById('btn-send-steer'),
    ...verbButtons,
    ...padButtons,
  ];
  controlsToDisable.forEach((el) => {
    if (el) el.disabled = true;
  });
  if (seedDropzone) seedDropzone.classList.add('is-disabled');
  if (clipExportBanner) clipExportBanner.classList.add('hidden');
  if (telRecStatus) telRecStatus.textContent = 'Disabled (Production)';
}

function announcePolite(msg) {
  if (!politeAnnouncer) return;
  politeAnnouncer.textContent = '';
  requestAnimationFrame(() => {
    politeAnnouncer.textContent = msg;
  });
}

function showError(msg) {
  if (!errorBanner) return;
  errorBanner.textContent = msg;
  errorBanner.classList.remove('hidden');
}

function clearError() {
  if (!errorBanner) return;
  errorBanner.textContent = '';
  errorBanner.classList.add('hidden');
}

function setStatus(stateKey, label) {
  if (liveStatusPill) {
    liveStatusPill.className = `status-pill ${stateKey}`;
    liveStatusPill.textContent = label;
  }
  if (telState) {
    telState.textContent = label;
  }
}

function formatClock(totalSec) {
  const s = Math.max(0, Math.floor(totalSec));
  const mm = String(Math.floor(s / 60)).padStart(2, '0');
  const ss = String(s % 60).padStart(2, '0');
  return `${mm}:${ss}`;
}

function updateTimerDisplay(elapsedSec) {
  const cap = Number(durationSelect?.value || sessionCapSec || 45);
  const estCost = (elapsedSec * COST_PER_SEC_USD).toFixed(2);
  if (sessionTimerBadge) {
    sessionTimerBadge.textContent = `${formatClock(elapsedSec)} / ${formatClock(cap)} · ~$${estCost}`;
    sessionTimerBadge.classList.toggle('warning', elapsedSec >= Math.max(cap - 10, 0) && activeSession !== null);
  }
}

function applyPreset(presetKey) {
  const preset = WORLD_PRESETS[presetKey] || WORLD_PRESETS.lunar_ice_ambush;
  if (worldPromptTextarea) worldPromptTextarea.value = preset.prompt;
  if (toggleUseSeedImage) toggleUseSeedImage.checked = preset.useSeedByDefault;
  if (hudPresetName) hudPresetName.textContent = preset.name;

  activeVerbProfile = VERB_PROFILES[preset.verbProfile] || VERB_PROFILES.default;
  verbButtons.forEach((btn) => {
    const spec = activeVerbProfile[btn.dataset.verbKey];
    const lbl = btn.querySelector('.verb-label');
    if (spec && lbl) lbl.textContent = spec.label;
  });

  const nextSeedUrl = preset.seedUrl || SEED_IMAGE_URL;
  const nextSeedLabel = preset.seedLabel || 'Commander Pip';
  if (!isCustomSeedActive && (nextSeedUrl !== activePresetSeedUrl || !cachedSeedBase64)) {
    activePresetSeedUrl = nextSeedUrl;
    activePresetSeedLabel = nextSeedLabel;
    cachedSeedBase64 = null;
    cachedSeedBytes = 0;
    if (seedPreviewImg) seedPreviewImg.src = activePresetSeedUrl;
    if (seedThumbImg) seedThumbImg.src = activePresetSeedUrl;
    loadSeedImageBase64().catch(() => { });
  }
}

function arrayBufferToBase64(buf) {
  const bytes = new Uint8Array(buf);
  let binary = '';
  for (let i = 0; i < bytes.length; i += 0x8000) {
    binary += String.fromCharCode(...bytes.subarray(i, i + 0x8000));
  }
  return btoa(binary);
}

async function loadSeedImageBase64() {
  if (cachedSeedBase64) return cachedSeedBase64;
  const targetUrl = activePresetSeedUrl || SEED_IMAGE_URL;
  const resp = await fetch(targetUrl);
  if (!resp.ok) {
    throw new Error(`Could not load seed image (${resp.status})`);
  }
  const buf = await resp.arrayBuffer();
  if (buf.byteLength > MAX_WEBRTC_RAW_BYTES) {
    throw new Error(`Seed image (${buf.byteLength} bytes) exceeds 48 KB WebRTC SCTP safety limit.`);
  }
  cachedSeedBase64 = arrayBufferToBase64(buf);
  cachedSeedBytes = buf.byteLength;
  const kbLabel = (cachedSeedBytes / 1024).toFixed(1);
  if (telSeedSize) {
    telSeedSize.textContent = `${kbLabel} KB JPEG (< 48 KB cap)`;
  }
  if (!isCustomSeedActive && seedUploadStatus) {
    seedUploadStatus.textContent = `Preset: ${activePresetSeedLabel} (${kbLabel} KB JPEG)`;
  }
  return cachedSeedBase64;
}

function decodeImageFile(file) {
  if (typeof createImageBitmap === 'function') {
    return createImageBitmap(file).then((bmp) => ({
      source: bmp,
      width: bmp.width,
      height: bmp.height,
      cleanup: () => bmp.close && bmp.close(),
    }));
  }
  return new Promise((resolve, reject) => {
    const tmpUrl = URL.createObjectURL(file);
    const img = new Image();
    img.onload = () => {
      resolve({
        source: img,
        width: img.naturalWidth,
        height: img.naturalHeight,
        cleanup: () => URL.revokeObjectURL(tmpUrl),
      });
    };
    img.onerror = () => {
      URL.revokeObjectURL(tmpUrl);
      reject(new Error('Browser could not decode the selected image file.'));
    };
    img.src = tmpUrl;
  });
}

function canvasToJpegBlob(canvas, quality) {
  return new Promise((resolve, reject) => {
    canvas.toBlob(
      (blob) => {
        if (!blob) {
          reject(new Error('Canvas JPEG encoding failed.'));
          return;
        }
        resolve(blob);
      },
      'image/jpeg',
      quality
    );
  });
}

async function compressCustomSeedImage(file) {
  if (!file || !file.type || !/^image\/(png|jpeg|webp)$/i.test(file.type)) {
    throw new Error('Select a PNG, JPEG, or WebP image for the 16:9 seed.');
  }

  const decoded = await decodeImageFile(file);
  try {
    const targetAspect = 16 / 9;
    const srcAspect = decoded.width / decoded.height;
    let sx = 0;
    let sy = 0;
    let sw = decoded.width;
    let sh = decoded.height;
    if (srcAspect > targetAspect) {
      sw = Math.round(decoded.height * targetAspect);
      sx = Math.round((decoded.width - sw) / 2);
    } else if (srcAspect < targetAspect) {
      sh = Math.round(decoded.width / targetAspect);
      sy = Math.round((decoded.height - sh) / 2);
    }

    const sizeLadder = [
      [960, 540],
      [800, 450],
      [640, 360],
    ];
    const qualityLadder = [0.78, 0.70, 0.62, 0.54, 0.46, 0.38, 0.30, 0.24];

    let chosenBlob = null;
    let chosenDims = [960, 540];
    let chosenQuality = 0.78;

    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    if (!ctx) throw new Error('2D canvas context unavailable for seed compression.');

    for (const [tw, th] of sizeLadder) {
      canvas.width = tw;
      canvas.height = th;
      ctx.imageSmoothingEnabled = true;
      ctx.imageSmoothingQuality = 'high';
      ctx.drawImage(decoded.source, sx, sy, sw, sh, 0, 0, tw, th);

      for (const q of qualityLadder) {
        const blob = await canvasToJpegBlob(canvas, q);
        chosenBlob = blob;
        chosenDims = [tw, th];
        chosenQuality = q;
        if (blob.size <= CUSTOM_SEED_TARGET_MAX_BYTES) {
          break;
        }
      }
      if (chosenBlob && chosenBlob.size <= CUSTOM_SEED_TARGET_MAX_BYTES) {
        break;
      }
    }

    if (!chosenBlob || chosenBlob.size > MAX_WEBRTC_RAW_BYTES) {
      throw new Error(
        `Could not compress "${file.name}" below the 48 KB WebRTC limit (best attempt: ${chosenBlob ? (chosenBlob.size / 1024).toFixed(1) : 'N/A'
        } KB).`
      );
    }

    const buf = await chosenBlob.arrayBuffer();
    return {
      blob: chosenBlob,
      base64: arrayBufferToBase64(buf),
      bytes: buf.byteLength,
      width: chosenDims[0],
      height: chosenDims[1],
      quality: chosenQuality,
    };
  } finally {
    decoded.cleanup();
  }
}

async function handleCustomSeedFile(file) {
  if (isComingSoonLocked || activeSession || isStarting || !file) return;
  clearError();
  try {
    const result = await compressCustomSeedImage(file);
    if (customSeedFileInput) customSeedFileInput.removeAttribute('aria-invalid');
    if (customSeedObjectUrl) URL.revokeObjectURL(customSeedObjectUrl);
    customSeedObjectUrl = URL.createObjectURL(result.blob);

    cachedSeedBase64 = result.base64;
    cachedSeedBytes = result.bytes;
    isCustomSeedActive = true;

    if (seedPreviewImg) {
      seedPreviewImg.src = customSeedObjectUrl;
      seedPreviewImg.alt = `Custom 16:9 seed image: ${file.name}`;
    }
    if (seedThumbImg) {
      seedThumbImg.src = customSeedObjectUrl;
    }
    if (toggleUseSeedImage) {
      toggleUseSeedImage.checked = true;
    }
    if (btnResetSeed) {
      btnResetSeed.disabled = false;
    }

    const kbLabel = (result.bytes / 1024).toFixed(1);
    const shortName = file.name.length > 26 ? `${file.name.slice(0, 23)}...` : file.name;
    if (seedUploadStatus) {
      seedUploadStatus.textContent = `Custom: ${shortName} (${result.width}x${result.height}, ${kbLabel} KB JPEG)`;
    }
    if (telSeedSize) {
      telSeedSize.textContent = `${kbLabel} KB JPEG (custom, < 40 KB)`;
    }
    announcePolite(`Custom 16:9 seed ready: ${file.name}, compressed to ${kbLabel} kilobytes.`);
  } catch (err) {
    if (customSeedFileInput) customSeedFileInput.setAttribute('aria-invalid', 'true');
    showError(err.message || 'Failed to prepare custom seed image.');
  }
}

async function resetToDefaultSeed() {
  if (isComingSoonLocked || activeSession || isStarting) return;
  clearError();
  if (customSeedObjectUrl) {
    URL.revokeObjectURL(customSeedObjectUrl);
    customSeedObjectUrl = null;
  }
  cachedSeedBase64 = null;
  cachedSeedBytes = 0;
  isCustomSeedActive = false;
  if (customSeedFileInput) {
    customSeedFileInput.value = '';
    customSeedFileInput.removeAttribute('aria-invalid');
  }
  if (seedPreviewImg) {
    seedPreviewImg.src = activePresetSeedUrl || SEED_IMAGE_URL;
    seedPreviewImg.alt = `${activePresetSeedLabel} 16:9 orbital habitat seed frame`;
  }
  if (seedThumbImg) {
    seedThumbImg.src = activePresetSeedUrl || SEED_IMAGE_URL;
  }
  if (btnResetSeed) {
    btnResetSeed.disabled = true;
  }
  try {
    await loadSeedImageBase64();
    announcePolite('Restored default Commander Pip 16:9 seed image.');
  } catch {
    // Fallback label already visible
  }
}

function pickBestRecorderMimeType() {
  if (typeof MediaRecorder === 'undefined') return '';
  if (typeof MediaRecorder.isTypeSupported !== 'function') return '';
  for (const mime of RECORDER_MIME_CANDIDATES) {
    if (MediaRecorder.isTypeSupported(mime)) return mime;
  }
  return '';
}

function updateIdleRecorderTelemetry() {
  if (!telRecStatus || isComingSoonLocked) return;
  if (typeof MediaRecorder === 'undefined') {
    telRecStatus.textContent = 'Unsupported in browser';
    return;
  }
  if (toggleAutoRecord?.checked) {
    const mime = pickBestRecorderMimeType();
    const label = mime.includes('mp4') ? 'MP4' : 'WebM';
    telRecStatus.textContent = `Armed (Auto ${label})`;
  } else {
    telRecStatus.textContent = 'Off (Manual)';
  }
}

function clearRecordedClip() {
  if (recordedClipUrl) {
    URL.revokeObjectURL(recordedClipUrl);
    recordedClipUrl = null;
  }
  if (clipPreviewVideo) {
    clipPreviewVideo.pause();
    clipPreviewVideo.removeAttribute('src');
    clipPreviewVideo.load();
  }
  if (clipExportBanner) clipExportBanner.classList.add('hidden');
  if (btnDownloadClip) btnDownloadClip.setAttribute('href', '#');
  updateIdleRecorderTelemetry();
}

function tryStartStreamRecorderNow() {
  if (isComingSoonLocked || !toggleAutoRecord?.checked) return false;
  if (typeof MediaRecorder === 'undefined') {
    updateIdleRecorderTelemetry();
    return false;
  }
  const stream = worldVideo?.srcObject;
  if (!stream || typeof stream.getTracks !== 'function' || stream.getTracks().length === 0) {
    return false;
  }
  if (mediaRecorder && mediaRecorder.state === 'recording') return true;

  try {
    recordedChunks = [];
    const mimeType = pickBestRecorderMimeType();
    const options = { videoBitsPerSecond: 6000000 };
    if (mimeType) options.mimeType = mimeType;
    try {
      mediaRecorder = new MediaRecorder(stream, options);
    } catch {
      // Fallback for browsers (e.g., Safari) that prefer their native default container/codec
      mediaRecorder = new MediaRecorder(stream);
    }
    mediaRecorder.ondataavailable = (evt) => {
      if (evt.data && evt.data.size > 0) {
        recordedChunks.push(evt.data);
      }
    };
    mediaRecorder.start(500);
    recordingStartMs = Date.now();
    if (hudRecPill) hudRecPill.classList.remove('hidden');
    if (telRecStatus) telRecStatus.textContent = 'Recording (Raw 720p)...';
    return true;
  } catch (err) {
    console.warn('MediaRecorder start failed:', err);
    mediaRecorder = null;
    if (telRecStatus) telRecStatus.textContent = 'Recorder unavailable';
    return false;
  }
}

function startStreamRecorder() {
  if (recorderRetryInterval) {
    clearInterval(recorderRetryInterval);
    recorderRetryInterval = null;
  }
  if (tryStartStreamRecorderNow()) return;
  if (isComingSoonLocked || !toggleAutoRecord?.checked || typeof MediaRecorder === 'undefined') return;
  // Retry briefly if WebRTC tracks attach slightly after playing/loadeddata fires
  let attempts = 0;
  recorderRetryInterval = setInterval(() => {
    attempts += 1;
    if (!activeSession || attempts > 20 || tryStartStreamRecorderNow()) {
      clearInterval(recorderRetryInterval);
      recorderRetryInterval = null;
    }
  }, 250);
}

function stopStreamRecorder() {
  if (recorderRetryInterval) {
    clearInterval(recorderRetryInterval);
    recorderRetryInterval = null;
  }
  if (hudRecPill) hudRecPill.classList.add('hidden');
  if (!mediaRecorder || mediaRecorder.state === 'inactive') {
    mediaRecorder = null;
    return Promise.resolve(null);
  }
  const rec = mediaRecorder;
  mediaRecorder = null;
  const elapsedSec = recordingStartMs ? Math.max(0.5, (Date.now() - recordingStartMs) / 1000) : 0;

  return new Promise((resolve) => {
    let settled = false;
    const finalizeBlob = () => {
      if (settled) return;
      settled = true;
      if (!recordedChunks.length) {
        updateIdleRecorderTelemetry();
        resolve(null);
        return;
      }
      const mime = rec.mimeType || 'video/webm';
      const ext = mime.includes('mp4') ? 'mp4' : 'webm';
      const blob = new Blob(recordedChunks, { type: mime });
      recordedChunks = [];
      if (recordedClipUrl) URL.revokeObjectURL(recordedClipUrl);
      recordedClipUrl = URL.createObjectURL(blob);

      const stamp = new Date().toISOString().replace(/[-:T]/g, '').slice(0, 14);
      const presetSlug = (presetSelect?.value || 'world').replace(/[^a-z0-9_-]/gi, '_');
      const filename = `orbiting_minds_genie4_${presetSlug}_${stamp}.${ext}`;
      const sizeStr =
        blob.size >= 1024 * 1024
          ? `${(blob.size / (1024 * 1024)).toFixed(2)} MB`
          : `${(blob.size / 1024).toFixed(0)} KB`;
      const durStr = formatClock(Math.round(elapsedSec));

      if (btnDownloadClip) {
        btnDownloadClip.href = recordedClipUrl;
        btnDownloadClip.download = filename;
      }
      if (clipPreviewVideo) {
        clipPreviewVideo.src = recordedClipUrl;
      }
      if (clipExportMeta) {
        clipExportMeta.textContent = `${filename} · ${durStr} · ${sizeStr} · Clean 1280x720 + 48 kHz Audio`;
      }
      if (clipExportBanner) clipExportBanner.classList.remove('hidden');
      if (telRecStatus) telRecStatus.textContent = `Clip Ready (${sizeStr} ${ext.toUpperCase()})`;
      announcePolite(`Clean Genie 4 recording ready to replay and download (${sizeStr}).`);
      resolve(blob);
    };

    rec.addEventListener('stop', finalizeBlob, { once: true });
    setTimeout(finalizeBlob, 1500);
    try {
      if (typeof rec.requestData === 'function') rec.requestData();
      rec.stop();
    } catch {
      finalizeBlob();
    }
  });
}

async function probeBackendCapabilities() {
  if (shouldEnforceComingSoonFromUrl()) {
    applyComingSoonLock();
    return;
  }
  try {
    const resp = await fetch('/api/genie-session', { method: 'GET' });
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    const info = await resp.json();

    if (info.comingSoon) {
      applyComingSoonLock();
      return;
    }

    if (info.serverKeyConfigured && !info.requiresPasscode) {
      backendStatusText.textContent = 'Localhost server key ready: click Launch to mint an ephemeral Genie 4 WebRTC session.';
      backendStatusText.classList.remove('warn');
      if (passcodeGroup) passcodeGroup.classList.add('hidden');
    } else if (info.serverKeyConfigured && info.requiresPasscode) {
      backendStatusText.textContent = 'Host Genie 4 endpoint online (passcode-gated). Enter the demo passcode or expand BYOK below.';
      backendStatusText.classList.remove('warn');
      if (passcodeGroup) passcodeGroup.classList.remove('hidden');
    } else {
      backendStatusText.textContent = 'Host server key is locked or unset. Expand BYOK below with your paid Gemini API key, or open Google AI Studio.';
      backendStatusText.classList.add('warn');
      if (passcodeGroup) passcodeGroup.classList.add('hidden');
      const byokDetails = document.getElementById('byok-details');
      if (byokDetails) byokDetails.open = true;
    }
  } catch {
    backendStatusText.textContent =
      'Static file server detected (no /api/genie-session route). Run `python3 run_pipeline.py --serve` locally or deploy to Vercel to mint ephemeral tokens.';
    backendStatusText.classList.add('warn');
  }
}

function sendWorldImpulse(promptText, label = 'World event') {
  if (!activeSession) {
    showError('Launch Commander Pip World first before sending live steering events.');
    return;
  }
  const now = Date.now();
  const remaining = VERB_COOLDOWN_MS - (now - lastVerbFiredMs);
  if (remaining > 0) {
    announcePolite(`Steering cooldown active (${(remaining / 1000).toFixed(1)}s remaining).`);
    return;
  }

  lastVerbFiredMs = now;
  clearError();
  if (activeImpulseTimer) {
    clearInterval(activeImpulseTimer);
    activeImpulseTimer = null;
  }

  if (cooldownIndicator) {
    cooldownIndicator.textContent = `STEERING: ${label.toUpperCase()}`;
    cooldownIndicator.classList.add('cooling');
  }
  announcePolite(`Sent world steering event: ${label}`);

  // Repeat 10x every 150ms (~1.5s) per official Genie 4 docs so the 4-frame planner samples it cleanly
  let sent = 0;
  const fire = () => {
    if (!activeSession) {
      if (activeImpulseTimer) clearInterval(activeImpulseTimer);
      activeImpulseTimer = null;
      return;
    }
    activeSession.send(promptText).catch((err) => {
      console.warn('Genie steering impulse error:', err);
      if (activeImpulseTimer) clearInterval(activeImpulseTimer);
      activeImpulseTimer = null;
    });
    sent += 1;
    if (sent >= IMPULSE_REPEATS && activeImpulseTimer) {
      clearInterval(activeImpulseTimer);
      activeImpulseTimer = null;
    }
  };
  fire();
  activeImpulseTimer = setInterval(fire, IMPULSE_INTERVAL_MS);

  setTimeout(() => {
    if (Date.now() - lastVerbFiredMs >= VERB_COOLDOWN_MS - 50 && cooldownIndicator) {
      cooldownIndicator.textContent = 'READY';
      cooldownIndicator.classList.remove('cooling');
    }
  }, VERB_COOLDOWN_MS);
}

function sendNativeAction(action, genieInput) {
  if (!activeSession) return;
  activeSession
    .send({
      event_type: 'user_action',
      action,
      input: genieInput,
    })
    .catch((err) => console.warn('Genie user_action error:', err));
}

function releaseAllHeldKeys() {
  for (const inputName of Array.from(heldInputs)) {
    sendNativeAction('key_up', inputName);
    heldInputs.delete(inputName);
  }
  padButtons.forEach((btn) => btn.classList.remove('pressed'));
}

function setControlsStreamingState(isLive) {
  if (btnStartSession) btnStartSession.disabled = isLive || isStarting;
  if (btnLaunchOverlay) btnLaunchOverlay.disabled = isLive || isStarting;
  if (btnStopSession) btnStopSession.disabled = !isLive;
  if (presetSelect) presetSelect.disabled = isLive;
  if (durationSelect) durationSelect.disabled = isLive;
  if (customSeedFileInput) customSeedFileInput.disabled = isLive || isComingSoonLocked;
  if (btnResetSeed) btnResetSeed.disabled = isLive || isComingSoonLocked || !isCustomSeedActive;
  if (toggleAutoRecord) toggleAutoRecord.disabled = isLive || isComingSoonLocked;
  if (seedDropzone) seedDropzone.classList.toggle('is-disabled', isLive || isComingSoonLocked);
  if (stageFrame) stageFrame.classList.toggle('streaming', isLive);
  if (liveHud) liveHud.classList.toggle('hidden', !isLive);
  if (worldVideo) worldVideo.classList.toggle('hidden', !isLive);
  if (seedPreviewImg) seedPreviewImg.classList.toggle('hidden', isLive);
  if (stageOverlay) stageOverlay.classList.toggle('hidden', isLive);
}

function finalizeLocalCleanup(reasonText = 'Standby') {
  if (recorderRetryInterval) {
    clearInterval(recorderRetryInterval);
    recorderRetryInterval = null;
  }
  if (timerInterval) {
    clearInterval(timerInterval);
    timerInterval = null;
  }
  if (warmupGuardTimeout) {
    clearTimeout(warmupGuardTimeout);
    warmupGuardTimeout = null;
  }
  if (hiddenTabTimeout) {
    clearTimeout(hiddenTabTimeout);
    hiddenTabTimeout = null;
  }
  if (activeImpulseTimer) {
    clearInterval(activeImpulseTimer);
    activeImpulseTimer = null;
  }
  heldInputs.clear();
  padButtons.forEach((btn) => btn.classList.remove('pressed'));

  activeSession = null;
  activeInteractionId = null;
  activeAuthSnapshot = null;
  isStarting = false;
  isStopping = false;

  if (worldVideo) {
    worldVideo.srcObject = null;
  }
  if (overlayProgress) overlayProgress.classList.add('hidden');
  if (overlayTitle) overlayTitle.textContent = 'Ready to Step Inside Commander Pip\'s Habitat';
  if (overlayDesc) overlayDesc.textContent = reasonText;
  if (telInteractionId) telInteractionId.textContent = '--';

  setControlsStreamingState(false);
  setStatus('standby', 'STANDBY');
  updateTimerDisplay(0);
}

async function stopWorldSession(reason = 'Session ended cleanly; server billing stopped.') {
  if (isStopping) return;
  const sessionToStop = activeSession;
  const interactionToStop = activeInteractionId;
  const authSnapshot = activeAuthSnapshot;

  if (!sessionToStop && !interactionToStop) {
    finalizeLocalCleanup(reason);
    return;
  }

  isStopping = true;
  setStatus('connecting', 'STOPPING...');
  releaseAllHeldKeys();
  // Flush clean WebRTC recording BEFORE session.complete() tears down tracks
  await stopStreamRecorder();

  try {
    if (sessionToStop && typeof sessionToStop.complete === 'function') {
      await sessionToStop.complete();
    }
  } catch (err) {
    console.warn('session.complete() failed, sending server cancel fallback:', err);
    if (interactionToStop) {
      fetch('/api/genie-stop', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          interactionId: interactionToStop,
          passcode: authSnapshot?.passcode || '',
          userApiKey: authSnapshot?.userApiKey || '',
        }),
      }).catch(() => { });
    }
  } finally {
    announcePolite(reason);
    finalizeLocalCleanup(reason);
  }
}

function beaconEmergencyStop() {
  if (!activeInteractionId) return;
  try {
    if (activeSession && typeof activeSession.complete === 'function') {
      activeSession.complete().catch(() => { });
    }
  } catch {
    // Ignore unload sync errors
  }
  try {
    const payload = JSON.stringify({
      interactionId: activeInteractionId,
      passcode: activeAuthSnapshot?.passcode || '',
      userApiKey: activeAuthSnapshot?.userApiKey || '',
    });
    navigator.sendBeacon(
      '/api/genie-stop',
      new Blob([payload], { type: 'application/json' })
    );
  } catch {
    // Best-effort beacon on tab close
  }
}

async function startWorldSession() {
  if (isComingSoonLocked || isStarting || activeSession) return;
  clearError();

  const promptText = (worldPromptTextarea?.value || '').trim();
  if (!promptText) {
    showError('Enter a World Setup Prompt before launching.');
    return;
  }

  isStarting = true;
  sessionCapSec = Math.min(90, Math.max(10, Number(durationSelect?.value || 20)));
  setStatus('connecting', 'CONNECTING');
  if (btnStartSession) btnStartSession.disabled = true;
  if (btnLaunchOverlay) btnLaunchOverlay.disabled = true;
  if (overlayTitle) overlayTitle.textContent = 'Initializing Commander Pip World...';
  if (overlayDesc) overlayDesc.textContent = 'Minting ephemeral token, connecting WebRTC, and rendering frame 1 (~5-9 seconds).';
  if (overlayProgress) overlayProgress.classList.remove('hidden');
  if (overlayProgressLabel) overlayProgressLabel.textContent = 'Step 1/3: Minting single-session ephemeral auth token...';

  const passcode = (passcodeInput?.value || '').trim();
  const userApiKey = (byokKeyInput?.value || '').trim();

  try {
    // 1. Mint interaction + ephemeral auth token via backend (keeps API keys off browser WebRTC/WS)
    const tokenResp = await fetch('/api/genie-session', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ passcode, userApiKey }),
    });
    const tokenData = await tokenResp.json().catch(() => ({}));
    if (!tokenResp.ok || !tokenData.interactionId || !tokenData.authToken) {
      throw new Error(tokenData.error || `Token minting failed (HTTP ${tokenResp.status}).`);
    }

    activeInteractionId = tokenData.interactionId;
    activeAuthSnapshot = { passcode, userApiKey };
    if (telInteractionId) telInteractionId.textContent = activeInteractionId;

    // 2. Load official @google/genai@3.6.1 browser ES module and connect over WebRTC
    if (overlayProgressLabel) overlayProgressLabel.textContent = 'Step 2/3: Loading @google/genai SDK & opening WebRTC stream...';
    const { GoogleGenAI } = await import(GENAI_ESM_URL);
    const clientAi = new GoogleGenAI({
      apiKey: tokenData.authToken,
      apiVersion: 'v1beta',
    });

    const session = await clientAi.interactions.connect(
      tokenData.interactionId,
      { transport: 'webrtc', api_version: 'v1beta' },
      { timeout_ms: 30000 }
    );
    activeSession = session;

    if (session.transport && typeof session.transport.setVideoElement === 'function') {
      session.transport.setVideoElement(worldVideo);
    }

    // Consume server lifecycle and error events in the background
    (async () => {
      try {
        for await (const event of session.receive()) {
          if (event.event_type === 'error') {
            const errMsg = event.error?.message || 'Genie 4 stream encountered an error.';
            showError(errMsg);
            await stopWorldSession(`Stream stopped: ${errMsg}`);
            break;
          } else if (event.event_type === 'interaction.completed') {
            await stopStreamRecorder();
            finalizeLocalCleanup('Genie 4 interaction completed.');
            break;
          }
        }
      } catch (loopErr) {
        if (activeSession === session && !isStopping) {
          showError(`Stream disconnected: ${loopErr.message || loopErr}`);
          await stopWorldSession('Stream disconnected.');
        }
      }
    })();

    // 3. Send initial `world_setup` event (top-level `reference_image` sibling to `world_prompt`)
    if (overlayProgressLabel) overlayProgressLabel.textContent = 'Step 3/3: Sending world_setup seed (frame 1 arrives in ~5-9s)...';
    const setupEvent = {
      event_type: 'world_setup',
      world_prompt: { text: promptText },
    };
    if (toggleUseSeedImage?.checked) {
      const b64 = await loadSeedImageBase64();
      setupEvent.reference_image = {
        mime_type: 'image/jpeg',
        data: b64,
      };
    }
    await session.send(setupEvent);

    // Transition UI to LIVE state
    isStarting = false;
    setControlsStreamingState(true);
    setStatus('connecting', 'WARMING UP');
    announcePolite('World setup sent. Waiting for frame 1 (~5-9 seconds), then W A S D and Arrow keys are active.');

    let countdownStarted = false;
    const startBillableCountdown = () => {
      if (countdownStarted || activeSession !== session) return;
      countdownStarted = true;
      if (warmupGuardTimeout) {
        clearTimeout(warmupGuardTimeout);
        warmupGuardTimeout = null;
      }
      sessionStartMs = Date.now();
      setStatus('live', 'LIVE · 24 FPS');
      updateTimerDisplay(0);
      startStreamRecorder();
      timerInterval = setInterval(() => {
        const elapsedSec = (Date.now() - sessionStartMs) / 1000;
        updateTimerDisplay(elapsedSec);
        if (elapsedSec >= sessionCapSec) {
          stopWorldSession(`Auto-stopped at ${sessionCapSec}s safety cap to protect your Gemini API budget.`);
        }
      }, 250);
    };

    if (worldVideo) {
      worldVideo.muted = false;
      worldVideo.addEventListener('playing', startBillableCountdown, { once: true });
      worldVideo.addEventListener('loadeddata', startBillableCountdown, { once: true });
      worldVideo.play().catch(() => { });
    }
    if (stageFrame) stageFrame.focus({ preventScroll: true });

    // Safety fallback: if frame 1 event doesn't fire within 15s, start the cap countdown anyway
    warmupGuardTimeout = setTimeout(startBillableCountdown, 15000);
  } catch (err) {
    console.error('Failed to start Genie 4 session:', err);
    const errMsg = err.message || 'Unable to launch Genie 4 session.';
    showError(errMsg);
    if (/API key|401|403|billing|BYOK/i.test(errMsg)) {
      const byokDetails = document.getElementById('byok-details');
      if (byokDetails) byokDetails.open = true;
    }
    // Ensure server interaction is cancelled if created before failure
    if (activeInteractionId) {
      beaconEmergencyStop();
    }
    finalizeLocalCleanup('Launch failed. Check the message below and try again.');
    setStatus('error', 'ERROR');
  }
}

function isTypingTarget(el) {
  if (!el) return false;
  const tag = el.tagName;
  return tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT' || el.isContentEditable;
}

function wireEventListeners() {
  presetSelect?.addEventListener('change', (e) => applyPreset(e.target.value));
  durationSelect?.addEventListener('change', () => {
    sessionCapSec = Math.min(90, Math.max(10, Number(durationSelect.value || 20)));
    if (!activeSession) updateTimerDisplay(0);
  });

  toggleAutoRecord?.addEventListener('change', updateIdleRecorderTelemetry);
  btnClearClip?.addEventListener('click', () => {
    clearRecordedClip();
    announcePolite('Discarded recorded clip.');
  });

  customSeedFileInput?.addEventListener('change', (e) => {
    const file = e.target.files?.[0];
    if (file) handleCustomSeedFile(file);
  });

  btnResetSeed?.addEventListener('click', resetToDefaultSeed);

  if (seedDropzone) {
    ['dragenter', 'dragover'].forEach((evtName) => {
      seedDropzone.addEventListener(evtName, (e) => {
        if (isComingSoonLocked || activeSession || isStarting) return;
        e.preventDefault();
        seedDropzone.classList.add('drag-over');
      });
    });
    ['dragleave', 'dragend'].forEach((evtName) => {
      seedDropzone.addEventListener(evtName, () => {
        seedDropzone.classList.remove('drag-over');
      });
    });
    seedDropzone.addEventListener('drop', (e) => {
      seedDropzone.classList.remove('drag-over');
      if (isComingSoonLocked || activeSession || isStarting) return;
      e.preventDefault();
      const file = e.dataTransfer?.files?.[0];
      if (file) handleCustomSeedFile(file);
    });
  }

  btnLaunchOverlay?.addEventListener('click', startWorldSession);
  btnStartSession?.addEventListener('click', startWorldSession);
  btnStopSession?.addEventListener('click', () => stopWorldSession('Stopped by user. Server billing halted.'));
  btnStopHud?.addEventListener('click', () => stopWorldSession('Stopped by user. Server billing halted.'));

  btnCopyPromptOverlay?.addEventListener('click', async () => {
    const promptText = worldPromptTextarea?.value || WORLD_PRESETS.pip_corridor.prompt;
    try {
      await navigator.clipboard.writeText(promptText);
      btnCopyPromptOverlay.textContent = 'Prompt Copied!';
      announcePolite('World setup prompt copied to clipboard.');
      setTimeout(() => {
        btnCopyPromptOverlay.textContent = 'Copy Prompt for AI Studio';
      }, 2000);
    } catch {
      showError('Clipboard write unavailable; copy directly from the World Setup Prompt box.');
    }
  });

  btnMute?.addEventListener('click', () => {
    if (!worldVideo) return;
    worldVideo.muted = !worldVideo.muted;
    btnMute.setAttribute('aria-pressed', worldVideo.muted ? 'true' : 'false');
    btnMute.textContent = worldVideo.muted ? 'Unmute Audio' : 'Mute Audio';
  });

  btnFullscreen?.addEventListener('click', () => {
    if (!stageFrame) return;
    if (document.fullscreenElement) {
      document.exitFullscreen().catch(() => { });
    } else if (stageFrame.requestFullscreen) {
      stageFrame.requestFullscreen().catch(() => { });
    }
  });

  // Custom key-bound verb buttons
  verbButtons.forEach((btn) => {
    btn.addEventListener('click', () => {
      const code = btn.dataset.verbKey;
      const spec = activeVerbProfile[code];
      if (spec) sendWorldImpulse(spec.text, spec.label);
    });
  });

  // Free-form mid-session steering prompt form
  customSteerForm?.addEventListener('submit', (e) => {
    e.preventDefault();
    const text = (customSteerInput?.value || '').trim();
    if (!text) return;
    sendWorldImpulse(text, 'Custom event');
    customSteerInput.value = '';
    if (stageFrame) stageFrame.focus({ preventScroll: true });
  });

  // Pointer hold support for on-screen WASD / Arrow pad
  padButtons.forEach((btn) => {
    const genieInput = btn.dataset.genieInput;
    if (!genieInput) return;
    const press = (e) => {
      e.preventDefault();
      if (!activeSession || heldInputs.has(genieInput)) return;
      heldInputs.add(genieInput);
      btn.classList.add('pressed');
      sendNativeAction('key_down', genieInput);
    };
    const release = () => {
      if (!heldInputs.has(genieInput)) return;
      heldInputs.delete(genieInput);
      btn.classList.remove('pressed');
      sendNativeAction('key_up', genieInput);
    };
    btn.addEventListener('pointerdown', press);
    btn.addEventListener('pointerup', release);
    btn.addEventListener('pointerleave', release);
    btn.addEventListener('pointercancel', release);
  });

  // Keyboard steering when live and not typing in an input
  window.addEventListener('keydown', (e) => {
    if (!activeSession || isTypingTarget(document.activeElement)) return;
    if (e.repeat) return;

    if (NATIVE_KEY_MAP[e.code]) {
      e.preventDefault();
      const inputName = NATIVE_KEY_MAP[e.code];
      heldInputs.add(inputName);
      sendNativeAction('key_down', inputName);
      const matchBtn = padButtons.find((b) => b.dataset.genieInput === inputName);
      if (matchBtn) matchBtn.classList.add('pressed');
    } else if (activeVerbProfile[e.code]) {
      e.preventDefault();
      const spec = activeVerbProfile[e.code];
      sendWorldImpulse(spec.text, spec.label);
    } else if (e.code === 'Escape') {
      releaseAllHeldKeys();
    }
  });

  window.addEventListener('keyup', (e) => {
    if (!activeSession || !NATIVE_KEY_MAP[e.code]) return;
    const inputName = NATIVE_KEY_MAP[e.code];
    if (heldInputs.has(inputName)) {
      heldInputs.delete(inputName);
      sendNativeAction('key_up', inputName);
      const matchBtn = padButtons.find((b) => b.dataset.genieInput === inputName);
      if (matchBtn) matchBtn.classList.remove('pressed');
    }
  });

  window.addEventListener('blur', releaseAllHeldKeys);

  stageFrame?.addEventListener('focus', () => {
    if (hudFocusHint) hudFocusHint.textContent = 'WASD + Arrows Active';
  });
  stageFrame?.addEventListener('blur', () => {
    if (hudFocusHint) hudFocusHint.textContent = 'Click viewport for WASD';
  });

  // 10-second hidden-tab billing guard (matches Google AI Studio Live protection)
  document.addEventListener('visibilitychange', () => {
    if (!activeSession) return;
    if (document.hidden) {
      releaseAllHeldKeys();
      hiddenTabTimeout = setTimeout(() => {
        if (document.hidden && activeSession) {
          stopWorldSession('Auto-stopped after tab was hidden for 10s to prevent idle billing.');
        }
      }, HIDDEN_TAB_AUTOSTOP_MS);
    } else if (hiddenTabTimeout) {
      clearTimeout(hiddenTabTimeout);
      hiddenTabTimeout = null;
    }
  });

  // Belt-and-suspenders unload cleanup
  window.addEventListener('pagehide', beaconEmergencyStop);
  window.addEventListener('beforeunload', beaconEmergencyStop);
}

// Init
applyPreset(presetSelect?.value || 'lunar_ice_ambush');
updateTimerDisplay(0);
updateIdleRecorderTelemetry();
wireEventListeners();
probeBackendCapabilities();
loadSeedImageBase64().catch(() => { });
