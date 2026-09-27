# Adressaten-Liste — Beispiel-Schablone

> **Demo-Schablone**, nicht echte Praxis-Daten. Tenants kopieren diese
> Datei nach `ADRESSATEN_TENANT.md` (gitignored) und tragen dort ihre
> echten Adressaten ein. `ADRESSATEN_TENANT.md` wird NIE committed —
> sie enthält teilweise personenbezogene Daten (Sachbearbeiter-Namen,
> Steuerberater, Anwälte) und Behörden-Aktenzeichen-Konventionen.

## Struktur eines Adressaten-Eintrags

```
### <Adressat-Schlüssel>
- **Vollname:** <Behörde / Person / Firma>
- **Anschrift:** <Straße + PLZ + Ort>
- **Kontakt:** <Telefon / Mail / Behörden-Portal-URL>
- **Aktenzeichen-Schema:** <wenn die Stelle ein eigenes AZ-Format führt>
- **Sprache/Stil:** <Verweis auf D-008 Matrix-Zeile>
- **Anrede-Konvention:** <Sehr geehrte … / An die … / Herrn Direktor …>
- **Bevorzugter Versandweg:** <Mail / Brief / Behörden-Portal>
- **Antwort-Frist-Standard:** <ggf. typische Frist dieses Adressaten>
- **Notizen:** <Praxis-spezifische Hinweise>
```

## Beispiele

### PSEUDO-<BEHOERDE>
- **Vollname:** Pseudo-<behoerde> Demo-Land
- **Anschrift:** Pseudo-Straße 1, 99999 Pseudo-Stadt
- **Kontakt:** behoerde@pseudo.example
- **Aktenzeichen-Schema:** `VA-<Jahr>-<6-stellige-Nummer>`
- **Sprache/Stil:** D-008 Zeile „<behoerde>" — Fokus auf
  funktionelle Einschränkungen
- **Anrede-Konvention:** „Sehr geehrte Damen und Herren,"
- **Bevorzugter Versandweg:** Brief mit Empfangsbekenntnis
- **Antwort-Frist-Standard:** 4 Wochen ab Anfrage-Datum
- **Notizen:** Antwortet auf eMail nur, wenn ausdrücklich gewünscht.

### PSEUDO-MDK
- **Vollname:** Pseudo-Medizinischer Dienst Demo-Region
- **Anschrift:** Pseudo-Allee 100, 99999 Pseudo-Stadt
- **Aktenzeichen-Schema:** `MD-<Jahr>-<Buchstabe>-<5-stellige-Nr>`
- **Sprache/Stil:** D-008 Zeile „Arzt/MDK" — internistisch präzise,
  ICD-Codes zulässig
- **Anrede-Konvention:** „Sehr geehrte Frau Kollegin, sehr geehrter
  Herr Kollege,"
- **Bevorzugter Versandweg:** Behörden-Portal
- **Antwort-Frist-Standard:** 2 Wochen
- **Notizen:** Bei MDK-Befund-Anforderung NIE Diagnose-Liste ohne
  funktionelle Würdigung — sonst Rückfrage.

### PSEUDO-FINANZAMT
- **Vollname:** Pseudo-Finanzamt Demo-Stadt
- **Anschrift:** Pseudo-Steuer-Allee 1, 99999 Pseudo-Stadt
- **Aktenzeichen-Schema:** Steuernummer 999/9999/9999 +
  Vorgangs-AZ je Anfrage
- **Sprache/Stil:** D-008 Zeile „Finanzamt" — steuerrechtlich präzise,
  Paragraphen vollständig
- **Anrede-Konvention:** „Sehr geehrte Damen und Herren,"
- **Bevorzugter Versandweg:** ELSTER-Portal / Brief
- **Antwort-Frist-Standard:** Frist aus konkretem Anschreiben
  (oft 4 Wochen)
- **Notizen:** Steuerberater PSEUDO-StB-1 hat Vollmacht — Kopie
  immer beilegen.

### PSEUDO-KV
- **Vollname:** Pseudo-Kassenärztliche-Vereinigung Demo-Land
- **Anschrift:** Pseudo-KV-Straße 1, 99999 Pseudo-Stadt
- **Aktenzeichen-Schema:** KV-Honorarnummer 9999 + Quartal Q?/JJ
- **Sprache/Stil:** D-008 Zeile „Krankenkasse" (analog für KV) —
  Fachsprache mit Erklärungen
- **Anrede-Konvention:** „Sehr geehrte Damen und Herren,"
- **Bevorzugter Versandweg:** KV-Portal / Brief
- **Antwort-Frist-Standard:** je nach Mitteilungs-Typ
- **Notizen:** Quartalsabrechnung-Plausibilitätsprüfung: immer mit
  Anlagen-Verzeichnis antworten.

### PSEUDO-STB
- **Vollname:** PSEUDO-Steuerberater (Demo-Kanzlei)
- **Anschrift:** Pseudo-Wirtschaftsweg 5, 99999 Pseudo-Stadt
- **Kontakt:** stb@pseudo.example
- **Sprache/Stil:** D-008 Zeile „Finanzamt" (analog) —
  steuerrechtlich präzise
- **Anrede-Konvention:** „Sehr geehrter Herr <Name>,"
- **Bevorzugter Versandweg:** Mail mit verschlüsseltem Anhang
- **Notizen:** Vollmacht-Beilage für alle Finanzamt-Korrespondenz.

### PSEUDO-ANWALT
- **Vollname:** PSEUDO-Rechtsanwalt (Demo-Kanzlei)
- **Sprache/Stil:** D-008 Zeile „Gericht/Anwalt" — sachlich-formal
- **Anrede-Konvention:** „Sehr geehrter Herr Kollege," (wenn Anwalt
  Vertrauenskreis), sonst „Sehr geehrter Herr <Name>,"
- **Notizen:** Mandant-Vorgangs-Daten NIE per unverschlüsselter Mail.

### PSEUDO-VERMIETER
- **Vollname:** PSEUDO-Vermietungsverwaltung
- **Aktenzeichen-Schema:** Mietvertrags-AZ
- **Sprache/Stil:** D-008 Zeile „Geschäftspartner" — sachlich,
  formgebunden
- **Anrede-Konvention:** „Sehr geehrte Damen und Herren,"

## Anti-Pattern

❌ Privatadressen von Sachbearbeitern (außer geschäftliche Mail).
❌ Inoffizielle Kontaktwege (private Mobilnummern) — nicht im
   Versandweg dokumentieren, auch wenn sie genutzt werden.
❌ Bewertungen / Sachbearbeiter-Charakterisierungen („nett",
   „streng") — gehört in interne Notizen, nicht ins Adressbuch.
❌ Patient-Daten in Adressaten-Notizen.

## Hinweise zur Pflege

- Bei Wechsel des Sachbearbeiters: Aktualisierung des Eintrags
  innerhalb von 1 Woche.
- Bei Aktenzeichen-Schema-Änderung der Behörde: Workflow-Checklist
  des betroffenen Sub-Workflows ergänzen.
- Bei neuem Adressaten-Typ (z.B. neue Aufsichtsbehörde nach
  Gesetzes-Änderung): zusätzliche D-008-Zeile in
  `_TENANT.md`-Ergänzung dokumentieren.
