# hplan MD→HTML Auto-Renderer 설계

**날짜**: 2026-05-26  
**상태**: 설계 확정 / 구현 대기  
**범위**: `hooks/PostToolUse.sh` 확장 + `hplan/scripts/md_renderer.py` 신규 + `hplan/templates/` 신규 (10개)

---

## 1. 배경 및 목표

### 문제

hplan의 모든 핵심 출력물(Evidence 점수, COGS 판정, PRD, 아키텍처 등)은 `.md` 파일로 생성된다. 마크다운은 작성하기엔 좋지만 **게이트 판정을 빠르게 읽거나 팀에 공유하기엔 부적합**하다.

- Evidence 87/100이 `BUILD`인지 `HOLD`인지 — 스크롤 없이 1초 안에 보여야 한다.
- COGS `GREEN`이 68% 마진인지 — 수치 계산 없이 시각적으로 보여야 한다.
- 컬러 팔레트 `#1E293B` — 색상 블록으로 봐야 쓸 수 있다.

### 목표

hplan 커맨드(`/harness-discover`, `/harness-plan`, `/harness-build`)가 `.md`를 생성하는 순간, **같은 위치에 `.html`이 자동으로 함께 생성**된다. 별도 명령 없이, 어떤 스킬도 수정하지 않고.

---

## 2. 설계 원칙

1. **Claude Code 흐름 비차단** — HTML 생성 실패 시 항상 `exit 0`. MD 생성이 먼저다.
2. **MD 옆에 HTML** — `harness/evidence/report.md` → `harness/evidence/report.html`. 별도 폴더 없음.
3. **게이트 판정이 1초 안에** — 판정(BUILD/GREEN/RED)은 페이지 최상단에 전체 폭 배너로.
4. **설치 시 템플릿 포함** — `hplan/templates/`는 레포에 포함. 사용자는 설치 후 즉시 사용.
5. **스킬 수정 없음** — 기존 8개 스킬 코드 변경 없이 PostToolUse 훅 하나로 처리.

---

## 3. 아키텍처

### 3-1. 파일 구조 변경

```
hplan/
├── hooks/
│   └── PostToolUse.sh          ← [수정] md_renderer.py 호출 블록 추가
├── scripts/
│   └── md_renderer.py          ← [신규] 핵심 변환 엔진
└── templates/                  ← [신규] 디렉토리 전체
    ├── _base.html              ← Tailwind CDN + Chart.js + Mermaid 공통 레이아웃
    ├── generic.html            ← 기본 변환 (구조 자동 감지)
    ├── evidence-gate.html      ← harness/evidence/report.md
    ├── cogs-sentinel.html      ← harness/build-gate/cogs_report.md
    ├── gate-state.html         ← harness/STATE.md
    ├── pain-board.html         ← harness/pain.md
    ├── ost-viewer.html         ← docs/OPPORTUNITY_TREE.md
    ├── market-intel.html       ← harness/competitors.md
    ├── architecture-blueprint.html  ← harness/ARCHITECTURE.md
    ├── sprint-tracker.html     ← harness/PROGRESS.md
    ├── prd-reader.html         ← docs/PRD.md
    └── design-system.html      ← docs/DESIGN.md + .design/RESPECT.md
```

### 3-2. 데이터 흐름

```
/harness-build 실행
    │
    ▼
Write tool: harness/evidence/report.md 생성
    │
    ▼
PostToolUse.sh 발동
    ├─ [기존] secrets scan (변경 없음)
    └─ [신규] md_renderer.py harness/evidence/report.md
                │
                ▼
         경로 패턴 매칭
                │
                ▼
         evidence-gate.html 템플릿 로드
                │
                ▼
         MD 파싱 (패턴별 데이터 추출)
                │
                ▼
         harness/evidence/report.html 저장
                │
                ▼ (성공 or 실패 모두)
            exit 0
```

### 3-3. 경로-템플릿 매핑

