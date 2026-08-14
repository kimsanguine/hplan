# hplan Intro Video — Remotion + Gemini TTS

70-second README intro video. Korean narration (Gemini TTS) + bilingual on-screen captions.

> The full production plan is maintained locally/private and is intentionally not part of this public repository.

## Quick Start

```bash
cd tools/intro-video

# 1. Install dependencies
npm install

# 2. Preview in browser (live-reload)
npm run dev
```

Open Remotion Studio at `http://localhost:3000` — you'll see 3 compositions:

- `HplanIntro16x9` — 1920×1080 (README primary)
- `HplanIntro1x1` — 1080×1080 (X / LinkedIn)
- `HplanIntro9x16` — 1080×1920 (Shorts / Reels)

Each scrubs through 70 seconds (2100 frames at 30fps).

## Generate Narration (Gemini TTS)

```bash
# 1. Set your Gemini API key (already used in other hplan projects)
export GEMINI_API_KEY="..."

# 2. Generate 8 narration WAV files (~30 seconds total)
npm run narration   # equivalent to: python3 scripts/generate_narration.py

# 3. (Optional) Convert WAV → MP3 to shrink file size
cd public/audio/narration
for f in *.wav; do
  ffmpeg -i "$f" -codec:a libmp3lame -qscale:a 4 "${f%.wav}.mp3"
  rm "$f"
done
cd -

# 4. Open src/compositions/HplanIntro16x9.tsx and uncomment the
#    <Audio> imports (the commented block at the bottom).
```

### Voice A/B Testing

Three voices recommended for the hplan brand:

```bash
VOICE=Charon python3 scripts/generate_narration.py    # deep authoritative (1st pick)
VOICE=Kore   python3 scripts/generate_narration.py    # clear professional
VOICE=Aoede  python3 scripts/generate_narration.py    # warm friendly
```

Listen to **Scene 3** (Solution intro) and pick the one whose pronunciation of "LINE Wallet, 카카오, 이스트소프트" feels most natural for Ethan's authority line.

### Pronunciation Notes

- `hplan` is read by Gemini as "에이치플랜" (Korean phonetic spelling is in the script).
- `p50`, `p90` are pronounced as English digits.
- If a voice mispronounces `LINE` or `CJ`, adjust `STYLE_INSTRUCTION` in `generate_narration.py` with a fix instruction.

## Background Music (BGM)

Drop a 70-second ambient track at `public/audio/bgm.mp3`. Free sources:

- [Pixabay Music](https://pixabay.com/music/) — search "ambient electronic calm"
- [YouTube Audio Library](https://studio.youtube.com/) — Music tab, filter "No attribution required"

The composition mixes BGM at volume 0.15 (≈−16 dB) under the narration. Edit in `src/compositions/HplanIntro16x9.tsx` if you need different mixing.

## Render Final Videos

```bash
# Render all 3 formats
npm run build:all

# Or one at a time
npm run build:16x9   # → out/intro-16x9.mp4
npm run build:1x1    # → out/intro-1x1.mp4
npm run build:9x16   # → out/intro-9x16.mp4

# GIF fallback for README (if mp4 is too large for GitHub video assets)
npm run build:gif    # → out/intro.gif
```

Render times on a modern Mac M-series: 16:9 takes ~1-2 min at concurrency 4.

## Embed in README

GitHub allows MP4 upload via the issue/PR drag-and-drop interface (10MB limit). Steps:

1. Open https://github.com/kimsanguine/hplan and create a draft issue
2. Drag `out/intro-16x9.mp4` into the issue body
3. GitHub generates a `https://github.com/user-attachments/assets/...` URL — copy it
4. Cancel the issue
5. Embed in README.md:

```html
<p align="center">
  <video src="https://github.com/user-attachments/assets/xxx/intro-16x9.mp4"
         autoplay loop muted playsinline width="800">
    <img src="docs/images/intro.gif" alt="hplan intro" />
  </video>
</p>
```

If MP4 > 10MB, either:
- Render 1280×720 instead of 1920×1080 (~40% smaller)
- Upload to YouTube + embed link
- Use the GIF fallback (8-15MB typical)

## File Layout

```
tools/intro-video/
├── package.json
├── tsconfig.json
├── remotion.config.ts
├── README.md                ← you are here
├── scripts/
│   └── generate_narration.py   ← Gemini TTS generator
├── src/
│   ├── index.ts             ← entry point
│   ├── Root.tsx             ← Composition registry (3 formats)
│   ├── theme.ts             ← Catppuccin Mocha palette + SCENE_TIMING
│   ├── compositions/
│   │   ├── HplanIntro16x9.tsx   ← main (1920×1080)
│   │   ├── HplanIntro1x1.tsx    ← square
│   │   └── HplanIntro9x16.tsx   ← vertical
│   ├── scenes/
│   │   ├── 01-Hook.tsx           ← 0-6s
│   │   ├── 02-Problem.tsx        ← 6-20s
│   │   ├── 03-Solution.tsx       ← 20-28s
│   │   ├── 04a-DemoEvidence.tsx  ← 28-36s
│   │   ├── 04b-DemoCogs.tsx      ← 36-46s (hero)
│   │   ├── 04c-DemoHandoff.tsx   ← 46-55s
│   │   ├── 05-Lifecycle.tsx      ← 55-63s
│   │   └── 06-CTA.tsx            ← 63-70s
│   ├── components/
│   │   ├── Terminal.tsx          ← title bar + dots
│   │   ├── TerminalLine.tsx      ← single line with appearAt animation
│   │   ├── TypewriterText.tsx    ← character-by-character reveal
│   │   ├── BlinkingCursor.tsx
│   │   ├── BilingualCaption.tsx  ← Korean + English overlay
│   │   ├── PluginBox.tsx         ← lifecycle stage box
│   │   └── BigStat.tsx           ← count-up number
│   └── data/
│       ├── lifecycle.ts
│       ├── demoEvidence.ts
│       ├── demoCogs.ts
│       └── demoHandoff.ts
├── public/
│   └── audio/                ← generated; gitignored
└── out/                      ← rendered videos; gitignored
```

## Editing Tips

- **Adjust scene timing**: edit `SCENE_TIMING` in `src/theme.ts`. All Sequences reference it.
- **Adjust narration text**: edit `SCENES` in `scripts/generate_narration.py` and re-run.
- **Change voice tone**: edit `STYLE_INSTRUCTION` in the same file — it's a natural-language prompt to Gemini.
- **Tweak demo terminal lines**: each demo has its own data file in `src/data/`. Each line has `appearAt` (frame number relative to scene start).
- **Skip a scene**: comment out its `<Sequence>` in `HplanIntro16x9.tsx`.

## Known Issues / TODO

- [ ] Gemini TTS model name (`gemini-2.5-flash-preview-tts`) may change as the preview matures — check the latest at https://ai.google.dev/gemini-api/docs/speech-generation
- [ ] BGM track not included (license-restricted) — user must provide their own
- [ ] English-dubbed version (using same TTS, English voice + English narration script) is a 1-hour follow-up if global launch needs it

## License

Same as parent repo — [MIT](../../LICENSE).
