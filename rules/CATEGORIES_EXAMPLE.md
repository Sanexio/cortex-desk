# Sub-Subkategorien — Beispiel-Inhalte

> **Demo-Hinweise**, nicht echte Praxis-Daten. Tenants füllen ihre
> konkreten Inhalte in den `_config/subcategories/<sub>/RULES.md`
> ein, ergänzt um die praxis-spezifischen oder praxis-eigenen
> Spezifika. Konkrete Patient-/Mandanten-Bezüge gehören NICHT ins
> OSS-Repo, sondern bleiben im jeweiligen Tenant.

## Struktur eines Subkategorie-Eintrags

```
### <Subkategorie-Name>

**Hauptort:**          <Pfad in der Arbeitsumgebung>
**Output-Typ:**        <Was wird erzeugt>
**Primär-Adressat:**   <Wer bekommt das Ergebnis>
**Pflicht-Inhalte:**   <Was muss zwingend im Output stehen>
**Optionale Inhalte:** <Was hängt vom Vorgang ab>
**Regulatorische Anker:** <Gesetze/Richtlinien, die hier greifen>
**Typische Fehler-IDs:** <Schema z.B. MED-CAT-001, MAF-001, …>
```

---

## Medizin/befundberichte

**Hauptort:** `Medizin/Input/`

**Output-Typ:** strukturierter Befundbericht in einheitlichem Format
(Markdown / DOCX / PDF; Tenant entscheidet)

**Primär-Adressat:** Arzt / MDK

**Pflicht-Inhalte:**
- Vollständiger Praxis-Header (Tenant-File `PRAXIS_HEADER_TENANT.md`)
- Patient-Block (Name, Geburtsdatum, ggf. Versicherungs-Nr — nur
  soweit für den Adressaten erforderlich)
- Anamnese (aus Input-Dokumenten ableitbar — D-002)
- Befund (klinisch, ggf. Laborwerte mit Einheiten + Referenzbereich)
- Beurteilung (in Fachsprache — D-008)
- Therapie-Empfehlung (sofern Aufgabe des Berichts)
- ICD-10-Codes (im Adressaten-Bereich Arzt/MDK zulässig — D-008)

**Optionale Inhalte:**
- Vorbefunde-Zusammenfassung
- Verlaufs-Skizze über mehrere Vorstellungen

**Regulatorische Anker:** ärztliche Berufsordnung,
ICD-10-GM (BfArM)

**Typische Fehler-IDs:** `MED-CAT-001` Patientenordner-Konvention
verletzt, `MED-CAT-002` ICD-Code nicht aus Input ableitbar
(D-002-Verstoß)

---

## Medizin/amtsanfragen

**Hauptort:** `Medizin/Input/`

**Output-Typ:** Antwortschreiben an Behörde (<behoerde>, MDK,
Gesundheitsamt) mit medizinischer Stellungnahme

**Primär-Adressat:** Behörde (mit Patient-Kopie nach Anfrage-Typ)

**Pflicht-Inhalte:**
- Aktenzeichen der Behörden-Anfrage (im Header und in jedem
  Absatz-Bezug, sofern nötig)
- Vollständige Anrede + Adressbezug
- Beantwortung **jeder einzelnen** Frage der Anfrage in derselben
  Reihenfolge wie im Anschreiben (<behoerde>-Standard)
- Fokus auf **funktionelle Einschränkungen** (D-008 <behoerde>-
  Zeile), nicht auf reine Diagnose-Liste
- Datums-Abgrenzung (seit wann, bis wann, Verlauf)

**Optionale Inhalte:**
- Hinweis auf weitere noch ausstehende Befunde
- Hinweis auf laufende Verfahren bei anderen Behörden

**Regulatorische Anker:** SGB IX (<behoerde>),
SGB V §275 (MDK), IfSG (Gesundheitsamt)

**Typische Fehler-IDs:** `MAF-001` Aktenzeichen fehlt im Header,
`MAF-002` Frage übersprungen, `MAF-003` Diagnose-Liste statt
funktioneller Beschreibung

