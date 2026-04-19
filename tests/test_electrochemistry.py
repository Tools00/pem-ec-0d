"""
Validation tests for the electrochemistry module.

Core validation strategy for MVP:
  1. Tafel slope at high current matches the analytical value b = 2.303·R·T/(α·F).
  2. U_cell is monotonically increasing with current density.
  3. Reversible voltage scales correctly with temperature and pressure (Nernst).
  4. Input validation rejects non-physical parameters.
"""

import math

import numpy as np
import pytest

from src import units as U
from src.constants import DE0_DT, E0_H2O, T_STANDARD, F, R
from src.electrochemistry import (
    Electrochemistry,
    arrhenius_exchange_current_density,
    springer_membrane_conductivity,
)

# ---------------- Tafel slope validation ---------------- #


def test_tafel_slope_matches_analytical():
    """
    The slope of η_act vs log10(j) must equal  b = 2.303·R·T/(α·F)
    within 0.5 % at high current densities (Tafel regime).
    """
    cell = Electrochemistry.from_engineering(temperature_celsius=80.0, pressure_bar=10.0)

    # Stay at high j (>> j0) so Tafel approximation is valid
    j_si = np.logspace(3, 4.5, 20)  # 1000 to ~31,600 A/m²
    eta_a = np.array([cell.activation_overpotential(j, "anode") for j in j_si])

    # Fit slope in V/decade
    log10_j = np.log10(j_si)
    slope_fit, _ = np.polyfit(log10_j, eta_a, 1)

    slope_analytical = cell.tafel_slope("anode")
    rel_err = abs(slope_fit - slope_analytical) / slope_analytical
    assert rel_err < 5e-3, (
        f"Fitted slope {slope_fit:.6f} V/dec vs analytical {slope_analytical:.6f} V/dec, "
        f"rel_err={rel_err:.2%}"
    )


def test_tafel_slope_values_at_80c():
    """
    At T = 353.15 K, α = 0.5:  b = 2.303 · R·T / (α·F) ≈ 0.1400 V/dec.
    Sanity check on the computed value.
    """
    cell = Electrochemistry.from_engineering(temperature_celsius=80.0, pressure_bar=1.0)
    expected = 2.302_585 * R * 353.15 / (0.5 * F)
    assert math.isclose(cell.tafel_slope("anode"), expected, rel_tol=1e-6)
    assert 0.135 < cell.tafel_slope("anode") < 0.145  # sanity, ≈140 mV/dec at 80 °C


# ---------------- Monotonicity ---------------- #


def test_u_cell_monotonic_in_current():
    cell = Electrochemistry.from_engineering()
    j_si = np.linspace(1e2, 2.5e4, 100)  # 0.01 A/cm² … 2.5 A/cm²
    u = np.array([cell.cell_voltage(j)["u_cell"] for j in j_si])
    diffs = np.diff(u)
    assert np.all(diffs > 0), "U_cell must strictly increase with current density"


# ---------------- Nernst sanity ---------------- #


def test_reversible_voltage_at_standard_conditions():
    cell = Electrochemistry(temperature=T_STANDARD, pressure=101_325.0)
    # ln(1) = 0, so E_rev should equal E0 at standard conditions
    assert math.isclose(cell.e_rev, E0_H2O, abs_tol=1e-9)


def test_reversible_voltage_temperature_coefficient():
    """dE_rev/dT at fixed pressure should match DE0_DT (≈ -0.846 mV/K)."""
    p = 101_325.0
    t1, t2 = 298.15, 348.15
    e1 = Electrochemistry(temperature=t1, pressure=p).e_rev
    e2 = Electrochemistry(temperature=t2, pressure=p).e_rev
    slope = (e2 - e1) / (t2 - t1)
    # Nernst also contributes, but with p = p_ref it vanishes.
    assert math.isclose(slope, DE0_DT, rel_tol=1e-6)


def test_reversible_voltage_pressure_dependence():
    """E_rev increases with operating pressure (Nernst pressure term > 0)."""
    t = 353.15
    e_low = Electrochemistry(temperature=t, pressure=1e5).e_rev
    e_high = Electrochemistry(temperature=t, pressure=30e5).e_rev
    assert e_high > e_low


# ---------------- H2 production ---------------- #


