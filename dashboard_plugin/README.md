# TOSORT Dashboard-Plugin

Erstfassung für `/tosort` im Bereich `vsr`. Benutzt das Host-React-SDK wie
`cortex-ledger/dashboard_plugin`; keine eigenen Frontend-Laufzeitabhängigkeiten.
`node build.mjs` prüft JavaScript und kopiert `src/` nach `dist/`.

## Messung und Datenschutz

`GET /api/plugins/tosort/status` liefert nur feste Pool-Schlüssel, Zahlen,
Zeitpunkte und feste Statuswerte. Keine Dateinamen, Pfade, Inhalte, Hashes,
CLI-Kommandos, stdout/stderr oder Exception-Texte. Dokumentinhalte werden für
die Statusmessung nicht geöffnet. Das Frontend rendert nur bekannte Felder.

| Pool | Quelle | Zählung |
|---|---|---|
| Eingang | `ARCHIV_ROOT/TOSORT` | rekursiv; `_KLAEREN`, `_TRASH`, `.DS_Store`, `README.md` ausgeschlossen, entsprechend Router-Auswahl |
| Klärung (Altbestand) | `ARCHIV_ROOT/TOSORT/_KLAEREN` | separat, rekursiv |
| Manuelle Prüfung | `ARCHIV_ROOT/_AI_META/TOSORT_REVIEW` | separat, rekursiv, neuere Regel vom 19.09. |

Die Quellen stammen aus `_common.py`, `tosort_route.py` und
`Desk/_rules/ARCHIV_TOSORT.md`. Keine erfundenen Zusatz-Eingänge und kein
Mail-Import. Sonstige Unterordner im kanonischen Eingang sind im Eingang enthalten.
Fehlende/unlesbare Pools, Teilfehler, Symlinks und zukünftige Datei-mtimes:
`count=null`, Status `not_measurable`; niemals Ersatzwert null Dateien.
Leerer lesbarer Pool: `count=0`. Alter = Sekunden seit ältester Datei-mtime;
kein Dokumentdatum und keine garantierte Eingangszeit.

`last_routing_at` ist die neueste mtime einer lesbaren vorhandenen
`_AI_META/TOSORT/**/Routing_YYYYMMDD.csv`. Die UI nennt dies ausdrücklich
„Routing-Nachweis (Dateiänderung)“: nachträgliche Änderungen sind möglich;
daraus wird kein erfolgreicher Ablagelauf behauptet. Kein Nachweis: `null`.
Die Laufanzeige liest zusätzlich die atomar geschriebene `state/run.json`.
Fremde JSON-Felder werden verworfen; unbekannte/defekte Zustände oder ein
verwaister `running`-Status ergeben „nicht messbar“.

## Laufstart

`POST /api/plugins/tosort/lauf` (202) startet einen Hintergrund-Thread;
`GET /api/plugins/tosort/lauf/status` liefert dessen reduzierten Zustand.
Die UI pollt alle 2,5 Sekunden. Start während eines Laufs: 409.
Start ist ohne `TOSORT_ENABLE_RUN=1` gesperrt. Custom-Header
`X-TOSORT-Action: start` ist Pflicht; `Sec-Fetch-Site: cross-site` wird abgewiesen.
Alle drei API-Endpunkte prüfen vor Zugriffen den Host-Header: genau einmal
`127.0.0.1` oder `localhost`, optional mit numerischem Port 1–65535.
Fehlende, fremde, doppelte oder ungültige Hosts erhalten 403 ohne Interna.
Forwarding-Header ersetzen diese Prüfung nicht. Die Host-Prüfung schützt gegen
DNS-Rebinding; Benutzer-Authentifizierung muss der Dashboard-Host bereitstellen.
Der Action-Header ist kein Authentifizierungsersatz. Keine offene CORS-Freigabe setzen.

Der Adapter ruft ausschließlich die bestehenden Skripte auf, sequenziell:

1. `archiv_index.py scan`
2. `archiv_index.py hash` (vollständiger MD5-Nachzug für Dublettenchecks)
3. `archiv_index.py registers`
4. Falls eine Downloads-Korrekturliste existiert: `lern_diff.py`; Auswahl und Vergleich durch den bestehenden Helfer. Fehlender Vorschlag führt zu Abbruch.
5. `tosort_route.py --input <ARCHIV>/TOSORT --out <eindeutiger Laufordner>`
6. `downloads_liste.py --routing <Routing-CSV dieses Laufs> --datum <Datum> --neue-generation --personenbezug --lauf Dashboard_<ID>`

Kein Import der Pipeline beim API-Laden: `_common.py`/DB-Helfer können schreiben.
Kein `shell=True`, keine vom HTTP-Request wählbaren Pfade/Argumente.
Nach Erfolg: `awaiting_review`. Kein Aufruf von `tosort_execute.py --run`:
die Freigabe und anschließende Ablage bleiben im bestehenden Workflow.
Die Pipeline darf beim späteren Betrieb ihre üblichen Artefakte schreiben
(Katalog, Register, Anfrage, Downloads-Liste, geschützte Vorschlagskopie,
Lernzeiger/Protokoll). Der Entwicklungsauftrag hat sie **nicht ausgeführt**.

