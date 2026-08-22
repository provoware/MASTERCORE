# INPUT_FUER_TODO

Nur offene, fachlich begründete, priorisierte und nicht duplizierte Verbesserungen eintragen. Erledigte Punkte entfernen oder in eine Historie verschieben.

## 2.1.x — Executable Foundation Hardening
- [ ] Zentrale plattformübergreifende Root-Auflösung für `user_config`, `user_content`, `derived_data`, `operational_data` und `recovery_data` ergänzen.
- [ ] Pfadvalidator um Größen-, Format-/Magic-, Schema-, Rechte- und freien-Speicher-Prüfungen erweitern, jeweils nur wo fachlich relevant.
- [ ] Safe-IO gegen TOCTOU-/Symlink-Rennen weiter härten (plattformabhängige dirfd/openat-Strategie prüfen).
- [ ] Backup-/Recovery-Hook vor `backup_required`-Writes integrieren.
- [ ] Fehler→Nutzerhinweis-Abbildung zentral definieren.
- [ ] Logging um Korrelations-ID, Dauer, strukturierte Felder und datensparsamen Diagnoseexport erweitern.
- [ ] Tests für Schreibfehler, unterbrochene Writes, fehlende Rechte und beschädigte Stage-/Finaldaten ergänzen.

## 2.2.0 — Quality Gate Automation
- [ ] G0–G8 aus `docs/QUALITY_GATES.md` als registrierbare Gates im Validator abbilden.
- [ ] PASS/WARN/FAIL/NOT_RUN zusätzlich maschinenlesbar als JSON ausgeben.
- [ ] Dokumentations-/Versionskonsistenz auf alle normativen Dateien erweitern.
- [ ] Ruff als reproduzierbaren Lint-/Import-/Bugbear-Gate integrieren.
- [ ] Statische Typprüfung mit mypy oder pyright als reproduzierbares Gate integrieren.
- [ ] Abhängigkeits-/Supply-Chain-Prüfung mit minimaler zusätzlicher Toollast planen.
- [ ] Backup-/Restore-/Recovery-Testmatrix ergänzen.
- [ ] Branch Protection auf erfolgreichen Quality-Workflow vorbereiten.

## 2.3.0 — UI Foundation
- [ ] Laufende Backendprozesse kontrolliert abbrechen und beim Fensterschließen mit Timeout beenden.
- [ ] Konfigurierbaren, schema-validierten Backend-Startvertrag statt ausschließlicher Dateinamenerkennung ergänzen.
- [ ] Zentrale Design-Tokens für Farben, Abstände, Typografie, Radien, Rahmen, Elevation, Control-Größen, Breakpoints, Motion und Layer definieren.
- [ ] Wiederverwendbare Basis-Komponenten mit vollständigen Zuständen implementieren.
- [ ] Responsive Größenklassen und Layout-Regeln definieren.
- [ ] Accessibility-Checks und Tastatur-/Fokus-Abnahme automatisierbar machen.
- [ ] Einklappbares Profi-Debug-/Loggingpanel mit Filter, Suche, Kopieren und Diagnoseexport implementieren.
- [ ] Dashboard-Shell mit Status, Warnungen, Schnellaktionen, letzten Projekten, Backup/Recovery und Diagnose vorbereiten.
- [ ] Layout Reset und persistente Nutzer-Layoutpräferenzen implementieren.

## 2.4.0 — Reliability & Data Lifecycle
- [ ] Action-Policy `reversible|compensatable|cancelable|backup_required|irreversible` als ausführbares Schema implementieren.
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
**Nächster logischer Schritt: 2.1.x — Foundation Hardening.** Der sichere Kern ist vorhanden; als Nächstes werden Root-Auflösung, Rechte/Schema/Format-Prüfung, Recovery-Hooks sowie Fehler- und Loggingkontext vervollständigt. Für die neue Startroutine ist danach das kontrollierte Beenden laufender Backends die höchste UI-Reliability-Aufgabe; anschließend werden G0–G8 automatisiert.
