# ADR 006 — Visual Stack Designer (v0.4)

**Status:** Accepted — implementiert in v0.4
**Date:** 2026-04-20
**Scope:** Erweiterung des pem-ec-0d um einen visuellen
Stack-Konfigurator (Bauteil-Picker + maßstabsgetreue Geometrie-Vorschau)
innerhalb der bestehenden Streamlit-App.

## Context

v0.3 bildet die Elektrochemie einer PEM-Zelle korrekt ab, hat aber keine
Datenquelle für Stack-Komponenten außerhalb der MEA (Bipolarplatte,
Endplatte, Stromabnehmer, Dichtung, Zuganker). Die Geometrie eines realen
Stacks ist für den User nur als Textparameter („20 Zellen, 100 cm²")
sichtbar — keine Vorschau, keine Plausibilitätsprüfung, keine
Bauteil-Auswahl.

Anwender-Feedback (Portfolio-Review 2026-04-20): Das Tool wirkt
mathematisch stark, aber visuell unkonkret — „man sieht dem Stack nicht
an, wie er aussieht". Für Bewerbungskontext (Simulation-Engineering) ist
das ein Präsentations-Nachteil.

## Decision

Wir bauen einen **Visual Stack Designer** als 6. Tab der App. Technisch:

- Pure Streamlit + Plotly (kein JS, keine React-Komponente, keine neue
  Runtime-Abhängigkeit). Flow-Field als SVG-Shapes zur Laufzeit generiert.
- Neue Module `src/components.py` (Preset-Specs), `src/assembly.py`
  (Konfigurations-Dataclass + Aggregation + JSON-I/O), `src/visualization.py`
  (Plotly-Zeichenfunktionen).
- `src/materials.py` bleibt unverändert; Assembly referenziert MEA-Presets
  per Name (DRY, kein Duplizieren).
- Physik-Kopplung in v0.4 bewusst minimal: nur `bpp.bulk_resistivity × thickness`
  fließt als `r_bpp` in die ohmsche Bilanz. Alle anderen neuen Felder
  (flow_pattern, tie_rod_torque, frame_width) sind Display-Only und
  dokumentierte Hooks für v0.5+.

### Alternativen verworfen

1. **React-Canvas / dnd-kit.** Zu groß, neue Build-Toolchain, kollidiert
   mit der Streamlit-Only-Regel in CLAUDE.md.
2. **streamlit-plotly-events.** Funktioniert, aber unnötig — die Picker
   sind trivial mit `st.selectbox` abgebildet; Klick-Interaktion in der
   Figur braucht v0.4 nicht.
3. **Auto-generierte 3D-Ansicht (pyvista).** Drittes Viewport, schwerer
   Dep, zu weit für eine Zwei-Tage-Erweiterung. v1.0-Scope.

## Design-Entscheidungen (Details)

| Frage | Antwort | Grund |
|---|---|---|
| Materials-Tab ersetzen? | Nein, Assembly ist zusätzlicher Tab | Materials = Datenblatt-Ansicht; Assembly = Konfigurations-Ansicht. Zwei Sichten auf dieselben Daten. |
| Polarisationskurve im Assembly-Tab? | Nein | Verhindert Tab-Überfrachtung, Polarization-Tab bleibt die kanonische Ansicht (User, 2026-04-20). |
| N=200 rendern? | Compressed-View: 3+collapsed+3 Zellen | Plotly bleibt < 80 Shapes, Interaktivität erhalten. |
| BPP-Form | Quadratisch (sqrt(A) + 2·frame) | Rechteckige Stacks brauchen zwei Dimensionen → v0.5-Scope. |
| r_bpp-Coupling aktiv? | **Ja — wired in v0.4.1**: BPP-Picker sitzt in der Sidebar, `r_bpp = ρ·t` fließt in `Electrochemistry.from_engineering`. | Single source of truth für Polarisation + Assembly. |

## Consequences

### Positive

- User kann Stack-Geometrie in unter 10 Sekunden visuell plausibilisieren.
- JSON-Save/Load erlaubt reproduzierbare Konfigurationen (Portfolio-tauglich).
- Neue Komponenten-Specs sind durchgängig SI + Literatur-referenziert,
  konsistent zur bestehenden `materials.py`-Konvention.
- Kein neuer Build-Footprint: nur `plotly` (schon da) + SVG-Shapes.

### Negative / offen

- ~~r_bpp aus Assembly ist noch nicht aktiv im Polarization-Tab.~~
  **Erledigt in v0.4.1:** BPP-Picker in Sidebar, `r_bpp = ρ·t` fließt in
  `Electrochemistry.from_engineering`.
- Tie-rod-Torque, flow_pattern-Druckabfall, gasket-compression-modulus haben
  keinen Physik-Konsumer in v0.4 — sie stehen als Hook für v0.5 (ΔP-Modell)
  bzw. v1.0 (Dichtkraft-FEM).
- Rechteckige Stacks nicht modellierbar.
- Stack-Masse vernachlässigt MEA (< 5 %) und Tie-Rods (< 1 %) — explizit
  dokumentierte Näherung.

## Verweise

- Plan: `docs/planning/visual-designer-plan.md`
- Dataset-Audit: `docs/planning/dataset-audit-2026-04-20.md`
- Presets: Lettenmeier 2016 EES 9(8), Barbir 2012 Ch. 4.3 & 6.3,
  Carmo 2013 IJHE 38(12) §5.1, Wang 2011 IJHE 36(16), Grigoriev 2009 IJHE 34(14).
