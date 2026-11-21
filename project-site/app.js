/**
 * Orbiting Minds: An RR-10 Data-to-3D Simulation Experience
 * Project Site Interactive Logic
 */

// ==========================================================================
// CONFIGURATION CONSTANTS (Update these for future releases)
// ==========================================================================

/**
 * 1. Miris Cinematic Companion Video Source
 * Replace with public video URL or local relative path (e.g., 'assets/miris_pip_cinematic.mp4')
 * Leaving this empty will gracefully display the "Cinematic clip coming soon" state.
 */
const VIDEO_SOURCE = 'assets/Commander-Pip-orbital-habitat-cinematic-sequence.mp4'; 

/**
 * 2. Verified Google Scholar Profile URL
 * Replace with your public Google Scholar link once active.
 */
const GOOGLE_SCHOLAR_URL = 'https://scholar.google.com/citations?view_op=view_citation&hl=en&user=juOv0f0AAAAJ&citation_for_view=juOv0f0AAAAJ:d1gkVwhDpl0C'; 

/**
 * 3. NASA GeneLab Analysis Working Group (AWG) Direct Discussion URLs
 * Live NASA OSDR AWG thread tagged both `aiml` and `brainawg`.
 */
const AWG_BRAIN_POST_URL = 'https://awg.osdr.space/t/can-frontier-llms-accurately-interpret-spaceflight-biology-rr-10-benchmark-interactive-3d-viewer/4569';
const AWG_AIML_POST_URL = 'https://awg.osdr.space/t/can-frontier-llms-accurately-interpret-spaceflight-biology-rr-10-benchmark-interactive-3d-viewer/4569';

/**
 * 4. Live Production Project Deployment URL
 * Replace with GitHub Pages or custom domain URL once hosted.
 */
const LIVE_PROJECT_PAGE_URL = 'https://orbiting-minds.vercel.app/'; 


// ==========================================================================
// DOM Ready & Component Initializations
// ==========================================================================

document.addEventListener('DOMContentLoaded', () => {
  initMobileNavigation();
  initHeaderScrollFallback();
  initVideoPlayerComponent();
  initCitationCopyButton();
  initPlaceholderLinks();
  initSmoothScroll();
  initV11CorpusSummary();
});

/**
 * Fallback scroll-direction header hiding for browsers without @container scroll-state
 */
function initHeaderScrollFallback() {
  if (typeof CSS !== 'undefined' && CSS.supports && CSS.supports('container-type', 'scroll-state')) {
    return;
  }
  const bar = document.querySelector('.site-header');
  if (!bar) return;
  let lastY = window.scrollY;
  window.addEventListener(
    'scroll',
    () => {
      const maxScroll = Math.max(0, document.documentElement.scrollHeight - window.innerHeight);
      const y = Math.max(0, Math.min(window.scrollY, maxScroll));
      if (y === lastY) return;
      bar.classList.toggle('is-hidden', y > lastY && y > bar.offsetHeight);
      lastY = y;
    },
    { passive: true }
  );
}

/**
 * Mobile Navigation Drawer Toggle
 */
function initMobileNavigation() {
  const toggleBtn = document.querySelector('.mobile-nav-toggle');
  const navMenu = document.querySelector('.nav-menu');
  const headerEl = document.querySelector('.site-header');

  if (!toggleBtn || !navMenu) return;

  const setOpen = (isOpen) => {
    navMenu.classList.toggle('is-open', isOpen);
    toggleBtn.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
    if (headerEl) headerEl.classList.toggle('nav-menu-open', isOpen);
  };

  toggleBtn.addEventListener('click', () => {
    setOpen(!navMenu.classList.contains('is-open'));
  });

  // Close menu when clicking a link or pressing Escape
  navMenu.querySelectorAll('.nav-link, .nav-cta-btn').forEach((link) => {
    link.addEventListener('click', () => setOpen(false));
  });
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && navMenu.classList.contains('is-open')) {
      setOpen(false);
      toggleBtn.focus();
    }
  });
}

