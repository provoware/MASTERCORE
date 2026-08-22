# MASTERCORE — Globale Standards

Version: 0.1.0

## 1. Zweck
Diese Datei ist die technische Referenz hinter `AGENTS.md`. Sie definiert globale, projektübergreifende Regeln für Architektur, Daten, Dateisystem, Fehlerbehandlung, Oberfläche und Qualität.

## 2. Schichtenmodell
Empfohlene Schichten:
1. **Domain** — Fachlogik und Regeln, ohne UI-/Dateisystemabhängigkeit.
2. **Application** — Anwendungsfälle und Ablaufkoordination.
3. **Infrastructure** — Dateien, Datenbank, Netzwerk, Betriebssystem.
4. **Presentation** — UI, ViewModels/Controller, Nutzerinteraktion.
5. **Composition** — Start, Dependency Wiring, Konfiguration.

Abhängigkeiten dürfen nicht unkontrolliert quer durch alle Schichten laufen.

## 3. Datenklassen und Speicherorte
### Basistooldaten
- Programmcode
- Standardkonfiguration
- Schemas
- Vorlagen
- Icons und statische Ressourcen

Diese Daten werden mit dem Programm ausgeliefert und sind zur Laufzeit grundsätzlich unveränderlich.

### Nutzerdaten
- Projekte
- Datenbanken
- Nutzerkonfiguration
- Layoutpräferenzen
- Exporte
- Backups
- Cache
- Logs

Diese Daten liegen getrennt von den Basistooldaten. Updates dürfen sie niemals überschreiben.

## 4. IO-Vertrag
Jede Dateioperation folgt demselben Lebenszyklus:

`resolve → normalize → authorize → inspect → operate → verify → commit/report`

### Vorvalidierung
- erlaubter Root
- kanonischer/normalisierter Pfad
- Existenzstatus
- Typ
- Größe
- Erweiterung/Format
- Schema/Signatur, sofern vorhanden
- Rechte
- Speicherplatz
- Symlink-/Traversal-Schutz

### Schreiben
- temporär schreiben
- Inhalt validieren
- optional Hash bilden
- atomar ersetzen
- Fehlerfall ohne beschädigte Zieldatei verlassen

### Nachvalidierung
- Ziel vorhanden
- erwarteter Dateityp
- erwartete Mindest-/Maximalgröße
- Schema korrekt
- optional Hash/Signatur korrekt
- Fehler sauber protokolliert

## 5. Fehlerklassen
Mindestens unterscheiden:
- `ValidationError`
- `ConfigurationError`
- `PermissionError`
- `StorageError`
- `DataIntegrityError`
- `MigrationError`
- `ExternalServiceError`
- `UserInputError`
- `UnexpectedApplicationError`

Nutzeroberflächen zeigen keine rohen Stacktraces als Hauptmeldung. Technische Details gehören in den Diagnosebereich.

## 6. Recovery
Für kritische Nutzerdaten:
- Backup vor Migration oder destruktiver Änderung.
- Atomare Updates bevorzugen.
- Journal/Transaktion bei mehrstufigen Schreibvorgängen.
- Unterbrochene Operationen müssen erkennbar sein.
- Wiederanlauf darf nicht stillschweigend beschädigte Zwischenstände akzeptieren.

## 7. Logging
Strukturiertes Logging bevorzugen.

Pflichtfelder, soweit verfügbar:
- timestamp
- level
- component
- operation
- result
- correlation_id
- message
- error_type

Nicht loggen:
- Passwörter
- Tokens
- private Schlüssel
- vollständige sensible Nutzerdaten

## 8. Design-Tokens
Ein globales Token-System ist Pflicht.

### Abstände
Bevorzugte Skala: `4, 8, 12, 16, 24, 32, 48`.

### Radien
Kleine, mittlere und große Standardradien statt individueller Einzelwerte.

### Typografie
Zentrale Rollen:
- body
- body-strong
- caption
- label
- heading-sm
- heading-md
- heading-lg

