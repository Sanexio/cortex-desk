# Sub-Workflow-Anpassungen — Beispiel-Schablone

> **Demo-Schablone**, nicht echte Praxis-Daten. Tenants kopieren diese
> Datei nach `SUBWORKFLOWS_TENANT.md` (gitignored) und tragen dort
> ihre praxis-spezifischen Sub-Workflow-Anpassungen ein.
>
> **Worum geht's:** das OSS-`WORKFLOW.md` definiert neun Sub-Workflows
> in generischer Form. Jede Praxis hat aber individuelle Spezifika
> (Welche MFA macht welchen Schritt? Wer gibt frei? Welche
> Hausregeln gelten beim Befundbericht-Versand? Wie ist die Eskalations-
> kette bei einer Datenschutz-Anfrage?). Diese Anpassungen leben hier,
> NICHT im OSS-Repo.

## Struktur eines Sub-Workflow-Eintrags

```
### <Sub-Workflow-Name>

**Verantwortlich (Lead):**  <Rolle, ggf. konkrete Person aus PERSONAL>
**Freigabe vor Versand:**   <Praxisinhaber / delegierte MFA mit Vollmacht>
**Häufigste Adressaten:**   <Verweis auf ADRESSATEN_TENANT.md-Einträge>
**Praxis-Hausregeln:**      <was diese Praxis hier individuell handhabt>
**Eskalations-Kette:**      <wer bei Unsicherheit gefragt wird>
**Frist-Konvention:**       <typische Bearbeitungsdauer dieser Praxis>
**Übergabeprotokoll:**      <wie wird der Vorgang im ARCHIV vermerkt>
```

## Beispiele

### befundberichte

- **Verantwortlich (Lead):** PSEUDO-MFA-1 für Erstextraktion;
  behandelnder Arzt für Beurteilung und Therapie-Empfehlung
- **Freigabe vor Versand:** behandelnder Arzt persönlich
- **Häufigste Adressaten:** PSEUDO-MDK, PSEUDO-Kassenarzt-Kollegen
  (Konsiliarrückbericht)
- **Praxis-Hausregeln:**
  - Befundbericht innerhalb von 7 Werktagen nach Patient-Kontakt
  - Vorbefunde IMMER als separates Dokument im Patientenordner
  - ICD-Codes nur bei Adressat MDK/Arzt, nicht bei Patient-Kopie
- **Eskalations-Kette:** Mit-Inhaber bei medizinischer Unsicherheit
  vor Freigabe konsultieren
- **Frist-Konvention:** 7 Werktage Standard
- **Übergabeprotokoll:** im Patientenordner unter ARCHIV mit
  Versand-Datum als Filename-Suffix

### amtsanfragen-medizin

- **Verantwortlich (Lead):** PSEUDO-MFA-2 für Erst-Sichtung +
  Aktenzeichen-Vermerk; behandelnder Arzt für Stellungnahme
- **Freigabe vor Versand:** behandelnder Arzt
- **Häufigste Adressaten:** PSEUDO-<behoerde>, PSEUDO-MDK,
  PSEUDO-Gesundheitsamt
- **Praxis-Hausregeln:**
  - Antworten an <behoerde> IMMER mit Empfangsbekenntnis-Brief
  - MDK-Antworten über Behörden-Portal
  - Bei laufendem Widerspruchsverfahren: Anwalt PSEUDO-ANWALT-1 in
    Kopie
- **Eskalations-Kette:** geschäftsführender Partner bei
  haftungs-/budget-relevanten Fragen
- **Frist-Konvention:** Behörden-Frist immer einhalten, Standard
  4 Wochen
- **Übergabeprotokoll:** Aktenzeichen + Versanddatum im
  Patientenordner

### amtsanfragen-steuer

- **Verantwortlich (Lead):** Steuerberater PSEUDO-StB-1 (extern)
  hat Vollmacht; intern PSEUDO-MFA-3 für Vorgangs-Sichtung
- **Freigabe vor Versand:** Steuerberater PSEUDO-StB-1
- **Häufigste Adressaten:** PSEUDO-Finanzamt
- **Praxis-Hausregeln:**
  - JEDE Finanzamt-Anfrage wird direkt an PSEUDO-StB-1 weitergeleitet
  - Praxis erstellt nur Sachverhalts-Notiz, nicht die Antwort selbst
  - Anlagen-Sammlung intern in `VSR/Input/<Aktenzeichen>/`
- **Frist-Konvention:** Finanzamt-Frist + 1 Woche Puffer für StB
- **Übergabeprotokoll:** Aktenzeichen + StB-Antwort-Datum

### verwaltung-personal

- **Verantwortlich (Lead):** geschäftsführender Partner
- **Freigabe vor Versand:** geschäftsführender Partner;
  bei Zeugnis: zusätzlich Praxis-Mit-Inhaber
- **Häufigste Adressaten:** Mitarbeiter, KV-Sozialversicherung,
  Bundesagentur für Arbeit
