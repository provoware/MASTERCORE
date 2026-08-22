# MASTERCORE — UI/UX & Accessibility Standard

Version: 2.0.0
Status: verbindlich

## 1. Ziel
Alle Oberflächen sollen modern, ruhig, konsistent, flexibel, schnell erfassbar und auf kleinen wie großen Geräten nutzbar sein.

## 2. Design Tokens
Zentral definieren:
- Farben
- Abstände
- Typografie
- Radien
- Rahmen
- Schatten/Elevation
- Control-Größen
- Icons
- Breakpoints
- Motion
- Z-Index/Layer

Keine verstreuten Einzelwerte, wenn ein Token existiert.

## 3. Größen- und Abstandslogik
Bevorzugte Basisskala: 4/8-basiert.

Beispiel:
- 4: Mikroabstand
- 8: kompakt
- 12/16: Standard
- 24: Gruppierung
- 32/48: größere Bereichstrennung

Komponenten müssen Mindest- und Maximalgrößen besitzen, wenn freie Größenänderung sonst Inhalte unbrauchbar machen könnte.

## 4. Responsive Verhalten
- Inhalte dürfen nicht abgeschnitten werden
- Text darf nicht unter feste Controls rutschen
- Layouts sollen umbrechen/stapeln statt unkontrolliert horizontal überlaufen
- kleine Fenster: Nebenfunktionen einklappen, Hauptaktion sichtbar halten
- große Fenster: Platz sinnvoll nutzen, aber Lesebreite begrenzen
- wichtige Aktionen dürfen nicht außerhalb des sichtbaren Bereichs verschwinden

## 5. Komponentenvertrag
Gemeinsame Komponenten mindestens für:
- Button
- Input
- Select
- Toggle
- Checkbox
- Dialog
- Toast
- Card
- Toolbar
- Sidebar
- Table/List
- Tabs
- Empty State
- Error State
- Loading State
- Debug Panel

Relevante Zustände:
`default`, `hover`, `focus`, `active`, `disabled`, `loading`, `success`, `warning`, `error`.

## 6. Aktionshierarchie
- Primäraktion: eindeutig dominant
- Sekundäraktion: sichtbar, aber untergeordnet
- Gefahraktion: klar unterscheidbar und nicht versehentlich auslösbar
- irreversible Aktionen: zusätzliche Klarheit/Bestätigung nach Risiko

## 7. Dashboard
Dashboard priorisiert:
1. Fehler/Warnungen
2. aktiver Projekt-/Systemstatus
3. nächste sinnvolle Aktionen
4. zuletzt verwendete Inhalte
5. Speicher/Backup/Recovery
6. Diagnose
7. Statistiken

Schnellaktionen müssen wirklich häufige Vorgänge abkürzen.

## 8. Anpassbarkeit
Wo sinnvoll dürfen Bereiche:
- verschoben
- angedockt
- skaliert
- eingeklappt
- ausgeblendet
werden.

Pflicht: Standardlayout wiederherstellen.

Layoutzustand gehört zu Nutzerdaten.

## 9. Accessibility
Mindestziel: WCAG 2.2 AA soweit anwendbar.

Pflicht:
- vollständige Tastaturbedienung
- sichtbarer Fokus
- semantische Namen/Labels
- ausreichender Kontrast
- keine Information ausschließlich über Farbe
- ausreichend große Touch-/Klickziele
- Zoom/Schriftvergrößerung ohne Funktionsverlust
- Screenreader-taugliche Statusmeldungen
- Reduced Motion berücksichtigen

## 10. Fehler-UX
Fehleranzeige soll vier Ebenen trennen:
- Was ist passiert?
- Was bedeutet das?
- Was kann ich tun?
- Technische Details

Technische Details standardmäßig einklappbar.

## 11. Empty/Loading/Offline
Jeder relevante Datenbereich braucht definierte Zustände für:
- leer
- lädt
- Fehler
- keine Berechtigung
- offline/nicht erreichbar
- keine Treffer

## 12. Abnahmekriterien
UI-Patch erst freigeben, wenn relevante Punkte geprüft wurden:
- kleine Fenstergröße
- große Fenstergröße
- lange Texte
- große Schrift/Zoom
- Tastatur
- Fokus
- Kontrast
- Loading/Error/Empty
- wichtige Aktionen sichtbar
