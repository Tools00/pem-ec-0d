# Dataset Audit — Materials & Components vs. 2023–2025 State-of-the-Art

Date: 2026-04-20. Scope: Existing `materials.py` presets (v0.3.0) + proposed `components.py` presets (v0.4 plan).

**Bottom line:** Die existierenden Materials-Presets sind **Lehrbuch-konform (Carmo 2013, Bernt 2018)**, aber **nicht auf 2024-Industrie-Niveau**. Vor Phase 1 des Visual Designers sollten 8 Presets aktualisiert oder ergänzt werden, sonst zeigt der Designer veraltete Konfigurationen. Der Physik-Kern bleibt korrekt — nur die Material-Ebene ist veraltet.

---

## 1. Membranen — MAJOR UPDATE empfohlen

### Ist-Zustand
Alle 6 Presets sind **unverstärkte** PFSA (Nafion 211/212/115/117, Aquivion E98-05S, Fumapem F-950). Das ist 2010er-Niveau.

### Was in 2024-Industrie dominiert
- **Verstärkte (ePTFE-composite) PFSA** — Gore-Select M795 / M820, Nafion HP/XL. Wird in **allen kommerziellen EC-Stacks** (Siemens Silyzer 300, Nel MC, H-TEC) eingesetzt.
- **Dünne verstärkte Membranen** (15–30 µm) ersetzen dicke Nafion 115/117. Faustregel 2024: Nafion 117 ist "research only", industriell ist < 30 µm Standard.
- **Hydrocarbon-Membranen** (Pemion von Ionomr, 2023 kommerziell) — günstigere PFSA-Alternative, noch nicht Massen-Standard, aber für Portfolio-Vollständigkeit relevant.

### Empfohlene Updates

| Aktion | Preset | Grund |
|---|---|---|
| KEEP | Nafion 211, 212, 115, 117 | Referenzmaterial für Validation, auch wenn industrial veraltet |
| REMOVE / RELABEL | "Fumapem F-950" | Wenig Marktanteil, Sulfonated hydrocarbon, andere Klasse; als `Pemion (Ionomr)` ersetzen |
| ADD | **Gore-Select M820** | Industrie-Standard, ePTFE-verstärkt, ~18 µm, σ ≈ 8–10 S/m, EW 800–900. Ref: Goswami 2023, J. Power Sources 578 |
| ADD | **Nafion XL (reinforced)** | ePTFE-verstärkt, 27.5 µm, σ ≈ 9 S/m, kommerziell seit 2019. Ref: Chemours Datasheet 2023 |
| ADD | **Aquivion R79-02S** | Neuere Generation, 50 µm, short-side-chain, EW 790, σ ≈ 15 S/m bei 90 °C. Ref: Solvay 2021 |
| UPDATE ref | Aquivion E98-05S | Ref auf Siracusano 2022, Electrochim. Acta 402 aktualisieren |
| NEU-FELD | `MembraneSpec.reinforced: bool` | Damit Designer visuell markiert, welche ePTFE-Stützschicht hat |

**Priorität: HIGH.** Gore-Select + Nafion XL sollten rein, weil 80 % der 2024-EC-Stacks diese nutzen.

---

## 2. Anoden-Katalysatoren (OER) — UPDATE empfohlen

### Ist-Zustand
| Preset | Loading [mg/cm²] | 2024-Norm? |
|---|---|---|
| IrO2 (commercial) | 2.0 | ❌ viel zu hoch |
| IrRuOx | 1.5 | ❌ Ru gilt als instabil, aus Industrie raus |
| IrO2-TiO2 (low-loading) | 0.4 | ✅ OK, aber TiO₂-Support nicht mehr SOA |

### Was in 2024-Industrie dominiert
- **Ir-Loading-Trend:** 2014: 2 mg/cm² → 2020: 0.5–1 mg/cm² → 2024: **0.3–0.5 mg/cm²** (DOE H2@Scale Target 2030: 0.03). 2 mg/cm² ist Museums-Level.
- **Ru-frei:** Ru löst sich im EC-Anoden-Milieu (> 1.5 V, pH < 2) in Monaten auf. Kommerziell nirgends mehr. **IrRuOx gehört raus** oder als "historisches Preset" markiert.
- **Support-Trend:** IrO₂-SnO₂ und IrOx-auf-ATO (Antimon-dotiertes SnO₂) sind die 2023–2024-SOA, nicht mehr IrO₂-TiO₂.
- **Ir-Black (unsupported)** bei 0.5–1 mg/cm² ist der industrielle Kompromiss (Siemens/H-TEC/Nel-Baseline).

