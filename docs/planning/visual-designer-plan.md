# Visual Stack Designer — Implementation Plan

Target: v0.4.0 feature. 3–5 working days, one developer. Stays inside Streamlit + Plotly. Reuses all existing `materials.py` specs; adds only what today has no data source.

---

## 1. Component inventory (new specs to add)

### 1.1 Bipolar Plate — `BipolarPlateSpec`

```python
@dataclass(frozen=True)
class BipolarPlateSpec:
    name: str
    material: str                    # "titanium" | "graphite-composite" | "stainless-316L"
    thickness_m: float               # Plattendicke [m], SI
    flow_pattern: str                # "serpentine" | "parallel" | "interdigitated"
    channel_width_m: float           # [m]
    channel_depth_m: float           # [m]
    channel_pitch_m: float           # [m]  (land_width = pitch − channel_width)
    density_kg_m3: float             # für Stack-Masse
    bulk_resistivity_ohm_m: float    # el. Durchgangswiderstand, SI
    ref: str
```

**Presets (4):**

| Name | Material | Thickness [mm] | Pattern | Ch W / D / Pitch [mm] | ρ_bulk [Ω·m] | Ref |
|---|---|---|---|---|---|---|
| Ti-serpentine (EC standard) | titanium | 2.0 | serpentine | 1.0 / 1.0 / 2.0 | 4.3e-7 | Lettenmeier 2016, EES 9(8) |
| Ti-parallel (low-ΔP) | titanium | 2.0 | parallel | 1.2 / 0.8 / 2.4 | 4.3e-7 | Grigoriev 2009, IJHE 34(14) |
| Graphite (PEMFC-like) | graphite-composite | 3.0 | serpentine | 1.0 / 1.0 / 2.0 | 1.3e-4 | Barbir 2012, Ch. 4.3 |
| SS-316L (cost-optimized) | stainless-316L | 1.5 | parallel | 1.0 / 0.8 / 2.0 | 7.4e-7 | Wang 2011, IJHE 36(16) |

### 1.2 End Plate — `EndPlateSpec`

```python
@dataclass(frozen=True)
class EndPlateSpec:
    name: str
    material: str                    # "stainless-316L" | "aluminum-6061"
    thickness_m: float               # typ. 10–40 mm (dominiert Stack-Höhe)
    density_kg_m3: float
    ref: str
```

**Presets (2):** SS-316L 20 mm (ρ=7990); Al-6061 25 mm (ρ=2700). Ref: Barbir 2012, Ch. 6.3.

### 1.3 Current Collector — `CurrentCollectorSpec`

```python
@dataclass(frozen=True)
class CurrentCollectorSpec:
    name: str
    material: str                    # "copper-Au-plated" | "copper-Ni-plated"
    thickness_m: float
    bulk_resistivity_ohm_m: float
    ref: str
```

**Presets (2):** Cu-Au 1.0 mm (ρ=1.7e-8); Cu-Ni 1.5 mm (ρ=1.7e-8 Bulk + Ni-Layer). Ref: Barbir 2012.

### 1.4 Gasket — `GasketSpec`

```python
@dataclass(frozen=True)
class GasketSpec:
    name: str
    material: str                    # "PTFE" | "EPDM" | "Viton-FKM"
    thickness_m: float               # 100–500 µm
    compressed_thickness_m: float    # nach 30 % Kompression (für Stack-Höhe)
    frame_width_m: float             # Rahmen-Breite um Active Area [m], typ. 5–10 mm
    ref: str
```

**Presets (3):** PTFE 250 µm (comp. 200 µm, frame 5 mm); EPDM 500 µm (comp. 350 µm, 8 mm); Viton 300 µm (comp. 220 µm, 5 mm). Ref: Carmo 2013, §5.1.

### 1.5 Tie-Rod — `TieRodSpec`

```python
@dataclass(frozen=True)
class TieRodSpec:
    name: str                        # "M8×4" | "M10×8" | "M12×6"
    thread_size: str
    diameter_m: float
    count: int                       # typ. 4, 6, 8, 12
    torque_nm: float                 # Anzugsmoment für Dichtkraft
    material: str                    # "stainless-316L" | "titanium"
    ref: str
```

**Presets (3):** M8×4 / M10×8 / M12×6, alle SS-316L. Ref: Barbir 2012, Ch. 6.3.

---

## 2. File structure (new & modified files)

