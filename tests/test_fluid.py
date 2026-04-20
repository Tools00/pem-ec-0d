"""Tests für src/fluid.py — ΔP-Modell und Pumpenleistung."""

import pytest

from src.fluid import (
    PressureDropResult,
    darcy_friction_factor,
    flow_path_length_m,
    hydraulic_diameter_m,
    n_channels_parallel,
    pressure_drop,
    pump_power_w,
    stoichiometric_water_flow_m3_s,
    water_density_kg_m3,
    water_viscosity_pa_s,
)

# ---------------- Stoffwerte ---------------- #


def test_water_density_range():
    """ρ(20 °C) ≈ 998, ρ(80 °C) ≈ 971 kg/m³ (lineare Näherung ±5 kg/m³)."""
    assert water_density_kg_m3(293.15) == pytest.approx(998, abs=5)
    assert water_density_kg_m3(353.15) == pytest.approx(972, abs=5)


def test_water_viscosity_monotone_decrease_with_T():
    mu_cold = water_viscosity_pa_s(293.15)
    mu_hot = water_viscosity_pa_s(353.15)
    assert mu_cold > mu_hot
    # 20 °C ≈ 1.00 mPa·s, 80 °C ≈ 0.355 mPa·s
    assert 0.9e-3 < mu_cold < 1.1e-3
    assert 0.3e-3 < mu_hot < 0.4e-3


def test_water_property_range_checks():
    with pytest.raises(ValueError):
        water_density_kg_m3(200.0)
    with pytest.raises(ValueError):
        water_viscosity_pa_s(500.0)


# ---------------- Friction Factor ---------------- #


def test_friction_factor_square_channel_matches_table():
    """α=1.0 → f·Re = 56.91 (Shah & London Table 42, exakt)."""
    re = 100.0
    f = darcy_friction_factor(1.0, re)
    assert f * re == pytest.approx(56.91, rel=1e-3)


def test_friction_factor_narrow_channel_higher():
    """α=0.1 (flach) hat höheres f·Re (~84.7) als quadratisch (56.91)."""
    re = 100.0
    f_square = darcy_friction_factor(1.0, re)
    f_flat = darcy_friction_factor(0.1, re)
    assert f_flat > f_square
    assert f_flat * re == pytest.approx(84.68, rel=1e-3)


def test_friction_factor_interpolation_monotone():
    """α zwischen Tabellen-Stützstellen → zwischen deren Werten."""
    re = 100.0
    values = [darcy_friction_factor(a, re) * re for a in (1.0, 0.8, 0.5, 0.25, 0.1)]
    # Muss monoton steigend sein
    assert all(values[i] <= values[i + 1] for i in range(len(values) - 1))


def test_friction_factor_input_validation():
    with pytest.raises(ValueError):
        darcy_friction_factor(0.0, 100.0)
    with pytest.raises(ValueError):
        darcy_friction_factor(1.5, 100.0)
    with pytest.raises(ValueError):
        darcy_friction_factor(1.0, 0.0)


# ---------------- Geometrie ---------------- #


def test_hydraulic_diameter_square():
    """Quadratischer 1×1 mm Kanal: D_h = 1.0 mm (2·w·d/(w+d) = 2·1·1/2 = 1)."""
    dh = hydraulic_diameter_m(1e-3, 1e-3)
    assert dh == pytest.approx(1e-3, rel=1e-9)


def test_hydraulic_diameter_flat():
    """Flacher Kanal (2×0.5 mm): D_h = 2·2·0.5/2.5 = 0.8 mm."""
    dh = hydraulic_diameter_m(2e-3, 0.5e-3)
    assert dh == pytest.approx(0.8e-3, rel=1e-9)


def test_n_channels_parallel():
    # 100 mm edge, 2 mm pitch → 50 Kanäle
    assert n_channels_parallel(100e-3, 2e-3) == 50
    # edge kleiner als pitch → mindestens 1
    assert n_channels_parallel(0.5e-3, 2e-3) == 1


# ---------------- Path Length ---------------- #


def test_path_length_serpentine_much_longer_than_parallel():
    """Serpentine läuft seriell durch alle N Passes; parallel ist kurz."""
    w = h = 100e-3  # 10×10 cm active area
    pitch = 2e-3
    l_ser = flow_path_length_m("serpentine", w, h, pitch)
    l_par = flow_path_length_m("parallel", w, h, pitch)
    assert l_ser == pytest.approx(h * 50, rel=1e-6)  # 50 passes
    assert l_par == pytest.approx(h, rel=1e-6)
    assert l_ser > 40 * l_par


