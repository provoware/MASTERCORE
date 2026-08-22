# MASTERCORE — Release Governance

Version: 2.0.0
Status: verbindlich

## 1. Ziel
Releases müssen nachvollziehbar, reproduzierbar und rückverfolgbar sein. Versionen werden nicht aus kosmetischen Gründen erhöht.

## 2. Versionierung
SemVer:
- MAJOR: inkompatible Vertrags-/Architekturänderung
- MINOR: rückwärtskompatible Funktion/erweiterter Vertrag
- PATCH: rückwärtskompatible Fehlerkorrektur/kleine Verbesserung

## 3. Commit-Regeln
- fachlich zusammengehörige Änderung
- Wirkung in der Commitnachricht
- keine unnötigen Mischcommits
- keine unbeteiligten Formatierungsänderungen

## 4. Release-Voraussetzungen
- relevante Quality Gates bestanden
- kein ungeklärter kritischer FAIL
- Versionen konsistent
- Daten-/Migrationspfade geprüft, falls betroffen
- Dokumentation synchron, falls Aussagen verändert wurden

## 5. Artefaktintegrität
Für distributierbare Artefakte bevorzugt:
- eindeutiger Versionsname
- Build-/Release-Metadaten
- SHA-256
- Manifest der enthaltenen Dateien
- Herkunft/Parent-Version, wenn relevant

## 6. Rollback
Vor Releases mit riskanten Datenmigrationen muss klar sein:
- welche Version zurückrollbar ist
- ob Datenformat rückwärtskompatibel ist
- wie Backup/Restore funktioniert
- welche Schritte nicht automatisch rückgängig gemacht werden können

## 7. Dokumentation
README, CHANGELOG, TODO und Statusdateien nur aktualisieren, wenn ihre Aussagen betroffen sind. Keine mechanischen Versionsänderungen in unbeteiligten Dateien.

## 8. Release-Bericht
- Version
- Scope
- wichtigste Änderungen
- relevante Gates
- bekannte WARNs
- Upgrade-/Migrationhinweis
- Rollback-/Recoveryhinweis, falls relevant
