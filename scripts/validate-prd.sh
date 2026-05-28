#!/bin/bash
# validate-prd.sh — Unified PRD 15-section Quality Gate
# v0.8: Add §15 QA Pool to 14-section gate

OUTPUT_DIR="${1:-.}"
ERRORS=0

PRD_FILE=$(find "$OUTPUT_DIR" -name "*prd*" -o -name "*PRD*" | head -1)

if [ -z "$PRD_FILE" ]; then
  echo "⚠️ PRD 파일을 찾을 수 없습니다."
  exit 0
fi

echo "📋 Unified PRD 15-section Quality Gate 검증: $PRD_FILE"

# 15-section 필수 키워드 (한글·영문 모두 매칭)
SECTIONS=(
  "ICP|페르소나|persona"
  "JTBD|Jobs|Push|Pull"
  "문제|problem|10배|10x"
  "결정 옵션|decision|매트릭스"
  "제외사항|Out-of-Scope|exclusion"
  "Now|Next|Later|MVP|범위|scope"
  "Role|Anti-Goal"
  "Tools|Integration|도구"
  "Memory|Working|Long-term|Procedural"
  "Trigger|Cron|Event|Manual|Pipeline"
  "Output|출력|채널"
  "OKR|North Star|Anti-Metric|성공 지표"
  "가설|Hypothes|2-day experiment"
  "실패|Failure|HITL|Human-in-the-loop"
  "QA Pool|페르소나 에이전트|dev_roles|interview_evidence_verified"
)

SECTION_NAMES=(
  "ICP·페르소나"
  "JTBD·Switch 4 Forces"
  "문제·10배 가치"
  "결정 옵션 매트릭스"
  "제외사항 (Out-of-Scope)"
  "Now/Next/Later"
  "Role·Anti-Goals"
  "Tools & Integrations"
  "Memory & Context (3-tier)"
  "Trigger & Execution"
  "Output Specification"
  "Success Metrics (OKR)"
  "검증 가능 가설"
  "실패 모드·HITL"
  "QA Pool (페르소나 + dev_roles)"
)

for i in "${!SECTIONS[@]}"; do
  pattern="${SECTIONS[$i]}"
  name="${SECTION_NAMES[$i]}"
  if ! grep -qiE "$pattern" "$PRD_FILE" 2>/dev/null; then
    echo "❌ Section $((i+1)) 누락: $name"
    ERRORS=$((ERRORS + 1))
  fi
done

if [ $ERRORS -eq 0 ]; then
  echo "✅ Quality Gate 통과 — 15-section 모두 포함"
else
  echo "⚠️ $ERRORS개 섹션 누락 — 검토 권장"
fi

exit 0
