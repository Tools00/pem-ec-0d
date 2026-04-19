"""
Electrochemistry — PEM water electrolysis kinetics, SI units throughout.

Cell voltage assembly:
    U_cell = E_rev + η_act,anode + η_act,cathode + η_ohm + η_conc

- E_rev      Nernst equation, temperature- and pressure-corrected
- η_act      Butler-Volmer / Tafel approximation, anode (OER) and cathode (HER)
- η_ohm      Ohmic losses (membrane, GDL, contact, bipolar plate)
- η_conc     Concentration (mass-transport) overpotential near limiting current

All internal calculations in strict SI:
    T [K], p [Pa], j [A/m²], j0 [A/m²], R [Ω·m²] (area-specific),
    σ [S/m], thickness [m]

If your inputs are in engineering units, use `src.units` to convert first
or construct via `Electrochemistry.from_engineering()`.

@refs:
    [1] Larminie, J., & Dicks, A. (2003). Fuel Cell Systems Explained. 2nd ed. Wiley.
    [2] Barbir, F. (2012). PEM Fuel Cells: Theory and Practice. 2nd ed. Academic Press.
    [3] Carmo, M., Fritz, D. L., Mergel, J., & Stolten, D. (2013).
        A comprehensive review on PEM water electrolysis.
        Int. J. Hydrogen Energy, 38(12), 4901–4934.
    [4] Springer, T. E., Zawodzinski, T. A., & Gottesfeld, S. (1991).
        Polymer electrolyte fuel cell model. J. Electrochem. Soc., 138(8).
"""

from dataclasses import dataclass, field

import numpy as np

from . import units as U
from .constants import (
    DE0_DT,
    DELTA_H_H2O,
    E0_H2O,
    LHV_H2,
    M_H2,
    N_ELECTRONS_H2O,
    P_STANDARD,
    T_STANDARD,
    F,
    R,
)

# -------------------- Module-level physics functions -------------------- #


# Threshold below which Springer's formula predicts σ ≤ 0 (non-physical).
# Solving 0.005139·λ − 0.00326 = 0 gives λ ≈ 0.6344.
_SPRINGER_LAMBDA_MIN = 0.6344


def springer_membrane_conductivity(
    lambda_h2o: float,
    temperature_k: float,
) -> float:
    """
    Proton conductivity of perfluorosulfonic-acid membranes (Nafion-type)
    as a function of water content λ and temperature T.

        σ [S/cm] = (0.005139·λ − 0.00326) · exp(1268·(1/303 − 1/T))

    Returned value is converted to SI (S/m).

    Args:
        lambda_h2o:    Water content λ = mol H2O per mol SO3H  [-]
                       Typical PEM-EC range: 14–22 (liquid-water contact, fully swollen)
        temperature_k: Membrane temperature  [K]

    Returns:
        σ in S/m.

    @ref: Springer, T. E., Zawodzinski, T. A., & Gottesfeld, S. (1991).
          Polymer electrolyte fuel cell model. J. Electrochem. Soc. 138(8),
          2334–2342. Eq. (23).
    @valid-range: λ in (0.634, 24]; T in [293.15, 373.15] K (Springer's calibration).
                  Extrapolations outside are permitted but lose accuracy.
    """
    if lambda_h2o <= _SPRINGER_LAMBDA_MIN:
        raise ValueError(
            f"lambda_h2o={lambda_h2o} ≤ {_SPRINGER_LAMBDA_MIN} — "
            "Springer formula yields non-positive conductivity (membrane too dry)."
        )
    if not (273.15 <= temperature_k <= 423.15):
        raise ValueError(f"temperature_k={temperature_k} outside [273.15, 423.15] K")

    sigma_s_per_cm = (0.005139 * lambda_h2o - 0.00326) * np.exp(
        1268.0 * (1.0 / 303.0 - 1.0 / temperature_k)
    )
    return float(sigma_s_per_cm * 100.0)  # S/cm → S/m


