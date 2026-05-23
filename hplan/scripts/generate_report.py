#!/usr/bin/env python3
import argparse
import json
import re
from pathlib import Path


DECISIONS = {
    "build": ("지금 만들기", "인터뷰 근거와 대체재 압력이 충분합니다. 좁은 MVP로 바로 검증하세요."),
    "interview": ("인터뷰 먼저", "아이디어는 살아있지만 아직 사용자의 행동 증거가 부족합니다."),
    "pivot": ("피벗", "솔루션보다 문제 문장이 약합니다. 더 비싼 문제로 각도를 바꾸세요."),
    "hold": ("보류", "지금은 빌딩보다 관찰과 대체재 조사가 먼저입니다."),
}


def split_terms(value):
    terms = []
    for chunk in value.replace("/", ",").replace("\n", ",").split(","):
        chunk = chunk.strip()
        if chunk:
            terms.append(chunk)
    return terms


def first_sentence(value, fallback):
    for delimiter in [".", "!", "?", "\n", "。"]:
        value = value.replace(delimiter, "\n")
    for line in value.splitlines():
        line = line.strip()
        if line:
            return line
    return fallback


def completeness(data):
    fields = ["idea", "target", "hypothesis", "alternatives", "features"]
    values = [str(data.get(field, "")) for field in fields]
    filled = sum(1 for value in values if len(value.strip()) > 12)
    depth = sum(min(len(value.strip()), 180) for value in values) / 900
    return round(((filled / len(fields)) * 0.65 + depth * 0.35) * 100)


def score_diagnosis(data, interview_notes):
    combined = "\n".join(
        str(data.get(field, ""))
        for field in ["idea", "target", "hypothesis", "alternatives", "features"]
    ) + "\n" + interview_notes
    alternatives = split_terms(str(data.get("alternatives", "")))
    features = split_terms(str(data.get("features", "")))
    interview_lines = [line.strip() for line in interview_notes.splitlines() if len(line.strip()) > 8]

    def depth(value, max_score, good_length):
        return max(0, min(max_score, round((len(value.strip()) / good_length) * max_score)))

    checks = [
        (
            "ICP specificity",
            depth(str(data.get("target", "")), 20, 90),
            20,
            "행동·맥락이 비교적 구체적입니다." if len(str(data.get("target", "")).strip()) > 70 else "타깃이 아직 넓습니다.",
        ),
        (
            "Recent painful event",
            15 if re.search(r"최근|오늘|어제|지난|이번|last|today|yesterday|week|month|\d+\s?(일|시간|건|명|회)", combined, re.I) else 10 if len(interview_lines) >= 2 else 4,
            15,
            "최근 사건 또는 구체 수량이 보입니다." if len(interview_lines) >= 2 else "최근 30일 안의 사건이 더 필요합니다.",
        ),
        (
            "Current alternative/workaround",
            15 if len(alternatives) >= 3 else 10 if alternatives else 0,
            15,
            "현재 대체재가 충분히 명명되었습니다." if len(alternatives) >= 3 else "사용자가 지금 무엇으로 버티는지 더 적어야 합니다.",
        ),
        (
            "Repetition/frequency",
            10 if re.search(r"매일|매주|매월|반복|자주|계속|항상|daily|weekly|monthly|repeated", combined, re.I) else 7 if len(interview_lines) >= 3 else 3,
            10,
            "반복 빈도 신호가 있습니다." if len(interview_lines) >= 3 else "문제가 얼마나 자주 반복되는지 약합니다.",
        ),
        (
            "Economic pain",
            15 if re.search(r"돈|매출|비용|결제|구매|리스크|기회|전환|이탈|revenue|cost|pay|paid|payment|risk", combined, re.I) else 5,
            15,
            "돈/기회/리스크 손실 신호가 있습니다." if re.search(r"돈|매출|비용|결제|구매|리스크|기회|전환|이탈|revenue|cost|pay|paid|payment|risk", combined, re.I) else "시간 외에 돈/기회 손실이 더 필요합니다.",
        ),
        (
            "Switching trigger",
            10 if re.search(r"버리|전환|대체|갈아타|불편|짜증|느리|비싸|switch|replace|too slow|expensive", combined, re.I) else 5 if alternatives else 0,
            10,
            "대체재를 버릴 이유가 보입니다." if alternatives else "기존 대체재를 버릴 최소 조건이 약합니다.",
        ),
        (
            "MVP narrowness",
            10 if 0 < len(features) <= 3 else 7 if len(features) <= 5 else 3,
            10,
            "MVP 범위가 좁습니다." if 0 < len(features) <= 3 else "기능을 한 가지 워크플로우로 더 줄이세요.",
        ),
        (
            "Acquisition path to first 5 users",
            5 if re.search(r"첫\s?5|첫\s?10|사용자|인터뷰|dm|링크드인|커뮤니티|디스코드|레딧|고객|user|interview|linkedin|community", combined, re.I) else 1,
            5,
            "첫 사용자를 찾을 힌트가 있습니다." if re.search(r"첫\s?5|첫\s?10|사용자|인터뷰|dm|링크드인|커뮤니티|디스코드|레딧|고객|user|interview|linkedin|community", combined, re.I) else "첫 5명을 어디서 찾을지 필요합니다.",
        ),
    ]
    total = sum(score for _, score, _, _ in checks)
    economic = re.search(r"돈|매출|비용|결제|구매|리스크|기회|전환|이탈|revenue|cost|pay|paid|payment|risk", combined, re.I)
    if total >= 75 and economic:
        decision = "build"
    elif total >= 55:
        decision = "interview"
    elif total >= 35:
        decision = "pivot"
    else:
        decision = "hold"
    missing = [label for label, score, max_score, _ in checks if score / max_score < 0.55]
    breakdown = [{"label": label, "score": score, "max": max_score, "reason": reason} for label, score, max_score, reason in checks]
    return {"score": total, "decision": decision, "missing": missing, "breakdown": breakdown}