```
pem-ec-0d/
├── src/
│   ├── components.py          [NEW] Dataclasses + presets für BPP, End Plate, CC, Gasket, Tie-Rod
│   ├── assembly.py            [NEW] StackAssembly dataclass + JSON save/load + Höhen-/Massen-Aggregation
│   ├── visualization.py       [NEW] Plotly-Zeichenfunktionen (Querschnitt, BPP Top, Gasket-Overlay)
│   ├── materials.py           [MOD] unverändert gelassen (DRY); Assembly referenziert Presets von hier
│   ├── electrochemistry.py    [MOD] optionaler BPP-Material-Multiplikator im R_contact-Term
│   ├── stack.py               [MOD] `from_assembly(a: StackAssembly)`-Konstruktor
│   ├── thermal.py             [MOD] Masse-Berechnung nutzt Assembly-Massen für Aufwärmzeit (v0.5-Hook)
│   └── streamlit_app.py       [MOD] neuer 6. Tab "Assembly"
├── tests/
│   ├── test_components.py     [NEW] Spec-Validierung, Preset-Konsistenz
│   ├── test_assembly.py       [NEW] Höhen-Summe, JSON-Roundtrip, BPP-Area = Active-Area + 2·frame
│   └── test_visualization.py  [NEW] Headless Figure-Erzeugung (smoke test, no rendering)
└── docs/adr/
    └── 006-visual-stack-designer.md   [NEW] ADR für Scope, Technologie-Wahl, Coupling-Entscheidungen
```

---

## 3. Function signatures (public API)

### `src/components.py`

```python
from dataclasses import dataclass

# Dataclasses aus §1 (BipolarPlateSpec, EndPlateSpec, CurrentCollectorSpec, GasketSpec, TieRodSpec)

BIPOLAR_PLATES: dict[str, BipolarPlateSpec] = {...}
END_PLATES: dict[str, EndPlateSpec] = {...}
CURRENT_COLLECTORS: dict[str, CurrentCollectorSpec] = {...}
GASKETS: dict[str, GasketSpec] = {...}
TIE_RODS: dict[str, TieRodSpec] = {...}

def bipolar_plate_names() -> list[str]: ...
def end_plate_names() -> list[str]: ...
def current_collector_names() -> list[str]: ...
def gasket_names() -> list[str]: ...
def tie_rod_names() -> list[str]: ...

def land_width_m(bpp: BipolarPlateSpec) -> float:
    """Land-Breite = Pitch − Channel-Width. Open-Area-Ratio = Ch/Pitch."""

def open_area_ratio(bpp: BipolarPlateSpec) -> float:
    """Anteil offener Kanal-Fläche an BPP-Fläche [dimensionslos 0..1]."""
```

### `src/assembly.py`

```python
from dataclasses import dataclass, asdict
import json
from pathlib import Path

@dataclass(frozen=True)
class StackAssembly:
    """Vollständige Bauteil-Konfiguration eines Stacks. Alle Referenzen per Preset-Name."""
    n_cells: int
    active_area_m2: float
    membrane: str                    # Key in MEMBRANES
    anode_catalyst: str
    cathode_catalyst: str
    anode_gdl: str
    cathode_gdl: str
    bipolar_plate: str               # Key in BIPOLAR_PLATES
    end_plate: str
    current_collector: str
    gasket: str
    tie_rod: str

def total_stack_height_m(a: StackAssembly) -> float:
    """Σ Dicken aller Layer × N_cells + End Plates + Current Collectors. SI."""

def total_stack_mass_kg(a: StackAssembly) -> float:
    """Gesamtmasse für Stack-Transport und Wärme-Kapazität (v0.5 thermal-dynamic hook)."""

def bpp_outer_dimensions_m(a: StackAssembly) -> tuple[float, float]:
    """Kantenlänge der quadratischen BPP: sqrt(active_area) + 2·frame_width. Return (width, height)."""

def to_json(a: StackAssembly, path: Path) -> None: ...
def from_json(path: Path) -> StackAssembly: ...

def default_assembly() -> StackAssembly:
    """N=5, 50 cm², Nafion 212, IrO2, Pt/C, Ti-serp, SS-endplate, ..."""
```

### `src/visualization.py`

