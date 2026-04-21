# Lessons Learned — pem-ec-designer

**Projekt:** pem-ec-designer (PEM Electrolysis Cell & Stack Designer)
**Zeitraum:** April 2026
**Versionen:** v0.1 → v0.6
**Zweck dieses Dokuments:** Ehrliche Aufarbeitung aller Entscheidungen,
Fehler und Strukturprobleme. Kein Marketing. Basis für das allgemeine
Simulations-Projekt-Framework in `simulation-project-framework.md`.

---

## 1. Was gut gelaufen ist

### Physik-Layer (von Tag 1 richtig)
- CODATA-2018-Konstanten aus einer Quelle (`constants.py`), nie
  hardcoded. Hat nullmal zu Konstanten-Inkonsistenz geführt.
- SI-only intern, Engineering-Units nur in der UI-Schicht (`units.py`).
  Hat mehrfach Bugs verhindert (kein "A/cm² vs A/m²"-Schlupf in Formeln).
- Jede Gleichung mit `@ref:` im Docstring. Bei Code-Review war immer
  nachvollziehbar, wo die Formel herkommt.
- Arrhenius-Temperaturkorrektur, Springer-Membranmodell, Full-Butler-Volmer
  alle mit Quellenangabe und gültigem Bereich implementiert.

### Zero-Fit-Validierungsstrategie (gut ab Phase 3)
- Strict-xfail für Kalibrierungs-Targets: dokumentiert, warum der Test
  nicht grün ist, ohne die Test-Suite kaputt zu machen.
- Zwei-Paper-Ansatz (Bernt 2020 + Zimmer 2026) liefert sowohl
  mechanistische Diagnose als auch statistische Einordnung.
- Envelope-Test (Zimmer) vs RMSE-Target (Bernt): sauber getrennte
  Aussagen, keine Vermischung von "physikalisch konsistent" und
  "perfekt kalibriert".

### ADR-Disziplin
- ADR-001 bis 007 dokumentieren alle nicht-trivialen Entscheidungen mit
  Alternativen und Begründung.
- Gegenlesen eines ADR nach 2 Monaten ergibt sofort: "Aha, deswegen."

### Test-Struktur
- Unitkonversions-Roundtrips in `test_units.py` — haben mehrfach
  früh Tippfehler gefangen.
- Tafel-Slope-Analytik-Vergleich als erster mechanistischer Test.
- Monotonie und Sanity-Ranges als Regressionsschutz.

---

## 2. Strukturelle Fehler (mit Ursache und Behebungspfad)

### Fehler 1: Framework-Wahl ohne Trade-off-Analyse

**Was passiert ist:**
`CLAUDE.md` v0.1 hatte `streamlit run src/streamlit_app.py` als
Ziel-Command — kein Framework-Vergleich, kein ADR für diese
Entscheidung, keine Frage an den User.

**Symptome:**
- v0.6 Wunsch nach "visueller Konstruktion mit Elementen als 2D/3D" →
  sofortiger Widerspruch mit Streamlit-Grenzen (pyvista instabil auf
  Streamlit-Cloud, kein CAD-Interaktionsmodell).
- Exploded-View v0.6a als workaround statt echter Lösung.
- User musste nach mehreren Monaten erst fragen, um die Trade-offs
  zu erfahren.

**Ursache:**
Portfolio-Kontext ("schnell ein Link") wurde als implizites Primärziel
gesetzt. Technische Langzeit-Ziele ("3D-Konstruktion") standen im
gleichen Backlog, aber ohne Framework-Konsequenz-Check.

**Richtig wäre gewesen:**
ADR-001 nicht "Python + 0D-Modell für MVP" sondern
"UI-Framework-Entscheidung" mit explizitem Abgleich:
- Was soll das Tool in 6 Monaten können?
- Was davon ist Streamlit-inkompatibel?
- Dann: Streamlit OK für jetzt? Migrationskosten in v1.0 akzeptiert?

**Behebung für Nachfolgeprojekt:**
Vor dem ersten `requirements.txt`-Eintrag: Framework-ADR als
Pre-Condition. Siehe `simulation-project-framework.md`, Abschnitt 3.

---

### Fehler 2: Validierung als Scope-Item behandelt statt als Gate

**Was passiert ist:**
In CLAUDE.md v0.1 stand unter "Draußen bis v0.5":
> "2. Validation gegen Experiment"

Validation war ein Feature-Backlog-Item, kein Delivery-Gate.
Das Modell lief monatelang ohne Überprüfung, ob die Physik-Defaults
überhaupt in der richtigen Größenordnung liegen.

