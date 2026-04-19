# ADR 003 — Springer-Modell für Membran-Leitfähigkeit σ(λ, T)

**Status:** Accepted — implementiert in v0.3
**Date:** 2026-04-19
**Context:** Bisher war `membrane_conductivity` ein statischer Preset-Wert pro Membran
(z.B. 10 S/m für Nafion 212). Das ist physikalisch inkorrekt: σ hängt stark von der
Membrantemperatur T und vom Wassergehalt λ ab.

## Entscheidung

Wir ersetzen den statischen Preset durch die Springer-Korrelation (1991):

```
σ [S/cm] = (0.005139 · λ − 0.00326) · exp( 1268 · (1/303 − 1/T) )
```

- **λ** = Wassergehalt (mol H₂O pro mol SO₃H-Gruppe), aus der Material-Spec (`water_uptake`),
  moduliert durch einen UI-Hydrationsfaktor ∈ [0.3, 1.0].
- **T** = Betriebstemperatur in K, aus dem UI-Slider.

Das `MembraneSpec.conductivity_sm`-Feld bleibt als Info-Feld erhalten (Preset-Wert bei
80 °C, voll hydratisiert), wird aber nicht mehr für die Berechnung verwendet.

## Warum diese Formel

- **Klassische Referenz** seit 35 Jahren; Zitat über 8000-mal.
- Gültigkeitsbereich deckt unseren MVP-Use-Case ab (298–353 K, λ > 1).
- Einfache analytische Form ohne numerisches Lösen.
- Basis für fast alle nachfolgenden Membran-Modelle (auch für nicht-Nafion-PFSA
  in guter Näherung).

## Alternativen verworfen

| Alternative | Warum nicht |
|---|---|
| **Weber-Newman-Modell (2004)** | genauer, aber braucht Porenmodell + mehr Parameter — Overkill für 0D |
| **Kusoglu-Weber-Review (2017)** | ist Zusammenfassung, gibt Springer + Korrekturen — übernehmen wir später für v1.0 |
| **Empirisches Polynom aus Datenblatt** | nicht temperaturabhängig; Herstellerangaben sind nur Punktwerte |
| **Statisch lassen (Preset-Wert)** | wissenschaftlich falsch: σ(30 °C) ≈ 11 S/m vs. σ(80 °C) ≈ 20 S/m — Faktor 1.8 |

## Konsequenzen

### Positiv
- **η_ohm automatisch T-korrekt.** Bei Temperatur-Sweep sinkt der Ohm-Anteil
  realistisch um ~45 % zwischen 30 °C und 80 °C (vorher: 0 %).
- **MODEL_CARD-Gültigkeitsbereich erweitert** von "80 °C only" zu "50–90 °C verlässlich".
- **User kann Austrocknung simulieren** über den Hydrations-Slider.

### Negativ
- **Nicht-Nafion-Membranen** (Aquivion, Fumapem) bekommen die Nafion-Korrelation
  appliziert — Näherung. Für v0.5 ggf. materialspezifische Fits ergänzen.
- **Unterhalb λ ≈ 0.63** gibt die Formel σ ≤ 0 → Guard im Code mit klarer
  Fehlermeldung; User muss Hydrationsfaktor > 0.3 halten.

## Tests

Sechs neue Unit-Tests in `tests/test_electrochemistry.py`:
1. Referenzwert bei T=303 K, λ=22 stimmt auf 9 Nachkommastellen
2. σ steigt mit T (Arrhenius-ähnlich, Faktor 1.6–2.0 zwischen 303–353 K)
3. σ steigt monoton mit λ
4. Trockene Membran (λ ≤ 0.634) wirft ValueError
5. Temperatur außerhalb [273, 423] K wirft ValueError
6. Realistischer Nafion-Wert bei 80 °C im Band 17–22 S/m

## Referenzen

- **Springer, T. E., Zawodzinski, T. A., & Gottesfeld, S. (1991).** Polymer electrolyte
  fuel cell model. *J. Electrochem. Soc.* 138(8), 2334–2342. Eq. (23).
- **Kusoglu, A., & Weber, A. Z. (2017).** New insights into perfluorinated sulfonic-acid
  ionomers. *Chem. Rev.* 117(3), 987–1104. — Review, bestätigt Springer im PEM-EC-Regime.

## Re-Evaluation

Austausch empfohlen wenn:
- Wir auf nicht-Nafion-Membranen mit anderer Chemie umsteigen (Aquivion bleibt nah genug)
- Betrieb bei λ < 5 (trockene Membran) realistisch wird → anderes Modell nötig
- v1.0 1D-Membran-Transport einführt → Springer wird dann Baustein, nicht Standalone
