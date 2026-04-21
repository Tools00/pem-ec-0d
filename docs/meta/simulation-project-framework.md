# Simulations-Projekt-Framework

**Abgeleitet aus:** pem-ec-designer v0.1–v0.6
**Zweck:** Allgemeines Framework für physikalisch-basierte Simulations-Tools
in Python. Direkt anwendbar auf PEMFC-Designer, CFD-Preprocessing-Tools,
Stack-Auslegungs-Tools und ähnliche Projekte.

Dieses Dokument ist kein "nice to have" — es ist die Pre-Condition für
den Start jedes neuen Simulations-Projekts.

---

## 1. Vor dem ersten Commit: Pflichtfragen

Diese 8 Fragen müssen beantwortet sein, **bevor** eine einzige Zeile Code
geschrieben wird. Keine Ausnahmen.

### 1.1 Ziel-Nutzer (ein Satz)
> "Dieses Tool ist für [Person] die [Aufgabe] macht, damit [Ergebnis]."

Beispiel gut:
> "Für einen Simulation-Engineer, der PEM-Elektrolyseur-Zellen auslegt,
> damit er Polarisationskurven und Stack-Dimensionierung ohne CFD-Lizenz
> abschätzen kann."

Beispiel schlecht:
> "Für Engineers und Forscher die PEM-Systeme analysieren wollen."

Wenn du keinen einzelnen Satz hinbekommst, ist der Scope noch nicht klar.
Nicht anfangen.

### 1.2 UI-Ziel-State (jetzt + 6 Monate + 18 Monate)

| Horizont | Was soll das Tool zeigen/können? |
|---|---|
| Jetzt (v0.1) | [konkret] |
| 6 Monate (v0.x) | [konkret] |
| 18 Monate (v1.0) | [konkret] |

Der 18-Monats-State bestimmt die Framework-Wahl. Nicht der 6-Monats-State.

### 1.3 Deploy-Ziel
- [ ] Lokal only (kein Browser nötig)
- [ ] Browser, frei zugänglich (Streamlit Cloud / HuggingFace Spaces / Vercel)
- [ ] Browser, intern (eigener Server / Docker)
- [ ] Desktop-App
- [ ] API / Library (kein UI)

### 1.4 3D-Visualisierung (jetzt oder in 18 Monaten)?
- [ ] Nein → Streamlit/Dash/Gradio alle OK
- [ ] Ja, einfache 3D-Plots (keine Interaktion) → Plotly 3D reicht
- [ ] Ja, interaktives CAD-ähnlich (Rotate, Zoom, Click-on-Part) → kein Streamlit
- [ ] Ja, CAD-Qualität (Export als STEP/STL, Simulation-Geometrie) → Desktop oder NiceGUI/Panel+pyvista

### 1.5 Echtzeit-Simulation oder Batch?
- [ ] Parameter ändern → sofort neues Ergebnis (< 1s) → Streamlit OK
- [ ] Parameter ändern → lange Rechnung (> 5s) → Celery/Background-Job nötig
- [ ] Batch: 1000 Konfigurationen parallel → Streamlit ungeeignet, CLI oder Ray

### 1.6 Multi-User?
- [ ] Single User (Portfolio, persönlich) → kein Auth, kein DB nötig
- [ ] Multi-User, isolierte Sessions → Streamlit session_state reicht
- [ ] Multi-User, geteilte Daten / Konfigurationen → DB + Auth nötig

### 1.7 Welche Physik-Domänen?
Liste alle, die in 18 Monaten drin sein sollen. Das bestimmt,
welche externe Libraries früh als Dependencies eingeplant werden.

Beispiel:
- Elektrochemie (Butler-Volmer, Nernst) → nur numpy, scipy
- Thermodynamik → nur numpy
- Fluid-Mechanik (0D) → nur numpy
- Fluid-Mechanik (1D/2D) → OpenFOAM, FEniCS, cantera
- Strukturmechanik → FEniCS, sfepy, pyvista+FE
- CFD → OpenFOAM-Wrapper, SU2

### 1.8 Wer validiert?
- Wer ist die zitierfähige Quelle für die Physik-Defaults?
- Gegen welche Papers wird v0.1 validiert? (mindestens 1)
- Was ist der Akzeptanzbereich? (RMSE, visueller Check, σ-Band)

