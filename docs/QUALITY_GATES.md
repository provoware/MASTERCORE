# MASTERCORE — Quality Gates

Version: 2.0.0
Status: verbindlich
Executable Mapping: 2.2.0

## 1. Zweck
Qualität wird nicht behauptet, sondern über reproduzierbare Gates nachgewiesen. Seit MASTERCORE 2.2.0 bildet `tools/quality_engine.py` diese Gates ausführbar ab und `tools/validate_mastercore.py` stellt den CLI-Einstieg bereit.

## 2. Gate-Stufen
### G0 — Scope Gate
- Ziel klar
- betroffener Bereich identifiziert
- keine ungeklärte Scope-Ausweitung
- Repository-/Contract-Struktur konsistent

### G1 — Static Gate
Im Python-Kern aktuell zwingend:
- Syntax/Parser über `compileall`
- Ruff für Lint, Imports, Bugbear-, Modernisierungs- und Simplify-Regeln
- mypy mit `strict = true`

### G2 — Functional Gate
- relevante Unit-Tests
- gezielte Integrationsprüfung
- Smoke-/Starttests

### G3 — Negative Gate
- ungültige Eingaben
- fehlende Dateien/Rechte
- falsche Zustände
- Abbruch/Timeout, wenn relevant
- Failure-Injection, soweit vorhanden

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

Solange keine echte automatisierte UI-Acceptance-Harness vorhanden ist, bleibt G6 im normalen CI-Profil explizit `NOT_RUN` und ist nicht Teil der automatisierten Pflichtgates.

### G7 — Regression Gate
- angrenzende Funktionen
- alte unterstützte Datenstände
- Start/Shutdown
- betroffene Workflows
- vollständige automatisierte Testsuite

### G8 — Release Gate
Vor Release:
- Version konsistent
- Changelog/README nur soweit betroffen
- keine offenen kritischen FAILs
- Artefakte reproduzierbar
- Integritätsnachweis, sofern vorgesehen

Solange die Release-/Packaging-Harness noch nicht existiert, bleibt G8 im normalen PR-Profil explizit `NOT_RUN`.

## 3. Statussystem
- `PASS` — Prüfung wurde tatsächlich ausgeführt und bestanden.
- `WARN` — Prüfung wurde ausgeführt; eine dokumentierte Restgrenze bleibt.
- `FAIL` — Prüfung fehlgeschlagen; ein erforderlicher FAIL blockiert die Freigabe.
- `NOT_RUN` — Prüfung wurde nicht ausgeführt.

Ein Gate darf nur PASS sein, wenn es tatsächlich geprüft wurde. Ein erforderliches `NOT_RUN` wird von der Engine nicht als Erfolg behandelt.

## 4. CI-Pflichtprofil 2.2.0
Im normalen Pull-Request-/Main-Quality-Profil sind erforderlich:

`G0 + G1 + G2 + G3 + G4 + G5 + G7`

G6 und G8 bleiben sichtbar im Report, werden aber erst Pflicht, wenn dafür reale automatisierte Harnesses existieren.

## 5. Maschinenlesbare Evidence
Jeder Engine-Lauf erzeugt `quality-evidence.json` mit:
- Evidence-Schema-Version
- Engine-Version
- Zeitpunkt
- Profil
- Gesamtstatus
- Liste der Pflichtgates
- jedem G0–G8-Ergebnis
- ausgeführten Befehlen
- Returncodes
- Laufzeiten
- begrenzter stdout/stderr-Ausgabe

GitHub Actions lädt die Evidence auch dann als Artefakt hoch, wenn ein Pflichtgate fehlschlägt. Dadurch bleibt der Fehlernachweis erhalten.

## 6. Reproduzierbare Toolchain
Die Python-Quality-Werkzeuge werden im `quality`-Extra von `pyproject.toml` versionsgenau gepinnt. CI installiert genau diese Gruppe, bevor die Engine startet.

## 7. Risikobasierte Tiefe
Niedriges Risiko benötigt nicht automatisch jedes Gate. Hohes Daten-/Migrations-/Recovery-Risiko benötigt mehr Gates. Das CI-Pflichtprofil ist die technische Untergrenze für normale Codeänderungen; spezielle Releases dürfen strengere Profile verlangen.

## 8. Stop-Regel
Kritischer FAIL stoppt Freigabe. WARN benötigt dokumentierte Begründung und klare Restgrenze. Fehlende Pflichtwerkzeuge ergeben `NOT_RUN` und damit im Pflichtprofil einen fehlgeschlagenen Gesamtstatus.

## 9. Nachweisformat
Für jedes relevante Gate dokumentieren:
- Gate
- Methode/Befehl/Test
- Ergebnis
- kurze Evidence
- verbleibende Grenze

Die JSON-Evidence ist der maschinenlesbare Primärnachweis; die Konsolenausgabe ist die kompakte Menschenansicht.
