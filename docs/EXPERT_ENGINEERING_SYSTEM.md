# MASTERCORE — Expert Engineering System

Version: 2.0.0
Status: verbindlich

## Zweck
Dieses Dokument beschreibt die Expertenlogik hinter MASTERCORE. Es ergänzt `AGENTS.md` und zerlegt komplexe Entwicklungsarbeit in prüfbare Verträge statt in lose Empfehlungen.

## 1. Arbeitsmodell
Jede Änderung folgt zwingend diesem Zyklus:

`DISCOVER → CLASSIFY → DESIGN → PATCH → VERIFY → PROVE → RECORD`

### DISCOVER
- betroffene Datei, Symbol, Datenfluss, UI-Bereich oder Konfiguration exakt finden
- Ist-Zustand lesen, nicht vermuten
- Aufrufer, Abhängigkeiten und Schreib-/Lesegrenzen ermitteln
- bestehende Hilfsfunktionen und Verträge suchen

### CLASSIFY
Bewerte vor dem Patch:
- Nutzen: niedrig / mittel / hoch / kritisch
- technisches Risiko: niedrig / mittel / hoch / kritisch
- Datenrisiko: keines / lesend / verändernd / destruktiv
- Rückbaubarkeit: reversibel / kompensierbar / abbrechbar / Backup nötig / irreversibel
- Reichweite: lokal / Modul / mehrere Module / global
- Testtiefe: Smoke / Unit / Integration / Recovery / UI / Release

### DESIGN
Vor jeder Änderung muss klar sein:
- kleinster vollständiger Patch
- erwartete Wirkung
- akzeptierte Seiteneffekte
- explizit nicht zu verändernde Bereiche
- Recovery-/Rollback-Pfad
- notwendige Nachweise

### PATCH
- lokal und zielgerichtet
- bestehende Konventionen respektieren
- keine Nebenrefactorings ohne unmittelbaren Nutzen
- keine Vollersetzung großer Dateien, wenn lokaler Patch möglich ist
- keine neue Abstraktion ohne klaren Vertrag oder echte Wiederverwendung

### VERIFY
Relevante Prüfungen tatsächlich ausführen. Nicht ausgeführte Prüfungen heißen `NOT_RUN`.

### PROVE
Erfolg nur mit Nachweis melden:
- welches Verhalten geprüft wurde
- wie geprüft wurde
- Ergebnis PASS/WARN/FAIL/NOT_RUN
- verbleibende Grenzen

### RECORD
Nur betroffene Dokumente aktualisieren. TODOs dürfen keine erledigten Punkte als offen führen und keine Duplikate enthalten.

## 2. Änderungsbudget
Jeder Patch bekommt ein mentales Änderungsbudget:
- so wenig Dateien wie möglich
- so wenig neue öffentliche Schnittstellen wie möglich
- so wenig neue Zustände wie möglich
- so wenig neue Abhängigkeiten wie möglich
- so wenig persistierte Felder wie möglich

Wenn ein Patch dieses Budget überschreitet, muss der Mehrumfang fachlich begründet sein.

## 3. Architektur-Invarianten
Diese Regeln dürfen nicht schleichend verletzt werden:
- Domain kennt keine konkrete UI, Datenbank, Dateisystem- oder Netzwerkimplementierung.
- Application orchestriert Anwendungsfälle, besitzt aber keine plattformspezifische Persistenzlogik.
- Infrastructure implementiert Ports/Adapter und kapselt Seiteneffekte.
- Presentation darf Fachregeln nicht duplizieren.
- Composition verbindet Abhängigkeiten und ist der einzige Ort für Wiring, soweit praktikabel.
- Nutzerdaten sind physisch und logisch von ausgelieferten Basistooldaten getrennt.
- Alle Schreiboperationen laufen durch zentrale, validierende Storage-/IO-Grenzen.
- UI-Maße und Farben kommen aus Tokens, nicht aus verstreuten Einzelwerten.

## 4. Datenklassifikation
Jeder persistente Datentyp gehört genau einer Klasse an:
1. `immutable_app_data` — ausgelieferte Ressourcen und Defaults
2. `user_config` — Einstellungen und UI-Präferenzen
3. `user_content` — Projekte, Datenbanken, importierte Inhalte
4. `derived_data` — Cache, Indizes, Thumbnails, temporäre Ableitungen
5. `operational_data` — Logs, Diagnose, Sessions, Journale
6. `recovery_data` — Backups, Snapshots, Recovery-Journale

