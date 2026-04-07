"""Tests for src.tools.unit_converter."""

import math

import pytest

from src.tools.unit_converter import (
    KCAL_PER_H_PER_KW,
    degree_days,
    kcal_per_h_to_kw,
    kw_to_kcal_per_h,
)


class TestKwKcalConversion:
    def test_constant_value(self):
        # 1 kW = 3600 kJ/h / 4.184 kJ/kcal
        assert math.isclose(KCAL_PER_H_PER_KW, 860.4206, abs_tol=1e-3)

    def test_one_kw(self):
        assert math.isclose(kw_to_kcal_per_h(1.0), 860.4206, abs_tol=1e-3)

    def test_zero(self):
        assert kw_to_kcal_per_h(0.0) == 0.0
        assert kcal_per_h_to_kw(0.0) == 0.0

    def test_round_trip(self):
        for kw in [0.5, 1.0, 7.5, 24.0, 150.0]:
            assert math.isclose(kcal_per_h_to_kw(kw_to_kcal_per_h(kw)), kw, rel_tol=1e-12)

    def test_typical_residential_boiler(self):
        # 24 kW gas boiler -> ~20,650 kcal/h (commonly cited reference)
        assert math.isclose(kw_to_kcal_per_h(24.0), 20650.0, abs_tol=5.0)


class TestDegreeDays:
    def test_empty_series(self):
        assert degree_days(15.0, []) == 0.0

    def test_all_warmer_than_base(self):
        assert degree_days(15.0, [16.0, 18.0, 20.0]) == 0.0

    def test_known_sequence(self):
        # base=20, temps=[10, 15, 25] -> (20-10) + (20-15) + 0 = 15
        assert degree_days(20.0, [10.0, 15.0, 25.0]) == 15.0

    def test_german_base_15c(self):
        # Cold week: 5 days at 0°C, 2 days at 10°C, base 15°C
        # HDD = 5*15 + 2*5 = 85
        temps = [0.0] * 5 + [10.0] * 2
        assert degree_days(15.0, temps) == 85.0

    def test_negative_temps(self):
        assert degree_days(15.0, [-5.0, -10.0]) == 45.0

    def test_accepts_generator(self):
        assert degree_days(15.0, (t for t in [10.0, 12.0])) == 8.0