# INPUT_FUER_TODO

Nur offene, fachlich begründete, priorisierte und nicht duplizierte Verbesserungen eintragen. Erledigte Punkte entfernen oder in eine Historie verschieben.

## 2.1.2 — Foundation Hardening Restpunkte
- [ ] Format-/Magic-Byte-Prüfungen als operationstypabhängige Validatoren ergänzen; nicht jede Datei pauschal prüfen.
- [ ] Windows-Dateioperationen um eine möglichst handle-basierte No-Follow-/Race-Abwehr ergänzen; POSIX nutzt bereits Directory-FD/O_NOFOLLOW, wo verfügbar.
- [ ] Für extrem konkurrierende Schreibpfade optionalen Lock-/Lease-Vertrag oder Compare-and-Swap-Strategie definieren.
- [ ] Fehler→Nutzerhinweis-Abbildung zentral definieren.
- [ ] Logging um Korrelations-ID, Dauer, strukturierte Felder und datensparsamen Diagnoseexport erweitern.
- [ ] Failure Injection um simulierten Plattenvollzustand, erzwungenen Backup-Fehler und Prozessabbruch-/Crash-Szenarien erweitern.

## 2.2.1 — Quality Gate Hardening
- [ ] G6 UI/Accessibility mit echter automatisierter Acceptance-Harness statt `NOT_RUN` abdecken.
- [ ] G8 Release mit Build-, Manifest-, Hash- und Reproduzierbarkeitsprüfung automatisieren.
- [ ] Dokumentations-/Versionskonsistenz um semantische Querverweise zwischen normativen Dateien erweitern.
- [ ] Abhängigkeits-/Supply-Chain-Prüfung mit minimaler zusätzlicher Toollast integrieren.
- [ ] Quality-Evidence um Git-Commit, Tree-SHA und optional Artefakt-Hashes erweitern.
- [ ] Branch Protection so konfigurieren, dass `MASTERCORE Quality` vor Merge nach `main` zwingend erfolgreich sein muss.
- [ ] Optional einen schnellen Changed-Files-Modus ergänzen, ohne das vollständige G7-Regressionsgate im PR zu ersetzen.

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

## Erledigt in 2.2.0
- G0–G8 als ausführbare Quality-Gate-Engine abgebildet.
- Pflichtprofil mit G0, G1, G2, G3, G4, G5 und G7 eingeführt.
- `PASS/WARN/FAIL/NOT_RUN` maschinenlesbar und strikt aggregiert.
- Ruff als reproduzierbares Lint-/Import-/Bugbear-Gate integriert.
- mypy in striktem Modus als Typgate integriert.
- JSON-Evidence mit Befehlen, Returncodes, Laufzeiten und begrenzter Ausgabe eingeführt.
- Evidence wird auch bei fehlgeschlagenem Gate als GitHub-Actions-Artefakt hochgeladen.
- Gate-Aggregation und atomarer Evidence-Write besitzen eigene Unit-Tests.
- Bestehende Ruff-/mypy-Funde im Produkt- und Testcode behoben statt ignoriert.

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
**Nächster logischer Schritt: 2.2.1 — Quality Gate Hardening.** Die Quality Gate Engine erzwingt jetzt statische Qualität, Tests, Datenintegrität und Recovery reproduzierbar. Der größte verbleibende Hebel ist Branch Protection plus echte G6-/G8-Harnesses; parallel können die plattformspezifischen 2.1.2-Restpunkte geschlossen werden.
