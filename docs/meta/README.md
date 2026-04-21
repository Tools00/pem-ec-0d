# Meta-Dokumentation — verschoben auf Workspace-Ebene

Die Lessons-Learned- und Projekt-Framework-Dokumente liegen nicht mehr
in diesem Projekt, sondern **eine Ebene höher** im gemeinsamen
Workspace-Ordner, damit sie für alle Simulations-Projekte nutzbar sind:

- **Projekt-spezifische Lessons:**
  `../../../docs/lessons/pem-ec-designer.md`
  (Absolut: `Simulation-tools/docs/lessons/pem-ec-designer.md`)

- **Allgemeines Framework für neue Simulations-Projekte:**
  `../../../docs/simulation-project-framework.md`
  (Absolut: `Simulation-tools/docs/simulation-project-framework.md`)

**Warum auf Workspace-Ebene?**

Die Lehren aus diesem Projekt sollen beim Start des Nachfolgeprojekts
(`Simulation-tools/<projekt-2>/`) direkt gelesen werden. Eine Kopie in
jedem Projekt würde divergieren; ein einziger Ort im Workspace macht
das Framework zur lebenden Referenz.

**Wie das nächste Projekt die Docs nutzt:**

1. Beim Start von Projekt 2: erst `simulation-project-framework.md`
   durchgehen (Pflichtfragen, Framework-Auswahl, Layer-Prinzipien).
2. Lessons-Datei(en) relevanter Vorprojekte lesen — hier: `pem-ec-designer.md`.
3. Eigene `lessons/<projekt-2>.md` bei Projektende schreiben.
4. Wiederkehrende Muster ins Framework-Dokument zurück-destillieren.