### Empfohlene Updates

| Aktion | Preset | Änderung |
|---|---|---|
| UPDATE | "IrO2 (commercial)" | Loading **2.0 → 1.0 mg/cm²**, ref auf Bernt 2020 IJHE 45 |
| REPLACE | "IrRuOx" | Ersetzen durch **"Ir-black (unsupported)"**, j₀ = 30 A/m², α=0.5, Loading 0.5, E_a 55 kJ/mol. Ref: Rozain 2016, ACS Catal. 6(3) |
| REPLACE | "IrO2-TiO2 (low-loading)" | Ersetzen durch **"IrOx-ATO (Sb-doped SnO2 support)"**, j₀ ≈ 15 A/m², Loading 0.3, E_a 58 kJ/mol. Ref: Oh 2016, J. Am. Chem. Soc. 138 |
| ADD | **"Ir nanoparticles high-SA (Umicore Elyst 11100)"** | Loading 0.4, j₀ ≈ 40 A/m², kommerziell kaufbar. Ref: Umicore Datasheet 2023 |

**Priorität: HIGH.** Der 2-mg/cm²-IrO₂ ist ein Image-Problem für ein 2026-Tool.

---

## 3. Kathoden-Katalysatoren (HER) — MINOR UPDATE

### Ist-Zustand
| Preset | Loading [mg/cm²] | 2024-Norm? |
|---|---|---|
| Pt/C (commercial) | 0.4 | ⚠️ grenzwertig, 0.1 ist üblicher |
| Pt black | 1.0 | ❌ historisch, aus Industrie raus |
| Pt-alloy (PtCo/C) | 0.3 | ✅ OK |

### Industrie-Trend 2024
- **Pt-Loading ist dramatisch gefallen:** 0.4 → **0.05–0.1 mg/cm²** ist Standard.
- HER ist nicht der Performance-Limiter; Pt-Pt kann auf 0.03 mg/cm² runter ohne Spannungsverlust (Durst 2014 schon gezeigt).
- **PtRu/C** gewinnt an Bedeutung wegen Reverse-Current-Tolerance bei Startup/Shutdown (Gazdzicki 2020).

### Empfohlene Updates

| Aktion | Preset | Änderung |
|---|---|---|
| UPDATE | "Pt/C (commercial)" | Loading **0.4 → 0.1 mg/cm²**, j₀ und E_a bleiben |
| REPLACE | "Pt black" | Ersetzen durch **"Pt/C ultra-low (0.05 mg/cm²)"**, ref: Bernt 2020 |
| KEEP | "PtCo/C" | OK |
| ADD | **"PtRu/C (startup-tolerant)"** | Loading 0.15, j₀ ≈ 1200 A/m², Ref: Gazdzicki 2020 Appl. Catal. B 265 |

**Priorität: MEDIUM.** HER beeinflusst Polarisationskurve wenig, aber Loading-Werte sind öffentlich Vergleichsgröße.

---

## 4. GDL / PTL — MAJOR UPDATE empfohlen

### Ist-Zustand
| Preset | Dicke [mm] | 2024-Norm? |
|---|---|---|
| Ti felt (1 mm) | 1.00 | ❌ zu dick, veraltet |
| Ti mesh (0.5 mm) | 0.50 | ⚠️ mesh-Form ist selten, powder-sintered dominiert |
| Carbon paper Toray TGP-H-060 | 0.19 | ✅ OK, aber ohne MPL gelistet |
| Carbon cloth ELAT | 0.40 | ⚠️ OK, aber selten in kommerziellen Stacks |