def generate(data):
    idea = first_sentence(str(data.get("idea", "")), "새로운 SaaS 아이디어")
    target = first_sentence(str(data.get("target", "")), "1인 빌더 또는 작은 팀")
    hypothesis = first_sentence(str(data.get("hypothesis", "")), "반복 업무가 너무 많아 더 나은 방법을 찾고 있다")
    alternatives = split_terms(str(data.get("alternatives", "")))
    features = split_terms(str(data.get("features", "")))
    interview_notes = str(data.get("interview_notes", ""))
    interview_signals = [line.strip() for line in interview_notes.splitlines() if len(line.strip()) > 8]

    has_alternatives = len(alternatives) > 0
    has_interview = len(interview_signals) >= 2
    scoring = score_diagnosis(data, interview_notes)
    decision = scoring["decision"]
    score = scoring["score"]
    label, reason = DECISIONS[decision]

    return {
        "input": data,
        "decision": decision,
        "decision_label": label,
        "decision_reason": reason,
        "score": score,
        "score_breakdown": scoring["breakdown"],
        "missing_evidence": scoring["missing"],
        "pm_lens": [
            f'Hplan Operator Lens: 이 아이디어는 "빨리 만드는 법"이 아니라 {target}의 반복적이고 비싼 문제를 줄이는가?',
            f"증거 우선순위: 칭찬 < 미래 의향 < 기능 요청 < 최근 사건 < 현재 대체재 < 돈/시간 손실. 현재 가장 강한 증거는 {'인터뷰 노트' if has_interview else '대체재' if has_alternatives else '아직 약한 창업자 직감'}이다.",
            "카운터 포지션: 기능을 먼저 늘리기보다 ICP, JTBD, 첫 5명의 강한 증거, 반복 사용 메트릭을 먼저 좁힌다.",
        ],
        "problem_brief": [
            f"사용자: {target}. 현재 상황: {hypothesis}. 이 맥락에서 {idea} 같은 해결책을 찾고 있다.",
            f"현재 대체재는 {', '.join(alternatives) if alternatives else '아직 명확히 적히지 않았다'}이며, Harness Planning 기준으로는 대체재가 없는 시장보다 대체재가 불편한 시장을 우선 검증한다.",
            f"첫 MVP는 {features[0] if features else '가장 반복되는 한 가지 워크플로우'}만 남기고, 나머지는 인터뷰에서 돈/시간 손실이 확인된 뒤 붙인다.",
        ],
        "icp": [
            f"{target} 중 최근 30일 안에 같은 문제를 3번 이상 겪은 사람",
            "이미 수작업, 외주, 노코드, 사내 템플릿 중 하나로 임시 해결 중인 사람",
            "문제를 설명할 때 기능명이 아니라 시간 손실, 매출 손실, 평판 리스크를 말하는 사람",
        ],
        "jtbd": [
            f'When {target}에게 "{hypothesis}" 상황이 생길 때, I want {features[0] if features else "반복 업무를 줄이는 방법"} so I can 다음 행동을 확신 있게 결정한다.',
            f'When 기존 대체재 "{alternatives[0] if alternatives else "수작업"}"이 느리거나 불안할 때, I want 더 작은 자동화 so I can 빌딩 전에 시장 반응을 확인한다.',
            "When 혼자 제품을 만들기 시작할 때, I want 누가 왜 살지 먼저 정리 so I can 기능 과잉을 피한다.",
        ],
        "agent_spec": [
            f'Agent job: {target}가 "{hypothesis}" 상황을 입력하면, 5개 이하의 질문으로 맥락을 수집하고 {features[0] if features else "핵심 결과물"} 초안을 생성한다.',
            "Success metric: 첫 가치 도달 시간(TTV)을 줄이고, 사용자가 결과물을 다시 쓰는 Override Rate를 낮춘다.",
            "Guardrail: 사용자의 기능 wishlist를 그대로 PRD로 바꾸지 말고, 대체재·Push·Anxiety·Habit을 먼저 태깅한다.",
        ],
        "metric_stack": [
            "1층 Sean Ellis: 없으면 매우 실망할 사용자가 40% 이상인지 확인한다.",
            "2층 TTV: 첫 Problem Brief 또는 핵심 결과물을 몇 분 안에 받는지 본다.",
            "3층 Override Rate: AI 산출물을 사용자가 얼마나 고쳐야 하는지 측정한다.",
            "4층 Frustration Index: 막힘, 재시도, 포기, 불신 표현을 태깅한다.",
            "5층 Agentic PMF: 반복 사용과 다음 작업 위임이 생기는지 본다.",
        ],
        "human_checkpoint": [
            f"Decision needed: {label} 판정을 받아들일지, 인터뷰를 더 할지, ICP/JTBD를 바꿀지 결정한다.",
            f"Recommended decision: {decision}.",
            "Evidence to review: 최근 사건, 현재 대체재, 돈/시간 손실, 전환 조건, 실제 commitment.",
            "If approval is missing: WAITING_FOR_HUMAN 상태로 멈추고 다음 gate 산출물은 초안으로만 둔다.",
        ],
    }


