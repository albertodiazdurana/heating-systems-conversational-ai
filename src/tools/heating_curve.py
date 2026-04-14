"""Compute Vorlauftemperatur (flow temperature) from the Heizkennlinie.

The heating curve (Heizkennlinie) relates outdoor temperature to the flow
temperature a heating system must supply to maintain the target room
temperature. This module ports the core formula from the companion app at
``~/dsm-residential-energy-apps/models/heating-curve/app/simulation.py``
(function ``calculate_vorlauf``), kept stdlib-only so the tool leaf has no
numpy dependency.

Formula:
    T_vorlauf = t_base + slope * (t_room - t_outdoor)

Clamped to ``[t_min, t_max]``. Heating is off (returns ``math.nan``) when
``t_outdoor > summer_cutoff`` (Heizgrenztemperatur, default 15 °C per
VDI 3807). The summer-mode check short-circuits before the clamp.

Functions:
    flow_temp: plain-Python core; returns float (may be ``math.nan``).
LangChain tools:
    heating_curve_tool: ``@tool`` wrapper; returns JSON-safe dict with
        ``flow_temp = None`` + ``heating_off = True`` in summer mode.
"""

import math

from langchain_core.tools import tool


def flow_temp(
    t_outdoor: float,
    t_room: float,
    slope: float,
    t_base: float = 20.0,
    t_min: float = 25.0,
    t_max: float = 75.0,
    summer_cutoff: float = 15.0,
) -> float:
    """Heizkennlinie flow temperature.

    Args:
        t_outdoor: Outdoor temperature in °C.
        t_room: Target room temperature in °C.
        slope: Heating curve slope (Steilheit). Typical values 0.3 (low-
            energy / floor heating) to 1.6 (historic / poor insulation);
            see ``standard_lookup`` VDI 6030 entries.
        t_base: Base offset added to the slope term. Default 20 °C.
        t_min: Minimum clamp for the flow temperature. Default 25 °C
            (prevents condensation in return pipes).
        t_max: Maximum clamp. Default 75 °C (DIN 4703 traditional radiator).
        summer_cutoff: Outdoor temperature above which heating is off.
            Default 15 °C (VDI 3807 Heizgrenztemperatur).

    Returns:
        Flow temperature in °C, clamped to ``[t_min, t_max]``. Returns
        ``math.nan`` when ``t_outdoor > summer_cutoff``.
    """
    if t_outdoor > summer_cutoff:
        return math.nan
    vorlauf = t_base + slope * (t_room - t_outdoor)
    return max(t_min, min(t_max, vorlauf))


@tool
def heating_curve_tool(
    t_outdoor: float,
    t_room: float,
    slope: float,
    t_base: float = 20.0,
    t_min: float = 25.0,
    t_max: float = 75.0,
    summer_cutoff: float = 15.0,
) -> dict:
    """Compute Vorlauftemperatur (flow temperature) from the Heizkennlinie (heating curve).

    Formula: T_vorlauf = t_base + slope*(t_room - t_outdoor), clamped to
    [t_min, t_max]. Heating is off when t_outdoor > summer_cutoff
    (Heizgrenztemperatur, default 15 °C per VDI 3807).

    Use when the user asks for the flow temperature at a given outdoor
    temperature, or to evaluate how a heating-curve slope (Steilheit)
    translates outside conditions into Vorlauftemperatur. Typical slopes
    range 0.3 (heat pump + floor heating) to 1.6 (historic Altbau); see
    VDI 6030 via standard_lookup.

    Args:
        t_outdoor: Outdoor temperature (°C).
        t_room: Target room temperature (°C).
        slope: Heating-curve slope (Steilheit), typically 0.3-1.6.
        t_base: Base offset (°C), default 20.
        t_min: Minimum flow-temperature clamp (°C), default 25.
        t_max: Maximum flow-temperature clamp (°C), default 75.
        summer_cutoff: Heizgrenztemperatur (°C), default 15.
    """
    result = flow_temp(
        t_outdoor=t_outdoor,
        t_room=t_room,
        slope=slope,
        t_base=t_base,
        t_min=t_min,
        t_max=t_max,
        summer_cutoff=summer_cutoff,
    )
    heating_off = math.isnan(result)
    return {
        "flow_temp": None if heating_off else result,
        "heating_off": heating_off,
        "inputs": {
            "t_outdoor": t_outdoor,
            "t_room": t_room,
            "slope": slope,
            "t_base": t_base,
            "t_min": t_min,
            "t_max": t_max,
            "summer_cutoff": summer_cutoff,
        },
    }