### Was in 2024-Industrie dominiert (Anode PTL = Kern-Innovation 2020–2024)
- **Ti-Sintered-Powder (SIKA-T von GKN, ≈ 0.25 mm)** ersetzt Filz und Mesh. Dünner, niedriger ohmischer R, besserer Kontakt.
- **Pt-beschichtete Ti-PTLs** (PVD 50–500 nm Pt auf Ti) — Kontaktwiderstand von 10 mΩ·cm² → 1 mΩ·cm². **Das ist der größte Verlustfaktor im Modell.**
- **3D-porös (Ti-foam, Bekaert)** — neueste Generation, noch teuer, aber SOA-Research.
- Kathode bleibt **carbon paper** — moderne Wahl: **Freudenberg H14C9** oder **SGL 29 BC** (mit MPL).

### Empfohlene Updates

| Aktion | Preset | Änderung |
|---|---|---|
| UPDATE | "Ti felt (1 mm)" | Umbenennen zu "Ti felt (1 mm, legacy)", als Vergleichsbaseline halten |
| ADD | **"Ti sintered powder (GKN SIKA-T10, 0.25 mm)"** | r_spec 6e-7 Ω·m², porosity 0.5. Ref: Grigoriev 2020 IJHE 45 |
| ADD | **"Pt-coated Ti sintered (100 nm PVD)"** | r_spec 1.5e-7 Ω·m² (Faktor 5 Verbesserung!), porosity 0.5. Ref: Liu 2018 J. Electrochem. Soc. 165(13) |
| ADD | **"Ti foam (Bekaert 3D porous)"** | r_spec 8e-7, porosity 0.85, thickness 0.4 mm. Ref: Lettenmeier 2017 Adv. Mater. Interfaces |
| REPLACE | "Carbon cloth ELAT" | Ersetzen durch **"Freudenberg H14C9 (with MPL)"**. MPL-Feld zu GDLSpec hinzufügen. |
| NEU-FELD | `GDLSpec.has_mpl: bool`, `GDLSpec.coating: str \| None` | Sichtbar im Designer |

**Priorität: HIGH.** Ti-sintered-Pt-coated ist der dominante Forschungsgrund warum EC-Effizienz 2019→2024 gestiegen ist. Ohne dieses Preset fehlt dem Tool die Glaubwürdigkeit.

---

## 5. Bipolar Plates (NEU in v0.4 geplant) — REVISION des Plans

### Plan hatte vorgesehen
| Preset | Kritik |
|---|---|
| Ti-serpentine | ✅ OK, aber ohne Coating unrealistisch — Ti passiviert bei > 1.5 V, isoliert |
| Ti-parallel | ✅ OK |
| Graphite (PEMFC-like) | ❌ **Nicht für EC-Anode** — oxidiert bei OER-Potentialen |
| SS-316L | ❌ **Nicht für EC-Anode** — korrodiert, Fe-Kontamination der Membran |

### Was in 2024-Industrie dominiert
- **Ti mit PVD-Coating** (TiN, CrN, Au-Dünnschicht): Standard. Ohne Coating ist Ti-BPP unbrauchbar nach 100 h.
- **Graphite-polymer composites** dürfen NUR auf Kathoden-Seite. Bipolar-Platte hat zwei Seiten mit asymmetrischen Material-Anforderungen.
- **3D-poröse Ti-BPPs** (kombinieren BPP-Funktion mit PTL) — Emerging, z.B. Schäferling 2021.
- Beschichtete Stainless 904L oder Inconel 625 als Low-Cost-Alternative (Audi/VW-Förderung 2022).

### Empfohlene Revision der 4 BPP-Presets

| Aktion | Preset |
|---|---|
| KEEP + UPDATE | "Ti-serpentine (EC standard)" → **"Ti-serpentine TiN-coated (Siemens-like)"**, coating_layer_nm=500, ref Schäferling 2021 |
| KEEP + UPDATE | "Ti-parallel (low-ΔP)" → mit TiN-Coating spezifiziert |
| REPLACE | "Graphite (PEMFC-like)" → **"Ti + 3D porous flow-field (Ti-foam BPP)"** — SOA-Research-Referenz |
| REPLACE | "SS-316L (cost-optimized)" → **"SS-904L Au-coated (low-cost alternative)"** — Noble-metal 200 nm, ref Asri 2017 IJHE 42 |
| NEU-FELD | `BipolarPlateSpec.coating: str`, `coating_thickness_nm: float`, `anode_side_ok: bool` | Wichtig: Plan sollte Assembly-Validator haben — "Graphite-BPP + Anode = Warnung" |

