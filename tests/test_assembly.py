"""Tests für src/assembly.py — Höhen-/Massen-Aggregation, JSON-Roundtrip."""

import json
from dataclasses import asdict
from pathlib import Path

import pytest

from src.assembly import (
    StackAssembly,
    active_dimensions_m,
    assembly_pressure_drop,
    assembly_pump_power_w,
    bpp_outer_dimensions_m,
    bpp_resistance_ohm_m2,
    default_assembly,
    from_json,
    per_cell_height_m,
    to_json,
    total_stack_height_m,
    total_stack_mass_kg,
)

# ---------------- Preset resolution ---------------- #


def test_default_assembly_resolves_all_presets():
    a = default_assembly()
    # Kein KeyError:
    a.membrane_spec()
    a.anode_catalyst_spec()
    a.cathode_catalyst_spec()
    a.anode_gdl_spec()
    a.cathode_gdl_spec()
    a.bipolar_plate_spec()
    a.end_plate_spec()
    a.current_collector_spec()
    a.gasket_spec()
    a.tie_rod_spec()


def test_unknown_preset_raises_clear_keyerror():
    a = default_assembly()
    bad = StackAssembly(**{**asdict(a), "membrane": "Nafion-ThatDoesNotExist"})
    with pytest.raises(KeyError, match="membrane=.*Nafion-ThatDoesNotExist"):
        bad.membrane_spec()


# ---------------- Height ---------------- #


def test_per_cell_height_matches_hand_calc():
    a = default_assembly()
    m = a.membrane_spec()
    ag = a.anode_gdl_spec()
    cg = a.cathode_gdl_spec()
    bpp = a.bipolar_plate_spec()
    gk = a.gasket_spec()
    expected = (
        2 * bpp.thickness_m
        + ag.thickness_m
        + cg.thickness_m
        + 2 * a.catalyst_layer_thickness_m
        + m.thickness_m
        + 2 * gk.compressed_thickness_m
    )
    assert per_cell_height_m(a) == pytest.approx(expected, rel=1e-12)


def test_total_stack_height_linear_in_ncells():
    a5 = default_assembly()  # n_cells=5
    a10 = StackAssembly(**{**asdict(a5), "n_cells": 10})
    dh = total_stack_height_m(a10) - total_stack_height_m(a5)
    # Zuwachs = 5 weitere Zellen (Endplatten + Stromabnehmer fallen weg):
    assert dh == pytest.approx(5 * per_cell_height_m(a5), rel=1e-12)


# ---------------- Mass ---------------- #


def test_total_stack_mass_positive_and_scales_with_ncells():
    a1 = default_assembly()
    a50 = StackAssembly(**{**asdict(a1), "n_cells": 50})
    m1 = total_stack_mass_kg(a1)
    m50 = total_stack_mass_kg(a50)
    assert m1 > 0 and m50 > m1
    # BPP-Masse skaliert linear mit N; Endplatten/CC sind Konstanten, also
    # (m50 - m1)/(50-1) == 2*rho_bpp*t_bpp*area (prüfen: positiv, endlich)
    per_cell_bpp_mass = (m50 - m1) / (50 - 1)
    assert per_cell_bpp_mass > 0


# ---------------- Geometry ---------------- #


def test_bpp_outer_dimensions_active_plus_frame():
    a = default_assembly()
    w, h = bpp_outer_dimensions_m(a)
    expected = a.active_area_m2**0.5 + 2 * a.gasket_spec().frame_width_m
    assert w == pytest.approx(expected, rel=1e-12)
    assert w == h  # quadratisch (default aspect_ratio=1.0)


# ---------------- Aspect Ratio (v0.5) ---------------- #


def test_default_aspect_ratio_is_square():
    a = default_assembly()
    assert a.aspect_ratio == 1.0
    w, h = active_dimensions_m(a)
    assert w == pytest.approx(h, rel=1e-12)


def test_aspect_ratio_preserves_area():
    """Verschiedene Aspect-Ratios dürfen die aktive Fläche nicht ändern."""
    base = default_assembly()
    for ar in (0.5, 1.0, 2.0, 4.0):
        a = StackAssembly(**{**asdict(base), "aspect_ratio": ar})
        w, h = active_dimensions_m(a)
        assert w * h == pytest.approx(a.active_area_m2, rel=1e-12)
        assert w / h == pytest.approx(ar, rel=1e-12)


def test_aspect_ratio_rectangular_bpp():
    """aspect_ratio=2.0 → BPP ist rechteckig (width > height)."""
    base = default_assembly()
    a = StackAssembly(**{**asdict(base), "aspect_ratio": 2.0})
    w, h = bpp_outer_dimensions_m(a)
    assert w > h
    aw, ah = active_dimensions_m(a)
    fw = a.gasket_spec().frame_width_m
    assert w == pytest.approx(aw + 2 * fw, rel=1e-12)
    assert h == pytest.approx(ah + 2 * fw, rel=1e-12)


def test_aspect_ratio_nonpositive_raises():
    base = default_assembly()
    a = StackAssembly(**{**asdict(base), "aspect_ratio": 0.0})
    with pytest.raises(ValueError, match="aspect_ratio"):
        active_dimensions_m(a)
    a2 = StackAssembly(**{**asdict(base), "aspect_ratio": -1.0})
    with pytest.raises(ValueError, match="aspect_ratio"):
        active_dimensions_m(a2)