- **Praxis-Hausregeln:**
  - Arbeitszeugnis-Erstellung intern, nicht ausgelagert
  - Standard-Formulierung „qualifiziertes Zeugnis" beachten
    (Geheimcode-Vermeidung)
  - Kündigungen IMMER mit Anwalt PSEUDO-ANWALT-2 vor Versand
- **Eskalations-Kette:** Anwalt PSEUDO-ANWALT-2 bei
  arbeitsrechtlicher Unsicherheit
- **Frist-Konvention:** Zeugnisse innerhalb von 4 Wochen nach
  Austritt

### verwaltung-mietvertrag

- **Verantwortlich (Lead):** geschäftsführender Partner
- **Freigabe vor Versand:** geschäftsführender Partner
- **Häufigste Adressaten:** PSEUDO-Vermieter, PSEUDO-Verwaltung
- **Praxis-Hausregeln:**
  - Nebenkosten-Anpassung mit Steuerberater vorbesprechen
  - Mängelanzeige IMMER mit Foto-Dokumentation als Anhang
  - Mietvertrags-Verlängerungs-Option: Vorlauf 6 Monate vor
    Frist-Ablauf

### verwaltung-kv

- **Verantwortlich (Lead):** PSEUDO-MFA-1 für Erst-Sichtung,
  geschäftsführender Partner für Antwort
- **Freigabe vor Versand:** geschäftsführender Partner
- **Häufigste Adressaten:** PSEUDO-KV, PSEUDO-PVS
- **Praxis-Hausregeln:**
  - Quartalsabrechnung-Plausibilitätsprüfung: immer mit
    EBM-Ziffern-Vergleich
  - Bei Honorar-Rückforderung: 4-Wochen-Antwort, ggf. Widerspruch
- **Frist-Konvention:** KV-Frist + 3 Tage Puffer

### recht-anwaltskorrespondenz

- **Verantwortlich (Lead):** geschäftsführender Partner
- **Freigabe vor Versand:** geschäftsführender Partner
- **Häufigste Adressaten:** PSEUDO-ANWALT-1 (Allgemein),
  PSEUDO-ANWALT-2 (Arbeitsrecht), Gerichte
- **Praxis-Hausregeln:**
  - Direkter Anwalt-Mandat-Mailverkehr verschlüsselt
  - Gerichts-Korrespondenz immer mit Rubrum-Prüfung
  - Mandant-Daten NIE per unverschlüsselter Mail

### recht-datenschutz

- **Verantwortlich (Lead):** Datenschutzbeauftragter (intern oder
  extern PSEUDO-DSB)
- **Freigabe vor Versand:** Datenschutzbeauftragter +
  geschäftsführender Partner
- **Häufigste Adressaten:** Patient (Auskunft / Berichtigung /
  Löschung), Aufsichtsbehörde (Beschwerde)
- **Praxis-Hausregeln:**
  - Auskunfts-Antrag: 1-Monats-Frist tracken
  - Aufsichtsbehörde-Beschwerde: 4-Augen-Prinzip vor Antwort
  - Bei Datenpanne: SOFORT Meldepflicht nach Art. 33 DSGVO prüfen
    (72-Stunden-Frist)

### recht-gesellschaftsrecht

- **Verantwortlich (Lead):** geschäftsführender Partner
- **Freigabe vor Versand:** ALLE Mitgesellschafter
  (Gesellschafterversammlung)
- **Häufigste Adressaten:** Mitgesellschafter, PSEUDO-Notar,
  PSEUDO-StB-1
- **Praxis-Hausregeln:**
  - Gesellschafterbeschluss-Vorlage: 2 Wochen Vorlauf
  - Notarielle Beurkundung: PSEUDO-Notar standardmäßig
  - Steuerliche Implikationen: PSEUDO-StB-1 vor Beschluss einbinden

## Anti-Pattern

❌ Sub-Workflow-Hausregeln, die das OSS-Regelwerk
   **aufheben** wollen (z.B. „bei uns wird auf Sessionstart-Pflicht
   verzichtet") — Verschärfung erlaubt, Aufhebung nicht.
❌ Praxis-Interne Eskalations-Ketten mit Namen einer einzelnen
   Person ins OSS-Repo schreiben — gehört in Tenant.
❌ Konkrete Sachbearbeiter-Eigenarten („antwortet nur per Fax",
   „mag keine Listen-Form") — gehört in Tenant-Notizen oder
   `ADRESSATEN_TENANT.md`.

## Hinweise zur Pflege

- Bei Wechsel der Verantwortlichkeit: Eintrag aktualisieren UND
  Personal-Liste (`PERSONAL_TENANT.md` falls vorhanden) abgleichen.
- Bei Wechsel des externen Steuerberaters / Anwalts: Eintrag UND
  `ADRESSATEN_TENANT.md` aktualisieren.
- Neue Hausregel aus Fehler-Ereignis: zuerst Eintrag im
  `FEHLERPROTOKOLL_TENANT.md`, dann Regel hier ergänzen, dann
  WORKFLOW_CHECKLIST.md prüfen.