---

## 2. Framework-Auswahlmatrix

Nutze 1.2–1.5 um die richtige Zeile zu finden.

| Use Case | Empfehlung | Warum | Nicht wählen |
|---|---|---|---|
| Portfolio-Demo, Charts + Sliders, kein 3D | **Streamlit** | Zero-Config, gratis, Python-only | pyvista, FastAPI |
| Engineering-Dashboard, komplexer State | **Dash** | Callback-Modell skaliert, Plotly nativ | Streamlit (rerun-Modell) |
| Wissenschaftliches Dashboard mit 3D | **Panel (HoloViz)** | pyvista/VTK nativ, bokeh/HoloViews | Streamlit |
| Modernes Python-Web-UI mit 3D | **NiceGUI** | three.js `ui.scene` integriert, Python-first | Streamlit |
| Volle Freiheit, 3D, REST, Auth | **FastAPI + React + three.js** | Unlimitiert | Alles andere |
| Exploration / Prototyp | **Jupyter + ipywidgets + k3d** | Interaktiv, keine Deploy-Hürde | Streamlit (zu rigid) |
| Desktop-App, CAD-Qualität | **PyQt/PySide + pyvistaqt** | Beste 3D-Qualität, GPU | Browser-Deployment unmöglich |
| Library / API ohne UI | **Python Package + FastAPI** | Klare Trennung | Streamlit (UI-Kopplung) |

**Regel:** Die Framework-Entscheidung muss als **ADR-001** dokumentiert
sein. Nicht als Kommentar, nicht als README-Zeile — als ADR.

---

## 3. Architektur-Prinzipien für Simulation-Tools

### 3.1 Layer-Trennung (nicht verhandelbar)

```
┌─────────────────────────────────┐
│          UI Layer                │  ← streamlit_app.py / main.py
│  (Framework-spezifisch)          │     Framework kann ausgetauscht werden
├─────────────────────────────────┤
│       Visualization Layer        │  ← visualization.py
│  (Library-spezifisch: Plotly,    │     Rewrite bei Framework-Wechsel
│   pyvista, three.js-wrapper)     │
├─────────────────────────────────┤
│      Assembly / Composition      │  ← assembly.py
│  (Physik + Geometrie kombiniert) │     Frameworkagnostisch!
├─────────────────────────────────┤
│         Physics Layer            │  ← electrochemistry.py, fluid.py
│  (Reine Physik, Pure Functions)  │     Kein UI-Import, voll testbar
├─────────────────────────────────┤
│       Materials / Presets        │  ← materials.py, components.py
│  (Daten + Specs + Literatur-Refs)│     Frozen Dataclasses
├─────────────────────────────────┤
│       Foundation Layer           │  ← constants.py, units.py
│  (CODATA, SI ↔ Engineering)      │     Niemals ändern ohne ADR
└─────────────────────────────────┘
```

**Regel:** Kein Import von Framework-Code (streamlit, nicegui, dash)
in Physics Layer, Materials Layer oder Foundation Layer. Verletzung = Bug.

**Test:** `import src.electrochemistry` muss ohne installiertes Streamlit
funktionieren.

### 3.2 Einheiten-Disziplin

- Intern: **nur SI** (CODATA 2018)
- UI: Engineering-Units erlaubt, aber nur durch `units.py`
- Tests: Test sowohl in SI als auch Round-Trip über `units.py`
- Niemals: gerundete Konstanten (`R = 8.314` statt `8.314462618`)
- Niemals: Engineering-Units in Physics-Functions ohne expliziten Converter

Datei `units.py` hat mindestens:
- `celsius_to_kelvin` / `kelvin_to_celsius`
- `bar_to_pascal` / `pascal_to_bar`
- `a_per_cm2_to_a_per_m2` / `a_per_m2_to_a_per_cm2`
- `ohm_cm2_to_ohm_m2` / `ohm_m2_to_ohm_cm2`

Neue Einheit → neuer Eintrag in `units.py` + Round-Trip-Test. Keine Ausnahme.

### 3.3 Literatur-Referenzierung

Jede Formel im Code trägt:

```python
def calculate_xyz(...):
    """
    [Formel in LaTeX-Kommentar]
    @ref: Autor Jahr, Eq. (N) oder Table N
    @valid-range: T in [273, 373] K, j in [0, 20000] A/m²
    """
```

