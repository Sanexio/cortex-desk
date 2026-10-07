# cortex-desk — Regelwerk für die Verwaltungsschicht einer Arztpraxis

> **Cortex-Layer-Projekt** in einem Plattform-Modell mit klarer Trennung
> von offenem Regelwerk und proprietärer Engine:
> generisches Regelwerk für die Verwaltungsschicht einer
> ambulanten Arztpraxis — das, was zwischen klinischer Tätigkeit und
> Buchhaltung an wiederkehrenden Dokumenten-Vorgängen anfällt:
> Befundberichte, Amtsanfragen, Steuersachen, Anwaltskorrespondenz,
> Personal- und Mietangelegenheiten, KV-Mitteilungen.
>
> **Status:** Kuratiertes, anonymisiertes Regelwerk unter Apache 2.0.
> Das produktive Verarbeitungs-Tooling ist nicht Teil dieses Repos
> (siehe `docs/ENGINE_INTEGRATION.md`); enthalten sind lauffähige
> Show-Case-Demos unter `examples/` (python3-stdlib, fiktive Daten).

## Phase-B-Vorlagen (2026-09-26)

Die öffentlichen Schablonen sind in [Umfang und Nutzung](docs/PHASE_B_VORLAGEN.md)
beschrieben und im [Vorlagenmanifest](docs/vorlagen-manifest.json) erfasst.
Sie enthalten ausschließlich Platzhalter; befüllte Kopien bleiben im privaten Tenant.

## Was ist hier drin

- **`rules/`** — kuratiertes Regelwerk (D-001 bis D-010), Top-Level-
  Schema (Medizin · VSR), Sub-Workflow-Übersicht, Sprache-und-Stil-
  Matrix nach Adressat, Demo-Schablonen für Tenant-Files.
- **`docs/ENGINE_INTEGRATION.md`** — wie Tenants Verarbeitungs-Tooling
  (PDF-Extraktion, OCR, Diagnosen-Erkennung, Berichtsvalidierung)
  anbinden.

- **`examples/`** — freie Demos mit fiktiven Daten.
- **`tools/desk-sync.sh`** — freies Sync-Hilfsskript; lokale
  Konfiguration nach `tools/desk-sync.conf.example` erforderlich.
- **`tests/`** — Testsuiten für `examples/` und `tools/`. Die Suite des
  Dashboard-Plugins liegt weiterhin unter `dashboard_plugin/tests/`.

## Tests

Alle Tests legen ihre Fixtures synthetisch in Wegwerf-Verzeichnissen an;
weder echte Dokumente noch Netzzugriff sind beteiligt.

```sh
# Repo-Suiten (examples/, tools/)
PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest discover -s tests -t tests

# Plugin-Suiten (FastAPI-Adapter, React-Oberfläche)
PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest discover -s dashboard_plugin/tests
npm ci --prefix dashboard_plugin --no-audit --no-fund && npm test --prefix dashboard_plugin

# Alles zusammen mit Abdeckungsbericht
bash tests/coverage.sh
```

## Was hier explizit NICHT drin ist

- **Konkrete Patient-/Mandanten-Daten** in jeglicher Form — diese
  verlassen den Tenant-Bereich nie und gehören niemals in ein OSS-Repo.
  Live-Arbeitsverzeichnisse (`Medizin/Input`, `Medizin/Output`, `VSR/`,
  `ARCHIV`) sind gitignored und werden auch im Tenant-Repo nur intern
  versioniert (Tenant-Arbeitsbereich `<lokaler-pfad>`).
- **Praxis-spezifische Header / Adressbuch / Steuerberater- /
  Anwalts-Listen** — gehören in `rules/*_TENANT.md` (gitignored) bzw.
  ins Tenant-Repo.
- **Vorbefüllte Befundbericht- oder Antwort-Templates** mit Praxis-
  Logo, Briefkopf, konkreten Versorgungsangeboten — Tenant.
- **Produktives proprietäres Verarbeitungs-Tooling** (Textextraktion,
  Diagnosen-Erkennung, Berichtsvalidierung, OCR und PDF-Verarbeitung).
  Tenants haben zwei
  Optionen:
  1. **Eigenes Tooling bauen** nach diesem Regelwerk (Open-Source-
     Distribution).
  2. **Proprietäres Tooling lizenzieren** als Teil eines Tenant-
     Pakets.
- **Proprietäre Sessionstart-Hooks oder Skill-Verdrahtung** gehören
  in die jeweilige Engine. Das Regelwerk dokumentiert die
  Sub-Workflows als generische Bausteine, ohne die proprietäre Skill-
  Mechanik mit auszuliefern.

Das ist die Cortex-Plattform-Architektur: offenes Regelwerk (dieses
Repo), tenant-spezifische Konfiguration (privates Tenant-Repo) und
proprietäres Engine-Tooling (Sanexio) — drei getrennte Schichten.

## Top-Level-Schema (Auszug aus `rules/SCHEMA.md`)

Eine Praxis-Verwaltungs-Arbeitsumgebung gliedert sich in:

