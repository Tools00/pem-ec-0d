"""Tests für src/thermal.py — 0D Thermal-Bilanz."""

import math

import pytest

from src import units as U
from src.electrochemistry import Electrochemistry
from src.thermal import E_TN_STANDARD, ThermalModel


@pytest.fixture
def cell_80c():
    return Electrochemistry.from_engineering(temperature_celsius=80.0, pressure_bar=10.0)


# ---------------- Thermoneutral voltage sanity ---------------- #


def test_thermoneutral_voltage_approx_1_481():
    """E_tn = ΔH / (n·F) ≈ 1.481 V bei 298.15 K, HHV."""
    assert 1.475 < E_TN_STANDARD < 1.488
    assert math.isclose(ThermalModel.thermoneutral_voltage(), E_TN_STANDARD)


# ---------------- Konstruktor-Validation ---------------- #


def test_thermal_invalid_n_cells(cell_80c):
    with pytest.raises(ValueError):
        ThermalModel(cell=cell_80c, n_cells=0)


def test_thermal_invalid_coolant_cp(cell_80c):
    with pytest.raises(ValueError):
        ThermalModel(cell=cell_80c, coolant_cp=-1.0)


def test_thermal_invalid_dt(cell_80c):
    with pytest.raises(ValueError):
        ThermalModel(cell=cell_80c, coolant_dt_k=0.0)


# ---------------- Exothermer Betrieb bei typischen Bedingungen ---------------- #


def test_pem_ec_exothermic_at_typical_operation(cell_80c):
    """Bei 80 °C, 10 bar, 1 A/cm² → U_cell ~ 1.9 V > E_tn ~ 1.48 V → exotherm."""
    thermal = ThermalModel(cell=cell_80c, n_cells=1, active_area_si=U.cm2_to_m2(100.0))
    j_si = U.a_per_cm2_to_a_per_m2(1.0)
    q = thermal.heat_generation(j_si)
    assert q["mode"] == "exothermic"
    assert q["q_cell_w"] > 0


# ---------------- Heat skaliert mit N ---------------- #


def test_heat_scales_with_n_cells(cell_80c):
    area = U.cm2_to_m2(100.0)
    t1 = ThermalModel(cell=cell_80c, n_cells=1, active_area_si=area)
    t50 = ThermalModel(cell=cell_80c, n_cells=50, active_area_si=area)
    j_si = U.a_per_cm2_to_a_per_m2(1.0)
    q1 = t1.heat_generation(j_si)["q_stack_w"]
    q50 = t50.heat_generation(j_si)["q_stack_w"]
    assert math.isclose(q50 / q1, 50.0, rel_tol=1e-12)


# ---------------- Cooling-Flow ist konsistent mit Q ---------------- #


def test_cooling_flow_matches_heat_balance(cell_80c):
    """ṁ · cp · ΔT muss Q_stack ergeben."""
    thermal = ThermalModel(
        cell=cell_80c,
        n_cells=20,
        active_area_si=U.cm2_to_m2(100.0),
        coolant_cp=4196.0,
        coolant_dt_k=5.0,
    )
    j_si = U.a_per_cm2_to_a_per_m2(1.5)
    q = thermal.heat_generation(j_si)["q_stack_w"]
    flow = thermal.cooling_flow(j_si)
    recovered_q = flow["m_dot_kg_per_s"] * thermal.coolant_cp * thermal.coolant_dt_k
    assert math.isclose(recovered_q, q, rel_tol=1e-12)


# ---------------- Thermal efficiency ---------------- #


def test_thermal_efficiency_less_than_one_in_operation(cell_80c):
    """η_thermal = E_tn / U_cell, muss < 1 bei U_cell > E_tn sein."""
    thermal = ThermalModel(cell=cell_80c, n_cells=1, active_area_si=U.cm2_to_m2(100.0))
    j_si = U.a_per_cm2_to_a_per_m2(1.0)
    eff = thermal.thermal_efficiency(j_si)
    assert eff["eta_thermal_hhv"] < 1.0
    assert eff["eta_voltage_gibbs"] < eff["eta_thermal_hhv"]  # E_rev < E_tn


# ---------------- Cooling-Flow-Sanity ---------------- #


def test_cooling_flow_realistic_for_5kw_stack(cell_80c):
    """20 Zellen @ 100 cm², 1 A/cm², ΔT=5K → Kühlmittelstrom wenige L/min."""
    thermal = ThermalModel(
        cell=cell_80c,
        n_cells=20,
        active_area_si=U.cm2_to_m2(100.0),
        coolant_dt_k=5.0,
    )
    j_si = U.a_per_cm2_to_a_per_m2(1.0)
    flow = thermal.cooling_flow(j_si)
    # Grobe Sanity: 500–2000 W Abwärme → 1–5 L/min Wasser bei ΔT=5 K
    assert 0.5 < flow["v_dot_l_per_min"] < 10.0, (
        f"v_dot={flow['v_dot_l_per_min']:.2f} L/min außerhalb plausibler Range"
    )
