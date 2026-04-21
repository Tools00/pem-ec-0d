# Changelog

All notable changes to `pem-ec-0d` are documented here.
Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) · SemVer.

## [Unreleased]

## [0.6.0] — 2026-04-21

v0.6 friert das 0D-Referenzmodell ein. Exploded-View für Querschnitts-
Visualisierung, Meta-Dokumentation auf Workspace-Ebene zentralisiert,
Repo-Rename `pem-ec-designer` → `pem-ec-0d` um den Namen
`pem-ec-designer` für das Nachfolgeprojekt (CAD/3D-Designer) freizugeben.

### Changed
- **chore: rename project to `pem-ec-0d`** — Paket, Pfade, Docs, CI-Targets.
  `pem-ec-designer` ist ab sofort für Projekt 2 reserviert.

### Added (v0.6a — exploded-view slider)
- **`draw_layer_cross_section(..., explosion_mm=0.0)`**: neuer optionaler
  Parameter in `src/visualization.py`. 0.0 = assembled (v0.5-Verhalten
  unverändert). > 0.0 = Luft-Gap nach jedem Layer, gestrichelte graue
  Guide-Lines zwischen Layer-Nachbarn. Layer-Dicken bleiben maßstabsgetreu.
- **Streamlit Assembly-Tab**: Slider „Exploded view — gap between layers
  [mm]" über dem Querschnitt-Chart, 0…5 mm in 0.1er-Schritten.
- **2 neue Tests** (163 + 2 xfail): `test_cross_section_exploded_view_grows_extent`,
  `test_cross_section_explosion_negative_raises`.
- **Scope-Entscheidung:** kein v0.6b (Isometrische Pseudo-3D) und kein
  pyvista/STL-Import in diesem Projekt. Weitergehende 3D-/CAD-Visualisierung
  gehört ins Nachfolgeprojekt mit bewusster Framework-Wahl. Rationale in
  Workspace-Docs (siehe unten).

### Docs — Meta (verschoben auf Workspace-Ebene)
- **`Simulation-tools/docs/lessons/pem-ec-0d.md`**: Ehrliche Chronik aller Entscheidungen,
  Strukturfehler und ihrer Ursachen aus pem-ec-0d v0.1–v0.6.
  Fünf dokumentierte Strukturfehler mit Root-Cause-Analyse:
  Framework ohne Trade-off-Analyse, Validation als Feature-Item,
  Visualisierung ohne Ziel-State, Preset-System zu spät geplant,
  fehlende Ziel-Nutzer-Definition.
- **`Simulation-tools/docs/simulation-project-framework.md`**: Allgemeines Framework
  für zukünftige Simulations-Projekte, direkt anwendbar.
  Enthält: 8 Pflichtfragen vor erstem Commit, Framework-Auswahlmatrix,
  Architektur-Prinzipien (Layer-Trennung, SI-Disziplin, Preset-System,
  Literatur-Referenzierung), Validierungs-Framework (Strict-Xfail-Strategie,
  Gate-Modell), Dokumentations-Framework, Fehler-Abwehr-Tabelle,
  Projekt-Start-Checkliste.
- **`docs/meta/README.md`** (im Projekt): Pointer auf die Workspace-Docs.
  Die eigentlichen Inhalte liegen eine Ebene höher, damit Nachfolgeprojekte
  direkt davon lernen. Workspace-CLAUDE.md + README reflektieren die
  neue Regel „Code bleibt im Projekt, Lehren werden zentralisiert".

## [0.5.0] — 2026-04-21

Phases 1-3 abgeschlossen: Fluid-Modul + Pumpen-Kopplung, rechteckige
Stacks, Literatur-Validation mit Zero-Fit-Property. Test-Suite wächst
von 123 auf 161 Tests + 2 strict-xfail (dokumentierte Kalibrierungs-
Targets für v0.6).

### Added (v0.5 Phase 1 — fluid module + pump coupling)
- **`src/fluid.py`** — neues Modul mit Hagen-Poiseuille-Druckverlust im
  laminaren Regime + Darcy-Weisbach-Warnung für turbulente Kanäle
  (Re > 2000). Pure functions, Assembly-frei testbar.
- **Stoichiometrische Wasser-Flussberechnung** aus Faraday-Strom × λ,
  angekoppelt an die Anoden-Kanal-Geometrie aus `BipolarPlateSpec`.
- **`assembly.assembly_pressure_drop` + `assembly_pump_power_w`** als
  dünne Komposition über `fluid.*`.

