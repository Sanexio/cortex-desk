# Praxis-Briefkopf — Beispiel-Schablone

> **Demo-Schablone**, nicht echte Praxis-Daten. Tenants kopieren diese
> Datei nach `PRAXIS_HEADER_TENANT.md` (gitignored) und tragen dort
> ihren tatsächlichen Briefkopf ein.

## Struktur

Jedes Output-Dokument hat einen Briefkopf, der aus zwei Blöcken
besteht:

1. **Absender-Block** (Praxis-Identität)
2. **Empfänger-Block** (aus `ADRESSATEN_TENANT.md` befüllt)

Gefolgt von Vorgangs-Block (Datum, Aktenzeichen, Betreff).

## Absender-Block — Demo

```
Pseudo-Praxiszentrum Demo-Stadt
Dr. med. PSEUDO-Inhaber
und PSEUDO-Praxispartner

Pseudo-Straße 99
99999 Pseudo-Stadt

Tel.:  +49 99 999 99 99
Fax:   +49 99 999 99 90
Mail:  praxis@pseudo.example
Web:   https://praxis.pseudo.example
```

### Optionale Zusatzfelder

- **KV-Honorarnummer** — bei KV-Mitteilungs-Korrespondenz oben rechts
- **Steuernummer + USt-IdNr** — bei Finanzamt-Korrespondenz Pflicht
  (Briefkopf-Fuß)
- **Berufsbezeichnung** ärztliche Approbation laut Berufsordnung
- **Datenschutzbeauftragter-Kontakt** — empfohlen bei DSGVO-
  Korrespondenz

## Empfänger-Block — Demo

Aus `ADRESSATEN_TENANT.md` automatisch oder manuell einfügen:

```
Pseudo-<behoerde> Demo-Land
- Sachbearbeiter Herrn/Frau PSEUDO -
Pseudo-Straße 1
99999 Pseudo-Stadt
```

## Vorgangs-Block

Direkt unter dem Empfänger-Block:

```
                                          99999 Pseudo-Stadt, 2026-04-13

Aktenzeichen: VA-2026-099999
Ihr Anschreiben vom: 2026-03-15

Betreff: Stellungnahme an <behoerde> — Patient/in PSEUDO
```

## Layout-Regeln

- **DIN 5008** (Geschäftsbrief-Norm) als Default-Layout
- Schriftart: serife oder sans-serife Standard-Schrift, keine
  Schmuck-Schriften
- Schriftgrad 11–12 pt Standard, Briefkopf evtl. 10 pt
- Falt- und Lochmarken nach DIN 5008
- Anschriftenfeld im Sichtfenster eines DIN-lang-Umschlags

## Logo-Konvention

- Logo im Briefkopf oben rechts oder oben mittig
- Vektor-Format (SVG oder hochauflösendes PNG)
- Tenant-spezifisch — gehört in `<tenant-repo>/desk/assets/logo.*`
- KEIN Logo im OSS-Repo

## Signatur-Block

Am Ende des Briefes:

```
Mit freundlichen kollegialen Grüßen

(Unterschrift PSEUDO-Inhaber)

Dr. med. PSEUDO-Inhaber
```

Bei Mehr-Personen-Praxis: Unterzeichner-Person je nach Vorgangs-
Typ (medizinische Sachen: behandelnder Arzt; rechtliche Sachen:
geschäftsführender Partner; Standard-Schreiben: MFA-Unterschrift mit
Vollmacht-Vermerk „i.A.").

## Anti-Pattern

❌ Logo aus Word-Vorlage mit Pixel-Klötzchen — beim Empfänger
   schlechter Eindruck.
❌ Briefkopf-Variante, die im Sichtfenster nicht der Anschrift
   entspricht — Brief geht zurück.
❌ Mehrere Briefkopf-Varianten je Mitarbeitender — Layout-Drift.
   Eine zentrale Vorlage, alle anderen referenzieren.
❌ Patient-bezogene Informationen im Briefkopf-Bereich (gehört in
   den Vorgangs-Block, nicht in den Header).

## Hinweise zur Pflege

- Bei Adress-/Telefon-Änderung: zentrale Tenant-Vorlage aktualisieren
  + alle Sub-Workflow-Templates regenerieren
- Bei neuer Approbation / neuer Partner-Aufnahme: Berufsbezeichnungs-
  Liste aktualisieren
- Briefkopf-Logo nur über Tenant-Asset-Pfad einbinden, nie inline-
  base64 im Markdown