```python
TEMPLATE_MAP = [
    (r"harness/evidence/report\.md$",          "evidence-gate"),
    (r"harness/build-gate/cogs_report\.md$",   "cogs-sentinel"),
    (r"harness/STATE\.md$",                    "gate-state"),
    (r"harness/pain\.md$",                     "pain-board"),
    (r"docs/OPPORTUNITY_TREE\.md$",            "ost-viewer"),
    (r"harness/competitors\.md$",              "market-intel"),
    (r"harness/ARCHITECTURE\.md$",             "architecture-blueprint"),
    (r"harness/PROGRESS\.md$",                 "sprint-tracker"),
    (r"docs/PRD\.md$",                         "prd-reader"),
    (r"docs/DESIGN\.md$|\.design/RESPECT\.md$","design-system"),
    # 위 패턴 미해당 + 변환 대상 경로
    (r"(harness|docs|specs)/.*\.md$",          "generic"),
]

# 변환 제외 경로 (절대 변환하지 않음)
EXCLUDE_PATTERNS = [
    r"CLAUDE\.md$",
    r"README\.md$",
    r"PLUGIN\.md$",
    r"SKILL\.md$",
    r"references/.*\.md$",
    r"examples/.*\.md$",
]
```

---

## 4. 10개 템플릿 사양

### 4-1. 공통 사양 (`_base.html`)

각 템플릿은 독립적인 자기완결 HTML 파일이다. `_base.html`은 Python 레벨 상속이 아니라 **스캐폴딩 레퍼런스** — 새 템플릿 작성 시 복사해서 시작하는 기준 파일이다. CDN 링크와 공통 디자인 토큰이 여기 정의되어 있다.

```html
<!-- CDN (인터넷 연결 필요, 오프라인 시 graceful degradation) -->
<script src="https://cdn.tailwindcss.com"></script>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4/dist/chart.umd.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js"></script>
```

공통 디자인 토큰:
- 배경: `bg-[#0f1117]` (다크)
- 카드: `bg-slate-800/60 border border-slate-700/50`
- 판정 GREEN: `bg-emerald-500` / CONDITIONAL_GO: `bg-amber-500` / RED: `bg-red-500`
- 폰트: 시스템 sans-serif

---

### 4-2. 게이트 판정 템플릿 (3개)

#### ① `evidence-gate` — `harness/evidence/report.md`

**파싱 대상**:
- `score: N` 또는 `총점: N/100` → 총점
- `decision: build|hold|interview` → 판정
- `## [축 이름]\n점수: N` 패턴 → 8축 점수
- 점수 낮은 축 자동 추출 → 취약 축

**레이아웃**:
```
[BUILD 배지 — 전체 폭 초록 배너]          (점수 < 55이면 빨간 HOLD)

[총점 게이지]          [8축 레이더 차트 — Chart.js radar]
 87 / 100
 ████████████░░░

[취약 축 경고 카드]
⚠ Acquisition: 3/10 — 다음 인터뷰에서 보완 필요
```

---

#### ② `cogs-sentinel` — `harness/build-gate/cogs_report.md`

**파싱 대상**:
- `verdict: GREEN|CONDITIONAL_GO|RED` → 판정
- `p50_margin: N%`, `p90_margin: N%` → 마진
- `gross_margin: N%` → 전체 마진
- `break_even_users: N` → 손익분기
- 시나리오 테이블 (`free:paid` 비율별 마진) → 막대 차트

**레이아웃**:
```
[GREEN / CONDITIONAL_GO / RED — 전체 폭 배너]

[p50 도넛]  [p90 도넛]  [gross margin 숫자 카드]  [break-even 카드]

[시나리오별 마진 가로 막대 차트]
free:paid 0:1  ████████████ 72%
free:paid 4:1  ██████████   61%
free:paid 24:1 ██████░░░░   38%
```

---

#### ③ `gate-state` — `harness/STATE.md`

**파싱 대상**:
- `gate: build|evidence|...` → 게이트 단계
- `verdict: GO|CONDITIONAL_GO|HOLD` → 판정
- `| [조건] | [verified_by] | ✅/❌ |` 테이블 행 → 조건 목록
- `## 블로커` 섹션 → 블로커 목록

