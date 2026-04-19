"""
Thermal-0D — stationäre Energiebilanz für PEM-EC Zelle und Stack.

Annahme: Isotherme Zellbedingungen, stationär, keine räumliche Verteilung.
Differenz zwischen tatsächlicher Zellspannung und thermoneutraler Spannung
wird als Wärme dissipiert und muss vom Kühlmittel abgeführt werden.

Energiebilanz:
    P_electric = P_reaction + P_heat
    U_cell · I = E_tn · I · η_F + Q_heat

⇒  Q_heat = (U_cell − E_tn · η_F) · I       (pro Zelle)

E_tn (thermoneutral voltage):
    E_tn = ΔH / (n·F)    (endothermisch bei U_cell < E_tn, exothermisch sonst)
    = 285.83 kJ/mol / (2 · 96485 C/mol) ≈ 1.4813 V bei 298.15 K, HHV

@refs:
    [1] Barbir (2012), Ch. 2.4 — Thermal Management.
    [2] Carmo et al. (2013), Sec. 3.2 — Thermodynamics of Water Electrolysis.
    [3] Tijani et al. (2018), Int. J. Hydrogen Energy 43(20) —
        Thermodynamic Analysis of PEM Water Electrolysis.
"""

from dataclasses import dataclass
from typing import Dict

from .constants import DELTA_H_H2O, F, N_ELECTRONS_H2O
from .electrochemistry import Electrochemistry


# Thermoneutral voltage at 25 °C, liquid water product (HHV-basis)
# E_tn = ΔH_H2O / (n · F) = 285830 / (2 · 96485.33212)
E_TN_STANDARD: float = DELTA_H_H2O / (N_ELECTRONS_H2O * F)  # ≈ 1.4813 V


@dataclass
class ThermalModel:
    """
    0D Thermal-Bilanz für eine Zelle oder einen Stack.

    Attributes:
        cell:             Electrochemistry-Instanz
        n_cells:          Anzahl Zellen (1 = Einzelzelle)
        active_area_si:   Aktive Fläche pro Zelle [m²]
        coolant_cp:       Spez. Wärmekapazität Kühlmittel [J/(kg·K)]
                          Wasser bei 80 °C ≈ 4196 J/(kg·K)
        coolant_dt_k:     Erlaubter Temperaturhub Kühlmittel [K]
    """

    cell: Electrochemistry
    n_cells: int = 1
    active_area_si: float = 0.01
    coolant_cp: float = 4196.0      # J/(kg·K), Wasser @ 80 °C
    coolant_dt_k: float = 5.0       # K

    def __post_init__(self) -> None:
        if self.n_cells < 1:
            raise ValueError(f"n_cells must be >= 1, got {self.n_cells}")
        if self.coolant_cp <= 0:
            raise ValueError(f"coolant_cp must be > 0, got {self.coolant_cp}")
        if self.coolant_dt_k <= 0:
            raise ValueError(f"coolant_dt_k must be > 0, got {self.coolant_dt_k}")

    # -------------------- Thermoneutral voltage -------------------- #

    @staticmethod
    def thermoneutral_voltage() -> float:
        """
        E_tn = ΔH / (n·F) bei 298.15 K (HHV-Basis, flüssiges Wasser).

        Bei U_cell < E_tn: endotherm (Zelle kühlt sich ab, braucht Wärmezufuhr).
        Bei U_cell > E_tn: exotherm (Abwärme muss abgeführt werden).
        PEM-EC läuft praktisch immer exotherm bei j > 0.5 A/cm².
        """
        return E_TN_STANDARD

    # -------------------- Heat generation -------------------- #

    def heat_generation(self, current_density_si: float) -> Dict[str, float]:
        """
        Abwärme-Leistung pro Zelle und für gesamten Stack.

            Q̇_cell = (U_cell − E_tn · η_F) · I     [W]
            Q̇_stack = N · Q̇_cell

        Negative Werte = endothermer Betrieb (untypisch).
        """
        v = self.cell.cell_voltage(current_density_si)
        i_a = current_density_si * self.active_area_si
        u_cell = v["u_cell"]
        eta_f = self.cell.faraday_efficiency

        # Je nachdem ob man HHV-basiert rechnet (mit η_F) oder nicht:
        # streng thermodynamisch: Q = (U - E_tn) · I, ignoriert Faraday-Verluste
        # praktisch (mit Crossover): Q = (U - E_tn · η_F) · I
        q_cell_w = (u_cell - E_TN_STANDARD * eta_f) * i_a
        q_stack_w = self.n_cells * q_cell_w

        return {
            "u_cell_v": u_cell,
            "e_tn_v": E_TN_STANDARD,
            "current_a": i_a,
            "q_cell_w": q_cell_w,
            "q_stack_w": q_stack_w,
            "q_stack_kw": q_stack_w / 1000.0,
            "mode": "exothermic" if q_cell_w > 0 else "endothermic",
        }

    # -------------------- Cooling requirement -------------------- #

    def cooling_flow(self, current_density_si: float) -> Dict[str, float]:
        """
        Erforderlicher Kühlmittel-Massenstrom für definierten ΔT.

            ṁ_cool = Q̇_stack / (cp · ΔT)    [kg/s]

        Bei endothermem Betrieb (q < 0) → Heizung nötig, ṁ_cool wird Null
        gesetzt (keine Kühlung gebraucht).
        """
        q = self.heat_generation(current_density_si)
        q_w = max(0.0, q["q_stack_w"])  # Clamp: keine negative Kühlung
        m_dot_cool = q_w / (self.coolant_cp * self.coolant_dt_k)
        v_dot_cool_l_min = m_dot_cool / 1000.0 * 60.0 * 1000.0  # kg/s → L/min (water)

        return {
            "q_stack_w": q["q_stack_w"],
            "coolant_dt_k": self.coolant_dt_k,
            "m_dot_kg_per_s": m_dot_cool,
            "m_dot_kg_per_h": m_dot_cool * 3600.0,
            "v_dot_l_per_min": v_dot_cool_l_min,  # Näherung, ρ_Wasser ≈ 1000 kg/m³
            "heating_needed": q["q_stack_w"] < 0,
        }

    # -------------------- Thermal efficiency -------------------- #

    def thermal_efficiency(self, current_density_si: float) -> Dict[str, float]:
        """
        Zusätzliche Thermal-Metriken.

            η_thermal = E_tn / U_cell     (thermoneutral efficiency, HHV-Basis)
            η_voltage = E_rev / U_cell    (voltage efficiency, Gibbs-Basis)
        """
        v = self.cell.cell_voltage(current_density_si)
        u_cell = v["u_cell"]
        eta_thermal_hhv = E_TN_STANDARD / u_cell
        eta_voltage = v["e_rev"] / u_cell

        return {
            "eta_thermal_hhv": eta_thermal_hhv,
            "eta_voltage_gibbs": eta_voltage,
            "u_cell_v": u_cell,
            "e_tn_v": E_TN_STANDARD,
            "e_rev_v": v["e_rev"],
        }
