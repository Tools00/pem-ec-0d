# PEM Electrolysis - Geometries & Flow Field Designs

## Table of Contents
- [Cell Configurations](#cell-configurations)
- [Flow Field Designs](#flow-field-designs)
- [Channel Geometries](#channel-geometries)
- [Active Area Sizing](#active-area-sizing)
- [Stack Design](#stack-design)
- [Design Optimization](#design-optimization)

---

## Cell Configurations

### Planar Design

**Most Common Configuration**
```
┌─────────────────────────┐
│ End Plate               │
├─────────────────────────┤
│ Current Collector       │
├─────────────────────────┤
│ Bipolar Plate           │
├─────────────────────────┤
│ Anode GDL               │
├─────────────────────────┤
│ Anode Catalyst Layer    │
├─────────────────────────┤
│ Membrane                │
├─────────────────────────┤
│ Cathode Catalyst Layer  │
├─────────────────────────┤
│ Cathode GDL             │
├─────────────────────────┤
│ Bipolar Plate           │
├─────────────────────────┤
│ Current Collector       │
├─────────────────────────┤
│ End Plate               │
└─────────────────────────┘
```

**Advantages:**
- Easy to scale (add more cells)
- Good current collection
- Uniform compression
- Proven technology

**Disadvantages:**
- Large footprint
- Many sealing surfaces
- Heavy (for large areas)

---

### Tubular Design

**Cylindrical Configuration**
```
    ┌───────┐
    │ Outer │  ← Cathode GDL
   ╱       ╲
  │ Anode  │  ← Anode GDL
  │ Tube   │
   ╲       ╱
    │ Membr │  ← MEA
     └─────┘
```

**Advantages:**
- No side seals (only end seals)
- Better pressure containment
- Compact for small systems
- Reduced current collection path

**Disadvantages:**
- Difficult to manufacture large diameters
- Complex MEA installation
- Limited active area per tube
- Stacking requires manifold

---

### Spiral Wound Design

**Rolled MEA Configuration**
```
   ┌──────────┐
   │ @@@@@@@@ │  ← Multiple layers
   │ @@@@@@@@ │  ← wound in spiral
   │ @@@@@@@@ │
   └──────────┘
```

**Construction:**
1. Long strip of MEA
2. Separator plates between layers
3. Rolled into cylinder
4. Housed in pressure vessel

**Advantages:**
- Very high surface area/volume
- Compact design
- Fewer external connections

**Disadvantages:**
- Non-uniform flow distribution
- Difficult to service
- Limited commercial adoption

---

## Flow Field Designs

The flow field distributes reactants (water) and removes products (H₂, O₂) from the electrode surface.

### Serpentine Flow Field

**Single Serpentine:**
```
┌═══════════════════┐
│ → → → → → → → → →│
│                   │
│← ← ← ← ← ← ← ← ← │
│                   │
│→ → → → → → → → →│
└═══════════════════┘
```

**Characteristics:**
- Single continuous channel
- Forces all fluid through entire channel
- High pressure drop
- Excellent reactant distribution

**Design Equations:**

Number of channels:
```
N_ch = (W - W_land) / (W_ch + W_land)
```

- W = total width
- W_ch = channel width
- W_land = land width

Channel length:
```
L_ch = L × N_ch
```

**Pressure Drop:**
```
Δp = f · (L_ch/D_h) · (ρ·u²/2)
```

For laminar flow (Re < 2300):
```
f = 64/Re  (circular)
f ≈ 57/Re  (square)
```

**Advantages:**
- Uniform distribution
- Good water management
- Prevents dead zones

**Disadvantages:**
- High pressure drop
- Long channels → high pumping power
- Sensitive to blockages

---

### Multiple Serpentine

**Parallel Serpentine:**
```
┌═══════════════════┐
│ →→→  →→→  →→→   │
│                  │
│←←←  ←←←  ←←←    │
│                  │
│→→→  →→→  →→→   │
└═══════════════════┘
```

**Characteristics:**
- 2-4 parallel serpentine channels
- Manifold at inlet/outlet
- Lower pressure drop than single
- Balance between uniformity and pumping

---

### Parallel Flow Field

**Straight Channels:**
```
┌═══════════════════┐
│ →   →   →   →   →│
│ →   →   →   →   →│
│ →   →   →   →   →│
│ →   →   →   →   →│
└═══════════════════┘
```

**Characteristics:**
- All channels independent
- Common manifold
- Low pressure drop
- Risk of maldistribution

**Flow Distribution:**

The flow in each channel should be equal:
```
Q_i = Q_total / N_ch
```

But in practice, unequal due to:
- Manifold geometry
- Friction losses
- Manufacturing tolerances

**Uniformity Index:**
```
U = 1 - (σ_Q / Q_avg)
```

U > 0.95 is desirable

---

### Interdigitated Flow Field

**Dead-Ended Channels:**
```
┌═══════════════════┐
│ ⊕   ⊕   ⊕   ⊕   ⊕│  ← Inlets (blocked)
│  \\ // \\ // \\  │
│   X   X   X   X  │  ← Flow through GDL
│  // \\ // \\ //  │
│ ⊖   ⊖   ⊖   ⊖   ⊖│  ← Outlets (blocked)
└═══════════════════┘
```

**Mechanism:**
- Inlet and outlet channels alternate
- Channels are blocked at opposite ends
- Forced convection through porous GDL
- Enhanced mass transport

**Advantages:**
- Excellent water removal
- Prevents flooding
- Good for high current density

**Disadvantages:**
- Higher pumping power
- Complex manufacturing
- GDL compression critical

---

### Pin-Type / Dotted Field

**Discrete Contact Points:**
```
┌═══════════════════┐
│ ● ● ● ● ● ● ● ● ●│
│ ● ● ● ● ● ● ● ● ●│
│ ● ● ● ● ● ● ● ● ●│
│ ● ● ● ● ● ● ● ● ●│
└═══════════════════┘
```

**Design:**
- Array of cylindrical pins/pillars
- Water flows between pins
- High contact area
- Low flow resistance

**Pin Dimensions:**
- Diameter: 0.5-2 mm
- Height: 0.5-2 mm
- Spacing: 2-5 mm

**Advantages:**
- Good electrical contact
- Low pressure drop
- Easy to manufacture (stamping)

**Disadvantages:**
- Non-uniform current distribution
- Potential dead zones

---

### Biomimetic / Fractal Design

**Nature-Inspired Patterns:**
```
┌═══════════════════┐
│       /│\         │
│      / │ \        │
│     /  │  \       │
│    \   │   /      │
│     \  │  /       │
└═══════════════════┘
```

**Inspiration:**
- Leaf venation
- River networks
- Lung bronchial trees

**Advantages:**
- Optimal distribution
- Low pressure drop
- Self-similar scaling

**Disadvantages:**
- Complex to manufacture
- Limited commercial use

---

### Mesh / Screen Flow

**Grid Pattern:**
```
┌═══════════════════┐
│ ╬╬╬╬╬╬╬╬╬        │
│ ╬╬╬╬╬╬╬╬╬        │
│ ╬╬╬╬╬╬╬╬╬        │
└═══════════════════┘
```

**Construction:**
- Woven mesh or expanded metal
- Acts as both flow field and current collector
- High porosity

**Applications:**
- Small-scale cells
- Simplified design
- Low-cost manufacturing

---

## Channel Geometries

### Cross-Sectional Shapes

**Rectangular:**
```
┌─────┐
│     │
│     │
└─────┘
```
- Easiest to machine
- Sharp corners can cause issues
- Most common

**Trapezoidal:**
```
┌───────┐
│       │
│  ___  │
└───────┘
```
- Better for stacking
- Reduced stress concentration
- Requires specialized tooling

**Semi-Circular:**
```
┌─────┐
│     │
╰━━━━━╯
```
- Best flow characteristics
- Lowest pressure drop
- Difficult to manufacture

**Triangular:**
```
┌───┐
│   │
│ /_\│
└───┘
```
- Rare
- High pressure drop
- Not recommended

---

### Channel Dimensions

**Typical Ranges:**

| Parameter | Range | Optimal | Notes |
|-----------|-------|---------|-------|
| **Channel Width** | 0.5-3 mm | 1-1.5 mm | Narrow → high Δp |
| **Channel Depth** | 0.5-2 mm | 0.8-1.2 mm | Deep → poor contact |
| **Land Width** | 0.3-2 mm | 0.5-1 mm | Wide → high resistance |
| **Channel Pitch** | 1-5 mm | 2-3 mm | Center-to-center |

**Design Ratios:**

Channel-to-land ratio:
```
CLR = W_ch / W_land
Typical: 1.5 - 2.5
```

Aspect ratio:
```
AR = W_ch / H_ch
Typical: 1 - 2
```

Open area fraction:
```
f_open = W_ch / (W_ch + W_land)
Typical: 0.6 - 0.7 (60-70%)
```

---

### Hydraulic Diameter

**Definition:**
```
D_h = 4 × A_cross / P_wet
```

For rectangular channel:
```
D_h = 2·W·H / (W + H)
```

For square channel:
```
D_h = W (= H)
```

**Impact:**
- Smaller D_h → higher pressure drop
- Larger D_h → poorer distribution
- Optimal: 1-2 mm

---

## Active Area Sizing

### Single Cell Sizing

**Current and Power:**
```
I = j × A_active
P = U_cell × I
```

**Example:**
- j = 1 A/cm²
- A = 100 cm²
- U = 1.8 V

```
I = 1 × 100 = 100 A
P = 1.8 × 100 = 180 W
```

**Common Sizes:**

| Application | Active Area | Current @ 1 A/cm² | Power |
|-------------|-------------|-------------------|-------|
| Laboratory | 5 cm² | 5 A | 9 W |
| Small portable | 25 cm² | 25 A | 45 W |
| Medium | 100 cm² | 100 A | 180 W |
| Large | 500 cm² | 500 A | 900 W |
| Industrial | 2000 cm² | 2000 A | 3.6 kW |

---

### Scaling Considerations

**Geometric Constraints:**

Aspect ratio (length/width):
```
AR = L / W < 3
```

Reason: Uniform flow distribution becomes difficult

**Maximum Size:**
- Limited by manufacturing
- Limited by compression uniformity
- Typically: < 1 m per side

**Scaling Strategy:**

For higher power:
1. Increase active area (limited)
2. Increase current density (limited by degradation)
3. Add more cells in stack (preferred)

---

## Stack Design

### Series vs Parallel Configuration

**Electrical Series (Most Common):**
```
┌──┐ ┌──┐ ┌──┐ ┌──┐
│C1│-│C2│-│C3│-│C4│  → V_total = V1+V2+V3+V4
└──┘ └──┘ └──┘ └──┘
Same current I through all cells
```

**Electrical Parallel:**
```
    ┌──┐
   ─┤C1├─
    └──┘
    ┌──┐
   ─┤C2├─  → V_total = V1 (same), I_total = I1+I2+...
    └──┘
    ┌──┐
   ─┤C3├─
    └──┘
```

**Series-Parallel (Hybrid):**
```
Groups of series cells in parallel

  ┌─────┐   ┌─────┐
  │C1-C5│   │C6-C10│  → Balance voltage/current
  └─────┘   └─────┘
```

---

### Stack Sizing

**Number of Cells:**
```
N_cells = V_system / U_cell
```

**Example for 500 V system:**
```
N_cells = 500 V / 1.8 V ≈ 278 cells
```

**Stack Length:**
```
L_stack = N_cells × t_cell
```

With t_cell ≈ 3-5 mm:
```
L_stack = 278 × 4 mm ≈ 1.1 m
```

**Stack Configurations:**

| Application | N_cells | V_stack | I @ 1 A/cm² | Power |
|-------------|---------|---------|-------------|-------|
| Small | 10-20 | 18-36 V | 50 A | 1-2 kW |
| Medium | 50-100 | 90-180 V | 100 A | 10-20 kW |
| Large | 100-200 | 180-360 V | 200 A | 40-80 kW |
| Industrial | 200-500 | 360-900 V | 500 A | 200-500 kW |

---

### Manifold Design

**Purpose:**
- Distribute water to all cells
- Collect H₂ from cathodes
- Collect O₂ from anodes
- Maintain pressure balance

**Configurations:**

**U-Configuration:**
```
Inlet →  [C1] [C2] [C3] → Outlet
         │________________│
```

**Z-Configuration:**
```
Inlet →  [C1] [C2] [C3]
                     │
         └───────────┘ Outlet
```

**Parallel Manifold:**
```
         [C1]
Inlet →  [C2]  → Outlet
         [C3]
```

**Manifold Sizing:**

Manifold cross-section area:
```
A_manifold ≈ N_cells × A_channel / 4
```

Ensure uniform pressure:
```
Δp_manifold << Δp_channel  (typically < 10%)
```

---

### Flow Distribution

**Maldistribution Factor:**
```
M = Q_max / Q_avg
```

M < 1.1 is desirable (< 10% variation)

**Ways to Improve:**
1. Larger manifold diameter
2. Symmetric design
3. Flow restrictors/orifices
4. Computational optimization (CFD)

---

## Design Optimization

### Pressure Drop Considerations

**Total Pressure Drop:**
```
Δp_total = Δp_channels + Δp_manifold + Δp_GDL
```

**Typical Values:**
- Per cell: 50-200 mbar
- Stack (100 cells): 0.5-2 bar

**Pumping Power:**
```
P_pump = Δp · Q_water / η_pump
```

- Should be < 2% of stack power
- Typically: 50-200 W for 10 kW system

---

### Heat Management

**Cooling Strategies:**

1. **Reactant Cooling:**
   - Water flow through channels
   - Simple, but limited

2. **Separate Cooling Plates:**
   - Dedicated cooling cells
   - Every 5-10 cells
   - Better control

3. **Integrated Cooling:**
   - Cooling channels in BPP
   - Complex, but effective

**Cooling Water Flow:**
```
Q_cool = Q_stack / η_thermal
```

Typical: 50-200 ml/min per kW

---

### Current Distribution

**Uniformity Factors:**
- Contact resistance variation
- Temperature gradients
- Flow distribution

**Bus-Bar Design:**
- Minimize current path length
- Use high-conductivity materials (Cu, Al)
- Adequate cross-section (avoid heating)

---

### Mechanical Design

**Clamping Force:**
```
F_clamp = P_contact × A_cell
```

Typical: 1-3 MPa contact pressure

**Stress Management:**
- Uniform compression
- Avoid point loads
- Use torque-controlled bolts

**Bolt Pattern:**
```
Number of bolts ≈ (Perimeter) / (100-150 mm)
```

Example for 200×200 mm:
```
N_bolts ≈ 800 / 120 ≈ 6-8 bolts
```

---

### Optimization Workflow

```
1. Define Requirements
   ├─ Power output
   ├─ Voltage/current
   └─ Size constraints

2. Select Flow Field
   ├─ Serpentine (uniformity)
   ├─ Parallel (low Δp)
   └─ Interdigitated (mass transport)

3. Size Active Area
   ├─ Current density
   └─ Number of cells

4. Design Manifold
   ├─ Flow distribution
   └─ Pressure balance

5. Thermal Design
   ├─ Cooling strategy
   └─ Temperature uniformity

6. Mechanical Design
   ├─ Clamping
   ├─ Sealing
   └─ Structural analysis

7. Simulate & Iterate
   ├─ CFD analysis
   ├─ FEM stress
   └─ Electrochemical model
```

---

## Summary

**Design Selection Guide:**

| Application | Flow Field | Active Area | Stack Size |
|-------------|------------|-------------|------------|
| **Lab/Research** | Serpentine | 5-25 cm² | 1-5 cells |
| **Portable** | Parallel | 25-100 cm² | 5-20 cells |
| **Stationary** | Interdigitated | 100-500 cm² | 50-100 cells |
| **Industrial** | Hybrid | 500-2000 cm² | 100-500 cells |

**Key Trade-offs:**
- Uniformity vs Pressure drop
- Performance vs Complexity
- Size vs Manufacturability
- Cost vs Performance

---

**Previous:** [Materials & Components](03-materials-components.md)  
**Next:** [Water Management](05-water-management.md)
