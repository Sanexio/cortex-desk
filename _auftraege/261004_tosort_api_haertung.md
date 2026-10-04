# AUFTRAG: TOSORT-Plugin-API gegen DNS-Rebinding/fehlende Authentisierung haerten (Review 20:10)

Auftraggeber: Nexus-KI. Umsetzung: Codex.
Arbeitsverzeichnis: ~/Cortex/projects/cortex-desk (NUR hier).

Gleicher Befund wie beim Kalkulations-Plugin: plugins/tosort/dashboard/
plugin_api.py meldet missing-authentication / DNS-rebinding.

AUFGABE: In dashboard_plugin/plugin_api.py alle Endpunkte (auch die
Status-GETs) mit strikter Host-Header-Erlaubnisliste (127.0.0.1[:port],
localhost[:port]) absichern — fremder/fehlender Host -> 403; vorher das
bestehende Schutzmuster des Dashboard-Servers/anderer Plugins messen und
ihm folgen; existiert ein serverseitiger Schutz bereits, Fehlalarm mit
Datei:Zeile belegen statt doppelt zu bauen. Der Start-Endpunkt bleibt
zusaetzlich standardmaessig deaktiviert. Negativtests wie ueblich
(fremder Host -> 403, kein Prozessstart, keine Interna in Antworten).

NACHWEIS: 16er-Suite + neue Tests gruen, dist falls betroffen neu.
Kein Commit. Bericht als Abschnitt "Haertung Host-Check" an
_auftraege/261004_tosort_plugin_vsr_ERGEBNIS.md.
