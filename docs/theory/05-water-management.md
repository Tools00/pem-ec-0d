# PEM Electrolysis - Water Management

## Table of Contents
- [Water Transport Mechanisms](#water-transport-mechanisms)
- [Two-Phase Flow](#two-phase-flow)
- [Capillary Pressure & Porous Media](#capillary-pressure--porous-media)
- [Gas Diffusion Layer Management](#gas-diffusion-layer-management)
- [Water Supply Strategy](#water-supply-strategy)
- [Flooding & Drying](#flooding--drying)
- [Modeling Approaches](#modeling-approaches)

---

## Water Transport Mechanisms

Water management is **critical** for PEM electrolysis performance and lifetime. Poor water management leads to:
- **Drying out** → membrane conductivity loss → hot spots
- **Flooding** → gas transport blockage → voltage increase
- **Poor performance** → reduced efficiency

---

### 1. Electro-Osmotic Drag (EOD)

Protons crossing the membrane drag water molecules with them.

**EOD Flux:**
```
N_eod = n_d · (I / F)
```

**Where:**
- n_d = electro-osmotic drag coefficient (2-3 for Nafion)
- I = current [A]
- F = 96,485 C/mol

**Water Molecules per Proton:**
- Fully hydrated: n_d ≈ 2.5-3
- Low hydration: n_d ≈ 1.5-2

**Example at 1 A/cm², 100 cm²:**
```
I = 100 A
N_eod = 2.5 × (100 / 96485) ≈ 2.6 × 10⁻³ mol/s
ṁ = 0.047 g/s = 2.8 ml/min
```

---

### 2. Back Diffusion

Water diffuses back from cathode to anode due to concentration gradient.

**Fick's Law:**
```
N_diff = -D_w · (dc/dx) = D_w · (C_c - C_a) / t_mem
```

**Where:**
- D_w = water diffusion coefficient in membrane [m²/s]
- C_c, C_a = water concentration at cathode/anode
- t_mem = membrane thickness [m]

**Diffusion Coefficient:**
```
D_w = D_0 · exp(-E_a / RT)
```

For Nafion:
- D_w ≈ 2-5 × 10⁻¹⁰ m²/s at 80°C

---

### 3. Net Water Transport

**Overall Water Flux:**
```
N_net = N_eod - N_diff
```

**Water Balance at Anode:**
```
Water_in - Water_consumed - Water_eod + Water_diff = Water_out
```

**Water Consumption (Reaction):**
```
N_rxn = I / (2F)
```

**Typical Ratio:**
```
N_eod / N_rxn = 2·n_d ≈ 5
```

This means **5x more water is dragged** than consumed by reaction!

---

## Two-Phase Flow

### Gas Evolution at Electrodes

**Anode (Oxygen):**
```
2H₂O → O₂ + 4H⁺ + 4e⁻
```

Molar production:
```
ṅ_O₂ = I / (4F)
```

**Cathode (Hydrogen):**
```
4H⁺ + 4e⁻ → 2H₂
```

Molar production:
```
ṅ_H₂ = I / (2F)
```

**Volume Generation Rate:**
```
Q_gas = ṅ · (RT/P)
```

At 1 A/cm²:
- O₂: 0.0032 L/min per cm²
- H₂: 0.0064 L/min per cm²

---

### Flow Regimes

**In Channels:**

1. **Bubble Flow:** Small bubbles dispersed in liquid
2. **Slug Flow:** Large gas slugs
3. **Stratified Flow:** Gas on top, liquid below
4. **Annular Flow:** Gas core, liquid film on walls

**Characterization (Reynolds Number):**
```
Re = ρ·u·D_h / μ
```

- Re < 2300: Laminar
- Re > 4000: Turbulent
- Typical in channels: Re = 50-500 (laminar)

---

### Void Fraction

**Gas Volume Fraction:**
```
α = V_gas / (V_gas + V_liquid)
```

**Homogeneous Model:**
```
α = 1 / [1 + (1-x)·(ρ_g/ρ_l)]
```

- x = quality (mass fraction of gas)
- ρ_g, ρ_l = gas/liquid density

**Typical Values:**
- Low current: α < 10%
- High current: α = 30-50%
- At outlet: α can reach 80%

---

## Capillary Pressure & Porous Media

### Young-Laplace Equation

**Capillary Pressure in Pores:**
```
p_c = p_g - p_l = (2·σ·cosθ) / r
```

**Where:**
- σ = surface tension [N/m] (0.072 for water/air at 20°C)
- θ = contact angle [°]
- r = pore radius [m]

**Implications:**
- Smaller pores → higher capillary pressure
- Hydrophobic (θ > 90°) → cosθ < 0 → gas prefers pores
- Hydrophilic (θ < 90°) → cosθ > 0 → liquid prefers pores

---

### Leverett J-Function

**Empirical Relationship for GDL:**
```
p_c(S) = σ·√(ε/K)·J(S)
```

**Where:**
- S = liquid saturation (0-1)
- ε = porosity
- K = absolute permeability [m²]
- J(S) = Leverett function (empirical)

**For Hydrophobic GDL (θ > 90°):**
```
J(S) = 1.417·(1-S) - 2.120·(1-S)² + 1.263·(1-S)³
```

**For Hydrophilic GDL (θ < 90°):**
```
J(S) = 1.417·S - 2.120·S² + 1.263·S³
```

**Typical GDL Parameters:**
- ε = 0.7-0.8
- K = 1-5 × 10⁻¹² m²
- r_pore = 10-50 μm

---

### Relative Permeability

**Effective Permeability:**
```
K_eff,liquid = K · k_rl(S)
K_eff,gas = K · k_rg(S)
```

**Common Correlations:**
```
k_rl = S³
k_rg = (1-S)³
```

**Alternative (Brooks-Corey):**
```
k_rl = S^((2+3λ)/λ)
k_rg = (1-S)²·(1 - S^((2+λ)/λ))
```

λ = pore size distribution index (typically 2-4)

---

## Gas Diffusion Layer Management

### GDL Saturation

**Definition:**
```
S = V_liquid / V_pore
```

**Ideal Saturation:**
- Anode: S = 0.3-0.5 (ensure water supply, allow O₂ escape)
- Cathode: S = 0.1-0.3 (primarily gas, some humidification)

**Effects of High Saturation:**
- Reduced gas permeability
- Blocked pores
- Mass transport losses
- Voltage increase

**Effects of Low Saturation:**
- Membrane drying
- Increased resistance
- Hot spots
- Degradation

---

### GDL Compression

**Impact of Clamping Pressure:**

| Clamping Pressure [MPa] | Porosity Change | Permeability Change |
|------------------------|-----------------|---------------------|
| 0.5 | -5% | -10% |
| 1.0 | -10% | -25% |
| 2.0 | -20% | -50% |
| 3.0 | -30% | -70% |

**Compressed Thickness:**
```
t_compressed = t₀ · (1 - α·log(P/P₀))
```

- α ≈ 0.05-0.1 for carbon paper
- t₀ = uncompressed thickness

**Design Trade-off:**
- Higher compression → lower contact resistance
- Higher compression → lower porosity → worse mass transport

---

### Water Transport in GDL

**Combined Mechanisms:**

1. **Diffusion:**
   ```
   N_diff = -ρ·D_eff·∇Y_H₂O
   ```

2. **Convection (Darcy):**
   ```
   N_conv = ρ·v = -ρ·(K/μ)·∇p
   ```

3. **Capillary-Driven:**
   ```
   v_cap = -(K/μ)·(dp_c/dS)·∇S
   ```

**Overall Mass Conservation:**
```
∂(ε·ρ·S)/∂t + ∇·(ρ·v) = Source
```

---

## Water Supply Strategy

### Anode Water Flow Rate

**Stoichiometric Requirement:**
```
ṅ_H₂O,rxn = I / (2F)
```

**Actual Water Supply:**
```
ṅ_H₂O,supply = λ_stoich · ṅ_H₂O,rxn
```

- λ_stoich = stoichiometric ratio (typically 5-20)

**Volumetric Flow Rate:**
```
Q_water = (ṅ_H₂O · M_H₂O) / ρ_water
```

**Example at 1 A/cm², 100 cm²:**
```
ṅ_H₂O,rxn = 100 / (2 × 96485) = 5.2 × 10⁻⁴ mol/s
ṅ_H₂O,supply = 10 × 5.2 × 10⁻⁴ = 5.2 × 10⁻³ mol/s
Q_water ≈ 5.6 ml/min
```

---

### Flow Rate Optimization

**Too Low Flow:**
- Insufficient water at reaction sites
- Drying near outlet
- Poor performance

**Too High Flow:**
- Excessive pumping power
- Heat removal > heat generation → cooling needed
- Dilute products

**Optimal Range:**
- λ_stoich = 5-10
- Adjust based on current density
- Higher flow at start-up, reduce at steady state

---

### Recirculation vs Once-Through

**Recirculation System:**
```
     ┌──── Stack ────┐
     │               │
Pump ─┤               ├─ Separator
     │               │
     └──────┬────────┘
            │
         Purge (remove dissolved gases)
```

**Advantages:**
- Higher water utilization
- Better temperature control
- Lower deionized water consumption

**Disadvantages:**
- Complex system
- Pump energy
- Purge line needed

---

**Once-Through:**
```
DI Water → Stack → Separator → Drain
```

**Advantages:**
- Simple
- No recirculation pump
- Easier control

**Disadvantages:**
- High water consumption
- Low efficiency
- Not practical for large systems

**Recommendation:** Recirculation for systems > 1 kW

---

## Flooding & Drying

### Anode Flooding

**Symptoms:**
- Increased O₂ content in outlet water
- Pressure fluctuations
- Voltage increase (especially at high current)
- Gas bubbles in outlet water

**Causes:**
- Low water flow rate (paradoxically)
- High gas generation rate
- Poor GDL permeability
- Low operating temperature

**Solutions:**
- Increase water flow rate
- Increase temperature (reduces surface tension)
- Optimize GDL porosity
- Use interdigitated flow field

---

### Cathode Flooding

**Symptoms:**
- Liquid water in H₂ outlet
- Increased H₂ humidity
- Voltage instability

**Causes:**
- Back diffusion from anode
- Low cathode gas flow
- Low operating temperature

**Solutions:**
- Increase cathode purge/dry gas flow
- Use hydrophobic GDL (MPL coating)
- Optimize flow field

---

### Membrane Drying

**Symptoms:**
- Increased membrane resistance
- Hot spots
- Reduced performance
- Permanent degradation

**Causes:**
- Insufficient water supply
- High electro-osmotic drag
- High operating temperature
- Low relative humidity

**Solutions:**
- Increase stoichiometry
- Ensure proper humidification
- Reduce current density
- Use thicker membrane

---

### Diagnostic Tools

**In-Situ Monitoring:**
1. **Differential Pressure:** Increase → flooding
2. **Impedance Spectroscopy:** High frequency → membrane resistance
3. **Neutron Imaging:** Direct water distribution measurement
4. **Visual Observation:** Transparent cells

**Post-Mortem:**
- Membrane thickness measurement
- SEM imaging (pore structure)
- Contact angle measurement

---

## Modeling Approaches

### 1D Water Balance Model

**Assumptions:**
- Uniform current density
- No lateral transport
- Steady state

**Governing Equation:**
```
d/dx(N_H₂O) = 0  (conservation)
```

**Boundary Conditions:**
- Inlet: Known water flow
- Outlet: Known pressure

**Solution:**
```python
def solve_1d_water_balance(j, stoich, L=0.1, n_points=100):
    x = np.linspace(0, L, n_points)
    dx = L / n_points

    # Water flow rate
    N_H2O = np.zeros(n_points)
    N_H2O[0] = stoich * j / (2 * F)  # Inlet

    for i in range(1, n_points):
        # Reaction consumption
        N_rxn = j * dx / (2 * F)

        # Electro-osmotic drag
        N_eod = n_d * j * dx / F

        # Back diffusion
        N_diff = D_w * (C_prev - C_current) / t_mem

        # Update
        N_H2O[i] = N_H2O[i-1] - N_rxn - N_eod + N_diff

    return x, N_H2O
```

---

### 2D/3D CFD Model

**Governing Equations:**

Mass conservation (liquid):
```
∂(ε·ρ·S)/∂t + ∇·(ρ·u_l) = -ṁ_evap
```

Mass conservation (gas):
```
∂(ε·ρ_g·(1-S))/∂t + ∇·(ρ_g·u_g) = ṁ_evap + S_gen
```

Momentum (Darcy):
```
u_l = -(K_rl·K/μ_l)·∇p_l
u_g = -(K_rg·K/μ_g)·∇p_g
```

Saturation transport:
```
∂S/∂t + ∇·(u_l·S) = ∇·(D_cap·∇S) + Source
```

Where capillary diffusion:
```
D_cap = -(K/μ_l)·(dp_c/dS)
```

---

### Pore Network Model

**Concept:**
- Discretize GDL into pore network
- Each pore has specific size, shape
- Solve transport at pore scale
- Upscale to macro scale

**Advantages:**
- Captures heterogeneity
- Predicts pore-level phenomena
- Can optimize GDL microstructure

**Disadvantages:**
- Computationally intensive
- Requires detailed GDL characterization
- Complex implementation

---

## Summary

**Water Management Checklist:**

✅ **Anode Side:**
- Sufficient water flow (λ_stoich = 5-10)
- Proper GDL saturation (S = 0.3-0.5)
- Good O₂ removal (avoid flooding)
- Maintain membrane hydration

✅ **Cathode Side:**
- Remove product H₂ efficiently
- Control humidity (avoid flooding)
- Use hydrophobic GDL if needed

✅ **System Level:**
- Monitor pressure drop
- Control temperature (60-70°C optimal)
- Implement water recirculation
- Regular purge of dissolved gases

**Key Equations to Remember:**

Electro-osmotic drag:
```
N_eod = n_d · (I/F)
```

Capillary pressure:
```
p_c = σ·√(ε/K)·J(S)
```

Water stoichiometry:
```
Q_water = λ_stoich · (I/2F) · (M_H₂O/ρ_H₂O)
```

---

**Previous:** [Geometries & Flow Field Designs](04-geometries-designs.md)  
**Next:** [Balance of Plant](06-balance-of-plant.md)
