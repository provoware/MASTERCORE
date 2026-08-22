# MASTERCORE

Globaler Engineering-Standard für wartbare, robuste, modulare und laienfreundliche Werkzeuge.

## Aktueller Stand

Standards-Version: **1.0.0**

MASTERCORE definiert verbindliche Arbeits-, Architektur-, Daten-, UI-, Qualitäts- und Releaseverträge für zukünftige Module und Tools.

## Kernprinzip

**Inspect → Decide → Patch → Prove**

1. Ist-Zustand und exakte Patchposition ermitteln.
2. Risiko, Datenwirkung, Rückbaubarkeit und Testtiefe klassifizieren.
3. Kleinsten vollständigen Patch durchführen.
4. Ergebnis mit real ausgeführten Prüfungen nachweisen.

## Verbindliche Dokumente

- `AGENTS.md` — zentrale Experten-Anweisung und Entwicklungsvertrag.
- `docs/GLOBAL_STANDARDS.md` — technische Referenz und wiederverwendbare Systemstandards.
- `INPUT_FUER_TODO.md` — nur offene, nicht duplizierte Weiterentwicklungen.

## Architekturziel

```text
MASTERCORE/
├── AGENTS.md
├── README.md
├── INPUT_FUER_TODO.md
├── docs/
│   └── GLOBAL_STANDARDS.md
├── src/
│   ├── domain/
│   ├── application/
│   ├── infrastructure/
│   ├── presentation/
│   └── composition/
├── resources/
├── config/
│   └── defaults/
├── tests/
└── tools/
```

Nutzerdaten liegen ausdrücklich außerhalb der Basistooldaten. Projekte, Einstellungen, Datenbanken, Layoutzustände, Exporte, Backups, Cache und Logs werden über eine zentrale Path-/Storage-API verwaltet.

## Qualitätspriorität

1. Datenintegrität
2. Recovery und Fehlerfreiheit
3. Wartbarkeit und Architektur
4. Entkopplung und Wiederverwendbarkeit
5. Nutzbarkeit und Barrierefreiheit
6. Diagnosefähigkeit
7. Performance
8. visuelle Verfeinerung

## Zentrale Standards

- sichere Pfad- und Dateioperationen mit Vor-/Nachvalidierung
- atomare kritische Schreibvorgänge
- deklarierte Undo-/Recovery-Policy
- strukturierte Fehlerklassen und Logging
- zentrale Design-Tokens und wiederverwendbare UI-Komponenten
- Responsive Design für kleine und große Geräte
- WCAG-2.2-AA als Accessibility-Mindestziel, soweit anwendbar
- Dashboard als Arbeitszentrale statt dekorative Oberfläche
- Tests inklusive Negativ- und Recoverypfaden
- PASS nur bei tatsächlich ausgeführten Prüfungen
- laienverständliche Schritt-für-Schritt-Anweisungen mit exakten Befehlen und Erfolgskriterien

## Entwicklungsregel

Keine Änderung ohne belegbaren Nutzen. Keine geratenen Patchpositionen. Keine unnötigen Komplettumbauten. Keine Vermischung von Basistool- und Nutzerdaten. Keine neue Abstraktion ohne klaren fachlichen Grund.
