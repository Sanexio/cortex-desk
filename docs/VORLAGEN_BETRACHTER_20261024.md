# Vorlagen-Betrachter — Cortex Desk (2026-10-24)

## Ausgangslage

Prüfbefund CD (`CD_PRUEFUNG_EINZELAPPS.md`, Abschnitt Cortex Desk): Der Vorlagen-Tab listete nur Manifest-Einträge ohne Datei-Viewer.

## Umsetzung

- **Backend (Rust):** Tauri-Befehl `vorlagen_read` liefert `VorlageInhalt` (`format`, optional `text`, optional `pdf_base64`). Erlaubnisliste: nur Pfade unter `templates/` mit Endung `.md`, `.txt`, `.pdf`, kein `..`, kanonische Prüfung gegen den Vorlagenordner.
- **Frontend:** Modul `app/src/vorlagen-betrachter.ts` — zweispaltige Liste + Vorschau, Suche, Kopieren in die Zwischenablage, Umschaltung Quelltext/Vorschau für Markdown, PDF per eingebetteter Blob-URL.
- **Design:** bestehende Themes Praxis 2025 / Cyberpunk (`themes.css`, Erweiterungen `.vorlagen-*`, `.md-preview`).
- **Tests:** `cargo test` in `desk_content` (Pfadflucht, Lesen), Vitest `vorlagen-betrachter.test.ts` und `markdown-preview`.

## Nicht im Scope

- Kein Zugriff auf `Desk/`, Tenant-Daten, Vault oder Terminal-Fenster.
- Schreiben oder Bearbeiten von Vorlagen in der App — nur lesen.

## Verifikation

```bash
cd app && npm test
cd app/src-tauri && cargo test
cd app && npm run build
```
