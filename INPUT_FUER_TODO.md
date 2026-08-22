# INPUT_FUER_TODO

Nur offene, fachlich begründete, priorisierte und nicht duplizierte Verbesserungen eintragen. Erledigte Punkte entfernen oder in eine Historie verschieben.

## 2.1.2 — Foundation Hardening Restpunkte
- [ ] Format-/Magic-Byte-Prüfungen als operationstypabhängige Validatoren ergänzen; nicht jede Datei pauschal prüfen.
- [ ] Windows-Dateioperationen um eine möglichst handle-basierte No-Follow-/Race-Abwehr ergänzen; POSIX nutzt bereits Directory-FD/O_NOFOLLOW, wo verfügbar.
- [ ] Für extrem konkurrierende Schreibpfade optionalen Lock-/Lease-Vertrag oder Compare-and-Swap-Strategie definieren.
- [ ] Fehler→Nutzerhinweis-Abbildung zentral definieren.
- [ ] Logging um Korrelations-ID, Dauer, strukturierte Felder und datensparsamen Diagnoseexport erweitern.
- [ ] Failure Injection um simulierten Plattenvollzustand, erzwungenen Backup-Fehler und Prozessabbruch-/Crash-Szenarien erweitern.

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

## Erledigt in 2.1.1
- Plattformübergreifende User-Root-Auflösung für mutable Datenklassen.
- Größen-, Suffix-, Rechte- und Freispeicherprüfung für Writes.
- JSON-Schema-/Shape-Validator-Hook vor dem Schreiben.
- POSIX Directory-FD/O_NOFOLLOW-Härtung und wiederholte Pfadvalidierung.
- interner Rollback-Snapshot vor dem Überschreiben bestehender Dateien.
- optionaler SHA-256-verifizierter Backup-Hook.
- Erkennung konkurrierender Zieländerungen und neu auftauchender Zieldateien.
- Failure-Injection-Tests für Abbruch, Korruption, Rechte, Rollback und Parent-Swap.

## Priorität
**Nächster logischer Schritt: 2.2.0 — Quality Gate Automation.** Der Storage-Kern ist jetzt deutlich stärker gegen Datenverlust und Race-/Korruptionsfälle gehärtet. Als nächstes sollten Ruff, statische Typprüfung, G0–G8 und JSON-Reports die Codequalität automatisch und reproduzierbar erzwingen. Parallel kann 2.1.2 die wenigen plattformspezifischen Restpunkte schließen.
