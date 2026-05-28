# Bad Example — hitl

## 사용자 요청
"프롬프트 최적화 좀 해줘. CRISP 프레임워크로 다시 작성해봐."

## 거절 이유
- 에이전트의 Human-in-the-Loop 설계가 아닌 프롬프트 최적화
- hitl 스킬은 "어디에 인간 개입을 넣을지"를 설계하는 것
- 프롬프트 개선은 instruction-design 스킬 범위

## 올바른 라우팅
- 프롬프트 최적화: `deliver/instruction` [예정]
- HITL 설계 필요: `discover/hitl`

## 수정 방향
"에이전트가 승인 없이 고객 결제를 자동 처리하려고 하는데, 할루시네이션 위험이 있어서 어디서 사람이 확인해야 할지 설계해줄 수 있어?" → hitl로 라우팅 가능
