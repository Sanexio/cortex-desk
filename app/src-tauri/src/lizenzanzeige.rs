use crate::basis::cortex_basis;
use chrono::Local;
use cortex_app_core::{darf_starten, lade_lizenz, Lizenz, LizenzFehler, Startentscheid};
use serde::Serialize;
use std::path::PathBuf;

use crate::app_meta::{app_id, KLASSE};
use crate::schluessel::oeffentlich_bytes;

#[derive(Debug, Serialize)]
pub struct LicenseOverview {
    pub state: String,
    pub gebucht: bool,
    pub hinweis: String,
}

fn heute() -> chrono::NaiveDate {
    Local::now().date_naive()
}

pub fn lizenz_laden() -> Result<Lizenz, LizenzFehler> {
    lade_lizenz(
        &cortex_basis().map_err(|e| LizenzFehler::Format(e))?,
        &oeffentlich_bytes(),
        heute(),
    )
}

pub fn ueberblick() -> LicenseOverview {
    let basis = cortex_basis().unwrap_or_else(|_| PathBuf::from("."));
    match lizenz_laden() {
        Ok(lizenz) => {
            let app = app_id();
            match darf_starten(Ok(&lizenz), &app, KLASSE) {
                Startentscheid::Erlaubt => LicenseOverview {
                    state: "valid".into(),
                    gebucht: true,
                    hinweis: format!(
                        "Lizenz für Mandant {} gültig bis {} — App gebucht.",
                        lizenz.tenant_id,
                        lizenz.gueltig_bis
                    ),
                },
                Startentscheid::NichtGebucht => LicenseOverview {
                    state: "not_booked".into(),
                    gebucht: false,
                    hinweis:
                        "Signierte Lizenz vorhanden, aber cortex-desk nicht gebucht. Inhalte bleiben bis zur Freischaltung gesperrt. Freischaltung über Marketplace-Lizenz.".into(),
                },
                Startentscheid::ObergrenzeZuNiedrig { klasse, obergrenze } => LicenseOverview {
                    state: "obergrenze".into(),
                    gebucht: false,
                    hinweis: format!(
                        "Lizenz-Obergrenze {obergrenze:?} reicht nicht für App-Klasse {klasse:?}."
                    ),
                },
                Startentscheid::KeineLizenz(err) => LicenseOverview {
                    state: "error".into(),
                    gebucht: false,
                    hinweis: err.to_string(),
                },
            }
        }
        Err(LizenzFehler::NichtGefunden) => LicenseOverview {
            state: "unconfigured".into(),
            gebucht: false,
            hinweis: format!(
                "Keine Lizenzdatei unter {}. Freischaltung über eine signierte Lizenz ohne Zahlung erforderlich.",
                cortex_app_core::lizenz_pfad(&basis).display()
            ),
        },
        Err(e) => LicenseOverview {
            state: "invalid".into(),
            gebucht: false,
            hinweis: e.to_string(),
        },
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn ueberblick_liefert_status() {
        let o = ueberblick();
        assert!(!o.hinweis.is_empty());
        assert!(matches!(
            o.state.as_str(),
            "unconfigured" | "not_booked" | "valid" | "invalid" | "obergrenze" | "error"
        ));
    }
}

/// Every content command must pass the compiled app identity/class and signature check.
pub fn require_access() -> Result<(), String> {
    let lizenz = lizenz_laden()
        .map_err(|_| "Nicht gebucht: signierte Freischaltung erforderlich".to_string())?;
    check_access(Ok(&lizenz))
}

fn check_access(lizenz: Result<&Lizenz, &LizenzFehler>) -> Result<(), String> {
    match darf_starten(lizenz, &app_id(), KLASSE) {
        Startentscheid::Erlaubt => Ok(()),
        _ => Err("Nicht gebucht: signierte Freischaltung oder Obergrenze reicht nicht".into()),
    }
}

#[cfg(test)]
mod angriff {
    use super::*;
    use base64::{engine::general_purpose::STANDARD, Engine};
    use cortex_app_core::{pruefe_lizenz, signiere_nutzlast, AppId, Klasse};
    use ed25519_dalek::SigningKey;
    #[test]
    fn echte_signierte_nutzlast_und_angriffe_am_app_gate() {
        let key = SigningKey::from_bytes(&[41; 32]);
        let public = key.verifying_key().to_bytes();
        let today = chrono::NaiveDate::from_ymd_opt(2026, 10, 22).unwrap();
        let mut lizenz = Lizenz {
            tenant_id: "synthetisch-ba2".into(),
            ausgestellt: today,
            gueltig_bis: today,
            apps: vec![app_id()],
            obergrenze: Klasse::K3,
            geraet: None,
        };
        let bytes = signiere_nutzlast(&lizenz, &key.to_bytes()).unwrap();
        let verified = pruefe_lizenz(&bytes, &public, today);
        assert!(check_access(verified.as_ref()).is_ok());
        let other = SigningKey::from_bytes(&[42; 32]).verifying_key().to_bytes();
        assert!(check_access(pruefe_lizenz(&bytes, &other, today).as_ref()).is_err());
        assert!(
            check_access(pruefe_lizenz(&bytes, &public, today.succ_opt().unwrap()).as_ref())
                .is_err()
        );
        lizenz.apps = vec![AppId::neu("andere-app").unwrap()];
        let bytes = signiere_nutzlast(&lizenz, &key.to_bytes()).unwrap();
        assert!(check_access(pruefe_lizenz(&bytes, &public, today).as_ref()).is_err());
        let mut envelope: serde_json::Value = serde_json::from_slice(&bytes).unwrap();
        let mut payload: serde_json::Value = serde_json::from_slice(
            &STANDARD
                .decode(envelope["nutzlast"].as_str().unwrap())
                .unwrap(),
        )
        .unwrap();
        payload["apps"] = serde_json::json!([crate::app_meta::APP_ID_STR]);
        payload["obergrenze"] = serde_json::json!("K3");
        envelope["nutzlast"] = STANDARD
            .encode(serde_json::to_vec(&payload).unwrap())
            .into();
        assert!(check_access(
            pruefe_lizenz(&serde_json::to_vec(&envelope).unwrap(), &public, today).as_ref()
        )
        .is_err());
        assert!(AppId::neu("harness").is_err());
    }
}
