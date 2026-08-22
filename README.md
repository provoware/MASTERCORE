# MASTERCORE

Globales Engineering-Fundament für wartbare, robuste, modulare, datenintegritätssichere und laienfreundliche Werkzeuge.

## Aktueller Stand

Standards-Version: **2.0.0**

MASTERCORE ist kein einzelnes Tool, sondern ein wiederverwendbares Architektur-, Qualitäts-, Daten-, UI- und Release-Fundament für zukünftige Multi-Modul-, Datenbank-, Medien-, Automations-, Desktop- und Web-Werkzeuge.

## Kernprinzip

**DISCOVER → CLASSIFY → DESIGN → PATCH → VERIFY → PROVE → RECORD**

1. Ist-Zustand und exakte Patchposition ermitteln.
2. Nutzen, Risiko, Datenwirkung, Reichweite und Rückbaubarkeit klassifizieren.
3. kleinsten vollständigen Patch planen.
4. lokal und codesparsam ändern.
5. risikobasiert prüfen.
6. Erfolg nur mit realem Nachweis ausweisen.
7. nur betroffene Dokumentation/TODOs synchronisieren.

## Verbindliche Dokumente

- `AGENTS.md` — zentrale Experten-Orchestrierung.
- `docs/EXPERT_ENGINEERING_SYSTEM.md` — vollständige Entscheidungs- und Engineeringlogik.
- `docs/GLOBAL_STANDARDS.md` — globale technische Referenz.
- `docs/PATCH_AND_VALIDATION_PROTOCOL.md` — exakte Vor-Ort-Patches und Nachvalidierung.
- `docs/DATA_STORAGE_CONTRACT.md` — Basistool-/Nutzerdatentrennung, Pfad- und Safe-IO-Vertrag.
- `docs/UI_UX_ACCESSIBILITY_STANDARD.md` — Designsystem, responsive UI und Barrierefreiheit.
- `docs/QUALITY_GATES.md` — risikobasierte Qualitätsgates.
- `docs/RELEASE_GOVERNANCE.md` — Versionierung, Releases und Rollback.
- `quality-contract.json` — maschinenlesbare Kurzform zentraler Regeln.
- `INPUT_FUER_TODO.md` — ausschließlich offene, nicht duplizierte nächste Schritte.

## Architekturziel

```text
src/
├── domain/          # Fachlogik, Invarianten, Modelle
├── application/     # Use Cases, Workflows, Ports
├── infrastructure/  # Dateisystem, DB, Netzwerk, OS-Adapter
├── presentation/    # UI, Views, Controller/ViewModels
└── composition/     # Start, Dependency Wiring, Konfiguration

resources/           # unveränderliche ausgelieferte Ressourcen
config/defaults/     # Standardkonfiguration
tests/               # automatisierte Prüfungen
tools/               # Entwickler-/Validierungswerkzeuge
```

Nutzerdaten liegen getrennt außerhalb dieser Basistooldaten.

## Datenklassen

MASTERCORE unterscheidet verbindlich:
- `immutable_app_data`
- `user_config`
- `user_content`
- `derived_data`
- `operational_data`
- `recovery_data`

## Safe-IO-Grundsatz

```text
resolve
→ normalize
→ authorize
→ inspect
→ stage
→ operate
→ validate
→ commit
→ verify
→ report
```

Erfolg wird erst nach Endvalidierung gemeldet.

## Qualitätsstatus

- `PASS` — ausgeführt und bestanden
- `WARN` — funktionsfähig mit dokumentierter Restunsicherheit
- `FAIL` — nicht freigabefähig
- `NOT_RUN` — nicht geprüft

`NOT_RUN` ist niemals PASS.

## UI-Grundsatz

Oberflächen verwenden zentrale Design-Tokens, wiederverwendbare Komponenten und definierte Zustände. Kleine und große Fenster müssen nutzbar bleiben; wichtige Aktionen dürfen nicht verschwinden oder abgeschnitten werden. Mindestziel für Barrierefreiheit ist WCAG 2.2 AA, soweit anwendbar.

## Entwicklungspriorität

1. Datenintegrität
2. Recovery/Fehlerprävention
3. Wartbarkeit
4. Entkopplung/Wiederverwendung
5. Nutzbarkeit/Barrierefreiheit
6. Performance
7. visuelle Verfeinerung
