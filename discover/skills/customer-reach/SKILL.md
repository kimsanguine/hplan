---
name: customer-reach
description: "인터뷰 대상자 확보 + 컨택 초안 생성. --mode plan(확보 전략), --mode linkedin(LinkedIn cold DM 초안), --mode community(커뮤니티 포스팅 초안), --mode survey(설문 초안). harness/pain.md를 채우기 위한 선행 단계. Use when a PM needs to find and contact interview candidates before evidence-gate."
argument-hint: "[--mode plan|linkedin|community|survey] [target ICP description]"
allowed-tools: ["Read", "Write"]
model: sonnet
---

## Core Goal

"고객 발화 3건"을 pain.md에 채우기 위한 인터뷰 대상자 확보 도구.
발견(plan/search) → 초안 생성(linkedin/community/survey) → 기록(pain.md) 순서로 사용.

## Trigger Gate

### Use This Skill When
- "인터뷰할 사람 어떻게 찾아요?" → plan
- "LinkedIn에서 DM 보내고 싶어요" → linkedin
- "커뮤니티에 포스팅하려고요" → community
- "설문지 만들어줘요" → survey
- evidence-gate WARN → "실제 인터뷰 증거를 얻기 전에 이 스킬부터 시작하세요"

### Route to Other Skills When
- 인터뷰 결과를 기록할 때 → harness/pain.md 직접 작성 (커맨드 없음)
- 기록 후 검증 → evidence-rubric / evidence-gate
- 소크라테스 가정 심문 (인터뷰 전) → socratic-question

## Instructions

### mode: plan
1. $ARGUMENTS의 ICP 설명을 읽어 타겟 확보 전략을 설계한다 (LLM)
2. 3가지 채널 추천: LinkedIn / 커뮤니티(오픈채팅, Reddit, Discord) / 지인 네트워크
3. 각 채널별 예상 성공률과 소요 시간 추정 (결정론: 고정 기준표 기반)
4. harness/reach-plan.md에 저장

### mode: linkedin
ICP에 맞는 LinkedIn cold DM 초안 생성:
```
안녕하세요 [이름]님,

저는 [내 소개 1줄]입니다.
[ICP의 특정 역할/상황]에서 [핵심 고충]을 어떻게 해결하시는지 15분 여쭤봐도 될까요?

보상 없이도 가능하지만, 원하신다면 [가치 교환 1줄]도 가능합니다.
```
ICP 분야에 따라 문구를 조정한다. 스팸 느낌 패턴 (긴급/할인/과장) 제거.

### mode: community
커뮤니티 포스팅 초안:
- 제목: "[ICP 역할] 분들께 15분 인터뷰 요청드립니다"
- 내용: 무엇을 만드는지 1줄, 누구에게 물어보고 싶은지, 왜 당신의 의견이 중요한지
- 플랫폼별 톤 조정: Reddit(영문/격식X) vs 카카오오픈채팅(한국어/친근함)

### mode: survey
인터뷰 대체용 5문 이하 설문 초안:
- Q1: 현재 [문제 영역]을 어떻게 해결하시나요? (객관식 4개)
- Q2: 가장 번거로운 점은? (서술 or 객관식)
- Q3: 기존 해결책에 얼마나 만족하시나요? (1-5)
- Q4: 새로운 도구가 생긴다면 가장 원하는 기능 1가지는?
- Q5: 인터뷰 참여 의향 (예/아니오 + 연락처 선택)

## Quality Gate
- [ ] DM/포스팅 초안에 과장/압박 문구 없음
- [ ] 설문 5문 이하 (인지 부하 최소화)
- [ ] 확인 게이트: 초안 보여주고 수정 기회 제공 후 저장