### Added (v0.5 Phase 2 — rectangular stacks + ΔP in UI)
- **`aspect_ratio` auf `StackAssembly`** (`src/assembly.py`): dimensionslos,
  default 1.0 (quadratisch = v0.4-Verhalten). `active_dimensions_m(a) → (w, h)`
  mit `w·h = active_area_m2` und `w/h = aspect_ratio`. BPP-Außenmaße folgen
  als `(w + 2·frame, h + 2·frame)` — echte rechteckige Plates.
  - v0.4-JSONs ohne `aspect_ratio`-Feld laden weiterhin als quadratisch (Default).
- **Fluid-Kopplung** (`src/assembly.py`): `assembly_pressure_drop(a, *, current_a,
  temperature_k, stoich_ratio)` berechnet ΔP über `fluid.pressure_drop` mit
  aktiven Dimensionen aus `aspect_ratio`. `assembly_pump_power_w(...)` liefert
  Stack-Pumpenleistung (alle N Zellen hydraulisch parallel, Q_total = N·Q_cell).
- **Streamlit Assembly-Tab**: neuer Block „Flow field — pressure drop & pump
  power" mit λ- und η_pump-Slidern, Metrics für ΔP [kPa], v [cm/s], Re, Pump
  [W] + Parasit-Anteil der Stack-Leistung. Turbulenter Regime (Re > 2000)
  liefert saubere Warnung statt Crash.
- **Streamlit Sidebar**: `aspect_ratio`-Slider 0.25…4.0; Caption zeigt
  resultierende w × h der aktiven Fläche. Area bleibt beim Drehen konstant.
- **13 neue Tests** (total 157): aspect_ratio area-preserving, ΔP-Linearität
  in I, Pump-Power ∝ N, serpentine > parallel ΔP, JSON-Roundtrip mit
  aspect_ratio, Legacy-JSON-Kompat, rechteckige BPP-Visualization.
- **Rechteckiges Flow-Field-Rendering** (`src/visualization.py`):
  `_draw_flow_pattern` nimmt `width_mm`+`height_mm` statt `edge_mm`. Bei
  aspect_ratio ≠ 1.0 zeichnen alle drei Pattern (parallel, serpentine,
  interdigitated) auf rechteckiger Fläche.

### Added (v0.5 Phase 3 — Bernt 2020 validation baseline)
- **Validation-Dataset** `tests/data/bernt_2020_fig1.csv`: 15 Punkte der
  Polarisationskurve aus Bernt et al. (2020) *Chem. Ing. Tech.* 92(1-2),
  Fig. 1, rote durchgezogene Linie (2 mg Ir/cm², gemessen) — 80 °C, Nafion
  212, 1 bar. Digitalisiert per Screenshot-Abfrage, ±20 mV Genauigkeit,
  Paper Open Access (CC-BY).
- **Validation-Test** `tests/test_validation_bernt2020.py` mit drei Tests:
  - Dataset-Sanity (Load, Monotonie, physikalischer Wertebereich) — PASS.
  - Low-j Shape-Match (j ≤ 0.1 A/cm², RMSE < 50 mV) — PASS bei ~35 mV RMSE.
    Bestätigt dass Butler-Volmer + Nernst + Ohm die Tafel-Region korrekt
    abbildet.
  - Full-range RMSE-Target 40 mV — **strict xfail** bei ~510 mV RMSE.
    Residual-Wachstum monoton in j: Model überschätzt R_ohm und unterschätzt
    j₀ für Bernt's Premium-Setup. Keine heimliche Kalibrierung — Rationale
    dokumentiert.
- **Neues Doc** `docs/validation/bernt2020_v0.5.md`: Diagnose, warum xfail
  statt Fit, Plan für v0.6-Preset-System (`IrO2_generic` vs
  `IrO2_TiO2_Umicore_Elyst_Ir75`).

### Added (v0.5 Phase 3 — Zimmer 2026 statistical validation)
- **Validation-Dataset** `tests/data/zimmer_2026_fig1c.csv`: 5 Benchmark-Punkte
  aus Zimmer et al. (2026) *J. Electrochem. Soc.* 173, 024503, Fig. 1c
  (gefiltert auf Nafion N115 + 80 °C, aggregiert über >127 peer-reviewed
  Publikationen 2006-2024). Je Punkt: Mittelwert, σ, [min, max] der
  Literatur-Zell-Spannung bei j ∈ {0.2, 0.5, 1.0, 1.5, 2.0} A/cm². Open
  Access (CC-BY 4.0).