**Symptome:**
- v0.5 Phase 3 enthüllt 510 mV RMSE gegen Bernt 2020 — eine Abweichung,
  die mit einer 20-Minuten-Back-of-the-envelope-Rechnung früher hätte
  auffallen können (R_total 0.131 vs. ~0.05 Ω·cm²).
- Erster Lit-Vergleich ergab keinen plötzlichen "alles grün", sondern
  eine dokumentierte Kalibrierungslücke — die jetzt als v0.6-Scope
  weiterlebt.
- Die xfail-Strategie ist die elegante Lösung — aber sie sollte Teil
  von v0.2 gewesen sein, nicht v0.5.

**Ursache:**
"Validation" wurde mit "aufwendige Experiment-Datenauswertung"
gleichgesetzt. Tatsächlich reicht für eine erste Validation:
1. Ein Paper mit OC-Voltage, Tafel-Slope, und Hochstrom-Verhalten
2. Plotten von Vorhersage vs. Experiment
3. Residual-Analyse
→ 2-3 Stunden Arbeit ab v0.2.

**Behebung für Nachfolgeprojekt:**
Validation-Baseline in v0.1/v0.2. Nicht als Feature, sondern als
Akzeptanzkriterium: "Das Modell darf erst in eine neue Phase, wenn
es gegen mindestens eine Literaturkurve visuell plausibel ist."

---

### Fehler 3: Visualisierungs-Architektur ohne Ziel-State definiert

**Was passiert ist:**
`draw_layer_cross_section` + `draw_bpp_top_view` wurden in v0.4
als "gut genug für jetzt" implementiert. Kein expliziter Ziel-State
("was soll die Visualisierung in v1.0 können?").

**Symptome:**
- v0.5: Exploded-View als Patch auf bestehende Funktion.
- v0.6-Frage nach 3D/STL → struktureller Widerspruch mit Streamlit.
- Jede neue visuelle Anforderung führt zu "Patch auf Patch".

**Ursache:**
ADR-006 definiert gut, warum der Visual Stack Designer existiert,
aber nicht, wo er hingehen soll. "Hooks für v0.5+" ohne konkrete
Ziel-Architektur.

**Behebung:**
Visualisierungs-ADR immer mit drei Fragen:
1. Was zeigen wir heute?
2. Was soll in 6 Monaten gezeigt werden?
3. Welche Architektur trägt beides — oder welcher Bruch ist geplant?

---

### Fehler 4: Scope-Creep bei Defaults vs. Setup-spezifische Parameter

**Was passiert ist:**
`Electrochemistry.from_engineering()` hat generische Carmo-2013-Defaults.
Das ist korrekt für ein Zero-Fit-Modell. Aber der Weg von "generisch"
zu "Bernt-spezifisch" (IrO₂/TiO₂-Catalyst, Research-Grade-Kontakt)
wurde als v0.6-Scope in ADR-007 verschoben — obwohl er logisch zu
Phase 3 (Validation) gehört.

**Symptome:**
- Zwei strict-xfail-Tests als permanent sichtbare "Schulden" in der
  Suite. Kein v0.6 ohne ADR-Architekturentscheidung für das
  Preset-System.
- 510 mV RMSE Bernt ist nicht dramatisch (Zimmer belegt 500 mV σ in
  Literatur), aber es hinterlässt einen unvollständigen Eindruck im
  Portfolio.

**Ursache:**
Das Preset-System braucht unabhängig extrahierte kinetische Parameter
(nicht aus dem Fig.-1-Fit). Das erfordert Literaturarbeit, nicht nur
Code. Deswegen Scope-Verschiebung. Korrekte Entscheidung — nur sollte
sie früher explizit gemacht worden sein.

**Behebung:**
Schon in v0.3 entscheiden: "Wir brauchen ein Preset-System für
Catalyst + Kontakt-Resistenz. Wann? v0.4 oder v0.5?" Dann nicht
überrascht sein, wenn die Validation-Phase das sichtbar macht.

---

### Fehler 5: Keine explizite "Ziel-Nutzer"-Definition

**Was passiert ist:**
Das Tool wurde gleichzeitig als Fiverr-Demo, Portfolio-Evidence und
Engineering-Tool positioniert. Das sind drei verschiedene User-Typen
mit unterschiedlichen Anforderungen.

**Symptome:**
- "Fiverr-Demo" → Streamlit Cloud, schneller Link.
  "Engineering-Tool" → 3D-CAD, pyvista, echte Interaktion.
  Beide passen nicht ins gleiche Framework.
