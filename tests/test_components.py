"""Tests für src/components.py — Preset-Konsistenz und abgeleitete Größen."""

from src.components import (
    BIPOLAR_PLATES,
    CURRENT_COLLECTORS,
    END_PLATES,
    GASKETS,
    TIE_RODS,
    bipolar_plate_names,
    current_collector_names,
    end_plate_names,
    gasket_names,
    land_width_m,
    open_area_ratio,
    tie_rod_names,
)


def test_all_presets_have_positive_thickness_and_density():
    for bpp in BIPOLAR_PLATES.values():
        assert bpp.thickness_m > 0 and bpp.density_kg_m3 > 0
        assert bpp.channel_width_m > 0 and bpp.channel_depth_m > 0
        assert bpp.channel_pitch_m > bpp.channel_width_m, (
            f"{bpp.name}: pitch must exceed channel_width so land > 0"
        )
    for ep in END_PLATES.values():
        assert ep.thickness_m > 0 and ep.density_kg_m3 > 0
    for cc in CURRENT_COLLECTORS.values():
        assert cc.thickness_m > 0 and cc.bulk_resistivity_ohm_m > 0
    for g in GASKETS.values():
        assert g.thickness_m > 0 and g.frame_width_m > 0
        assert g.compressed_thickness_m < g.thickness_m, (
            f"{g.name}: compressed must be thinner than uncompressed"
        )
    for tr in TIE_RODS.values():
        assert tr.diameter_m > 0 and tr.count > 0 and tr.torque_nm > 0


def test_bpp_open_area_ratio_in_range():
    for bpp in BIPOLAR_PLATES.values():
        ratio = open_area_ratio(bpp)
        assert 0.0 < ratio < 1.0, f"{bpp.name}: open_area_ratio={ratio} not in (0,1)"


def test_bpp_land_width_positive():
    for bpp in BIPOLAR_PLATES.values():
        lw = land_width_m(bpp)
        assert lw > 0, f"{bpp.name}: land_width={lw} must be positive"


def test_bpp_flow_pattern_values():
    allowed = {"serpentine", "parallel", "interdigitated"}
    for bpp in BIPOLAR_PLATES.values():
        assert bpp.flow_pattern in allowed, f"{bpp.name}: unknown flow_pattern {bpp.flow_pattern}"


def test_all_presets_have_refs():
    for dict_ in (BIPOLAR_PLATES, END_PLATES, CURRENT_COLLECTORS, GASKETS, TIE_RODS):
        for preset in dict_.values():
            assert preset.ref, f"{preset.name}: reference required"


def test_name_helpers_match_dict_keys():
    assert set(bipolar_plate_names()) == set(BIPOLAR_PLATES.keys())
    assert set(end_plate_names()) == set(END_PLATES.keys())
    assert set(current_collector_names()) == set(CURRENT_COLLECTORS.keys())
    assert set(gasket_names()) == set(GASKETS.keys())
    assert set(tie_rod_names()) == set(TIE_RODS.keys())


def test_preset_counts_match_plan():
    """Plan §1: 4 BPP + 2 EndPlate + 2 CurrentCollector + 3 Gasket + 3 TieRod = 14."""
    total = (
        len(BIPOLAR_PLATES)
        + len(END_PLATES)
        + len(CURRENT_COLLECTORS)
        + len(GASKETS)
        + len(TIE_RODS)
    )
    assert total == 14, f"expected 14 presets, got {total}"
