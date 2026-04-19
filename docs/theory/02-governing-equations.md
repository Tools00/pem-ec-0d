# PEM Electrolysis - Governing Equations

## Table of Contents
- [Electrochemical Equations](#electrochemical-equations)
- [Mass Transport](#mass-transport)
- [Heat Transfer](#heat-transfer)
- [Fluid Dynamics](#fluid-dynamics)
- [Coupled Multi-Physics](#coupled-multi-physics)

---

## Electrochemical Equations

### Butler-Volmer Equation

The fundamental equation describing electrode kinetics:

```
j = j₀ · [exp(αₐ·F·η/(R·T)) - exp(-α꜀·F·η/(R·T))]
```

**Where:**
- j = current density [A/m²]
- j₀ = exchange current density [A/m²]
- αₐ = anodic transfer coefficient (0.5-0.7)
- α꜀ = cathodic transfer coefficient (0.5-0.7)
- η = overpotential [V] = E - E_eq
- F = 96,485 C/mol (Faraday constant)
- R = 8.314 J/(mol·K) (gas constant)
- T = temperature [K]

### Simplified Forms

**High Overpotential (Tafel Region):**

For η > 50 mV (anodic):
```
j ≈ j₀ · exp(αₐ·F·η/(R·T))
η = (RT/αₐF) · ln(j/j₀)
```

The term (RT/αF) is called the **Tafel slope**:
```
b = (RT/αF) · ln(10) ≈ 2.303·RT/αF
```

At 80°C with α = 0.5:
```
b ≈ 60 mV/decade
```

**Low Overpotential (Linear Region):**

For η < 10 mV:
```
j ≈ j₀ · (F·η/(R·T))
η ≈ (RT/F) · (j/j₀)
```

---

### Activation Overpotential

**For Anode (OER):**
```
η_act,anode = (RT/αₐF) · asinh(j/(2·j₀,anode))
```

Using typical values:
- j₀,anode ≈ 10⁻⁵ - 10⁻⁴ A/cm² (IrO₂)
- αₐ ≈ 0.5

**For Cathode (HER):**
```
η_act,cathode = (RT/α꜀F) · asinh(j/(2·j₀,cathode))
```

Using typical values:
- j₀,cathode ≈ 10⁻³ - 10⁻² A/cm² (Pt/C)
- α꜀ ≈ 0.5

**Temperature Dependence of j₀:**
```
j₀(T) = j₀,ref · exp(-Eₐ/R · (1/T - 1/T_ref))
```

Eₐ for OER on IrO₂: ~50-70 kJ/mol

---

### Ohmic Losses

**Membrane Resistance:**
```
R_mem = t_mem / σ_mem
σ_mem = σ₀ · exp(-Eₐ/(R·T)) · f(λ)
```

**Where:**
- t_mem = membrane thickness [m]
- σ_mem = membrane conductivity [S/m]
- λ = water content (14-22 for Nafion)

**Nafion Conductivity Model:**
```
σ = (0.005139·λ - 0.00326) · exp[1268·(1/303 - 1/T)]
```

Valid for:
- λ: 5-22
- T: 303-353 K
- σ: S/cm

**Other Ohmic Components:**

GDL resistance:
```
R_GDL = t_GDL / (σ_GDL · ε/τ)
```

Contact resistance:
```
R_contact ≈ 0.01-0.1 Ω·cm² (depends on clamping pressure)
```

Bipolar plate resistance:
```
R_bpp = t_bpp / σ_bpp
```

**Total Ohmic Loss:**
```
η_ohm = j · (R_mem + R_GDL,anode + R_GDL,cathode + R_bpp + R_contact)
```

---

### Concentration Overpotential

**Due to Mass Transport Limitations:**

```
η_conc = (RT/nF) · ln(1 - j/j_L)
```

**Where:**
- j_L = limiting current density [A/m²]
- n = number of electrons (2 for H₂, 4 for O₂)

**Limiting Current Density:**
```
j_L = n·F·D_eff·C_bulk / δ
```

- D_eff = effective diffusivity [m²/s]
- C_bulk = bulk concentration [mol/m³]
- δ = diffusion layer thickness [m]

**For Porous Electrodes (Bruggeman Correction):**
```
D_eff = D · ε^1.5
```

- ε = porosity (0.6-0.8 for GDL)

---

## Cell Voltage Model

### Complete Equation

```
U_cell = E_rev + η_act,anode + η_act,cathode + η_ohm + η_conc,anode + η_conc,cathode
```

### Expanded Form

```
U_cell = E_rev
       + (RT/αₐ,anode·F)·asinh(j/(2·j₀,anode))
       + (RT/αₐ,cathode·F)·asinh(j/(2·j₀,cathode))
       + j·(t_mem/σ_mem + ΣR_other)
       + (RT/2F)·ln(1 - j/j_L,anode)
       + (RT/2F)·ln(1 - j/j_L,cathode)
```

---

## Mass Transport

### Water Transport

**Electro-osmotic Drag:**
Water molecules are dragged with protons through the membrane.

```
N_eod = n_d · (I/F)
```

- n_d = electro-osmotic drag coefficient (2-3 for Nafion)
- I = current [A]

**Back Diffusion:**
Water diffuses from cathode to anode due to concentration gradient.

```
N_diff = -D_w · (dc/dx)
```

- D_w = water diffusion coefficient in membrane [m²/s]
- dc/dx = concentration gradient

**Net Water Transport:**
```
N_net = N_eod - N_diff
```

**Water Flux Through Membrane:**
```
J_H₂O = (n_d·I/F) - (D_w·ΔC/t_mem)
```

---

### Gas Transport in GDL

**Fick's Law (Binary Diffusion):**
```
N_i = -D_ij · (dc_i/dx)
```

**For Porous Media (Stefan-Maxwell):**
```
∇x_i = Σ(x_i·N_j - x_j·N_i) / (c·D_ij,eff)
```

**Effective Diffusivity:**
```
D_eff = D · (ε/τ)
τ = ε^(-0.5)  (Bruggeman approximation)
```

**Typical Values:**

| Species | D in air [cm²/s] | D in GDL [cm²/s] |
|---------|------------------|------------------|
| H₂      | 0.61             | 0.02-0.05        |
| O₂      | 0.20             | 0.008-0.015      |
| H₂O     | 0.24             | 0.01-0.02        |

---

### Two-Phase Flow Equations

**Gas Saturation:**
```
S_g = V_gas / V_pore
S_l = 1 - S_g
```

**Capillary Pressure (Young-Laplace):**
```
p_c = p_g - p_l = (2·σ·cosθ) / r
```

- σ = surface tension [N/m]
- θ = contact angle [°]
- r = pore radius [m]

**Leverett J-Function (Empirical for GDL):**
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

**Relative Permeability:**
```
k_rl = S³    (liquid)
k_rg = (1-S)³  (gas)
```

---

### Species Conservation

**General Transport Equation:**
```
∂(ε·c_i)/∂t + ∇·(u·c_i) = ∇·(D_eff·∇c_i) + R_i
```

**For Each Species:**

**Hydrogen (cathode):**
```
∂(ε·c_H₂)/∂t + ∇·(u·c_H₂) = ∇·(D_H₂,eff·∇c_H₂) + S_H₂
```

Source term:
```
S_H₂ = j/(2·F)  (production at catalyst)
```

**Oxygen (anode):**
```
∂(ε·c_O₂)/∂t + ∇·(u·c_O₂) = ∇·(D_O₂,eff·∇c_O₂) + S_O₂
```

Source term:
```
S_O₂ = j/(4·F)  (production at catalyst)
```

**Water:**
```
∂(ε·c_H₂O)/∂t + ∇·(u·c_H₂O) = ∇·(D_H₂O,eff·∇c_H₂O) + S_H₂O
```

Source/sink terms:
- Anode: -j/(2F) (consumption) + electro-osmotic drag
- Cathode: +j/(2F) (production)

---

## Heat Transfer

### Energy Equation

**General Form (with convection):**
```
ρ·C_p·(∂T/∂t + u·∇T) = ∇·(k·∇T) + Q_gen
```

**Where:**
- ρ = density [kg/m³]
- C_p = specific heat capacity [J/(kg·K)]
- k = thermal conductivity [W/(m·K)]
- Q_gen = volumetric heat generation [W/m³]

### Heat Generation Sources

**Irreversible Heat (Activation + Ohmic):**
```
Q_irr = j·(U_cell - E_rev)
```

**Reversible Heat (Entropy Change):**
```
Q_rev = j·T·(dE_rev/dT)
dE_rev/dT ≈ -0.846 mV/K
```

**Joule Heating:**
```
Q_joule = j²·ρ_e
```

- ρ_e = electrical resistivity [Ω·m]

**Total Heat Generation in MEA:**
```
Q_total = j·(U_cell - E_rev - T·dE_rev/dT)
```

Simplified (most models neglect reversible heat):
```
Q_total ≈ j·(U_cell - 1.23)
```

### Heat Transfer in Different Regions

**Solid Regions (Bipolar Plates, GDL):**
```
ρ_s·C_p,s·∂T/∂t = ∇·(k_s·∇T)
```

**Porous Media (GDL with fluid):**
```
(ρ·C_p)_eff·∂T/∂t = ∇·(k_eff·∇T) + (ρ·C_p)_f·u·∇T
```

Effective properties:
```
(ρ·C_p)_eff = ε·(ρ·C_p)_f + (1-ε)·(ρ·C_p)_s
k_eff = ε·k_f + (1-ε)·k_s
```

**Fluid Regions (Channels):**
```
ρ_f·C_p,f·(∂T/∂t + u·∇T) = ∇·(k_f·∇T)
```

### Boundary Conditions

**Dirichlet (Fixed Temperature):**
```
T = T₀  (at boundary)
```

**Neumann (Fixed Heat Flux):**
```
-k·(∂T/∂n) = q''
```

**Convective Cooling:**
```
-k·(∂T/∂n) = h·(T_s - T_∞)
```

- h = heat transfer coefficient [W/(m²·K)]
- T_s = surface temperature
- T_∞ = coolant temperature

**Typical h values:**
- Natural convection (air): 5-25 W/(m²·K)
- Forced convection (water): 500-10,000 W/(m²·K)
- Flow in channels: 100-2000 W/(m²·K)

---

## Fluid Dynamics

### Continuity Equation

**Incompressible Flow:**
```
∇·u = 0
```

**Compressible Flow:**
```
∂ρ/∂t + ∇·(ρ·u) = 0
```

### Navier-Stokes Equations

**Momentum Conservation:**
```
ρ·(∂u/∂t + u·∇u) = -∇p + μ·∇²u + F
```

**Where:**
- u = velocity vector [m/s]
- p = pressure [Pa]
- μ = dynamic viscosity [Pa·s]
- F = body forces [N/m³]

### Flow in Porous Media (Darcy's Law)

**Darcy's Law (Low Reynolds Number):**
```
u = -(K/μ)·∇p
```

- K = permeability [m²]
- μ = viscosity [Pa·s]

**For GDL:**
```
K ≈ 10⁻¹² - 10⁻¹¹ m² (through-plane)
K ≈ 10⁻¹¹ - 10⁻¹⁰ m² (in-plane)
```

**Brinkman Equation (Transition Region):**
```
μ_eff·∇²u - (μ/K)·u - ∇p = 0
```

**Forchheimer Equation (Higher Velocity):**
```
-∇p = (μ/K)·u + (ρ·C_F/√K)·|u|·u
```

- C_F = Forchheimer coefficient (~0.55)

### Pressure Drop in Channels

**Laminar Flow (Re < 2300):**

Circular pipe (Hagen-Poiseuille):
```
Δp = (128·μ·L·Q) / (π·D⁴)
```

Rectangular channel:
```
Δp = f·(L/D_h)·(ρ·u²/2)
f = 64/Re  (for circular)
```

**Hydraulic Diameter:**
```
D_h = 4·A/P
```

- A = cross-sectional area
- P = wetted perimeter

---

## Coupled Multi-Physics

### Conservation Equations Summary

**Mass:**
```
∂ρ/∂t + ∇·(ρ·u) = 0
```

**Momentum:**
```
ρ·(∂u/∂t + u·∇u) = -∇p + ∇·τ + F
```

**Species:**
```
∂(ρ·Y_i)/∂t + ∇·(ρ·u·Y_i) = -∇·J_i + R_i
```

**Energy:**
```
ρ·C_p·(∂T/∂t + u·∇T) = ∇·(k·∇T) + Φ + Q_rxn
```

**Charge (Electronic):**
```
∇·(σ_s·∇φ_s) = 0
```

**Charge (Ionic in Membrane):**
```
∇·(σ_m·∇φ_m) = 0
```

## 