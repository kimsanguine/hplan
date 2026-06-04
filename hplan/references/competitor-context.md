# competitor-context.md
# 경쟁 맥락 — hplan Build Gate 선행 입력
# 목적: "이 시장에 진입해야 하는가"를 판단하는 5-Block 구조
# 저장 위치: harness/competitor-context.md (프로젝트별 작성)
# 소요 시간: 15–20분
#
# 설계 원칙:
#   1. competitive intelligence 수집이 아니라 GO/HOLD 신호 추출이 목적
#   2. 각 필드는 "이 필드가 HOLD 조건을 만족하는가"를 묻는 구조
#   3. 완성된 moat 분석이 아니라 "18개월 안에 방어 가능한 포지션이 있는가" 판단
#
# 이 파일이 있으면 /hplan이 자동으로 읽어 Step 1(exclusions check) 직후 반영합니다.
# architect/strategy --focus moat skill은 내 제품의 해자 설계용 (이 파일과 역할이 다릅니다).

idea: ""    # context-intake.md의 idea 필드와 동일하게 작성

---

## BLOCK A — 시장 존재 확인
# 목적: "이미 누가 이 문제를 풀고 있는가?" 사실 확인
# HOLD 조건: direct_competitors = 0이고 indirect도 없음 (시장 자체 미존재 의심)

direct_competitors:
  # 동일한 pain을 동일한 워크플로우로 푸는 제품 (최대 3개)
  # 없으면 아래 예시를 지우고 "없음"으로 명시 (빈칸 = 미조사)
  - name: ""
    url: ""
    pricing_tier: ""      # 확인 가능한 요금대: "$49/mo", "enterprise only", "freemium"
    primary_segment: ""   # 누구를 주로 serve하는가: "enterprise CTOs", "SMB marketers"

indirect_alternatives:
  # 사용자가 지금 실제로 쓰는 대체재 (context-intake.md와 중복 가능, 경쟁 관점으로 재기술)
  - name: ""
    category: ""          # "manual", "generic AI", "adjacent SaaS", "in-house"

---

## BLOCK B — 세그먼트 갭 식별
# 목적: Linear vs Jira 패턴 — incumbent가 serve하지 않는 레이어 식별
# HOLD 조건: 갭이 없거나 incumbent가 이미 해당 세그먼트를 명시적으로 target 중
#
# GO 예시: "Jira는 enterprise 복잡성에 최적화 → 온보딩 90일 이내 5인 이하 팀에게 overkill"
# HOLD 예시: "Jasper는 이미 SMB 마케터를 pricing page에서 명시적으로 target 중"

incumbent_gap:
  what_they_serve: ""     # 가장 큰 direct competitor가 주로 serve하는 세그먼트
  what_they_neglect: ""   # 그들이 의도적으로 안 풀거나 못 푸는 세그먼트/워크플로우
  gap_evidence: ""        # 이 갭이 실재한다는 신호 (리뷰 패턴, 포럼 불만, 가격 구조)
                          # ✅ Good: "G2 리뷰 47개에서 'too complex for small teams' 반복"
                          # ❌ Bad: "그럴 것 같다"

your_wedge:
  icp_in_the_gap: ""      # 그 갭 안의 구체적 ICP (행동 기술, 인구통계 금지)
  switching_trigger: ""   # 이 ICP가 현재 대체재를 버릴 사건/조건

---

## BLOCK C — 비즈니스 모델 충돌
# 목적: a16z counterpositioning 테스트
#   "incumbent가 우리 모델을 copy하면 자기 revenue를 잠식하는가?"
# GO 조건: copy cost가 있으면 incumbent가 18개월+ 지연될 가능성
# HOLD 조건: copy cost = "없음" + incumbent moat이 강함

incumbent_model:
  pricing_structure: ""   # "per-seat", "per-project", "enterprise contract", "freemium"
  moat_type: ""           # "workflow lock-in", "data flywheel", "network effects", "brand"

your_model_diff:
  pricing_diff: ""        # 우리 과금 구조가 어떻게 다른가 (예: "per-task vs per-seat")
  copy_cost_for_incumbent: ""
    # incumbent가 우리 방식을 copy하면 어떤 손해를 입는가
    # ✅ Good: "per-seat → per-task 전환 시 ARR 30% 이탈 예상"
    # ❌ HOLD 신호: "없음" 또는 "모르겠음"

---

## BLOCK D — 하드 블로커 체크
# 목적: 즉시 HOLD시키는 구조적 진입 불가 조건 확인
# 아래 중 하나라도 true이면 HOLD — 이유를 evidence와 함께 기재

blockers:
  incumbent_owns_our_segment: false
    # true = incumbent가 우리 ICP를 명시적으로 serve 중이고 NPS가 높음
    # 근거: ""

  regulatory_or_data_moat_blocks_entry: false
    # true = 진입에 필요한 데이터/허가가 incumbent 독점 또는 규제로 막혀 있음
    # 근거: ""

  no_switching_trigger_found: false
    # true = 인터뷰/리뷰에서 전환 조건을 한 건도 찾지 못함
    # 근거: ""

---

## BLOCK E — 진입 근거
# 목적: "왜 지금, 왜 이 팀인가"를 강제 명시
# HOLD 조건: 두 필드 중 하나라도 비어 있음 (모름 / 없음도 불인정)

why_now: ""
  # 시장 타이밍 신호: 규제 변화, 기술 변곡점, incumbent의 pivot, 채널 공백
  # ✅ Good: "Jira가 2025 Q4 enterprise AI 기능에 집중하며 SMB 지원 팀 축소 발표"
  # ❌ Bad: "AI 시대라서"

unfair_advantage: ""
  # 이 팀이 gap을 먼저 fill할 수 있는 구조적 이유
  # ✅ Good: "타깃 ICP 도메인에서 5년 근무, 첫 10명 고객 이미 알고 있음"
  # ❌ Bad: "열심히 할 것이다" / 빈칸

---

## Gate Decision (hplan 자동 판정 기준)

# IMMEDIATE HOLD if any of:
#   - BLOCK B: incumbent_gap.what_they_neglect == ""
#   - BLOCK B: your_wedge.icp_in_the_gap == ""
#   - BLOCK D: blockers.* 중 하나라도 true
#   - BLOCK C: copy_cost_for_incumbent == "없음" AND incumbent moat_type이 강함
#   - BLOCK E: why_now == "" OR unfair_advantage == ""
#
# CONDITIONAL (evidence gate에서 추가 검증 필요) if:
#   - BLOCK A: direct_competitors 0개 (시장 존재 불확실 — 새 카테고리 가능성)
#   - BLOCK B: gap_evidence가 opinion-only (리뷰/인터뷰 인용 없음)
#   - BLOCK B: switching_trigger가 가설 수준 (실제 발화 없음)
#
# GO_SIGNAL if:
#   - 갭 식별 + ICP 정의 + switching trigger 존재 + copy cost 명시 + why_now 명시