def test_stack_mass_unchanged_by_aspect_ratio_at_constant_area():
    """Masse hängt nur an w·h (= A) und ρ·t, nicht an Aspekt."""
    base = default_assembly()
    m1 = total_stack_mass_kg(base)
    a2 = StackAssembly(**{**asdict(base), "aspect_ratio": 2.5})
    m2 = total_stack_mass_kg(a2)
    # Minimale Differenz weil frame 2·fw pro Seite, aber Frame-Fläche ändert sich
    # geringfügig (perimeter · fw). Wir testen hier die BPP-Area-Komponente.
    # Bei constant area ändert sich nur der Rahmen-Anteil. Abweichung < 10 %.
    assert abs(m1 - m2) / m1 < 0.10


# ---------------- Physics coupling ---------------- #


def test_bpp_resistance_positive_and_monotone_in_thickness():
    """Dickere BPP → höherer ohmscher Widerstand."""
    a_thin = default_assembly()  # Ti 2 mm
    # Rebuild mit dickerer BPP (Graphit 3 mm) für Vergleich:
    a_thick = StackAssembly(
        **{**asdict(a_thin), "bipolar_plate": "Graphite-composite (PEMFC-like)"}
    )
    r_thin = bpp_resistance_ohm_m2(a_thin)
    r_thick = bpp_resistance_ohm_m2(a_thick)
    assert r_thin > 0 and r_thick > r_thin


def test_bpp_resistance_wires_into_electrochemistry_r_bpp():
    """v0.4.1 wire-up: r_bpp aus Assembly landet 1:1 in Electrochemistry.r_bpp."""
    from src.electrochemistry import Electrochemistry

    a = default_assembly()
    r_si = bpp_resistance_ohm_m2(a)  # Ω·m²
    cell = Electrochemistry.from_engineering(r_bpp_ohm_cm2=r_si * 1e4)
    assert cell.r_bpp == pytest.approx(r_si, rel=1e-12)


# ---------------- Fluid coupling (v0.5) ---------------- #


def test_assembly_pressure_drop_returns_positive_physical():
    """Default Ti-serpentine, 50 cm², 100 A Zellstrom, 80 °C → ΔP > 0, Re < 2000."""
    a = default_assembly()
    res = assembly_pressure_drop(
        a,
        current_a=100.0,
        temperature_k=353.15,
        stoich_ratio=50.0,
    )
    assert res.dp_pa > 0
    assert res.reynolds > 0
    assert res.reynolds < 2000  # laminar


def test_assembly_pressure_drop_scales_with_current():
    """Doppelter Strom → doppelter Flow → ΔP skaliert linear bei laminar + fester L."""
    a = default_assembly()
    r1 = assembly_pressure_drop(a, current_a=50.0, temperature_k=353.15)
    r2 = assembly_pressure_drop(a, current_a=100.0, temperature_k=353.15)
    # Laminar: ΔP = f·(L/Dh)·(ρv²/2), f = C/Re = C·μ/(ρ·v·Dh)
    # → ΔP = C·μ·L·v / (2·Dh²) → linear in v → linear in Q → linear in I.
    assert r2.dp_pa == pytest.approx(2.0 * r1.dp_pa, rel=1e-6)


def test_assembly_pump_power_scales_with_n_cells():
    """Pumpenleistung ∝ N (alle Zellen hydraulisch parallel, gleicher ΔP, Σ Q)."""
    a5 = default_assembly()  # n_cells=5
    a10 = StackAssembly(**{**asdict(a5), "n_cells": 10})
    p5 = assembly_pump_power_w(a5, current_a=100.0, temperature_k=353.15)
    p10 = assembly_pump_power_w(a10, current_a=100.0, temperature_k=353.15)
    assert p10 == pytest.approx(2.0 * p5, rel=1e-6)


def test_assembly_pressure_drop_serpentine_vs_parallel():
    """Bei gleichem Flow: serpentine > parallel (längerer Pfad, kein Kanal-Split)."""
    base = default_assembly()  # Ti-serpentine
    a_par = StackAssembly(**{**asdict(base), "bipolar_plate": "Ti-parallel (low-dP)"})
    r_ser = assembly_pressure_drop(base, current_a=100.0, temperature_k=353.15)
    r_par = assembly_pressure_drop(a_par, current_a=100.0, temperature_k=353.15)
    assert r_ser.dp_pa > r_par.dp_pa


# ---------------- JSON Roundtrip ---------------- #


def test_json_roundtrip(tmp_path: Path):
    a = default_assembly()
    path = tmp_path / "assembly.json"
    to_json(a, path)
    a2 = from_json(path)
    assert a == a2


def test_json_file_is_human_readable(tmp_path: Path):
    a = default_assembly()
    path = tmp_path / "assembly.json"
    to_json(a, path)
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["n_cells"] == 5
    assert data["membrane"] == "Nafion 212"


def test_json_roundtrip_with_aspect_ratio():
    """v0.5: Neues Feld aspect_ratio muss im JSON-Roundtrip überleben."""
    base = default_assembly()
    a = StackAssembly(**{**asdict(base), "aspect_ratio": 2.5})
    data = json.dumps(asdict(a))
    a2 = StackAssembly(**json.loads(data))
    assert a == a2
    assert a2.aspect_ratio == 2.5


def test_legacy_json_without_aspect_ratio_loads_as_square():
    """Rückwärtskompatibilität: v0.4-JSONs (ohne aspect_ratio) müssen laden."""
    base = default_assembly()
    d = asdict(base)
    d.pop("aspect_ratio")  # simuliert v0.4-JSON
    a = StackAssembly(**d)
    assert a.aspect_ratio == 1.0  # Default
    w, h = active_dimensions_m(a)
    assert w == pytest.approx(h, rel=1e-12)
