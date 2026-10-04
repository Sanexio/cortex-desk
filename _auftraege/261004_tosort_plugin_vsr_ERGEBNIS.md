# Ergebnis: TOSORT-Plugin unter VSR

Stand: 04.10.2026. Implementiert in `dashboard_plugin/`, nicht aktiviert, kein Commit.
Alle Schreiboperationen dieses Auftrags blieben in `~/Cortex/projects/cortex-desk`.
Nexus, Desk-Skill und Harness wurden nur gelesen. Keine Praxisdokumente gelesen,
keine produktive Pipeline gestartet. Vorhandener Auftrag blieb unverändert.

## Geliefert

- Manifest `/tosort`, Bereich `vsr`, Host-SDK-Registrierung und API-Router nach Ledger-Konvention.
- Aggregate für kanonischen Eingang, alte Klärung und neue manuelle Prüfung; älteste Datei nur als Alter. Fehlende oder teilweise unlesbare Quellen: „nicht messbar“.
- Letzter Routing-Nachweis aus vorhandener Routing-Datei-mtime, ausdrücklich als Dateiänderung gekennzeichnet; Start/Ende aus reduziertem Laufzustand.
- Button „TOSORT-Lauf starten“, Polling, persistierter Laufstatus, Mehrfachstart-Sperre, vorhandener Archiv-Writer-Lock, neutralisierte Fehler.
- Adapter für bestehende Skripte: scan → hash → registers → ggf. lern_diff → tosort_route → downloads_liste. Keine neue Routing-/Ablagelogik. Erfolg bedeutet „Freigabe ausstehend“; tatsächliche Ablage bleibt freigabepflichtig.
- `src` und gebautes `dist`, dependency-freier Produktionsbuild, Fixture-Tests und Aktivierungspaket.

## Gemessene Grundlagen

Gelesen: `Desk/_skills/archiv-tosort/SKILL.md`, `_common.py`, Router,
Index-Tick, Downloads-/Lern-Helfer; ergänzend Archiv-/Inhaltspflichtregeln.
Ledger-Vorbild: manifest, build.mjs, Host-React-SDK und Hintergrundlaufstatus.
Nexus `dashboard/server.py` erwartet `plugins/tosort/dashboard/`, API-Prefix
`/api/plugins/tosort`. Harness `plugin-areas.ts` benötigt explizit
`"/tosort": "vsr"`; allein das Manifest ordnet die Route dort nicht zu.

## Verifikation

**Suite-Summe: 16 Tests, 16 bestanden, 0 fehlgeschlagen.**

- Python: `Ran 15 tests ... OK` in `dashboard_plugin/evidence/python-tests.txt`.
- React/jsdom: `tests 1 / pass 1 / fail 0` in `dashboard_plugin/evidence/dom-tests.txt`.
- Build: `TOSORT plugin build: 2 files`; src/dist identisch geprüft.
- DOM-Nachweis: `dashboard_plugin/evidence/dom-fixture.html`, aus echtem React-Mount der gebauten Datei mit synthetischen API-Daten. Startklick, Laufstatus, Polling, Fehler, deaktivierter Button und Datenschutz geprüft.
- API: leer vs. fehlend, Rekursion/Ausschlüsse, Alter, Teil-Lesefehler, Symlinks, Zukunftsdatum, historische Routing-mtime, korrupter/verwaister Laufstatus, Startschutz, fehlende Pipeline, Mehrfachstart, externer Writer, Erfolg/Fehler und echte Subprozesse mit ausschließlich synthetischen Skripten.

Testinterpreter: vorhandene `Nexus/.venv/bin/python` nur ausgeführt,
mit `-B`/`PYTHONDONTWRITEBYTECODE=1`; keine Installation/Änderung dort.
Frontend-Testabhängigkeiten und npm-Cache liegen ausschließlich in diesem Repo.
FastAPI-Testclient meldet eine bestehende httpx-Deprecation; alle Tests bestehen.
Im ursprünglichen Repo wurde keine Testsuite gefunden; vorhanden ist eine
separate Befund-Demo, die für diesen Plugin-Auftrag nicht verändert wurde.

## Übergabe und Betriebsgrenzen

Vollständige Dateizuordnung, Umgebungsvariablen, Mapping-Änderung und
Abnahmeschritte: `dashboard_plugin/README.md`, Abschnitt Aktivierungspaket.
Kein Kopieren nach Nexus, kein Harness-Build/Deployment, kein Live-DOM auf :9119.
Laufstart ist standardmäßig deaktiviert und benötigt die spätere Aktivierung.

Der historische Zeitpunkt ist ein Routing-Artefakt-Nachweis, kein verifizierter
Ablageabschluss. Ohne Nachweis bleibt die Anzeige unbekannt. Statusdaten werden
nur feldweise freigegeben; Prozessausgaben werden vollständig verworfen.

Der Legacy-Index-Tick verwendet einen nicht atomaren PID-Lock. Vor produktiven
Starts Tick/Drain koordiniert pausieren; manuelle CLI-Läufe sind nicht durch
den Plugin-Lock serialisiert. Hard-Kill/Teilprodukte benötigen manuelle Prüfung.
Die bestehenden Skripte schreiben beim späteren Betrieb ihre üblichen
Katalog-/Freigabe-/Lernartefakte außerhalb dieses Repos; im Auftrag wurden
nur ihre Aufrufe implementiert und durch Fixture-Skripte verifiziert.