Für jede Klasse sind Root, Lebensdauer, Löschbarkeit, Backupbedarf und Migrationsstrategie festzulegen.

## 5. Safe-IO-Protokoll
Jede Dateioperation folgt:

`resolve → normalize → authorize → inspect → stage → operate → validate → commit → verify → report`

Schreiboperationen sollen, wo technisch möglich:
- im selben Dateisystem temporär schreiben
- nach dem Schreiben flushen
- kritische Daten optional fsyncen
- temporären Inhalt validieren
- atomar ersetzen
- endgültigen Zustand nachvalidieren
- bei Fehlschlag Original oder Recovery-Kopie erhalten

Verboten:
- ungeprüfte Nutzereingabe als direkter Pfad
- Traversal außerhalb erlaubter Roots
- stilles Überschreiben fremder Daten
- Erfolgsmeldung vor Nachvalidierung
- zerstörerische Migration ohne Sicherungs-/Rollback-Strategie

## 6. Fehlerarchitektur
Fehler werden in vier Ebenen getrennt:
- Ursache: technische Exception/Fehlercode
- Domänenfehler: fachlich typisierter Fehler
- Diagnose: Kontext für Entwickler
- Nutzerhinweis: verständliche Handlungsempfehlung

Mindestens berücksichtigen:
- ValidationError
- ConfigurationError
- PermissionError
- StorageError
- DataIntegrityError
- MigrationError
- ExternalServiceError
- TimeoutError
- StateConflictError
- RecoveryError

Fehler dürfen nicht verschluckt werden. Retries benötigen Höchstzahl, Backoff und Abbruchbedingung.

## 7. Logging-/Diagnosevertrag
Strukturierte Logs enthalten nach Möglichkeit:
- Zeitstempel
- Level
- Komponente
- Operation
- Korrelations-ID
- Ergebnis
- Dauer
- Fehlerklasse
- kurze technische Ursache

Logs dürfen keine Geheimnisse, Passwörter, Tokens oder unnötige personenbezogene Inhalte enthalten.

UI-Diagnosebereich:
- standardmäßig kompakt oder einklappbar
- Suche und Filter
- Kopieren
- Diagnoseexport
- Klartext: Was ist passiert? / mögliche Ursache / was kann ich tun? / technische Details

Logrotation und Größenbegrenzung sind Pflicht, sobald dauerhaft auf Platte geloggt wird.

## 8. Datenbank- und Migrationsvertrag
- Schema-Version explizit speichern
- Migrationen geordnet und idempotent gestalten, soweit möglich
- keine automatische Downgrade-Annahme
- vor riskanter Migration Backup/Snapshot
- Migration einzeln protokollieren
- nach Migration Integritätscheck
- Migrationstest von mindestens vorheriger unterstützter Version
- fehlgeschlagene Migration darf keinen halbdefinierten Zustand als Erfolg hinterlassen

## 9. Undo-/Recovery-Vertrag
Jede schreibende Action bekommt eine Policy:
- `reversible`
- `compensatable`
- `cancelable`
- `backup_required`
- `irreversible`

UI darf nur dann "Rückgängig" anbieten, wenn die Action dies wirklich unterstützt.

## 10. UI-System
Globale Tokens definieren mindestens:
- color.*
- spacing.*
- typography.*
- radius.*
- border.*
- elevation.*
- control_size.*
- breakpoint.*
- motion.*
- z_index.*

Komponenten müssen relevante Zustände vollständig besitzen:
`default`, `hover`, `focus`, `active`, `disabled`, `loading`, `success`, `warning`, `error`.

Responsive Prinzipien:
- Inhalt darf weder abgeschnitten noch hinter festen Bereichen verschwinden
- Layout bevorzugt fließen/wrappen statt horizontal zu überlaufen
- kleine Geräte: Priorisierung, Stapelung, einklappbare Nebenbereiche
- große Geräte: bessere Raumnutzung ohne überlange Textzeilen
- verschiebbare/skalierbare Bereiche brauchen Mindest-/Maximalgrößen und Reset

## 11. Dashboard-Governance
Ein Dashboard zeigt Entscheidungs- und Aktionswert, keine Dekoration.

