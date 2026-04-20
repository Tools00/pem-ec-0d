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


def test_bpp_top_view_all_patterns():
    for name in BIPOLAR_PLATES:
        fig = draw_bpp_top_view(name, 50e-4, "PTFE 250 um")
        assert len(fig.layout.shapes) > 0, f"{name}: no shapes drawn"


def test_bpp_top_view_unknown_preset_raises():
    with pytest.raises(KeyError, match="not in BIPOLAR_PLATES"):
        draw_bpp_top_view("Nope", 50e-4, "PTFE 250 um")
    with pytest.raises(KeyError, match="not in GASKETS"):
        draw_bpp_top_view("Ti-serpentine (EC standard)", 50e-4, "Nope")


def test_gasket_outline_renders():
    fig = draw_gasket_outline("PTFE 250 um", 50e-4)
    assert len(fig.layout.shapes) == 2  # outer + cut-out
