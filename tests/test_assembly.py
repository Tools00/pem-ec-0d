"""Tests für src/assembly.py — Höhen-/Massen-Aggregation, JSON-Roundtrip."""

import json
from dataclasses import asdict
from pathlib import Path

import pytest

from src.assembly import (
    StackAssembly,
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
    assert w == h  # quadratisch


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