- **Validation-Test** `tests/test_validation_zimmer2026.py` mit drei Tests:
  - Dataset-Sanity (Load, Monotonie, σ > 0, min < mean < max) — PASS.
  - **Envelope-Test**: Model-Vorhersage bei jedem Benchmark-j innerhalb
    [E_min, E_max] — **PASS**. Zero-Fit-Model ist literatur-konsistent, kein
    struktureller Outlier.
  - ±1σ-Band-Test — **strict xfail** (4/5 Punkten außerhalb, Bias +175 mV,
    RMSE vs Mean 210 mV). Konsistent mit Bernt-Overshoot: selbe
    Wurzelursache (Carmo 2013 generic-commercial defaults).
- **Neues Doc** `docs/validation/zimmer2026_v0.5.md`: Warum statistische
  Validation > Single-Paper-RMSE (Zimmer-Zitat: σ oft > 500 mV, max-Spread
  bis 1.5 V), Interpretation der ±σ-Abweichung, v0.6-Pfad (Katalysator- +
  Membran- + Kontakt-Preset-Systeme).
- **Cross-Referenz** in `docs/validation/bernt2020_v0.5.md`: neuer Abschnitt
  „Context from Zimmer 2026 — why single-paper RMSE is fraught" macht die
  510-mV-Bernt-Abweichung durch Zimmer's Literatur-Varianz statistisch
  einordbar.

### Docs (v0.5 Phase 3 — ADR)
- **ADR-007** `docs/adr/007-v0.5-architecture.md`: Entscheidungs-Record
  für die drei orthogonalen v0.5-Erweiterungen (Fluid-Modul, rechteckige
  Stacks, Zero-Fit-Validation mit strict-xfail). ADR-Index aktualisiert.

### Deferred (v0.6)
- Katalysator-Preset-System: `IrO2_generic` vs `IrO2_TiO2_Umicore_Elyst_Ir75`,
  mit unabhängig extrahierten kinetischen Parametern (nicht aus Fig.-1-Fit).