Wenn keine Quelle bekannt: `@ref: UNVERIFIED — needs check`
(nicht weglassen, nicht raten).

### 3.4 Preset-System statt Magic Constants

Physikalische Defaults gehören in named Presets, nicht in Funktions-Defaults:

```python
# SCHLECHT:
def Electrochemistry(..., j0_anode=1e-3, ...):

# BESSER:
PRESETS = {
    "IrO2_generic_Carmo2013": ElectrochemPreset(j0_anode=1e-3, ...),
    "IrO2_TiO2_Umicore_Elyst_Ir75": ElectrochemPreset(j0_anode=5e-3, ...),
}
```

Warum: Defaults ohne Namen sind unsichtbare Kalibrierungsannahmen.
Benannte Presets sind testbar, dokumentierbar, und ausschreibbar.

---

## 4. Validierungs-Framework

### 4.1 Validation als Gate, nicht als Feature

Validation ist **kein Backlog-Item**. Es ist eine Pre-Condition für
jede neue Feature-Phase.

| Gate | Bedingung für nächste Phase |
|---|---|
| v0.1 → v0.2 | Modell reproduziert mindestens 1 analytisches Resultat (z. B. Tafel-Slope) |
| v0.2 → v0.3 | Modell liegt visuell im richtigen Bereich einer Literaturkurve |
| v0.3 → v0.x | Modell liegt innerhalb Literatur-Envelope (statistischer Test) |
| v1.0 | Mindestens 2 unabhängige Papers, RMSE dokumentiert, kein offenes UNVERIFIED |

### 4.2 Strict-Xfail-Strategie

Für Kalibrierungs-Targets, die noch nicht erfüllt sind:

```python
@pytest.mark.xfail(
    strict=True,
    reason="[Diagnose]: [Root Cause]. Kalibrierungs-Pfad: [v0.x Scope]. Ref: [doc]"
)
def test_rmse_under_target():
    ...
```

**Strict=True bedeutet:** Wenn der Test unerwartet grün wird, wirft
pytest XPASS und zwingt zu explizitem Re-Baseline. Das ist gewollt —
es verhindert stille Regressionen in beide Richtungen.

### 4.3 Validierungs-Dokument-Struktur

Für jedes Validierungs-Paper eine Datei `docs/validation/<paper>_v<version>.md`:

```
# Paper Validation — vX.Y

**Paper:** Vollständige Zitation + DOI + Open Access (ja/nein)
**Dataset:** Pfad + Herkunft + Digitalisierungsgenauigkeit
**Test file:** Pfad

## Operating conditions (aus dem Paper)
## Results with vX.Y defaults
## Diagnosis (warum Abweichung wenn vorhanden)
## Why xfail instead of calibrating (falls zutreffend)
## v(X+1) path
## Reproduction
```

### 4.4 Single-Paper vs. Statistisches Ensemble

Single-Paper-RMSE allein ist kein ausreichendes Validierungsargument.
Zimmer et al. (2026) zeigen: σ > 500 mV bei gleicher j ist typisch
in PEMWE-Literatur. Das ist kein Ausnahmefall — es gilt für die meisten
experimentellen Domänen.

**Minimum:** Ein Single-Paper-Test (mechanistische Diagnose) + ein
Ensemble-Test (statistische Einordnung) aus einem Literature-Review-Paper
oder Data-Mining-Paper.

---

## 5. Dokumentations-Framework

### Was existieren muss (in dieser Reihenfolge)

| Zeitpunkt | Dokument | Inhalt |
|---|---|---|
| Vor erstem Commit | ADR-001 | Framework-Entscheidung + Trade-offs |
| v0.1 | CLAUDE.md | Scope (drin/draußen), Constraints, Regeln |
| v0.1 | README.md | Ziel-Nutzer, Quick-Start, Validation-Status |
| v0.1 | `constants.py` mit Quellen | CODATA-Version explizit |
| v0.2 | docs/validation/ | Erste Validierungs-Baseline |
| v0.3 | CHANGELOG.md | Keep-a-Changelog Format, ab erstem Eintrag |
| Jede Architekturentscheidung | docs/adr/NNN.md | ADR sofort, nicht nachträglich |
| Release | Closed `[Unreleased]` Block | CHANGELOG + Release-Tag |