---

## VSR/verwaltung/kv-mitteilungen

**Hauptort:** `VSR/Input/`

**Output-Typ:** Antwort an KV / PVS (Quartalsabrechnung, Honorar-
Anpassung, Plausibilitätsprüfung)

**Primär-Adressat:** Kassenärztliche Vereinigung / PVS

**Pflicht-Inhalte:**
- KV-/PVS-Aktenzeichen oder Honorarnummern-Bezug
- Vollständiger Praxis-Header
- Bezug zur konkreten Mitteilung (Datum, Betreff)
- Antwort-Inhalt strikt zu den gestellten Punkten

**Optionale Inhalte:**
- Anhang mit Belegen / Quartalsstatistik

**Regulatorische Anker:** SGB V §75, KV-Satzungen, EBM

**Typische Fehler-IDs:** `VSR-KV-001` Honorarnummer fehlt, …

---

## VSR/verwaltung/mietvertrag

**Hauptort:** `VSR/Input/`

**Output-Typ:** Mietsachen-Korrespondenz (Anpassung Nebenkosten,
Verlängerungs-Option, Mängelanzeige, Verhandlungs-Korrespondenz)

**Primär-Adressat:** Vermieter, Verwaltung

**Pflicht-Inhalte:**
- Praxis-Header
- Mietvertrags-Bezug (Datum, Objekt-Bezeichnung)
- Sachverhalt, Antrag/Bitte, Frist

**Optionale Inhalte:**
- Anhang Bestandsaufnahme bei Mängelanzeige

**Regulatorische Anker:** BGB §535 ff., Gewerberaummietrecht

**Typische Fehler-IDs:** `VSR-MIET-001` Frist fehlt, …

---

## VSR/verwaltung/personal

**Hauptort:** `VSR/Input/`

**Output-Typ:** Personalvorgangs-Antwort (Vertrag, Arbeitszeugnis,
Abmahnung, Kündigung, Auflösungsvertrag)

**Primär-Adressat:** Mitarbeiter, ggf. KV/Sozialversicherung

**Pflicht-Inhalte:**
- Praxis-Header
- Vollständiger Name + Personalnummer (sofern vergeben)
- Vertrags-/Beschäftigungs-Bezug
- Datums-Angabe(n)
- Bei Zeugnis: Vollständigkeitsgrad, Wohlwollens-Prinzip, korrekte
  Notation

**Optionale Inhalte:**
- Anhang Lohnsteuerbescheinigung

**Regulatorische Anker:** BGB §§611a ff., NachwG, KSchG, BetrVG (bei
Praxen mit BR ungewöhnlich, aber denkbar)

**Typische Fehler-IDs:** `VSR-PERS-001` …

---

## VSR/steuer/amtsanfragen-steuer

**Hauptort:** `VSR/Input/`

**Output-Typ:** Antwortschreiben an Finanzamt (Anfragen zu
Einkommen, Betriebsvermögen, Privatentnahmen, Umsatzsteuer)

**Primär-Adressat:** Finanzamt

**Pflicht-Inhalte:**
- Steuernummer / IDNr-Bezug
- Aktenzeichen der Anfrage
- Vollständige Anrede an die Behörde (Sachbearbeiter sofern bekannt)
- **Steuerrechtlich präzise Sprache mit vollständigen
  Paragraphen** (D-008 Finanzamt-Zeile)
- Anlagen-Verzeichnis

**Optionale Inhalte:**
- Hinweis auf eingeschalteten Steuerberater (Vollmacht beifügen)

**Regulatorische Anker:** AO, EStG, UStG, GewStG, HGB

**Typische Fehler-IDs:** `VSR-FA-001` Steuernummer fehlt im Header,
`VSR-FA-002` umgangssprachliche Formulierung statt Paragraph

---

## VSR/recht/anwaltskorrespondenz

**Hauptort:** `VSR/Input/`

**Output-Typ:** Anwaltsbrief, Stellungnahme an Gericht, Klageerwiderung