def markdown(report):
    data = report["input"]
    sections = [
        "# Harness Planning 진단 리포트",
        "",
        "## 입력",
        f"- 아이디어: {data.get('idea', '-') or '-'}",
        f"- 타깃: {data.get('target', '-') or '-'}",
        f"- 현재 가설: {data.get('hypothesis', '-') or '-'}",
        f"- 경쟁/대체재: {data.get('alternatives', '-') or '-'}",
        f"- 만들고 싶은 기능: {data.get('features', '-') or '-'}",
        "",
        "## Build Decision",
        f"{report['decision_label']} ({report['score']}/100)"
        + (f" — Evidence Source 누락 페널티: -{report['evidence_source_penalty']}pt" if report.get("evidence_source_penalty") else ""),
        "",
        report["decision_reason"],
        "",
        "## 100점 루브릭",
        *[
            f"- {item['label']}: {item['score']}/{item['max']} — {item['reason']}"
            for item in report["score_breakdown"]
        ],
        "",
        "## 부족한 증거",
        *([f"- {item}" for item in report["missing_evidence"]] or ["- 현재 루브릭 기준의 큰 결손은 없습니다."]),
        "",
        "## Hplan Operator Lens",
        *[f"- {item}" for item in report["pm_lens"]],
        "",
        "## Problem Brief",
        *[f"- {item}" for item in report["problem_brief"]],
        "",
        "## ICP",
        *[f"- {item}" for item in report["icp"]],
        "",
        "## JTBD",
        *[f"- {item}" for item in report["jtbd"]],
        "",
        "## JTBD → Agent Spec",
        *[f"- {item}" for item in report["agent_spec"]],
        "",
        "## 5층 메트릭",
        *[f"- {item}" for item in report["metric_stack"]],
        "",
        "## Human Checkpoint",
        *[f"- {item}" for item in report["human_checkpoint"]],
        "",
        "## Interview Kit",
        "- 최근에 이 문제를 마지막으로 겪은 때를 시간순으로 말해주세요.",
        "- 그때 실제로 어떤 도구, 사람, 문서, 결제로 해결하려고 했나요?",
        "- 그 해결책에서 가장 짜증났던 장면은 무엇이었나요?",
        "- 이 문제가 해결되지 않아 잃은 시간, 돈, 기회 중 가장 큰 것은 무엇인가요?",
        "- 제가 만든다고 하면 어떤 기능이 아니라 어떤 결과가 나오면 돈을 낼 수 있나요?",
        "- 지금 쓰는 대체재를 버리려면 무엇이 최소 조건인가요?",
        "",
        "## 7일 검증 로드맵",
        "- Day 1: 아이디어를 한 문장 문제 가설로 해부.",
        "- Day 2: 대체재 3개와 커뮤니티/리뷰 불만 30개 수집.",
        "- Day 3: 칭찬 말고 증거를 뽑는 인터뷰 질문지와 첫 10명 리스트 작성.",
        "- Day 4: 인터뷰 3건 진행. 최근 사건과 현재 대체재를 캡처.",
        "- Day 5: 발화를 weak/strong evidence로 태깅하고 Problem Brief 재작성.",
        "- Day 6: 수동 해결 제안 DM 20개 또는 가격/commitment CTA 테스트.",
        "- Day 7: Build/Pivot 판정표로 다음 행동 결정.",
        "",
        "## 14일 검증 로드맵",
        "- Week 2-1: 인터뷰 5건 추가. 이미 돈을 쓰는 사용자 비율 확인.",
        "- Week 2-2: 기능 1개짜리 데모 또는 수동 concierge MVP로 결과 전달.",
        "- Week 2-3: 낮은 마찰의 유료 commitment, preorder, 또는 예약 결제 의향 테스트.",
        "- Week 2-4: AI agent용 PRD와 AGENTS.md 초안으로 빌딩 범위 고정.",
        "",
        "## 30-60일 Stage Gate",
        "- W1: ICP 카드 + JTBD Statement 작성. 페르소나는 행동·압박·대체재로만 정의.",
        "- W2: Mom Test/Switch Interview 5건. 5건 중 3건이 같은 Push를 말하는지 확인.",
        "- W3: OST v0.1 작성. Opportunity와 Solution을 섞지 않기.",
        "- W4: 베타 사용자에게 Sean Ellis 질문과 TTV 측정.",
        "- W5-W6: 매우 실망 세그먼트만 좁혀 추가 인터뷰 5건.",
        "- W7-W8: 첫 5명 paying, 반복 사용, 또는 must-have 신호가 약하면 ICP/JTBD 재설정.",
        "",
    ]
    return "\n".join(sections)