Jeder Fehler stoppt die Sequenz; UI meldet nur „Fehlgeschlagen“.
Prozessausgaben gehen nach DEVNULL; Detaildiagnose bleibt außerhalb der UI.
Ein Dateilock schützt parallele Plugin-Worker. Zusätzlich reserviert der Adapter
den vorhandenen PID-Lock `.archiv_index_writer.lock` per O_EXCL; bestehende
Locks werden nicht automatisch entfernt. Der Legacy-Tick reserviert selbst
nicht atomar: ein gleichzeitiger Tick-Start hat weiterhin ein Rennen.
Vor produktiver Aktivierung Tick/Drain auf dem einzigen Katalog-Rechner
koordiniert pausieren; eine globale Garantie über manuelle CLI-Läufe gibt es
nicht. Hard-Kill kann Teilprodukte/verwaiste Locks hinterlassen; erst prüfen,
keine automatische Fortsetzung. Keine neue Rollback-/Ablagelogik eingeführt.

## Aktivierungspaket für Nexus-KI — hier NICHT angewendet

| Quelle in diesem Repo | Ziel |
|---|---|
| `dashboard_plugin/manifest.json` | `Nexus/plugins/tosort/dashboard/manifest.json` |
| `dashboard_plugin/plugin_api.py` | `Nexus/plugins/tosort/dashboard/plugin_api.py` |
| `dashboard_plugin/dist/index.js` | `Nexus/plugins/tosort/dashboard/dist/index.js` |
| `dashboard_plugin/dist/style.css` | `Nexus/plugins/tosort/dashboard/dist/style.css` |

Optional README daneben kopieren. **Nicht** node_modules, Fixtures, evidence,
`.tmp` oder lokalen Zustand installieren. Der gemessene Nexus-Loader sucht
`plugins/<name>/dashboard/manifest.json`, importiert `router` und mountet ihn
unter `/api/plugins/<name>`. SDK-Registrierung: `registry.register('tosort', App)`.

Im Harness in
`projects/cortex-harness/vendor/cortex-agent/web/src/lib/ide-workbench/plugin-areas.ts`
in `PLUGIN_PATH_AREA` neben Ledger ergänzen:

```ts
"/tosort": "vsr",
```

Das ist notwendig: Manifest-`section` wird von diesem Resolver nicht ausgewertet;
unbekannte Routen landen in `mehr`. Im zugehörigen Mapping-Test `/tosort` und
`/tosort/` auf `vsr` prüfen. Harness nach dessen regulärem Verfahren bauen und
ausrollen, Dashboard neu laden/starten. Dies ist eine Übergabe, keine Aktivierung.

Konfiguration am autorisierten Dashboard-Prozess auf dem Katalog-Rechner:

| Variable | Default / Bedeutung |
|---|---|
| `TOSORT_SKILL_ROOT` | `~/Cortex/Desk/_skills/archiv-tosort` |
| `ARCHIV_ROOT` | `<Skill>/../../ARCHIV` (kanonisches Desk-Archiv) |
| `TOSORT_PYTHON` | Python des Dashboard-Prozesses; produktiv Interpreter mit PyYAML und Pipeline-Abhängigkeiten wählen |
| `TOSORT_STATE_DIR` | `<installiertes dashboard>/state`, beschreibbar und privat |
| `TOSORT_ENABLE_RUN` | default gesperrt; `1` erst bei produktiver Startfreigabe |

Python benötigt FastAPI; flock ist auf dem vorgesehenen macOS/Linux verfügbar.
Bestehenden Ordner `_AI_META/ARCHIV_INDEX/logs` voraussetzen (kein automatisches
Anlegen eines neuen Archivbaums). Schreibrechte für die Pipeline-Ziele,
OCR-Werkzeuge und aktuelle Regeln/Zuordnungswissen separat im Zielbetrieb prüfen.
Der vorhandene Router erzeugt weiterhin `_ANFRAGEN`; neuere Archivregeln
unterscheiden sich teilweise vom Skriptbestand. Adapter verändert diese Regeln
nicht und ersetzt die fachliche Freigabe nicht.

Abnahme nach Aktivierung: `/tosort` unter VSR, alle Aggregate korrekt oder
„nicht messbar“, API ohne Einzeldateidaten, Start zunächst in separater
synthetischer Pipeline-Umgebung prüfen. In diesem Auftrag kein Live-Start.

## Reproduzierbare Nachweise

Vom Repo-Root, mit Python-Umgebung mit FastAPI/httpx:

```sh
PYTHONDONTWRITEBYTECODE=1 python -B -m unittest discover -s dashboard_plugin/tests -v
npm ci --prefix dashboard_plugin --cache .tmp/npm-cache --no-audit --no-fund
node dashboard_plugin/build.mjs
npm test --prefix dashboard_plugin
```

Tests schreiben ausschließlich Fixtures innerhalb dieses Repos. Der Subprozess-Test
führt ausschließlich synthetische Skripte aus. Der React/jsdom-Test lädt **dist**,
montiert die echte Komponente, klickt, pollt und prüft Ausfall/Redaktion.
`tests/dom.test.cjs` deckt den Ablauf ab; `tests/render.test.cjs` deckt die
Feld-für-Feld-Rückfälle auf „nicht messbar“ ab und lädt `dist` per `require`,
damit `node --test --experimental-test-coverage` die Datei messen kann.
`evidence/dom-fixture.html` ist der serialisierte Fixture-DOM, kein Screenshot
und kein Nachweis einer Live-Aktivierung in :9119.
