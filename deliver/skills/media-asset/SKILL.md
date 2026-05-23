---
name: media-asset
description: "Unified media asset production skill — video (Remotion React-based agent demo video) and infographic (HTML/CSS → GIF/MP4 animated infographic). --type 인자 필수 (기본값 없음). gemini-image-flow 는 통합하지 않음. Use when creating visual assets for stakeholder communication, documentation, or demo materials."
argument-hint: "--type video|infographic [target description or topic]"
allowed-tools: ["Read", "Write", "Edit", "Bash"]
model: sonnet
---

## Core Goal

두 미디어 에셋 제작 워크플로우를 단일 인터페이스로 통합한다:

| type | 책임 | 기술 스택 | 출력 |
|---|---|---|---|
| `--type video` | 에이전트 데모 영상 제작 | Remotion (React) | output.mp4, 1920×1080, 30fps |
| `--type infographic` | 애니메이션 인포그래픽 제작 | HTML/CSS → ffmpeg | output.gif (≤8MB) 또는 output.mp4 (≤50MB) |

> ⚠️ **`--type` 인자 필수**: 기본값 없음. 미명시 시 에러 출력 후 type 목록 안내.
>
> gemini-image-flow는 이 스킬에 통합하지 않음.

---

## Trigger Gate

### Use This Skill When
- 에이전트 데모 영상 제작 (투자자·이해관계자·랜딩페이지용) → `--type video`
- 에이전트 아키텍처·워크플로우 애니메이션 GIF/MP4 제작 → `--type infographic`
- README/문서 삽입용 루프 GIF 필요 → `--type infographic`

### Route to Other Skills When
- 정적 슬라이드 (PPTX) → `pptx-ai-slide`
- 정적 이미지 생성 → `gemini-image-flow`
- 에이전트 아키텍처 설계 자체 → `3-tier` 또는 `orchestration`
- 멀티씬 장편 영상 합성 파이프라인 → `compose-video`

### Boundary Checks
- `--type` 미명시 → 에러 + type 목록 출력, 실행 중단
- Remotion 미설치 (`--type video`) → fail loud + 설치 안내
- Puppeteer/Playwright 미설치 (`--type infographic`) → fail loud + 설치 안내

---

## Inputs

| 입력 | 출처 | 처리 |
|---|---|---|
| `--type` | `$ARGUMENTS` | video/infographic 분기 |
| target | `$ARGUMENTS` (type 이후 나머지) | 스토리라인 설계 또는 장면 설계 |

---

## Instructions

You are producing a media asset with arguments: **$ARGUMENTS**

### 공통 Step 0 — type 파싱

```
args = parse("$ARGUMENTS")
type = args.get("--type", None)
target = args remainder after --type value
```

`--type` 미명시 시:
```
❌ 에러: --type 인자가 필요합니다.

사용 가능한 type:
  --type video         Remotion 기반 에이전트 데모 영상 (1920×1080 MP4)
  --type infographic   HTML/CSS → GIF/MP4 애니메이션 인포그래픽

예시: media-asset --type video "고객 문의 분류 에이전트 60초 데모"
     media-asset --type infographic "3-Tier 에이전트 아키텍처 GIF"
```

---

### type: video

Remotion(React) 기반으로 에이전트 데모 영상을 제작한다.

**Step 1 — 스토리라인 설계**
- 에이전트 핵심 가치 1문장
- 5단계 구조: Hook(0~5s) → 문제(5~15s) → 데모(15~45s) → 성과(45~55s) → CTA(55~60s)
- 총 영상 길이 결정 (권장 30~90초)
- 스토리라인 불명확 시 3개 후보 제시 + 사용자 선택

**Step 2 — Composition 설계**

```typescript
const AgentDemo: React.FC = () => (
  <Composition
    id="agent-demo"
    component={DemoVideo}
    width={1920} height={1080} fps={30}
    durationInFrames={1800}   // 60초
  />
);

const DemoVideo: React.FC = () => (
  <>
    <Sequence from={0} durationInFrames={150}><HookScene /></Sequence>
    <Sequence from={150} durationInFrames={300}><ProblemScene /></Sequence>
    <Sequence from={450} durationInFrames={900}><DemoScene /></Sequence>
    <Sequence from={1350} durationInFrames={300}><ResultScene /></Sequence>
    <Sequence from={1650} durationInFrames={150}><CTAScene /></Sequence>
  </>
);
```

- Scene별 duration 프레임 단위 명시
- 컴포넌트 책임 분리 (각 Scene = 독립 컴포넌트)
- 데이터 바인딩 필드 null-safe 처리

**Step 3 — 타임라인 구현**
- spring() 또는 interpolate() 텍스트 애니메이션
- 스크린 레코딩 삽입 (있는 경우)
- 배경 음악/나레이션 싱크

**Step 4 — 렌더 & QA**
```bash
# 프리뷰
npx remotion preview src/index.ts

# 최종 렌더
npx remotion render src/index.ts agent-demo output.mp4 \
  --fps=30 --width=1920 --height=1080
```
- 시작/중간/끝 3구간 프레임 캡처 QA
- 오디오-비주얼 싱크 확인

---

### type: infographic

HTML/CSS 애니메이션 → ffmpeg 2-pass 인코딩으로 GIF/MP4를 제작한다.

**Step 1 — 장면 설계**
- 핵심 메시지 1문장 확정
- 키프레임 수 결정 (권장 3~8)
- 텍스트 최소 노출 시간: `(글자 수 ÷ 12) + 1`초
- 루프 여부 결정

**Step 2 — HTML/CSS 구현**

