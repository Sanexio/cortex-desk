use std::path::PathBuf;
use chrono::Local;
use cortex_app_core::{darf_starten, lade_lizenz, Lizenz, LizenzFehler, Startentscheid};
use crate::basis::cortex_basis;
use serde::Serialize;

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
    lade_lizenz(&cortex_basis().map_err(|e| LizenzFehler::Format(e))?, &oeffentlich_bytes(), heute())
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
                        "Signierte Lizenz vorhanden, aber cortex-desk nicht gebucht. Regelwerk-Katalog bleibt lesbar (K0). Freischaltung über Marketplace-Lizenz.".into(),
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
                "Keine Lizenzdatei unter {}. K0-Regelwerk ist ohne Zahlung nutzbar; signierte Freischaltung für Marketplace-Andocken optional.",
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