def test_h2_production_scaling():
    """H2 production should scale linearly with active area at fixed j."""
    cell = Electrochemistry.from_engineering()
    j_si = U.a_per_cm2_to_a_per_m2(1.0)

    h2_small = cell.h2_production(j_si, U.cm2_to_m2(10.0))
    h2_big = cell.h2_production(j_si, U.cm2_to_m2(1_000.0))

    ratio = h2_big["m_dot_kg_per_s"] / h2_small["m_dot_kg_per_s"]
    assert math.isclose(ratio, 100.0, rel_tol=1e-9)


# ---------------- Input validation ---------------- #


@pytest.mark.parametrize(
    "kwargs",
    [
        {"temperature": 200.0},  # below 273.15
        {"temperature": 500.0},  # above 423.15
        {"pressure": 1.0},  # below 1e4 Pa
        {"pressure": 1e10},  # above 1e8 Pa
        {"j0_anode": -1.0},  # negative
        {"alpha_anode": 0.0},  # zero
        {"alpha_cathode": 1.5},  # > 1
        {"membrane_thickness": -1e-6},  # negative
        {"membrane_conductivity": 0.0},  # zero
    ],
)
def test_invalid_parameters_rejected(kwargs):
    with pytest.raises(ValueError):
        Electrochemistry(**kwargs)


def test_activation_requires_positive_current():
    cell = Electrochemistry()
    with pytest.raises(ValueError):
        cell.activation_overpotential(0.0, "anode")
    with pytest.raises(ValueError):
        cell.activation_overpotential(-100.0, "anode")


def test_activation_side_must_be_valid():
    cell = Electrochemistry()
    with pytest.raises(ValueError):
        cell.activation_overpotential(1000.0, "middle")  # type: ignore


def test_concentration_raises_at_limit():
    cell = Electrochemistry()
    with pytest.raises(ValueError):
        cell.concentration_overpotential(30_000.0, j_limiting_si=30_000.0)


# ---------------- Sanity ranges for typical PEM-EC operating point ---------------- #


def test_sensible_voltage_at_typical_operating_point():
    """
    80 °C, 10 bar, 1 A/cm² — typical U_cell should be 1.7–2.1 V.
    Literature range: Carmo et al. (2013), Fig. 6.
    """
    cell = Electrochemistry.from_engineering(temperature_celsius=80.0, pressure_bar=10.0)
    j_si = U.a_per_cm2_to_a_per_m2(1.0)
    u = cell.cell_voltage(j_si)["u_cell"]
    assert 1.6 < u < 2.2, f"U_cell={u:.3f} V outside plausible 1.6–2.2 V range"


# ---------------- Springer membrane conductivity σ(λ, T) ---------------- #


def test_springer_reference_value_at_303k():
    """
    Springer 1991 Eq. (23) at T = 303 K, λ = 22 (fully hydrated) must yield
    the literature value:
        σ = (0.005139·22 − 0.00326) · exp(0) S/cm
          = 0.10980 S/cm = 10.980 S/m
    """
    sigma = springer_membrane_conductivity(lambda_h2o=22.0, temperature_k=303.0)
    expected_s_per_m = (0.005139 * 22.0 - 0.00326) * 100.0
    assert math.isclose(sigma, expected_s_per_m, rel_tol=1e-9), (
        f"Got {sigma:.4f} S/m, expected {expected_s_per_m:.4f}"
    )


def test_springer_conductivity_increases_with_temperature():
    """
    Arrhenius-like behaviour: σ(353 K) > σ(303 K) at the same λ.
    Ratio at 80 °C vs. 30 °C should be ~1.8 (Springer calibration).
    """
    sigma_303 = springer_membrane_conductivity(22.0, 303.0)
    sigma_353 = springer_membrane_conductivity(22.0, 353.0)
    assert sigma_353 > sigma_303
    ratio = sigma_353 / sigma_303
    assert 1.6 < ratio < 2.0, f"σ(353)/σ(303) = {ratio:.3f} outside 1.6–2.0"


def test_springer_conductivity_increases_with_hydration():
    """Drier membrane must have lower conductivity (monotonic in λ)."""
    sigma_dry = springer_membrane_conductivity(10.0, 353.0)
    sigma_wet = springer_membrane_conductivity(22.0, 353.0)
    assert sigma_wet > sigma_dry


def test_springer_rejects_dry_membrane():
    """λ ≤ 0.6344 yields non-positive σ → must raise."""
    with pytest.raises(ValueError, match="Springer formula"):
        springer_membrane_conductivity(0.5, 353.0)


