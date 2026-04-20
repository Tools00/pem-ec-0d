# Changelog

All notable changes to `pem-ec-designer` are documented here.
Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) · SemVer.

## [Unreleased]

### Planned (next)
- Tafel-Plot (semi-log) in der UI zur Visualisierung der Validation
- Effizienz-Kurve η_energy(j) neben Polarisationskurve
- Vergleichs-Modus (2 Zellen/Stacks nebeneinander)
- 2. Validation gegen experimentelle Paper-Kurve

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

[Unreleased]: https://github.com/Tools00/pem-ec-designer/compare/v0.3.1...HEAD
[0.3.1]: https://github.com/Tools00/pem-ec-designer/compare/v0.3.0...v0.3.1
[0.3.0]: https://github.com/Tools00/pem-ec-designer/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/Tools00/pem-ec-designer/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/Tools00/pem-ec-designer/releases/tag/v0.1.0