```
DESK.md                 ← Steuerdokument (Sessionstart-Pflicht D-001)
README.md               ← Onboarding
_rules/                 ← Desk-Regeln + Pointer aufs zentrale Regelwerk
_config/                ← übergreifende Konfiguration + Fehlerprotokoll
_sync/                  ← Multi-Device-Sync-Mechanismus
_archiv/                ← Migrations- und Architekturhistorie

Medizin/                ← Medizinische Vorgänge
├── Input/   Output/   ARCHIV/
└── _config/subcategories/   (befundberichte · amtsanfragen · …)

VSR/                    ← Verwaltung · Steuer · Recht
├── Input/   Output/   ARCHIV/
└── _config/subcategories/   (verwaltung · steuer · recht)
```

## Sub-Workflows (Auszug aus `rules/WORKFLOW.md`)

| Subworkflow | Hauptort | Output-Typ |
|---|---|---|
| Befundbericht-Erstellung | `Medizin/Input` | strukturierter Befundbericht |
| Amtsanfrage Medizin | `Medizin/Input` | Antwortschreiben an Behörde |
| Amtsanfrage Steuer | `VSR/Input` | Antwortschreiben an Finanzamt |
| Verwaltung Personal | `VSR/Input` | Personalvorgangs-Antwort |
| Verwaltung Mietvertrag | `VSR/Input` | Mietsachen-Antwort |
| Verwaltung KV | `VSR/Input` | Antwort an KV-/PVS-Stelle |
| Recht Anwaltskorrespondenz | `VSR/Input` | Anwaltsbrief |
| Recht Datenschutz | `VSR/Input` | DSGVO-Antwort |
| Recht Gesellschaftsrecht | `VSR/Input` | GbR-/MVZ-/PartG-Antwort |

## Quickstart für andere Praxen

```bash
# 1. Repo klonen
git clone https://github.com/Sanexio/cortex-desk.git
cd cortex-desk

# 2. Tenant-eigene Inhalte anlegen (gitignored, sicher gegen
#    versehentliches Commit ins OSS-Repo)
cp rules/ADRESSATEN_EXAMPLE.md     rules/ADRESSATEN_TENANT.md
cp rules/PRAXIS_HEADER_EXAMPLE.md  rules/PRAXIS_HEADER_TENANT.md
cp rules/SUBWORKFLOWS_EXAMPLE.md   rules/SUBWORKFLOWS_TENANT.md
nano rules/PRAXIS_HEADER_TENANT.md   # eigenen Briefkopf eintragen
nano rules/ADRESSATEN_TENANT.md      # eigene KV, <behoerde>,
                                     # Steuerberater, Anwalt eintragen

# 3. Arbeitsumgebung initialisieren (live Patient-/Mandant-Daten;
#    diese Ordner sind .gitignored, kommen NIE in Versionskontrolle)
mkdir -p Medizin/{Input,Output,ARCHIV}
mkdir -p VSR/{Input,Output,ARCHIV}

# 4. Tooling-Optionen — siehe docs/ENGINE_INTEGRATION.md
#    (Extraktion, OCR, Diagnosen-Erkennung, Berichtsvalidierung)
```

## Datenschutz-Hardstop

`cortex-desk` arbeitet per Konstruktion mit Patient- und Mandanten-Daten.
Drei harte Grenzen:

1. **Live-Arbeitsverzeichnisse** (`Medizin/Input|Output|ARCHIV`,
   `VSR/Input|Output|ARCHIV`) sind gitignored und kommen **niemals**
   ins OSS-Repo. Auch im Tenant-Repo bleiben sie nur im privaten
   Tenant-Kontext (`<tenant-live-repo>/desk`, private).
2. **Patientendaten verlassen den Tenant nur** per direktem Versand
   an den jeweils zuständigen Adressaten (Krankenkasse, MDK,
   <behoerde>, Gericht, …) — niemals über öffentliche Repos,
   öffentliche Pastebins, Cloud-Services außerhalb des autorisierten
   Verarbeiter-Kreises.
3. **Output-Dokumente enthalten keine Meta-Kommentare** auf KI,
   Sprachmodell, Vorlagen, automatische Erstellung oder
   Bearbeitungshistorie (D-003).

## Beitrags-Modell

Pull-Requests willkommen. Bevor du eine PR aufmachst:

- README + `docs/ENGINE_INTEGRATION.md` lesen
- Schema-Erweiterungen (neue Top-Level-Kategorie neben Medizin/VSR,
  neuer Sub-Workflow, Anpassung der Sprache/Stil-Matrix) bitte zuerst
  als Issue diskutieren
- Tenant-spezifische Inhalte (eigene Adressaten, eigener Briefkopf,
  konkrete Patient-/Mandanten-Beispiele) sind **nicht** Teil dieses
  Repos
- Patient-/mandantenbezogene Daten in PRs werden ohne Diskussion
  zurückgewiesen.

Maintenance: Projekt-Maintainer — 2-Personen-Approval bei PRs
mit Schema-Impact.

## Querverweise

- Sister-Repos im Cortex Layer: `cortex-qm`,
  `cortex-rename`, ein generisches Praxiswebseiten-Theme.

## Lizenz

Regelwerk, Vorlagen, Demos und Hilfsskripte dieses Repos stehen unter der
Apache License 2.0 — siehe [LICENSE](LICENSE) und [NOTICE](NOTICE).
Optionale proprietäre Engines sind nicht Bestandteil dieser Lizenzierung.
