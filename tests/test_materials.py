"""Tests für src/materials.py — Preset-Konsistenz."""

from src.materials import (
    CATALYSTS_ANODE,
    CATALYSTS_CATHODE,
    GDL_ANODE,
    GDL_CATHODE,
    MEMBRANES,
    anode_catalyst_names,
    cathode_catalyst_names,
    membrane_names,
)

# ---------------- Membran-Presets ---------------- #


def test_membranes_have_positive_properties():
    for name, m in MEMBRANES.items():
        assert m.thickness_m > 0, f"{name}: thickness must be > 0"
        assert m.conductivity_sm > 0, f"{name}: conductivity must be > 0"
        assert m.water_uptake > 0, f"{name}: water uptake must be > 0"
        assert m.ewt_g_mol > 0, f"{name}: EW must be > 0"
        assert m.ref, f"{name}: reference missing"


def test_nafion_thickness_order():
    """Nafion 211 < 212 < 115 < 117 (thickness)."""
    t211 = MEMBRANES["Nafion 211"].thickness_m
    t212 = MEMBRANES["Nafion 212"].thickness_m
    t115 = MEMBRANES["Nafion 115"].thickness_m
    t117 = MEMBRANES["Nafion 117"].thickness_m
    assert t211 < t212 < t115 < t117


def test_membrane_validity_range_sensible():
    for name, m in MEMBRANES.items():
        tmin, tmax = m.valid_temp_k
        assert 273.15 <= tmin < tmax <= 423.15, f"{name}: implausible temp range"


# ---------------- Katalysator-Presets ---------------- #


def test_anode_catalysts_have_lower_j0_than_cathode():
    """OER (Anode) ist langsamer als HER (Kathode) — j0_anode << j0_cathode."""
    for a in CATALYSTS_ANODE.values():
        for c in CATALYSTS_CATHODE.values():
            assert a.j0_a_m2 < c.j0_a_m2, (
                f"j0_anode {a.name}={a.j0_a_m2} ≥ j0_cathode {c.name}={c.j0_a_m2}"
            )


def test_catalyst_side_labels_correct():
    for cat in CATALYSTS_ANODE.values():
        assert cat.side == "anode"
    for cat in CATALYSTS_CATHODE.values():
        assert cat.side == "cathode"


def test_catalyst_alpha_in_valid_range():
    for cat in list(CATALYSTS_ANODE.values()) + list(CATALYSTS_CATHODE.values()):
        assert 0 < cat.alpha <= 1, f"{cat.name}: alpha out of (0, 1]"


# ---------------- GDL-Presets ---------------- #


def test_gdl_resistances_realistic():
    """GDL-Widerstand typisch 1e-7 bis 1e-5 Ω·m²."""
    for gdl in list(GDL_ANODE.values()) + list(GDL_CATHODE.values()):
        assert 1e-8 < gdl.r_specific_ohm_m2 < 1e-4, (
            f"{gdl.name}: r_specific={gdl.r_specific_ohm_m2} outside plausible range"
        )
        assert 0 < gdl.porosity < 1, f"{gdl.name}: porosity out of (0, 1)"


# ---------------- Helper-Funktionen ---------------- #


def test_name_helpers_return_nonempty_lists():
    assert len(membrane_names()) >= 4
    assert len(anode_catalyst_names()) >= 2
    assert len(cathode_catalyst_names()) >= 2


def test_membrane_names_match_dict_keys():
    assert set(membrane_names()) == set(MEMBRANES.keys())


# ---------------- v0.3.1 additive presets ---------------- #


def test_v031_new_membranes_present():
    for name in (
        "Gore-Select M820 (reinforced)",
        "Nafion XL (reinforced)",
        "Aquivion R79-02S",
    ):
        assert name in MEMBRANES, f"missing v0.3.1 membrane: {name}"
        m = MEMBRANES[name]
        assert m.thickness_m > 0 and m.conductivity_sm > 0
        assert m.ref, f"{name}: reference required"


def test_v031_new_catalysts_present():
    for name in (
        "Ir-black (Rozain 2016)",
        "IrOx-ATO (Sb-doped SnO2 support)",
        "Heraeus H2EL-IrO (commercial 2023)",
    ):
        assert name in CATALYSTS_ANODE, f"missing v0.3.1 anode catalyst: {name}"
        assert CATALYSTS_ANODE[name].activation_energy_j_mol > 0
    for name in ("Pt/C ultra-low (0.05 mg/cm\u00b2)", "PtRu/C (startup-tolerant)"):
        assert name in CATALYSTS_CATHODE, f"missing v0.3.1 cathode catalyst: {name}"
        assert CATALYSTS_CATHODE[name].activation_energy_j_mol > 0


def test_v031_new_gdls_present():
    for name in (
        "Ti sintered powder (Mott, 0.25 mm)",
        "Au-coated Ti sintered (0.25 mm)",
    ):
        assert name in GDL_ANODE, f"missing v0.3.1 anode GDL: {name}"
        g = GDL_ANODE[name]
        assert g.thickness_m > 0 and 0 < g.porosity < 1
