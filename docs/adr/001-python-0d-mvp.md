# ADR 001 — Python + 0D-Modell für MVP

**Status:** Accepted
**Date:** 2026-04-19
**Context:** pem-ec-0d v0.1 Scope-Festlegung

## Kontext

Entscheidung über den Tech-Stack und die Modellierungs-Tiefe für das MVP (v0.1) von pem-ec-0d.

## Alternativen

| Option | Stack | Modellierung | Pros | Cons |
|---|---|---|---|---|
| A | Python + 0D | Butler-Volmer + Nernst + Ohm | Schnell, lesbar, großes Ecosystem | Keine räumliche Auflösung |
| B | Python + 1D | Springer-PDE | Wissenschaftlich ernster | 5–10x mehr Code, FEM-Dependency |
| C | C++ + Eigen + Qt | 1D/2D | Performance | Monate Aufwand, Over-Engineering |
| D | MATLAB | 1D | Etabliert in Industrie | Lizenzkosten, kein Deploy |
| E | AVL Fire M | 3D CFD | Industriestandard | €€€, kein Self-Build |

## Entscheidung

**Option A gewählt: Python + 0D.**

## Begründung

1. **Scope ist MVP (7 Werktage).** Option B/C sind Wochen/Monate.
2. **Zielgruppe** sind Ingenieure für Konzeptstudie, nicht CFD-Spezialisten.
3. **0D reicht für Polarisationskurven** mit typ. 5–10 % Abweichung zu Experiment — gut genug für Zellsizing.
4. **Python-Ecosystem** (NumPy, Streamlit, Plotly) ist State-of-the-Art für Data-Apps.
5. **Deploy** auf Streamlit Cloud ist 1-Click. C++/Qt bräuchte Docker+Server.
6. **Keine Vendor-Lock-in** — alles Open Source.

## Konsequenzen

### Positiv
- MVP in 7 Tagen machbar
- Niedriger Einstiegsaufwand für Contributor
- Einfach zu validieren (analytische Tafel-Slope)
- Portfolio-tauglich als Web-Demo

### Negativ
- Keine räumlichen Verteilungen (j(x), T(x), λ(x))
- Performance-Wall bei großen Parameter-Sweeps (Grid-Search > 10⁴ Punkte wird langsam)
- Kein direkter Vergleich zu CFD-Ergebnissen wie Stromdichte-Heatmap
- Bei späteren 1D/2D-Erweiterungen: Python evtl. zu langsam → Numba/Cython nötig

## Trigger für Re-Evaluation

Dieses ADR sollte überdacht werden, wenn:
- Parameter-Sweeps > 30 s pro Punkt dauern
- User räumlich aufgelöste Ergebnisse fordern
- CFD-Vergleiche quantitativ gebraucht werden

Siehe auch: `docs/adr/002-hybrid-cfd-surrogate.md` (geplant für v0.5)
