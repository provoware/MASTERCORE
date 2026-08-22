# MASTERCORE — Patch & Validation Protocol

Version: 2.0.0
Status: verbindlich

## 1. Ziel
Jeder Eingriff muss reproduzierbar, lokal begründet und nachweisbar sein. Patchpositionen werden ermittelt, nicht geraten.

## 2. Vorermittlung
Vor jeder Änderung:
1. betroffene Datei(en) identifizieren
2. Zielsymbol, Funktion, Klasse, Selektor, Schlüssel oder eindeutige Kontextzeilen lokalisieren
3. Aufrufer/Abhängigkeiten prüfen
4. vorhandene Tests und Hilfsfunktionen suchen
5. aktuellen Zustand dokumentieren
6. nicht zu verändernde Nachbarbereiche festlegen

## 3. Patch-Plan
Vor Ausführung kurz festhalten:
- Ziel
- Datei/Pfad
- exakte Position
- Patchgrund
- erwartete Wirkung
- Risiko
- Datenwirkung
- Rückbaubarkeit
- Validierungsplan

## 4. Patch-Regeln
- kleinstmöglicher vollständiger Patch
- keine Shotgun Changes
- keine Formatierungswelle ohne Grund
- keine Umbenennungen nebenbei
- keine neue Abhängigkeit ohne belegbaren Mehrwert
- keine komplette Dateiersetzung, wenn lokaler Patch genügt
- keine Änderung unbeteiligter Bereiche zur "Verschönerung"

## 5. Nachvalidierung
Je nach Änderung:
- Parser/Syntax
- Lint/Format
- Typprüfung
- Schema
- Unit
- Integration
- Negativpfad
- Recovery
- UI/Responsive
- Accessibility
- Start/Smoke
- Regression angrenzender Funktionen

## 6. Nachweisstatus
Nur diese Zustände verwenden:
- `PASS` — ausgeführt und bestanden
- `WARN` — funktionsfähig mit dokumentierter Restunsicherheit
- `FAIL` — nicht freigabefähig
- `NOT_RUN` — nicht ausgeführt

`NOT_RUN` darf niemals als PASS formuliert werden.

## 7. Patch-Abbruch
Nicht weiterpatchen, wenn während der Arbeit herauskommt, dass:
- der Ist-Zustand anders als angenommen ist
- Datenverlust möglich ist
- ein notwendiger Vertrag fehlt
- ein Test einen unerwarteten angrenzenden Fehler zeigt
- der Scope wesentlich größer wird

Dann neu klassifizieren und neuen kleinsten sicheren Patch bestimmen.

## 8. Abschlussbericht
Immer ausgeben:
1. Stand
2. exakte Änderungen
3. Validierung
4. Risiken/Grenzen
5. nächster logisch bester Schritt
6. zwei sinnvolle Alternativen
7. klare Empfehlung mit Auswirkungsstufe
