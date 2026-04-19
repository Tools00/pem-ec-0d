# PEM Electrolysis - Materials & Components

## Table of Contents
- [Membrane Electrode Assembly (MEA)](#membrane-electrode-assembly-mea)
- [Catalysts](#catalysts)
- [Membranes](#membranes)
- [Gas Diffusion Layers](#gas-diffusion-layers)
- [Bipolar Plates](#bipolar-plates)
- [Seals & Gaskets](#seals--gaskets)
- [End Plates & Hardware](#end-plates--hardware)
- [Material Costs](#material-costs)

---

## Membrane Electrode Assembly (MEA)

The MEA is the heart of the PEM electrolysis cell, consisting of:
1. **Membrane** (50-175 μm)
2. **Catalyst Layers** (5-20 μm each)
3. **Gas Diffusion Layers** (200-400 μm each)

### MEA Fabrication Methods

**CCM (Catalyst Coated Membrane):**
- Catalyst ink is directly coated onto the membrane
- Better catalyst utilization
- Lower contact resistance
- **Most common in industry**

**CCS (Catalyst Coated Substrate):**
- Catalyst is coated on GDL
- Easier to handle
- Higher contact resistance

**Typical MEA Structure:**
```
┌─────────────────────────┐
│ GDL (Anode)  350 μm    │
├─────────────────────────┤
│ CL (Anode)   10-20 μm  │
├─────────────────────────┤
│ Membrane     50-175 μm │
├─────────────────────────┤
│ CL (Cathode) 5-10 μm   │
├─────────────────────────┤
│ GDL (Cathode) 350 μm   │
└─────────────────────────┘
Total thickness: ~800-950 μm
```

---

## Catalysts

### Anode Catalysts (OER)

The anode catalyst is the **most critical** component due to:
- Slow OER kinetics (requires high overpotential)
- Harsh oxidizing environment (1.6-2.0 V vs SHE)
- High iridium loading (cost driver)

#### Iridium Oxide (IrO₂)

**Properties:**
- Most stable OER catalyst in acidic environment
- Exchange current density: j₀ ≈ 1-5 × 10⁻⁵ A/cm²
- Tafel slope: 40-60 mV/dec
- Loading: 1-3 mg/cm² (typically 2 mg/cm²)

**Synthesis Methods:**
1. **Adams Fusion:** Ir salt + NaNO₃ → IrO₂ (high activity)
2. **Thermal Decomposition:** IrCl₃ → IrO₂ (good crystallinity)
3. **Sol-Gel:** Controlled particle size

**Performance Factors:**
- **Crystallinity:** Amorphous > Crystalline (activity)
- **Particle Size:** 2-5 nm optimal
- **Surface Area:** 50-100 m²/g

#### Iridium-Ruthenium Oxide (Ir-Ru Oxide)

**Properties:**
- Higher activity than pure IrO₂
- Ru reduces Ir content (cost saving)
- Ru dissolution limits lifetime

**Typical Composition:**
- Ir:Ru = 70:30 to 50:50 (atomic ratio)
- Loading: 0.5-2 mg/cm²

**Stability Trade-off:**
```
Pure IrO₂:     Activity = 7/10, Stability = 10/10
Ir-Ru (50:50): Activity = 9/10, Stability = 6/10
```

#### Pyrochlore Catalysts

**Structure:** A₂B₂O₇

**Examples:**
- Pb₂Ir₂O₇
- Bi₂Ir₂O₇
- Y₂Ir₂O₇

**Advantages:**
- Lower Ir content
- Tunable properties via A-site substitution
- Good activity

**Disadvantages:**
- Complex synthesis
- Limited stability data

#### Novel Catalysts (Research Stage)

**Core-Shell Structures:**
- Ir shell on non-precious core (e.g., TiO₂, Ta₂O₅)
- Reduces Ir loading to 0.1-0.5 mg/cm²

**Single-Atom Catalysts:**
- Isolated Ir atoms on support
- Maximum atom utilization
- Very early stage

---

### Cathode Catalysts (HER)

The cathode environment is **reducing** and **less harsh**, allowing more material options.

#### Platinum on Carbon (Pt/C)

**Standard Catalyst:**
- Pt loading: 20-40 wt% on carbon black
- Catalyst loading: 0.3-1 mg/cm²
- Exchange current density: j₀ ≈ 1-5 × 10⁻³ A/cm²
- Tafel slope: 30-40 mV/dec

**Advantages:**
- Highest HER activity
- Well-established
- Long-term stable

**Disadvantages:**
- High cost (~30 €/g Pt)
- Carbon corrosion during start/stop

#### Platinum-Ruthenium (Pt-Ru/C)

**Use Case:** When CO tolerance is needed
- Ru content: 10-50 at%
- Slightly lower HER activity
- More expensive than pure Pt/C

#### Palladium (Pd/C)

**Alternative to Pt:**
- Lower cost (~5 €/g)
- Lower activity (j₀ ≈ 10⁻⁴ A/cm²)
- Higher loading needed (1-2 mg/cm²)

#### Non-Precious Metal Catalysts (Research)

**Transition Metal Dichalcogenides:**
- MoS₂, WS₂
- Promising lab results
- Stability issues in PEM environment

**Nickel-Molybdenum (Ni-Mo):**
- Good in alkaline, not stable in acid
- Not suitable for standard PEM

---

### Catalyst Layer Design

**Typical Structure:**
```
CL Composition:
- Catalyst: 60-80 wt%
- Ionomer (Nafion): 20-30 wt%
- Pores: 30-40% (for gas/water transport)
```

**Ionomer Function:**
- Proton conduction within CL
- Binds catalyst particles
- Too much → blocks pores
- Too little → poor proton access

**Optimal Ionomer Content:**
- Anode: 20-25 wt%
- Cathode: 25-30 wt%

**CL Thickness:**
```
t_CL = (Loading) / (ρ_catalyst · (1-ε))
```

Example for anode (2 mg/cm² IrO₂):
```
t_CL = (0.002 g/cm²) / (11.7 g/cm³ · 0.6) ≈ 0.3 μm
```

Typical: 5-20 μm (with ionomer and porosity)

---

## Membranes

### PFSA (Perfluorosulfonic Acid) Membranes

**Chemical Structure:**
```
-[CF₂-CF₂]n-[CF₂-CF(OCF₂CF(SO₃H))m]-O-CF=CF₂
```

**Key Properties:**
- **Proton conductivity:** 0.08-0.15 S/cm (hydrated)
- **Water uptake:** 20-40 wt%
- **Ion Exchange Capacity (IEC):** 0.9-1.1 meq/g
- **Equivalent Weight (EW):** 900-1100 g/eq

#### Nafion (DuPont/Chemours)

**Product Line:**

| Grade | Thickness [μm] | EW [g/eq] | Application |
|-------|---------------|-----------|-------------|
| Nafion 112 | 51 | 1100 | General |
| Nafion 115 | 127 | 1100 | Standard electrolysis |
| Nafion 117 | 178 | 1100 | High durability |
| Nafion 211 | 25 | 1000 | High conductivity |
| Nafion 212 | 51 | 1000 | Balance perf/durability |

**Properties (Nafion 212):**
- Conductivity: 0.1 S/cm at 80°C (λ=14)
- Gas crossover (H₂): 1-2 mA/cm² equivalent
- Mechanical strength: 20-30 MPa
- Elongation at break: >200%

**Water Content (λ):**
```
λ = number of H₂O / SO₃H group
λ = 14-22 (fully hydrated)
λ < 5 (membrane dries out → conductivity drops)
```

#### Aquivion (Solvay)

**Differences from Nafion:**
- Shorter side chain
- Higher crystallinity
- Better mechanical properties
- Higher glass transition temperature (T_g)

**Products:**
- Aquivion E87-05S: 50 μm, EW=870
- Aquivion E98-05S: 50 μm, EW=980

**Advantages for Electrolysis:**
- Lower gas crossover
- Better high-temperature performance
- Improved chemical stability

### Alternative Membranes

#### PBI (Polybenzimidazole)

**High-Temperature Membrane:**
- Operates at 120-180°C
- Doped with phosphoric acid (H₃PO₄)
- Proton conductivity: 0.1-0.2 S/cm

**Advantages:**
- No humidification needed
- Higher efficiency at high T
- Lower catalyst loading possible

**Disadvantages:**
- Acid leaching
- Lower mechanical strength
- Expensive

#### sPEEK (Sulfonated Polyetheretherketone)

**Lower-Cost Alternative:**
- Conductivity: 0.01-0.1 S/cm (depends on sulfonation degree)
- Cheaper than PFSA
- Moderate stability

**Properties:**
- IEC: 1.0-2.0 meq/g
- Water uptake: 20-60% (can swell excessively)
- Temperature limit: ~80°C

---

## Gas Diffusion Layers

The GDL serves multiple functions:
1. **Electronic conduction** (current collection)
2. **Gas transport** (O₂ removal, H₂ removal)
3. **Water management** (supply to anode, removal from cathode)
4. **Mechanical support** (for thin membranes)
5. **Heat conduction** (cooling)

### Anode GDL (Oxygen Side)

**Challenges:**
- Highly oxidizing environment (1.6-2.0 V)
- Carbon corrodes rapidly
- Must use titanium

#### Titanium Felt

**Standard Choice:**
- Thickness: 250-500 μm
- Porosity: 70-85%
- Permeability: 1-5 × 10⁻¹² m²
- Conductivity: 200-500 S/m

**Properties (Garmat GDL2925):**
- Thickness: 250 μm
- Porosity: 78%
- Density: 1.2 g/cm³

**Advantages:**
- Excellent corrosion resistance
- Good mechanical strength
- High porosity

**Disadvantages:**
- Expensive (~100-200 €/m²)
- Heavy
- Requires cleaning/passivation

#### Titanium Fleece

**Thinner Alternative:**
- Thickness: 100-300 μm
- Lower density
- More flexible

**Properties:**
- Porosity: 60-75%
- Areal weight: 30-80 g/m²

#### Surface Treatments

**Platinized Titanium:**
- Pt coating (0.1-0.5 mg/cm²)
- Reduces contact resistance
- Prevents TiO₂ formation

**Other Coatings:**
- Au, Pd, Nb
- Improve conductivity
- Reduce passivation

---

### Cathode GDL (Hydrogen Side)

**Environment:** Reducing, non-corrosive
**Material Options:** Carbon-based

#### Carbon Paper

**Most Common:**
- Toray H2315 (Japan)
- AvCarb (USA)
- SGL SIGRACET (Germany)

**Properties (Toray H2315):**
- Thickness: 350 μm
- Porosity: 78%
- Density: 0.45 g/cm³
- Conductivity: 500-800 S/m (through-plane)
- Tensile strength: 10-15 MPa

**Advantages:**
- Low cost (~10-30 €/m²)
- Lightweight
- Good conductivity
- Flexible

**Disadvantages:**
- Hydrophobic treatment degrades over time
- Lower mechanical strength than Ti

#### Carbon Cloth

**Woven Structure:**
- More flexible than paper
- Better conformability
- Higher cost

**Properties:**
- Thickness: 300-500 μm
- Porosity: 70-80%

#### Microporous Layer (MPL)

**Purpose:**
- Improves water management
- Reduces contact resistance
- Prevents membrane intrusion into GDL pores

**Composition:**
- Carbon black (Vulcan XC-72)
- PTFE binder (10-30 wt%)
- Pore size: 0.1-1 μm

**Structure:**
```
GDL Substrate (350 μm)
│
├─ Macropores (10-50 μm)
│
└─ MPL (20-50 μm)
   ├─ Micropores (0.1-1 μm)
   └─ PTFE coating (hydrophobic)
```

---

## Bipolar Plates

Bipolar plates serve as:
1. **Current collectors** (electronic conduction)
2. **Flow field** (water/gas distribution)
3. **Structural support** (stack compression)
4. **Cooling** (heat removal)
5. **Gas separation** (H₂/O₂ barrier)

### Material Requirements

**Electrical Conductivity:**
- >100 S/cm (bulk)
- Low contact resistance (<10 mΩ·cm²)

**Thermal Conductivity:**
- >10 W/(m·K) (for cooling)

**Corrosion Resistance:**
- Stable in acidic environment (pH 2-4)
- Anode side: 1.6-2.0 V vs SHE
- Cathode side: 0 V vs SHE

**Mechanical Properties:**
- Compressive strength >200 MPa
- Low gas permeability (<10⁻⁶ cm³/cm²·s)

### Titanium Plates

**Industry Standard:**
- Grade 2 (pure Ti)
- Grade 5 (Ti-6Al-4V) - stronger but less conductive

**Properties (Ti Gr2):**
- Conductivity: 2.2 × 10⁶ S/m
- Thermal conductivity: 17 W/(m·K)
- Density: 4.5 g/cm³
- Cost: 30-50 €/kg (raw material)

**Advantages:**
- Excellent corrosion resistance
- Forms passive TiO₂ layer
- High strength-to-weight ratio

**Disadvantages:**
- Expensive to machine
- Heavy
- TiO₂ layer increases contact resistance

**Surface Treatments:**
- Nitride coatings (TiN, TiAlN)
- Carbide coatings (TiC)
- Noble metal coatings (Au, Pt)
- Purpose: Reduce contact resistance

---

### Stainless Steel Plates

**Lower-Cost Alternative:**
- SS 316L (standard grade)
- Requires protective coating

**Properties (SS 316L):**
- Conductivity: 1.4 × 10⁶ S/m
- Thermal conductivity: 15 W/(m·K)
- Density: 8.0 g/cm³
- Cost: 5-10 €/kg

**Coatings (Required for Anode):**

| Coating | Method | Conductivity | Stability | Cost |
|---------|--------|--------------|-----------|------|
| **TiN** | PVD | High | Good | Medium |
| **CrN** | PVD | High | Very good | Medium |
| **TiC** | CVD | Very high | Excellent | High |
| **Au** | Electroplating | Excellent | Good | Very high |
| **Carbon** | Sputtering | Medium | Moderate | Low |

**Coating Thickness:**
- Typically: 50-200 nm
- Too thin → pinholes → corrosion
- Too thick → cracking, high cost

---

### Flow Field Design

**Common Patterns:**

1. **Serpentine:**
   ```
   ═╗══╗══╗
     ╚══╩══╩═
   ```
   - Single continuous channel
   - Good water distribution
   - High pressure drop

2. **Parallel:**
   ```
   ═══  ═══  ═══
   ```
   - Multiple parallel channels
   - Low pressure drop
   - Risk of uneven distribution

3. **Interdigitated:**
   ```
   ⊕ ║ ⊕ ║ ⊕
    ═╩═╩═╩═
   ```
   - Dead-ended channels
   - Forced convection through GDL
   - Good for water removal

4. **Mesh/Screen:**
   ```
   ╬╬╬╬
   ╬╬╬╬
   ```
   - Multiple flow paths
   - Good distribution
   - Complex manufacturing

**Channel Dimensions (Typical):**
- Width: 0.5-2 mm
- Depth: 0.5-1.5 mm
- Land width: 0.5-1 mm
- Number of channels: 10-50 (depends on size)

---

## Seals & Gaskets

### Requirements

**Chemical Compatibility:**
- Resistant to acidic environment
- Stable in oxidizing (anode) and reducing (cathode) conditions

**Temperature Range:**
- Operating: 50-80°C
- Startup/shutdown: 20-90°C
- Thermal cycling resistance

**Compression Set:**
- Maintain seal under constant compression
- Recover after decompression

**Gas Permeability:**
- H₂ permeability < 10⁻⁶ cm³/s
- Prevent H₂/O₂ mixing

---

### Elastomeric Seals

#### FKM (Viton)

**Most Common:**
- Temperature range: -20 to 200°C
- Excellent chemical resistance
- Cost: €€

**Properties:**
- Hardness: 60-80 Shore A
- Elongation: 200-400%
- Compression set: <25% (70h @ 200°C)

#### EPDM

**Lower-Cost Option:**
- Temperature range: -40 to 150°C
- Good steam resistance
- Lower cost than FKM

**Limitations:**
- Poor oil/fuel resistance (not critical for electrolysis)
- Lower temperature limit

#### FFKM (Kalrez, Chemraz)

**High-Performance:**
- Temperature range: -25 to 320°C
- Excellent chemical resistance
- Very low compression set

**Disadvantages:**
- Very expensive (€€€€)
- Used in critical applications

### PTFE Seals

**Virgin PTFE:**
- Temperature range: -200 to 260°C
- Excellent chemical resistance
- High creep (cold flow)

**Filled PTFE:**
- Glass-filled, carbon-filled
- Reduced creep
- Higher hardness

### Liquid Gaskets

**Form-in-Place (FIP):**
- Silicone-based
- Cures in place
- Good for complex geometries

---

## End Plates & Hardware

### End Plates

**Function:**
- Provide clamping force
- Distribute compression evenly
- Structural support for stack

**Materials:**

| Material | Strength | Weight | Cost | Use Case |
|----------|----------|--------|------|----------|
| **Aluminum 6061** | High | Light | €€ | Standard |
| **Stainless Steel** | Very high | Heavy | €€€ | High pressure |
| **Carbon Fiber** | Very high | Very light | €€€€ | Weight-critical |
| **Titanium** | High | Medium | €€€€€ | Corrosion-critical |

**Design Considerations:**
- Thickness: 15-30 mm (depends on stack size)
- Flatness: <0.1 mm across surface
- Machining tolerance: ±0.05 mm

---

## Material Costs

### Cost Breakdown (for 100 cm² cell)

| Component | Material | Quantity | Unit Cost | Total Cost | % of Total |
|-----------|----------|----------|-----------|------------|------------|
| **Anode Catalyst** | IrO₂ | 2 mg/cm² | 150 €/g | 30 € | 30% |
| **Cathode Catalyst** | Pt/C | 0.5 mg/cm² | 30 €/g | 1.5 € | 2% |
| **Membrane** | Nafion 212 | 100 cm² | 0.5 €/cm² | 50 € | 25% |
| **GDL Anode** | Ti Felt | 100 cm² | 1.5 €/cm² | 15 € | 8% |
| **GDL Cathode** | Carbon Paper | 100 cm² | 0.3 €/cm² | 3 € | 2% |
| **Bipolar Plates** | Ti Gr2 | 2 × 100 cm² | 0.8 €/cm² | 16 € | 8% |
| **Seals/Gaskets** | FKM | - | - | 5 € | 3% |
| **Assembly** | Labor | - | - | 10 € | 5% |
| **Overhead** | - | - | - | 34 € | 17% |
| **Total** | - | - | - | **~200 €** | 100% |

**Cost per kW:**
- At 1 A/cm², 1.8 V: 180 W per 100 cm²
- Cost: 200 € / 0.18 kW ≈ 1100 €/kW

**Target (DOE 2025):**
- <200 €/kW for large-scale production
- Requires: Reduced Ir loading, cheaper membranes, automation

---

### Cost Reduction Strategies

**Catalyst:**
- Reduce Ir loading to 0.5 mg/cm² (from 2 mg/cm²)
- Use Ir alloys (Ir-Ru)
- Core-shell structures

**Membrane:**
- Use thinner membranes (25-50 μm)
- Alternative materials (sPEEK, hydrocarbon)

**Bipolar Plates:**
- Use coated stainless steel instead of Ti
- High-volume manufacturing (stamping)

**Manufacturing:**
- Roll-to-roll processing
- Automated MEA assembly
- Economies of scale

---

## Summary

**Critical Material Choices:**

1. **Anode Catalyst:** IrO₂ is standard, but expensive
2. **Membrane:** Nafion proven, but alternatives emerging
3. **Anode GDL:** Titanium felt required for stability
4. **Bipolar Plates:** Ti or coated SS
5. **Seals:** FKM for standard, FFKM for high-performance

**Material Selection Criteria:**
- Performance (activity, conductivity)
- Stability (lifetime, degradation rate)
- Cost (raw material, processing)
- Availability (supply chain security)

**Research Directions:**
- Reduce/replace precious metals
- Lower-cost membranes
- Improved GDL designs
- Advanced coatings for BPPs

---

**Previous:** [Governing Equations](02-governing-equations.md)  
**Next:** [Geometries & Flow Field Designs](04-geometries-designs.md)
