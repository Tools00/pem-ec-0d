# Known Issues & Limitations

**Stand:** 2026-04-19, v0.1.0

Ehrliche Auflistung aller bekannten Schwächen und bewussten Vereinfachungen.

---

## Physikalische Vereinfachungen (bewusst, im MVP-Scope)

| # | Vereinfachung | Warum OK für MVP | Wann problematisch |
|---|---|---|---|
| 1 | 0D stationär — keine räumliche Auflösung | Performance-Kurven (U-j) sind gut approximiert | Lokale Strom-/Temperaturverteilung gebraucht |
| 2 | Einheitlicher Druck Anode = Kathode | Typisch für symmetrische Betriebsbedingungen | Differential-Druck-Betrieb (H2 unter Druck) |
| 3 | Tafel-Approximation statt voller Butler-Volmer | j >> j0 für PEM-EC (j > 1000 A/m²) | Sehr niedrige Stromdichten (j < 100 A/m²) |
| 4 | Membran-Leitfähigkeit als Konstante | Vereinfachung bei konstanter Hydratation | Betrieb bei variabler Feuchte, Trocknung |
| 5 | Keine Anisotropie der Membran | Nafion ist isotrop genug für 0D | Composite-Membranen, reinforced membranes |
| 6 | Flüssiges Wasser als Aktivität = 1 | Gültig bei Überschuss-Wasser (typisch) | Unterversorgung, dry-out |
| 7 | Konstante Faraday-Effizienz (98 %) | Literatur-Wert für kommerziell | Bei hoher Temperatur und Gas-Crossover |
| 8 | Konzentrations-Überspannung mit fixem j_limit | Einfaches Butler-Volmer-Konzentrations-Modell | Bei starker Überflutung/Austrocknung |

## Implementierungs-Lücken (noch nicht implementiert, geplant)

| # | Was fehlt | Geplant für | Impact auf aktuelle Ergebnisse |
|---|---|---|---|
| 1 | Stack-Skalierung (N Zellen in Serie) | v0.2 | Keiner — U_stack ist lineare Multiplikation |
| 2 | Thermal-Bilanz | v0.5 | Keine, solange T als Input fix ist |
| 3 | Wasser-Transport durch Membran (Springer) | v1.0 | Annahme: Membran voll hydratisiert |
| 4 | Multi-phase Flow im GDL | niemals (PEMFC-v2) | Annahme: kein flooding |
| 5 | Dynamik/Transient-Verhalten | niemals (nur stationär) | Nur Steady-State-Betrieb abbildbar |
| 6 | Degradation | v1.0 | Zelle wird als "neu" modelliert |
| 7 | EIS / Impedanzspektroskopie | niemals | Out of scope |

## Software-Schulden

| # | Was | Priorität | Geplant für |
|---|---|---|---|
| 1 | Kein Git-Repo bei Projekt-Start | BEHOBEN 2026-04-19 | — |
| 2 | `requirements.txt` statt `pyproject.toml` | MITTEL | v0.5 |
| 3 | Keine CI/CD (GitHub Actions) | HOCH | v0.5 |
| 4 | Keine Type-Check mit `mypy` | MITTEL | v0.5 |
| 5 | Kein Linter (`ruff`/`pre-commit`) | MITTEL | v0.5 |
| 6 | Streamlit-App ohne State-Caching | NIEDRIG | v0.5 |
| 7 | Polarisationskurve als Python-Loop (nicht vektorisiert) | NIEDRIG | v1.0 (wenn langsam) |
| 8 | Keine Logging-Infrastruktur | MITTEL | v0.5 |

## Validierungs-Gaps

| # | Was | Status | Blocker für |
|---|---|---|---|
| 1 | Tafel-Slope gegen analytische Formel | GRÜN (< 0.5 % Abweichung) | — |
| 2 | Polarisationskurve gegen Paper-Experiment | FEHLT | v0.5 |
| 3 | Temperatur-Sweep gegen Messdaten | FEHLT | v0.5 |
| 4 | Druck-Abhängigkeit vs. Experiment | FEHLT | v1.0 |
| 5 | Wirkungsgrad-Karte vs. kommerzielle Anlagen | FEHLT | v1.0 |

## UX/UI-Schwächen

| # | Was | Priorität |
|---|---|---|
| 1 | Tafel-Plot (semi-log) nicht sichtbar in der UI | MITTEL |
| 2 | Keine Material-Presets (Nafion 212 / 115 / 117) | HOCH |
| 3 | Kein Vergleichs-Modus (2 Zellen nebeneinander) | MITTEL |
| 4 | Kein DE/EN-Sprachswitch | NIEDRIG |
| 5 | Keine Screenshots/GIFs im README für Portfolio | HOCH |

---

## Wie mit diesem Dokument umgehen

- **User meldet Bug?** → Prüfen ob in "Physikalische Vereinfachungen" gelistet. Wenn ja: dokumentiertes Verhalten, kein Bug.
- **Feature-Request?** → In CHANGELOG.md unter "Planned" einordnen, nicht in v0.1 reinziehen (Scope-Creep vermeiden).
- **Neuer Contributor?** → Diese Datei zuerst lesen, dann `CLAUDE.md`.