- "Portfolio" → maximale Tiefe (Validation, ADRs).
  "Demo" → maximale Geschwindigkeit (wenig Doku).
  Beide passen nicht in denselben Entwicklungsstil.

**Ursache:**
Keine explizite User-Story am Anfang.

**Behebung:**
Vor v0.1: "Wer benutzt das und für was?" Als einzelner Satz, nicht als
Liste. Dann Framework + Scope-Grenzen daraus ableiten.

---

## 3. Was bewusst gut entschieden wurde (aber hätte schiefgehen können)

### Strict-xfail statt Skip
Hätten wir "skip" oder "xfail(strict=False)" genommen, wären die
Kalibrierungslücken im Portfolio unsichtbar. Strict-xfail erzwingt
explizites Re-Baselining wenn v0.6 kommt. Das ist ein Feature der
Ehrlichkeit, nicht ein Bug.

### Physik-Layer von UI-Layer getrennt
`src/electrochemistry.py` importiert kein Streamlit. Das macht
den Physik-Layer testbar ohne UI, portierbar in Jupyter, reusable
im Nachfolgeprojekt. Wäre das nicht von Anfang an getrennt gewesen,
hätte jeder Framework-Wechsel auch den Physik-Code berührt.

### "Draußen bis v1.0: CFD, 3D" in CLAUDE.md
Diese harte Grenze hat verhindert, dass pyvista in einem schwachen
Moment reingerutscht ist. Scope-Grenzen in CLAUDE.md schriftlich =
sie halten unter Druck.

---

## 4. Timeline der wichtigsten Entscheidungen

| Version | Entscheidung | Bewertung |
|---|---|---|
| v0.1 | Streamlit gewählt, kein ADR | Fehler: Framework ohne Trade-off-Analyse |
| v0.1 | SI-only intern, units.py | Richtig von Tag 1 |
| v0.1 | constants.py mit CODATA | Richtig von Tag 1 |
| v0.2 | Stack + Thermal als separate Module | Richtig |
| v0.3 | Springer-Membran + Arrhenius + Full-BV | Richtig, ADR dokumentiert |
| v0.4 | Visual Stack Designer, Plotly-SVG | Richtig für Scope; ADR-006 explizit |
| v0.4 | r_bpp in Sidebar als single source | Richtig |
| v0.5 | Fluid-Modul eigenständig (pure functions) | Richtig |
| v0.5 | aspect_ratio statt (w, h) explizit | Richtig: area-preserving, legacy-compat |
| v0.5 | Validation als xfail mit Diagnose | Richtig: ehrlicher als skip oder fit |
| v0.5 | Zimmer 2026 als statistischer Kontext | Richtig: stärker als single-paper RMSE |
| v0.6 | Exploded View statt pyvista | Richtig für dieses Projekt; pyvista im Nachfolger |
| v0.6 | Preset-System auf Nachfolgeprojekt verschoben | Vertretbar; hätte früher entschieden werden sollen |

---

## 5. Was ins Nachfolgeprojekt mitgenommen wird

**Code (direkt reusable):**
- `src/constants.py` — CODATA 2018, frameworkagnostisch
- `src/units.py` — SI ↔ Engineering, frameworkagnostisch
- `src/electrochemistry.py` — Butler-Volmer, Nernst, Ohm, Arrhenius
- `src/fluid.py` — Hagen-Poiseuille / Darcy-Weisbach
- `src/materials.py` — Membran/Catalyst/GDL-Presets
- `src/components.py` — Stack-Component-Presets
- `src/assembly.py` — StackAssembly-Dataclass (Physik-Teil)
- `tests/` — Validation-Datasets + Tests als Regressionsschutz

**Nicht reusable (Streamlit-spezifisch):**
- `src/streamlit_app.py` — neu schreiben im gewählten Framework
- `src/visualization.py` — Plotly-SVG-Shapes, neu implementieren in
  drei.js / pyvista / Panel je nach Framework-Entscheidung

**Strategie (direkt übertragen):**
- Zero-Fit-Validierung mit strict-xfail
- SI-only + units.py
- ADR von Tag 1
- Framework-ADR als Pre-Condition (nicht nachträglich)
- Validation-Baseline in v0.1/v0.2, nicht v0.5

**Vorlage für CLAUDE.md:**
Füge hinzu: "Framework-ADR muss vor erstem `requirements.txt`-Eintrag
existieren. UI-Ziel-State für 6 Monate und 18 Monate explizit formulieren."