**레이아웃**:
```
[CONDITIONAL_GO 배너]    gate: build    2026-05-24

[조건 체크보드]                    [진행률 카드]
✅ API 연동 검증                    1 / 3 완료
   tests/test_api.py               ████░░░░░░
❌ DB 마이그레이션 [미검증]
❌ Auth E2E [미검증]

[블로커 카드 — 빨간 테두리]
외부 API 키 미발급
```

---

### 4-3. 증거·탐색 템플릿 (4개)

#### ④ `pain-board` — `harness/pain.md`

**파싱 대상**:
- `[Time-sink]`, `[Cost-heavy]`, `[Error-prone]`, `[Scale-blocker]` 태그
- 인터뷰 구분자(`---`, `## Interview N`) → 인터뷰 수
- `"..."` 따옴표 인용 → Pain 카드 본문
- Signal Gate 5건 달성 여부

**레이아웃**:
```
[인터뷰 3건 — Signal Gate 5건 미달 ⚠]   [태그별 빈도 바 차트]

Time-sink        Cost-heavy       Error-prone      Scale-blocker
┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐
│"3시간씩    │  │"월 50만원  │  │            │  │            │
│ 수작업"    │  │ 날림"      │  │            │  │            │
└────────────┘  └────────────┘  └────────────┘  └────────────┘
```

---

#### ⑤ `ost-viewer` — `docs/OPPORTUNITY_TREE.md`

**파싱 대상**:
- Mermaid 코드 블록 전체 → 그대로 렌더링
- `## Solution` 섹션 → 솔루션 카드
- `status: pending|running|done` → 실험 배지

**레이아웃**:
```
[Mermaid flowchart — 전체 폭]

[솔루션 카드 그리드]
[Solution A]      [Solution B]      [Solution C]
[pending ○]       [running ◌]       [done ✓]
```

---

#### ⑥ `market-intel` — `harness/competitors.md`

**파싱 대상**:
- `|` 마크다운 테이블 → 비교 테이블
- `## [경쟁사명]` 섹션 → 버블 차트 데이터 포인트
- `price:`, `feature_depth:` 키워드 → 포지셔닝 축

**레이아웃**:
```
[경쟁사 비교 테이블 — sticky 헤더]
│ 제품 │ 가격 │ 핵심 기능 │ 취약점 │ 우리 우위 │

[포지셔닝 버블 차트 — 가격 × 기능깊이]
(우리 제품 강조 색상)
```

---

#### ⑦ `architecture-blueprint` — `harness/ARCHITECTURE.md`

**파싱 대상**:
- Mermaid 코드 블록 → 3-Tier 다이어그램
- `## Routing` 섹션의 테이블 → 모델 라우팅 표
- `## Memory` 섹션 → 메모리 아키텍처 카드
- `decision_log hitl` 항목 → 결정 타임라인

**레이아웃**:
```
[Mermaid 3-Tier 다이어그램 — 전체 폭]

[모델 라우팅 테이블]          [메모리 아키텍처 카드]
│ 태스크 │ 모델 │ 이유 │      단기: Redis TTL 1h
│ plan   │ opus │ ...  │      장기: Vector Store
```

---

### 4-4. 추적 템플릿 (2개)

#### ⑧ `sprint-tracker` — `harness/PROGRESS.md`

**파싱 대상**:
- `## W1`, `## W2`, ... → 마일스톤 목록
- `- [x]` / `- [ ]` → 완료/미완료 체크박스
- `COGS.*p[59]0.*%` → COGS 천장 수치
- "블로커" 키워드 → 블로커 카드

**레이아웃**:
```
[Wx 전체 도넛: 1/3 완료]    [COGS 천장 카드: p90 28% < 40% ✅]

W1 ████████░░ 4/5    W2 ░░░░░░░░░░ 0/4    W3 ─
[완료]                [미시작]             [미시작]

[블로커 카드]
❌ DB 마이그레이션 — 외부 의존성
```

---

#### ⑨ `prd-reader` — `docs/PRD.md`

**파싱 대상**:
- `## ` H2 헤더 → 사이드 네비 항목
- `evidence_score: N` 주석 → Evidence 배지
- `cogs_verdict: GREEN|...` 주석 → COGS 배지
- Mermaid 코드 블록 → 인라인 렌더링

