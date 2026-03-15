// src/components/introOverlay.ts
// Fullscreen WEBP frame-sequence intro overlay.
// Auto-discovers frames via Vite import.meta.glob, sorts by index.
// Plays FAST, auto-dismisses when done. Fully responsive.
// Runs once per browser session (sessionStorage flag).

// Dynamically discover all .webp frames in public/intro/sequence/ at build time
const frameModules = import.meta.glob<string>(
  '/public/intro/sequence/frame_*.webp',
  { eager: true, query: '?url', import: 'default' }
);

// Sort by extracted numeric index (frame_00, frame_01, …)
const FRAME_URLS: string[] = Object.entries(frameModules)
  .map(([path, url]) => {
    const match = path.match(/frame_(\d+)/);
    return { index: match ? parseInt(match[1], 10) : 0, url };
  })
  .sort((a, b) => a.index - b.index)
  .map((entry) => entry.url);

const TOTAL_FRAMES = FRAME_URLS.length;

const SESSION_KEY = 'justor_intro_seen';

/** Detect if we're on a mobile/low-power device */
function isMobileDevice(): boolean {
  return window.innerWidth <= 768 || /Mobi|Android|iPhone|iPad|iPod/i.test(navigator.userAgent);
}

/** If the intro was already viewed this session, returns false immediately. */
export function shouldShowIntro(): boolean {
  return !sessionStorage.getItem(SESSION_KEY);
}

/**
 * Mount the intro overlay to document.body.
 * Resolves once the animation finishes or the user skips.
 */
