# profiles/velocity/ — sprint plan velocity baseline

`baseline.jsonl` 은 `deliver/sprint --step plan` 이 complexity 1-5 태스크의 loc/tokens/minutes 예측에 사용하는 기준 데이터다.

## 파일 형식

각 줄은 하나의 complexity 레벨을 나타내는 JSON 객체:

```jsonl
{"complexity": 3, "label": "medium", "loc_p50": 95, "loc_p90": 240, "tokens_p50": 9100, "tokens_p90": 18500, "minutes_p50": 17, "minutes_p90": 38, "sample_n": 0, "confidence": "seed"}
```

| 필드 | 의미 |
|---|---|
| `complexity` | 1-5 정수 (sprint plan의 WBS 분류 기준) |
| `label` | 사람이 읽는 이름 (trivial/small/medium/large/xlarge) |
| `loc_p50` / `loc_p90` | 변경 라인 수 중간값/90백분위 |
| `tokens_p50` / `tokens_p90` | LLM 토큰 소비 중간값/90백분위 |
| `minutes_p50` / `minutes_p90` | 실측 경과 분 중간값/90백분위 |
| `sample_n` | 실측 샘플 수. 0 = seed 값 (측정 전) |
| `confidence` | `seed` (초기값) → `low` (n<10) → `medium` (n<30) → `high` (n≥30) |

## 캘리브레이션 방법

1. `sprint --step init` 으로 `.track/actual_log.jsonl` 추적 시작
2. 스프린트 완료 후 `.track/actual_log.jsonl` 에 실측값(loc_delta, tokens_used, minutes_elapsed) 누적
3. 10개 이상 샘플이 쌓이면 `baseline.jsonl` 수치를 실측 중앙값/90백분위로 갱신
4. `sample_n` 과 `confidence` 를 함께 업데이트

## 초기 seed 값 출처

`sample_n: 0` 인 현재 값은 sprint SKILL.md 의 내부 예시 수치를 그대로 옮긴 시드다.
실측 데이터가 쌓이면 반드시 갱신하여 conservative fallback 의존도를 낮출 것.

> **주의**: `profiles/<your-name>/` 아래에 개인 인스턴스를 만들고 gitignore 하는 것을 권장한다.
> 이 파일은 공개 시드이므로 개인 실측 데이터를 직접 커밋하지 말 것.