```python
from plotly.graph_objects import Figure
from src.assembly import StackAssembly

def draw_layer_cross_section(a: StackAssembly, *, max_visible_cells: int = 6) -> Figure:
    """
    Seitenansicht, maßstabsgetreu (log-Scale optional für dünne Katalysator-Layer).
    Wenn N > max_visible_cells: zeigt 3 Zellen oben + "… N-6 weitere …" + 3 Zellen unten.
    X-Achse: Dicke [mm]. Y-Achse: Layer-Position (0 unten).
    Farb-Kodierung per Komponenten-Typ. Hover: name + thickness + ref.
    """

def draw_bpp_top_view(
    bpp_name: str,
    active_area_m2: float,
    gasket_name: str,
    *,
    resolution_px: int = 600,
) -> Figure:
    """
    Draufsicht mit SVG-Shapes: BPP-Außenkontur, Gasket-Rahmen, Flow-Field-Pattern.
    Pattern aus bpp.flow_pattern:
      - "serpentine":    meander, einbahnig
      - "parallel":      N parallele Kanäle (N = W_active / pitch)
      - "interdigitated": abwechselnd Inlet/Outlet-Finger, Länge = 0.9·W_active
    Inlet/Outlet-Ports als Kreise in diagonalen Ecken.
    """

def draw_gasket_outline(
    gasket_name: str,
    active_area_m2: float,
) -> Figure:
    """
    Standalone: Gasket-Shape isoliert. Nützlich für Material-Tab zusätzlich zu Assembly.
    """

def draw_assembly_summary(a: StackAssembly) -> Figure:
    """
    3-Panel-Figure: links Querschnitt, mittig BPP-Top, rechts Info-Panel mit Höhe/Masse/Zellanzahl.
    Für Export-Tab als PNG.
    """
```

### `src/streamlit_app.py` (Änderungen, nicht Gesamtsignatur)

```python
def render_assembly_tab(sidebar_defaults: dict) -> None:
    """Neuer Tab 6: Assembly Designer. Liest Sidebar-Werte (T, p, j, Area, N), rendert Preview + BPP-Top."""
```

---

## 4. UI layout — Assembly Tab (Tab 6)

Neuer Tab **"Assembly"** ganz rechts. Materials-Tab bleibt unverändert (Preset-Details), Assembly ist Zusammenbau + Geometrie.

```
┌─ Sidebar (UNVERÄNDERT) ───────────────────────────────────────────┐
│ T, p, j, λ/λ_max, Active Area (cm²), N_cells, Materials (6 DDs)   │
└───────────────────────────────────────────────────────────────────┘

┌─ Tab 6: Assembly ─────────────────────────────────────────────────┐
│                                                                   │
│  Column 1 (1/4)             Column 2 (3/4)                        │
│  ┌──────────────────────┐   ┌──────────────────────────────────┐  │
│  │ ▼ Bipolar Plate      │   │  [Plotly: Layer Cross-Section]   │  │
│  │   Ti-serpentine  ▼   │   │  Side view, to scale             │  │
│  │                      │   │  N=5 cells, hover for specs      │  │
│  │ ▼ End Plate          │   │                                  │  │
│  │   SS-316L 20 mm  ▼   │   └──────────────────────────────────┘  │
│  │                      │                                         │
│  │ ▼ Current Coll.      │   ┌──────────────────────────────────┐  │
│  │   Cu Au-plated   ▼   │   │  [Plotly: BPP Top View]          │  │
│  │                      │   │  Active area + gasket + ports    │  │
│  │ ▼ Gasket             │   └──────────────────────────────────┘  │
│  │   PTFE 250 µm    ▼   │                                         │
│  │                      │   ┌──────────────────────────────────┐  │
│  │ ▼ Tie-Rod            │   │ Stack stats (KPI cards):         │  │
│  │   M10 × 8        ▼   │   │  Height: 143.4 mm                │  │
│  │                      │   │  Mass:    2.81 kg                │  │
│  │ ──────────────────   │   │  BPP:   78 × 78 mm               │  │
│  │ Custom dimensions:   │   │  Open-area ratio: 50 %           │  │
│  │ [Ch width]  1.0 mm   │   └──────────────────────────────────┘  │
│  │ [Ch pitch]  2.0 mm   │                                         │
│  │ [Ch depth]  1.0 mm   │   [ Save config ]  [ Load config ]      │
│  │ [Torque]   12 N·m    │   [ Export PNG  ]                       │
│  └──────────────────────┘                                         │
└───────────────────────────────────────────────────────────────────┘
```

**Widget-Liste (konkret):**

