"""
Unit conversion tests — round-trip identity must hold for every converter.

If a converter loses precision round-trip, it is broken.
"""

import math

import pytest

from src import units as U


@pytest.mark.parametrize("value", [0.1, 1.0, 10.0, 123.456, 1e6])
def test_pressure_roundtrip(value):
    assert math.isclose(U.pa_to_bar(U.bar_to_pa(value)), value, rel_tol=1e-12)
    assert math.isclose(U.bar_to_pa(U.pa_to_bar(value)), value, rel_tol=1e-12)


@pytest.mark.parametrize("value", [-40.0, 0.0, 25.0, 100.0, 250.0])
def test_temperature_roundtrip(value):
    assert math.isclose(U.kelvin_to_celsius(U.celsius_to_kelvin(value)), value, abs_tol=1e-12)
    assert math.isclose(U.celsius_to_kelvin(U.kelvin_to_celsius(value + 273.15)), value + 273.15, abs_tol=1e-12)


@pytest.mark.parametrize("value", [1e-6, 1e-3, 0.1, 1.0, 5.0])
def test_current_density_roundtrip(value):
    assert math.isclose(U.a_per_m2_to_a_per_cm2(U.a_per_cm2_to_a_per_m2(value)), value, rel_tol=1e-12)


@pytest.mark.parametrize("value", [1e-3, 0.01, 0.05, 0.5, 1.0])
def test_ohm_cm2_roundtrip(value):
    assert math.isclose(U.ohm_m2_to_ohm_cm2(U.ohm_cm2_to_ohm_m2(value)), value, rel_tol=1e-12)


@pytest.mark.parametrize("value", [25.0, 50.0, 125.0, 250.0])
def test_length_um_roundtrip(value):
    assert math.isclose(U.m_to_um(U.um_to_m(value)), value, rel_tol=1e-12)


@pytest.mark.parametrize("value", [1.0, 25.0, 100.0, 1000.0])
def test_area_roundtrip(value):
    assert math.isclose(U.m2_to_cm2(U.cm2_to_m2(value)), value, rel_tol=1e-12)


@pytest.mark.parametrize("value", [30.0, 50.0, 75.0])
def test_specific_energy_roundtrip(value):
    e_j_kg = U.kwh_per_kg_to_j_per_kg(value)
    assert math.isclose(U.j_per_kg_to_kwh_per_kg(e_j_kg), value, rel_tol=1e-12)


# Hard-coded conversion factors — catches accidental power-of-10 errors.
def test_conversion_factors():
    assert math.isclose(U.bar_to_pa(1.0), 1e5, rel_tol=1e-12)
    assert math.isclose(U.a_per_cm2_to_a_per_m2(1.0), 1e4, rel_tol=1e-12)
    assert math.isclose(U.ohm_cm2_to_ohm_m2(1.0), 1e-4, rel_tol=1e-12)
    assert math.isclose(U.cm2_to_m2(1.0), 1e-4, rel_tol=1e-12)
    assert math.isclose(U.um_to_m(1.0), 1e-6, rel_tol=1e-12)