**Primär-Adressat:** Anwalt, Gericht

**Pflicht-Inhalte:**
- Vollständiges Rubrum bei Gerichts-Korrespondenz
- Aktenzeichen
- Sachverhalt, sachlich-formal, ohne Wertung
- Anträge (sofern angebracht)
- Beweis-Angebote

**Optionale Inhalte:**
- Anlagen mit Anlagen-Verzeichnis (K1, K2, … nach Klage-
  Konvention)

**Regulatorische Anker:** ZPO, BGB, je nach Sachverhalt
spezifische Bereiche (z.B. BGB §823, BÄO, MBO-Ä)

**Typische Fehler-IDs:** `VSR-ANW-001` Rubrum unvollständig, …

---

## VSR/recht/datenschutz

**Hauptort:** `VSR/Input/`

**Output-Typ:** DSGVO-Antwort (Auskunft Art. 15, Berichtigung
Art. 16, Löschung Art. 17, Beschwerde-Stellungnahme)

**Primär-Adressat:** Patient (bei Auskunft/Berichtigung/Löschung),
Aufsichtsbehörde (bei Beschwerde)

**Pflicht-Inhalte:**
- Vollständige Anrede
- Bezug zur konkreten Anfrage (Datum, Inhalt)
- DSGVO-Artikel-Bezug
- Frist-Wahrung (Auskunft: 1 Monat; Verlängerung um 2 Monate möglich
  bei Begründung)
- Bei Beschwerde an Aufsichtsbehörde: vollständige Sachverhalts-
  Darstellung + ggf. Stellungnahme zu Vorwurf

**Optionale Inhalte:**
- Anhang Patientenakten-Ausdruck (bei Auskunfts-Antrag)

**Regulatorische Anker:** DSGVO Art. 12-22, BDSG

**Typische Fehler-IDs:** `VSR-DS-001` Frist überschritten ohne
Begründung, …

---

## VSR/recht/gesellschaftsrecht

**Hauptort:** `VSR/Input/`

**Output-Typ:** GbR-/MVZ-/PartG-/MB-Korrespondenz (Gesellschafter-
beschluss, Vertragsänderung, Aufnahme/Austritt, Notar-
Korrespondenz)

**Primär-Adressat:** Mitgesellschafter, Notar, ggf. Steuerberater

**Pflicht-Inhalte:**
- Bezug zum Gesellschaftsvertrag (Datum, ggf. notarielle URNr)
- Tagesordnung bei Beschluss-Vorlagen
- Beschluss-Wortlaut
- Stimmen-Erfordernis (einstimmig / Mehrheit / qualifizierte
  Mehrheit nach Vertrag)

**Optionale Inhalte:**
- Anhang Liquiditäts-Berechnung bei Aufnahme/Austritt
- Anhang aktuelle Bilanz / GuV

**Regulatorische Anker:** BGB (GbR), PartGG (PartG), MVZG / Ärzte-
ZV (MVZ), GmbHG (selten in der Praxis)

**Typische Fehler-IDs:** `VSR-GR-001` Tagesordnung fehlt, …

---

## Anti-Pattern: Was NICHT in dieses OSS-Repo gehört

❌ Konkrete Patient-Namen aus Befundberichten oder Amtsanfragen.
❌ Konkrete Mandanten- oder Gegner-Namen aus Anwaltskorrespondenz.
❌ Konkrete Steuernummern, Aktenzeichen, Honorarnummern einer
   einzelnen Praxis.
❌ Vermieter-/Verwalter-Adressen, Vertragsdaten.
❌ Tatsächliche Personalnummern oder MFA-Namen.
❌ Konkrete Anwaltskanzleien, Steuerberater, Notare einer einzelnen
   Praxis (Liste gehört ins Tenant-Adressbuch
   `ADRESSATEN_TENANT.md`).

All das gehört in die **Tenant-Files** oder ins jeweilige
Tenant-Repo. Pseudo-Beispiele werden im OSS-Repo NICHT durch
echte Daten ersetzt.
