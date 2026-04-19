# PEM Electrolysis - Complete Theory Reference

## 📖 Purpose

This document contains **all theoretical foundations** for the PEM Electrolysis Simulator. It serves as:
- Reference for implementation
- Validation source
- Educational resource
- Citation repository

**Last Updated:** 2026-04-07  
**Version:** 1.0  
**Status:** Living document (continuously updated)

---

## Table of Contents

1. [Chemical Reactions & Thermodynamics](#1-chemical-reactions--thermodynamics)
2. [Electrochemical Kinetics](#2-electrochemical-kinetics)
3. [Transport Phenomena](#3-transport-phenomena)
4. [Mass & Energy Conservation](#4-mass--energy-conservation)
5. [Two-Phase Flow](#5-two-phase-flow)
6. [Heat Transfer](#6-heat-transfer)
7. [Mass Transport in Porous Media](#7-mass-transport-in-porous-media)
8. [Degradation Models](#8-degradation-models)
9. [Safety & Limits](#9-safety--limits)
10. [Cost Models](#10-cost-models)

---

## 1. Chemical Reactions & Thermodynamics

### 1.1 Overall Reaction

```
2H₂O(l) → 2H₂(g) + O₂(g)
```

**Stoichiometry:**
- 2 moles H₂O → 2 moles H₂ + 1 mole O₂
- 4 electrons transferred per H₂ molecule

### 1.2 Half-Reactions

**Anode (Oxidation - OER):**
```
2H₂O → O₂ + 4H⁺ + 4e⁻
E°_anode = +1.23 V vs SHE (at 25°C)
```

**Cathode (Reduction - HER):**
```
4H⁺ + 4e⁻ → 2H₂
E°_cathode = 0 V vs SHE
```

### 1.3 Thermodynamic Parameters (25°C, 1 atm)

| Parameter | Symbol | Value | Unit |
|-----------|--------|-------|------|
| Enthalpy change | ΔH° | +285.8 | kJ/mol |
| Gibbs free energy | ΔG° | +237.1 | kJ/mol |
| Entropy change | ΔS° | +163 | J/(mol·K) |
| Entropy term | T·ΔS° | +48.7 | kJ/mol |

### 1.4 Reversible Voltage (Nernst Equation)

**General Form:**
```
E_rev = E° + (RT/nF)·ln(a_H₂O / (a_H₂ · a_O₂^0.5))
```

**Simplified (ideal gases, liquid water):**
```
E_rev = 1.23 - 8.46×10⁻⁴·(T - 298.15) + (RT/2F)·ln(p_H₂) + (RT/4F)·ln(p_O₂^0.5)
```

**Temperature Dependence:**
```
dE_rev/dT ≈ -0.846 mV/K
```

**Pressure Dependence:**
```
E_rev(p) = E_rev(1 atm) + (RT/2F)·ln(p_H₂) + (RT/4F)·ln(p_O₂)
```

**Example Calculations:**

| T [°C] | p [bar] | E_rev [V] |
|--------|---------|-----------|
| 25     | 1       | 1.23      |
| 50     | 1       | 1.21      |
| 80     | 1       | 1.19      |
| 80     | 30      | 1.24      |

### 1.5 Efficiency Definitions

**Voltage Efficiency:**
```
η_V = E_rev / U_cell
```

**Faraday Efficiency:**
```
η_F = (actual H₂ produced) / (theoretical H₂)
Typical: 95-99%
```

**Energy Efficiency (LHV-based):**
```
η_energy = η_V · η_F · (LHV_H₂ / ΔH)
LHV_H₂ = 241.8 kJ/mol = 119.9 MJ/kg
```

**Practical Values:**
- At U_cell = 1.8 V: η ≈ 75%
- At U_cell = 2.0 V: η ≈ 68%
- At U_cell = 2.2 V: η ≈ 62%

### 1.6 Specific Energy Consumption

**Theoretical Minimum:**
```
E_specific,theoretical = ΔG / (2·F·M_H₂) = 33 kWh/kg H₂
```

**Practical:**
```
E_specific = U_cell · (2·F) / (η_F · M_H₂ · 3600)
           ≈ 50-55 kWh/kg H₂ (typical)
```

---

## 2. Electrochemical Kinetics

### 2.1 Butler-Volmer Equation

**Fundamental Kinetic Equation:**
```
j = j₀ · [exp(αₐ·F·η/(R·T)) - exp(-α꜀·F·η/(R·T))]
```

**Parameters:**

| Symbol | Meaning | Typical Range | Unit |
|--------|---------|---------------|------|
| j | Current density | 0.1-3.0 | A/cm² |
| j₀ | Exchange current density | 10⁻⁶-10⁻² | A/cm² |
| αₐ | Anodic transfer coefficient | 0.5-0.7 | - |
| α꜀ | Cathodic transfer coefficient | 0.5-0.7 | - |
| η | Overpotential | 0.1-0.5 | V |
| F | Faraday constant | 96485 | C/mol |
| R | Gas constant | 8.314 | J/(mol·K) |
| T | Temperature | 323-353 | K |

### 2.2 Simplified Forms

**Tafel Approximation (High Overpotential, η > 50 mV):**

Anodic:
```
j ≈ j₀ · exp(αₐ·F·η/(R·T))
η = (RT/αₐF) · ln(j/j₀)
```

Cathodic:
```
j ≈ -j₀ · exp(-α꜀·F·η/(R·T))
```

**Linear Approximation (Low Overpotential, η < 10 mV):**
```
j ≈ j₀ · (F·η/(R·T))
η ≈ (RT/F) · (j/j₀)
```

### 2.3 Tafel Slope

**Definition:**
```
b = (2.303·RT) / (α·F)
```

**At 80°C (353 K):**
- α = 0.5: b ≈ 63 mV/decade
- α = 0.7: b ≈ 45 mV/decade

**Typical Values for PEM Electrolysis:**
- Anode (IrO₂): b = 40-60 mV/dec
- Cathode (Pt/C): b = 30-40 mV/dec

### 2.4 Activation Overpotential

**Anode (OER):**
```
η_act,anode = (RT/αₐ,anode·F) · asinh(j/(2·j₀,anode))
```

Typical: 0.2-0.4 V at 1 A/cm²

**Cathode (HER):**
```
η_act,cathode = (RT/αₐ,cathode·F) · asinh(j/(2·j₀,cathode))
```

Typical: 0.05-0.1 V at 1 A/cm²

**Temperature Dependence:**
```
j₀(T) = j₀,ref · exp(-Eₐ/R · (1/T - 1/T_ref))
```

For IrO₂: Eₐ ≈ 50-70 kJ/mol  
For Pt/C: Eₐ ≈ 20-30 kJ/mol

### 2.5 Ohmic Losses

**Membrane Resistance:**
```
R_mem = t_mem / σ_mem
```

**Nafion Conductivity Model (Springer et al.):**
```
σ_mem = (0.005139·λ - 0.00326) · exp[1268·(1/303 - 1/T)]
```

Valid for:
- λ (water content): 5-22
- T: 303-353 K
- σ in S/cm

**Other Resistances:**

GDL:
```
R_GDL = t_GDL / (σ_GDL · ε/τ)
```

Contact:
```
R_contact ≈ 0.01-0.1 Ω·cm²
Depends on clamping pressure
```

Bipolar Plate:
```
R_bpp = t_bpp / σ_bpp
```

**Total Ohmic Loss:**
```
η_ohm = j · (R_mem + R_GDL,anode + R_GDL,cathode + R_bpp + R_contact)
```

Typical: 0.1-0.3 V at 1 A/cm²

### 2.6 Concentration Overpotential

**Due to Mass Transport Limitation:**
```
η_conc = (RT/nF) · ln(1 - j/j_L)
```

**Limiting Current Density:**
```
j_L = n·F·D_eff·C_bulk / δ
```

For porous electrodes:
```
D_eff = D · ε^1.5  (Bruggeman correction)
```

**Typical Values:**
- j_L,anode: 2-5 A/cm²
- j_L,cathode: 3-8 A/cm²

---

## 3. Transport Phenomena

### 3.1 Water Transport

**Electro-Osmotic Drag (EOD):**
```
N_eod = n_d · (I/F)
```

n_d (drag coefficient):
- Fully hydrated: 2.5-3
- Low hydration: 1.5-2

**Back Diffusion:**
```
N_diff = -D_w · (dc/dx) ≈ D_w · (C_cathode - C_anode) / t_mem
```

D_w in Nafion: 2-5 × 10⁻¹⁰ m²/s at 80°C

**Net Water Transport:**
```
N_net = N_eod - N_diff
```

**Water Balance at Anode:**
```
Water_in - Water_consumed - Water_eod + Water_diff = Water_out
```

**Stoichiometric Ratio:**
```
λ_stoich = Water_supplied / Water_consumed
Typical: 5-20
```

### 3.2 Gas Transport in GDL

**Effective Diffusivity:**
```
D_eff = D · (ε/τ)
τ = ε^(-0.5)  (Bruggeman approximation)
```

**Typical Values:**

| Gas | D in air [cm²/s] | D in GDL [cm²/s] |
|-----|------------------|------------------|
| H₂  | 0.61             | 0.02-0.05        |
| O₂  | 0.20             | 0.008-0.015      |
| H₂O | 0.24             | 0.01-0.02        |

### 3.3 Species Conservation

**General Transport Equation:**
```
∂(ε·c_i)/∂t + ∇·(u·c_i) = ∇·(D_eff·∇c_i) + R_i
```

**Source Terms:**

Anode:
```
S_H₂O = -j/(2F)  (consumption)
S_O₂ = j/(4F)    (production)
```

Cathode:
```
S_H₂ = j/(2F)    (production)
```

---

## 4. Mass & Energy Conservation

### 4.1 Mass Conservation

**Continuity Equation:**
```
∂ρ/∂t + ∇·(ρ·u) = 0
```

For incompressible flow:
```
∇·u = 0
```

### 4.2 Momentum Conservation

**Navier-Stokes:**
```
ρ·(∂u/∂t + u·∇u) = -∇p + μ·∇²u + F
```

**In Porous Media (Darcy's Law):**
```
u = -(K/μ)·∇p
```

**Brinkman Equation (Transition):**
```
μ_eff·∇²u - (μ/K)·u - ∇p = 0
```

### 4.3 Energy Conservation

**General Form:**
```
ρ·C_p·(∂T/∂t + u·∇T) = ∇·(k·∇T) + Q_gen
```

**Heat Generation:**
```
Q_gen = j·(U_cell - E_rev - T·dE_rev/dT)
```

Simplified:
```
Q_gen ≈ j·(U_cell - 1.23)  [W/m²]
```

**Effective Properties (Porous Media):**
```
(ρ·C_p)_eff = ε·(ρ·C_p)_fluid + (1-ε)·(ρ·C_p)_solid
k_eff = ε·k_fluid + (1-ε)·k_solid
```

---

## 5. Two-Phase Flow

### 5.1 Gas Saturation

**Definition:**
```
S_g = V_gas / V_pore
S_l = 1 - S_g
```

### 5.2 Capillary Pressure

**Young-Laplace:**
```
p_c = p_g - p_l = (2·σ·cosθ) / r
```

**Leverett J-Function:**
```
p_c(S) = σ·√(ε/K)·J(S)
```

For hydrophobic GDL (θ > 90°):
```
J(S) = 1.417·(1-S) - 2.120·(1-S)² + 1.263·(1-S)³
```

For hydrophilic GDL (θ < 90°):
```
J(S) = 1.417·S - 2.120·S² + 1.263·S³
```

### 5.3 Relative Permeability

**Common Model:**
```
k_rl = S³
k_rg = (1-S)³
```

**Alternative (Brooks-Corey):**
```
k_rl = S^((2+3λ)/λ)
k_rg = (1-S)²·(1 - S^((2+λ)/λ))
```

λ = pore size distribution index (2-4)

### 5.4 Flow Regimes

**Reynolds Number:**
```
Re = ρ·u·D_h / μ
```

- Re < 2300: Laminar
- Re > 4000: Turbulent
- Typical in PEM: 50-500 (laminar)

---

## 6. Heat Transfer

### 6.1 Heat Generation Sources

**Irreversible Heat:**
```
Q_irr = j·(U_cell - E_rev)
```

**Reversible Heat:**
```
Q_rev = j·T·(dE_rev/dT)
dE_rev/dT ≈ -0.846 mV/K
```

**Joule Heating:**
```
Q_joule = j²·ρ_e
```

**Total:**
```
Q_total = Q_irr + Q_rev + Q_joule
```

### 6.2 Boundary Conditions

**Dirichlet (Fixed T):**
```
T = T₀ at boundary
```

**Neumann (Fixed Flux):**
```
-k·(∂T/∂n) = q''
```

**Convective:**
```
-k·(∂T/∂n) = h·(T_s - T_∞)
```

Typical h values:
- Natural convection: 5-25 W/(m²·K)
- Forced water: 500-10000 W/(m²·K)
- Flow channels: 100-2000 W/(m²·K)

---

## 7. Mass Transport in Porous Media

### 7.1 Darcy's Law

**Basic Form:**
```
u = -(K/μ)·∇p
```

**Permeability:**
- GDL through-plane: 10⁻¹³ - 10⁻¹² m²
- GDL in-plane: 10⁻¹² - 10⁻¹¹ m²

### 7.2 Forchheimer Extension (High Velocity)

```
-∇p = (μ/K)·u + (ρ·C_F/√K)·|u|·u
```

C_F ≈ 0.55 (Forchheimer coefficient)

---

## 8. Degradation Models

### 8.1 Voltage Degradation

**Empirical Model:**
```
U(t) = U₀ + a·t + b·√t
```

- a: linear degradation rate (5-15 µV/h)
- b: square-root term (initial break-in)

### 8.2 ECSA Loss

**Electrochemical Surface Area:**
```
ECSA(t) = ECSA₀ · (1 - β·t^n)
```

Typical:
- β ≈ 10⁻⁶ h⁻ⁿ
- n ≈ 0.6

### 8.3 Membrane Thinning

```
d(t) = d₀ - k_deg·t
```

k_deg ≈ 10⁻¹² m/h

**Crossover Increase:**
```
J_H₂,cross(t) = J₀ · exp(k_cross·t)
```

Safety limit: J_H₂ < 4 Vol% in O₂

---

## 9. Safety & Limits

### 9.1 Gas Crossover

**H₂ in O₂:**
- Normal: < 2 Vol%
- Warning: 2-4 Vol%
- Critical: > 4 Vol% (explosion risk!)

**Explosion Limits:**
- H₂ in air: 4-75 Vol%
- H₂ in O₂: 4-95 Vol%

### 9.2 Temperature Limits

**Nafion:**
- Maximum: 90°C
- Optimal: 60-80°C
- Minimum: 20°C (startup)

### 9.3 Pressure Limits

**Typical:**
- Anode: 10-30 bar
- Cathode: 10-30 bar
- Differential: < 2 bar

---

## 10. Cost Models

### 10.1 Material Costs

**Catalyst:**
```
Cost_catalyst = Loading × Area × Price
```

Example:
- Ir loading: 2 mg/cm²
- Price: 150 €/g
- Area: 100 cm²
- Cost: 2 × 10⁻³ × 100 × 150 = 30 €

### 10.2 Manufacturing Costs

**Empirical:**
```
Cost_manufacturing = 50 + 0.5 × Area × N_cells  [€]
```

### 10.3 Total Stack Cost

```
Cost_stack = Cost_materials + Cost_manufacturing
Cost_per_kW = Cost_stack / Power_kW
```

Target (DOE 2025): < 200 €/kW

---

## 📚 References

### Key Papers

1. **Carmo, M. et al.** "A comprehensive review on PEM water electrolysis." *Int J Hydrogen Energy* 38.12 (2013): 4901-4934.

2. **Grigoriev, S.A. et al.** "Current achievements and future prospects of PEM water electrolysis." *Int J Hydrogen Energy* (2020).

3. **Springer, T.E. et al.** "Polymer Electrolyte Fuel Cell Model." *J. Electrochem. Soc.* 138.8 (1991): 2334-2342.

### Standards

- ISO 22734:2019 - Hydrogen generators using water electrolysis
- ASME BPVC - Boiler and Pressure Vessel Code
- UL 2264 - Standard for Stationary Fuel Cell Power Systems

### Books

- **Barbir, F.** "PEM Electrolysis: Theory, Design, and Applications." Academic Press, 2013.
- **O'Hayre, R. et al.** "Fuel Cell Fundamentals." Wiley, 2016.

---

## 📝 Notes for Implementation

### Priority Order

1. **Butler-Volmer + Ohmic** (core performance)
2. **Water balance** (critical for operation)
3. **Thermal model** (for safety/optimization)
4. **Degradation** (for lifetime prediction)
5. **Cost model** (for economic analysis)

### Simplifications for v1.0

- Use Tafel approximation (skip full BV)
- Assume constant Faraday efficiency (98%)
- 1D models first (no 2D/3D CFD)
- Look-up tables for properties (σ(T,λ))

### Validation Targets

- Polarization curves (compare to literature)
- H₂ production rate (Faraday's law)
- Temperature rise (energy balance)
- Efficiency (65-80% range)

---

**This document is continuously updated. Last review: 2026-04-07**