| Widget | Typ | Default | Quelle |
|---|---|---|---|
| BPP preset | `st.selectbox` | "Ti-serpentine (EC standard)" | `components.bipolar_plate_names()` |
| End Plate preset | `st.selectbox` | "SS-316L 20 mm" | ... |
| Current Collector preset | `st.selectbox` | "Cu Au-plated 1 mm" | ... |
| Gasket preset | `st.selectbox` | "PTFE 250 µm" | ... |
| Tie-Rod preset | `st.selectbox` | "M10 × 8" | ... |
| Ch width override | `st.slider` 0.3–3.0 mm | aus Preset | disabled wenn pattern="serpentine" |
| Ch pitch override | `st.slider` 0.8–5.0 mm | aus Preset | |
| Ch depth override | `st.slider` 0.3–2.0 mm | aus Preset | |
| Save config | `st.download_button` | — | JSON via `assembly.to_json()` |
| Load config | `st.file_uploader` | — | JSON via `assembly.from_json()` |

---

## 5. Coupling zu bestehender Physik

| Assembly-Feld | Fließt in | Wie |
|---|---|---|
| `bpp.bulk_resistivity_ohm_m` × `thickness` × 2 (anode+cathode BPP pro Zelle) | `electrochemistry.ohmic_losses_v()` als zusätzlicher `r_bpp` im `r_other_ohm_m2`-Sammelterm | additiv, heute als Sammelkonstante; wird per-Zelle aus Assembly berechnet |
| `gasket.frame_width_m` × `active_area` | `bpp_outer_dimensions_m()` | BPP-Kantenlänge = √A + 2·frame |
| `gasket.compressed_thickness_m` | `total_stack_height_m()` | Addiert zum Layer-Sum pro Zelle |
| `end_plate.thickness_m` × 2 | `total_stack_height_m()` | Oben+Unten Einmal-Addend |
| `current_collector.thickness_m` × 2 | `total_stack_height_m()` | Einmal-Addend |
| `bpp.open_area_ratio` | **DISPLAY ONLY** heute | Hook für v0.5 Mass-Transport-Korrektur |
| `tie_rod.count`, `torque_nm` | **DISPLAY ONLY** | Hook für v1.0 FEM-Dichtkraft-Modell |
| `bpp.flow_pattern` | **DISPLAY ONLY** | Hook für v0.5 ΔP-Schätzung |
| `*.density_kg_m3` | `total_stack_mass_kg()` | neue Funktion, kein Physik-Einfluss in v0.4 |

**Entscheidung:** Nur `bulk_resistivity` und Geometrie sind Physik-Konsumer in v0.4. Rest ist Display + ADR-dokumentierter Hook für Folgeversionen. Das hält den Merge klein und reviewbar.

---

## 6. Implementation phases (5 Tage max)

### Phase 1 — Components-Modul (Tag 1)
**Deliverable:** `src/components.py` mit 5 Dataclasses, 14 Presets, 5 Accessor-Funktionen.
**pytest:** `test_components.py` — jedes Preset hat positive Dicken, alle Refs non-empty, open_area_ratio ∈ (0, 1).
**Commit:** `feat(components): add BPP/gasket/endplate/currentcollector/tierod specs with 14 presets`

### Phase 2 — Assembly + Coupling (Tag 2)
**Deliverable:** `src/assembly.py` (StackAssembly + Aggregation + JSON). Kleiner Patch in `electrochemistry.py` (r_bpp in ohmic term), Feld in `CellSpec` für `bpp_resistance_ohm_m2`.
**pytest:** `test_assembly.py` — Höhe = Σ(Layer × N) + 2·EndPlate + 2·CC; BPP-Außenmaß konsistent; JSON roundtrip; r_bpp erhöht U_cell monoton.
**Commit:** `feat(assembly): StackAssembly with height/mass aggregation and physics coupling`

### Phase 3 — Visualization-Modul (Tag 3)
**Deliverable:** `src/visualization.py` mit `draw_layer_cross_section`, `draw_bpp_top_view`. Flow-Patterns als SVG-Shapes (keine Bilder). N>6 → compressed view mit "…".
**pytest:** `test_visualization.py` — Figures erzeugt ohne Exception für alle 4 BPP-Presets × 3 Patterns × N ∈ {1, 5, 50, 200}.
**Commit:** `feat(viz): Plotly cross-section and BPP top-view renderers`

### Phase 4 — Streamlit-Tab + Save/Load (Tag 4)
**Deliverable:** `render_assembly_tab()` in `streamlit_app.py`, neuer Tab 6, alle Widgets aus §4, Save/Load via JSON-Download/-Upload.
**Manual check:** `streamlit run src/streamlit_app.py` — Tab rendert, Dropdown-Wechsel ändert Cross-Section live, Save/Load roundtrip funktioniert.
**Commit:** `feat(ui): Assembly tab with visual designer and config save/load`