def arrhenius_exchange_current_density(
    j0_reference: float,
    activation_energy_j_mol: float,
    temperature_k: float,
    reference_temperature_k: float = 353.15,
) -> float:
    """
    Temperature-corrected exchange current density (Arrhenius).

        j0(T) = j0_ref · exp( −E_a / R · (1/T − 1/T_ref) )

    Args:
        j0_reference:            j0 measured at reference temperature [A/m²]
        activation_energy_j_mol: apparent activation energy E_a [J/mol]
                                 OER/IrO₂:  ~50–70 kJ/mol
                                 HER/Pt:    ~18–30 kJ/mol
        temperature_k:           operating temperature [K]
        reference_temperature_k: temperature at which j0_reference was measured [K].
                                 Defaults to 353.15 K (80 °C), the convention used
                                 in the material-preset table.

    Returns:
        j0(T) in A/m².

    @ref: Carmo et al. (2013), Eq. (9) and discussion p. 4908.
          Suermann et al. (2017), J. Power Sources 365 — IrO₂ E_a ≈ 52 kJ/mol.
          Durst et al. (2014), Energy Environ. Sci. 7 — Pt HER E_a ≈ 25 kJ/mol.
    @valid-range: T in [273, 423] K; E_a > 0; physically meaningful for
                  |T − T_ref| ≲ 80 K before higher-order effects matter.
    """
    if j0_reference <= 0:
        raise ValueError(f"j0_reference must be > 0, got {j0_reference}")
    if activation_energy_j_mol <= 0:
        raise ValueError(f"activation_energy_j_mol must be > 0, got {activation_energy_j_mol}")
    if not (273.15 <= temperature_k <= 423.15):
        raise ValueError(f"temperature_k={temperature_k} outside [273.15, 423.15] K")
    if not (273.15 <= reference_temperature_k <= 423.15):
        raise ValueError(
            f"reference_temperature_k={reference_temperature_k} outside [273.15, 423.15] K"
        )

    return float(
        j0_reference
        * np.exp(
            -activation_energy_j_mol / R * (1.0 / temperature_k - 1.0 / reference_temperature_k)
        )
    )


# -------------------- Data class -------------------- #


