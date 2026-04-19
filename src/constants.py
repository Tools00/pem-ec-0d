"""
Physical constants — CODATA 2018 recommended values.

All units are SI. Do not redefine these constants anywhere else in the codebase.
If a constant is not here, do not hardcode it — add it.

@ref: CODATA recommended values of the fundamental physical constants (2018)
      Tiesinga, E., Mohr, P. J., Newell, D. B., & Taylor, B. N. (2021).
      Reviews of Modern Physics, 93(2), 025010.
"""

# Fundamental constants (CODATA 2018)
R: float = 8.314_462_618  # J/(mol·K) — Universal gas constant
F: float = 96_485.332_12  # C/mol — Faraday constant
N_A: float = 6.022_140_76e23  # 1/mol — Avogadro constant

# Thermodynamic reference
T_STANDARD: float = 298.15  # K — 25 °C reference temperature
T_ZERO_CELSIUS: float = 273.15  # K
P_STANDARD: float = 101_325.0  # Pa — 1 atm reference pressure
P_BAR: float = 100_000.0  # Pa — 1 bar
V_MOLAR_STP: float = 22.413_969_54e-3  # m³/mol — molar volume at STP (273.15 K, 101.325 kPa)

# Water electrolysis standard cell potential
# 2 H2O → 2 H2 + O2 at 298.15 K, 101.325 kPa, liquid water
E0_H2O: float = 1.229  # V — reversible cell voltage at standard conditions
#   @ref: Bard, A. J., Parsons, R., & Jordan, J. (1985).
#         Standard Potentials in Aqueous Solution. IUPAC.

# Temperature coefficient of E0 for H2O electrolysis
# dE0/dT ≈ -0.846 mV/K (liquid water product)
DE0_DT: float = -8.46e-4  # V/K
#   @ref: Larminie, J., & Dicks, A. (2003). Fuel Cell Systems Explained. Wiley.

# Molar masses (kg/mol) — IUPAC 2021 atomic weights
M_H2: float = 2.015_88e-3  # kg/mol
M_O2: float = 31.998_0e-3  # kg/mol
M_H2O: float = 18.015_28e-3  # kg/mol

# Thermodynamic data for H2O electrolysis (at 298.15 K, liquid water)
DELTA_H_H2O: float = 285.83e3  # J/mol — higher heating value (HHV) of H2
DELTA_G_H2O: float = 237.13e3  # J/mol — Gibbs free energy change
LHV_H2: float = 241.82e3  # J/mol — lower heating value of H2 (gas products)

# Number of electrons in half-reactions
N_ELECTRONS_H2O: int = 2  # electrons per H2 molecule produced
