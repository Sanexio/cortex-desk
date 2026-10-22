# C8 — Betriebsprotokolle

Produkt: **cortex-desk**. Vertrag: `marketplace/logging-c8.json`.

Die native Lizenzentscheidung verwendet `cortex_app_core::darf_starten` und
`audit::write_entry`: exakt `timestamp` (Unix-Sekunden), `event` (`license_check`),
`outcome` (`allowed`/`denied`). Keine Freitexte, Namen, Mandanten-/Personal-/
Patientenkennungen, Dateipfade, URLs, Zugangsdaten, Fehlermeldungen oder Inhalte.
Zusätzliche Schlüssel und unbekannte Werte werden abgewiesen, nicht übernommen.

Die App legt keine Betriebsprotokoll-Dateien an (Aufbewahrung: 0 Sekunden).
Der lokale stderr-Strom ist nur für die laufende Diagnose bestimmt. Keine automatische
Support-Übertragung, Telemetrie, Crash-Uploads oder Screenshots. Support erhält
nur einen ausdrücklich angeforderten Auszug aus `audit::support_excerpt(input, now)`:
maximal 24 Stunden alte Erlaubnislisten-Ereignisse; unbekannte Felder, ungültige Werte,
Zukunftszeiten und ältere Einträge brechen den Auszug ab. Auszüge spätestens nach
24 Stunden verwerfen; Rohprotokolle sind kein Supportweg. Prozess-/Betriebssystem-
Absturzberichte gehören nicht zu diesem Auszug und dürfen nicht automatisch exportiert werden.

Fachliche Verlaufstabellen, Veröffentlichungsprotokolle und Arbeitszeit-Audits sind
Anwendungsdaten, keine Betriebsprotokolle. Sie werden unverändert lokal geführt;
diese Regel erlaubt weder Datenkorrekturen noch deren Einsicht oder Support-Export.

Fehlt-Prüfer (vor jedem Neubau/Release):
`python3 <cortex-app-core>/scripts/check-c8.py --app <dieses-Repository>`.
Der Prüfer kontrolliert Vertrag, tatsächliche Core-Abhängigkeit, den nativen
Entscheidungspfad und unstrukturierte native Diagnoseausgaben. Er ersetzt keine
Laufzeitprüfung beliebiger Bibliotheken oder Betriebssystemberichte.

BA2-Bundles enthalten diese neue C8-Grenze erst nach erneutem Bau und Verteilung.