### Was NICHT gemacht werden muss

- `build-log.md` — Overhead ohne Nutzen; CHANGELOG reicht
- Separates `decisions-log.md` — ADRs sind das Format
- Tägliche Session-Notes — nur wenn sie zu ADRs/CHANGELOG kondensiert werden

### CLAUDE.md Pflicht-Einträge für Simulations-Projekte

```markdown
## Scope-Grenzen
**Drin:** [konkrete Feature-Liste]
**Draußen bis vX.x:** [konkrete Liste]
**Niemals in diesem Projekt:** [technische Grenzen]

## Framework-Entscheidung
Siehe ADR-001. Begründung nicht hier wiederholen — Verweis reicht.

## UI-Ziel-State (18 Monate)
[Ein Satz was das Tool in 18 Monaten können soll]

## Validation-Gate
Kein Feature-Phase-Wechsel ohne Validation-Baseline.
Strict-xfail für offene Kalibrierungs-Targets.
```

---

## 6. Häufige Fehler und Abwehr-Patterns

| Fehler | Symptom | Abwehr |
|---|---|---|
| Framework ohne Ziel-State gewählt | 3D-Wunsch kollidiert mit Streamlit-Grenzen | Framework-ADR mit 18-Monats-State als Pre-Condition |
| Validation als Feature-Item | RMSE-Überraschung in v0.5 | Validation-Gate zwischen jeder Phase |
| Magic Constants ohne Namen | "Warum ist j0 = 1e-3?" unklar | Named Presets, nie anonyme Defaults |
| CLAUDE.md aufgebläht | Regeln werden ignoriert | Max. 200 Zeilen, Verweise auf ADRs statt Inline-Wiederholung |
| UI-Code in Physics-Layer | Framework-Wechsel teuer | Layer-Trennung + Smoke-Test ohne UI-Framework |
| Session-Degradation | Fix A bricht B bricht C | Rollback nach 3. Kaskade, neue Session |
| Scope-Creep durch "noch schnell" | Lange Phasen ohne greifbaren Output | CLAUDE.md-Grenzen explizit, User-Antwort vor Implementierung |
| Einheitsfehler | A/cm² statt A/m² in Formel | `units.py` + Round-Trip-Test vor erstem Physics-Test |

---

## 7. Wiederverwendbare Physik-Layer-Checkliste

Für einen neuen Simulations-Physik-Layer:

- [ ] `constants.py` — Alle benötigten Konstanten aus CODATA oder ISO-Standard
- [ ] `units.py` — SI ↔ Domain-Engineering-Units, Round-Trip-Tests
- [ ] Jede Funktion: `@ref:` + `@valid-range:`
- [ ] Keine Framework-Imports im Physics-Layer
- [ ] Minimum ein analytischer Self-Check-Test (z. B. Butler-Volmer → Tafel-Slope)
- [ ] Minimum eine Literatur-Baseline bis v0.2

---

## 8. Checkliste für Projektstart

```
Pre-Code:
[ ] Ziel-Nutzer in einem Satz definiert
[ ] UI-Ziel-State für jetzt, 6 Monate, 18 Monate
[ ] Deploy-Ziel festgelegt
[ ] 3D-Bedarf in 18 Monaten: ja/nein
[ ] Framework-ADR geschrieben (ADR-001)
[ ] Validierungs-Paper für v0.1 identifiziert (min. 1)
[ ] CLAUDE.md mit Scope-Grenzen + Framework-Verweis + Validation-Gate

v0.1:
[ ] constants.py mit Quellenangabe
[ ] units.py mit Round-Trip-Tests
[ ] Erstes analytisches Validierungs-Test grün
[ ] README mit Ziel-Nutzer + Quick-Start

v0.2:
[ ] Erste Literatur-Baseline (visuell oder RMSE)
[ ] CHANGELOG gestartet
[ ] Layer-Trennung verifiziert: `import src.physics` ohne Framework möglich

Vor jedem Release:
[ ] Validation-Status aktuell in README
[ ] CHANGELOG [Unreleased] geschlossen
[ ] Alle xfail-Tests haben Diagnose + v(X+1)-Pfad
[ ] ADRs für alle nicht-trivialen Entscheidungen dieser Phase
```
