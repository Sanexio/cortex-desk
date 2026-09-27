# Ordner-Schema — kanonischer Aufbau einer Praxis-Desk-Arbeitsumgebung

## Top-Level-Ebene

```
DESK.md                 ← Steuerdokument (Sessionstart-Pflicht D-001)
README.md               ← Onboarding für neue Mitarbeitende
_rules/                 ← Desk-Regeln + Pointer aufs zentrale Regelwerk
_config/                ← übergreifende Konfiguration + Fehlerprotokoll
_sync/                  ← Multi-Device-Sync (LaunchAgent o.ä.)
_archiv/                ← Migrations- und Architekturhistorie

Medizin/                ← Medizinische Vorgänge
├── Input/
├── Output/
├── ARCHIV/
└── _config/
    └── subcategories/
        ├── befundberichte/
        └── amtsanfragen/

VSR/                    ← Verwaltung · Steuer · Recht
├── Input/
├── Output/
├── ARCHIV/
└── _config/
    └── subcategories/
        ├── verwaltung/
        ├── steuer/
        └── recht/
```

## Top-Level-Datei `DESK.md`

Verbindlich vorhandenes Steuerdokument. Inhalt:

- Frontmatter mit `name`, `version`, `status`, `ebene`, `erstellt`
- Architekturübersicht (Regelwerk, private Arbeitsdaten und optionale Engine)
- Top-Level-Struktur (analog zu diesem Dokument, mit Tenant-Anpassungen)
- Regel-Hierarchie (s.u.)
- Sessionstart-Pflicht-Schritte
- Tool-Aufrufmuster (verweist auf Engine- oder Tenant-eigenes Tooling)
- Sync-Hinweis (Repo-URL, Frequenz, LaunchAgent-Name)
- Grundregeln-Zusammenfassung (D-002..D-004 als One-Liner)

Das Dokument wird **bei jedem Trigger eines Desk-Workflows zuerst
gelesen** (D-001). Es ist die Single Source of Truth für die
Tenant-Hülle und überschreibt nichts aus dem OSS-Regelwerk —
ergänzt nur.

## Die zwei Top-Level-Kategorien

Verbindlich: **Medizin** und **VSR**. Eine Praxis kann zusätzliche
Top-Level-Kategorien einführen, sollte aber die Aufteilung von
medizinisch-klinischen vs. verwaltungs-/steuer-/rechtlichen Vorgängen
beibehalten.

| Kategorie | Vorgangs-Typen | Adressaten |
|---|---|---|
| **Medizin** | Befundberichte, Konsiliarbriefe, Atteste, Amtsanfragen mit medizinischem Bezug (MDK, <behoerde>) | Patient, Arzt, Krankenkasse, MDK, <behoerde> |
| **VSR** | Verwaltungsvorgänge, Steuersachen, Rechtskorrespondenz | Finanzamt, Anwalt, Gericht, KV/PVS, Vermieter, Personal, Behörde |

Erweiterung um weitere Top-Level-Kategorien (z.B. `Forschung/`,
`Lehre/` für Praxen mit akademischer Anbindung): erlaubt, sollte aber
in `DESK.md` der Tenant-Hülle erläutert werden.

## Sub-Subkategorien

Jede Top-Level-Kategorie hat eigene Subkategorien unter
`<Kategorie>/_config/subcategories/`:

```
Medizin/_config/subcategories/
├── befundberichte/
│   ├── RULES.md                    ← spezifische Regeln (MED-CAT-*)
│   ├── FEHLERPROTOKOLL.md
│   └── WORKFLOW_CHECKLIST.md
└── amtsanfragen/
    ├── RULES.md                    ← MAF-*
    ├── FEHLERPROTOKOLL.md
    └── WORKFLOW_CHECKLIST.md

VSR/_config/subcategories/
├── verwaltung/
│   └── (kv, mietvertrag, personal — jeweils RULES.md + FEHLERPROTOKOLL.md)
├── steuer/
│   └── (amtsanfragen-steuer)
└── recht/
    └── (anwaltskorrespondenz, datenschutz, gesellschaftsrecht)
```

Detaillierte Inhalts-Hinweise pro Subkategorie: siehe
`CATEGORIES_EXAMPLE.md`.

## Output-Lebenszyklus

