# INPUT_FUER_TODO

Nur offene, fachlich begründete, priorisierte und nicht duplizierte Verbesserungen eintragen. Erledigte Punkte entfernen oder in eine Historie verschieben.

## 2.1.0 — Executable Foundation
- [ ] Kanonische Verzeichnisstruktur `src/domain`, `src/application`, `src/infrastructure`, `src/presentation`, `src/composition`, `resources`, `config/defaults`, `tests`, `tools` anlegen.
- [ ] Zentrale plattformübergreifende Path-/Storage-API für Basistooldaten, Nutzerdaten, Cache, Logs, Backups und Exporte implementieren.
- [ ] Datenklassen aus `DATA_STORAGE_CONTRACT.md` als typisierte Konstanten/Schema abbilden.
- [ ] Gemeinsamen Pfad-/Dateivalidator mit Root-, Traversal-, Symlink-, Typ-, Größen-, Format-, Schema- und Rechteprüfung implementieren.
- [ ] Sicheren atomaren Schreibdienst mit Temp-Datei, Vor-/Nachvalidierung, optionalem Hash und Recovery-Vertrag implementieren.
- [ ] Zentrale Fehlerklassen und Fehler→Nutzerhinweis-Abbildung einführen.
- [ ] Strukturiertes Logging mit Korrelations-ID, Dauer, Rotation, Größenbegrenzung und Diagnoseexport implementieren.
- [ ] Validator für `quality-contract.json` bereitstellen.

## 2.2.0 — Quality Gate Automation
- [ ] CLI `tools/validate_mastercore.py` oder stackäquivalentes Werkzeug anlegen.
- [ ] G0–G8 aus `docs/QUALITY_GATES.md` als ausführbare/registrierbare Gates abbilden.
- [ ] PASS/WARN/FAIL/NOT_RUN maschinenlesbar ausgeben.
- [ ] Dokumentations-/Versionskonsistenz automatisch prüfen.
- [ ] Negativtests für Pfad-Traversal, Symlink-Flucht, fehlende Rechte und beschädigte Daten anlegen.
- [ ] Backup-/Restore-/Recovery-Testmatrix ergänzen.
- [ ] CI-Workflow für statische Prüfungen, Tests und Contract-Validation anlegen.

## 2.3.0 — UI Foundation
- [ ] Zentrale Design-Tokens für Farben, Abstände, Typografie, Radien, Rahmen, Elevation, Control-Größen, Breakpoints, Motion und Layer definieren.
- [ ] Wiederverwendbare Basis-Komponenten mit vollständigen Zuständen implementieren.
- [ ] Responsive Größenklassen und Layout-Regeln definieren.
- [ ] Accessibility-Checks und Tastatur-/Fokus-Abnahme automatisierbar machen.
- [ ] Einklappbares Profi-Debug-/Loggingpanel mit Filter, Suche, Kopieren und Diagnoseexport implementieren.
- [ ] Dashboard-Shell mit Status, Warnungen, Schnellaktionen, letzten Projekten, Backup/Recovery und Diagnose vorbereiten.
- [ ] Layout Reset und persistente Nutzer-Layoutpräferenzen implementieren.

## 2.4.0 — Reliability & Data Lifecycle
- [ ] Action-Policy `reversible|compensatable|cancelable|backup_required|irreversible` als Schema implementieren.
- [ ] Transaktions-/Journalvertrag für mehrstufige schreibende Workflows definieren.
- [ ] Schema-Migrationen mit Backup, Integritätscheck und Recovery-Nachweis implementieren.
- [ ] Cache-Lifecycle und sichere Invalidierung definieren.
- [ ] Backup-Retention und Größenlimits definieren.
- [ ] Crash-/Exit-Recovery-Pfad implementieren und testen.

## 2.5.0 — Release Hardening
- [ ] `VERSION.json`/Projektstatus-Vertrag definieren.
- [ ] Release-Manifest und SHA-256-Nachweise für distributierbare Artefakte einführen.
- [ ] Release Gate automatisieren.
- [ ] Migration-/Upgrade-/Rollback-Hinweise aus Metadaten erzeugbar machen.
- [ ] Reproduzierbaren Build-/Packaging-Pfad definieren.

## Priorität
**Nächster logischer Schritt: 2.1.0 — Executable Foundation.** Erst die zentralen Pfad-, Storage-, Validator-, Fehler- und Logginggrenzen implementieren; danach Quality Gates und UI darauf aufbauen.
