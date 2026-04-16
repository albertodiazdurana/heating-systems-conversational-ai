"""Tests for src.tools.heating_curve."""

import math

import pytest

from src.tools.heating_curve import flow_temp, heating_curve_tool


class TestKnownPoints:
    """Numerical anchors: the Heizkennlinie formula hits specific expected values.

    Each case fixes inputs whose output can be hand-computed from
    T_vorlauf = t_base + slope*(t_room - t_outdoor), with the clamp
    inactive. Covers the Berlin design condition (-14 °C), a mid-range
    linear check, and a low-slope floor-heating scenario.
    """

    def test_berlin_design_point(self):
        # t_outdoor=-14 (Berlin design), slope=1.4 (factory default),
        # t_room=20, t_base=20: 20 + 1.4 * (20 - (-14)) = 20 + 47.6 = 67.6
        assert flow_temp(
            t_outdoor=-14.0, t_room=20.0, slope=1.4
        ) == pytest.approx(67.6)

    def test_mild_day_linear(self):
        # Check the formula algebraically on a mid-range point.
        # t_outdoor=0, slope=1.0, t_room=20, t_base=20 -> 20 + 20 = 40
        assert flow_temp(t_outdoor=0.0, t_room=20.0, slope=1.0) == 40.0

    def test_floor_heating_low_slope(self):
        # slope=0.3 (heat pump + floor heating). t_outdoor=-14 design.
        # 20 + 0.3 * 34 = 30.2
        assert flow_temp(
            t_outdoor=-14.0, t_room=20.0, slope=0.3
        ) == pytest.approx(30.2)


class TestClamping:
    """Operating-limit clamps: results saturate at t_min and t_max.

    The heating curve is a straight line in (t_outdoor, t_vorlauf) space;
    without limits it would go arbitrarily high in extreme cold or dip
    below condensation-safe levels on mild days. The tool clamps to the
    configured [t_min, t_max] window. These tests exercise both clamps
    with default and custom limits.
    """

    def test_high_clamp_extreme_cold(self):
        # Would compute 20 + 1.4 * 50 = 90, clamped to t_max=75
        assert flow_temp(t_outdoor=-30.0, t_room=20.0, slope=1.4) == 75.0

    def test_low_clamp_mild_outside(self):
        # t_outdoor=14 (just below cutoff), slope=0.3, t_room=20:
        # 20 + 0.3 * 6 = 21.8, clamped up to t_min=25
        assert flow_temp(t_outdoor=14.0, t_room=20.0, slope=0.3) == 25.0

    def test_custom_clamp_limits(self):
        # Narrow floor-heating window: t_min=30, t_max=40. Even extreme
        # cold saturates at 40.
        assert (
            flow_temp(
                t_outdoor=-20.0, t_room=20.0, slope=1.0, t_min=30.0, t_max=40.0
            )
            == 40.0
        )


class TestSummerMode:
    """Heizgrenztemperatur (summer cutoff) behaviour.

    Above ``summer_cutoff`` (default 15 °C per VDI 3807) the heating
    system is off; the plain function signals this with ``math.nan``.
    The cutoff check is strictly ``>``: at exactly the cutoff, heating
    is still on (prevents flapping at the boundary). The custom-cutoff
    case confirms the parameter is honored.
    """

    def test_above_cutoff_returns_nan(self):
        assert math.isnan(flow_temp(t_outdoor=16.0, t_room=20.0, slope=1.0))

    def test_cutoff_edge_not_summer(self):
        # Strictly greater-than: at exactly the cutoff, heating is still on.
        result = flow_temp(t_outdoor=15.0, t_room=20.0, slope=1.0)
        assert not math.isnan(result)
        # 20 + 1.0 * 5 = 25, already at t_min
        assert result == 25.0

    def test_custom_cutoff(self):
        assert math.isnan(
            flow_temp(
                t_outdoor=12.0, t_room=20.0, slope=1.0, summer_cutoff=10.0
            )
        )


class TestMonotonicity:
    """Physical invariant: colder outside -> higher required flow temperature.

    Inside the unclamped range the heating curve is strictly decreasing
    in ``t_outdoor``. This test guards against sign errors that would
    still pass the individual known-point checks but violate the shape
    of the curve.
    """

    def test_colder_outside_gives_higher_vorlauf(self):
        a = flow_temp(t_outdoor=0.0, t_room=20.0, slope=1.0)
        b = flow_temp(t_outdoor=-5.0, t_room=20.0, slope=1.0)
        c = flow_temp(t_outdoor=-10.0, t_room=20.0, slope=1.0)
        assert a < b < c


class TestToolWrapper:
    """LangChain ``@tool`` wrapper contract.

    Confirms the wrapper (a) returns equivalent numeric values to the
    plain function in heating mode, (b) normalises summer-mode NaN to
    JSON-safe ``None`` plus an explicit ``heating_off`` flag, (c)
    exposes a stable tool name for the agent, and (d) carries the
    bilingual vocabulary cues the LLM uses to route German-language
    queries to this tool.
    """

    def test_tool_heating_on_matches_plain(self):
        plain = flow_temp(t_outdoor=-10.0, t_room=20.0, slope=1.0)
        result = heating_curve_tool.invoke(
            {"t_outdoor": -10.0, "t_room": 20.0, "slope": 1.0}
        )
        assert result["flow_temp"] == plain
        assert result["heating_off"] is False
        assert result["inputs"]["t_outdoor"] == -10.0
        assert result["inputs"]["slope"] == 1.0

    def test_tool_summer_mode_returns_none(self):
        result = heating_curve_tool.invoke(
            {"t_outdoor": 18.0, "t_room": 20.0, "slope": 1.0}
        )
        assert result["flow_temp"] is None
        assert result["heating_off"] is True

    def test_tool_name(self):
        assert heating_curve_tool.name == "heating_curve_tool"

    def test_tool_description_has_bilingual_cues(self):
        desc = heating_curve_tool.description
        assert "Heizkennlinie" in desc
        assert "Vorlauftemperatur" in desc
        assert "Steilheit" in desc