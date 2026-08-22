# MASTERCORE

Globales Engineering-Fundament für wartbare, robuste, modulare, datenintegritätssichere und laienfreundliche Werkzeuge.

## Aktueller Stand

Standards-Version: **2.0.0**  
Executable Foundation: **2.1.1**  
Quality Automation: **2.2.0**

MASTERCORE ist kein einzelnes Tool, sondern ein wiederverwendbares Architektur-, Qualitäts-, Daten-, UI- und Release-Fundament für zukünftige Multi-Modul-, Datenbank-, Medien-, Automations-, Desktop- und Web-Werkzeuge.

## Klick & Start

Die Desktopoberfläche prüft einen gewählten Python-Projektordner, erstellt darin bei Bedarf eine isolierte `.venv`, installiert dessen `requirements.txt`, prüft danach erneut und startet einen vorhandenen Einstiegspunkt (`run.py`, `main.py` oder `app.py`). Alle Schritte erscheinen mit Textstatus, Farbe, einfacher Erklärung, Lösung und optionalen technischen Details im selben Fenster. Das Protokoll kann zusätzlich als JSON gespeichert werden.

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e .
.venv/bin/mastercore-start
```

Tastatur: `Tab` wechselt zwischen Bedienelementen, `Strg+O` öffnet die Ordnerwahl und `Strg+Eingabe` startet die Prüfung. MASTERCORE erweitert keine Systemrechte und führt kein pauschales `chmod` aus. Fehlende Rechte werden verständlich gemeldet, statt die Sicherheit des Projektordners unbemerkt zu verändern.

## Kernprinzip

**DISCOVER → CLASSIFY → DESIGN → PATCH → VERIFY → PROVE → RECORD**

1. Ist-Zustand und exakte Patchposition ermitteln.
2. Nutzen, Risiko, Datenwirkung, Reichweite und Rückbaubarkeit klassifizieren.
3. Kleinsten vollständigen Patch planen.
4. Lokal und codesparsam ändern.
5. Risikobasiert prüfen.
6. Erfolg nur mit realem Nachweis ausweisen.
7. Nur betroffene Dokumentation/TODOs synchronisieren.

## Ausführbarer Qualitätskern 2.1.1

Vorhanden:

- `src/mastercore/domain/errors.py` — zentrale typisierte Fehlerhierarchie inklusive Schema- und Storage-Limit-Fehlern.
- `src/mastercore/domain/data_classes.py` — verbindliche Datenklassen.
- `src/mastercore/infrastructure/user_roots.py` — getrennte, plattformabhängige Nutzerpfade für Konfiguration, Inhalte, Cache, Logs, Backups und Exporte.
- `src/mastercore/infrastructure/paths.py` — Root-, Traversal-, Symlink-, Größen-, Suffix-, Rechte- und Freispeicherprüfung.
- `src/mastercore/infrastructure/storage.py` — Stage → Hashprüfung → Rollback-Snapshot → atomarer Replace → Endprüfung.
- `src/mastercore/infrastructure/logging.py` — begrenztes rotierendes Datei-Logging.
- `tests/` — Unit-, Negativ-, Recovery- und Failure-Injection-Tests.

### Storage Hardening

Schreibende Dateioperationen können unter anderem:

- maximale Payload-Größe begrenzen,
- erlaubte Dateiendungen einschränken,
- freien Speicher vorab prüfen,
- fehlende Schreibrechte früh erkennen,
- JSON-Daten vor dem Schreiben validieren,
- bestehende Dateien vor dem Replace intern als Rollback-Snapshot sichern,
- optionale SHA-256-verifizierte dauerhafte Backups erzeugen,
- konkurrierende Änderungen am Ziel vor dem Replace erkennen,
- auf POSIX den Zielordner per Directory-FD binden und `O_NOFOLLOW`/dir-fd-Operationen nutzen,
- bei Fehlern nach dem Replace den vorherigen Zustand wiederherstellen.

Die Failure-Injection-Tests provozieren unter anderem Schreibabbrüche, beschädigte Stage-/Finaldaten, fehlende Rechte, konkurrierende Zieländerungen, neu auftauchende Zieldateien und einen Parent-Verzeichnis-Swap.

## Quality Gate Engine 2.2.0

`tools/quality_engine.py` setzt die Qualitätsverträge als ausführbare G0–G8-Engine um. `tools/validate_mastercore.py` ist der kleine CLI-Einstieg.

### Automatisierte Pflichtgates im normalen CI-Profil

- **G0 Scope / Contract** — Pflichtstruktur und Qualitätsvertrag.
- **G1 Static** — `compileall`, Ruff und striktes mypy.
- **G2 Functional** — funktionale Start-/Use-Case-Tests.
- **G3 Negative** — Pfad-, Rechte- und Failure-Injection-Negativfälle.
- **G4 Data Integrity** — Storage-/Contract-Integrität.
- **G5 Recovery** — Rollback- und Recovery-Szenarien.
- **G7 Regression** — vollständige Test-Suite.

**G6 UI/Accessibility** und **G8 Release** bleiben bewusst `NOT_RUN`, solange dafür keine echte automatisierte Acceptance- beziehungsweise Release-Harness existiert. Sie werden nicht als PASS ausgegeben.

### Statische Qualität

Die Quality-Toolchain ist reproduzierbar in `pyproject.toml` gepinnt:

- Ruff `0.12.9`
- mypy `1.17.1`
- mypy `strict = true`

Ruff prüft Produktcode, Tooling und Tests. Striktes mypy prüft `src/mastercore`.

### Maschinenlesbare Evidence

Jeder Gate-Lauf erzeugt `quality-evidence.json` mit:

- Engine-/Schema-Version,
- Gesamtstatus,
- Pflichtgates,
- jedem Gate und dessen Status,
- ausgeführten Befehlen,
- Returncodes,
- Laufzeiten,
- begrenzter stdout/stderr-Evidence.

GitHub Actions lädt diese Datei auch bei einem fehlgeschlagenen Gate als Artefakt hoch. Ein erforderliches `NOT_RUN` oder `FAIL` blockiert den Workflow.

### Lokale Qualitätsprüfung unter Linux/Kubuntu

Im Repository-Ordner:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e ".[quality]"
.venv/bin/python tools/validate_mastercore.py --profile ci --json quality-evidence.json
```

