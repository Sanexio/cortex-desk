# Workflow — Sub-Workflows und generischer Verarbeitungsgang

Zwei Ebenen:

1. **Sub-Workflow-Übersicht** — neun konkrete Bausteine, die in einer
   typischen Praxis-Verwaltungsschicht ansetzen.
2. **Generischer Verarbeitungsgang** — die Schritte, die jeder
   Sub-Workflow durchläuft (Vor-, Während-, Nach-Bearbeitung).

---

## Teil 1: Sub-Workflow-Übersicht

| Sub-Workflow | Hauptort | Output-Typ | Primär-Adressat |
|---|---|---|---|
| Befundbericht-Erstellung | `Medizin/Input` | strukturierter Befundbericht | Arzt / MDK |
| Amtsanfrage Medizin | `Medizin/Input` | Antwortschreiben mit medizinischer Stellungnahme | Behörde (<behoerde> etc.) |
| Amtsanfrage Steuer | `VSR/Input` | Antwortschreiben Finanzamt | Finanzamt |
| Verwaltung Personal | `VSR/Input` | Personalvorgangs-Antwort (Vertrag, Zeugnis, Mahnung) | Mitarbeiter, KV/Sozialversicherung |
| Verwaltung Mietvertrag | `VSR/Input` | Mietsachen-Antwort | Vermieter, Verwalter |
| Verwaltung KV | `VSR/Input` | Antwort an Kassenärztliche Vereinigung / PVS | KV, PVS |
| Recht Anwaltskorrespondenz | `VSR/Input` | Anwaltsbrief / Stellungnahme | Anwalt, Gericht |
| Recht Datenschutz | `VSR/Input` | DSGVO-Antwort (Auskunft, Löschung, Beschwerde) | Patient, Aufsichtsbehörde |
| Recht Gesellschaftsrecht | `VSR/Input` | GbR-/MVZ-/PartG-Antwort | Mitgesellschafter, Notar |

Jeder Sub-Workflow hat eigene RULES.md + FEHLERPROTOKOLL.md +
WORKFLOW_CHECKLIST.md unter `<Kategorie>/_config/subcategories/<sub>/`.
Beispiel-Inhalte: `CATEGORIES_EXAMPLE.md`.

### Proprietäre Skill-Trigger (Tenant-spezifisch)

Für Tenants kann es zu jedem Sub-Workflow ein Cortex-Skill
mit dem Schema `desk:<sub-workflow-kurzform>`, z.B.:

```
desk:befundberichte
desk:amtsanfragen-medizin
desk:amtsanfragen-steuer
desk:verwaltung-personal
desk:verwaltung-mietvertrag
desk:verwaltung-kv
desk:recht-anwaltskorrespondenz
desk:recht-datenschutz
desk:recht-gesellschaftsrecht
```

Die Skill-Trigger-Mechanik selbst ist Teil der proprietären
Sanexio-Engine. Eigene
Implementierungen können äquivalente Trigger über andere
Plattformen (Slack, Telegram, CLI, Web-UI) bauen. Das Regelwerk hier
ist Skill-Trigger-agnostisch.

---

## Teil 2: Generischer Verarbeitungsgang

Jeder Sub-Workflow durchläuft im Kern dieselben Phasen.

### Vor dem Vorgang

1. **Sessionstart-Pflicht D-001** erfüllen:
   - Tenant-`DESK.md` gelesen?
   - `CORE_RULES.md` gelesen?
   - Tenant-`_rules/DESK_RULES.md` gelesen?
   - Kategorie- und Subkategorie-RULES.md geladen?
   - Aktuelle FEHLERPROTOKOLL.md-Stände gesichtet?

2. **Input-Verifikation:**
   - Liegt eine vollständige Eingangs-Datei in `<Kategorie>/Input/`?
   - Ist das Format verarbeitbar (PDF nativ / PDF gescannt / DOCX /
     Bild / Mail-Anhang)? OCR-Fallback benötigt?
   - Ist der Vorgangs-Typ klar (Befundbericht? Amtsanfrage? KV-
     Mitteilung?) — wenn nicht, vor Verarbeitung klären, nicht raten
     (D-002).

3. **Adressat bestimmt:** auf welche Sprache/Stil-Zeile aus D-008
   wird abgebildet? Bei Mischformen (Schreiben an Patient mit Kopie
   an Krankenkasse): primären Adressaten festlegen + Stil-Anpassung
   für Kopie dokumentieren.

### Während des Vorgangs