_EVIDENCE_SOURCE_PATTERNS = {
    "harness/pain.md":        [r'(?i)##\s*evidence\s*source', r'(?i)출처\s*[:：]', r'(?i)Source\s*[:：]'],
    "harness/cogs.md":        [r'(?i)##\s*price\s*reference', r'(?i)가격\s*출처', r'(?i)Source\s*[:：]'],
    "harness/market.md":      [r'(?i)##\s*market\s*data\s*source', r'(?i)데이터\s*출처', r'(?i)Source\s*[:：]'],
    "harness/competitors.md": [r'(?i)##\s*evidence\s*source', r'(?i)관찰\s*출처', r'(?i)Source\s*[:：]'],
}


def evidence_source_penalty(root: Path) -> int:
    """Signal Gate 문서에 Evidence Source 섹션이 없으면 문서당 -5점."""
    penalty = 0
    for doc, patterns in _EVIDENCE_SOURCE_PATTERNS.items():
        path = root / doc
        if not path.exists():
            continue
        content = path.read_text(encoding="utf-8")
        if not any(re.search(p, content) for p in patterns):
            penalty += 5
    return penalty


def main():
    parser = argparse.ArgumentParser(description="Generate a Harness Planning markdown diagnosis from JSON.")
    parser.add_argument("input", help="Path to JSON input")
    parser.add_argument("--json", action="store_true", help="Print JSON instead of markdown")
    args = parser.parse_args()

    data = json.loads(Path(args.input).read_text(encoding="utf-8"))
    report = generate(data)
    root = Path(args.input).parent
    penalty = evidence_source_penalty(root)
    if penalty > 0:
        report["score"] = max(0, report["score"] - penalty)
        report["evidence_source_penalty"] = penalty
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(markdown(report))


if __name__ == "__main__":
    main()
