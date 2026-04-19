# PEM Electrolysis - Basics & Chemistry

## Table of Contents
- [What is PEM Electrolysis?](#what-is-pem-electrolysis)
- [Chemical Reactions](#chemical-reactions)
- [Thermodynamics](#thermodynamics)
- [Key Performance Metrics](#key-performance-metrics)
- [Operating Conditions](#operating-conditions)

---

## What is PEM Electrolysis?

PEM (Proton Exchange Membrane) electrolysis is a technology for producing hydrogen by splitting water molecules using electrical energy. The key component is a solid polymer membrane that conducts protons (H⁺ ions) while preventing gas mixing.

### Advantages over Alkaline Electrolysis
- **Higher current density:** 1-3 A/cm² vs 0.2-0.6 A/cm²
- **Higher hydrogen purity:** >99.99%
- **Compact design:** No liquid electrolyte
- **Dynamic operation:** Fast response to load changes
- **Higher operating pressure:** Up to 30-70 bar

### Disadvantages
- **Higher cost:** Precious metal catalysts (Ir, Pt)
- **Shorter lifetime:** 40-60k hours vs 80-100k hours
- **Acidic environment:** Requires corrosion-resistant materials

---

## Chemical Reactions

### Anode (Oxidation) - Oxygen Evolution Reaction (OER)

```
2H₂O → O₂ + 4H⁺ + 4e⁻    E° = +1.23 V vs SHE
```

**Mechanism (simplified):**
1. H₂O → OH* + H⁺ + e⁻
2. OH* → O* + H⁺ + e⁻
3. O* + H₂O → OOH* + H⁺ + e⁻
4. OOH* → O₂ + H⁺ + e⁻

*R represents an active site on the catalyst surface*

**Catalysts:** IrO₂, Ir-Ru mixed oxides, Pyrochlores

---

### Cathode (Reduction) - Hydrogen Evolution Reaction (HER)

```
4H⁺ + 4e⁻ → 2H₂    E° = 0 V vs SHE
```

**Mechanism:**
1. **Volmer step:** H⁺ + e⁻ → H*
2. **Tafel step:** H* + H* → H₂
   or **Heyrovsky step:** H* + H⁺ + e⁻ → H₂

**Catalysts:** Pt/C, Pt-Ru/C, Pd/C

---

### Overall Reaction

```
2H₂O + electrical energy → 2H₂ + O₂
```

**Thermodynamic parameters at 25°C (298.15 K):**
- ΔH° = +285.8 kJ/mol (enthalpy, endothermic)
- ΔG° = +237.1 kJ/mol (Gibbs free energy)
- ΔS° = +163 J/(mol·K) (entropy increase)
- T·ΔS° = +48.7 kJ/mol (can be supplied as heat)

---

## Thermodynamics

### Reversible Voltage (Nernst Equation)

```
E_rev = E° + (RT/nF) · ln(a_H₂O / (a_H₂ · a_O₂^0.5))
```

**Simplified for ideal conditions:**
```
E_rev = 1.23 - 8.46×10⁻⁴ · (T - 298.15) + (RT/2F) · ln(p_H₂) + (RT/4F) · ln(p_O₂)
```

**Where:**
- R = 8.314 J/(mol·K) - Universal gas constant
- F = 96,485 C/mol - Faraday constant
- n = 2 - Electrons per H₂ molecule
- T = Temperature (K)
- p = Partial pressures (bar)

### Temperature Dependence

| T [°C] | E_rev [V] | ΔG [kJ/mol] | T·ΔS [kJ/mol] |
|--------|-----------|-------------|---------------|
| 25     | 1.23      | 237.1       | 48.7          |
| 50     | 1.21      | 233.5       | 52.3          |
| 80     | 1.19      | 229.0       | 56.8          |
| 100    | 1.18      | 226.5       | 59.3          |

**Note:** Higher temperature reduces required voltage but increases degradation.

---

## Key Performance Metrics

### 1. Cell Voltage Components

```
U_cell = E_rev + η_act + η_ohm + η_conc
```

**Components:**
- **E_rev:** Reversible voltage (1.18-1.23 V)
- **η_act:** Activation overpotential (anode: 0.2-0.4 V, cathode: 0.05-0.1 V)
- **η_ohm:** Ohmic losses (0.1-0.3 V)
- **η_conc:** Concentration losses (<0.1 V at high current)

### 2. Efficiency Calculations

**Voltage Efficiency:**
```
η_V = E_rev / U_cell
```

**Faraday Efficiency:**
```
η_F = (actual H₂ production) / (theoretical H₂ production)
η_F ≈ 95-99% (typically 98%)
```

**Overall Efficiency (LHV-based):**
```
η_overall = η_V · η_F · (LHV_H₂ / ΔH)
LHV_H₂ = 241.8 kJ/mol = 119.9 MJ/kg
```

**Practical values:**
- At 1.8 V: η ≈ 75%
- At 2.0 V: η ≈ 68%
- At 2.2 V: η ≈ 62%

### 3. Specific Energy Consumption

**Theoretical minimum:**
```
E_specific,theoretical = ΔG / (2·F·M_H₂) = 33 kWh/kg H₂
```

**Practical values:**
```
E_specific = U_cell · (2·F) / (η_F · M_H₂)
```

| U_cell [V] | E_specific [kWh/kg H₂] |
|------------|------------------------|
| 1.6        | 42                     |
| 1.8        | 48                     |
| 2.0        | 53                     |
| 2.2        | 58                     |

### 4. Hydrogen Production Rate

**Faraday's Law:**
```
ṁ_H₂ = (η_F · I · M_H₂) / (n · F)
```

**Simplified:**
```
ṁ_H₂ [g/h] = 0.0672 · η_F · I [A]
V_H₂ [L/min] = 0.0124 · η_F · I [A]  (at STP)
```

**Example at 1 A/cm², 100 cm²:**
- I = 100 A
- ṁ_H₂ = 6.6 g/h (with η_F = 98%)
- V_H₂ = 1.22 L/min

---

## Operating Conditions

### Standard Operating Range

| Parameter | Range | Optimal | Notes |
|-----------|-------|---------|-------|
| **Temperature** | 50-80°C | 60-70°C | Limited by membrane |
| **Pressure** | 1-30 bar | 10-20 bar | Higher = better purity |
| **Current Density** | 0.5-3 A/cm² | 1-2 A/cm² | Material-dependent |
| **Voltage** | 1.6-2.4 V | 1.8-2.0 V | Per cell |
| **Water Flow** | 50-200 ml/min per kW | 100 ml/min | For cooling & reaction |

### Water Quality Requirements

| Parameter | Requirement | Unit |
|-----------|-------------|------|
| **Conductivity** | <1 | μS/cm |
| **Resistivity** | >1 | MΩ·cm |
| **Total Organic Carbon** | <50 | ppb |
| **Chloride** | <10 | ppb |
| **Sulfate** | <10 | ppb |
| **Metal ions** | <1 | ppb each |
| **Particles** | <0.1 | μm |

**Why ultra-pure water?**
- Ions poison the membrane → reduced conductivity
- Metals deposit on catalysts → reduced activity
- Impurities cause degradation → shorter lifetime

### Gas Purity

**Typical specifications:**
- **H₂ purity:** 99.95-99.999% (after drying)
- **O₂ purity:** >99% (with 1-2% H₂O)
- **H₂ in O₂:** <2% (safety limit: 4%)
- **O₂ in H₂:** <0.5%
- **Dew point (H₂):** -40 to -70°C (after drying)

---

## Material Selection Overview

### Catalysts

**Anode (OER):**
1. **IrO₂ (Iridium Oxide)**
   - Best stability >5000 h
   - j₀ ≈ 10⁻⁶ - 10⁻⁵ A/cm²
   - Loading: 1-3 mg/cm²
   - Cost: ~150 €/g

2. **Ir-Ru Mixed Oxide**
   - Higher activity than pure IrO₂
   - Ru dissolves over time
   - Loading: 0.5-2 mg/cm²
   - Cost: ~100 €/g

3. **Pyrochlore (Iridate)**
   - A₂Ir₂O₇ structure
   - Good stability
   - Lower Ir loading possible

**Cathode (HER):**
1. **Pt/C (Platinum on Carbon)**
   - Best activity
   - j₀ ≈ 10⁻³ - 10⁻² A/cm²
   - Loading: 0.3-1 mg/cm²
   - Cost: ~30 €/g

2. **Pt-Ru/C**
   - CO-tolerant
   - Slightly lower activity
   - Used in reformate applications

### Membranes

**PFSA (Perfluorosulfonic Acid):**
1. **Nafion (DuPont/Chemours)**
   - Nafion 115: 127 μm, 1100 g/mol EW
   - Nafion 212: 50 μm, higher conductivity
   - Nafion 117: 178 μm, robust

2. **Aquivion (Solvay)**
   - Shorter side chain
   - Higher crystallinity
   - Better high-temperature performance

3. **3M PFSA**
   - Nanostructured thin film
   - Lower gas crossover

**Alternative Membranes:**
- **PBI/H₃PO₄:** High temperature (>120°C)
- **sPEEK:** Lower cost, moderate performance
- **Radiation-grafted:** Custom properties

### Gas Diffusion Layers

**Anode Side (oxidizing environment):**
- **Titanium Felt:** sintered Ti fibers, 80% porosity
- **Titanium Fleece:** non-woven, lower thickness
- **Pt-coated Ti:** improves contact, reduces passivation

**Cathode Side (reducing environment):**
- **Carbon Paper:** Toray H2315, 350 μm, 78% porosity
- **Carbon Cloth:** woven fibers, flexible
- **Microporous Layer (MPL):** improves water management

---

## Summary

PEM electrolysis offers:
- ✅ High efficiency (65-80%)
- ✅ High hydrogen purity (>99.99%)
- ✅ Compact design
- ✅ Dynamic operation
- ⚠️ High material costs (Ir, Pt, Ti)
- ⚠️ Water purity requirements
- ⚠️ Limited lifetime (40-60k hours)

Understanding the chemistry and thermodynamics is essential for:
- Optimizing operating conditions
- Selecting appropriate materials
- Designing efficient systems
- Developing accurate simulations

---

## References

1. Carmo, M., et al. "A comprehensive review on PEM water electrolysis." *International Journal of Hydrogen Energy* 38.12 (2013): 4901-4934.
2. Grigoriev, S. A., et al. "Current achievements and future prospects of PEM water electrolysis." *International Journal of Hydrogen Energy* (2020).
3. Shiva Kumar, S., and V. Himabindu. "Materials investigation and optimization of proton exchange membrane electrolyzer cell." *Materials Science and Energy Technology* 2.3 (2019): 433-440.

---

**Next:** [Governing Equations](02-governing-equations.md)
