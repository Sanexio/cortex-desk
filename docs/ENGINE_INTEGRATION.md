# Tooling-Integration — wie ein Tenant Werkzeuge anbindet

> Dieses Repo enthält Regelwerk, Vorlagen, freie Demos und
> ein Sync-Hilfsskript. Produktives proprietäres Tooling ist nicht enthalten.
> Tenants haben drei Optionen.

## Option 1: Sanexio-Tooling lizenzieren (empfohlen, wenn Sanexio-Tenant)

Wer Sanexio-Tenant ist, bekommt das Sanexio-Desk-Tooling-Bundle als
Teil des Tenant-Pakets. Das Bundle ist Teil der proprietären
Sanexio-Engine und besteht aus:

| Fähigkeit | Ein- und Ausgabe |
|---|---|
| Textextraktion und OCR | PDF/DOCX → Text mit Quellenbezug |
| Diagnosen-Erkennung | Befundtext → strukturierte Diagnosen |
| Berichtsvalidierung | Bericht → Prüfergebnis mit Fundstellen |
| PDF-Verarbeitung | PDFs → zusammengeführte oder getrennte Dokumente |
| Dateibenennung | Dokument und Metadaten → regelkonformer Dateiname |
| Verwaltungshilfen | Vorgangsdaten → strukturierte Arbeitsunterlagen |

Die konkrete Anbindung wird von der gewählten Engine dokumentiert.
Diese Beschreibung legt keine privaten Modulpfade oder Importnamen fest.

Cortex-CLI (geplant, Phase 3 der Cortex-Plattform-Roadmap):

```bash
cortex desk process --in Medizin/Input --subworkflow befundberichte
cortex desk validate Medizin/Output/<patient>/
cortex desk archive --auto   # alles abgeschlossene nach ARCHIV/
```

Die CLI-Befehle zeigen ein geplantes Schnittstellenschema und sind nicht
Teil dieses Repos. Die freie Demo läuft mit `bash examples/run-demo.sh`.

## Option 2: Eigenes Tooling bauen nach diesem Regelwerk

Wer keinen Sanexio-Vertrag hat, kann eigenes Tooling implementieren.
Das Regelwerk in `rules/` ist die normative Spezifikation.
Empfohlener Stack:

| Schicht | Library/Tool | Zweck |
|---|---|---|
| PDF-Textextraktion (nativ) | `pdfplumber` (Python) oder `PyMuPDF` | Text-Layer auslesen |
| OCR-Fallback | `tesseract` + `pytesseract` | Gescannte PDFs |
| Bildverarbeitung für OCR | `Pillow` | Pre-Processing |
| DOCX-Bearbeitung | `python-docx` oder direkter XML-Zugriff | Output-Dokument-Erzeugung |
| Validierung | eigene Regel-Skripte | Strukturprüfung gegen `CORE_RULES.md` |
| Sprache | Python ≥3.11 | Konsistenz mit allgemeinem Cortex-Stack |

Architektur-Skelett (Pseudo-Code für einen typischen Verarbeitungs-Workflow):

