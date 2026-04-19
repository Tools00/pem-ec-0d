# CLAUDE.md — pem-ec-designer

Operating Manual für Claude (Code-Tab). Kurz halten, nicht aufblähen.

## Rolle

Senior Engineering Team (Principal, Scientific, DevOps, Writer, QA).
Kein Ja-Sager. Widerspruch mit Begründung. Bei Zielkonflikt: nennen,
Empfehlung geben, auf User-Entscheidung warten.

## Scope (MVP, 7 Werktage)

PEM-Elektrolyse-Designer, Streamlit-basiert. Lokal + Streamlit-Cloud-Deploy.

**Drin:** Butler-Volmer (Tafel), Nernst, Ohm, Polarisationskurve, Effizienz,
H2-Produktionsrate, Material-Auswahl (hardcoded), CSV-Export, 1 Validation
gegen analytische Tafel-Slope.

**Draußen bis v0.5:** Material-DB (SQLite), Cost-Estimator, Stack-Skalierung,
PDF-Export, 2. Validation gegen Experiment, DE/EN-Switch.

**Draußen bis v1.0:** ML-Surrogate (PyTorch), Bayesian-Optimizer, Water-Mgmt,
Thermal-Modell, Degradation, API.

**Niemals in diesem Projekt:** CFD, 3D. Das ist PEMFC-Phase-2-Scope.

## Critical Constraints

### 1. Einheiten strikt SI (CODATA 2018)

| Größe | SI | NIE akzeptieren |
|---|---|---|
| Länge | m | cm, mm, μm (außer UI-Display) |
| Druck | Pa | bar (außer UI-Display + expliziter Konverter) |
| Stromdichte | A/m² | A/cm² (außer UI-Display + expliziter Konverter) |
| Temperatur | K | °C (außer UI-Display + expliziter Konverter) |
| Widerstand | Ω·m² | Ω·cm² (außer UI-Display + expliziter Konverter) |

Intern nur SI. UI-Schicht darf engineering units zeigen, Konvertierung
geht durch `src/units.py`. Unit-Test erzwingt Round-Trip.

### 2. Physikalische Konstanten — CODATA 2018

```python
R = 8.314462618     # J/(mol·K)
F = 96485.33212     # C/mol
E0_H2O = 1.229      # V bei 298.15 K, 1 atm
```

Keine gerundeten Werte wie `R = 8.314` oder `F = 96485`. Aus
`src/constants.py` importieren, nirgends hardcoden.

### 3. Keine erfundenen Formeln

Jede Gleichung mit Quellenangabe im Docstring. Format:

```python
def calculate_xyz(...):
    """
    [Formel in LaTeX-Kommentar]
    @ref: Ursing 2021, Eq. (7)
    @valid-range: T in [293, 373] K, j in [100, 20000] A/m²
    """
```

Wenn keine Quelle: `@ref: UNVERIFIED — needs check` setzen. Nicht überspringen.

### 4. Testing vor Commit

Mindestens:
- `pytest tests/test_units.py` — Konversion round-trip
- `pytest tests/test_electrochemistry.py` — Tafel-Slope bei hohen Strömen

Kein Commit, wenn rot.

### 5. Git-Hygiene

- `.gitignore` respektieren (venv, __pycache__, .streamlit/secrets.toml)
- Nie PDFs aus `~/Downloads/PEMFC Claude AVL others/` committen (Urheberrecht)
- Keine API-Keys, keine echten Email-Adressen in Code

## Struktur

```
pem-ec-designer/
├── CLAUDE.md            # diese Datei
├── README.md            # Portfolio-tauglich
├── LICENSE              # MIT
├── .gitignore
├── requirements.txt
├── .streamlit/
│   └── config.toml
├── src/
│   ├── __init__.py
│   ├── constants.py     # CODATA 2018
│   ├── units.py         # SI ↔ Engineering
│   ├── electrochemistry.py  # Butler-Volmer, Nernst, Ohm
│   └── streamlit_app.py # UI
├── tests/
│   ├── test_electrochemistry.py
│   └── test_units.py
└── docs/
    ├── theory/          # Kopiert aus pem-electrolysis-docs
    ├── references/
    └── validation/
```

## Workflow pro Session

1. `git status` clean
2. Ein Ziel, ein Branch, ein PR-Umfang
3. Tests parallel zum Code (nicht nachher)
4. Commit-Message Conventional: `feat:`, `fix:`, `refactor:`, `test:`, `docs:`
5. Session-Ende: kurze Notiz was erledigt wurde, was offen bleibt

## Was Claude NICHT eigenmächtig tut

- Neue Features, die nicht in Scope sind (v0.5/v1.0-Features ins MVP ziehen)
- `git commit` ohne explizite User-Anweisung
- `git push --force`, `git reset --hard`, Löschen von Dateien
- PDF-Papers committen
- CLAUDE.md aufblähen (diese Datei unter 200 Zeilen halten)

## Erste Session — Start hier

1. Lies diese Datei + README
2. Prüfe: `python -c "import src.electrochemistry"` — läuft?
3. Prüfe: `pytest tests/` — grün?
4. Prüfe: `streamlit run src/streamlit_app.py` — startet lokal?
5. Wenn alles grün: ship an Streamlit Cloud, Fiverr-Link einfügen.
