# MASTERCORE — Global Engineering Standards

Version: 2.0.0
Status: verbindliche technische Referenz

## 1. Zweck
Diese Datei definiert die globalen technischen Invarianten. Detailverträge sind in spezialisierten Dokumenten ausgelagert, damit MASTERCORE selbst modular und wartbar bleibt.

## 2. Normative Dokumente
- `AGENTS.md` — Agenten-Orchestrierung und Prioritäten
- `docs/EXPERT_ENGINEERING_SYSTEM.md` — vollständige Expertenlogik
- `docs/PATCH_AND_VALIDATION_PROTOCOL.md` — Patchdisziplin und Nachweis
- `docs/DATA_STORAGE_CONTRACT.md` — Datenklassen, Pfade, Safe IO
- `docs/UI_UX_ACCESSIBILITY_STANDARD.md` — UI, Responsive, Accessibility
- `docs/QUALITY_GATES.md` — Qualitätsgates
- `docs/RELEASE_GOVERNANCE.md` — Versionierung und Releases
- `quality-contract.json` — maschinenlesbare Kurzform

## 3. Architekturgrenzen
### Domain
Fachmodelle, Regeln und Invarianten. Keine direkten UI-, Dateisystem-, Datenbank- oder Netzwerkzugriffe.

### Application
Use Cases und Workflow-Orchestrierung. Arbeitet über kleine Verträge/Ports.

### Infrastructure
Konkrete Adapter für Dateisystem, Datenbank, Netzwerk, Betriebssystem und externe Dienste.

### Presentation
Darstellung, Navigation und Nutzerinteraktion. Keine duplizierte Fachlogik.

### Composition
Start, Konfiguration und Dependency Wiring.

## 4. Architektur-Invarianten
- Abhängigkeiten dürfen nicht unkontrolliert zwischen Schichten springen.
- Globale mutable Zustände vermeiden.
- Seiteneffekte an expliziten Grenzen bündeln.
- öffentliche Schnittstellen klein halten.
- keine Abstraktion ohne stabilen Vertrag oder tatsächliche Wiederverwendung.
- Fachlogik muss unabhängig von konkreter Oberfläche testbar bleiben.

## 5. Daten-Invarianten
- Basistooldaten und Nutzerdaten sind getrennt.
- jede persistente Datenart besitzt eine Datenklasse.
- alle kritischen Schreibvorgänge durchlaufen zentrale Storage-/IO-Grenzen.
- Updates dürfen Nutzerdaten nicht still überschreiben.
- Cache ist rekonstruierbar und niemals einzige Kopie wichtiger Nutzerdaten.

## 6. Safe-IO-Invariante
Kanonischer Ablauf:

`resolve → normalize → authorize → inspect → stage → operate → validate → commit → verify → report`

Erfolg erst nach Endvalidierung.

## 7. Fehler-Invarianten
- Fehler nicht verschlucken.
- technische Ursache, Domänenfehler, Diagnose und Nutzerhinweis trennen.
- Retries sind begrenzt und besitzen Abbruchbedingungen.
- sensible Daten nicht loggen.
- kritische Fehler dürfen keinen falschen Erfolgszustand hinterlassen.

## 8. UI-Invarianten
- Designwerte aus zentralen Tokens.
- wiederverwendbare Komponenten statt Copy/Paste.
- wichtige Zustände explizit gestalten.
- kleine und große Fenster nutzbar halten.
- keine wichtigen Aktionen außerhalb des sichtbaren/erreichbaren Bereichs.
- anpassbare Layouts benötigen sichere Grenzen und Reset.

## 9. Accessibility-Invarianten
Mindestziel WCAG 2.2 AA soweit anwendbar:
- Tastatur
- Fokus
- Kontrast
- semantische Beschriftung
- keine reine Farbcodierung
- Zoom/Schriftvergrößerung
- Screenreader-relevante Meldungen
- Reduced Motion

## 10. Qualitäts-Invarianten
- Tests risikobasiert auswählen.
- `NOT_RUN` nie als PASS.
- kritischer FAIL blockiert Freigabe.
- schreibende/riskante Änderungen benötigen stärkere Daten-/Recovery-Nachweise als rein lokale Darstellungspatches.

## 11. Patch-Invarianten
- Position zuerst exakt ermitteln.
- kleinsten vollständigen Patch wählen.
- keine Shotgun Changes.
- keine unbeteiligten Refactorings.
- Scope-Erweiterung neu klassifizieren.

## 12. Release-Invarianten
- SemVer.
- Version nur bei realem Scope ändern.
- Releases benötigen relevante Gates.
- Datenmigrationen benötigen Upgrade-/Recovery-Betrachtung.
- Artefaktintegrität soll nachweisbar sein.

## 13. Entscheidungspriorität
1. Datenintegrität
2. Recovery/Fehlerprävention
3. Wartbarkeit
4. Entkopplung/Wiederverwendung
5. Nutzbarkeit/Barrierefreiheit
6. Performance
7. visuelle Verfeinerung

## 14. Definition of Done
Ein Patch ist nur fertig, wenn Ziel, Datenwirkung und Risiko verstanden wurden, der kleinste vollständige Eingriff umgesetzt ist, relevante Gates ehrlich ausgewiesen sind und kein ungeklärter kritischer Daten-/Recovery-Fehler verbleibt.