**레이아웃**:
```
┌──────────┬──────────────────────────────────────┐
│ 목차     │  [게이트 배지 행]                     │
│ 1. 개요  │  Evidence 87pt BUILD ✅               │
│ 2. ICP   │  COGS GREEN ✅   STATE 1/3 ❌          │
│ ...      │                                      │
│ 8. 성공  │  [섹션 본문]                          │
└──────────┴──────────────────────────────────────┘
```

---

### 4-5. 디자인 시스템 템플릿 (1개)

#### ⑩ `design-system` — `docs/DESIGN.md` + `.design/RESPECT.md`

두 파일 중 존재하는 것을 렌더링. 둘 다 있으면 탭으로 분리.

**파싱 대상**:
- `#[0-9A-Fa-f]{3,6}` → 실제 색상 블록 렌더링
- `rgb(...)`, `hsl(...)` → 색상 블록
- `## Typography` 섹션의 크기/굵기 → 실제 폰트로 렌더링
- `` `bg-*`, `text-*`, `border-*` `` Tailwind 클래스 → Tailwind CDN으로 실시간 렌더링
- HTML 코드 블록 → 인라인 미리보기
- RESPECT.md의 `three_second_rule:`, `next_action:`, `hierarchy_rules:` → UX 원칙 카드

**레이아웃**:
```
[DESIGN.md 탭] [RESPECT.md 탭]

Color Palette
███ #1E293B slate-900   ███ #6366F1 indigo-500   ███ #F8FAFC slate-50

Typography Scale
이 크기로 실제 렌더링됩니다 — H1  36px/700
이 크기로 실제 렌더링됩니다 — H2  28px/600
이 크기로 실제 렌더링됩니다 — Body 16px/400

Tailwind Tokens              Component Preview
[bg-slate-900  ]             ┌──────────────────┐
[text-indigo-400]            │  [실제 컴포넌트]  │
[rounded-xl    ]             └──────────────────┘
(클래스명 + 렌더링 박스)
```

---

## 5. md_renderer.py 구조

```python
#!/usr/bin/env python3
"""
hplan MD → HTML 자동 렌더러
PostToolUse.sh에서 호출됨. 실패 시 조용히 종료 (exit 0).
"""

import sys, re, json
from pathlib import Path

TEMPLATE_DIR = Path(__file__).parent.parent / "templates"
EXCLUDE_PATTERNS = [...]  # 섹션 3-3 참조
TEMPLATE_MAP = [...]      # 섹션 3-3 참조

def select_template(file_path: str) -> str:
    """경로 패턴 매칭으로 템플릿 이름 반환. 매칭 없으면 None."""
    ...

def parse_md(content: str, template_name: str) -> dict:
    """템플릿별 파서. 구조화된 데이터 dict 반환."""
    parsers = {
        "evidence-gate": parse_evidence_gate,
        "cogs-sentinel": parse_cogs_sentinel,
        "gate-state":    parse_gate_state,
        # ...
    }
    return parsers.get(template_name, parse_generic)(content)

def render(template_name: str, data: dict) -> str:
    """템플릿 HTML에 data 주입. Jinja2 사용 안 함 (의존성 최소화)."""
    template_path = TEMPLATE_DIR / f"{template_name}.html"
    html = template_path.read_text()
    # __DATA_JSON__ placeholder를 JSON으로 치환
    # 실제 렌더링은 브라우저 JavaScript가 담당
    return html.replace("__DATA_JSON__", json.dumps(data, ensure_ascii=False))

def main():
    if len(sys.argv) < 2:
        sys.exit(0)
    
    file_path = sys.argv[1]
    
    # 제외 경로 체크
    for pattern in EXCLUDE_PATTERNS:
        if re.search(pattern, file_path):
            sys.exit(0)
    
    template_name = select_template(file_path)
    if not template_name:
        sys.exit(0)
    
    try:
        md_content = Path(file_path).read_text(encoding="utf-8")
        data = parse_md(md_content, template_name)
        html = render(template_name, data)
        
        output_path = Path(file_path).with_suffix(".html")
        output_path.write_text(html, encoding="utf-8")
    except Exception:
        pass  # 실패 시 조용히 종료
    
    sys.exit(0)

if __name__ == "__main__":
    main()
```

