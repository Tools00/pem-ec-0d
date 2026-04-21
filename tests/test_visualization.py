"""Tests für src/visualization.py — headless Figure-Smoke-Tests."""

from dataclasses import asdict

import pytest

from src.assembly import StackAssembly, default_assembly
from src.components import BIPOLAR_PLATES
from src.visualization import (
    draw_bpp_top_view,
    draw_gasket_outline,
    draw_layer_cross_section,
)


def test_cross_section_produces_figure_for_n1():
    a = StackAssembly(**{**asdict(default_assembly()), "n_cells": 1})
    fig = draw_layer_cross_section(a)
    # Für N=1: 2 EndPlates + 2 CC + 9 Layer = 13 Traces (mind.)
    assert len(fig.data) >= 13


def test_cross_section_n200_uses_compressed_view():
    a = StackAssembly(**{**asdict(default_assembly()), "n_cells": 200})
    fig = draw_layer_cross_section(a, max_visible_cells=6)
    # half=3 oben + 1 collapsed + 3 unten = 7 Zellen × 9 Layer + collapsed
    # + 2 EndPlates + 2 CC = ~67 Traces, sicher < 200
    assert len(fig.data) < 200, "compressed view should bound trace count"
    labels = [str(t.y[0]) for t in fig.data]
    assert any("collapsed" in lbl for lbl in labels)


def test_cross_section_exploded_view_grows_extent():
    """v0.6a: explosion_mm > 0 shifts every layer apart — total figure
    extent grows, layer count unchanged, one dotted guide per adjacency."""
    a = StackAssembly(**{**asdict(default_assembly()), "n_cells": 2})
    fig_flat = draw_layer_cross_section(a, explosion_mm=0.0)
    fig_exp = draw_layer_cross_section(a, explosion_mm=1.0)
    # Same number of layer-bars either way (explosion is pure visual offset):
    assert len(fig_flat.data) == len(fig_exp.data)
    # Highest bar top in the exploded view is strictly higher than flat:
    top_flat = max(t.base[0] + t.x[0] for t in fig_flat.data)
    top_exp = max(t.base[0] + t.x[0] for t in fig_exp.data)
    assert top_exp > top_flat, "exploded view must increase total y-extent"
    # Roughly: extent grows by (n_layers - 1) * explosion_mm; for N=2 we
    # have 2+2 + 2*9 = 22 layers, so at 1mm spread we gain ~21 mm minimum.
    assert top_exp - top_flat >= 15.0
    # Dotted guide lines: drawn as "line"-shapes, one per adjacency.
    dotted = [s for s in fig_exp.layout.shapes if getattr(s, "type", None) == "line"]
    flat_dotted = [s for s in fig_flat.layout.shapes if getattr(s, "type", None) == "line"]
    assert len(flat_dotted) == 0, "no guide lines in assembled view"
    assert len(dotted) >= 15, "should draw a guide line between each adjacency"


def test_cross_section_explosion_negative_raises():
    a = StackAssembly(**{**asdict(default_assembly()), "n_cells": 1})
    with pytest.raises(ValueError, match="explosion_mm"):
        draw_layer_cross_section(a, explosion_mm=-0.1)


def test_bpp_top_view_all_patterns():
    for name in BIPOLAR_PLATES:
        fig = draw_bpp_top_view(name, 50e-4, "PTFE 250 um")
        assert len(fig.layout.shapes) > 0, f"{name}: no shapes drawn"


def test_bpp_top_view_unknown_preset_raises():
    with pytest.raises(KeyError, match="not in BIPOLAR_PLATES"):
        draw_bpp_top_view("Nope", 50e-4, "PTFE 250 um")
    with pytest.raises(KeyError, match="not in GASKETS"):
        draw_bpp_top_view("Ti-serpentine (EC standard)", 50e-4, "Nope")


def test_bpp_top_view_rectangular_renders():
    """v0.5: aspect_ratio ≠ 1.0 wirft nicht und erzeugt Shapes."""
    for ar in (0.5, 2.0, 4.0):
        fig = draw_bpp_top_view(
            "Ti-serpentine (EC standard)", 50e-4, "PTFE 250 um", aspect_ratio=ar
        )
        assert len(fig.layout.shapes) > 0


def test_bpp_top_view_aspect_ratio_nonpositive_raises():
    with pytest.raises(ValueError, match="aspect_ratio"):
        draw_bpp_top_view("Ti-serpentine (EC standard)", 50e-4, "PTFE 250 um", aspect_ratio=0.0)


def test_gasket_outline_renders():
    fig = draw_gasket_outline("PTFE 250 um", 50e-4)
    assert len(fig.layout.shapes) == 2  # outer + cut-out
