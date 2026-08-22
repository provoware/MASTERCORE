# MASTERCORE

Globale Architektur- und Qualitätsbasis für ein wartbares, robustes, modulares und laienfreundliches Multi-Modul-/Datenbanktool.

## Aktueller Stand

Standards-Version: **0.1.0**

MASTERCORE definiert verbindliche Regeln für:
- saubere Trennung von Programm-, Ressourcen- und Nutzerdaten,
- modulare und entkoppelte Architektur,
- exakte Vor-Ort-Patches nach Positionsanalyse,
- Vor- und Nachvalidierung von Dateien, Pfaden und Änderungen,
- robustes Fehlerhandling, Recovery und Logging,
- wiederverwendbare UI-Komponenten und Design-Tokens,
- responsive Oberflächen für kleine und große Geräte,
- Barrierefreiheit als Standard,
- informatives, konfigurierbares Dashboard,
- nachvollziehbare Tests, Versionierung und Iterationen.

## Verbindliche Dokumente

- `AGENTS.md` — zentrale Experten-Anweisung für Entwicklungsagenten.
- `docs/GLOBAL_STANDARDS.md` — technische und gestalterische Referenz.
- `INPUT_FUER_TODO.md` — ausschließlich weiterführende, noch nicht umgesetzte Verbesserungen.

## Grundprinzip

**Erst ermitteln → vorvalidieren → kleinsten sinnvollen Patch ausführen → nachvalidieren → dokumentieren.**

Keine Änderung ohne konkreten Grund. Keine geratenen Patchpositionen. Keine unnötige Abstraktion. Keine Vermischung von Basistooldaten und Nutzerdaten.

## Empfohlene Zielstruktur

```text
MASTERCORE/
├── AGENTS.md
├── README.md
├── INPUT_FUER_TODO.md
├── docs/
│   └── GLOBAL_STANDARDS.md
├── src/                 # Programmcode
├── resources/           # unveränderliche ausgelieferte Ressourcen
├── config/defaults/     # Standardkonfiguration
├── tests/               # automatisierte Prüfungen
└── tools/               # Entwickler-/Validierungswerkzeuge
```

Die tatsächlichen Nutzerdaten gehören zur Laufzeit in einen getrennten, klar definierten Nutzerbereich und nicht in `src/`, `resources/` oder `config/defaults/`.
