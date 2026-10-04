# AUFTRAG: TOSORT-Oberflaeche als Dashboard-Plugin unter VSR (Nutzer 19:44)

Auftraggeber: Dr. Stracke via Nexus-KI. Umsetzung: Codex.
Arbeitsverzeichnis: ~/Cortex/projects/cortex-desk (NUR hier schreiben).
Desk/_skills/archiv-tosort/ und Nexus NUR LESEN.

## ZIEL
Der TOSORT-Algorithmus (Ablage-Pipeline, SKILL.md + Skripte unter
~/Cortex/Desk/_skills/archiv-tosort/) soll im Cortex-Dashboard (:9119)
unter der Sektion VSR bedienbar werden — bisher existiert dafuer
keinerlei Route/Plugin (gemessen heute 18:00).

## AUFGABE
1. Schritt 0: Pipeline verstehen (SKILL.md, scripts/, read-only) und die
   Plugin-Konventionen messen (Vorbild cortex-ledger/dashboard_plugin:
   manifest, plugin_api.py, src->dist via build.mjs).
2. Erstfassung dashboard_plugin/ in DIESEM Repo: (a) Statusansicht —
   Zaehler der TOSORT-Eingangsbecken, aelteste Datei (nur Alter, kein
   Name), letzte Lauf-Zeit aus vorhandenen Logs/Zustandsdateien (lesen);
   (b) Knopf "TOSORT-Lauf starten", der den BESTEHENDEN Pipeline-
   Einstieg ausfuehrt (kein neuer Algorithmus) mit Laufstatus-Anzeige
   nach Ledger-Vorbild; (c) Manifest mit Route /tosort, Bereich vsr.
3. WICHTIG: echte Praxisdokumente — die UI zeigt NUR Aggregate (Zaehler,
   Alter, Status), keine Dateinamen, keine Inhalte, keine Patientendaten.
   Fail-closed: ohne lesbaren Zustand "nicht messbar" anzeigen.
4. Aktivierungspaket fuer die Nexus-KI dokumentieren (Dateien -> Nexus/
   plugins/tosort/..., noetiges Harness-Mapping /tosort: vsr). NICHT
   aktivieren, nichts ausserhalb dieses Repos schreiben.

## NACHWEIS
Tests fuer die Statuslogik (Fixtures, KEINE Echtdaten), DOM-Nachweis,
Suite-Summenzeile falls Suite existiert. Kein Commit. Bericht:
_auftraege/261004_tosort_plugin_vsr_ERGEBNIS.md.