```html
<div class="scene" style="width:1280px; height:720px; background:#1a1a2e; overflow:hidden;">
  <div class="step" style="opacity:0; animation: fadeIn 0.5s forwards; animation-delay:0s;">Step 1</div>
  <div class="step" style="opacity:0; animation: fadeIn 0.5s forwards; animation-delay:2s;">Step 2</div>
</div>
<style>
@keyframes fadeIn { from { opacity:0; transform:translateY(10px); } to { opacity:1; transform:translateY(0); } }
</style>
```

- GPU 가속: transform·opacity 속성 우선
- 모든 리소스 inline 또는 로컬 경로

**Step 3 — 캡처 (우선순위 기반 방법 선택)**

```
Puppeteer ≥19.0?
├── Yes → CDP beginFrame (권장, 결정론 타이밍 ±1프레임)
└── No
    ├── CSS animation-play-state 제어 가능? → paused→play 트리거 방식
    └── No → animationend 이벤트 기반 (최후 수단, 비결정론)
```

Puppeteer CDP beginFrame 예시:
```javascript
const client = await page.target().createCDPSession();
for (let i = 0; i < totalFrames; i++) {
  await client.send('HeadlessExperimental.beginFrame');
  await page.screenshot({ path: `frames/${String(i).padStart(4, '0')}.png` });
}
```

- 예상 프레임 수 vs 실제 캡처 수 확인 (오차 ±1프레임 이내)

**Step 4 — 인코딩**

GIF (2-pass):
```bash
ffmpeg -i frames/%04d.png -vf "fps=12,scale=1280:-1:flags=lanczos,palettegen=stats_mode=diff" palette.png
ffmpeg -i frames/%04d.png -i palette.png -lavfi "fps=12,scale=1280:-1:flags=lanczos[v];[v][1:v]paletteuse=dither=sierra2" output.gif
```

MP4:
```bash
ffmpeg -i frames/%04d.png -c:v libx264 -preset medium -crf 22 -pix_fmt yuv420p -r 30 output.mp4
```

용량 초과 시 단계적 최적화:
1. fps 낮추기 (12→10→8)
2. 해상도 축소 (1280→1024→960)
3. 색상 수 제한 (palettegen `max_colors`)
4. gifsicle lossy 후처리

**Step 5 — QA & 전달**
- GIF ≤8MB, MP4 ≤50MB 확인
- 루프형: 시작/끝 프레임 시각차 5% 이하
- 텍스트 최소 노출 시간 충족
- 출력 파일 경로 + 재실행 명령 전달

---

## Failure Handling

| 실패 상황 | 감지 | 대응 |
|---|---|---|
| --type 미명시 | 파싱 결과 None | 에러 출력 + type 목록 안내, 실행 중단 |
| 스토리라인 불명확 (video) | 핵심 가치 문장 부재 | PRD/OKR 참조 요청, 없으면 3개 후보 제시 |
| Remotion 렌더 실패 | 빌드 에러 | 실패 구간/원인 분리 보고 (에셋 누락/코드 에러/메모리) |
| 타임라인 불일치 (video) | duration ±1프레임 이상 차이 | duration 매핑표 재생성 후 1회 재렌더 |
| GIF 8MB 초과 (infographic) | 인코딩 후 파일 크기 | fps 2단계 낮추기 + 색상 수 조정 후 재인코딩 |
| 프레임 드롭 (infographic) | 캡처 수 vs 예상 수 불일치 | 캡처 방법 한 단계 하향 + 해상도 축소 |

---

## Quality Gate

### video
- [ ] 스토리라인 5단계 (Hook/문제/데모/성과/CTA) 모두 포함
- [ ] 해상도 1920×1080, fps 30
- [ ] Scene별 duration 총합 오차 ±1프레임 이내
- [ ] QA 3구간 (시작/중간/끝) 프레임 캡처
- [ ] 데이터 바인딩 필드 null-safe 처리

### infographic
- [ ] 핵심 메시지 1문장 확정
- [ ] GIF fps 12 / MP4 fps 30
- [ ] GIF ≤8MB
- [ ] 텍스트 최소 노출 `(글자 수 ÷ 12) + 1`초 이상
- [ ] 캡처 프레임 수 오차 ±1프레임 이내
- [ ] 루프형: 시작/끝 시각차 5% 이하

---

## Examples

### Good Example
**입력:** `--type video "고객 문의 자동 분류 에이전트 데모, 투자자용 60초"`

**기대 동작:**
1. 5단계 스토리라인 설계
2. Composition 60초 (1800 frames @ 30fps) 구조 설계
3. Remotion 렌더 + QA 3구간

### Good Example
**입력:** `--type infographic "3-Tier 에이전트 아키텍처 GIF"`

**기대 동작:**
1. 3단계 순차 등장 장면 설계
2. HTML/CSS 구현
3. CDP beginFrame 캡처 → 2-pass GIF 인코딩
4. output.gif 약 3MB, 루프형

### Bad Example
**입력:** `media-asset "에이전트 영상"` (--type 없음)

**기대 동작:**
```
❌ 에러: --type 인자가 필요합니다.
사용 가능한 type: video | infographic
```
실행 중단.

---

## Contextual Knowledge (auto-loaded)

### Remotion Reference
!`cat references/remotion-patterns.md 2>/dev/null || echo ""`

### CDP beginFrame Reference
!`cat references/cdp-capture.md 2>/dev/null || echo ""`

### GIF Optimization
!`cat references/gif-optimization.md 2>/dev/null || echo ""`

### Good Example
!`cat examples/good-01.md 2>/dev/null || echo ""`

### Domain Context
!`cat context/domain.md 2>/dev/null || echo ""`