Für einen schnellen lokalen Static-/Contract-Check:

```bash
.venv/bin/python tools/validate_mastercore.py --profile local --json quality-evidence.json
```

Erfolgskriterium für das CI-Profil:

```text
* G0 PASS
* G1 PASS
* G2 PASS
* G3 PASS
* G4 PASS
* G5 PASS
- G6 NOT_RUN
* G7 PASS
- G8 NOT_RUN
OVERALL PASS
```

## Verbindliche Dokumente

- `AGENTS.md` — zentrale Experten-Orchestrierung.
- `docs/EXPERT_ENGINEERING_SYSTEM.md` — vollständige Entscheidungs- und Engineeringlogik.
- `docs/GLOBAL_STANDARDS.md` — globale technische Referenz.
- `docs/PATCH_AND_VALIDATION_PROTOCOL.md` — exakte Vor-Ort-Patches und Nachvalidierung.
- `docs/DATA_STORAGE_CONTRACT.md` — Basistool-/Nutzerdatentrennung, Pfad- und Safe-IO-Vertrag.
- `docs/UI_UX_ACCESSIBILITY_STANDARD.md` — Designsystem, responsive UI und Barrierefreiheit.
- `docs/QUALITY_GATES.md` — risikobasierte Qualitätsgates und deren ausführbare Zuordnung.
- `docs/RELEASE_GOVERNANCE.md` — Versionierung, Releases und Rollback.
- `quality-contract.json` — maschinenlesbare Kurzform zentraler Regeln.
- `INPUT_FUER_TODO.md` — ausschließlich offene, nicht duplizierte nächste Schritte.

## Architektur

```text
src/mastercore/
├── domain/          # Fachlogik, Invarianten, Fehler- und Datenverträge
├── application/     # Use Cases, Workflows, Ports
├── infrastructure/  # Dateisystem, DB, Netzwerk, OS-Adapter
├── presentation/    # UI, Views, Controller/ViewModels
└── composition/     # Start, Dependency Wiring, Konfiguration

resources/           # unveränderliche ausgelieferte Ressourcen
config/defaults/     # unveränderliche Standardkonfiguration
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
