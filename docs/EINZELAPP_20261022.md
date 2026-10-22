# Einzel-App Cortex Desk (2026-10-22)

## Auftrag

Native Tauri-2-Einzelapp für `cortex-desk` auf Zweig `einzelapp-20261022`, Marketplace-Manifest, lauffähiger unsignierter Build, Tests grün.

## Gebaut

| Baustein | Ort | Zweck |
|----------|-----|--------|
| Tauri 2 + Vite/TS | `app/` | Eigenständiges Programm `Cortex Desk`, Bundle-ID `de.sanexio.cortex-desk`, Version 0.1.0 |
| `cortex-app-core` | Pfadabhängigkeit in `app/src-tauri/Cargo.toml` | Andock-Manifest, signierte Lizenzprüfung (öffentlicher Schlüssel zur Build-Zeit) |
| UI | `app/src/` | Regelwerk-Katalog (`rules/*.md`), Vorlagenmanifest, Lizenz-/Update-Status |
| Design | `app/src/themes.css`, `theme.ts` | **Praxis 2025** (Default) und **Cyberpunk** (`cyber-dark`) umschaltbar |
| Marketplace | `marketplace/app.json` + `icon.png` / `icon-qr.png` | Katalog-Metadaten für den Cortex-Marketplace |
| Lizenz-Stub | `app/schluessel/lizenz-oeffentlich.txt` | Ed25519-Öffentlichkeit (wie Nexus Marketplace); keine Zahlung, Freischaltung über signierte `lizenz.json` |
| Updater-Stub | `tauri-plugin-updater` + Platzhalter-Feed in `tauri.conf.json` | Manuelle Prüfung im UI; Artefakt-Signierung aus (Codex/Beglaubigung offen) |

### Funktionsumfang v0.1.0

- Lesender Zugriff auf das **öffentliche Regelwerk** im Repo (`rules/`, Pfad-Allowlist).
- Anzeige der **Phase-B-Vorlagen** aus `docs/vorlagen-manifest.json` (nur Metadaten, Platzhalter-Templates).
- Beim Start: **Andock-Manifest** unter `~/Library/Application Support/Cortex/apps/cortex-desk.json` (macOS).
- **Kein** Zugriff auf `Desk/`, ARCHIV, TOSORT-Pipeline oder Tenant-Daten — das Harness-Plugin bleibt separat.

### Build (lokal, unsigniert)

```sh
cd app
npm ci
npm run build
npm exec tauri build
```

Ergebnis (macOS): `app/src-tauri/target/release/bundle/macos/Cortex Desk.app`

### Tests

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest discover -s tests -t tests
cd app && npm test
cd app/src-tauri && cargo test
```

## Noch offen (bewusst nicht in diesem Zweig)

- **Code-Signing / Notarisierung** (macOS) und Windows-Signatur — Auftrag Codex.
- **Minisign-Update-Schlüssel** und echter Update-Feed (aktuell Platzhalter-URL + `REPLACE_WITH_MINISIGN_PUBLIC_KEY`).
- **TOSORT-/Dashboard-Plugin** als eingebetteter Dienst (benötigt ARCHIV und Harness; K3-Nähe).
- **Nexus-Brücke** (Cargo-Feature wie App-Template) — nicht aktiviert.
- **CI** (GitHub Actions, drei OS) — folgt Marketplace-Welle.
- Symbol **Sanexio-QR**: `marketplace/icon-qr.png` ist vorerst dieselbe Rastergrafik wie `icon.png`; dedizierte QR-Markenvariante durch Design/Codex.

## Referenzen

- `Nexus/specs/app-marketplace/00_KONZEPT.md`, `02_CORTEX_APP_DESIGN.md`
- `Nexus/_rules/design-theme.md`
- Vorlage: `projects/cortex-tenant-template/app-template/`, `projects/cortex-app-core`