@dataclass
class Electrochemistry:
    """
    PEM electrolysis cell model. All fields in SI.

    Typical operating ranges:
        T:   323–363 K          (50–90 °C)
        p:   1e5–3e6 Pa         (1–30 bar)
        j:   100–30000 A/m²     (0.01–3 A/cm²)

    Attributes:
        temperature:           [K]
        pressure:              [Pa]  — isotropic operating pressure
        membrane_conductivity: [S/m] — Nafion ≈ 10 S/m at 80 °C fully hydrated
        membrane_thickness:    [m]   — e.g. Nafion 212: 50 μm = 50e-6 m
        j0_anode:              [A/m²] — OER on IrO2, ~10 A/m² (= 1e-3 A/cm²),
                                        Carmo et al. (2013) Table 4 typical commercial
        j0_cathode:            [A/m²] — HER on Pt, ~1000 A/m² (= 1e-1 A/cm²),
                                        Carmo et al. (2013) Table 4 typical commercial
        alpha_anode:           [-]   — charge-transfer coefficient
        alpha_cathode:         [-]
        r_contact:             [Ω·m²] — area-specific contact resistance
        r_gdl_anode:           [Ω·m²] — Ti felt, ~2e-6 Ω·m² = 0.02 Ω·cm²
        r_gdl_cathode:         [Ω·m²] — carbon paper, ~1e-6 Ω·m² = 0.01 Ω·cm²
        r_bpp:                 [Ω·m²] — bipolar plate
    """

    temperature: float = 353.15  # K, 80 °C
    pressure: float = 10.0 * 1e5  # Pa, 10 bar
    membrane_conductivity: float = 10.0  # S/m
    membrane_thickness: float = 50e-6  # m, Nafion 212
    j0_anode: float = 10.0  # A/m², ≈ 1e-3 A/cm² (IrO2, OER)  — Carmo 2013 Tab. 4
    j0_cathode: float = 1.0e3  # A/m², ≈ 1e-1 A/cm² (Pt, HER)    — Carmo 2013 Tab. 4
    alpha_anode: float = 0.5  # dimensionless
    alpha_cathode: float = 0.5
    r_contact: float = 5e-6  # Ω·m², ≈ 0.05 Ω·cm²
    r_gdl_anode: float = 2e-6  # Ω·m², ≈ 0.02 Ω·cm² (Ti felt)
    r_gdl_cathode: float = 1e-6  # Ω·m², ≈ 0.01 Ω·cm² (carbon paper)
    r_bpp: float = 1e-7  # Ω·m², ≈ 0.001 Ω·cm² (Ti)
    faraday_efficiency: float = 0.98  # dimensionless

    # Computed on init
    e_rev: float = field(init=False)

    def __post_init__(self) -> None:
        self._validate()
        self.e_rev = self._reversible_voltage()

    # -------------------- Constructors -------------------- #

    @classmethod
    def from_engineering(
        cls,
        temperature_celsius: float = 80.0,
        pressure_bar: float = 10.0,
        membrane_conductivity_s_per_m: float = 10.0,
        membrane_thickness_um: float = 50.0,
        j0_anode_a_per_cm2: float = 1e-3,
        j0_cathode_a_per_cm2: float = 1e-1,
        alpha_anode: float = 0.5,
        alpha_cathode: float = 0.5,
        r_contact_ohm_cm2: float = 0.05,
        r_gdl_anode_ohm_cm2: float = 0.02,
        r_gdl_cathode_ohm_cm2: float = 0.01,
        r_bpp_ohm_cm2: float = 0.001,
        faraday_efficiency: float = 0.98,
    ) -> "Electrochemistry":
        """Construct from engineering units (°C, bar, A/cm², Ω·cm²). Converts to SI."""
        return cls(
            temperature=U.celsius_to_kelvin(temperature_celsius),
            pressure=U.bar_to_pa(pressure_bar),
            membrane_conductivity=membrane_conductivity_s_per_m,
            membrane_thickness=U.um_to_m(membrane_thickness_um),
            j0_anode=U.a_per_cm2_to_a_per_m2(j0_anode_a_per_cm2),
            j0_cathode=U.a_per_cm2_to_a_per_m2(j0_cathode_a_per_cm2),
            alpha_anode=alpha_anode,
            alpha_cathode=alpha_cathode,
            r_contact=U.ohm_cm2_to_ohm_m2(r_contact_ohm_cm2),
            r_gdl_anode=U.ohm_cm2_to_ohm_m2(r_gdl_anode_ohm_cm2),
            r_gdl_cathode=U.ohm_cm2_to_ohm_m2(r_gdl_cathode_ohm_cm2),
            r_bpp=U.ohm_cm2_to_ohm_m2(r_bpp_ohm_cm2),
            faraday_efficiency=faraday_efficiency,
        )

    # -------------------- Validation -------------------- #

    def _validate(self) -> None:
        """Guard against non-physical inputs."""
        if not (273.15 <= self.temperature <= 423.15):
            raise ValueError(f"temperature={self.temperature} K outside [273.15, 423.15] K")
        if not (1e4 <= self.pressure <= 1e8):
            raise ValueError(f"pressure={self.pressure} Pa outside [1e4, 1e8] Pa")
        if self.j0_anode <= 0 or self.j0_cathode <= 0:
            raise ValueError("exchange current densities must be positive")
        if not (0 < self.alpha_anode <= 1) or not (0 < self.alpha_cathode <= 1):
            raise ValueError("charge-transfer coefficients must be in (0, 1]")
        if self.membrane_thickness <= 0 or self.membrane_conductivity <= 0:
            raise ValueError("membrane parameters must be positive")

    # -------------------- Nernst / reversible voltage -------------------- #

    def _reversible_voltage(self) -> float:
        """
        Temperature- and pressure-corrected reversible cell voltage.

            E_rev = E0 + dE0/dT · (T − T_ref) + (RT / nF) · ln(p_op / p_ref)

        Simplification: isotropic operating pressure p_op for H2 and O2,
        liquid water activity ≈ 1. Gas pressure ratio enters via Nernst.

        @ref: Larminie & Dicks (2003), Eq. (2.22), simplified for symmetric pressure.
        """
        pressure_ratio = self.pressure / P_STANDARD
        dt = self.temperature - T_STANDARD
        return (
            E0_H2O
            + DE0_DT * dt
            + (R * self.temperature / (N_ELECTRONS_H2O * F)) * np.log(pressure_ratio)
        )

    # -------------------- Butler-Volmer (Tafel) -------------------- #

    def activation_overpotential(
        self,
        current_density_si: float,
        side: str = "anode",
    ) -> float:
        """
        Tafel approximation of Butler-Volmer.

            η_act = (R·T) / (α·F) · ln(j / j0)

        Valid for j >> j0 (typically j/j0 > 10). For PEM electrolysis
        operating currents (j > 1000 A/m²) this is well satisfied.

        Args:
            current_density_si: j in A/m² (SI)
            side: 'anode' (OER) or 'cathode' (HER)

        Returns:
            η_act in V (positive — a loss)

        @ref: Carmo et al. (2013), Eq. (8).
        """
        if current_density_si <= 0:
            raise ValueError(f"current_density_si must be positive, got {current_density_si}")

        if side == "anode":
            j0, alpha = self.j0_anode, self.alpha_anode
        elif side == "cathode":
            j0, alpha = self.j0_cathode, self.alpha_cathode
        else:
            raise ValueError(f"side must be 'anode' or 'cathode', got {side!r}")

        return (R * self.temperature) / (alpha * F) * np.log(current_density_si / j0)

    def tafel_slope(self, side: str = "anode") -> float:
        """
        Tafel slope b = 2.303 · R·T / (α·F)  in V/decade.

        Used as a validation metric: the polarization curve at high j should
        exhibit this slope in semi-log coordinates.
        """
        alpha = self.alpha_anode if side == "anode" else self.alpha_cathode
        return 2.302_585 * R * self.temperature / (alpha * F)

    # -------------------- Ohmic losses -------------------- #

    def ohmic_resistance_total(self) -> float:
        """Total area-specific cell resistance [Ω·m²]."""
        r_membrane = self.membrane_thickness / self.membrane_conductivity
        return r_membrane + self.r_gdl_anode + self.r_gdl_cathode + self.r_contact + self.r_bpp

    def ohmic_overpotential(self, current_density_si: float) -> float:
        """η_ohm = j · R_total (both in SI, result in V)."""
        return current_density_si * self.ohmic_resistance_total()

    # -------------------- Concentration losses -------------------- #

    def concentration_overpotential(
        self,
        current_density_si: float,
        j_limiting_si: float = 30_000.0,  # A/m² (≈ 3 A/cm²)
    ) -> float:
        """
        Mass-transport overpotential near the limiting current.

            η_conc = (R·T) / (n·F) · ln(1 − j / j_L)       (negative-logarithm form, sign-adjusted)

        Implementation returns the magnitude added as a loss to U_cell.
        Returns 0 for j well below j_L (the log term is negligible).

        @ref: Larminie & Dicks (2003), Eq. (3.36).
        """
        if current_density_si >= j_limiting_si:
            raise ValueError(
                f"current_density {current_density_si} A/m² exceeds "
                f"limiting current {j_limiting_si} A/m²"
            )
        # ln(1 - x) is negative for 0 < x < 1; flip sign so eta_conc > 0.
        return -(R * self.temperature / (N_ELECTRONS_H2O * F)) * np.log(
            1.0 - current_density_si / j_limiting_si
        )

    # -------------------- Full cell voltage -------------------- #

    def cell_voltage(
        self,
        current_density_si: float,
        include_concentration: bool = True,
        j_limiting_si: float = 30_000.0,
    ) -> dict[str, float]:
        """
        Complete cell voltage decomposition. All inputs SI, all outputs SI.

        Args:
            current_density_si: j in A/m²
            include_concentration: include mass-transport loss
            j_limiting_si: limiting current density in A/m²

        Returns:
            dict with keys:
                u_cell, e_rev,
                eta_act_anode, eta_act_cathode, eta_act_total,
                eta_ohm, eta_conc, eta_total
            all values in V
        """
        eta_a = self.activation_overpotential(current_density_si, "anode")
        eta_c = self.activation_overpotential(current_density_si, "cathode")
        eta_ohm = self.ohmic_overpotential(current_density_si)

        eta_conc = 0.0
        if include_concentration:
            try:
                eta_conc = self.concentration_overpotential(
                    current_density_si, j_limiting_si=j_limiting_si
                )
            except ValueError:
                eta_conc = float("nan")

        u_cell = self.e_rev + eta_a + eta_c + eta_ohm + eta_conc
        return {
            "u_cell": u_cell,
            "e_rev": self.e_rev,
            "eta_act_anode": eta_a,
            "eta_act_cathode": eta_c,
            "eta_act_total": eta_a + eta_c,
            "eta_ohm": eta_ohm,
            "eta_conc": eta_conc,
            "eta_total": u_cell - self.e_rev,
        }

    # -------------------- Efficiency -------------------- #

    def efficiency(self, current_density_si: float) -> dict[str, float]:
        """
        Efficiency metrics.

            η_voltage = E_rev / U_cell
            η_energy  = η_voltage · η_faraday · (LHV / ΔH)   (LHV-based)
            specific_energy = U_cell · n · F / (M_H2 · η_faraday)  [J/kg]

        @ref: Carmo et al. (2013), Section 3.
        """
        v = self.cell_voltage(current_density_si)
        u_cell = v["u_cell"]

        eta_voltage = self.e_rev / u_cell
        eta_energy = eta_voltage * self.faraday_efficiency * (LHV_H2 / DELTA_H_H2O)

        # J per kg H2 produced at this U_cell
        specific_energy_j_kg = (u_cell * N_ELECTRONS_H2O * F) / (M_H2 * self.faraday_efficiency)
        specific_energy_kwh_kg = U.j_per_kg_to_kwh_per_kg(specific_energy_j_kg)

        return {
            "eta_voltage": eta_voltage,
            "eta_faraday": self.faraday_efficiency,
            "eta_energy": eta_energy,
            "specific_energy_j_kg": specific_energy_j_kg,
            "specific_energy_kwh_kg": specific_energy_kwh_kg,
        }

    # -------------------- H2 production -------------------- #

    def h2_production(
        self,
        current_density_si: float,
        active_area_si: float,
    ) -> dict[str, float]:
        """
        Hydrogen production rate at the given operating point.

            n_dot = η_F · I / (n · F)       [mol/s]
            m_dot = n_dot · M_H2            [kg/s]

        Args:
            current_density_si: j in A/m²
            active_area_si:     A in m²
        """
        current_a = current_density_si * active_area_si
        n_dot = self.faraday_efficiency * current_a / (N_ELECTRONS_H2O * F)
        m_dot_kg_s = n_dot * M_H2

        return {
            "current_a": current_a,
            "n_dot_mol_per_s": n_dot,
            "m_dot_kg_per_s": m_dot_kg_s,
            "m_dot_g_per_h": m_dot_kg_s * 3600.0 * 1000.0,
            # Volumetric at STP (not operating conditions): sanity-check number
            "v_dot_nm3_per_h": n_dot * 3600.0 * 22.414e-3,  # normal m³/h
        }

    # -------------------- Polarization curve -------------------- #

    def polarization_curve(
        self,
        current_densities_si: np.ndarray,
        include_concentration: bool = True,
        j_limiting_si: float = 30_000.0,
    ) -> dict[str, np.ndarray]:
        """
        Vectorized polarization curve. Input and output in SI.

        Returns arrays with same shape as input:
            current_density, u_cell, eta_act_total, eta_ohm, eta_conc, eta_energy
        """
        j = np.asarray(current_densities_si, dtype=float)
        u = np.empty_like(j)
        eta_act = np.empty_like(j)
        eta_ohm = np.empty_like(j)
        eta_conc = np.empty_like(j)
        eta_energy = np.empty_like(j)

        for i, ji in enumerate(j):
            v = self.cell_voltage(ji, include_concentration, j_limiting_si)
            e = self.efficiency(ji)
            u[i] = v["u_cell"]
            eta_act[i] = v["eta_act_total"]
            eta_ohm[i] = v["eta_ohm"]
            eta_conc[i] = v["eta_conc"]
            eta_energy[i] = e["eta_energy"]

        return {
            "current_density_si": j,
            "u_cell": u,
            "eta_act_total": eta_act,
            "eta_ohm": eta_ohm,
            "eta_conc": eta_conc,
            "eta_energy": eta_energy,
        }


# -------------------- Module self-test -------------------- #

if __name__ == "__main__":
    cell = Electrochemistry.from_engineering(temperature_celsius=80.0, pressure_bar=10.0)
    j_si = U.a_per_cm2_to_a_per_m2(1.0)  # 1 A/cm² → 10,000 A/m²
    v = cell.cell_voltage(j_si)
    e = cell.efficiency(j_si)
    print(f"U_cell at 1 A/cm²: {v['u_cell']:.3f} V")
    print(f"  E_rev:           {v['e_rev']:.3f} V")
    print(f"  eta_act_anode:   {v['eta_act_anode']:.3f} V")
    print(f"  eta_act_cathode: {v['eta_act_cathode']:.3f} V")
    print(f"  eta_ohm:         {v['eta_ohm']:.3f} V")
    print(f"  eta_conc:        {v['eta_conc']:.3f} V")
    print(f"Energy efficiency: {e['eta_energy'] * 100:.1f} %")
    print(f"Specific energy:   {e['specific_energy_kwh_kg']:.1f} kWh/kg H2")
