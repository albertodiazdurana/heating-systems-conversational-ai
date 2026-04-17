"""Lookup reference values from German residential-heating standards.

Covers eight standards relevant to Sprint 1 conversational queries:

- DIN EN 12831: design heat load calculation (indoor/outdoor design temps)
- VDI 6030:     heating-curve slopes by building type
- DIN 4703:     traditional radiator design flow temperatures
- DIN EN 1264:  floor-heating system design
- DIN 4702-8:   condensing boiler operation (max return temperature)
- VDI 2067:     economic efficiency, night-setback convention
- DVGW W 551:   DHW legionella prevention thresholds
- VDI 3807:     Heizgrenztemperatur (heating-limit temperature)

Values compiled from:
    ~/dsm-residential-heating-ds-guide/01_Domain_Fundamentals.md
    ~/dsm-residential-energy-apps/models/heating-curve/app/config.py

City design-outside temperatures (nested under DIN EN 12831) are rounded
approximations, NOT authoritative DIN EN 12831-1 Annex values. Each carries
a "notes" field flagging this.

Functions:
    standard_lookup: plain-Python lookup, raises ValueError on unknown
        standard or key (error message lists available options).
LangChain tools:
    standard_lookup_tool: @tool wrapper for agent consumption.
"""

from langchain_core.tools import tool

# Module-level reference table. Keys are stable; values carry unit + notes.
STANDARDS: dict[str, dict] = {
    "DIN EN 12831": {
        "scope": "Heating systems in buildings — method for calculation of the design heat load",
        "keys": {
            "indoor_design_temp_day": {
                "value": 20.0,
                "unit": "°C",
                "notes": "Standard residential comfort temperature",
            },
            "indoor_design_temp_night": {
                "value": 16.0,
                "unit": "°C",
                "notes": "Common 4 K night setback (see VDI 2067)",
            },
            "comfort_range_min": {"value": 18.0, "unit": "°C"},
            "comfort_range_max": {"value": 24.0, "unit": "°C"},
            "verfahren_B_mandatory_since": {
                "value": 2023,
                "notes": "Required for new and modernized systems",
            },
            # City-level design-outside-temperatures. Approximate; consult
            # DIN EN 12831-1 Annex for authoritative zone values.
            "design_outside_temp_berlin": {
                "value": -14.0,
                "unit": "°C",
                "notes": "Approximate; consult DIN EN 12831-1 Annex for exact value",
            },
            "design_outside_temp_munich": {
                "value": -16.0,
                "unit": "°C",
                "notes": "Approximate; alpine-continental, colder than Berlin",
            },
            "design_outside_temp_hamburg": {
                "value": -12.0,
                "unit": "°C",
                "notes": "Approximate; maritime, milder North Sea influence",
            },
            "design_outside_temp_frankfurt": {
                "value": -12.0,
                "unit": "°C",
                "notes": "Approximate; central moderate climate",
            },
            "design_outside_temp_cologne": {
                "value": -10.0,
                "unit": "°C",
                "notes": "Approximate; mild Rhine valley climate",
            },
            "design_outside_temp_stuttgart": {
                "value": -12.0,
                "unit": "°C",
                "notes": "Approximate; moderate continental",
            },
            "design_outside_temp_dresden": {
                "value": -14.0,
                "unit": "°C",
                "notes": "Approximate; eastern continental climate",
            },
            "design_outside_temp_freiburg": {
                "value": -10.0,
                "unit": "°C",
                "notes": "Approximate; warmest German city",
            },
        },
    },
    "VDI 6030": {
        "scope": "Designing free heating surfaces — fundamentals (heating-curve slopes by building type)",
        "keys": {
            "slope_low_energy": {
                "value": 0.3,
                "notes": "Heat pump + floor heating, KfW 40/55, passive house",
            },
            "slope_renovated": {
                "value": 1.0,
                "notes": "Renovated 1960s-1990s, KfW 70-100, condensing boilers",
            },
            "slope_default_factory": {
                "value": 1.4,
                "notes": "Common factory default (Viessmann, Buderus, Vaillant)",
            },
            "slope_historic": {
                "value": 1.6,
                "notes": "Pre-1940s unrenovated, high transmission losses (Altbau)",
            },
        },
    },
    "DIN 4703": {
        "scope": "Traditional radiator design flow temperatures",
        "keys": {
            "t_vorlauf_max_standard": {"value": 75.0, "unit": "°C"},
            "t_vorlauf_max_historic": {"value": 80.0, "unit": "°C"},
        },
    },
    "DIN EN 1264": {
        "scope": "Floor-heating system design",
        "keys": {
            "t_vorlauf_design": {
                "value": 35.0,
                "unit": "°C",
                "notes": "Typical design flow temperature for floor heating",
            },
        },
    },
    "DIN 4702-8": {
        "scope": "Condensing boiler operation",
        "keys": {
            "t_ruecklauf_max_for_condensing": {
                "value": 55.0,
                "unit": "°C",
                "notes": "Return temperature must stay below this for condensing mode",
            },
        },
    },
    "VDI 2067": {
        "scope": "Economic efficiency of building installations; night-setback convention",
        "keys": {
            "night_setback_standard": {
                "value": 4.0,
                "unit": "K",
                "notes": "Typical reduction from day to night indoor setpoint",
            },
        },
    },
    "DVGW W 551": {
        "scope": "Drinking-water heating and piping systems — legionella prevention",
        "keys": {
            "storage_min_temp": {
                "value": 60.0,
                "unit": "°C",
                "notes": "Minimum DHW storage temperature",
            },
            "distribution_min_temp": {
                "value": 55.0,
                "unit": "°C",
                "notes": "Minimum DHW distribution (return) temperature",
            },
        },
    },
    "VDI 3807": {
        "scope": "Energy consumption characteristics — heating-limit temperature",
        "keys": {
            "heating_limit_temp_standard": {
                "value": 15.0,
                "unit": "°C",
                "notes": "Heizgrenztemperatur: outdoor temp above which heating is off",
            },
        },
    },
}


