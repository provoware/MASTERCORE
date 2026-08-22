# MASTERCORE

Globales Engineering-Fundament für wartbare, robuste, modulare, datenintegritätssichere und laienfreundliche Werkzeuge.

## Aktueller Stand

Standards-Version: **2.0.0**  
Executable Foundation: **2.1.1**  
Quality Automation: **2.2.2**

MASTERCORE ist kein einzelnes Tool, sondern ein wiederverwendbares Architektur-, Qualitäts-, Daten-, UI- und Release-Fundament für Multi-Modul-, Datenbank-, Medien-, Automations-, Desktop- und Web-Werkzeuge.

## Kernprinzip

**DISCOVER → CLASSIFY → DESIGN → PATCH → VERIFY → PROVE → RECORD**

1. Ist-Zustand und exakte Patchposition ermitteln.
2. Nutzen, Risiko, Datenwirkung, Reichweite und Rückbaubarkeit klassifizieren.
3. Kleinsten vollständigen Patch planen.
4. Lokal und codesparsam ändern.
5. Risikobasiert prüfen.
6. Erfolg nur mit realem Nachweis ausweisen.
7. Nur betroffene Dokumentation/TODOs synchronisieren.

## Klick & Start

Die Desktopoberfläche prüft einen gewählten Python-Projektordner, erstellt bei Bedarf eine isolierte `.venv`, installiert dessen `requirements.txt`, prüft erneut und startet einen vorhandenen Einstiegspunkt (`run.py`, `main.py` oder `app.py`). Status, verständliche Erklärung, Lösung und technische Details bleiben im selben Fenster.

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e .
.venv/bin/mastercore-start
```

Tastatur: `Tab` wechselt zwischen den primären Bedienelementen, `Strg+O` öffnet die Ordnerwahl und `Strg+Eingabe` startet die Prüfung.

## Ausführbarer Qualitätskern

Vorhanden sind unter anderem:

- `src/mastercore/domain/errors.py` — typisierte Fehlerhierarchie.
- `src/mastercore/domain/data_classes.py` — verbindliche Datenklassen.
- `src/mastercore/infrastructure/user_roots.py` — getrennte Nutzerpfade.
- `src/mastercore/infrastructure/paths.py` — Pfad-, Rechte-, Größen- und Freispeicherprüfung.
- `src/mastercore/infrastructure/storage.py` — Stage → Verify → Rollback → Atomic Replace → Verify.
- `src/mastercore/infrastructure/logging.py` — begrenztes rotierendes Logging.
- `tools/quality_engine.py` — G0–G8 Quality Gate Engine.
- `tests/` — Unit-, Negativ-, Recovery-, Failure-Injection- und UI-Acceptance-Tests.

## Quality Gate Engine 2.2.2

Das normale CI-Profil verlangt jetzt:

- **G0 Scope / Contract** — Pflichtstruktur, Qualitätsvertrag und Versionskonsistenz.
- **G1 Static** — `compileall`, Ruff und striktes mypy.
- **G2 Functional** — funktionale Start-/Use-Case-Tests.
- **G3 Negative** — Pfad-, Rechte- und Failure-Injection-Fälle.
- **G4 Data Integrity** — Storage-/Contract-Integrität.
- **G5 Recovery** — Rollback- und Recovery-Szenarien.
- **G6 UI / Accessibility** — echte Headless-Tk-Acceptance-Harness unter Xvfb.
- **G7 Regression** — vollständige Testsuite inklusive UI.

**G8 Release** bleibt explizit `NOT_RUN`, bis eine echte Release-/Packaging-Harness existiert.

### G6 prüft aktuell

- Initialfokus.
- Tastaturkürzel.
- explizite Tastaturfokussierbarkeit primärer Controls.
- Small Viewport `640×440`.
- Large Viewport `1440×900`.
- große Standardschrift.
- Sichtbarkeit der Hauptaktionen.
- Fehlerzustand und Rückkehr aus Busy-State.
- verständliche Lösung und technische Details.
- textuelle `INFO/PASS/WARN/FAIL`-Kennzeichnung, sodass Status nicht nur über Farbe vermittelt wird.

G6 ist eine automatisierte Baseline und ersetzt keine vollständige manuelle Screenreader-, Kontrast- oder plattformspezifische WCAG-Abnahme.

## Reproduzierbare Quality-Toolchain

In `pyproject.toml` gepinnt:

- Ruff `0.12.9`
- mypy `1.17.1`
- `mypy strict = true`
- Python `>=3.12`

CI installiert zusätzlich Xvfb/Xauth/Tk für die Headless-GUI-Abnahme.

## Lokale Qualitätsprüfung unter Linux/Kubuntu

```bash
sudo apt install xvfb xauth tk
python3 -m venv .venv
.venv/bin/python -m pip install -e ".[quality]"
.venv/bin/python tools/validate_mastercore.py --profile ci --json quality-evidence.json
```

Erwarteter Pflichtstatus:

```text
G0 PASS
G1 PASS
G2 PASS
G3 PASS
G4 PASS
G5 PASS
G6 PASS
G7 PASS
G8 NOT_RUN
OVERALL PASS
```

Für einen schnellen lokalen Static-/Contract-Check genügt:

```bash
.venv/bin/python tools/validate_mastercore.py --profile local --json quality-evidence.json
```

## Maschinenlesbare Evidence

Jeder Lauf erzeugt `quality-evidence.json` mit Engine-Version, Profil, Gesamtstatus, Required-Check-Name, Pflichtgates, Befehlen, Returncodes, Laufzeiten und begrenzter stdout/stderr-Evidence. GitHub Actions lädt die Datei auch bei fehlgeschlagenen Pflichtgates als Artefakt hoch.

## Branch Protection

Der stabile gewünschte Required Status Check heißt:

```text
MASTERCORE Quality
```

Dieser Name ist sowohl im GitHub-Actions-Job als auch in `quality-contract.json` festgelegt und wird von G0 auf Konsistenz geprüft.

Die **serverseitige Branch Protection ist noch nicht aktiviert**, weil die verbundene GitHub-Schnittstelle keine schreibbare Branch-Protection-/Ruleset-Aktion bereitstellt. Sie darf daher nicht als PASS bezeichnet werden. Das Zielbild und die Aktivierungsschritte stehen in `docs/BRANCH_PROTECTION.md`.

## Verbindliche Dokumente

- `AGENTS.md` — Experten-Orchestrierung.
- `docs/EXPERT_ENGINEERING_SYSTEM.md` — Entscheidungs- und Engineeringlogik.
- `docs/GLOBAL_STANDARDS.md` — globale technische Referenz.
- `docs/PATCH_AND_VALIDATION_PROTOCOL.md` — Vor-Ort-Patches und Nachvalidierung.
- `docs/DATA_STORAGE_CONTRACT.md` — Daten-/Pfad-/Safe-IO-Vertrag.
- `docs/UI_UX_ACCESSIBILITY_STANDARD.md` — UI, responsive Verhalten und Barrierefreiheit.
- `docs/QUALITY_GATES.md` — G0–G8 und ausführbare Zuordnung.
- `docs/BRANCH_PROTECTION.md` — serverseitiges `main`-Schutz-Zielbild.
- `docs/RELEASE_GOVERNANCE.md` — Versionierung und Release/Recovery.
- `quality-contract.json` — maschinenlesbarer Kernvertrag.
- `INPUT_FUER_TODO.md` — offene nächste Schritte.

## Architektur

```text
src/mastercore/
├── domain/
├── application/
├── infrastructure/
├── presentation/
└── composition/

resources/
config/defaults/
tests/
tools/
```

Nutzerdaten bleiben von Basistooldaten getrennt.

## Qualitätsstatus

- `PASS` — ausgeführt und bestanden.
- `WARN` — ausgeführt, aber dokumentierte Restunsicherheit.
- `FAIL` — nicht freigabefähig.
- `NOT_RUN` — nicht geprüft.

`NOT_RUN` ist niemals PASS.

## Entwicklungspriorität

1. Datenintegrität
2. Recovery / Fehlerprävention
3. Wartbarkeit
4. Entkopplung / Wiederverwendung
5. Nutzbarkeit / Barrierefreiheit
6. Performance
7. visuelle Verfeinerung
