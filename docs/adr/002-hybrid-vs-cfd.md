# ADR 002 — Hybrid-Ansatz vs. Full-CFD

**Status:** Accepted — Strategie-Entscheidung für v0.5+
**Date:** 2026-04-19, Erweitert 2026-04-19 (broader reference set)
**Context:** User-Frage: "Können wir mit Open-Source-Python-Stack nahezu ähnliche Ergebnisse wie kommerzielle CFD-Tools (ANSYS Fluent, COMSOL, Siemens STAR-CCM+, AVL Fire M) erzielen?"

## Kurzantwort

**Teilweise ja. Je nach Use Case zwischen 70–98 % der CFD-Genauigkeit bei 1000x weniger Rechenzeit — aber mit klaren Grenzen.**

## Vergleichsreferenzen — kommerzielle CFD-Tools für PEM

| Tool | Hersteller | Lizenz/Jahr | Stärken im PEM-Kontext |
|---|---|---|---|
| **ANSYS Fluent** | Ansys | €30–60k | Marktführer, Fuel-Cell-Addon, breite Usergroup |
| **COMSOL Multiphysics** | COMSOL AB | €15–40k | Dediziertes Electrochemistry-Modul, academic-friendly |
| **Siemens STAR-CCM+** | Siemens | €40–70k | Multi-physics Kopplung, Automotive-verbreitet |
| **AVL Fire M** | AVL | €20–50k | Automotive/Brennstoffzellen-spezialisiert |
| **Convergent Science Converge** | CSI | €30–60k | Auto-meshing, transient starke Domäne |
| **Altair AcuSolve** | Altair | €20–40k | GPU-Beschleunigung |
| **OpenFOAM** | OpenFOAM Foundation | 0 € | Open Source, anpassbar, keine GUI |

**Gemeinsamkeit:** Alle lösen 3D-Strömung + Species-Transport + Electrochemistry + Energie mit FVM/FEM auf feinem Mesh. Wir wollen **nicht mit denen konkurrieren**, sondern sie für Early-Stage-Design ersetzen.

## Was ANSYS Fluent / COMSOL / STAR-CCM+ / AVL Fire M machen

Industrielle CFD-Tools lösen:

1. **3D Navier-Stokes** (Strömung in Flow-Fields)
2. **Species-Transport** (O₂, H₂, H₂O — Diffusion + Konvektion)
3. **Butler-Volmer gekoppelt an lokalen Gas-Partialdruck**
4. **Energiegleichung** (Wärmeleitung, Joule-Heating, Reaktionsenthalpie)
5. **Two-Phase-Flow** (flüssig/dampfförmiges H₂O im GDL)
6. **Ionomer-Transport** (Wasser durch die Membran, Electro-osmosis, Back-Diffusion)

**Rechenzeit:** 1–7 Tage pro Operating Point auf HPC (64+ Cores).
**Lizenzkosten:** €15.000–50.000 / Jahr.
**Setup-Zeit:** 2–6 Monate für neues Mesh/Modell.

## Was ein Hybrid-Ansatz leisten kann

### Tier 1 — Macht gute Polarisationskurven (1D-Modell)

| Methode | Genauigkeit vs. CFD | Rechenzeit | Tool |
|---|---|---|---|
| 0D lumped | ±5–10 % bei U(j) | < 1 ms | **dieses Projekt v0.1** |
| 1D through-MEA | ±2–5 % | < 100 ms | Python + Numba (geplant v1.0) |
| Pseudo-2D (along-channel + through-MEA) | ±3–7 % | < 1 s | Python + FiPy/FEniCS |

**Referenzen für 1D-Modelle:**
- Marangio et al. (2009), Int. J. Hydrogen Energy 34(3) — Steady-State 1D PEM-EC
- García-Valverde et al. (2012), Int. J. Hydrogen Energy 37(2) — Simple PEM-Electrolyser Model
- Abdin et al. (2015), Energy 91 — Modelling of a PEM Electrolyser Cell

### Tier 2 — Surrogate-Modelle aus CFD-Daten

**Prinzip:** CFD einmalig laufen lassen (oder aus Paper nehmen), dann ML-Modell trainieren, das in Millisekunden dasselbe Ergebnis liefert.

| Ansatz | Genauigkeit vs. Training-CFD | Aufwand |
|---|---|---|
| Polynomial Response Surface | ±5–15 % | niedrig |
| Gaussian Process Regression | ±2–5 % | mittel |
| Neural Network Surrogate | ±1–3 % | mittel-hoch |
| **PINN** (Physics-Informed Neural Network) | ±0.5–2 % | hoch |
| **POD-ROM** (Reduced-Order Model) | ±1–3 % | hoch |