def standard_lookup(standard: str, key: str = "") -> dict:
    """Look up a reference value from a German heating standard.

    Args:
        standard: Standard identifier, e.g. "DIN EN 12831" or "VDI 6030".
        key: Key within that standard, e.g. "indoor_design_temp_day". If
            empty or omitted, returns an overview of the standard with the
            list of available keys instead of a specific value.

    Returns:
        When key is provided: dict with keys: standard, scope, key, value,
        and optionally unit + notes.
        When key is empty: dict with keys: standard, scope, available_keys,
        note (overview shape, no specific value).

    Raises:
        ValueError: If the standard is unknown, or if the key is given but
            unknown. The error message lists the available options so
            callers (including LLMs) can self-correct.
    """
    if standard not in STANDARDS:
        available = ", ".join(sorted(STANDARDS.keys()))
        raise ValueError(
            f"Unknown standard: {standard!r}. Available: {available}."
        )

    entry = STANDARDS[standard]

    if not key:
        return {
            "standard": standard,
            "scope": entry["scope"],
            "available_keys": sorted(entry["keys"].keys()),
            "note": (
                "Overview returned because no specific key was requested. "
                "Call again with one of available_keys to get a value."
            ),
        }

    if key not in entry["keys"]:
        available = ", ".join(sorted(entry["keys"].keys()))
        raise ValueError(
            f"Unknown key {key!r} for standard {standard!r}. "
            f"Available keys: {available}."
        )

    key_entry = entry["keys"][key]
    result: dict = {
        "standard": standard,
        "scope": entry["scope"],
        "key": key,
        "value": key_entry["value"],
    }
    if "unit" in key_entry:
        result["unit"] = key_entry["unit"]
    if "notes" in key_entry:
        result["notes"] = key_entry["notes"]
    return result


@tool
def standard_lookup_tool(standard: str, key: str = "") -> dict:
    """Look up reference values from German residential-heating standards.

    Supports: DIN EN 12831 (design heat load, indoor/outdoor design temps),
    VDI 6030 (heating-curve slopes by building type), DIN 4703 (radiator
    flow-temperature limits), DIN EN 1264 (floor heating), DIN 4702-8
    (condensing boiler return), VDI 2067 (night setback), DVGW W 551 (DHW
    legionella thresholds), VDI 3807 (Heizgrenztemperatur).

    Use when the user asks about specific values, thresholds, or ranges
    defined by a named standard. If the user asks about a standard
    generally without a specific value (e.g. "What is DIN EN 12831?",
    "Was steht in VDI 6030?"), call with only the standard argument; the
    tool will return an overview with the list of available keys.
    On unknown standard or unknown key, the tool raises with a list of
    available options.

    Args:
        standard: e.g. "DIN EN 12831", "VDI 6030".
        key: e.g. "indoor_design_temp_day", "slope_historic",
            "design_outside_temp_berlin". Omit (empty string) for an
            overview of the standard.
    """
    return standard_lookup(standard, key)