def test_springer_rejects_out_of_range_temperature():
    """T outside physical bounds must raise."""
    with pytest.raises(ValueError, match="temperature_k"):
        springer_membrane_conductivity(22.0, 500.0)
    with pytest.raises(ValueError, match="temperature_k"):
        springer_membrane_conductivity(22.0, 250.0)


def test_springer_realistic_nafion_at_80c():
    """
    Fully hydrated Nafion at 80 °C should give σ ≈ 17–22 S/m
    (literature consensus for liquid-water contact). Value at
    (λ=22, T=353.15) should fall inside this band.
    """
    sigma = springer_membrane_conductivity(22.0, 353.15)
    assert 17.0 < sigma < 22.0, f"σ={sigma:.2f} S/m outside expected 17–22 range"


# ---------------- Arrhenius j₀(T) ---------------- #


def test_arrhenius_identity_at_reference_temperature():
    """At T = T_ref the correction factor must be exactly 1."""
    j0_ref = 10.0
    j0_t = arrhenius_exchange_current_density(
        j0_reference=j0_ref,
        activation_energy_j_mol=52_000.0,
        temperature_k=353.15,
        reference_temperature_k=353.15,
    )
    assert math.isclose(j0_t, j0_ref, rel_tol=1e-12)


def test_arrhenius_monotonic_in_temperature():
    """Positive E_a → j0(T) strictly increases with T."""
    temps = np.linspace(293.15, 373.15, 10)
    j0 = [
        arrhenius_exchange_current_density(
            j0_reference=10.0,
            activation_energy_j_mol=52_000.0,
            temperature_k=t,
        )
        for t in temps
    ]
    diffs = np.diff(j0)
    assert np.all(diffs > 0), f"j0(T) not monotonic: {j0}"


def test_arrhenius_iro2_drops_at_room_temperature():
    """
    For IrO₂ (E_a = 52 kJ/mol), j0(298 K) / j0(353 K) should be ≈ 0.05
    (factor ~20 drop from 80 °C to 25 °C). Literature consensus.
    """
    j0_353 = arrhenius_exchange_current_density(
        j0_reference=10.0, activation_energy_j_mol=52_000.0, temperature_k=353.15
    )
    j0_298 = arrhenius_exchange_current_density(
        j0_reference=10.0, activation_energy_j_mol=52_000.0, temperature_k=298.15
    )
    ratio = j0_298 / j0_353
    assert 0.03 < ratio < 0.08, f"j0(298)/j0(353)={ratio:.3f} outside expected 0.03–0.08"


def test_arrhenius_pt_her_weaker_temperature_dependence():
    """
    For Pt/C HER (E_a = 25 kJ/mol), temperature dependence is weaker than for IrO₂.
    Ratio j0(353)/j0(298) with E_a=25 kJ/mol < ratio with E_a=52 kJ/mol.
    """
    ratio_pt = arrhenius_exchange_current_density(
        1.0, 25_000.0, 353.15
    ) / arrhenius_exchange_current_density(1.0, 25_000.0, 298.15)
    ratio_ir = arrhenius_exchange_current_density(
        1.0, 52_000.0, 353.15
    ) / arrhenius_exchange_current_density(1.0, 52_000.0, 298.15)
    assert ratio_pt < ratio_ir


def test_arrhenius_rejects_nonpositive_j0_reference():
    with pytest.raises(ValueError, match="j0_reference"):
        arrhenius_exchange_current_density(0.0, 52_000.0, 353.15)
    with pytest.raises(ValueError, match="j0_reference"):
        arrhenius_exchange_current_density(-1.0, 52_000.0, 353.15)


def test_arrhenius_rejects_nonpositive_activation_energy():
    with pytest.raises(ValueError, match="activation_energy_j_mol"):
        arrhenius_exchange_current_density(10.0, 0.0, 353.15)
    with pytest.raises(ValueError, match="activation_energy_j_mol"):
        arrhenius_exchange_current_density(10.0, -1000.0, 353.15)


def test_arrhenius_rejects_out_of_range_temperature():
    with pytest.raises(ValueError, match="temperature_k"):
        arrhenius_exchange_current_density(10.0, 52_000.0, 500.0)
    with pytest.raises(ValueError, match="temperature_k"):
        arrhenius_exchange_current_density(10.0, 52_000.0, 250.0)


def test_arrhenius_rejects_out_of_range_reference_temperature():
    with pytest.raises(ValueError, match="reference_temperature_k"):
        arrhenius_exchange_current_density(10.0, 52_000.0, 353.15, reference_temperature_k=500.0)