1. **Textextraktion** der Input-Dokumente (Tooling-Aufruf, siehe
   `docs/ENGINE_INTEGRATION.md`):
   - native PDF-Textebene zuerst
   - OCR-Fallback bei leerem oder unvollständigem Ergebnis
   - Fachterminus-Validierung (medizinisch / steuerrechtlich / juristisch)

2. **Strukturierung** des extrahierten Inhalts nach Vorgangs-Typ:
   - Befundbericht: Anamnese, Befund, Beurteilung, Therapie-
     Empfehlung
   - Amtsanfrage: Aktenzeichen, Fragen-Liste, Antwort-Schema
   - Steuersache: Bezug-Aktenzeichen, Sachverhalts-Würdigung,
     Beweismittel
   - Anwaltskorrespondenz: Rubrum, Sachverhalt, Anträge,
     Beweis-Angebot

3. **Antwort-Erstellung** unter Beachtung von:
   - D-002 (keine Erfindungen — alle Aussagen aus Input ableitbar)
   - D-003 (keine Meta-Kommentare)
   - D-008 (Sprache/Stil nach Adressat)

4. **Patientenordner-Check (D-005)**: existieren bereits
   Output-Dateien für diesen Patient/Mandanten? Wenn ja: Ordner
   anlegen (bei Schritt von 1 auf 2), Dateinamen nach D-006.

5. **Validierung** (optional, je nach Tenant-Tooling):
   - vollständige Adress-Block, vollständige Anrede, Aktenzeichen
   - Stil-Check gegen D-008
   - Inhalts-Vollständigkeitsprüfung (alle Fragen einer
     Amtsanfrage beantwortet?)
   - Sicherheitscheck auf Patient-Daten, die nicht durchgereicht
     werden dürfen

### Nach dem Vorgang

1. **Ausgangskontrolle**:
   - Praxisinhaber-Freigabe vor Versand (außer bei eindeutig
     mfa-delegierbaren Vorgängen, siehe Tenant-Delegations-Regelung)
   - Sicht-Check auf alle Items aus der Subkategorie-Checkliste

2. **Versand / Print**:
   - Mail / Behörden-Portal / Print + Briefumschlag — nach
     Adressat-Präferenz
   - Versand-Datum + Versand-Kanal dokumentieren (entweder im
     Output-Dokument selbst oder in einer Versand-Liste)

3. **Archivierung (D-009)**:
   - Original aus `Input/` nach `ARCHIV/` verschieben
   - Output-Datei(en) aus `Output/` nach `ARCHIV/` verschieben
   - `ARCHIV/`-Struktur spiegelt `Output/`-Struktur (Patientenordner-
     Konvention bleibt erhalten)

4. **Wissens-Rückfluss**:
   - Neue Fehler-Klasse erkannt? → Eintrag in passender
     `FEHLERPROTOKOLL.md` mit ID, Beschreibung, Ursache, Wirkung
   - Daraus abgeleitete Regel formuliert? → Eintrag in passender
     `RULES.md`
   - Prüfpunkt in `WORKFLOW_CHECKLIST.md` ergänzt
   - Tenant-spezifische Lehre (Adressat-Präferenz, häufige Frage-
     Form einer bestimmten Behörde): → `*_TENANT.md`

## Empfohlene Frequenz

- **Sofort-Vorgänge** (Notfall-Befundbericht, Fristen-kritische
  Amtsanfrage): nach Eingang, ohne Sammelpunkt
- **Tägliche Sichtung** des `Input/`-Stands aller aktiven Kategorien
- **Wöchentliche Verarbeitungs-Slots** für Routine-Vorgänge (KV-
  Mitteilungen, Personalvorgänge)
- **Monatliche Archiv-Welle**: `Output/` → `ARCHIV/` für alle
  abgeschlossenen Vorgänge

## Notfall: Eingangs-Dokument enthält schwere Mängel

Wenn die Input-Datei Mängel hat, die eine vollständige Bearbeitung
verhindern (unleserlich, abgeschnitten, Adressat unklar, Antrag fehlt):

1. **NICHT raten oder interpolieren** — D-002.
2. Rückfrage an den Einsender / Aussteller dokumentieren.
3. Vorgang bleibt in `Input/` mit `_PENDING`-Suffix bis zur Klärung.
4. Eintrag im Fehlerprotokoll, falls die Mangel-Klasse häufiger
   auftritt (Pattern erkennbar → Tenant-Vorlage anpassen?
   Behörden-Schreiben-Vorlage zurückspielen?).
