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
const COST_PER_SEC_USD = 0.10;
const IMPULSE_REPEATS = 10;
const IMPULSE_INTERVAL_MS = 150;
const VERB_COOLDOWN_MS = 2000;
const HIDDEN_TAB_AUTOSTOP_MS = 10000;
const MAX_WEBRTC_RAW_BYTES = 48000;

// Prompts aligned with Genie 4 official prompting rules:
// - Frame-0 visible propulsion
// - Broadband physical contact Foley (no soundtrack / narrowband drone words)
// - Causal Rule: triggers anchored to distant concrete objects ("far away from me")
// - Original stylized aesthetic (no trademarked studio brand names)
const WORLD_PRESETS = {
  pip_corridor: {
    name: 'Orbital Habitat Corridor',
    useSeedByDefault: true,
    prompt:
      'Stylized 3D animated space-science adventure following closely behind Commander Pip, a cheerful white lab mouse in a white-and-orange EVA spacesuit with a clear gold-tinted visor and small articulated orange tail-wing thrusters puffing forward along brushed aluminum handrails down a bright modular orbital research corridor. Translucent floating nutrient droplets drift gently past glowing cyan bio-telemetry panels toward a circular cupola shutter lever far away from me at the end of the corridor. Rule: Approaching the circular cupola shutter lever slides open the viewport revealing bright golden sunrise light over Earth\'s curved blue horizon. Audio: Crisp micro-thruster air bursts, soft gloved fingertips tapping metal handrails, gentle water droplets clinking softly against aluminum bulkheads, and quiet velcro fabric rustling.',
  },
  cupola_sunrise: {
    name: 'Cupola Earth-Sunrise Bay',
    useSeedByDefault: false,
    prompt:
      'Immersive first-person EVA POV gripping white padded handrails while gliding slowly forward through a sunlit orbital observation module lined with silver equipment racks, floating water spheres, and an amber mechanical shutter lever on a circular cupola console far away from me. Rule: Pulling the amber shutter lever slides open the heavy cupola blast shields to reveal bright golden sunlight sweeping across Earth\'s curved blue atmosphere and swirling white clouds. Audio: Soft fabric glove friction on painted aluminum rails, crisp metallic latch clicks, gentle pressurized air puffs, and delicate water beads tapping clear glass.',
  },
  botany_dome: {
    name: 'Zero-G Bio-Botany Dome',
    useSeedByDefault: false,
    prompt:
      'Stylized 3D animated first-person POV holding a cylindrical white handrail gliding smoothly through a bright zero-gravity orbital botany dome lined with translucent green seedling pods, floating mist beads, and a bright orange watering valve far away from me on the central pedestal. Rule: Turning the orange watering valve releases a shower of sparkling floating water beads drifting across sunlit green leaves. Audio: Crisp rustling plant leaves, water droplets pattering lightly against acrylic pods, metallic handrail taps, and soft mechanical valve clicks.',
  },
};

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

const CUSTOM_VERB_PROMPTS = {
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
const hudFocusHint = document.getElementById('hud-focus-hint');

const liveStatusPill = document.getElementById('live-status-pill');
const sessionTimerBadge = document.getElementById('session-timer-badge');
const errorBanner = document.getElementById('error-banner');
const politeAnnouncer = document.getElementById('polite-announcer');
const cooldownIndicator = document.getElementById('cooldown-indicator');

const presetSelect = document.getElementById('preset-select');
const worldPromptTextarea = document.getElementById('world-prompt-textarea');
const toggleUseSeedImage = document.getElementById('toggle-use-seed-image');
const durationSelect = document.getElementById('duration-select');
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
  const preset = WORLD_PRESETS[presetKey] || WORLD_PRESETS.pip_corridor;
  if (worldPromptTextarea) worldPromptTextarea.value = preset.prompt;
  if (toggleUseSeedImage) toggleUseSeedImage.checked = preset.useSeedByDefault;
  if (hudPresetName) hudPresetName.textContent = preset.name;
}

async function loadSeedImageBase64() {
  if (cachedSeedBase64) return cachedSeedBase64;
  const resp = await fetch(SEED_IMAGE_URL);
  if (!resp.ok) {
    throw new Error(`Could not load seed image (${resp.status})`);
  }
  const buf = await resp.arrayBuffer();
  if (buf.byteLength > MAX_WEBRTC_RAW_BYTES) {
    throw new Error(`Seed image (${buf.byteLength} bytes) exceeds 48 KB WebRTC SCTP safety limit.`);
  }
  const bytes = new Uint8Array(buf);
  let binary = '';
  for (let i = 0; i < bytes.length; i += 0x8000) {
    binary += String.fromCharCode(...bytes.subarray(i, i + 0x8000));
  }
  cachedSeedBase64 = btoa(binary);
  cachedSeedBytes = buf.byteLength;
  if (telSeedSize) {
    telSeedSize.textContent = `${(cachedSeedBytes / 1024).toFixed(1)} KB JPEG (< 48 KB cap)`;
  }
  return cachedSeedBase64;
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
  if (stageFrame) stageFrame.classList.toggle('streaming', isLive);
  if (liveHud) liveHud.classList.toggle('hidden', !isLive);
  if (worldVideo) worldVideo.classList.toggle('hidden', !isLive);
  if (seedPreviewImg) seedPreviewImg.classList.toggle('hidden', isLive);
  if (stageOverlay) stageOverlay.classList.toggle('hidden', isLive);
}

function finalizeLocalCleanup(reasonText = 'Standby') {
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
      }).catch(() => {});
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
      activeSession.complete().catch(() => {});
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
      worldVideo.play().catch(() => {});
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
      document.exitFullscreen().catch(() => {});
    } else if (stageFrame.requestFullscreen) {
      stageFrame.requestFullscreen().catch(() => {});
    }
  });

  // Custom key-bound verb buttons
  verbButtons.forEach((btn) => {
    btn.addEventListener('click', () => {
      const code = btn.dataset.verbKey;
      const spec = CUSTOM_VERB_PROMPTS[code];
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
    } else if (CUSTOM_VERB_PROMPTS[e.code]) {
      e.preventDefault();
      const spec = CUSTOM_VERB_PROMPTS[e.code];
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
applyPreset('pip_corridor');
updateTimerDisplay(0);
wireEventListeners();
probeBackendCapabilities();
loadSeedImageBase64().catch(() => {});