/**
 * Commander Pip Video Player & 3D Viewer Branch Handlers
 */
function initVideoPlayerComponent() {
  const videoEl = document.getElementById('commander-pip-video');
  if (videoEl) {
    // Native video is embedded and active
    videoEl.addEventListener('play', () => {
      // Optional tracking or telemetry
    });
  }

  // Inspect Pip in 3D Viewer button handler
  const inspectPipBtn = document.getElementById('inspectPipBtn');
  if (inspectPipBtn) {
    inspectPipBtn.addEventListener('click', () => {
      try {
        sessionStorage.setItem('preferred_branch', 'media');
      } catch (e) {
        // Safe fallback if session storage is disabled
      }
    });
  }
}

/**
 * Citation Copy-to-Clipboard with Inline Feedback
 */
function initCitationCopyButton() {
  const copyBtn = document.getElementById('copy-citation-btn');
  const citationTextEl = document.getElementById('citation-text');
  const confirmMsg = document.getElementById('citation-confirm-msg');

  if (!copyBtn || !citationTextEl) return;

  copyBtn.addEventListener('click', () => {
    const textToCopy = citationTextEl.textContent.trim();

    navigator.clipboard.writeText(textToCopy).then(() => {
      copyBtn.classList.add('copied');
      copyBtn.innerHTML = `
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polyline points="20 6 9 17 4 12"></polyline>
        </svg>
        Copied to Clipboard!
      `;

      if (confirmMsg) {
        confirmMsg.classList.add('visible');
      }

      setTimeout(() => {
        copyBtn.classList.remove('copied');
        copyBtn.innerHTML = `
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
            <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
          </svg>
          Copy Citation
        `;
        if (confirmMsg) {
          confirmMsg.classList.remove('visible');
        }
      }, 2500);
    }).catch((err) => {
      console.warn('Clipboard write failed, falling back:', err);
      // Fallback selection
      const range = document.createRange();
      range.selectNodeContents(citationTextEl);
      const selection = window.getSelection();
      selection.removeAllRanges();
      selection.addRange(range);
      copyBtn.textContent = 'Selected (Press Ctrl+C)';
    });
  });
}

/**
 * Inactive Placeholders Management
 * Ensures placeholders remain visually distinct and non-misleading
 */
function initPlaceholderLinks() {
  // If user populates URLs in the configuration constants above, wire them dynamically
  if (GOOGLE_SCHOLAR_URL) {
    document.querySelectorAll('.scholar-placeholder').forEach((el) => {
      el.href = GOOGLE_SCHOLAR_URL;
      el.target = '_blank';
      el.rel = 'noopener noreferrer';
      el.classList.remove('resource-card-placeholder');
    });
  }

  if (AWG_BRAIN_POST_URL) {
    const brainEl = document.getElementById('placeholder-awg-brain');
    if (brainEl) {
      brainEl.href = AWG_BRAIN_POST_URL;
      brainEl.target = '_blank';
      brainEl.rel = 'noopener noreferrer';
      brainEl.classList.remove('resource-card-placeholder');
    }
  }

  if (AWG_AIML_POST_URL) {
    const aimlEl = document.getElementById('placeholder-awg-aiml');
    if (aimlEl) {
      aimlEl.href = AWG_AIML_POST_URL;
      aimlEl.target = '_blank';
      aimlEl.rel = 'noopener noreferrer';
      aimlEl.classList.remove('resource-card-placeholder');
    }
  }

  if (LIVE_PROJECT_PAGE_URL) {
    const liveEl = document.getElementById('placeholder-live-site');
    if (liveEl) {
      liveEl.href = LIVE_PROJECT_PAGE_URL;
      liveEl.target = '_blank';
      liveEl.rel = 'noopener noreferrer';
      liveEl.classList.remove('resource-card-placeholder');
    }
  }
}

/**
 * In-Page Smooth Scrolling
 */