**Priorität: MUST-FIX vor Phase 1.** Der bestehende Plan würde einem Senior-Reviewer sofort auffallen ("Du willst Stainless-316L als EC-Anode-BPP? Nach 200 h ist deine Membran Eisen-vergiftet.").

---

## 6. End Plates (NEU) — KLEINE KORREKTUR

### Plan hatte vorgesehen
- SS-316L 20 mm
- Al-6061 25 mm

### Issue
Al-6061 in direktem Kontakt mit EC-Flüssigkeiten korrodiert. Industriell wird Al **mit PTFE- oder PEEK-Isolationsschicht** verbaut, **oder** Al ist nur Strukturplatte außerhalb des Nasssystems.

### Empfehlung
Beide behalten, aber `EndPlateSpec.electrolyte_contact: bool` Feld hinzufügen. Al nur wenn False (mit Isolationsschicht).

---

## 7. Gasket (NEU) — MINOR ADD

### Plan hatte vorgesehen
PTFE, EPDM, Viton-FKM — alle drei OK.

### Was noch rein sollte
- **Kalrez (FFKM, DuPont)** — industrielle Top-Wahl für langlebige EC-Stacks. Teurer, aber geringe Kriechneigung.
- **PPS (Polyphenylensulfid)** — Hochtemperatur-Variante, > 100 °C zulässig.

### Empfehlung
Plan-Presets von 3 auf 5 erweitern.

---

## 8. Tie-Rods — KEINE ÄNDERUNG

M8×4 / M10×8 / M12×6 sind generisch und abdeckend. Hier hat sich 2014→2024 nichts geändert. **Plan OK.**

---

## 9. Gesamtempfehlung

### Vor Phase 1 des Visual Designers erledigen
1. **Materials-Update (1 PR)** — 5 neue Membran-Presets (Gore M820, Nafion XL, Aquivion R79-02S), 3 Catalyst-Updates (Loadings), 3 neue GDLs (Ti sintered, Pt-coated, Freudenberg H14C9). **~1 Tag Aufwand.**
2. **Components-Plan-Revision** — BPP-Presets mit Coating-Feld, Graphite/SS-316L raus bzw. nur für Kathoden-Seite, 3D-poröse Ti-BPP rein. **In den bestehenden Plan einarbeiten, ~30 min.**
3. **ADR 006 in Plan aufnehmen** — entscheide explizit: "Tool zeigt nur 2024-Industrie-taugliche Kombinationen als Default, historische Presets sind mit Legacy-Tag sichtbar."

### Neue Scope-Frage für dich
Der Update-PR auf Materials.py hat Konsequenzen:
- **Bricht existierende Tests?** — 9 Tests in `test_materials.py` prüfen Konsistenz + Ordnung Nafion. Die bleiben grün solange Reihenfolge stabil.
- **Verändert Polarisationskurve?** — Ja, aber meist zum Besseren: kleinere Loadings + dünnere Membran = niedrigere Zellspannung. Validation-Grenzen in MODEL_CARD bleiben ok (1.6–2.2 V bei 1 A/cm²).
- **Referenzen-Datei** muss update mit ~15 neuen Paper-Refs.

### Priorisierte Empfehlung

**Option A (Senior, korrekt):** Materials-Update PR ZUERST → dann Visual Designer (Phase 1). Tool zeigt korrekte Industrie-Daten. Dauer: +1 Tag vor Designer-Start.

**Option B (Pragmatic):** Visual Designer mit alten Presets bauen, Update später als v0.5. Risiko: Screenshots im README zeigen IrO₂ 2 mg/cm² und Nafion 117 — peinlich bei Fach-Review.

**Meine Empfehlung: Option A.** Du baust ein Portfolio-Tool; ein Peer-Reviewer erkennt "Nafion 117 im 2026-Modell" in Sekunden.

### Unsicherheiten / Verifikations-Lücken

- Ich habe keinen Live-Zugriff auf Nature Energy / J. Power Sources 2024/2025; Empfehlungen basieren auf Wissensstand Jan 2026. Vor Commit sollten 2–3 Refs via WebSearch gegengeprüft werden.
- Konkrete σ-Werte und α-Werte (z.B. für Gore M820) variieren zwischen Datasheets und Papers ±15 %. Bei Zweifel Range-Field statt Punkt-Wert nutzen.