### Farben
Semantische Rollen statt hart codierter Komponentenfarben:
- background
- surface
- surface-elevated
- text
- text-muted
- primary
- success
- warning
- danger
- focus
- border

## 9. Responsive Layout
- Kein starres Desktop-only-Layout.
- Komponenten definieren Mindest-, Ideal- und Maximalbreiten.
- Inhalt priorisieren statt nur verkleinern.
- Navigation darf auf kleineren Geräten in kompakte Form wechseln.
- Dashboard-Karten dürfen umbrechen.
- Resize-/Docking-Mechaniken müssen Grenzen und Reset besitzen.

## 10. Barrierefreiheit
Mindeststandard: WCAG 2.2 AA als Ziel.

Pflicht:
- Tastaturbedienung
- sichtbarer Fokus
- sinnvolle Fokusreihenfolge
- ausreichende Kontraste
- verständliche Labels
- Fehlertexte mit Ursache und Lösung
- keine reine Farbcodierung
- Reduced Motion
- skalierbare Schrift/Zoom

## 11. Dashboard
Jede Kachel braucht einen klaren Zweck. Keine Informationsdeko ohne Handlungswert.

Mögliche Kernkacheln:
- Projektstatus
- letzte Projekte
- offene Warnungen
- Daten-/Speicherstatus
- Backupstatus
- Diagnose
- Schnellaktionen
- Hilfe

Layoutpräferenzen werden als Nutzerdaten gespeichert.

## 12. Patchstandard
Vor jedem Patch muss eine Positionsermittlung stattfinden.

Bevorzugte Anker:
1. Symbol/Funktion/Klasse
2. eindeutiger Konfigurationsschlüssel
3. Selektor/Komponentenname
4. kleine eindeutige Kontextpassage

Zeilennummern allein sind kein stabiler Patchanker.

## 13. Validierungsstufen
### V0 — Bestand
Datei vorhanden, relevante Struktur gelesen.

### V1 — Vorprüfung
Patchziel und Voraussetzungen gültig.

### V2 — Syntax/Struktur
Parser, Linter, Schema oder Typprüfung erfolgreich.

### V3 — Verhalten
Relevante automatisierte Tests erfolgreich.

### V4 — Integration
Angrenzende Abläufe und Negativfälle geprüft.

### V5 — Release-Nähe
Smoke-Test, Datenmigration, Backup/Restore und UI-/Accessibility-Prüfung je nach Patchart.

## 14. Codequalitätsregeln
- Eine Funktion macht eine überschaubare Sache.
- Namen beschreiben Zweck statt Implementierungsdetail.
- Kommentare erklären Warum, nicht offensichtliches Was.
- Tote Pfade entfernen, wenn sicher belegt.
- Duplikate nicht vorschnell abstrahieren; echte Gemeinsamkeit zuerst nachweisen.
- Öffentliche Verträge dokumentieren.
- Datenmodelle und Schemas versionierbar halten.

## 15. Performance
Erst messen, dann optimieren.

Priorität:
1. unnötige IO vermeiden
2. große Datenmengen streamen/paginieren
3. teure Berechnungen cachen, wenn Invalidierung klar ist
4. UI nicht blockieren
5. Hintergrundarbeit abbrechbar machen, sofern technisch relevant

## 16. Sicherheitsprinzipien
- Least Privilege
- Eingaben validieren
- Pfade begrenzen
- Ausgaben kontextgerecht escapen
- keine Secrets im Repository
- Abhängigkeiten bewusst und sparsam wählen
- Fremddaten niemals blind vertrauen

## 17. Definition eines hochwertigen Patches
Ein hochwertiger Patch ist:
- klein,
- begründet,
- lokalisiert,
- testbar,
- rückverfolgbar,
- kompatibel mit bestehenden Verträgen,
- für einen fremden Entwickler verständlich,
- für den Nutzer ohne unnötige Komplexität.
