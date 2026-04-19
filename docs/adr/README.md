# Architecture Decision Records (ADR)

Format nach [Michael Nygard](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions.html).

Pro relevante Architektur-Entscheidung eine Datei. Immer dieselbe Struktur:
**Status · Date · Context · Alternativen · Entscheidung · Begründung · Konsequenzen · Re-Evaluation-Trigger.**

## Index

| # | Titel | Status | Date |
|---|---|---|---|
| [001](001-python-0d-mvp.md) | Python + 0D-Modell für MVP | Accepted | 2026-04-19 |
| [002](002-hybrid-vs-cfd.md) | Hybrid-Ansatz vs. Full-CFD (AVL Fire M & Co.) | Accepted | 2026-04-19 |

## Regeln

- Einmal geschrieben, **nie rückwirkend geändert** — bei neuer Entscheidung neue ADR mit Verweis auf alte.
- Bei "Superseded": alter ADR-Status auf "Superseded by NNN" setzen, Inhalt unverändert lassen.
- Trivialentscheidungen (Formatierungsregeln, Lib-Namen) gehören **nicht** hierher.
- Kriterium: "Würde ein neuer Contributor in 6 Monaten fragen 'warum?'" → ja = ADR nötig.
