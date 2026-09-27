# Examples

Dieses Verzeichnis enthält fiktive Demo-Artefakte für das
`cortex-desk`-Regelwerk. Es zeigt exemplarisch, wie eine Verarbeitung
für Extraktion, simulierte OCR, Diagnose-Erkennung und Validierung
aussehen kann.

Alle Inhalte sind frei erfunden. Namen, Praxis, Ort und medizinische
Angaben sind Demo-Daten und dürfen nicht als reale Patientendaten
verstanden werden.

## Start

```bash
bash examples/run-demo.sh
```

Der Runner führt die Pipeline unter `examples/befund-pipeline-demo/`
end-to-end aus:

1. `ocr_step.py` liest eine Text-Fixture und simuliert OCR inklusive
   fiktivem Confidence-Wert.
2. `extract.py` strukturiert Diagnosen, ICD-10-Codes, Medikation sowie
   Absender-/Empfänger-Rollen in `befund.json`.
3. `validate.py` prüft das Ergebnis gegen einfache Plausibilitätsregeln
   mit Bezug auf die Regelstruktur in `rules/`.

## Pseudo-Engine

Diese Demo ist keine produktive Engine und ersetzt kein echtes
medizinisch-administratives Tooling. Sie nutzt nur `python3`-Stdlib und
arbeitet ausschließlich mit fiktiven Textdaten.

Das echte Tooling-Bundle für produktive Sanexio-Tenants ist Teil des
Sanexio-Tenant-Vertrags. Details stehen in
`docs/ENGINE_INTEGRATION.md`.

