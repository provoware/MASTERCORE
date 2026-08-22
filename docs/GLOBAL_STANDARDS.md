# MASTERCORE — Global Engineering Standards

Version: 1.0.0
Status: verbindliche technische Referenz

## 1. Zweck
Diese Datei konkretisiert `AGENTS.md` in wiederverwendbare technische Verträge. Ziel ist ein konsistentes Fundament für alle zukünftigen MASTERCORE-Module.

## 2. Architekturgrenzen
### Domain
Enthält Fachmodelle, Regeln, Invarianten und reine Logik. Keine direkten UI-, Dateisystem-, Datenbank- oder Netzwerkzugriffe.

### Application
Orchestriert Anwendungsfälle, Transaktionen und Workflows. Kennt Verträge/Ports, aber möglichst keine konkreten Infrastrukturdetails.

### Infrastructure
Implementiert Dateisystem, Datenbank, Netzwerk, Betriebssystemintegration, externe Dienste und Persistenzadapter.

### Presentation
Enthält Views, Controller/ViewModels und Nutzerinteraktion. Keine eigenständige Fachlogikduplizierung.

### Composition
Startpunkt, Dependency Wiring, Konfiguration und Lebenszyklus.

## 3. Datenklassen
### Basistooldaten
Code, Defaults, Vorlagen, Schemas und ausgelieferte Ressourcen. Zur Laufzeit grundsätzlich unveränderlich.

### Nutzerdaten
Projekte, Datenbanken, Einstellungen, Layoutzustände, Exporte, Backups, Cache und Logs.

Regeln:
- klare getrennte Roots
- zentrale Auflösung über Path-/Storage-Service
- keine stillen Schreibzugriffe in Installations-/Ressourcenpfade
- Updates dürfen Nutzerdaten nicht überschreiben
- Cache ist entbehrlich; persistente Nutzerdaten nicht

## 4. IO-Lebenszyklus
`resolve → normalize → authorize → inspect → operate → verify → commit/report`

### Vorvalidierung
Je nach Operation:
- Root-Zulässigkeit
- kanonischer Pfad
- Traversal-/Symlink-Schutz
- Existenzstatus
- Typ
- Größe
- Dateierweiterung
- MIME/Magic/Signatur
- Schema/Version
- Rechte
- freier Speicher
- Zielkonflikt

### Schreibvertrag
1. Ziel und Quelle validieren.
2. Recoverybedarf bestimmen.
3. temp-Datei im gleichen Dateisystem anlegen.
4. vollständig schreiben.
5. flush; bei kritischen Daten fsync erwägen.
6. temp-Inhalt nachvalidieren.
7. atomar ersetzen/umbenennen.
8. finalen Inhalt nachvalidieren.
9. erst danach Erfolg melden.

## 5. Datenbankstandard
- explizite Schema-Version
- deterministische Migrationen
- Migrationen getrennt von normalen Leseoperationen
- Transaktion, sofern Backend dies erlaubt
- Backup vor riskanter Migration
- Integritätsprüfung davor/danach
- kein stilles Downgrade
- Rollback-Fähigkeit dokumentieren

## 6. Fehlerklassen
Mindestens logisch unterscheiden:
- ValidationError
- ConfigurationError
- PermissionError
- StorageError
- DataIntegrityError
- MigrationError
- ExternalServiceError
- InternalInvariantError

Ein Nutzerhinweis ist nicht identisch mit dem technischen Fehlerobjekt. Technischer Kontext bleibt diagnostizierbar; Nutzerausgabe bleibt verständlich und handlungsorientiert.

## 7. Retry-Standard
Retry nur wenn:
- Fehler transient sein kann
- Operation idempotent oder anderweitig abgesichert ist
- maximale Anzahl begrenzt ist
- Timeout existiert
- Backoff vorgesehen ist

Kein Retry bei strukturell ungültigen Eingaben, Schemafehlern oder fehlender Berechtigung ohne Änderung der Ursache.

## 8. Recovery-/Undo-Standard
Jede verändernde Action besitzt eine Policy:
- `reversible`
- `compensatable`
- `cancelable`
- `backup_required`
- `irreversible`

UI und Application-Layer dürfen Undo nur anbieten, wenn die Policy das fachlich erlaubt.

## 9. Loggingstandard
Pflichtfelder:
- timestamp
- severity
- component
- operation
- correlation_id
- outcome
- concise_reason

Optionaler technischer Kontext darf keine Secrets enthalten.

Stufen:
`DEBUG | INFO | WARNING | ERROR | CRITICAL`

