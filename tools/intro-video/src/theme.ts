/**
 * Catppuccin Mocha — visual theme for hplan intro video.
 * Matches the existing assets/images/demo-terminal.svg palette so the video
 * and the static README SVG feel like the same product.
 */

export const colors = {
  bg: '#1e1e2e',
  titleBar: '#313244',
  surface: '#181825',
  text: '#cdd6f4',
  dim: '#a6adc8',
  veryDim: '#6c7086',
  prompt: '#89b4fa',
  skillTag: '#cba6f7',
  arrow: '#f9e2af',
  ok: '#a6e3a1',
  warn: '#f9e2af',
  bad: '#f38ba8',
  dotRed: '#f38ba8',
  dotYellow: '#f9e2af',
  dotGreen: '#a6e3a1',
  // hplan brand red
  hplanRed: '#dc2626',
  hplanRedSoft: '#f87171',
  // v0.8 brand colors
  trackBlue: '#7dd3fc',     // cyan-300, prompt-level 데이터
  trackBlueSoft: '#0891b2',
  craftRose: '#fda4af',     // rose-300, RESPECT.md 디자인
  craftRoseSoft: '#e11d48',
};

export const fonts = {
  mono: "'SF Mono', 'JetBrains Mono', 'Fira Code', 'Menlo', monospace",
  display: "'Inter', 'SF Pro Display', -apple-system, system-ui, sans-serif",
};

export const typography = {
  hookSize: 64,
  titleSize: 48,
  bodySize: 24,
  smallSize: 18,
  captionSize: 16,
  terminalSize: 22,
  terminalSmall: 18,
};

/**
 * Total video length is 84s at 30fps = 2520 frames.
 * v0.6.1: extended from 70s to 84s after first Gemini TTS render produced
 * narration longer than initial budget. Sped narration 1.2x via ffmpeg atempo
 * and reset scene durations to fit each clip + small visual buffer.
 *
 * Each scene exposes [startFrame, endFrame] for absolute placement.
 */
export const SCENE_TIMING = {
  hook: { start: 0, end: 180 },             // 0-6s   (narration 5.0s + 1s buffer)
  problem: { start: 180, end: 750 },        // 6-25s  (narration 17.8s + 1.2s buffer)
  solution: { start: 750, end: 990 },       // 25-33s (narration 6.4s + 1.6s buffer)
  demoEvidence: { start: 990, end: 1260 },  // 33-42s (narration 7.1s + 1.9s buffer)
  demoCogs: { start: 1260, end: 1680 },     // 42-56s (narration 12.3s + 1.7s buffer)
  demoHandoff: { start: 1680, end: 1950 },  // 56-65s (narration 8.3s + 0.7s buffer)
  lifecycle: { start: 1950, end: 2310 },    // 65-77s (narration 11.2s + 0.8s buffer)
  cta: { start: 2310, end: 2520 },          // 77-84s (narration 5.0s + 2s buffer)
} as const;

export const FPS = 30;
export const TOTAL_FRAMES = 2520;

/** v0.8 Editorial — 60s (1800 frames). 메시지 위주, typography 중심. */
export const V8E_TIMING = {
  hook: { start: 0, end: 240 },         // 0-8s
  respect: { start: 240, end: 750 },    // 8-25s
  lifecycle: { start: 750, end: 1500 }, // 25-50s
  cta: { start: 1500, end: 1800 },      // 50-60s
} as const;
export const V8E_TOTAL = 1800;

/** v0.8 Core — 84s (2520 frames). hplan 본질 (Build Gate, WHETHER vs HOW) 위주, 사용자 narration 충실. */
export const V8C_TIMING = {
  hook: { start: 0, end: 300 },              // 0-10s
  question: { start: 300, end: 540 },        // 10-18s
  solution: { start: 540, end: 780 },        // 18-26s
  sixQuestions: { start: 780, end: 1230 },   // 26-41s
  threeGates: { start: 1230, end: 1830 },    // 41-61s
  verdict: { start: 1830, end: 2070 },       // 61-69s
  whyMatters: { start: 2070, end: 2370 },    // 69-79s
  stage0: { start: 2370, end: 2520 },        // 79-84s
} as const;
export const V8C_TOTAL = 2520;

/** v0.8 Core + Track Guardrail — 99s (2970 frames). Core 위에 track 만들기-중 가드레일 1 scene 추가. */
export const V8CT_TIMING = {
  hook: { start: 0, end: 300 },                    // 0-10s
  question: { start: 300, end: 540 },              // 10-18s
  solution: { start: 540, end: 780 },              // 18-26s
  sixQuestions: { start: 780, end: 1230 },         // 26-41s
  threeGates: { start: 1230, end: 1830 },          // 41-61s
  verdict: { start: 1830, end: 2070 },             // 61-69s
  trackGuardrail: { start: 2070, end: 2520 },      // 69-84s — NEW
  whyMatters: { start: 2520, end: 2820 },          // 84-94s
  stage0: { start: 2820, end: 2970 },              // 94-99s
} as const;
export const V8CT_TOTAL = 2970;

/** v0.8 Demo — 90s (2700 frames). 시스템·데모 위주. */
export const V8D_TIMING = {
  hook: { start: 0, end: 150 },              // 0-5s
  twoGaps: { start: 150, end: 450 },         // 5-15s
  trackDemo: { start: 450, end: 900 },       // 15-30s
  craftDemo: { start: 900, end: 1350 },      // 30-45s
  lifecycle: { start: 1350, end: 1800 },     // 45-60s
  convergence: { start: 1800, end: 2250 },   // 60-75s
  cta: { start: 2250, end: 2700 },           // 75-90s
} as const;
export const V8D_TOTAL = 2700;
