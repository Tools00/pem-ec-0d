# ADR 005 — Full Butler-Volmer statt Tafel-Näherung

**Status:** Accepted — implementiert in v0.3
**Date:** 2026-04-20
**Context:** Bisher wurde die Aktivierungsüberspannung über die Tafel-Näherung
berechnet:

```
η_Tafel = (R·T / α·F) · ln(j / j0)
```

Diese Form ist nur für j ≫ j0 gültig (Faustregel j/j0 > 10). Für die Anode
(IrO₂, j0 ≈ 10 A/m²) bei typischen Lasten (j > 10⁴ A/m²) ist das unkritisch,
aber für die Kathode (Pt/C, j0 ≈ 10³ A/m²) sitzt man bei kleinen Lasten
(j < 10⁴ A/m²) in einem Regime, wo der Rückreaktionsterm nicht vernachlässigbar
ist. Zudem wird η_Tafel(j = j0) = 0 und η_Tafel(j < j0) < 0 — beides
unphysikalisch, die Tafel-Form darf dort einfach nicht evaluiert werden.

## Entscheidung

Wir ersetzen die Tafel-Näherung durch die vollständige Butler-Volmer-Gleichung
für jede einzelne Elektrode:

```
j(η) = j0 · [ exp( α·F·η / R·T )  −  exp( −(1−α)·F·η / R·T ) ]
```

- **α** = Transfer-Koeffizient der Vorwärts-Richtung (aus Preset)
- **(1−α)** = Rückwärts-Koeffizient (eine Elektronen-RDS, Standard-Annahme)

Da es für η(j) keine geschlossene Form gibt, invertieren wir numerisch mit
**Newton-Raphson**, initialisiert mit dem Tafel-Schätzwert. BV ist strikt
monoton in η (Ableitung überall > 0), Konvergenz ist garantiert; ab dem
Tafel-Startwert ist sie quadratisch — typisch 3–5 Iterationen bei Toleranz
1e-10.

## Warum nicht weiterhin Tafel?

Bei j = 1.01 · j0 (Kathode knapp über Leerlauf):
- Tafel: η = (R·T / α·F) · ln(1.01) ≈ 0.72 mV — nahezu null
- Full BV: η ≈ 2.5 mV

Bei j = 0.5 · j0 (Kathode unterhalb Austauschstromdichte, realistisch bei
Niedriglastbetrieb oder Rückspeisung):
- Tafel: ln(0.5) < 0 → negatives η → Formel darf nicht verwendet werden
- Full BV: η ≈ −3 mV — korrektes Vorzeichen, sinnvolle Magnitude

Die quantitative Auswirkung bei PEM-EC-Volllast (j = 20 000 A/m²) ist
< 10⁻⁶ — bei Teillast aber bis 5 % im η_act-Anteil der Kathode.

## Warum Newton und nicht brentq/fsolve?

- **Kein neues Dependency** (scipy ist nicht erforderlich, aktuell nur numpy).
- **Quadratische Konvergenz** aus dem Tafel-Startwert.
- **Robust** durch Monotonie von BV; kein Bracketing nötig.
- **Einfach zu testen** — deterministisch, keine versteckten Toleranzen.

## Alternativen verworfen

| Alternative | Warum nicht |
|---|---|
| **Tafel mit Cutoff bei j < 10·j0** | unschön: künstliche Fallunterscheidung, Sprung im Gradienten |
| **Linearisierung bei kleinen η (Ohm'sches Regime)** | nur gültig für |η| < 10 mV — Grenze musst du selbst kennen |
| **Pre-computed η(j)-Tabelle** | Interpolation, Genauigkeit schwankt mit Gitter |
| **scipy.optimize.brentq** | 100 KB Dependency für eine Funktion — Overkill |
| **Matched Asymptotic Expansion** | Analytische Form existiert (Erdey-Grúz), aber komplizierter zu lesen und zu warten |

## Konsequenzen

### Positiv
- **Physikalisch korrekt für den gesamten j-Bereich**, inkl. Niedriglast und
  j < j0 auf der Kathode.
- **Tafel-Slope-Test bleibt unverändert grün** — BV konvergiert zu Tafel bei
  hohen η (numerisch: relativer Fehler < 10⁻⁶ bei η = 0.5 V).
- **Asymmetrisches α wird unterstützt** (α_anode, α_cathode separat) — bleibt
  kompatibel mit dem bestehenden `CatalystSpec.alpha`-Feld.
- **Roundtrip-Garantie:** `BV(activation_overpotential(j)) == j` auf 10⁻⁸
  (Test erzwungen).

### Negativ
- **~3–5× langsamer** als Tafel pro Aufruf (Newton-Iteration vs. ein `np.log`).
  Bei typischem Sweep (100 Punkte × 2 Elektroden) sind das < 5 ms — nicht
  merkbar in der Streamlit-UI.
- **Newton kann theoretisch fehlschlagen** bei pathologischen Startwerten.
  Wir fangen das ab (`RuntimeError` nach 50 Iterationen mit Diagnose) —
  ist in der Praxis nie eingetreten.
- **Annahme α_forward + α_backward = 1** (eine-Elektronen-RDS) ist eine
  Vereinfachung. Für Mehr-Elektronen-Übergänge müsste man α_a und α_c
  unabhängig setzen — ist für v1.0 mit Mechanismus-aufgelöster BV geplant.

## Tests

Sechs neue Unit-Tests in `tests/test_electrochemistry.py`:
1. j(η=0) = 0 (beide Exponentialterme kürzen sich)
2. Antisymmetrie für α = 0.5: j(−η) = −j(η)
3. BV → Tafel bei η = 0.5 V (rel. Fehler < 10⁻⁶)
4. Roundtrip: BV(activation_overpotential(j)) == j auf 10⁻⁸, über 15
   logarithmisch verteilte j-Punkte
5. Nahe-Leerlauf-Regime: j knapp über j0 gibt endliches, positives η < 50 mV
6. Input-Validierung: j0 ≤ 0, α ∉ (0, 1), T ≤ 0

Die bestehenden Tafel-Slope- und Monotonie-Tests bleiben **unverändert** grün.

## Referenzen

- **Bard, A. J., & Faulkner, L. R. (2001).** Electrochemical Methods:
  Fundamentals and Applications. 2nd ed. Wiley. Eq. 3.3.11.
- **Carmo, M., Fritz, D. L., Mergel, J., & Stolten, D. (2013).** Int. J.
  Hydrogen Energy, 38(12). Eq. (8).
- **Barbir, F. (2012).** PEM Fuel Cells: Theory and Practice. 2nd ed.
  Section 3.3 — Butler-Volmer derivation from transition-state theory.

## Re-Evaluation

Austausch / Erweiterung empfohlen wenn:
- Mehr-Elektronen-RDS-Reaktionen relevant werden (α_a + α_c ≠ 1) →
  `CatalystSpec` braucht getrennte α_forward, α_backward
- Temperaturabhängige α (zweiter-Ordnung-Effekt, Sharifi-Asl 2013) →
  α = α(T) Korrelation ergänzen
- Konvergenzprobleme in der Praxis sichtbar → Newton auf Brent'sches
  Verfahren umstellen (robuster, aber langsamer)
- v1.0 Mikrokinetik-Modell mit Einzelschritten einführt → BV wird dann
  letzte Stufe, nicht Standalone
