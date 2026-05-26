from .generic import parse_generic
from .evidence_gate import parse_evidence_gate
from .cogs_sentinel import parse_cogs_sentinel
from .gate_state import parse_gate_state
from .pain_board import parse_pain_board
from .ost_viewer import parse_ost_viewer
from .market_intel import parse_market_intel
from .architecture import parse_architecture
from .sprint_tracker import parse_sprint_tracker
from .prd_reader import parse_prd_reader
from .design_system import parse_design_system

_PARSER_MAP = {
    "generic":                parse_generic,
    "evidence-gate":          parse_evidence_gate,
    "cogs-sentinel":          parse_cogs_sentinel,
    "gate-state":             parse_gate_state,
    "pain-board":             parse_pain_board,
    "ost-viewer":             parse_ost_viewer,
    "market-intel":           parse_market_intel,
    "architecture-blueprint": parse_architecture,
    "sprint-tracker":         parse_sprint_tracker,
    "prd-reader":             parse_prd_reader,
    "design-system":          parse_design_system,
}


def parse(md_content: str, template_name: str) -> dict:
    """template_name에 맞는 파서를 선택해 md_content를 파싱한다."""
    parser = _PARSER_MAP.get(template_name, parse_generic)
    return parser(md_content)