def test_path_length_unknown_pattern_raises():
    with pytest.raises(ValueError):
        flow_path_length_m("spiral", 0.1, 0.1, 2e-3)


# ---------------- Druckabfall ---------------- #


def _default_kwargs(pattern: str = "serpentine") -> dict:
    return dict(
        flow_pattern=pattern,
        channel_width_m=1e-3,
        channel_depth_m=1e-3,
        channel_pitch_m=2e-3,
        active_width_m=0.1,  # 10×10 cm
        active_height_m=0.1,
        volumetric_flow_per_cell_m3_s=1e-7,  # ≈6 mL/min pro Zelle (typ. λ=50, 100 A)
        temperature_k=353.15,
    )


def test_pressure_drop_returns_physical_result():
    res = pressure_drop(**_default_kwargs("serpentine"))
    assert isinstance(res, PressureDropResult)
    assert res.dp_pa > 0
    assert res.reynolds > 0
    assert res.velocity_m_s > 0
    assert res.hydraulic_diameter_m == pytest.approx(1e-3)
    assert res.path_length_m == pytest.approx(0.1 * 50)  # 50 passes


def test_pressure_drop_serpentine_higher_than_parallel():
    """Serpentine hat deutlich höheren ΔP bei gleicher Flow-Rate."""
    res_ser = pressure_drop(**_default_kwargs("serpentine"))
    res_par = pressure_drop(**_default_kwargs("parallel"))
    assert res_ser.dp_pa > res_par.dp_pa


def test_pressure_drop_raises_on_turbulent():
    """Re > 2000 soll ValueError werfen (turbulent nicht implementiert)."""
    kw = _default_kwargs("serpentine")
    kw["volumetric_flow_per_cell_m3_s"] = 1e-3  # 1 L/s → sehr hohe Geschwindigkeit
    with pytest.raises(ValueError, match="laminar regime"):
        pressure_drop(**kw)


def test_pressure_drop_laminar_realistic_magnitude():
    """
    Sanity: 10×10 cm serpentine, 1×1 mm Kanal, ~6 mL/min Flow (typ. λ=50
    bei 100 A) sollte ΔP in der Größenordnung O(10²–10⁴) Pa geben.
    """
    kw = _default_kwargs("serpentine")
    kw["volumetric_flow_per_cell_m3_s"] = 6e-6 / 60  # 6 mL/min
    res = pressure_drop(**kw)
    assert 10 < res.dp_pa < 1e5, f"ΔP={res.dp_pa:.0f} Pa out of expected range"


# ---------------- Pumpenleistung ---------------- #


def test_pump_power_basic():
    """P = ΔP · Q / η = 1e5 Pa · 1e-4 m³/s / 0.5 = 20 W."""
    assert pump_power_w(1e5, 1e-4, 0.5) == pytest.approx(20.0)


def test_pump_power_input_validation():
    with pytest.raises(ValueError):
        pump_power_w(-1, 1e-4, 0.5)
    with pytest.raises(ValueError):
        pump_power_w(1e5, 1e-4, 0.0)
    with pytest.raises(ValueError):
        pump_power_w(1e5, 1e-4, 1.5)


# ---------------- Stoichiometrische Wasserzufuhr ---------------- #


def test_stoich_water_flow_scales_with_current():
    """ṁ ∝ I (Faraday); doppelter Strom → doppelter Flow."""
    q1 = stoichiometric_water_flow_m3_s(100.0, stoich_ratio=50.0, temperature_k=353.15)
    q2 = stoichiometric_water_flow_m3_s(200.0, stoich_ratio=50.0, temperature_k=353.15)
    assert q2 == pytest.approx(2.0 * q1, rel=1e-9)


def test_stoich_water_flow_scales_with_lambda():
    q50 = stoichiometric_water_flow_m3_s(100.0, 50.0, 353.15)
    q100 = stoichiometric_water_flow_m3_s(100.0, 100.0, 353.15)
    assert q100 == pytest.approx(2.0 * q50, rel=1e-9)


def test_stoich_water_flow_realistic_magnitude():
    """100 A, λ=50, 80 °C → ~0.47 mL/s = 28 mL/min.
    Hand: I/(2F)·M_H2O = 100/(2·96485)·0.01802 = 9.34e-6 kg/s stoich.
    Mit λ=50, ρ=972 → Q = 50·9.34e-6/972 = 4.80e-7 m³/s = 28.8 mL/min. ✓"""
    q = stoichiometric_water_flow_m3_s(100.0, 50.0, 353.15)
    assert q == pytest.approx(4.8e-7, rel=5e-2)
