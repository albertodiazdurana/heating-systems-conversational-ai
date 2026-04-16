"""Tests for src.tools.standard_lookup."""

import pytest

from src.tools.standard_lookup import (
    STANDARDS,
    standard_lookup,
    standard_lookup_tool,
)


class TestKnownValues:
    def test_din_12831_indoor_day(self):
        result = standard_lookup("DIN EN 12831", "indoor_design_temp_day")
        assert result["value"] == 20.0
        assert result["unit"] == "°C"
        assert result["standard"] == "DIN EN 12831"

    def test_din_12831_indoor_night(self):
        result = standard_lookup("DIN EN 12831", "indoor_design_temp_night")
        assert result["value"] == 16.0

    def test_vdi_6030_slope_historic(self):
        result = standard_lookup("VDI 6030", "slope_historic")
        assert result["value"] == 1.6
        # Slopes are dimensionless, so no unit field expected.
        assert "unit" not in result

    def test_vdi_6030_slope_low_energy(self):
        assert standard_lookup("VDI 6030", "slope_low_energy")["value"] == 0.3

    def test_din_4702_8_condensing_return(self):
        assert (
            standard_lookup("DIN 4702-8", "t_ruecklauf_max_for_condensing")["value"]
            == 55.0
        )

    def test_dvgw_w551_storage_min(self):
        result = standard_lookup("DVGW W 551", "storage_min_temp")
        assert result["value"] == 60.0
        assert result["unit"] == "°C"

    def test_design_outside_temp_berlin(self):
        assert (
            standard_lookup("DIN EN 12831", "design_outside_temp_berlin")["value"]
            == -14.0
        )

    def test_design_outside_temp_munich_colder_than_berlin(self):
        berlin = standard_lookup("DIN EN 12831", "design_outside_temp_berlin")["value"]
        munich = standard_lookup("DIN EN 12831", "design_outside_temp_munich")["value"]
        assert munich < berlin


class TestErrors:
    def test_unknown_standard_raises(self):
        with pytest.raises(ValueError, match="Unknown standard"):
            standard_lookup("ISO 9999", "anything")

    def test_unknown_standard_error_lists_available(self):
        with pytest.raises(ValueError) as exc:
            standard_lookup("ISO 9999", "anything")
        assert "DIN EN 12831" in str(exc.value)
        assert "VDI 6030" in str(exc.value)

    def test_unknown_key_raises(self):
        with pytest.raises(ValueError, match="Unknown key"):
            standard_lookup("DIN EN 12831", "indoor_design_temp_mars")

    def test_unknown_key_error_lists_available_keys(self):
        with pytest.raises(ValueError) as exc:
            standard_lookup("VDI 6030", "bogus_slope")
        msg = str(exc.value)
        assert "slope_historic" in msg
        assert "slope_low_energy" in msg


class TestStructuralInvariants:
    def test_every_standard_has_nonempty_scope(self):
        for name, entry in STANDARDS.items():
            assert entry.get("scope"), f"{name} is missing scope"

    def test_every_standard_has_at_least_one_key(self):
        for name, entry in STANDARDS.items():
            assert entry["keys"], f"{name} has no keys"

    def test_every_key_has_a_value(self):
        for standard, entry in STANDARDS.items():
            for key, payload in entry["keys"].items():
                assert "value" in payload, f"{standard}/{key} missing value"


class TestToolWrapper:
    def test_tool_invoke_returns_same_dict(self):
        via_plain = standard_lookup("DIN EN 12831", "indoor_design_temp_day")
        via_tool = standard_lookup_tool.invoke(
            {"standard": "DIN EN 12831", "key": "indoor_design_temp_day"}
        )
        assert via_tool == via_plain

    def test_tool_name(self):
        assert standard_lookup_tool.name == "standard_lookup_tool"

    def test_tool_has_description(self):
        # The LangChain tool description is sourced from the docstring; used
        # by the LLM for tool selection. Must not be empty or missing key terms.
        desc = standard_lookup_tool.description
        assert "DIN EN 12831" in desc
        assert "VDI 6030" in desc