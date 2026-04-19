# Changelog

All notable changes to `pem-ec-designer` are documented here.
Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) · SemVer.

## [Unreleased]

### Planned (v0.3)
- Tafel-Plot (semi-log) in der UI zur Visualisierung der Validation
- Effizienz-Kurve η_energy(j) neben Polarisationskurve
- Vergleichs-Modus (2 Zellen/Stacks nebeneinander)
- 2. Validation gegen experimentelle Paper-Kurve

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

### Planned (v0.5)
- 0D-Thermal-Bilanz (stationär)
- Material-Datenbank (SQLite)
- Parameter-Sweeps mit Heatmap-Visualisierung
- Kosten-Schätzer (CAPEX/OPEX, €/kg H2)
- Validation gegen experimentelle Paper-Kurve (#2)
- CI/CD via GitHub Actions (pytest + ruff)
- `pyproject.toml` + `uv` statt `requirements.txt`

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

[Unreleased]: https://github.com/USER/pem-ec-designer/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/USER/pem-ec-designer/releases/tag/v0.1.0
