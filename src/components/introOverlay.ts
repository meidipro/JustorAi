// src/components/introOverlay.ts
// Fullscreen WEBP frame‑sequence intro overlay.
// Auto‑discovers frames via Vite import.meta.glob, sorts by index.
// Plays FAST (~1.4 s total), shows Enter button, then fades out.
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

/** If the intro was already viewed this session, returns false immediately. */
export function shouldShowIntro(): boolean {
  return !sessionStorage.getItem(SESSION_KEY);
}

/**
 * Mount the intro overlay to document.body.
 * Resolves once the user clicks Enter and the fade‑out finishes.
 */
export function mountIntroOverlay(): Promise<void> {
  return new Promise((resolve) => {
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

    // No manual enter button needed, it will auto-dismiss

    // Skip button (top‑right, always visible)
    const skipBtn = document.createElement('button');
    skipBtn.id = 'intro-skip-btn';
    skipBtn.textContent = 'Skip';
    overlay.appendChild(skipBtn);

    document.body.appendChild(overlay);

    // Lock scroll
    document.documentElement.style.overflow = 'hidden';
    document.body.style.overflow = 'hidden';

    /* ── Frame loading ────────────────────────────────── */
    const frames: HTMLImageElement[] = new Array(TOTAL_FRAMES);
    let loadedCount = 0;
    const PRELOAD_BATCH = 12; // load first 12 before starting playback

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
          // Create a blank placeholder so playback doesn't break
          frames[i] = img;
          loadedCount++;
          res();
        };
      });

    /* ── Canvas rendering ─────────────────────────────── */
    const ctx = canvas.getContext('2d')!;
    let currentFrame = 0;
    let playing = false;

    const resize = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
      // Re‑draw current frame after resize
      if (frames[currentFrame]) drawFrame(frames[currentFrame]);
    };
    window.addEventListener('resize', resize);
    resize();

    function drawFrame(img: HTMLImageElement) {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      // Strict Cover-fit: ensuring no black bars are ever visible,
      // regardless of device orientation or background colors.
      const imgRatio = img.naturalWidth / img.naturalHeight;
      const canvasRatio = canvas.width / canvas.height;
      let dw: number, dh: number, dx: number, dy: number;

      if (canvasRatio > imgRatio) {
        // Monitor/Desktop (Wider than video)
        // Stretch width to match screen, crop top and bottom
        dw = canvas.width;
        dh = canvas.width / imgRatio;
        dx = 0;
        dy = (canvas.height - dh) / 2;
      } else {
        // Mobile (Taller than video)
        // Stretch height to match screen, crop left and right
        dh = canvas.height;
        dw = canvas.height * imgRatio;
        dy = 0;
        dx = (canvas.width - dw) / 2; // dx becomes negative, centering the crop
      }
      ctx.drawImage(img, dx, dy, dw, dh);
    }

    /* ── Playback loop (VERY FAST — target ≈2.2s total, not limited to 60fps) */
    const TARGET_DURATION = 2200; // ms total playback
    const FRAME_DELAY = TARGET_DURATION / TOTAL_FRAMES; // no 16ms clamp anymore

    function play() {
      playing = true;
      loader.style.display = 'none';
      let startTime = performance.now();

      const tick = (timestamp: number) => {
        if (!playing) return;

        const elapsed = timestamp - startTime;
        // Calculate which frame we SHOULD be on based purely on elapsed time
        const targetFrame = Math.floor(elapsed / FRAME_DELAY);

        // If we are behind, jump ahead but ensure we draw the latest one
        if (targetFrame > currentFrame) {
          currentFrame = Math.min(targetFrame, TOTAL_FRAMES - 1);
          if (frames[currentFrame]) drawFrame(frames[currentFrame]);

          if (currentFrame >= TOTAL_FRAMES - 1) {
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
      sessionStorage.setItem(SESSION_KEY, '1');
      overlay.classList.add('intro-fade-out');
      overlay.addEventListener('transitionend', () => {
        overlay.remove();
        window.removeEventListener('resize', resize);
        // Restore scroll
        document.documentElement.style.overflow = '';
        document.body.style.overflow = '';
        resolve();
      });
    }

    skipBtn.addEventListener('click', dismiss);

    /* ── Kick off loading ─────────────────────────────── */
    // Phase 1 — preload first batch
    const firstBatch = Array.from({ length: PRELOAD_BATCH }, (_, i) => loadFrame(i));
    Promise.all(firstBatch).then(() => {
      play();
      // Phase 2 — load the rest in the background
      for (let i = PRELOAD_BATCH; i < TOTAL_FRAMES; i++) {
        loadFrame(i);
      }
    });
  });
}
