"""
Stack — aggregation of N identical PEM-EC cells in electrical series.

Annahme: Alle Zellen identisch, gleicher Stromfluss, additive Spannungen.
Realitätseinschränkungen (Zellen-Inhomogenität, Thermal-Gradients,
Manifold-Druckverluste) sind in v0.2 NICHT modelliert — siehe
docs/KNOWN_ISSUES.md für geplante Erweiterungen.

Alle Berechnungen in SI. Engineering-Konversion nur in UI-Schicht.

@refs:
    [1] Barbir, F. (2012). PEM Fuel Cells: Theory and Practice, 2nd ed.,
        Ch. 6 — Stack Design.
    [2] Carmo et al. (2013), Int. J. Hydrogen Energy 38(12), Sec. 4 —
        System Integration.
"""

from dataclasses import dataclass
from typing import Dict

import numpy as np

from .electrochemistry import Electrochemistry


@dataclass
class Stack:
    """
    Serielle Verschaltung von N identischen Zellen.

    Attributes:
        cell:            Electrochemistry-Instanz (Einzelzelle)
        n_cells:         Anzahl Zellen in Serie
        active_area_si:  Aktive Fläche pro Zelle [m²]
    """

    cell: Electrochemistry
    n_cells: int = 20
    active_area_si: float = 0.01  # 100 cm² default

    def __post_init__(self) -> None:
        if self.n_cells < 1:
            raise ValueError(f"n_cells must be >= 1, got {self.n_cells}")
        if self.active_area_si <= 0:
            raise ValueError(f"active_area_si must be > 0, got {self.active_area_si}")

    # -------------------- Stack-Voltage & Power -------------------- #

    def stack_voltage(self, current_density_si: float) -> Dict[str, float]:
        """
        U_stack = N · U_cell   (SI, V)

        Alle Zellen teilen denselben Strom, Spannungen addieren sich.
        @ref: Barbir (2012), Eq. (6.1).
        """
        v = self.cell.cell_voltage(current_density_si)
        u_stack = self.n_cells * v["u_cell"]
        return {
            "u_cell": v["u_cell"],
            "u_stack": u_stack,
            "n_cells": self.n_cells,
            "current_a": current_density_si * self.active_area_si,
        }

    def stack_power(self, current_density_si: float) -> Dict[str, float]:
        """
        Leistungsaufnahme des Stacks.

            I          = j · A
            P_electric = U_stack · I
            P_h2_lhv   = ṁ_H2 · LHV_specific
            P_waste    = P_electric − P_h2_lhv − P_thermoneutral_surplus

        @ref: Carmo (2013), Sec. 4.
        """
        v = self.stack_voltage(current_density_si)
        h2 = self.cell.h2_production(current_density_si, self.active_area_si)

        p_electric_w = v["u_stack"] * v["current_a"]
        # LHV of H2 = 241.82 kJ/mol → energy in the hydrogen product stream
        from .constants import LHV_H2, N_ELECTRONS_H2O
        p_h2_lhv_w = self.n_cells * h2["n_dot_mol_per_s"] * LHV_H2

        return {
            "p_electric_w": p_electric_w,
            "p_electric_kw": p_electric_w / 1000.0,
            "p_h2_lhv_w": p_h2_lhv_w,
            "p_h2_lhv_kw": p_h2_lhv_w / 1000.0,
            "p_waste_w": p_electric_w - p_h2_lhv_w,
            "p_waste_kw": (p_electric_w - p_h2_lhv_w) / 1000.0,
            "current_a": v["current_a"],
            "u_stack_v": v["u_stack"],
        }

    # -------------------- Stack H2-Production -------------------- #

    def stack_h2_production(self, current_density_si: float) -> Dict[str, float]:
        """
        Gesamte H2-Produktion des Stacks = N · cell_production.
        """
        h2_cell = self.cell.h2_production(current_density_si, self.active_area_si)
        return {
            "n_dot_mol_per_s": self.n_cells * h2_cell["n_dot_mol_per_s"],
            "m_dot_kg_per_s": self.n_cells * h2_cell["m_dot_kg_per_s"],
            "m_dot_kg_per_h": self.n_cells * h2_cell["m_dot_kg_per_s"] * 3600.0,
            "m_dot_g_per_h": self.n_cells * h2_cell["m_dot_g_per_h"],
            "v_dot_nm3_per_h": self.n_cells * h2_cell["v_dot_nm3_per_h"],
        }

    # -------------------- Stack Efficiency -------------------- #

    def stack_efficiency(self, current_density_si: float) -> Dict[str, float]:
        """
        Stack-Wirkungsgrad.

        Identisch zum Zellwirkungsgrad, da alle Zellen gleich und Strom konstant
        (N·U · I / N·P_H2 = U · I / P_H2_per_cell). Separate Methode, damit
        die UI konsistent aggregieren kann.

            η_voltage = E_rev / U_cell
            η_energy  = η_voltage · η_faraday · (LHV / ΔH)
        """
        return self.cell.efficiency(current_density_si)

    # -------------------- Polarization Curve (Stack) -------------------- #

    def polarization_curve(
        self,
        current_densities_si: np.ndarray,
    ) -> Dict[str, np.ndarray]:
        """
        Stack-Polarisationskurve. U_stack = N · U_cell vektorisiert.
        """
        cell_pol = self.cell.polarization_curve(current_densities_si)
        return {
            "current_density_si": cell_pol["current_density_si"],
            "u_cell": cell_pol["u_cell"],
            "u_stack": self.n_cells * cell_pol["u_cell"],
            "eta_energy": cell_pol["eta_energy"],
            "current_a": current_densities_si * self.active_area_si,
            "p_electric_w": (
                self.n_cells * cell_pol["u_cell"]
                * current_densities_si * self.active_area_si
            ),
        }
