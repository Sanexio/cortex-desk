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

## Haertung Host-Check

Review 20:10 umgesetzt am 04.10.2026. Kein Commit, keine Aktivierung;
alle Änderungen und Testartefakte ausschließlich in `cortex-desk`.

Vor Änderung gemessen (Referenzen ausschließlich gelesen):
`Nexus/dashboard/server.py:333` erstellt die FastAPI-App ohne zentrale
Host-/Authentifizierungs-Middleware; `:350` bindet Plugin-Router ohne zusätzliche
Dependencies ein. Die Loopback-Bindung bei `:371` prüft keinen HTTP-Host.
`Nexus/plugins/kalkulation/dashboard/plugin_api.py:67` und `:87` verwenden den
Host zur URL-Bildung, ohne Erlaubnisliste (identisch im geprüften
`projects/cortex-prx-kalkulation/dashboard_plugin/kalkulation/dashboard/plugin_api.py`).
Damit kein belegbarer Fehlalarm und kein bestehender zentraler Schutz, der
hier doppelt implementiert würde. Die vorhandene APIRouter-Einbindung bleibt erhalten.

`dashboard_plugin/plugin_api.py:21` prüft genau einen Host-Header gegen
`127.0.0.1` bzw. `localhost`, optional mit ASCII-Port 1–65535.
Die Router-Dependency bei `:31` schützt beide Status-GETs und den Start-POST
vor Ausführung der Endpunkte. Fremde, fehlende, leere, doppelte oder manipulierte
Hosts erhalten ausschließlich `403 {"detail":"Zugriff nicht erlaubt"}`.
Forwarded-/X-Forwarded-Host-Werte gewähren keine Ausnahme.
Der Start bleibt ohne `TOSORT_ENABLE_RUN=1` deaktiviert; Action-Header und
Cross-Site-Sperre bleiben zusätzlich erforderlich. Host-Prüfung ist
DNS-Rebinding-Schutz, keine Benutzer-Authentifizierung; diese muss weiterhin
der Dashboard-Host bereitstellen. Die frühere unbelegte Code-Aussage, der Host
liefere bereits Authentifizierung, wurde korrigiert.

Nachweis: **19 Tests bestanden, 0 fehlgeschlagen** — ursprüngliche 16er-Suite
plus drei neue Tests (18 Python + 1 React/jsdom).
Neue Prüfungen: erlaubte Hosts/Ports auf beiden GETs; 27 ungültige bzw.
fehlende/doppelte Host-Konstellationen auf allen drei Endpunkten (81 negative
Requests); deaktivierter Start bei tatsächlich fehlender Aktivierungsvariable.
Bei sämtlichen negativen Host-Requests bleiben Messung, Statuslesen,
Routing-Lesen, Kommandoerzeugung, Thread und Subprozess unaufgerufen;
keine State-Dateien oder Writer-Locks entstehen. Antworten sind exakt auf
die neutrale Fehlermeldung beschränkt. Raw-ASGI-Requests sichern insbesondere
den fehlenden Host ab, den der TestClient sonst automatisch ergänzt.

Ausgeführt vom Repo-Root:

```sh
PYTHONDONTWRITEBYTECODE=1 /Users/ssmd/Cortex/Nexus/.venv/bin/python -B -m unittest discover -s dashboard_plugin/tests -v
npm test --prefix dashboard_plugin
git diff --check
```

Aktualisierte Nachweise: `dashboard_plugin/evidence/python-tests.txt` und
`dashboard_plugin/evidence/dom-tests.txt`. Bestehende httpx-Deprecation weiterhin
ohne Testfehler. `dist` enthält ausschließlich unverändertes JS/CSS und ist
von der Python-Härtung nicht betroffen; kein Neubuild erforderlich, src/dist
auf Inhaltsgleichheit geprüft. Keine produktive Pipeline gestartet.
