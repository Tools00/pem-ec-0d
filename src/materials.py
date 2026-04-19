"""
Material-Presets für Membranen, Katalysatoren und GDLs.

Hardcoded Dict-basierte Presets in SI-Einheiten. Werte aus Peer-Review-Quellen,
jede Entry mit `@ref:` und Temperatur-/Feuchte-Bereich der Gültigkeit.

Für v0.5 ist geplant, das in eine SQLite-DB zu migrieren. Für v0.2 reicht
ein Dict — weniger Dependencies, einfacher zu reviewen.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class MembraneSpec:
    """
    Membran-Spezifikation in SI-Einheiten.

    Attributes:
        name:              Handelsname
        thickness_m:       Trockendicke [m]
        conductivity_sm:   Protonen-Leitfähigkeit bei 80 °C, voll hydratisiert [S/m]
        water_uptake:      λ_max (H2O pro SO3H), @ref: Springer (1991)
        ewt_g_mol:         Equivalent weight [g/mol SO3H]
        ref:               Literaturquelle
        valid_temp_k:      Gültigkeitsbereich Temperatur [K]
    """

    name: str
    thickness_m: float
    conductivity_sm: float
    water_uptake: float
    ewt_g_mol: float
    ref: str
    valid_temp_k: tuple[float, float]


MEMBRANES: dict[str, MembraneSpec] = {
    "Nafion 212": MembraneSpec(
        name="Nafion 212",
        thickness_m=50.8e-6,
        conductivity_sm=10.0,
        water_uptake=22.0,
        ewt_g_mol=1100.0,
        ref="Kusoglu & Weber (2017), Chem. Rev. 117(3), 987–1104",
        valid_temp_k=(298.15, 363.15),
    ),
    "Nafion 115": MembraneSpec(
        name="Nafion 115",
        thickness_m=127e-6,
        conductivity_sm=10.0,
        water_uptake=22.0,
        ewt_g_mol=1100.0,
        ref="Kusoglu & Weber (2017), Chem. Rev. 117(3)",
        valid_temp_k=(298.15, 363.15),
    ),
    "Nafion 117": MembraneSpec(
        name="Nafion 117",
        thickness_m=183e-6,
        conductivity_sm=10.0,
        water_uptake=22.0,
        ewt_g_mol=1100.0,
        ref="Springer et al. (1991), J. Electrochem. Soc. 138(8)",
        valid_temp_k=(298.15, 363.15),
    ),
    "Nafion 211": MembraneSpec(
        name="Nafion 211",
        thickness_m=25.4e-6,
        conductivity_sm=10.0,
        water_uptake=22.0,
        ewt_g_mol=1100.0,
        ref="DuPont Datasheet (2016); Kusoglu & Weber (2017)",
        valid_temp_k=(298.15, 363.15),
    ),
    "Aquivion E98-05S": MembraneSpec(
        name="Aquivion E98-05S",
        thickness_m=50e-6,
        conductivity_sm=12.0,
        water_uptake=20.0,
        ewt_g_mol=980.0,
        ref="Solvay Datasheet (2018); Skulimowska et al. (2014), Int. J. Hydrogen Energy 39",
        valid_temp_k=(298.15, 393.15),
    ),
    "Fumapem F-950": MembraneSpec(
        name="Fumapem F-950",
        thickness_m=50e-6,
        conductivity_sm=11.0,
        water_uptake=21.0,
        ewt_g_mol=950.0,
        ref="FumaTech Datasheet (2020)",
        valid_temp_k=(298.15, 373.15),
    ),
}


@dataclass(frozen=True)
class CatalystSpec:
    """
    Katalysator-Spezifikation.

    Attributes:
        name:            Material
        side:            'anode' | 'cathode'
        j0_a_m2:         Austauschstromdichte [A/m²] bei 80 °C, 1 atm
        alpha:           Ladungstransfer-Koeffizient
        loading_mg_cm2:  typ. Beladung [mg/cm²]
        ref:             Literaturquelle
    """

    name: str
    side: str
    j0_a_m2: float
    alpha: float
    loading_mg_cm2: float
    ref: str


CATALYSTS_ANODE: dict[str, CatalystSpec] = {
    "IrO2 (commercial)": CatalystSpec(
        name="IrO2 (commercial)",
        side="anode",
        j0_a_m2=10.0,
        alpha=0.5,
        loading_mg_cm2=2.0,
        ref="Carmo et al. (2013), Tab. 4",
    ),
    "IrRuOx": CatalystSpec(
        name="IrRuOx",
        side="anode",
        j0_a_m2=50.0,
        alpha=0.55,
        loading_mg_cm2=1.5,
        ref="Bernt et al. (2018), J. Electrochem. Soc. 165(5)",
    ),
    "IrO2-TiO2 (low-loading)": CatalystSpec(
        name="IrO2-TiO2 (low-loading)",
        side="anode",
        j0_a_m2=5.0,
        alpha=0.45,
        loading_mg_cm2=0.4,
        ref="Siracusano et al. (2017), Appl. Catal. B 219",
    ),
}


CATALYSTS_CATHODE: dict[str, CatalystSpec] = {
    "Pt/C (commercial)": CatalystSpec(
        name="Pt/C (commercial)",
        side="cathode",
        j0_a_m2=1.0e3,
        alpha=0.5,
        loading_mg_cm2=0.4,
        ref="Carmo et al. (2013), Tab. 4",
    ),
    "Pt black": CatalystSpec(
        name="Pt black",
        side="cathode",
        j0_a_m2=2.0e3,
        alpha=0.5,
        loading_mg_cm2=1.0,
        ref="Bernt et al. (2018), J. Electrochem. Soc. 165(5)",
    ),
    "Pt-alloy (PtCo/C)": CatalystSpec(
        name="Pt-alloy (PtCo/C)",
        side="cathode",
        j0_a_m2=1.5e3,
        alpha=0.5,
        loading_mg_cm2=0.3,
        ref="Huang et al. (2015), Science 348(6240)",
    ),
}


@dataclass(frozen=True)
class GDLSpec:
    """
    Gas-Diffusion-Layer / Porous-Transport-Layer Spezifikation.
    r_specific_ohm_m2: area-specific resistance [Ω·m²]
    """

    name: str
    side: str
    r_specific_ohm_m2: float
    porosity: float
    thickness_m: float
    ref: str


GDL_ANODE: dict[str, GDLSpec] = {
    "Ti felt (1 mm)": GDLSpec(
        name="Ti felt (1 mm)",
        side="anode",
        r_specific_ohm_m2=2e-6,  # ≈ 0.02 Ω·cm²
        porosity=0.7,
        thickness_m=1.0e-3,
        ref="Grigoriev et al. (2009), Int. J. Hydrogen Energy 34(14)",
    ),
    "Ti mesh (0.5 mm)": GDLSpec(
        name="Ti mesh (0.5 mm)",
        side="anode",
        r_specific_ohm_m2=1.5e-6,
        porosity=0.6,
        thickness_m=0.5e-3,
        ref="Lettenmeier et al. (2016), Energy Environ. Sci. 9(8)",
    ),
}

GDL_CATHODE: dict[str, GDLSpec] = {
    "Carbon paper (Toray TGP-H-060)": GDLSpec(
        name="Carbon paper (Toray TGP-H-060)",
        side="cathode",
        r_specific_ohm_m2=1e-6,  # ≈ 0.01 Ω·cm²
        porosity=0.78,
        thickness_m=0.19e-3,
        ref="Toray Datasheet; Mathias et al. (2003), Handbook of Fuel Cells Vol. 3",
    ),
    "Carbon cloth (ELAT)": GDLSpec(
        name="Carbon cloth (ELAT)",
        side="cathode",
        r_specific_ohm_m2=8e-7,
        porosity=0.85,
        thickness_m=0.4e-3,
        ref="Mathias et al. (2003)",
    ),
}


def membrane_names() -> list[str]:
    return list(MEMBRANES.keys())


def anode_catalyst_names() -> list[str]:
    return list(CATALYSTS_ANODE.keys())


def cathode_catalyst_names() -> list[str]:
    return list(CATALYSTS_CATHODE.keys())


def anode_gdl_names() -> list[str]:
    return list(GDL_ANODE.keys())


def cathode_gdl_names() -> list[str]:
    return list(GDL_CATHODE.keys())