function initSmoothScroll() {
  document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
    anchor.addEventListener('click', function (e) {
      const targetId = this.getAttribute('href');
      if (targetId === '#' || targetId === '') return;

      const targetEl = document.querySelector(targetId);
      if (targetEl) {
        e.preventDefault();
        const navOffset = 80;
        const elementPosition = targetEl.getBoundingClientRect().top;
        const offsetPosition = elementPosition + window.pageYOffset - navOffset;

        window.scrollTo({
          top: offsetPosition,
          behavior: 'smooth',
        });
      }
    });
  });
}

/**
 * Dynamic RR-10 v1.1 Full Corpus Scale-Up Card (5,630 Items)
 * Loads strictly aggregated, public-safe metrics from ../data/processed/rr10_v1_1_public_summary.json
 */
function initV11CorpusSummary() {
  const tbody = document.getElementById('site-v11-scoreboard-tbody');
  const shaBtn = document.getElementById('site-copy-v11-sha');
  const shaShort = document.getElementById('site-v11-sha-short');
  const shaStatus = document.getElementById('site-v11-sha-status');
  const ablationText = document.getElementById('site-v11-ablation-text');
  const roadmapText = document.getElementById('site-v11-roadmap-text');

  const normModel = (name) => (name === 'gemini-3.5-flash-lite' ? 'google/gemini-3.5-flash-lite' : name);

  if (shaBtn) {
    shaBtn.addEventListener('click', () => {
      const fullSha = shaBtn.dataset.sha || '';
      if (!fullSha) return;
      const showCopied = () => {
        if (shaStatus) {
          shaStatus.textContent = 'Copied ✓';
          setTimeout(() => {
            shaStatus.textContent = 'Copy';
          }, 2200);
        }
      };
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard
          .writeText(fullSha)
          .then(showCopied)
          .catch(() => {
            const ta = document.createElement('textarea');
            ta.value = fullSha;
            ta.style.position = 'fixed';
            ta.style.opacity = '0';
            document.body.appendChild(ta);
            ta.select();
            try {
              document.execCommand('copy');
              showCopied();
            } catch (_) {
              if (shaStatus) shaStatus.textContent = 'Select SHA';
            }
            document.body.removeChild(ta);
          });
      }
    });
  }

  if (!tbody) return;

  const fmtPct = (v) => (typeof v === 'number' && !Number.isNaN(v) ? `${(v * 100).toFixed(2)}%` : '--');
  const esc = (s) =>
    String(s)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');

  fetch('../data/processed/rr10_v1_1_public_summary.json')
    .then((res) => {
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      return res.json();
    })
    .then((data) => {
      if (data.canonical_sha256 && shaBtn && shaShort) {
        shaBtn.dataset.sha = data.canonical_sha256;
        shaShort.textContent = `${data.canonical_sha256.slice(0, 8)}...${data.canonical_sha256.slice(-6)}`;
      }

      const rows = [];
      const baselines = (data.verification && data.verification.baselines) || {};
      if (baselines.gold_oracle_5630) {
        const b = baselines.gold_oracle_5630;
        rows.push({
          name: 'Gold Oracle Baseline',
          protocol: 'Canonical Reference (5,630)',
          n: `${b.n_items.toLocaleString()} (${b.n_pairs.toLocaleString()})`,
          pdr: b.pdr,
          trapAcc: b.trap_accuracy,
          trapOver: b.trap_overclaim_rate,
          ctrlAcc: b.control_accuracy,
          ctrlAbst: b.control_abstention_rate,
          rowCls: 'row-perfect',
        });
      }
      if (baselines.all_indeterminate_5630) {
        const b = baselines.all_indeterminate_5630;
        rows.push({
          name: 'All-Indeterminate Baseline',
          protocol: 'Blanket Abstention (5,630)',
          n: `${b.n_items.toLocaleString()} (${b.n_pairs.toLocaleString()})`,
          pdr: b.pdr,
          trapAcc: b.trap_accuracy,
          trapOver: b.trap_overclaim_rate,
          ctrlAcc: b.control_accuracy,
          ctrlAbst: b.control_abstention_rate,
          rowCls: '',
        });
      }

      const sb = data.scoreboard || {};
      (sb.full_5630_neutral_runs || []).forEach((run) => {
        rows.push({
          name: run.model,
          protocol: 'Full Neutral Closed-Book',
          n: `${run.n_items.toLocaleString()} (${run.n_pairs.toLocaleString()})`,
          pdr: run.metrics.pdr,
          trapAcc: run.metrics.trap_accuracy,
          trapOver: run.metrics.trap_overclaim_rate,
          ctrlAcc: run.metrics.control_accuracy,
          ctrlAbst: run.metrics.control_abstention_rate,
          rowCls: '',
        });
      });
      (sb.stratified_440_neutral_runs || []).forEach((run) => {
        rows.push({
          name: run.model,
          protocol: 'Stratified 440 Neutral Pilot',
          n: `${run.n_items.toLocaleString()} (${run.n_pairs.toLocaleString()})`,
          pdr: run.metrics.pdr,
          trapAcc: run.metrics.trap_accuracy,
          trapOver: run.metrics.trap_overclaim_rate,
          ctrlAcc: run.metrics.control_accuracy,
          ctrlAbst: run.metrics.control_abstention_rate,
          rowCls: '',
        });
      });

      tbody.innerHTML = rows
        .map(
          (r) => `
        <tr class="${r.rowCls}">
          <th scope="row">${esc(r.name)}</th>
          <td>${esc(r.protocol)}</td>
          <td class="text-center">${esc(r.n)}</td>
          <td class="text-center"><span class="score-pill ${r.pdr >= 0.99 ? 'total-100' : r.pdr >= 0.1 ? 'total-high' : 'total-mid'}">${fmtPct(r.pdr)}</span></td>
          <td class="text-center">${fmtPct(r.trapAcc)}</td>
          <td class="text-center"><span class="score-pill ${r.trapOver > 0.25 ? 'fail' : 'pass'}">${fmtPct(r.trapOver)}</span></td>
          <td class="text-center">${fmtPct(r.ctrlAcc)}</td>
          <td class="text-center">${fmtPct(r.ctrlAbst)}</td>
        </tr>`
        )
        .join('');

      if (ablationText && sb.caution_coached_ablation_440) {
        const ab = sb.caution_coached_ablation_440;
        const runBits = (ab.runs || [])
          .map(
            (r) =>
              `<code>${esc(normModel(r.model))}</code> (PDR ${fmtPct(r.metrics.pdr)}, Trap Overclaim ${fmtPct(r.metrics.trap_overclaim_rate)}, Ctrl Abstention ${fmtPct(r.metrics.control_abstention_rate)})`
          )
          .join(' · ');
        ablationText.innerHTML = `${esc(ab.note)}<br><span class="v11-ablation-runs">${runBits}</span>`;
      }

      if (roadmapText && data.roadmap_v1_2) {
        const rm = data.roadmap_v1_2;
        roadmapText.innerHTML = `<strong>${esc(rm.credit)}</strong> - ${esc(rm.title)} (<code>${esc(rm.formula)}</code>): ${esc(rm.rationale)}`;
      }

      // Render Per-Model Summary Cards beneath the scoreboard
      const modelCardsContainer = document.getElementById('site-v11-model-cards');
      if (modelCardsContainer) {
        const allRuns = [
          ...(sb.full_5630_neutral_runs || []),
          ...(sb.stratified_440_neutral_runs || []),
          ...((sb.caution_coached_ablation_440 && sb.caution_coached_ablation_440.runs) || []),
        ];

        const classifyFailure = (run) => {
          const m = run.metrics;
          if (run.prompt_mode === 'closed-book') return 'Caution-Induced Blanket Abstention Collapse';
          if (m.trap_overclaim_rate >= 0.9) return 'Unchecked Directional Overclaiming';
          if (m.control_abstention_rate >= 0.95) return 'Native Conservative Over-Abstention';
          return 'Mixed Calibration Trade-Off (~44% Trap Overclaim)';
        };

        const pickExtremes = (perCtx) => {
          const entries = Object.entries(perCtx || {});
          const sized = entries.filter(([, v]) => v.n_pairs >= 25);
          const pool = sized.length ? sized : entries;
          if (!pool.length) return { best: 'n/a', worst: 'n/a' };
          const allZeroPdr = pool.every(([, v]) => v.pdr === 0);
          const allZeroOver = pool.every(([, v]) => v.trap_overclaim_rate === 0);
          const allZeroCtrl = pool.every(([, v]) => v.control_accuracy === 0);
          if (allZeroPdr && allZeroOver) {
            return {
              best: 'All contexts tied at 0.00% PDR / 100% CtrlAbst',
              worst: 'None (0.00% TrapOver across all contexts)',
            };
          }
          const best = [...pool].sort((a, b) => (b[1].pdr - a[1].pdr) || (b[1].control_accuracy - a[1].control_accuracy))[0];
          const worst = [...pool].sort((a, b) => (b[1].trap_overclaim_rate - a[1].trap_overclaim_rate) || (a[1].pdr - b[1].pdr))[0];
          return {
            best:
              allZeroPdr && allZeroCtrl
                ? 'All contexts tied at 0.00% PDR / 0.00% CtrlAcc'
                : allZeroPdr
                ? `All tied at 0.00% PDR (max CtrlAcc: ${best[0]} ${fmtPct(best[1].control_accuracy)})`
                : `${best[0]} (PDR ${fmtPct(best[1].pdr)})`,
            worst: `${worst[0]} (Over ${fmtPct(worst[1].trap_overclaim_rate)})`,
          };
        };

        modelCardsContainer.innerHTML = allRuns
          .map((run) => {
            const m = run.metrics;
            const t = run.telemetry || {};
            const ex = pickExtremes(run.per_context);
            const tagCls =
              run.prompt_mode === 'closed-book'
                ? 'badge-gold'
                : m.trap_overclaim_rate >= 0.9
                ? 'badge-terracotta'
                : 'badge-cyan';
            return `
              <article class="v11-model-card">
                <div class="v11-model-card-top">
                  <code class="v11-model-card-name">${esc(normModel(run.model))}</code>
                  <span class="badge ${tagCls}">${esc(run.protocol_label)}</span>
                </div>
                <div class="v11-model-card-metrics">
                  <span><strong>PDR:</strong> ${fmtPct(m.pdr)}</span>
                  <span><strong>TrapOver:</strong> ${fmtPct(m.trap_overclaim_rate)}</span>
                  <span><strong>CtrlAcc:</strong> ${fmtPct(m.control_accuracy)}</span>
                  <span><strong>CtrlAbst:</strong> ${fmtPct(m.control_abstention_rate)}</span>
                  <span><strong>Parse:</strong> ${fmtPct(t.parse_rate)}</span>
                  <span><strong>Scale:</strong> ${run.n_items.toLocaleString()} items</span>
                </div>
                <p class="v11-model-card-mode"><strong>Failure Mode:</strong> ${esc(classifyFailure(run))}</p>
                <p class="v11-model-card-ctx"><strong>Strongest:</strong> <code>${esc(ex.best)}</code><br><strong>Highest Risk:</strong> <code>${esc(ex.worst)}</code></p>
              </article>`;
          })
          .join('');
      }
    })
    .catch((err) => {
      console.warn('Could not load RR-10 v1.1 public summary:', err);
      tbody.innerHTML =
        '<tr><th scope="row">Summary unavailable offline</th><td colspan="7">Serve via HTTP (<code>python3 run_pipeline.py --serve</code>) to inspect live v1.1 metrics.</td></tr>';
    });
}