Logs benötigen Größenbegrenzung oder Rotation. Diagnoseexport soll relevante System-/Versions-/Validierungsdaten bündeln, ohne unnötige private Daten einzuschließen.

## 10. Designsystem
Zentrale Tokens statt lokaler Einzelwerte.

### Tokenfamilien
- semantic colors
- spacing
- typography
- radii
- borders
- elevation
- control sizes
- icon sizes
- breakpoints
- motion
- z-layers

### Spacing
Bevorzugt konsistente 4/8-basierte Skala, z. B. `4, 8, 12, 16, 24, 32, 48`.

### Zustände
Interaktive Komponenten müssen, soweit relevant, `default`, `hover`, `focus`, `active`, `disabled`, `loading`, `success`, `warning`, `error` abdecken.

## 11. Responsive Standard
Mindestens kleine, mittlere und große Layoutklasse berücksichtigen.

Regeln:
- Inhalt priorisieren, nicht nur verkleinern
- keine abgeschnittenen Kernaktionen
- Text darf umbrechen
- Tabellen erhalten für kleine Ansichten Alternative/Scrollstrategie
- Panels können begrenzbar skalierbar/einklappbar sein
- Layoutreset verfügbar
- benutzerspezifische Layouts in Nutzerdaten

## 12. Accessibility Standard
Ziel: WCAG 2.2 AA, soweit technisch anwendbar.

Prüfen:
- Tastaturnavigation
- Fokusreihenfolge
- sichtbarer Fokus
- semantische Labels
- Kontrast
- Status nicht nur per Farbe
- größere Schrift/Zoom
- Touch-/Klickzielgröße
- Screenreader-Status
- Reduced Motion
- verständliche Fehlermeldungen

## 13. Dashboard Standard
Dashboard zeigt arbeitsrelevante Informationen:
- System-/Projektstatus
- Validierungsstatus
- letzte Projekte
- Warnungen
- Daten-/Speicherzustand
- Backup/Recovery
- letzte Fehler
- häufige Aktionen
- nächste Schritte
- kontextbezogene Hilfe

Karten dürfen keine redundanten Kennzahlen ohne Entscheidungshilfe erzeugen.

## 14. Patch Standard
Vor Patch dokumentieren:
- Datei
- Symbol/Bereich
- Ist-Zustand
- Grund
- Risiko
- Datenwirkung
- erwartete Wirkung
- Validierung

Nach Patch dokumentieren:
- tatsächliche Änderung
- ausgeführte Prüfungen
- Ergebnis
- Restunsicherheiten

## 15. Qualitätsgates
Statuswerte:
- PASS
- WARN
- FAIL
- NOT_RUN

`NOT_RUN` darf nie als Erfolg erscheinen.

Relevante Gates:
- Syntax
- Type/Lint
- Unit
- Integration
- Negativpfade
- Recovery
- Migration
- Accessibility
- Responsive
- Smoke/Start
- Dokumentationskonsistenz

## 16. Security Standard
- Eingaben an Grenzen validieren
- Least Privilege
- keine Secrets im Repository
- Shell-Eingaben nicht unsicher konkatenieren
- importierte Dateien als untrusted behandeln
- Pfad-/Traversal-/Symlink-Angriffe verhindern
- Abhängigkeiten bewusst und sparsam einsetzen

## 17. Performance Standard
Erst messen, dann optimieren.

Bevorzugen:
- Streaming/Chunking bei großen Daten
- vermeidbare Vollscans verhindern
- lange UI-Operationen aus Hauptthread auslagern, falls Framework dies verlangt
- Cache nur mit definierter Invalidierung
- Ressourcen deterministisch schließen
- Abbruchmöglichkeit für lange Operationen, soweit sinnvoll

## 18. Dokumentations- und Versionsstandard
- SemVer
- zentrale Versionsquelle
- README/CHANGELOG/TODO nur synchronisieren, wenn betroffen
- Commit-Nachricht beschreibt fachliche Wirkung
- keine offenen TODO-Duplikate
- keine Test-/Qualitätsbehauptung ohne Nachweis

## 19. Laienkommunikation
Manuelle Anleitung immer mit:
1. Voraussetzung
2. exaktem Ort
3. kopierbarem Befehl
4. erwarteter Ausgabe
5. Erfolgskriterium
6. Fehlerfall

## 20. Qualitätshebel
Bei der Wahl des nächsten Schrittes bevorzugen:
`Risikoreduktion + Architekturhebel + Nutzerwert + Wiederverwendbarkeit / Aufwand`.

Damit werden zentrale Verträge und robuste Foundations vor dekorativen Einzelverbesserungen priorisiert.
