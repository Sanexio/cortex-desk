fn lese_oeffentlich_pfad() -> Option<String> {
    if let Ok(p) = std::env::var("CORTEX_LIZENZ_OEFFENTLICH_DATEI") {
        if !p.trim().is_empty() {
            return Some(p);
        }
    }
    let manifest = std::path::Path::new(env!("CARGO_MANIFEST_DIR"));
    let kandidaten = [
        manifest.join("../../schluessel/lizenz-oeffentlich.txt"),
        manifest.join("../../../../Nexus/specs/app-marketplace/schluessel/lizenz-oeffentlich.txt"),
    ];
    for k in kandidaten {
        if k.is_file() {
            return Some(k.to_string_lossy().into_owned());
        }
    }
    None
}

fn parse_hex_32(hex: &str) -> Result<[u8; 32], String> {
    let hex = hex.trim();
    if hex.len() != 64 || !hex.bytes().all(|b| b.is_ascii_hexdigit()) {
        return Err("öffentlicher Schlüssel muss 64 Hex-Zeichen haben".into());
    }
    let mut out = [0u8; 32];
    for i in 0..32 {
        out[i] = u8::from_str_radix(&hex[i * 2..i * 2 + 2], 16)
            .map_err(|e| format!("Hex ungültig: {e}"))?;
    }
    Ok(out)
}

fn main() {
    let profile = std::env::var("PROFILE").unwrap_or_default();
    let pfad = lese_oeffentlich_pfad();
    let hex = match pfad {
        Some(p) => std::fs::read_to_string(&p)
            .map_err(|e| format!("Lizenz-Öffentlichkeit nicht lesbar ({p}): {e}"))
            .and_then(|t| parse_hex_32(&t).map(|b| (b, t.trim().to_string()))),
        None if profile == "debug" => {
            eprintln!(
                "WARNUNG: Kein Lizenz-Öffentlichkeitspfad — Debug-Build mit Nullschlüssel (nur Tests)."
            );
            Ok(([0u8; 32], String::new()))
        }
        None => Err(
            "Release-Build ohne CORTEX_LIZENZ_OEFFENTLICH_DATEI oder app/schluessel/lizenz-oeffentlich.txt"
                .into(),
        ),
    };

    let (bytes, hex_str) = hex.expect("Lizenz-Öffentlichkeit für Build");
    let joined = bytes
        .iter()
        .map(|b| b.to_string())
        .collect::<Vec<_>>()
        .join(",");
    println!("cargo:rustc-env=CORTEX_LIZENZ_OEFFENTLICH_BYTES={joined}");
    println!("cargo:rustc-env=CORTEX_LIZENZ_OEFFENTLICH_HEX={hex_str}");
    tauri_build::build();
}