Priorität:
1. kritische Fehler/Warnungen
2. aktueller Projekt-/Systemstatus
3. nächste sinnvolle Aktionen
4. letzte/aktive Projekte
5. Speicher, Backup und Recovery
6. Diagnose
7. Statistiken

Karten dürfen nur Informationen enthalten, für die ein Nutzer einen nächsten Schritt ableiten kann oder die einen relevanten Zustand anzeigen.

## 12. Accessibility-Vertrag
Mindestziel: WCAG 2.2 AA, soweit für die verwendete Plattform anwendbar.

Pflicht:
- vollständige Tastaturbedienung
- sichtbarer Fokus
- semantische Namen
- ausreichender Kontrast
- keine Information nur durch Farbe
- große Touch-/Klickziele
- Zoom/Schriftvergrößerung ohne Funktionsverlust
- Screenreader-taugliche Statusmeldungen
- Reduced Motion respektieren

## 13. Performance-Vertrag
Optimierung nur nach beobachtetem oder plausibel kritischem Engpass.

Bevorzugen:
- Lazy Loading großer Datenmengen
- Pagination/Virtualisierung langer Listen
- Debounce für teure UI-Suchen
- Caches mit klarer Invalidierung
- begrenzte Parallelität
- keine blockierenden Langläufer im UI-Thread

Performance darf Datenintegrität oder Wartbarkeit nicht unterlaufen.

## 14. Sicherheitsvertrag
- Eingaben an Systemgrenzen validieren
- Pfade autorisieren
- minimale Rechte
- keine Shell-Interpolation aus Nutzereingaben
- keine geheimen Daten in Repository/Logs
- externe Inhalte als untrusted behandeln
- sichere Defaults statt opt-in Sicherheit

## 15. Testmatrix nach Risiko
### Niedrig
- Syntax/Lint
- gezielter Unit-/Smoke-Test

### Mittel
- plus angrenzende Unit-/Integrationstests
- Negativpfad

### Hoch
- plus Daten-/Recoverytest
- Regression angrenzender Module
- manuelle oder automatisierte UI-Abnahme, falls relevant

### Kritisch/destruktiv
- reproduzierbarer Backup-/Restore-Test
- Migrations-/Recovery-Szenario
- Freigabe nur ohne ungeklärten FAIL

## 16. Qualitätsgate
Ein Patch darf erst als fertig gelten, wenn:
- Scope klar war
- exakte Position ermittelt wurde
- Risiko klassifiziert wurde
- Patch minimal und vollständig ist
- relevante Tests ausgeführt wurden
- kein ungeklärter Datenverlustpfad existiert
- Dokumentation konsistent ist
- nächster Schritt feststeht

## 17. Kommunikationsstandard für Laien
Jede technische Abschlussmeldung folgt:
1. Was wurde erreicht?
2. Was wurde konkret geändert?
3. Was wurde geprüft?
4. Gibt es offene Risiken?
5. Was ist der logisch beste nächste Schritt?

Befehle müssen kopierbar sein. Platzhalter eindeutig kennzeichnen. Nie voraussetzen, dass der Nutzer Git-, Python-, Shell- oder Framework-Fachbegriffe kennt.

## 18. Entscheidungsheuristik
Wenn mehrere Lösungen funktionieren, bevorzuge in dieser Reihenfolge:
1. geringeres Datenrisiko
2. kleinere Kopplung
3. geringerer Änderungsumfang
4. bessere Testbarkeit
5. bessere Wiederverwendbarkeit
6. weniger Laufzeitabhängigkeiten
7. bessere Bedienbarkeit
8. erst danach kosmetische Eleganz

## 19. Definition of Ready
Vor Implementierung müssen mindestens bekannt sein:
- Ziel
- betroffener Bereich
- Ist-Zustand
- Patchposition
- Datenwirkung
- Risiko
- Validierungsplan

## 20. Definition of Done
Fertig bedeutet:
- gewünschtes Verhalten vorhanden
- relevante alte Funktionen nicht regressiert
- Datenvertrag eingehalten
- Fehler- und Negativpfad bedacht
- Nachvalidierung durchgeführt
- PASS/WARN/FAIL/NOT_RUN ehrlich ausgewiesen
- Dokumentation/TODO synchron, falls betroffen
- nächster sinnvoller Schritt dokumentiert
