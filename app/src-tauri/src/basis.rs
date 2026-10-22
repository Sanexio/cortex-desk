use std::path::PathBuf;

use cortex_app_core::standard_basis;

pub fn cortex_basis() -> Result<PathBuf, String> {
    standard_basis().ok_or_else(|| "Cortex-Datenordner nicht ermittelbar".into())
}