**Referenzen:**
- Wang et al. (2020), Appl. Energy 275 — Deep Learning Surrogate for PEMFC
- Raissi et al. (2019), J. Comput. Phys. 378 — Physics-Informed Neural Networks
- Wilberforce et al. (2023), Energy AI 11 — ML für Elektrolyseur-Design

### Tier 3 — Hybrid: Physik-Kern + Empirische Korrekturen

**Der realistisch beste Ansatz für unser Projekt.**

```
U_cell(j, T, p, Material, Geometrie) =
    U_physik(j, T, p)                                ← dieses Projekt, 0D/1D
  + Δ_membrane(Material, λ_H2O)                       ← Springer-Modell 1D
  + Δ_transport(j, Geometrie, flow_rate)              ← empirisch aus Literatur
  + Δ_temperature_distribution(j, cooling)            ← 0D-Thermal-Bilanz
  + η_CFD_correction(j, Geometrie) [optional]         ← ML-Surrogate aus CFD-Paper
```

**Genauigkeit:** 90–95 % der CFD-Genauigkeit bei 10⁴–10⁶x Speedup.

## Was der Hybrid-Ansatz **nicht** kann

**Ehrliche Grenzen:**

| Was | Hybrid liefert das? |
|---|---|
| Polarisationskurve U(j) | JA, ±3 % |
| Wirkungsgrad η(j, T) | JA, ±5 % |
| H₂-Produktionsrate | JA, ±2 % |
| Operating-Point-Optimierung | JA |
| Stack-Performance | JA, mit Thermal-Kopplung |
| **Lokale Stromdichte-Verteilung j(x,y)** | NEIN (ohne 2D) |
| **Hotspots / Temperaturverteilung** | NEIN (nur 0D ΔT) |
| **Flow-Field-Optimierung** (Kanal-Design) | NEIN |
| **Flooding / Austrocknung lokalisiert** | NEIN |
| **Transient-Verhalten (Start/Stop)** | NEIN (nur stationär) |
| **Multi-phase Flow** | NEIN |
| **Akkurate Degradations-Vorhersage** | NEIN |

## Roadmap für Hybrid-Implementierung in diesem Projekt

### Phase 1 — v0.2 (jetzt nächste): 0D komplett
- Stack-Skalierung (N Zellen)
- 0D-Thermal-Bilanz
- Material-Presets

### Phase 2 — v0.5: Erweiterte 0D + Validierung
- Validierung gegen 3 Paper-Experimente
- Empirische Korrekturen aus Literatur integriert
- Kosten-Schätzer
- Material-DB

### Phase 3 — v1.0: 1D-Modelle
- Springer-Membran (1D Wasser-Transport)
- 1D Along-Channel (Gas-Partialdruck + Wasser-Balance)
- Numba/Cython für Performance
- Gültigkeitsbereich: 1D erreicht ~95 % der CFD-Genauigkeit für Cell-Performance

### Phase 4 — v2.0 (optional): Surrogate-Layer
- Training-Data aus publizierten CFD-Ergebnissen (Literature Digitization)
- Gaussian-Process-Regression oder PINN
- Optional: Kopplung an einen externen OpenFOAM-Runner (Hybrid mit echtem CFD-Kern)

## Technische Entscheidungen

### Ja zu:
- **Python** (Hauptsprache) + **NumPy/SciPy** + **FiPy/FEniCS** (1D/2D-PDE)
- **Numba/Cython** für Performance-kritische Schleifen
- **Scikit-learn / PyTorch** für Surrogate-Modelle
- **OpenFOAM** als externer CFD-Kern (wenn v2.0 kommt) — Open Source, kein Lizenzproblem

### Nein zu:
- **AVL Fire M nachbauen** — unrealistisch, 50+ Personenjahre
- **ANSYS Fluent nachbauen** — siehe oben
- **Eigenes 3D CFD in Python** — falsche Sprache für diese Aufgabe

## Empfehlung

**Zielmarke: 90–95 % der CFD-Genauigkeit für Cell-/Stack-Performance bei 10.000x weniger Kosten und 100.000x mehr Speed.**

Das ist realistisch, hat Präzedenzfälle in der Literatur (Marangio, García-Valverde, Abdin), und ist die richtige Positionierung für ein Open-Source-Tool, das **kommerzielle CFD (Fluent, COMSOL, STAR-CCM+, AVL Fire M) ergänzt** für Early-Stage-Design — nicht ersetzt für Detailed Design oder Zertifizierung.

**Gegen CFD antreten wollen wir nicht — CFD für schnelles Screening ersetzen schon.**

## Trigger für Re-Evaluation

- Wenn User lokal aufgelöste Ergebnisse braucht → 2D FEM via FEniCS einbauen
- Wenn kommerzielle Nutzer auftauchen, die CFD-Vergleich fordern → Surrogate-Layer (Phase 4)
- Wenn PhD/Research-Path genommen wird → das hier zu einem wissenschaftlichen Tool entwickeln
