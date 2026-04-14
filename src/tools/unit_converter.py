"""Unit conversions for heating calculations.

Plain-Python functions (framework-agnostic) + LangChain ``@tool`` wrappers for
agent consumption. Wrappers carry the ``_tool`` suffix so plain functions stay
importable for direct tests and Python use.

Functions:
    kw_to_kcal_per_h: Convert thermal power from kW to kcal/h.
    kcal_per_h_to_kw: Inverse of kw_to_kcal_per_h.
    degree_days: Heating degree days (HDD) for a daily temperature series.

LangChain tools:
    kw_to_kcal_per_h_tool, kcal_per_h_to_kw_tool, degree_days_tool.
"""

from collections.abc import Iterable

from langchain_core.tools import tool

# 1 kWh = 3600 kJ; 1 kcal = 4.184 kJ -> 1 kW = 3600/4.184 kcal/h
KCAL_PER_H_PER_KW: float = 3600.0 / 4.184  # 860.4206...


def kw_to_kcal_per_h(kw: float) -> float:
    """Convert thermal power from kilowatts to kilocalories per hour."""
    return kw * KCAL_PER_H_PER_KW


def kcal_per_h_to_kw(kcal_per_h: float) -> float:
    """Convert thermal power from kilocalories per hour to kilowatts."""
    return kcal_per_h / KCAL_PER_H_PER_KW


def degree_days(base_temp: float, daily_temps: Iterable[float]) -> float:
    """Heating degree days for a sequence of daily mean temperatures.

    HDD = sum(max(0, base_temp - t)) over all days. Days warmer than the
    base temperature contribute zero. Standard German base is 15°C
    (Heizgrenztemperatur per VDI 3807).

    Args:
        base_temp: Reference (base) temperature in °C.
        daily_temps: Iterable of daily mean temperatures in °C.

    Returns:
        Sum of heating degree days (°C·day).
    """
    return sum(max(0.0, base_temp - t) for t in daily_temps)


@tool
def kw_to_kcal_per_h_tool(kw: float) -> dict:
    """Convert thermal power from kilowatts (kW) to kilocalories per hour (kcal/h).

    Use when the user asks to convert heating power between the metric SI
    unit (kW) and the traditional kcal/h unit still common in legacy
    heating-system documentation.
    """
    return {"kcal_per_h": kw_to_kcal_per_h(kw), "input": {"kw": kw}}


@tool
def kcal_per_h_to_kw_tool(kcal_per_h: float) -> dict:
    """Convert thermal power from kilocalories per hour (kcal/h) to kilowatts (kW).

    Inverse of kw_to_kcal_per_h_tool. Use when a heating specification is
    given in kcal/h and the user wants the equivalent kW rating.
    """
    return {"kw": kcal_per_h_to_kw(kcal_per_h), "input": {"kcal_per_h": kcal_per_h}}


@tool
def degree_days_tool(base_temp: float, daily_temps: list[float]) -> dict:
    """Compute heating degree days (HDD) for a sequence of daily mean temperatures.

    HDD = sum(max(0, base_temp - t)). Days warmer than base contribute 0.
    German convention uses base_temp = 15 °C (Heizgrenztemperatur per
    VDI 3807). Use when estimating seasonal heating demand from weather data.
    """
    return {
        "hdd": degree_days(base_temp, daily_temps),
        "input": {"base_temp": base_temp, "n_days": len(daily_temps)},
    }