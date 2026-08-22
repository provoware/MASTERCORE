# INPUT_FUER_TODO

Nur offene, fachlich begründete, priorisierte und nicht duplizierte Verbesserungen eintragen. Erledigte Punkte werden in die Historie verschoben.

## 2.1.2 — Foundation Hardening Restpunkte
- [ ] Format-/Magic-Byte-Prüfungen operationstypabhängig ergänzen.
- [ ] Windows-Dateioperationen um handle-basierte No-Follow-/Race-Abwehr ergänzen.
- [ ] Für extrem konkurrierende Schreibpfade Lock-/Lease- oder Compare-and-Swap-Vertrag definieren.
- [ ] Fehler→Nutzerhinweis-Abbildung zentral definieren.
- [ ] Logging um Korrelations-ID, Dauer, strukturierte Felder und Diagnoseexport erweitern.
- [ ] Failure Injection um Disk-full-, Backup-/Restore-Fehler und Prozessabbruch erweitern.

## 2.2.1 — Branch Protection
- [ ] GitHub-serverseitig Schutzregel für `main` aktivieren.
- [ ] Pull Request vor Merge verlangen.
- [ ] `MASTERCORE Quality` als Required Status Check aktivieren.
- [ ] Wenn verfügbar „Branch muss aktuell sein“ verlangen.
- [ ] Force Pushes und Branch-Löschung sperren.
- [ ] Schutz mit absichtlich rotem Test-PR praktisch verifizieren.

Hinweis: Repository und Quality-Contract sind dafür vorbereitet. Die verbundene GitHub-Schnittstelle stellt aktuell keine schreibbare Branch-Protection-/Ruleset-Aktion bereit; deshalb bleibt die serverseitige Aktivierung ehrlich offen.

## 2.2.3 — G8 Release Evidence
- [ ] G8 mit Build-, Manifest-, Hash- und Reproduzierbarkeitsprüfung automatisieren.
- [ ] `VERSION.json`/Projektstatus-Vertrag definieren.
- [ ] Quality-Evidence um Git-Commit, Tree-SHA und Release-Artefakt-Hashes erweitern.
- [ ] Abhängigkeits-/Supply-Chain-Prüfung mit minimaler zusätzlicher Toollast integrieren.
- [ ] Reproduzierbaren Packaging-Pfad definieren.

## 2.3.0 — UI Foundation
- [ ] Laufende Backendprozesse kontrolliert abbrechen und beim Fensterschließen mit Timeout beenden.
- [ ] Konfigurierbaren, schema-validierten Backend-Startvertrag ergänzen.
- [ ] Zentrale Design-Tokens für Farben, Abstände, Typografie, Radien, Rahmen, Elevation, Control-Größen, Breakpoints, Motion und Layer definieren.
- [ ] Wiederverwendbare Basis-Komponenten mit vollständigen Zuständen implementieren.
- [ ] Responsive Größenklassen und Layout-Regeln definieren.
- [ ] Kontrast- und Screenreader-Abnahme ergänzen; G6 deckt aktuell die automatisierbare Tk-Baseline ab.
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

## Erledigt in 2.2.2
- G6 UI/Accessibility als echte Xvfb-basierte Acceptance-Harness umgesetzt.
- G6 in das verpflichtende CI-Profil aufgenommen.
- G7 so erweitert, dass die komplette Regression inklusive UI unter Xvfb läuft.
- Initialfokus und Tastaturkürzel automatisiert geprüft.
- Primäre Bedienelemente explizit tastaturfokussierbar gemacht.
- Small-/Large-Viewport-Abnahme für 640×440 und 1440×900 ergänzt.
- große Standardschrift und sichtbare Hauptaktionen geprüft.
- Fehlerzustand, Recovery aus Busy-State sowie Lösung/Technikdetails geprüft.
- INFO/PASS/WARN/FAIL textuell geprüft, damit Status nicht allein von Farbe abhängt.
- Quality-Contract um Engine-Version, Pflichtgates und stabilen Required-Check-Namen ergänzt.
- Runtime-, Paket- und Engine-Version in G0 gegeneinander validiert.
- Branch-Protection-Zielvertrag in `docs/BRANCH_PROTECTION.md` dokumentiert.

## Erledigt in 2.2.0
- G0–G8 als ausführbare Quality-Gate-Engine abgebildet.
- Ruff und striktes mypy integriert.
- JSON-Evidence mit Befehlen, Returncodes und Laufzeiten eingeführt.
- Evidence wird auch bei fehlgeschlagenem Gate als GitHub-Actions-Artefakt hochgeladen.
- Bestehende Ruff-/mypy-Funde im Produkt- und Testcode behoben statt ignoriert.

## Erledigt in 2.1.1
- Plattformübergreifende User-Root-Auflösung.
- Größen-, Suffix-, Rechte- und Freispeicherprüfung.
- JSON-Validator-Hook, Rollback-Snapshot und verifizierte Backups.
- POSIX Directory-FD/O_NOFOLLOW-Härtung.
- Failure-Injection-Tests für Abbruch, Korruption, Rechte, Rollback und Parent-Swap.

## Priorität
**Nächster logischer Schritt: 2.2.1 Branch Protection serverseitig aktivieren und danach 2.2.3 G8 Release Evidence implementieren.** G6 ist nun ein echtes Pflichtgate; der verbleibende GitHub-Schutz muss noch als Repository-Regel eingeschaltet werden.
