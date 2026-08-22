# MASTERCORE — Quality Gates

Version: 2.0.0
Status: verbindlich

## 1. Zweck
Qualität wird nicht behauptet, sondern über reproduzierbare Gates nachgewiesen.

## 2. Gate-Stufen
### G0 — Scope Gate
- Ziel klar
- betroffener Bereich identifiziert
- keine ungeklärte Scope-Ausweitung

### G1 — Static Gate
Je nach Stack:
- Syntax/Parser
- Format/Lint
- Typprüfung
- Schema

### G2 — Functional Gate
- relevante Unit-Tests
- gezielte Integrationsprüfung
- Smoke-Test

### G3 — Negative Gate
- ungültige Eingaben
- fehlende Dateien/Rechte
- falsche Zustände
- Abbruch/Timeout, wenn relevant

### G4 — Data Integrity Gate
Für schreibende Datenänderungen:
- Vorvalidierung
- Nachvalidierung
- Transaktions-/Atomaritätsverhalten
- Backupbedarf
- Datenintegrität

### G5 — Recovery Gate
Für riskante Änderungen:
- Rollback/Restore
- Crash-/Abbruchszenario
- Migration Recovery

### G6 — UI/Accessibility Gate
Bei UI-Änderungen:
- kleine/große Viewports
- Fokus/Tastatur
- lange Inhalte
- Zoom/Schrift
- Fehler/Loading/Empty
- Kontrast/semantische Labels

### G7 — Regression Gate
- angrenzende Funktionen
- alte unterstützte Datenstände
- Start/Shutdown
- betroffene Workflows

### G8 — Release Gate
Vor Release:
- Version konsistent
- Changelog/README nur soweit betroffen
- keine offenen kritischen FAILs
- Artefakte reproduzierbar
- Integritätsnachweis, sofern vorgesehen

## 3. Statussystem
- PASS
- WARN
- FAIL
- NOT_RUN

Ein Gate darf nur PASS sein, wenn es tatsächlich geprüft wurde.

## 4. Risikobasierte Tiefe
Niedriges Risiko benötigt nicht automatisch jedes Gate. Hohes Daten-/Migrations-/Recovery-Risiko benötigt mehr Gates.

## 5. Stop-Regel
Kritischer FAIL stoppt Freigabe. WARN benötigt dokumentierte Begründung und klare Restgrenze.

## 6. Nachweisformat
Für jedes relevante Gate dokumentieren:
- Gate
- Methode/Befehl/Test
- Ergebnis
- kurze Evidenz
- verbleibende Grenze