### Phase 5 — ADR + Dokumentation + Release (Tag 5)
**Deliverable:** `docs/adr/006-visual-stack-designer.md` (Scope, Plotly-vs-JS-Entscheidung, Display-Only-Felder dokumentiert). Update README + MODEL_CARD + CHANGELOG. Tag `v0.4.0`.
**pytest:** alle 98 + ~15 neue Tests grün.
**Commit:** `docs: ADR-006 and v0.4.0 release notes`

---

## 7. Test plan (neu, ~15 Tests)

**`test_components.py` (5):**
1. Alle 14 Presets haben positive Dicken und Density
2. `open_area_ratio` ∈ (0, 1) für alle 4 BPPs
3. `land_width_m = pitch − channel_width` > 0
4. `gasket.compressed < gasket.uncompressed` für alle 3 Gaskets
5. Jeder Preset hat `ref` non-empty

**`test_assembly.py` (7):**
1. Default-Assembly: alle Refs auflösbar in `materials.py` + `components.py`
2. `total_stack_height_m`: Σ(2·BPP + 2·GDL + 2·Cat + Mem + 2·Gasket) × N + 2·EndPlate + 2·CC — numerisch gegen Handrechnung
3. `total_stack_mass_kg` skaliert linear mit N (Endplate-Konstante abgezogen)
4. `bpp_outer_dimensions_m` = √A + 2·frame
5. JSON roundtrip: `to_json → from_json` identisch (frozen dataclass → dataclasses.asdict vergleich)
6. Load einer manuell editierten JSON mit unbekanntem Preset-Namen → klare `KeyError` mit Preset-Name
7. `r_bpp_ohm_m2` im ohmic loss erhöht U_cell monoton mit BPP-Dicke

**`test_visualization.py` (3):**
1. `draw_layer_cross_section` erzeugt Figure mit ≥ 5 Layern für N=1 (Anode BPP, GDL, Cat, Mem, Cat, GDL, Cat BPP)
2. `draw_bpp_top_view` rendert alle 3 Patterns ohne Exception, Shape-Count > 0
3. N=200 → compressed view, Plotly-Shape-Count bounded (< 80 Shapes, keine Lag-Explosion)

---

## 8. Risks and open questions

- **Active-Area vs BPP-Area:** Entschieden → BPP = Active + 2·`gasket.frame_width`, quadratisch. Rechteckige Stacks als v0.5-Item.
- **Rendering N=200:** Compressed-View-Strategie → nur 6 Zellen real, Mitte als graue Box mit "… 194 cells …". Plotly-Shape-Count bleibt < 80. Getestet in Phase 3.
- **Materials-Tab: ersetzen oder ergänzen?** Entschieden → Materials-Tab bleibt (Datenblatt-Ansicht), Assembly-Tab ist zusätzlich. Grund: Materials ist Preset-Reference, Assembly ist Konfiguration. Zwei Sichten auf gleiche Daten.
- **Streamlit-Komponenten-Abhängigkeiten:** KEINE neuen. Pure Plotly-Shapes + `st.selectbox`/`st.slider`/`st.download_button`/`st.file_uploader`. Kein `streamlit-plotly-events` (noch).
- **Flow-Pattern-Override:** Wenn User Kanal-Dimensionen ändert aber Preset-Dropdown fixiert, gewinnt der Slider. Preset-Wechsel setzt Sliders zurück via `st.session_state`.
- **Asset-Lizenzen:** Keine Bilder, keine CAD-Assets — alles als SVG-Shape zur Laufzeit. Null Lizenz-Risiko.
- **Polarisationskurve im Assembly-Tab?** Entschieden (User, 2026-04-20) → **NEIN**. Polarisationskurve bleibt ausschließlich im Polarization-Tab. Assembly-Tab zeigt nur Geometrie + Stack-Stats, damit der Tab nicht überfrachtet wird.

---

## 9. Out-of-scope (NICHT in v0.4)

1. **CFD-Simulation des Flow-Fields** (ΔP, Residence Time, Zwei-Phasen) — PEMFC-Phase-2
2. **CAD-Export (STEP/STL)** — braucht `cadquery` oder `FreeCAD`, eigenes Projekt
3. **Nicht-quadratische Stacks / 3D-Rendering** — v1.0 mit `pyvista`/`three.js`
4. **Dichtkraft-FEM für Tie-Rod-Torque** — v1.0
5. **Multi-Cell-Inhomogenität** (Temperatur-/Strom-Verteilung zwischen Zellen) — v1.0 mit 1D-Stack-PDE
