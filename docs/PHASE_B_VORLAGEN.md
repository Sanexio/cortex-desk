# Phase B.4 — öffentliche Vorlagen

Stand: 2026-09-26. Nach Nutzerentscheid werden die bisher zur Anlieferung
vorgesehenen Vorlagen aus dem vorhandenen Regelwerk als leere Schablonen
bereitgestellt. Keine privaten Bestände werden migriert.

## Umfang und Ableitung

| Dateien in `templates/` | Zweck / Grundlage |
|---|---|
| `briefkopf.md` | Zentrale Briefkopf-Slots nach PRAXIS_HEADER_EXAMPLE |
| `befundbericht.md` | Anamnese, Befund, Beurteilung, Therapie-Empfehlung nach WORKFLOW |
| `amtsanfrage-medizin.md` | Frage-Antwort-Struktur nach WORKFLOW |
| `amtsanfrage-steuer.md` | Sachverhalt, Fragen und Belege nach WORKFLOW |
| `vorgangspruefung.md` | Interne Quellen-, Freigabe- und Versandprüfung nach D-001 bis D-010 |
| `reha-erfassungsblatt.md`, `au-erfassungsblatt.md` | Interne Erfassung für die zusätzlich erwähnten Vorgangsarten |

Die drei Schreiben sind der konkret im Phase-B-Tracker benannte Kernumfang.
Reha/AU sind Erfassungsblätter, kein amtlicher Antrag, keine Bescheinigung und
kein Ersatz für das jeweils vorgesehene Formular oder elektronische Verfahren.
Konkrete Formularstände und Verfahren sind vor Nutzung im Tenant festzulegen.

Das [Vorlagenmanifest](vorlagen-manifest.json) führt alle Dateien. Das
Paketmanifest bleibt unverändert: K1, phi=false, selbsttest=null für das
Regelpaket; daraus folgt keine Einstufung späterer privater Vorgangsdaten.

## Slot-Konvention und Nutzung

1. Vorlage ausschließlich in den privaten Tenant kopieren. Alle Felder im
   Format `{{SLOT_NAME}}` sind Platzhalter, keine Beispielpersonen oder Daten.
2. `{{BRIEFKOPF}}` aus der zentralen Briefkopfvorlage beziehungsweise der
   privaten PRAXIS_HEADER-Konfiguration befüllen; Empfänger aus dem dortigen
   Adressbuch. Nur für den Vorgang erforderliche Angaben übernehmen.
3. Aussagen, Fristen und Kennungen ausschließlich aus geprüften Unterlagen
   übernehmen. Fehlende fachliche Angaben nach D-002 etwa als „aus den
   vorliegenden Unterlagen nicht ableitbar“ kennzeichnen. Fehlende
   Versandvoraussetzungen wie Empfänger oder Freigabe blockieren den Versand.
4. Wiederholte Fragen als eigene Frage-Antwort-Blöcke aufnehmen. Nicht
   einschlägige optionale Felder (etwa Aktenzeichen) nach Prüfung entfernen.
5. Quellen und Prüfnotizen getrennt in `vorgangspruefung.md` halten; dieses
   Blatt und die Reha/AU-Erfassungsblätter sind keine Versanddokumente.
6. Medizinische Inhalte ärztlich prüfen; steuerliche Inhalte durch die
   zuständige Rolle gemäß SUBWORKFLOWS prüfen lassen. Aus den Schablonen
   folgen keine Diagnosen, Empfehlungen, Bescheinigungen oder Rechtspositionen.
7. Vor Versand sämtliche Slots auflösen, Anlagen prüfen und Freigabe
   dokumentieren. Das Schreiben enthält keine Vorlagen-/Erstellungshinweise
   oder internen Notizen (D-003). Dateiname, Ablage und Archivierung folgen
   D-005/D-006/D-009, Sprache und Stil D-008.

Markdown folgt dem vorhandenen Schablonenbestand. Ein späteres Brieflayout
in DOCX/PDF muss im Tenant visuell geprüft werden; hier wird keine DIN-
Layoutkonformität behauptet. Public-Freigabe und Tenant-Migration sind
separate Schritte.
