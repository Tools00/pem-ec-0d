"""Tests für src/stack.py — Stack-Aggregation."""

import math

import numpy as np
import pytest

from src import units as U
from src.electrochemistry import Electrochemistry
from src.stack import Stack


@pytest.fixture
def cell_80c():
    return Electrochemistry.from_engineering(temperature_celsius=80.0, pressure_bar=10.0)


# ---------------- Konstruktor-Validation ---------------- #


def test_stack_invalid_n_cells(cell_80c):
    with pytest.raises(ValueError):
        Stack(cell=cell_80c, n_cells=0)


def test_stack_invalid_area(cell_80c):
    with pytest.raises(ValueError):
        Stack(cell=cell_80c, active_area_si=-1.0)


# ---------------- Stack-Voltage additiv ---------------- #


def test_stack_voltage_scales_linearly_with_n_cells(cell_80c):
    """U_stack = N · U_cell — exakt linear in N bei festem Strom."""
    j_si = U.a_per_cm2_to_a_per_m2(1.0)
    s1 = Stack(cell=cell_80c, n_cells=1, active_area_si=U.cm2_to_m2(100.0))
    s20 = Stack(cell=cell_80c, n_cells=20, active_area_si=U.cm2_to_m2(100.0))

    u1 = s1.stack_voltage(j_si)["u_stack"]
    u20 = s20.stack_voltage(j_si)["u_stack"]
    assert math.isclose(u20, 20.0 * u1, rel_tol=1e-12)


# ---------------- Stack-Current ---------------- #


def test_stack_current_scales_with_area(cell_80c):
    """I = j · A — unabhängig von N, da Serienschaltung."""
    j_si = U.a_per_cm2_to_a_per_m2(1.0)
    s_small = Stack(cell=cell_80c, n_cells=20, active_area_si=U.cm2_to_m2(50.0))
    s_big = Stack(cell=cell_80c, n_cells=20, active_area_si=U.cm2_to_m2(500.0))

    i_small = s_small.stack_voltage(j_si)["current_a"]
    i_big = s_big.stack_voltage(j_si)["current_a"]
    assert math.isclose(i_big / i_small, 10.0, rel_tol=1e-12)


# ---------------- Power ---------------- #


def test_stack_power_electric_equals_u_times_i(cell_80c):
    """P_electric = U_stack · I."""
    j_si = U.a_per_cm2_to_a_per_m2(1.5)
    stack = Stack(cell=cell_80c, n_cells=10, active_area_si=U.cm2_to_m2(200.0))
    v = stack.stack_voltage(j_si)
    p = stack.stack_power(j_si)
    assert math.isclose(p["p_electric_w"], v["u_stack"] * v["current_a"], rel_tol=1e-12)


def test_stack_power_positive_at_realistic_operating_point(cell_80c):
    """Stack von 20 Zellen @ 100 cm², 1 A/cm² → P_electric ~ 3–4 kW."""
    stack = Stack(cell=cell_80c, n_cells=20, active_area_si=U.cm2_to_m2(100.0))
    j_si = U.a_per_cm2_to_a_per_m2(1.0)
    p = stack.stack_power(j_si)
    assert 2_500.0 < p["p_electric_w"] < 5_000.0, (
        f"P_electric={p['p_electric_w']:.0f} W außerhalb plausibler Range"
    )


# ---------------- H2-Produktion ---------------- #


def test_stack_h2_scales_with_n_cells(cell_80c):
    """H2-Produktion skaliert linear mit Zellanzahl."""
    j_si = U.a_per_cm2_to_a_per_m2(1.0)
    area = U.cm2_to_m2(100.0)
    s1 = Stack(cell=cell_80c, n_cells=1, active_area_si=area)
    s50 = Stack(cell=cell_80c, n_cells=50, active_area_si=area)

    m1 = s1.stack_h2_production(j_si)["m_dot_kg_per_s"]
    m50 = s50.stack_h2_production(j_si)["m_dot_kg_per_s"]
    assert math.isclose(m50 / m1, 50.0, rel_tol=1e-12)


# ---------------- Polarisationskurve ---------------- #


def test_stack_polarization_curve_monotonic(cell_80c):
    stack = Stack(cell=cell_80c, n_cells=10, active_area_si=U.cm2_to_m2(100.0))
    j_range = np.linspace(1e3, 2e4, 50)
    pol = stack.polarization_curve(j_range)
    assert np.all(np.diff(pol["u_stack"]) > 0), "U_stack muss strikt steigen"
    assert np.all(pol["u_stack"] == 10 * pol["u_cell"])
