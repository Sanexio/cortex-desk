mod app_meta;
mod basis;
mod cortex_start;
mod desk_content;
mod lizenzanzeige;
mod schluessel;

use serde::Serialize;
use tauri_plugin_updater::UpdaterExt;

use crate::desk_content::{RuleEntry, VorlageEntry};

#[derive(Serialize)]
struct AppInfo {
    version: String,
    app_id: String,
    bundle_id: String,
    klasse: String,
}

#[tauri::command]
fn app_info() -> AppInfo {
    AppInfo {
        version: app_meta::VERSION.into(),
        app_id: app_meta::APP_ID_STR.into(),
        bundle_id: app_meta::BUNDLE_ID.into(),
        klasse: "K0".into(),
    }
}

#[tauri::command]
fn rules_list() -> Result<Vec<RuleEntry>, String> {
    lizenzanzeige::require_access()?;
    desk_content::rules_list()
}

#[tauri::command]
fn rules_read(pfad: String) -> Result<String, String> {
    lizenzanzeige::require_access()?;
    desk_content::rules_read(&pfad)
}

#[tauri::command]
fn vorlagen_list() -> Result<Vec<VorlageEntry>, String> {
    lizenzanzeige::require_access()?;
    desk_content::vorlagen_list()
}

#[tauri::command]
fn vorlagen_read(pfad: String) -> Result<String, String> {
    lizenzanzeige::require_access()?;
    desk_content::vorlagen_read(&pfad)
}

#[tauri::command]
fn lizenz_ueberblick() -> lizenzanzeige::LicenseOverview {
    lizenzanzeige::ueberblick()
}

#[tauri::command]
async fn updater_check(app: tauri::AppHandle) -> Result<Option<String>, String> {
    // Exact private repository; the public verification key is compiled into this app.
    let builder = app
        .updater_builder()
        .endpoints(vec![tauri::Url::parse(
            "https://api.github.com/repos/Sanexio/cortex-desk/releases/latest",
        )
        .map_err(|e| e.to_string())?])
        .map_err(|e| e.to_string())?;
    let updater = builder.build().map_err(|e| e.to_string())?;
    match updater.check().await {
        Ok(Some(update)) => Ok(Some(update.version.clone())),
        Ok(None) => Ok(None),
        Err(e) => Err(e.to_string()),
    }
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_updater::Builder::new().build())
        .setup(|app| {
            cortex_start::beim_start(app.handle())?;
            Ok(())
        })
        .invoke_handler(tauri::generate_handler![
            app_info,
            rules_list,
            rules_read,
            vorlagen_list,
            vorlagen_read,
            lizenz_ueberblick,
            updater_check
        ])
        .run(tauri::generate_context!())
        .expect("Cortex Desk konnte nicht starten");
}
