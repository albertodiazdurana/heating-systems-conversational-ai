"""Tool registry: single TOOLS list consumed by graph.build_agent.

Centralizes the 5 deterministic tools so graph construction and any
future caller (REPL, eval harness) share one source of truth.
"""

from src.tools.heating_curve import heating_curve_tool
from src.tools.standard_lookup import standard_lookup_tool
from src.tools.unit_converter import (
    degree_days_tool,
    kcal_per_h_to_kw_tool,
    kw_to_kcal_per_h_tool,
)

TOOLS = [
    kw_to_kcal_per_h_tool,
    kcal_per_h_to_kw_tool,
    degree_days_tool,
    standard_lookup_tool,
    heating_curve_tool,
]