```
Input/  → (Verarbeitung mit Tooling) →  Output/  → (Versand/Print)  →  ARCHIV/
   ↑                                       ↑                              ↑
   eingehende Originale                    erzeugte Antwort               Vorgangs-
   (PDF, gescannt,                         (Word, PDF, Markdown)          abschluss
   Mail-Anhang)
```

| Ordner | Lebensdauer | Zweck |
|---|---|---|
| `Input/` | kurz (eine Verarbeitungsiteration) | eingehende Originale, vor Verarbeitung |
| `Output/` | mittel (bis Versand) | erzeugte Antwort-Dokumente, ggf. Patientenordner |
| `ARCHIV/` | lang (Aufbewahrungsfrist) | abgeschlossene Vorgänge, read-only, git-versioniert |

**Regel D-009:** Originale werden nach Verarbeitung von `Input/` nach
`ARCHIV/` verschoben (nicht kopiert). `Output/` behält die erzeugten
Antwort-Dokumente bis zum Versand und wandert dann ebenfalls nach
`ARCHIV/`.

## Patientenordner-Konvention

Sobald für einen Patienten/Mandanten **≥ 2 Output-Dateien** existieren,
wird ein eigener Unterordner angelegt:

```
Output/<Nachname>_<Vorname>/
    <Nachname>_<Vorname>_<YYYY-MM-DD>_<Dokumenttyp>.<ext>
```

Transliteration: `ä → ae`, `ö → oe`, `ü → ue`, `ß → ss`,
Leerzeichen → `_`.

Bei Namensgleichheit: Geburtsjahr anhängen
(`Mueller_Peter_1972`).

Details: `CORE_RULES.md` D-005.

## Dateinamen-Konvention

Format: `<Name>_<Datum>_<Dokumenttyp>.<ext>`

- Datum als ISO `YYYY-MM-DD` für neue Dokumente (sortier-sicher,
  unverwechselbar).
- Kurzform `YYMMDD` nur für Altbestand zulässig (vor Migration auf
  ISO-Format).
- Mehrere Dokumente desselben Tages: thematisches Suffix
  (`_Befundbericht.pdf`, `_Vorbefunde_Onkologie.pdf`).
- Keine Patient-bezogenen Daten in Dateinamen, die über
  `<Nachname>_<Vorname>` hinausgehen (keine Geburtsdaten, keine
  Diagnosen, keine Versicherungs-Kennungen — DSGVO).

Details: `CORE_RULES.md` D-006.

## Regel-Hierarchie

Vom Allgemeinen zum Spezifischen — spezifischeres Regelwerk
überschreibt:

1. **Cortex-Layer-Regelwerk (dieses Repo)** — `rules/CORE_RULES.md`,
   `rules/SCHEMA.md`, `rules/WORKFLOW.md`. Verbindlich für alle
   Tenants.
2. **Tenant-Hülle** — `DESK.md` + `_rules/DESK_RULES.md` der
   Tenant-Variante. Ergänzt um Tenant-Spezifika (Praxis-Header,
   Adressbuch), kann aber das OSS-Regelwerk nicht aufheben.
3. **Kategorie** — `<Kategorie>/_config/RULES.md` (z.B.
   `Medizin/_config/RULES.md`). Medizin-spezifische oder
   VSR-spezifische Regeln.
4. **Subkategorie** — `<Kategorie>/_config/subcategories/<sub>/RULES.md`.
   Spezifischste Regeln (z.B. `befundberichte/RULES.md` mit
   ICD-Codes-Konventionen).

Bei Konflikt gewinnt die spezifischste Ebene, sofern sie nicht das
Cortex-Layer-Regelwerk **aufheben** will — Aufhebung ist nicht erlaubt,
nur **Verschärfung**.

## Anti-Patterns

- ❌ Patient-Daten direkt in `Input/` belassen, statt nach Verarbeitung
  ins `ARCHIV/` zu verschieben — `Input/` ist transient.
- ❌ `Output/`-Inhalte committen ins OSS-Repo — DSGVO-Verstoß. Live-
  Ordner sind gitignored.
- ❌ Vermischung von Medizin- und VSR-Vorgängen in einem Patienten-/
  Mandantenordner — die Top-Level-Trennung muss erhalten bleiben.
- ❌ Sub-Subkategorien direkt unter `Medizin/` oder `VSR/` (statt unter
  `_config/subcategories/`) — bricht die Schema-Erwartung von Tools,
  die nach Regel-Files suchen.
- ❌ Output-Dateinamen mit Diagnosen oder ICD-Codes — DSGVO.
