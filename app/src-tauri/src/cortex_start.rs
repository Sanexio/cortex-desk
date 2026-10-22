use crate::basis::cortex_basis;
use cortex_app_core::{schreibe_manifest, AndockManifest, Startziel};
use tauri::AppHandle;

use crate::app_meta::{app_id, BUNDLE_ID, KLASSE, PRODUKTNAME, VERSION};

pub fn andock_manifest_schreiben() -> Result<(), String> {
    let manifest = AndockManifest {
        id: app_id(),
        name: PRODUKTNAME.into(),
        version: VERSION.into(),
        klasse: KLASSE,
        start: Startziel::MacBundle {
            bundle_id: BUNDLE_ID.into(),
        },
        symbol: None,
    };
    schreibe_manifest(&cortex_basis()?, &manifest)
        .map_err(|e| format!("Andock-Manifest nicht schreibbar: {e}"))?;
    Ok(())
}

pub fn beim_start(_app: &AppHandle) -> Result<(), String> {
    andock_manifest_schreiben()?;
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    use cortex_app_core::lies_manifeste;
    use std::fs;

    #[test]
    fn manifest_roundtrip() {
        let dir = std::env::temp_dir().join(format!("cortex-desk-andock-{}", uuid_simple()));
        fs::create_dir_all(&dir).unwrap();
        let basis = dir.join("basis");
        fs::create_dir_all(&basis).unwrap();
        // standard_basis uses env - test schreibe_manifest directly
        let manifest = cortex_app_core::AndockManifest {
            id: crate::app_meta::app_id(),
            name: "Cortex Desk".into(),
            version: "0.1.0".into(),
            klasse: crate::app_meta::KLASSE,
            start: cortex_app_core::Startziel::MacBundle {
                bundle_id: crate::app_meta::BUNDLE_ID.into(),
            },
            symbol: None,
        };
        schreibe_manifest(&basis, &manifest).expect("schreiben");
        let gelesen = lies_manifeste(&basis);
        assert_eq!(gelesen.len(), 1);
        let _ = fs::remove_dir_all(&dir);
    }

    fn uuid_simple() -> String {
        use std::time::{SystemTime, UNIX_EPOCH};
        SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_nanos()
            .to_string()
    }
}
