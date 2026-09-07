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
 * Replace with published thread URLs after AWG review.
 */
const AWG_BRAIN_POST_URL = ''; 
const AWG_AIML_POST_URL = ''; 

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
  initVideoPlayerComponent();
  initCitationCopyButton();
  initPlaceholderLinks();
  initSmoothScroll();
});

/**
 * Mobile Navigation Drawer Toggle
 */
function initMobileNavigation() {
  const toggleBtn = document.querySelector('.mobile-nav-toggle');
  const navMenu = document.querySelector('.nav-menu');

  if (!toggleBtn || !navMenu) return;

  toggleBtn.addEventListener('click', () => {
    const isOpen = navMenu.classList.toggle('is-open');
    toggleBtn.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
  });

  // Close menu when clicking a link
  navMenu.querySelectorAll('.nav-link').forEach((link) => {
    link.addEventListener('click', () => {
      navMenu.classList.remove('is-open');
      toggleBtn.setAttribute('aria-expanded', 'false');
    });
  });
}

/**
 * Miris Video Player Placeholder / Active Video Player
 */
function initVideoPlayerComponent() {
  const videoWrapper = document.getElementById('video-poster-wrapper');
  const playButton = document.getElementById('video-play-btn');
  const stateOverlay = document.getElementById('video-state-overlay');
  const videoBadge = document.getElementById('video-status-badge');

  if (!videoWrapper) return;

  if (VIDEO_SOURCE && VIDEO_SOURCE.trim() !== '') {
    // A video source has been provided: instantiate real video player
    if (videoBadge) {
      videoBadge.textContent = 'Cinematic Preview';
      videoBadge.classList.remove('badge-gold');
      videoBadge.classList.add('badge-cyan');
    }

    const videoEl = document.createElement('video');
    videoEl.className = 'active-video-element';
    videoEl.src = VIDEO_SOURCE;
    videoEl.autoplay = false;
    videoEl.loop = true;
    videoEl.muted = true;
    videoEl.playsInline = true;
    videoEl.controls = true;
    videoEl.setAttribute('aria-label', 'Commander Pip Zero-G Odyssey Cinematic Video');

    videoWrapper.appendChild(videoEl);

    if (playButton) {
      playButton.addEventListener('click', () => {
        if (stateOverlay) stateOverlay.style.display = 'none';
        videoEl.style.display = 'block';
        videoEl.play();
      });
    }
  } else {
    // No video source: keep functional placeholder state
    if (playButton) {
      playButton.addEventListener('click', (e) => {
        e.preventDefault();
        // Friendly notice when video source is pending
        const titleEl = document.querySelector('.video-clip-title');
        if (titleEl) {
          const original = titleEl.textContent;
          titleEl.textContent = 'Cinematic Reel in Production...';
          setTimeout(() => {
            titleEl.textContent = original;
          }, 2400);
        }
      });
    }
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
