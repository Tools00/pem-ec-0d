# ADR 004 — Arrhenius-Korrektur für Austauschstromdichte j₀(T)

**Status:** Accepted — implementiert in v0.3
**Date:** 2026-04-20
**Context:** Die Material-Presets liefern einen festen `j0_a_m2`-Wert,
gemessen oder extrapoliert auf 80 °C (353.15 K). Die Stromdichte-Formel
(Tafel/Butler-Volmer) nahm diesen Wert unverändert, unabhängig von der
Betriebstemperatur. Das verletzt Arrhenius: bei 30 °C ist OER auf IrO₂
ca. 20-fach langsamer, bei 100 °C ca. 3-fach schneller als bei 80 °C.
Ein Temperatur-Sweep im UI zeigte bei 80 °C den korrekten η_act, bei 30 °C
aber viel zu kleinen Überpotential (weil j₀ bei Raumtemperatur zu hoch war).

## Entscheidung

Wir korrigieren j₀ dynamisch über eine Arrhenius-Beziehung:

```
j0(T) = j0_ref · exp( −E_a / R · (1/T − 1/T_ref) )
```

- **j0_ref** = Preset-Wert in `CatalystSpec.j0_a_m2` (bei T_ref = 353.15 K)
- **E_a**   = scheinbare Aktivierungsenergie, neu eingeführt als
  `CatalystSpec.activation_energy_j_mol`
- **T**     = Betriebstemperatur aus UI-Slider [K]
- **T_ref** = 353.15 K (80 °C, Konvention des Preset-Tabellenwerts)

Die Funktion liegt in `src/electrochemistry.py` als
`arrhenius_exchange_current_density()`, die UI berechnet `j0_anode(T)` und
`j0_cathode(T)` direkt vor dem `Electrochemistry.from_engineering(...)`-Aufruf.

## Zugewiesene E_a-Werte

| Katalysator | E_a [kJ/mol] | Quelle |
|---|---|---|
| IrO₂ (commercial) | 52 | Suermann et al. (2017), J. Power Sources 365 |
| IrRuOx | 48 | Ir-Ru Mischoxid-Konsens, leicht reduziert wegen Ru-Stabilisierung |
| IrO₂-TiO₂ (low-loading) | 56 | TiO₂-Support erhöht Aktivierungsbarriere |
| Pt/C (commercial) | 25 | Durst et al. (2014), EES 7 |
| Pt black | 20 | Unsupported Pt HER — literaturbasiert |
| Pt-alloy (PtCo/C) | 22 | Pt-Legierung senkt E_a leicht |

## Warum Arrhenius und nicht komplexer

- **Standard in der PEM-EC-Literatur.** Carmo et al. (2013) Eq. (9),
  alle Reviews verwenden dieselbe Form.
- **Ein neuer Parameter pro Katalysator** — kein Overkill.
- **Gültigkeitsbereich deckt MVP-Szenarien ab** (30–90 °C, |T−T_ref| < 80 K).
- **Kompatibel mit dem späteren Full-Butler-Volmer** — dort wird j₀(T)
  genauso eingesetzt, nur mit zusätzlichem Rückreaktions-Term.

## Alternativen verworfen

| Alternative | Warum nicht |
|---|---|
| **Statisch lassen (kein Update)** | wissenschaftlich falsch: 20× Fehler bei 30 °C für OER |
| **Eyring-Gleichung (TST)** | genauer, aber braucht ΔS‡ und ΔH‡ separat — nicht in Datenblättern |
| **Butler-Volmer mit asymmetrischer α(T)** | α-Temperaturabhängigkeit ist zweiter-Ordnung-Effekt; wird in v0.5 evaluiert |
| **Tabellierte j₀(T)-Punkte** | Interpolation instabil, keine gute Literaturbasis für alle 6 Presets |

## Konsequenzen

### Positiv
- **Temperatur-Sweep physikalisch korrekt.** η_act(30 °C) steigt realistisch,
  η_act(90 °C) sinkt realistisch — Polarisationskurven stimmen qualitativ mit
  Carmo et al. (2013) Fig. 6 überein.
- **Material-Vergleiche auf gleichem Temperaturlevel.** Ein User kann zwei
  Katalysatoren bei beliebigem T vergleichen, ohne manuell umrechnen zu müssen.
- **MODEL_CARD-Gültigkeitsbereich erweitert** von „nur 80 °C" auf 30–90 °C.
- **Breaking change im Daten-Schema** ist klein — nur ein neues Pflichtfeld
  in `CatalystSpec`, rückwärtskompatibel via Default wäre möglich, wurde aber
  bewusst ohne Default eingeführt, damit keine Spec ohne E_a gebaut werden kann.

### Negativ
- **Nicht-Ir-Anoden oder Nicht-Pt-Kathoden** (nicht im Preset) müssen E_a
  selbst mitbringen — es gibt keinen neutralen Default.
- **E_a aus Literatur hat Streuung ±15 %** — für |T−T_ref| > 30 K wird das
  sichtbar (z.B. ±5 % in j₀ bei T = 25 °C).
- **Gültigkeit bricht außerhalb [293, 373] K** — kalte Elektrolyseur-Starts
  (< 20 °C) sind unrealistisch, aber wir blocken nicht explizit (der 273–423-K-
  Guard in der Funktion greift).

## Tests

Acht neue Unit-Tests in `tests/test_electrochemistry.py`:
1. Identität: j₀(T_ref) == j₀_ref (exakt)
2. Monotonie: j₀(T) strikt steigend in T für E_a > 0
3. IrO₂-Realismus: j₀(298)/j₀(353) ≈ 0.05 (Faktor 20 Drop)
4. HER schwächer T-abhängig als OER (vergleichender Test)
5. Negatives/null j₀_ref → ValueError
6. Negatives/null E_a → ValueError
7. T außerhalb [273, 423] K → ValueError
8. T_ref außerhalb [273, 423] K → ValueError

## Referenzen

- **Carmo, M., Fritz, D. L., Mergel, J., & Stolten, D. (2013).** A comprehensive
  review on PEM water electrolysis. *Int. J. Hydrogen Energy* 38(12), 4901–4934.
  Eq. (9); Fig. 6.
- **Suermann, M., Bensmann, B., & Hanke-Rauschenbach, R. (2017).** Kinetic
  modeling of the oxygen evolution reaction on IrO₂ in PEM water electrolysis.
  *J. Power Sources* 365, 47–55.
- **Durst, J., Siebel, A., Simon, C., et al. (2014).** New insights into the
  electrochemical hydrogen oxidation and evolution reaction mechanism.
  *Energy Environ. Sci.* 7, 2255–2260.

## Re-Evaluation

Austausch / Erweiterung empfohlen wenn:
- v1.0 Full-Butler-Volmer einführt → die α(T)-Kopplung wird relevant
- Nicht-Edelmetall-Anoden (Ni-Fe-Oxide) ins Preset aufgenommen werden →
  eigene Korrelation nötig, Arrhenius mit konstantem E_a reicht dort nicht
- Validierung gegen Experiment zeigt > 20 % Abweichung bei T < 40 °C →
  zweite Term (z.B. ΔS‡-abhängig) ergänzen
