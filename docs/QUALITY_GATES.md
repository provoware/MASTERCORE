# MASTERCORE — Quality Gates

Version: 2.0.0
Status: verbindlich
Executable Mapping: 2.2.2

## 1. Zweck
Qualität wird nicht behauptet, sondern über reproduzierbare Gates nachgewiesen. `tools/quality_engine.py` bildet G0–G8 ausführbar ab; `tools/validate_mastercore.py` ist der CLI-Einstieg.

## 2. Gate-Stufen
### G0 — Scope / Contract
- Pflichtstruktur vorhanden
- Qualitätsvertrag konsistent
- Quality-Engine-, Paket- und Runtime-Version synchron
- Required-Check-Name stabil

### G1 — Static
Im Python-Kern zwingend:
- `compileall`
- Ruff für Lint, Imports, Bugbear, Modernisierung und Simplify
- mypy mit `strict = true`

### G2 — Functional
- funktionale Unit-/Use-Case-Tests
- Start-/Smoke-Prüfungen

### G3 — Negative
- ungültige Eingaben
- fehlende Dateien/Rechte
- falsche Zustände
- Abbruch-/Failure-Injection-Fälle

### G4 — Data Integrity
- Vorvalidierung
- Nachvalidierung
- Atomarität
- Integritätsnachweis
- Backup-/Datenvertrag

### G5 — Recovery
- Rollback/Restore
- Fehler nach Replace
- Recovery-Szenarien

### G6 — UI / Accessibility
Seit 2.2.2 automatisiert und im CI-Profil verpflichtend. Die Tk-Oberfläche wird unter Xvfb headless geprüft auf:
- Initialfokus
- Tastaturkürzel
- explizit fokussierbare Primärbedienelemente
- Small Viewport 640×440
- Large Viewport 1440×900
- große Standardschrift
- sichtbare Hauptaktionen
- Fehlerzustand und Rückkehr aus Busy-State
- verständliche Lösung und technische Details
- textuelle INFO/PASS/WARN/FAIL-Zustände, damit Status nicht nur über Farbe vermittelt wird

G6 ist eine automatisierte Baseline-Acceptance-Harness. Sie ersetzt keine vollständige manuelle Screenreader-, Kontrast- oder plattformspezifische WCAG-Abnahme.

### G7 — Regression
- vollständige automatisierte Testsuite
- läuft im CI ebenfalls unter Xvfb, damit UI-Tests Bestandteil der Gesamtregression sind

### G8 — Release
Noch `NOT_RUN` im normalen PR-Profil, bis eine reale Release-/Packaging-Harness existiert. Ziel:
- Versionen
- Build
- Manifest
- SHA-256
- Reproduzierbarkeit
- Release-Artefakte

## 3. Statussystem
- `PASS` — tatsächlich ausgeführt und bestanden
- `WARN` — ausgeführt, aber dokumentierte Restgrenze
- `FAIL` — nicht freigabefähig
- `NOT_RUN` — nicht ausgeführt

Ein erforderliches `NOT_RUN` ist kein Erfolg.

## 4. CI-Pflichtprofil 2.2.2
Im normalen Pull-Request-/Main-Quality-Profil sind erforderlich:

`G0 + G1 + G2 + G3 + G4 + G5 + G6 + G7`

G8 bleibt sichtbar `NOT_RUN`, bis die Release-Harness real vorhanden ist.

## 5. Required Status Check
Der stabile Checkname lautet:

`MASTERCORE Quality`

Er ist in `.github/workflows/quality.yml` als Jobname und in `quality-contract.json` als `quality_automation.required_status_check` hinterlegt. G0 prüft die Konsistenz.

Die serverseitige GitHub-Branch-Protection muss diesen Check separat als Required Status Check für `main` aktivieren. Details: `docs/BRANCH_PROTECTION.md`.

## 6. Maschinenlesbare Evidence
Jeder Engine-Lauf erzeugt `quality-evidence.json` mit:
- Evidence-Schema-Version
- Engine-Version
- Zeitpunkt
- Profil
- Gesamtstatus
- Required-Check-Name
- Liste der Pflichtgates
- jedem G0–G8-Ergebnis
- Befehlen
- Returncodes
- Laufzeiten
- begrenzter stdout/stderr-Ausgabe

GitHub Actions lädt die Evidence auch bei einem fehlgeschlagenen Pflichtgate als Artefakt hoch.

## 7. Reproduzierbare Toolchain
Ruff und mypy sind im `quality`-Extra von `pyproject.toml` versionsgenau gepinnt. Die CI installiert zusätzlich Xvfb/Xauth/Tk für reproduzierbare Headless-UI-Prüfungen.

## 8. Stop-Regel
Kritischer FAIL stoppt Freigabe. WARN benötigt eine dokumentierte Restgrenze. Fehlende Pflichtwerkzeuge führen zu `NOT_RUN` und damit zu einem fehlgeschlagenen Pflichtprofil.
