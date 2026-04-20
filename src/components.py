"""
Stack-Komponenten-Presets für den Visual Stack Designer (v0.4).

Bauteile ausserhalb der MEA (Membrane Electrode Assembly), die in v0.3 noch
nicht modelliert waren: Bipolarplatten, Endplatten, Stromabnehmer, Dichtungen,
Zuganker. SI-Einheiten intern, Preset-Werte aus Peer-Review + Industrie-Datasheets.

Design-Regel (ADR-006): Dataclasses hier leben parallel zu src/materials.py.
Keine Duplikation: Membran/Katalysator/GDL bleiben in materials.py, diese Datei
deckt nur Komponenten ab, für die v0.3 keine Datenquelle hatte.
"""

from dataclasses import dataclass

# -------------------------- Dataclasses -------------------------- #


@dataclass(frozen=True)
class BipolarPlateSpec:
    """
    Bipolarplatte (BPP) mit Flow-Field.

    Attributes:
        name:                     Handelsname oder Kurzbezeichnung
        material:                 "titanium" | "graphite-composite" | "stainless-316L"
        thickness_m:              Plattendicke [m]
        flow_pattern:             "serpentine" | "parallel" | "interdigitated"
        channel_width_m:          Kanalbreite [m]
        channel_depth_m:          Kanaltiefe [m]
        channel_pitch_m:          Kanalabstand Mitte-zu-Mitte [m]
        density_kg_m3:            Dichte für Stack-Masse [kg/m³]
        bulk_resistivity_ohm_m:   spez. el. Widerstand [Ω·m]
        ref:                      Literaturquelle
    """

    name: str
    material: str
    thickness_m: float
    flow_pattern: str
    channel_width_m: float
    channel_depth_m: float
    channel_pitch_m: float
    density_kg_m3: float
    bulk_resistivity_ohm_m: float
    ref: str


@dataclass(frozen=True)
class EndPlateSpec:
    """Endplatte (außen am Stack, trägt Tie-Rod-Kräfte)."""

    name: str
    material: str
    thickness_m: float
    density_kg_m3: float
    ref: str


@dataclass(frozen=True)
class CurrentCollectorSpec:
    """Stromabnehmer (zwischen Endplatte und äußerster BPP)."""

    name: str
    material: str
    thickness_m: float
    bulk_resistivity_ohm_m: float
    density_kg_m3: float
    ref: str


@dataclass(frozen=True)
class GasketSpec:
    """
    Dichtung/Rahmen um die aktive Fläche.

    frame_width_m ist die Rahmenbreite um das Active-Area-Quadrat, daraus
    folgt BPP-Kantenlänge = sqrt(active_area) + 2 * frame_width.
    compressed_thickness_m ist die Dicke nach typ. 20-30 % Kompression.
    """

    name: str
    material: str
    thickness_m: float
    compressed_thickness_m: float
    frame_width_m: float
    ref: str


@dataclass(frozen=True)
class TieRodSpec:
    """Zuganker (Anzugsmoment erzeugt Dichtkraft)."""

    name: str
    thread_size: str
    diameter_m: float
    count: int
    torque_nm: float
    material: str
    ref: str


# -------------------------- Presets: Bipolar Plate -------------------------- #

BIPOLAR_PLATES: dict[str, BipolarPlateSpec] = {
    "Ti-serpentine (EC standard)": BipolarPlateSpec(
        name="Ti-serpentine (EC standard)",
        material="titanium",
        thickness_m=2.0e-3,
        flow_pattern="serpentine",
        channel_width_m=1.0e-3,
        channel_depth_m=1.0e-3,
        channel_pitch_m=2.0e-3,
        density_kg_m3=4506.0,
        bulk_resistivity_ohm_m=4.3e-7,
        ref="Lettenmeier et al. (2016) Energy Environ. Sci. 9(8), 2569",
    ),
    "Ti-parallel (low-dP)": BipolarPlateSpec(
        name="Ti-parallel (low-dP)",
        material="titanium",
        thickness_m=2.0e-3,
        flow_pattern="parallel",
        channel_width_m=1.2e-3,
        channel_depth_m=0.8e-3,
        channel_pitch_m=2.4e-3,
        density_kg_m3=4506.0,
        bulk_resistivity_ohm_m=4.3e-7,
        ref="Grigoriev et al. (2009) Int. J. Hydrogen Energy 34(14), 5986",
    ),
    "Graphite-composite (PEMFC-like)": BipolarPlateSpec(
        name="Graphite-composite (PEMFC-like)",
        material="graphite-composite",
        thickness_m=3.0e-3,
        flow_pattern="serpentine",
        channel_width_m=1.0e-3,
        channel_depth_m=1.0e-3,
        channel_pitch_m=2.0e-3,
        density_kg_m3=1800.0,
        bulk_resistivity_ohm_m=1.3e-4,
        ref="Barbir (2012) PEM Fuel Cells, Ch. 4.3",
    ),
    "SS-316L (cost-optimized)": BipolarPlateSpec(
        name="SS-316L (cost-optimized)",
        material="stainless-316L",
        thickness_m=1.5e-3,
        flow_pattern="parallel",
        channel_width_m=1.0e-3,
        channel_depth_m=0.8e-3,
        channel_pitch_m=2.0e-3,
        density_kg_m3=7990.0,
        bulk_resistivity_ohm_m=7.4e-7,
        ref="Wang et al. (2011) Int. J. Hydrogen Energy 36(16), 10329",
    ),
}


