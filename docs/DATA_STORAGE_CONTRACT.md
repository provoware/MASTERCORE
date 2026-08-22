# MASTERCORE — Data & Storage Contract

Version: 2.0.0
Status: verbindlich

## 1. Oberstes Ziel
Programmdateien und Nutzerdaten müssen logisch und physisch getrennt bleiben. Updates dürfen Nutzerdaten niemals still überschreiben.

## 2. Datenklassen
- `immutable_app_data`: ausgelieferte Ressourcen, Defaults, Schemas
- `user_config`: Einstellungen und UI-Präferenzen
- `user_content`: Projekte, Datenbanken, importierte Inhalte
- `derived_data`: Cache, Indizes, Thumbnails, temporäre Ableitungen
- `operational_data`: Logs, Sessions, Journale
- `recovery_data`: Backups, Snapshots, Recovery-Zustände

Jede neue persistente Datenart muss einer Klasse zugeordnet werden.

## 3. Root-Vertrag
Jede Datenklasse besitzt einen kanonischen Root. Direkte Pfadkonstruktion außerhalb der zentralen Path-/Storage-API ist zu vermeiden.

Programm-/Ressourcenroots sind zur Laufzeit grundsätzlich unveränderlich. Schreibbare Daten gehören in einen dafür vorgesehenen Nutzerroot.

## 4. Path Security
Vor Zugriff:
- normalisieren/kanonisieren
- erlaubten Root prüfen
- Traversal verhindern
- Symlinks entsprechend Operation behandeln
- Existenz und Typ prüfen
- Rechte prüfen
- Erweiterung/Format/Schema prüfen, wenn relevant
- Größe und Speicherplatz prüfen, wenn relevant

## 5. Safe Write
Für kritische Daten bevorzugt:
1. Ziel autorisieren
2. Backupbedarf bestimmen
3. temporäre Datei im selben Dateisystem anlegen
4. vollständig schreiben
5. flush
6. optional fsync
7. temporären Inhalt validieren
8. atomar ersetzen
9. Endzustand nachvalidieren
10. Erfolg melden

## 6. Backup/Recovery
Backups müssen unterscheiden zwischen:
- automatisch vor riskanter Migration
- manuell angefordert
- periodisch/Autosave
- Crash-/Recovery-Zustand

Backups benötigen nachvollziehbare Zuordnung zum Original und dürfen nicht unkontrolliert anwachsen.

## 7. Datenbank
- explizite Schema-Version
- geordnete Migrationen
- Integritätscheck nach Migration
- Backup vor riskanten Migrationen
- fehlgeschlagene Migration darf keinen halbfertigen Zustand als erfolgreich markieren
- Transaktionen verwenden, wo fachlich möglich

## 8. Löschen
Löschen ist standardmäßig konservativ:
- prüfe Scope und Root erneut
- Nutzer möglichst über Wirkung informieren
- Papierkorb/Soft Delete bevorzugen, wenn sinnvoll
- irreversible Löschung explizit kennzeichnen

## 9. Cache
Cache darf rekonstruierbar sein. Cache-Fehler dürfen niemals die einzige Kopie von Nutzerdaten betreffen.

## 10. Export
Exporte gelten als neue Dateien und durchlaufen dieselbe Zielpfad-/Existenz-/Schreib-/Nachvalidierung wie andere Schreibvorgänge.
