# INPUT_FUER_TODO

Nur offene, fachlich begründete und nicht duplizierte Verbesserungen eintragen. Erledigte Punkte entfernen oder in eine Historie verschieben.

## 1.1.0 — Executable Foundation
- [ ] Kanonische Verzeichnisstruktur `src/domain`, `src/application`, `src/infrastructure`, `src/presentation`, `src/composition`, `resources`, `config/defaults`, `tests`, `tools` anlegen.
- [ ] Zentrale plattformübergreifende Path-/Storage-API für Basistooldaten, Nutzerdaten, Cache, Logs, Backups und Exporte definieren.
- [ ] Gemeinsamen Pfad-/Dateivalidator mit Root-, Traversal-, Symlink-, Typ-, Größen-, Schema- und Rechteprüfung implementieren.
- [ ] Sicheren atomaren Schreibdienst mit Temp-Datei, Vor-/Nachvalidierung, optionalem Hash und Recovery-Vertrag implementieren.
- [ ] Gemeinsame Fehlerklassen und Fehler-zu-Nutzerhinweis-Abbildung einführen.
- [ ] Strukturiertes Logging mit Korrelations-ID, Größenbegrenzung/Rotation und Diagnoseexport implementieren.
- [ ] Zentrale Design-Tokens für Farben, Abstände, Typografie, Radien, Zustände, Breakpoints und Motion definieren.
- [ ] Wiederverwendbare Basis-UI-Komponenten mit vollständigen Fokus-/Fehler-/Disabled-/Loading-Zuständen vorbereiten.
- [ ] Accessibility- und Responsive-Abnahmecheck als reproduzierbares Qualitätsgate definieren.
- [ ] Testgrundlage für Unit-, Integrations-, Negativ-, Recovery- und Smoke-Tests anlegen.

## 1.2.0 — Reliability & Recovery
- [ ] Deklarierte Action-Policy `reversible|compensatable|cancelable|backup_required|irreversible` als Schema definieren.
- [ ] Backup-/Restore-/Migrationstestmatrix implementieren.
- [ ] Datenbank-Schema-Versionierung und deterministische Migration Foundation anlegen.
- [ ] Crash-/Abbruch-Szenarien für kritische Schreibvorgänge automatisiert testen.
- [ ] Integritätsnachweise für kritische gespeicherte Daten standardisieren.

## 1.3.0 — Dashboard & Diagnostics
- [ ] Dashboard-Komponentenvertrag für anordenbare, skalierbare, ausblendbare und rücksetzbare Karten implementieren.
- [ ] einklappbaren Debug-/Loggingbereich mit Filter, Suche, Kopieren und Export integrieren.
- [ ] Statuskarten für Validierung, Backup/Recovery, Speicher, Warnungen und letzte Fehler vorsehen.
- [ ] Layoutzustand ausschließlich als Nutzerdaten speichern.

## 1.4.0 — Automated Quality Gates
- [ ] CI-Gates für Syntax, Typprüfung, Tests, Pfadsicherheit und Dokumentationskonsistenz einführen.
- [ ] PASS/WARN/FAIL/NOT_RUN maschinenlesbar ausgeben.
- [ ] Schutz gegen widersprüchliche Versionsnummern ergänzen.
- [ ] Repository-weiten Duplikat-/Dead-Code-/Architekturgrenzen-Check evaluieren und nur bei belastbarem Nutzen aktivieren.

## Neuer Verbesserungsvorschlag aus Standards 1.0.0
- [ ] Maschinenlesbare `quality-contract.json` definieren, damit Pfad-, IO-, UI-, Accessibility-, Recovery- und Release-Gates später nicht nur dokumentiert, sondern automatisiert geprüft werden können.
