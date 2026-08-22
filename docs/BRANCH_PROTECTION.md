# MASTERCORE — Branch Protection Contract

Status: verbindliches Zielbild  
Required Check: `MASTERCORE Quality`

## Zweck
`main` soll nur Änderungen aufnehmen, deren verpflichtende MASTERCORE-Qualitätsgates erfolgreich gelaufen sind. Ein fehlgeschlagener oder fehlender Required Check darf keinen normalen Merge erlauben.

## Zielregel für `main`

- Pull Request vor Merge erforderlich.
- Required Status Check: `MASTERCORE Quality`.
- Branch muss vor Merge auf aktuellem Stand mit `main` sein, sofern GitHub diese Option anbietet.
- Force Pushes deaktivieren.
- Branch-Löschung deaktivieren.
- Bypass nur für ausdrücklich dokumentierte Notfälle; im Normalbetrieb auch für Administratoren keine Qualitätsumgehung.

## Warum der Checkname stabil ist
Der GitHub-Actions-Job in `.github/workflows/quality.yml` trägt explizit den Namen `MASTERCORE Quality`. Derselbe Name steht in `quality-contract.json` unter `quality_automation.required_status_check`. G0 prüft diese Zuordnung, damit der Schutz nicht durch unbeabsichtigtes Umbenennen des Jobs ins Leere läuft.

## Aktivierung in GitHub
Die serverseitige Branch-Protection-/Ruleset-Einstellung ist keine Repository-Datei. Sie muss mit Adminrechten in GitHub aktiviert werden:

1. Repository `provoware/MASTERCORE` öffnen.
2. `Settings` öffnen.
3. Unter `Rules`/`Rulesets` oder `Branches` eine Schutzregel für `main` anlegen.
4. Pull Requests vor Merge verlangen.
5. Statuschecks vor Merge verlangen.
6. Den Check `MASTERCORE Quality` auswählen.
7. Wenn verfügbar, „Branch muss aktuell sein“ aktivieren.
8. Force Pushes und Löschen des Branches verbieten.
9. Regel aktivieren und speichern.

## Abnahme
Nach Aktivierung gilt Branch Protection nur dann als **PASS**, wenn ein Test-PR mit absichtlich fehlschlagendem `MASTERCORE Quality`-Check nicht gemergt werden kann und ein grüner PR mergebar bleibt.

Bis diese serverseitige Einstellung nachweislich aktiviert und getestet wurde, ist Branch Protection als **NOT_RUN / ausstehend** zu behandeln, nicht als PASS.
