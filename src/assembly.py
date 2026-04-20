"""
StackAssembly — vollständige Bauteil-Konfiguration eines PEM-EC-Stacks.

Referenziert Presets aus src/materials.py (Membran, Katalysator, GDL) und
src/components.py (BPP, Endplatte, Stromabnehmer, Dichtung, Tie-Rod) per
Name. Aggregiert Höhe + Masse, bietet JSON-Save/Load, liefert BPP-Außenmaße
für Visualisierung.

Physik-Kopplung in v0.4 bewusst minimal: nur bpp.bulk_resistivity * thickness
fließt in CellSpec.r_bpp. Alles andere ist geometrische Information für die
Visualisierung oder Display-only-Hook für v0.5+ (ADR-006).
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path

from src.components import (
    BIPOLAR_PLATES,
    CURRENT_COLLECTORS,
    END_PLATES,
    GASKETS,
    TIE_RODS,
    BipolarPlateSpec,
    CurrentCollectorSpec,
    EndPlateSpec,
    GasketSpec,
    TieRodSpec,
)
from src.materials import (
    CATALYSTS_ANODE,
    CATALYSTS_CATHODE,
    GDL_ANODE,
    GDL_CATHODE,
    MEMBRANES,
    CatalystSpec,
    GDLSpec,
    MembraneSpec,
)


@dataclass(frozen=True)
class StackAssembly:
    """
    Vollständige Konfiguration eines Stacks. Alle Bauteile per Preset-Name.

    active_area_m2 ist die geometrische Fläche pro Zelle (innerhalb des
    Gasket-Rahmens). BPP ist quadratisch angenommen mit Kante
    sqrt(active_area) + 2 * gasket.frame_width.
    """

    n_cells: int
    active_area_m2: float
    membrane: str
    anode_catalyst: str
    cathode_catalyst: str
    anode_gdl: str
    cathode_gdl: str
    bipolar_plate: str
    end_plate: str
    current_collector: str
    gasket: str
    tie_rod: str
    # Optional Catalyst-Layer-Dicke aus Loading+Density; default 10 µm reicht für Visualisierung.
    catalyst_layer_thickness_m: float = field(default=10e-6)

    # ---------------- Preset resolution ---------------- #

    def membrane_spec(self) -> MembraneSpec:
        return _resolve(MEMBRANES, self.membrane, "membrane")

    def anode_catalyst_spec(self) -> CatalystSpec:
        return _resolve(CATALYSTS_ANODE, self.anode_catalyst, "anode_catalyst")

    def cathode_catalyst_spec(self) -> CatalystSpec:
        return _resolve(CATALYSTS_CATHODE, self.cathode_catalyst, "cathode_catalyst")

    def anode_gdl_spec(self) -> GDLSpec:
        return _resolve(GDL_ANODE, self.anode_gdl, "anode_gdl")

    def cathode_gdl_spec(self) -> GDLSpec:
        return _resolve(GDL_CATHODE, self.cathode_gdl, "cathode_gdl")

    def bipolar_plate_spec(self) -> BipolarPlateSpec:
        return _resolve(BIPOLAR_PLATES, self.bipolar_plate, "bipolar_plate")

    def end_plate_spec(self) -> EndPlateSpec:
        return _resolve(END_PLATES, self.end_plate, "end_plate")

    def current_collector_spec(self) -> CurrentCollectorSpec:
        return _resolve(CURRENT_COLLECTORS, self.current_collector, "current_collector")

    def gasket_spec(self) -> GasketSpec:
        return _resolve(GASKETS, self.gasket, "gasket")

    def tie_rod_spec(self) -> TieRodSpec:
        return _resolve(TIE_RODS, self.tie_rod, "tie_rod")


# ---------------- Aggregation helpers ---------------- #


def per_cell_height_m(a: StackAssembly) -> float:
    """
    Höhe einer einzelnen Zelle [m] ohne Endplatten/Stromabnehmer.

    Eine Zelle = 2 BPP + 2 GDL + 2 Catalyst-Layer + 1 Membran + 2 komprimierte
    Gaskets. Dies ist die "repeating unit" im Stack.
    """
    m = a.membrane_spec()
    a_gdl = a.anode_gdl_spec()
    c_gdl = a.cathode_gdl_spec()
    bpp = a.bipolar_plate_spec()
    gask = a.gasket_spec()
    return (
        2 * bpp.thickness_m
        + a_gdl.thickness_m
        + c_gdl.thickness_m
        + 2 * a.catalyst_layer_thickness_m
        + m.thickness_m
        + 2 * gask.compressed_thickness_m
    )


def total_stack_height_m(a: StackAssembly) -> float:
    """Σ Layer pro Zelle × N + 2 * Endplatte + 2 * Stromabnehmer [m]."""
    return (
        a.n_cells * per_cell_height_m(a)
        + 2 * a.end_plate_spec().thickness_m
        + 2 * a.current_collector_spec().thickness_m
    )


def total_stack_mass_kg(a: StackAssembly) -> float:
    """
    Näherung: Bauteil-Masse = Dichte × Volumen, Volumen = BPP-Fläche × Dicke.
    MEA-Masse (Membran/GDL/Catalyst) vernachlässigt (< 5 % der Gesamtmasse).
    Tie-Rods vernachlässigt (dünne Stangen, < 1 %).
    """
    bpp_w, bpp_h = bpp_outer_dimensions_m(a)
    area_m2 = bpp_w * bpp_h
    bpp = a.bipolar_plate_spec()
    ep = a.end_plate_spec()
    cc = a.current_collector_spec()
    m_bpp = 2 * a.n_cells * bpp.density_kg_m3 * bpp.thickness_m * area_m2
    m_ep = 2 * ep.density_kg_m3 * ep.thickness_m * area_m2
    m_cc = 2 * cc.density_kg_m3 * cc.thickness_m * area_m2
    return m_bpp + m_ep + m_cc


def bpp_outer_dimensions_m(a: StackAssembly) -> tuple[float, float]:
    """
    Kantenlänge der quadratischen BPP [m, m].

    = sqrt(active_area) + 2 * gasket.frame_width. Return-Tuple ist (width, height).
    Rechteckige Stacks sind v0.5-Scope.
    """
    edge = a.active_area_m2**0.5 + 2 * a.gasket_spec().frame_width_m
    return edge, edge


def bpp_resistance_ohm_m2(a: StackAssembly) -> float:
    """
    Area-spezifischer BPP-Widerstand pro Zelle [Ω·m²].

    Eine Zelle sieht zwei halbe BPPs (oben+unten Anode/Kathode-seitig geteilt),
    elektrisch also einen Gesamtweg durch rho * thickness. Dieses Ergebnis kann
    direkt in CellSpec.r_bpp eingesetzt werden.
    """
    bpp = a.bipolar_plate_spec()
    return bpp.bulk_resistivity_ohm_m * bpp.thickness_m


# ---------------- JSON Save/Load ---------------- #


def to_json(a: StackAssembly, path: Path) -> None:
    """Schreibt Assembly als JSON (alle Felder, keine Preset-Expansion)."""
    path = Path(path)
    path.write_text(json.dumps(asdict(a), indent=2), encoding="utf-8")


def from_json(path: Path) -> StackAssembly:
    """
    Liest Assembly aus JSON.

    Preset-Namen werden beim Zugriff (*_spec()) validiert; ein KeyError
    hier bedeutet, die JSON hat einen nicht existierenden Preset-Namen.
    """
    path = Path(path)
    data = json.loads(path.read_text(encoding="utf-8"))
    return StackAssembly(**data)


# ---------------- Defaults ---------------- #


def default_assembly() -> StackAssembly:
    """Ausgangspunkt für UI: 5 Zellen, 50 cm², konservative Preset-Auswahl."""
    return StackAssembly(
        n_cells=5,
        active_area_m2=50e-4,
        membrane="Nafion 212",
        anode_catalyst="IrO2 (commercial)",
        cathode_catalyst="Pt/C (commercial)",
        anode_gdl="Ti felt (1 mm)",
        cathode_gdl="Carbon paper (Toray TGP-H-060)",
        bipolar_plate="Ti-serpentine (EC standard)",
        end_plate="SS-316L 20 mm",
        current_collector="Cu Au-plated 1 mm",
        gasket="PTFE 250 um",
        tie_rod="M10 x 8",
    )


# ---------------- Internal ---------------- #


def _resolve(preset_dict: dict, name: str, field_label: str):
    try:
        return preset_dict[name]
    except KeyError as err:
        raise KeyError(
            f"Assembly.{field_label}={name!r} nicht in Presets gefunden. "
            f"Verfügbar: {sorted(preset_dict.keys())}"
        ) from err