```python
from pathlib import Path

def process_input(input_path: Path, subworkflow: str, tenant_config: dict):
    """
    Generischer Verarbeitungs-Workflow gemäß rules/WORKFLOW.md Teil 2.
    """

    # 1. Sessionstart-Pflicht (D-001): Regeln in dieser Reihenfolge laden
    rules = load_rules_stack([
        "rules/CORE_RULES.md",                   # OSS
        "DESK.md",                               # Tenant-Steuerdokument
        "_rules/DESK_RULES.md",                  # Tenant-Regeln
        category_rules_for(subworkflow),         # Kategorie
        subcategory_rules_for(subworkflow),      # Sub
    ])

    # 2. Textextraktion (R-001-äquivalent für PDFs)
    text = extract_text(input_path)  # native → OCR-Fallback

    # 3. Strukturierung nach Vorgangs-Typ
    structured = structure_by_subworkflow(text, subworkflow)

    # 4. Validierung gegen D-002 (keine Erfindungen)
    assert_only_derivable_from_input(structured, text)

    # 5. Adressat-Sprache/Stil-Auswahl (D-008)
    adressat = determine_adressat(subworkflow, structured)
    style = tenant_config["sprache_stil_matrix"][adressat]

    # 6. Antwort-Erstellung
    output_doc = render_output(structured, style, tenant_config["praxis_header"])

    # 7. Meta-Check (D-003) — keine KI-/Template-Spuren
    assert_no_meta_comments(output_doc)

    # 8. Patientenordner-Check (D-005)
    target_dir = patient_folder_or_root(structured.patient, "Output/")

    # 9. Dateinamen-Konvention (D-006)
    filename = format_filename(
        structured.patient,
        date=structured.date,
        doctype=structured.doctype,
    )

    write_output(target_dir / filename, output_doc)

def archive_completed(category: Path):
    """D-009 Output-Lebenszyklus."""
    for vorgang in scan_completed(category / "Output"):
        move_to_archive(vorgang, category / "ARCHIV")
        move_to_archive(vorgang.original_input, category / "ARCHIV")
```

## Option 3: Manuelles Verfahren ohne Tooling

Wer eine kleine Praxis ohne Tooling-Bedarf führt, kann das Regelwerk
auch vollständig manuell anwenden:

- Word / LibreOffice / Pages für DOCX-Erstellung
- Eigener manueller Sessionstart-Check (Print-out der Regeln,
  Häkchen-Liste)
- Eigener manueller Archivierungs-Rhythmus (z.B. wöchentlich)
- Kalender-App für Frist-Tracking pro Sub-Workflow

In dem Fall ist dieses Repo hauptsächlich eine **Wissens-Quelle**
und ein Audit-Selbst-Check (Checklisten in `rules/WORKFLOW.md` und
`rules/CATEGORIES_EXAMPLE.md` ausdrucken und abhaken).

## Sanexio-Tooling-Lizenzierung (optional)

Wenn Tenants das Sanexio-Tooling-Bundle als Teil ihrer Plattform-
Anbindung nutzen wollen, gilt der Standard-Sanexio-Tenant-Vertrag.
Für Open-Source-Implementierungen ist dieses Regelwerk **frei nutzbar
unter Apache 2.0**.

Sanexio garantiert nicht, dass das eigene Tooling in jeder Praxis-
Umgebung lauffähig ist — das ist Teil des Tenant-Vertrags. Wer auf
sich selbst gestellt eigenes Tooling bauen will, hat hier die normative
Spec — das genügt für eine eigene robuste Implementierung.

## Schnittstellen zu anderen Cortex-Layer-Repos

- **cortex-rename** — `cortex-desk` kann `cortex-rename`-Konventionen
  für die Input-Sortierung nutzen, wenn Eingangs-Dokumente per
  Bulk-Scan ankommen und vor der Sichtung in `Input/` bereits
  vorklassifiziert werden sollen.
- **cortex-qm** — `cortex-desk`-Vorgänge im VSR-Bereich (Personal,
  Datenschutz, Brandschutz) verweisen oft auf QM-Dokumente
  (Schulungsnachweise, Datenschutz-Verfahrensanweisungen). Die
  Vernetzung läuft über Cross-Referenzen, nicht über Datei-Kopien
  (D-004-Prinzip: zentrale Quelle, kein Duplikat).
- **Praxiswebseiten-Theme** — wenn die Praxis-Webseite ein
  „Patient-Anfrage"-Formular hat, sollte dessen Output direkt ins
  `Medizin/Input/` oder `VSR/Input/` fließen (über eine sichere
  Mail- oder Portal-Schnittstelle), damit der Desk-Workflow ohne
  Medienbruch greift.
