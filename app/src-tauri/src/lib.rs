use cortex_app_updates as updates;
mod app_meta;
mod basis;
mod cortex_start;
mod desk_content;
mod lizenzanzeige;
mod schluessel;

use serde::Serialize;

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


#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_updater::Builder::new().build())
        .manage(updates::UpdateSpeicher::default())
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
            updates::update_status,
        updates::update_pruefen,
        updates::update_installieren
        ])
        .run(tauri::generate_context!())
        .expect("Cortex Desk konnte nicht starten");
}
