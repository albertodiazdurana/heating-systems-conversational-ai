"""Unit conversions for heating calculations.

Functions:
    kw_to_kcal_per_h: Convert thermal power from kW to kcal/h.
    kcal_per_h_to_kw: Inverse of kw_to_kcal_per_h.
    degree_days: Heating degree days (HDD) for a daily temperature series.
"""

from collections.abc import Iterable

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