# -------------------------- Presets: End Plate -------------------------- #

END_PLATES: dict[str, EndPlateSpec] = {
    "SS-316L 20 mm": EndPlateSpec(
        name="SS-316L 20 mm",
        material="stainless-316L",
        thickness_m=20.0e-3,
        density_kg_m3=7990.0,
        ref="Barbir (2012) PEM Fuel Cells, Ch. 6.3",
    ),
    "Al-6061 25 mm": EndPlateSpec(
        name="Al-6061 25 mm",
        material="aluminum-6061",
        thickness_m=25.0e-3,
        density_kg_m3=2700.0,
        ref="Barbir (2012) PEM Fuel Cells, Ch. 6.3",
    ),
}


# -------------------------- Presets: Current Collector -------------------------- #

CURRENT_COLLECTORS: dict[str, CurrentCollectorSpec] = {
    "Cu Au-plated 1 mm": CurrentCollectorSpec(
        name="Cu Au-plated 1 mm",
        material="copper-Au-plated",
        thickness_m=1.0e-3,
        bulk_resistivity_ohm_m=1.7e-8,
        density_kg_m3=8960.0,
        ref="Barbir (2012) PEM Fuel Cells, Ch. 6.3",
    ),
    "Cu Ni-plated 1.5 mm": CurrentCollectorSpec(
        name="Cu Ni-plated 1.5 mm",
        material="copper-Ni-plated",
        thickness_m=1.5e-3,
        bulk_resistivity_ohm_m=1.7e-8,
        density_kg_m3=8960.0,
        ref="Barbir (2012) PEM Fuel Cells, Ch. 6.3",
    ),
}


# -------------------------- Presets: Gasket -------------------------- #

GASKETS: dict[str, GasketSpec] = {
    "PTFE 250 um": GasketSpec(
        name="PTFE 250 um",
        material="PTFE",
        thickness_m=250e-6,
        compressed_thickness_m=200e-6,
        frame_width_m=5.0e-3,
        ref="Carmo et al. (2013) Int. J. Hydrogen Energy 38(12), §5.1",
    ),
    "EPDM 500 um": GasketSpec(
        name="EPDM 500 um",
        material="EPDM",
        thickness_m=500e-6,
        compressed_thickness_m=350e-6,
        frame_width_m=8.0e-3,
        ref="Carmo et al. (2013) Int. J. Hydrogen Energy 38(12), §5.1",
    ),
    "Viton-FKM 300 um": GasketSpec(
        name="Viton-FKM 300 um",
        material="Viton-FKM",
        thickness_m=300e-6,
        compressed_thickness_m=220e-6,
        frame_width_m=5.0e-3,
        ref="Carmo et al. (2013) Int. J. Hydrogen Energy 38(12), §5.1",
    ),
}


# -------------------------- Presets: Tie-Rod -------------------------- #

TIE_RODS: dict[str, TieRodSpec] = {
    "M8 x 4": TieRodSpec(
        name="M8 x 4",
        thread_size="M8",
        diameter_m=8.0e-3,
        count=4,
        torque_nm=8.0,
        material="stainless-316L",
        ref="Barbir (2012) PEM Fuel Cells, Ch. 6.3",
    ),
    "M10 x 8": TieRodSpec(
        name="M10 x 8",
        thread_size="M10",
        diameter_m=10.0e-3,
        count=8,
        torque_nm=12.0,
        material="stainless-316L",
        ref="Barbir (2012) PEM Fuel Cells, Ch. 6.3",
    ),
    "M12 x 6": TieRodSpec(
        name="M12 x 6",
        thread_size="M12",
        diameter_m=12.0e-3,
        count=6,
        torque_nm=20.0,
        material="stainless-316L",
        ref="Barbir (2012) PEM Fuel Cells, Ch. 6.3",
    ),
}


# -------------------------- Accessors -------------------------- #


def bipolar_plate_names() -> list[str]:
    """Liste aller BPP-Preset-Namen für UI-Dropdowns."""
    return list(BIPOLAR_PLATES.keys())


def end_plate_names() -> list[str]:
    """Liste aller EndPlate-Preset-Namen."""
    return list(END_PLATES.keys())


def current_collector_names() -> list[str]:
    """Liste aller Current-Collector-Preset-Namen."""
    return list(CURRENT_COLLECTORS.keys())


def gasket_names() -> list[str]:
    """Liste aller Gasket-Preset-Namen."""
    return list(GASKETS.keys())


def tie_rod_names() -> list[str]:
    """Liste aller Tie-Rod-Preset-Namen."""
    return list(TIE_RODS.keys())


# -------------------------- Derived quantities -------------------------- #


def land_width_m(bpp: BipolarPlateSpec) -> float:
    """
    Land-Breite = pitch − channel_width. [m]

    Physikalisch der Stegbereich, der die BPP gegen GDL presst; wichtig für
    den Kontaktwiderstand (v0.5-Hook).
    """
    return bpp.channel_pitch_m - bpp.channel_width_m


def open_area_ratio(bpp: BipolarPlateSpec) -> float:
    """
    Anteil der offenen Kanalfläche an der Gesamtfläche der BPP.

    Return: dimensionslos, (0, 1). Höher = mehr Fluid-Kontakt mit GDL, aber
    weniger el./mech. Kontakt. Hook für v0.5 Mass-Transport-Korrektur.
    """
    return bpp.channel_width_m / bpp.channel_pitch_m