- Membran-Preset-Tabelle erweitern (`Nafion 115` + Springer-Leitfähigkeit
  gegen Zimmer's gefilterten N115-Korpus verifizieren).
- Kontakt-Resistenz-Preset: `generic_commercial` vs `research_grade`.
- Flip beider strict-xfail-Tests zu normalen Asserts, sobald Bernt-RMSE
  < 60 mV und Zimmer innerhalb ±1σ an allen 5 j.

## [0.4.1] — 2026-04-20

### Changed
- **BPP → Ohmic-loss wire-up** (`src/streamlit_app.py`, `src/assembly.py`):
  - Bipolar-plate-Picker wandert in die Sidebar (Single Source of Truth für
    Polarization- und Assembly-Tab).
  - `r_bpp = ρ · t` der gewählten BPP fließt jetzt in
    `Electrochemistry.from_engineering(..., r_bpp_ohm_cm2=...)` und damit in
    die Polarisationskurve, statt den alten CellSpec-Default zu verwenden.
  - Beispiel: Graphit-Composite-BPP (3 mm, ρ=1.3e-4 Ω·m) erzeugt ~0.39 mΩ·cm²
    Beitrag vs. ~0.086 µΩ·cm² bei Ti-BPP (2 mm, ρ=4.3e-7 Ω·m) — im
    Ohm-Term jetzt sichtbar.
- Assembly-Tab zeigt gewählte BPP als Caption (aus Sidebar), lokaler
  Selectbox entfernt. Caption im Stack-Stats-Bereich: "active in Polarization tab".

### Added
- **1 neuer Test** (total 123): `test_bpp_resistance_wires_into_electrochemistry_r_bpp`
  verifiziert, dass `bpp_resistance_ohm_m2(a)` → Electrochemistry.r_bpp 1:1
  übertragen wird.

### Docs
- ADR-006: Tabellen-Zeile „r_bpp-Coupling aktiv?" aktualisiert
  (von „Display-only" → „Ja, wired"), Consequences-Abschnitt entsprechend angepasst.

## [0.4.0] — 2026-04-20

### Added
- **Visual Stack Designer** (6. Tab „Assembly") — siehe
  [ADR 006](docs/adr/006-visual-stack-designer.md):
  - `src/components.py` — 5 neue frozen Dataclasses (BipolarPlateSpec,
    EndPlateSpec, CurrentCollectorSpec, GasketSpec, TieRodSpec) mit
    insgesamt **14 Literatur-referenzierten Presets**
    (4 BPP, 2 Endplatten, 2 Stromabnehmer, 3 Dichtungen, 3 Tie-Rod-Sets).
  - `src/assembly.py` — `StackAssembly`-Dataclass aggregiert alle
    MEA- + Stack-Komponenten, berechnet `per_cell_height`,
    `total_stack_height`, `total_stack_mass`, `bpp_outer_dimensions`,
    `bpp_resistance_ohm_m2`. JSON Save/Load via `to_json`/`from_json`.
  - `src/visualization.py` — Plotly-Zeichenfunktionen:
    - `draw_layer_cross_section` — maßstabsgetreue Seitenansicht in mm
      mit Compressed-View ab N > 6 (grauer „… X cells collapsed …"-Block).
    - `draw_bpp_top_view` — Draufsicht mit Flow-Field-Pattern
      (serpentine/parallel/interdigitated), Gasket-Rahmen, diagonalen
      Inlet/Outlet-Ports.
    - `draw_gasket_outline` — Standalone Gasket-Kontur mit Active-Area-Cutout.
  - **Assembly-Tab** in der Streamlit-UI — 5 Selectbox-Picker
    (BPP/EndPlate/CurrentCollector/Gasket/Tie-Rod), Querschnitt +
    BPP-Top-View, 4 KPI-Metriken (Stack-Höhe, Masse, BPP-Kante,
    Open-Area-Ratio), JSON Download/Upload.
- **21 neue Tests** (total 122, alle grün) — `tests/test_components.py` (7),
  `tests/test_assembly.py` (9), `tests/test_visualization.py` (5).

### Design-Entscheidungen (ADR 006)
- **Pure Streamlit + Plotly** — kein JS, keine React-Komponente, keine
  neue Runtime-Abhängigkeit. Alternativen (React/dnd-kit,
  streamlit-plotly-events, pyvista 3D) dokumentiert verworfen.
- **r_bpp aus Assembly berechnet + angezeigt, noch nicht in CellSpec gewired** —
  Wire-up in v0.4.1, um diesen PR klein + reviewbar zu halten.
- **Rechteckige Stacks bewusst nicht modelliert** (v0.5-Scope).
- **MEA- und Tie-Rod-Masse in Stack-Masse vernachlässigt** (< 5 % bzw. < 1 %),
  explizit dokumentierte Näherung.

### References (neu für v0.4)
- Lettenmeier et al. (2016) Energy Environ. Sci. 9(8), 2569 — Ti-BPP
- Grigoriev et al. (2009) IJHE 34(14), 5986 — Parallel flow fields
- Barbir (2012) PEM Fuel Cells, Ch. 4.3 & 6.3 — Graphit-Composite, Endplatten
- Wang et al. (2011) IJHE 36(16), 10329 — SS-316L als BPP-Material
- Carmo et al. (2013) IJHE 38(12) §5.1 — PTFE/EPDM/FKM Gaskets

## [0.3.1] — 2026-04-20

### Added
- **Materials refresh** (`src/materials.py`) — 10 neue Presets, rein additiv
  (keine bestehenden Presets oder Felder geändert, keine Tests gebrochen):
  - **Membranen (+3):**
    - Gore-Select M820 (reinforced, 18 μm) — ePTFE-verstärkt,
      Industrie-Standard moderner EC-Stacks
    - Nafion XL (reinforced, 27.5 μm) — ePTFE-verstärkte Nafion-Variante
    - Aquivion R79-02S (50 μm, EW 790) — Short-side-chain PFSA
  - **Anoden-Katalysatoren (+3):**
    - Ir-black (Rozain 2016, 0.5 mg/cm²) — Low-loading Referenz
    - IrOx-ATO (Sb-doped SnO₂ Support, 0.3 mg/cm²) — moderner Ersatz für IrO₂-TiO₂
    - Heraeus H2EL-IrO (commercial 2023, 0.6 mg/cm²) — reduzierter Ir-Einsatz
  - **Kathoden-Katalysatoren (+2):**
    - Pt/C ultra-low (0.05 mg/cm²) — HER nicht PGM-limitiert
    - PtRu/C (startup-tolerant, 0.15 mg/cm²) — SU/SD-robust
  - **GDLs/PTLs (+2, anodenseitig):**
    - Ti sintered powder (Mott, 0.25 mm) — kommerzieller Sinter-PTL
    - Au-coated Ti sintered (0.25 mm) — Au-Coating schlägt Pt in Langzeit
- **3 neue Tests** (total 101, alle grün): presence + basic sanity der neuen Presets

### References
- Goswami et al. (2023) J. Power Sources 578 — Gore M820
- Rozain et al. (2016) ACS Catal. 6(3), 1949–1957 — Ir-black low-loading
- Oh et al. (2016) JACS 138; Liu et al. (2022) Nat. Catal. 5 — IrOx-ATO
- Bernt et al. (2020) J. Electrochem. Soc. 167 — Pt/C ultra-low
- Gazdzicki et al. (2020) Appl. Catal. B 265 — PtRu/C SU/SD
- Tao et al. (2024) SusMat; Liu et al. (2018) JES 165(13);
  RSC Energy Advances (2026) D5YA00274E — Ti sintered PTL, Au-coating

## [0.3.0] — 2026-04-20

### Added
- **Springer-Membran-Leitfähigkeit σ(λ, T)** (`src/electrochemistry.py`):
  - `springer_membrane_conductivity(lambda_h2o, temperature_k)`
  - Dynamisch statt statischem Preset — η_ohm nun T- und Hydration-korrekt
  - UI: Hydrations-Slider λ/λ_max ∈ [0.30, 1.00]
  - Siehe [ADR 003](docs/adr/003-springer-membrane-conductivity.md)
- **Arrhenius-Korrektur für Austauschstromdichte j₀(T)** (`src/electrochemistry.py`):
  - `arrhenius_exchange_current_density(j0_ref, E_a, T, T_ref=353.15)`
  - `CatalystSpec.activation_energy_j_mol` neu (Pflichtfeld, kein Default)
  - Alle 6 Katalysator-Presets mit Literatur-E_a aktualisiert
    (IrO₂ 52, IrRuOx 48, IrO₂-TiO₂ 56, Pt/C 25, Pt black 20, PtCo 22 kJ/mol)
  - UI zeigt effektives j₀(T) in der Sidebar
  - Siehe [ADR 004](docs/adr/004-arrhenius-exchange-current-density.md)
- **Full Butler-Volmer** (`src/electrochemistry.py`):
  - `butler_volmer_current_density(eta, j0, alpha, T)` — Vorwärts-BV
  - Newton-Raphson-Löser invertiert BV für η(j), initialisiert mit Tafel-Schätzung
  - `activation_overpotential()` nutzt jetzt den Löser statt Tafel-Formel
  - Bei j ≈ j0 physikalisch korrekt; Tafel-Grenzfall exakt erhalten
  - Siehe [ADR 005](docs/adr/005-full-butler-volmer.md)
- **20 neue Tests** (total 98, alle grün):
  - Springer: 6 (Referenzwert, Monotonie T/λ, Guards, realistischer Nafion)
  - Arrhenius: 8 (Identität, Monotonie, IrO₂-Drop, HER vs OER, 4× Guards)
  - Butler-Volmer: 6 (j(0)=0, Antisymmetrie, Tafel-Limes, Roundtrip, Nahe-j₀, Guards)

### Changed
- `MembraneSpec.conductivity_sm` wird nicht mehr in Berechnung verwendet —
  bleibt als Informationsfeld (Preset bei 80 °C, voll hydratisiert)
- Gültigkeitsbereich Temperatur erweitert: 30–90 °C (vorher: 50–90 °C)
- Gültigkeitsbereich Stromdichte erweitert: 0.01–2.5 A/cm² (vorher: 0.1–2.5)

### References
- Springer, Zawodzinski & Gottesfeld (1991) — J. Electrochem. Soc. 138(8), Eq. 23
- Suermann, Bensmann & Hanke-Rauschenbach (2017) — J. Power Sources 365
- Durst, Siebel, Simon et al. (2014) — Energy Environ. Sci. 7
- Bard & Faulkner (2001) — Electrochemical Methods, Eq. 3.3.11
- Carmo, Fritz, Mergel & Stolten (2013) — Int. J. Hydrogen Energy 38(12), Eqs. 8–9

## [0.2.0] — 2026-04-19

### Added
- **Stack-Modul** (`src/stack.py`) — N identische Zellen in Serie,
  aggregiert U_stack, P_electric, H2-Produktion, Polarisationskurve
- **Materials-Modul** (`src/materials.py`) — Hardcoded Presets mit Refs:
  - 6 Membranen (Nafion 211/212/115/117, Aquivion E98, Fumapem F-950)
  - 3 Anoden-Katalysatoren (IrO2, IrRuOx, IrO2-TiO2)
  - 3 Kathoden-Katalysatoren (Pt/C, Pt black, PtCo/C)
  - 2+2 GDLs (Ti felt/mesh, Carbon paper/cloth)
- **Thermal-0D-Modul** (`src/thermal.py`) — Stationäre Energiebilanz,
  Wärmegenerierung Q = (U − E_tn·η_F)·I, Kühlmittel-Massenstrom
  aus ṁ·cp·ΔT, thermische Effizienz (HHV-Basis)
- **UI-Neustruktur** — 5 Tabs: Polarization · Stack Analysis · Thermal ·
  Materials · Export
- **Stack-Level-KPIs** im Hero-Bereich (U_stack, P_kW, H2 g/h, Q_waste)
- **Material-Dropdowns** statt Slider — Presets für sofortige Verwendung
- **Operating-Point-Summary-Export** (CSV mit allen Kenngrößen)
- **26 neue Tests** (total 78), alle grün:
  - Stack: 8 Tests (Linearität, Skalierung, Monotonie)
  - Materials: 9 Tests (Konsistenz, Ordnung Nafion, Valid Ranges)
  - Thermal: 9 Tests (E_tn-Sanity, Exo/Endotherm, Heat-Balance)

### Changed
- Streamlit-App-Imports umgestellt (absolut statt relativ) für korrekten
  Script-Run ohne Paket-Kontext

### Planned (v0.5)
- Material-Datenbank (SQLite)
- Parameter-Sweeps mit Heatmap-Visualisierung
- Kosten-Schätzer (CAPEX/OPEX, €/kg H2)
- Validation gegen experimentelle Paper-Kurve (#2)

### Planned (v1.0)
- 1D-Membran-PDE (Springer-Modell + Wasser-Transport)
- 2D-Thermal-Verteilung (FEniCS oder FiPy)
- ML-Surrogate (PyTorch) für schnelle Parameter-Sweeps
- Bayesian-Optimizer für Zelldesign
- REST-API für Batch-Simulationen
- Degradations-Modell (Katalysator-Auflösung, Membran-Dünnung)

## [0.1.0] — 2026-04-19

### Added
- Butler-Volmer/Tafel-Approximation für OER (Anode) und HER (Kathode)
- Nernst-Gleichung mit Temperatur- und Druckkorrektur
- Ohmsche Verluste (Membran, GDL anode/cathode, Kontakt, Bipolarplatte)
- Konzentrations-Überspannung (Mass-Transport)
- Effizienz-Metriken (voltage, Faraday, energy, specific energy kWh/kg H2)
- H2-Produktionsrate (mol/s, g/h, Nm³/h)
- Vektorisierte Polarisationskurve
- Streamlit-UI mit Sliders, KPI-Cards, Plotly-Chart, CSV-Export
- SI-strenge Interna, Engineering-Units nur in der UI-Schicht
- 52 Tests (grün): Tafel-Slope-Validation, Monotonie, Nernst-Konsistenz, H2-Scaling, Input-Validation
- Vollständige Theorie-Dokumentation in `docs/theory/` (~3800 Zeilen Markdown)
- CODATA 2018 Konstanten (R, F, E0, dE0/dT, Molmassen, LHV)
- Unit-Conversion-Modul mit Round-Trip-Tests

### Validation
- Tafel-Slope vs. analytisch `b = 2.303·R·T/(α·F)`: Abweichung < 0.5 %
- U_cell bei 80 °C, 10 bar, 1 A/cm²: 1.7–2.1 V (Literatur-konform, Carmo et al. 2013)

### References
- Larminie & Dicks (2003) — Fuel Cell Systems Explained
- Barbir (2012) — PEM Fuel Cells: Theory and Practice
- Carmo et al. (2013) — Int. J. Hydrogen Energy 38(12)
- Springer, Zawodzinski & Gottesfeld (1991) — J. Electrochem. Soc. 138(8)

### Known Limitations
- 0D stationäres Modell (keine räumliche Auflösung)
- Keine Stack-Skalierung
- Keine Thermal-Dynamik
- Keine Degradation
- Keine Multi-phase Flow
- Nur 1 Validation-Datensatz (analytisch, noch nicht gegen Experiment)

[Unreleased]: https://github.com/Tools00/pem-ec-0d/compare/v0.3.1...HEAD
[0.3.1]: https://github.com/Tools00/pem-ec-0d/compare/v0.3.0...v0.3.1
[0.3.0]: https://github.com/Tools00/pem-ec-0d/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/Tools00/pem-ec-0d/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/Tools00/pem-ec-0d/releases/tag/v0.1.0