**핵심 설계 결정: 브라우저 렌더링 방식**

템플릿은 `__DATA_JSON__` 플레이스홀더를 포함한 HTML 파일이다. Python이 MD를 파싱해 JSON을 만들고, 브라우저 JavaScript가 Chart.js/Mermaid를 초기화한다. Jinja2 등 추가 의존성 없음.

```html
<!-- templates/evidence-gate.html 구조 -->
<script>
  const DATA = __DATA_JSON__;  // Python이 치환
  // Chart.js, Mermaid 초기화는 브라우저에서
  renderRadarChart(DATA.axes);
  renderVerdict(DATA.verdict, DATA.score);
</script>
```

---

## 6. PostToolUse.sh 수정 사양

기존 secrets scan 블록 뒤에 추가. 경로 탐색은 기존 PreToolUse.sh의 `SCRIPT_DIR` 패턴과 동일하게:

```bash
# ── MD → HTML 자동 렌더링 ──────────────────────────────
if [[ "$FILE_PATH" =~ \.md$ ]]; then
  SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  RENDERER="$SCRIPT_DIR/../hplan/scripts/md_renderer.py"
  if [ -f "$RENDERER" ]; then
    python3 "$RENDERER" "$FILE_PATH" 2>/dev/null || true
  fi
fi
# ──────────────────────────────────────────────────────
```

- `SCRIPT_DIR` 패턴 → PreToolUse.sh와 동일한 경로 탐색 방식. 심링크 안전
- `2>/dev/null || true` → 렌더러 오류가 절대 훅 출력에 노출되지 않음
- `[ -f "$RENDERER" ]` 가드 → hplan 미설치 환경에서 안전하게 skip

---

## 7. 오류 처리

| 상황 | 동작 |
|------|------|
| CDN 오프라인 | 빈 차트 (Chart.js 없음), 텍스트만 표시. Mermaid 코드 블록은 `<pre>`로 폴백 |
| MD 파싱 실패 | `generic` 템플릿으로 폴백 |
| 템플릿 파일 없음 | HTML 생성 skip, 조용히 exit 0 |
| HTML 쓰기 권한 없음 | 조용히 exit 0 |
| Python 3 미설치 | `[ -f "$RENDERER" ]` 가드가 skip |

---

## 8. 구현 순서 (Phase 분리)

### Phase 1 — 엔진 (선행 필수)
1. `hplan/templates/_base.html` 작성
2. `hplan/scripts/md_renderer.py` 작성 (경로 매핑 + generic 렌더러)
3. `hooks/PostToolUse.sh` 수정
4. generic 템플릿으로 전체 파이프라인 동작 검증

### Phase 2 — 게이트 판정 템플릿 (우선순위 최상)
5. `evidence-gate.html` + 파서
6. `cogs-sentinel.html` + 파서
7. `gate-state.html` + 파서

### Phase 3 — 증거·탐색 템플릿
8. `pain-board.html` + 파서
9. `ost-viewer.html` + 파서
10. `market-intel.html` + 파서
11. `architecture-blueprint.html` + 파서

### Phase 4 — 추적 + 디자인 템플릿
12. `sprint-tracker.html` + 파서
13. `prd-reader.html` + 파서
14. `design-system.html` + 파서

---

## 9. 제외 범위 (이 설계에 포함되지 않음)

- **오프라인 CDN 번들링** — CDN 의존성은 현재 허용. 오프라인 지원은 별도 이슈.
- **HTML → PDF 변환** — 브라우저 인쇄로 대체.
- **기존 스킬 SKILL.md 수정** — 어떤 스킬도 수정하지 않는다는 원칙 유지.
- **decisions.jsonl HTML 변환** — JSONL 포맷은 별도 결정 필요.
- **실시간 갱신** — PostToolUse 단발 생성. WebSocket/HMR 없음.