export function mountIntroOverlay(): Promise<void> {
  return new Promise((resolve) => {
    const mobile = isMobileDevice();
    // On mobile: skip every other frame for faster playback & less memory
    const frameStep = mobile ? 2 : 1;
    const effectiveFrames = Math.ceil(TOTAL_FRAMES / frameStep);

    /* ── DOM skeleton ─────────────────────────────────── */
    const overlay = document.createElement('div');
    overlay.id = 'intro-overlay';

    const canvas = document.createElement('canvas');
    canvas.id = 'intro-canvas';
    overlay.appendChild(canvas);

    // Loading ring (visible while preloading first batch)
    const loader = document.createElement('div');
    loader.id = 'intro-loader';
    loader.innerHTML = '<div class="intro-spinner"></div>';
    overlay.appendChild(loader);

    // Skip button (top-right, touch-friendly)
    const skipBtn = document.createElement('button');
    skipBtn.id = 'intro-skip-btn';
    skipBtn.textContent = 'Skip';
    overlay.appendChild(skipBtn);

    document.body.appendChild(overlay);

    // Lock scroll & prevent pull-to-refresh on mobile
    document.documentElement.style.overflow = 'hidden';
    document.body.style.overflow = 'hidden';
    overlay.addEventListener('touchmove', (e) => e.preventDefault(), { passive: false });

    /* ── Frame loading ────────────────────────────────── */
    const frames: HTMLImageElement[] = new Array(TOTAL_FRAMES);
    let loadedCount = 0;
    // Smaller preload batch on mobile to start playback faster
    const PRELOAD_BATCH = mobile ? 4 : 6;

    const loadFrame = (i: number): Promise<void> =>
      new Promise((res) => {
        const img = new Image();
        img.decoding = 'async';
        img.src = FRAME_URLS[i];
        img.onload = () => {
          frames[i] = img;
          loadedCount++;
          res();
        };
        img.onerror = () => {
          frames[i] = img;
          loadedCount++;
          res();
        };
      });

    /* ── Canvas rendering (DPR-aware) ─────────────────── */
    const ctx = canvas.getContext('2d')!;
    let currentFrame = 0;
    let playing = false;
    let dismissed = false;

    // Use a capped DPR to avoid oversized canvas on high-DPI mobile
    const dpr = Math.min(window.devicePixelRatio || 1, mobile ? 2 : 3);

    const resize = () => {
      const w = window.innerWidth;
      const h = window.innerHeight;
      canvas.width = w * dpr;
      canvas.height = h * dpr;
      canvas.style.width = w + 'px';
      canvas.style.height = h + 'px';
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      // Re-draw current frame after resize
      if (frames[currentFrame]) drawFrame(frames[currentFrame]);
    };

    window.addEventListener('resize', resize);
    // Also handle orientation change on mobile
    window.addEventListener('orientationchange', () => {
      setTimeout(resize, 100);
    });
    resize();

    function drawFrame(img: HTMLImageElement) {
      const w = window.innerWidth;
      const h = window.innerHeight;
      ctx.clearRect(0, 0, w, h);

      // Strict Cover-fit: ensuring no black bars are ever visible,
      // regardless of device orientation or background colors.
      const imgRatio = img.naturalWidth / img.naturalHeight;
      const canvasRatio = w / h;
      let dw: number, dh: number, dx: number, dy: number;

      if (canvasRatio > imgRatio) {
        // Monitor/Desktop (Wider than video)
        // Stretch width to match screen, crop top and bottom
        dw = w;
        dh = w / imgRatio;
        dx = 0;
        dy = (h - dh) / 2;
      } else {
        // Mobile (Taller than video)
        // Stretch height to match screen, crop left and right
        dh = h;
        dw = h * imgRatio;
        dy = 0;
        dx = (w - dw) / 2; // dx becomes negative, centering the crop
      }
      ctx.drawImage(img, dx, dy, dw, dh);
    }

    /* ── Playback loop (adaptive duration) ─────────────── */
    // Mobile gets slightly shorter duration since we skip frames
    const TARGET_DURATION = mobile ? 600 : 700;
    const FRAME_DELAY = Math.max(16, Math.round(TARGET_DURATION / effectiveFrames));

    function play() {
      playing = true;
      loader.style.display = 'none';
      let lastTime = 0;

      const tick = (timestamp: number) => {
        if (!playing || dismissed) return;
        if (!lastTime) lastTime = timestamp;
        const elapsed = timestamp - lastTime;

        if (elapsed >= FRAME_DELAY) {
          lastTime = timestamp;
          if (frames[currentFrame]) drawFrame(frames[currentFrame]);
          currentFrame += frameStep;

          if (currentFrame >= TOTAL_FRAMES) {
            playing = false;
            dismiss();
            return;
          }
        }
        requestAnimationFrame(tick);
      };
      requestAnimationFrame(tick);
    }

    /* ── Dismiss logic ────────────────────────────────── */
    function dismiss() {
      if (dismissed) return;
      dismissed = true;
      playing = false;
      sessionStorage.setItem(SESSION_KEY, '1');
      overlay.classList.add('intro-fade-out');

      const cleanup = () => {
        overlay.remove();
        window.removeEventListener('resize', resize);
        document.documentElement.style.overflow = '';
        document.body.style.overflow = '';
        resolve();
      };

      overlay.addEventListener('transitionend', cleanup);
      // Fallback in case transitionend doesn't fire (some mobile browsers)
      setTimeout(cleanup, 400);
    }

    skipBtn.addEventListener('click', dismiss);
    // Also allow tap anywhere on overlay to skip
    overlay.addEventListener('click', (e) => {
      if (e.target === skipBtn) return; // already handled
      if (playing) dismiss();
    });

    /* ── Kick off loading ─────────────────────────────── */
    // Phase 1 — preload first batch (only frames we'll actually use)
    const batchIndices: number[] = [];
    for (let i = 0; i < TOTAL_FRAMES && batchIndices.length < PRELOAD_BATCH; i += frameStep) {
      batchIndices.push(i);
    }
    const firstBatch = batchIndices.map((i) => loadFrame(i));

    Promise.all(firstBatch).then(() => {
      play();
      // Phase 2 — load remaining frames in the background
      for (let i = 0; i < TOTAL_FRAMES; i += frameStep) {
        if (!frames[i]) loadFrame(i);
      }
    });
  });
}
