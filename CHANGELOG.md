# Changelog

All notable changes to `pem-ec-designer` are documented here.
Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) · SemVer.

## [Unreleased]

### Planned (v0.2)
- Stack-Modul: N Zellen in Serie, Gesamtleistung, Stack-Wirkungsgrad
- Membran-Presets (Nafion 212 / 115 / 117, Aquivion, PFSA)
- Tafel-Plot (semi-log) in der UI zur Visualisierung der Validation
- Effizienz-Kurve η_energy(j) neben Polarisationskurve

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
