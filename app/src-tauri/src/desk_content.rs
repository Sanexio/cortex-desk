use std::fs;
use std::path::{Path, PathBuf};

use base64::{engine::general_purpose::STANDARD, Engine};
use serde::Serialize;

#[derive(Debug, Serialize, Clone)]
pub struct RuleEntry {
    pub pfad: String,
    pub titel: String,
}

#[derive(Debug, Serialize, Clone)]
pub struct VorlageEntry {
    pub pfad: String,
    pub phase: String,
    pub typ: String,
}

fn repo_root() -> PathBuf {
    let manifest = PathBuf::from(env!("CARGO_MANIFEST_DIR"));
    manifest.join("../..")
}

fn erlaubt_regel(rel: &str) -> bool {
    if rel.contains("..") || rel.starts_with('/') {
        return false;
    }
    rel.starts_with("rules/") && rel.ends_with(".md")
}

fn erlaubt_vorlage(rel: &str) -> bool {
    if rel.contains("..") || rel.starts_with('/') {
        return false;
    }
    if !rel.starts_with("templates/") {
        return false;
    }
    let lower = rel.to_ascii_lowercase();
    lower.ends_with(".md") || lower.ends_with(".txt") || lower.ends_with(".pdf")
}

fn vorlage_format(rel: &str) -> Option<&'static str> {
    let lower = rel.to_ascii_lowercase();
    if lower.ends_with(".md") {
        Some("markdown")
    } else if lower.ends_with(".txt") {
        Some("text")
    } else if lower.ends_with(".pdf") {
        Some("pdf")
    } else {
        None
    }
}

fn canonical_unter_templates(full: &Path) -> Result<PathBuf, String> {
    let canonical = full.canonicalize().map_err(|e| e.to_string())?;
    let templates_canon = repo_root()
        .join("templates")
        .canonicalize()
        .map_err(|e| e.to_string())?;
    if !canonical.starts_with(&templates_canon) {
        return Err("Pfad ausserhalb des Vorlagenordners".into());
    }
    Ok(canonical)
}

#[derive(Debug, Serialize, Clone)]
pub struct VorlageInhalt {
    pub format: String,
    pub text: Option<String>,
    pub pdf_base64: Option<String>,
}

pub fn rules_list() -> Result<Vec<RuleEntry>, String> {
    let rules_dir = repo_root().join("rules");
    if !rules_dir.is_dir() {
        return Err("Regelwerk-Ordner nicht gefunden".into());
    }
    let mut out = Vec::new();
    for entry in fs::read_dir(&rules_dir).map_err(|e| e.to_string())? {
        let entry = entry.map_err(|e| e.to_string())?;
        let path = entry.path();
        if !path.is_file() {
            continue;
        }
        let name = path.file_name().and_then(|n| n.to_str()).unwrap_or("");
        if !name.ends_with(".md") || name.contains("TENANT") {
            continue;
        }
        let rel = format!("rules/{name}");
        let titel = name.trim_end_matches(".md").replace('_', " ");
        out.push(RuleEntry { pfad: rel, titel });
    }
    out.sort_by(|a, b| a.pfad.cmp(&b.pfad));
    Ok(out)
}

pub fn rules_read(pfad: &str) -> Result<String, String> {
    if !erlaubt_regel(pfad) {
        return Err("Pfad nicht erlaubt".into());
    }
    let full = repo_root().join(pfad);
    let canonical = full.canonicalize().map_err(|e| e.to_string())?;
    let rules_canon = repo_root()
        .join("rules")
        .canonicalize()
        .map_err(|e| e.to_string())?;
    if !canonical.starts_with(&rules_canon) {
        return Err("Pfad ausserhalb des Regelwerks".into());
    }
    fs::read_to_string(&canonical).map_err(|e| e.to_string())
}

pub fn vorlagen_read(pfad: &str) -> Result<VorlageInhalt, String> {
    if !erlaubt_vorlage(pfad) {
        return Err("Pfad nicht erlaubt".into());
    }
    let format = vorlage_format(pfad)
        .ok_or_else(|| "Unbekanntes Vorlagenformat".to_string())?
        .to_string();
    let full = repo_root().join(pfad);
    let canonical = canonical_unter_templates(&full)?;
    if format == "pdf" {
        let bytes = fs::read(&canonical).map_err(|e| e.to_string())?;
        return Ok(VorlageInhalt {
            format,
            text: None,
            pdf_base64: Some(STANDARD.encode(bytes)),
        });
    }
    let text = fs::read_to_string(&canonical).map_err(|e| e.to_string())?;
    Ok(VorlageInhalt {
        format,
        text: Some(text),
        pdf_base64: None,
    })
}

pub fn vorlagen_list() -> Result<Vec<VorlageEntry>, String> {
    let path = repo_root().join("docs/vorlagen-manifest.json");
    let text = fs::read_to_string(&path).map_err(|e| format!("Manifest nicht lesbar: {e}"))?;
    let json: serde_json::Value = serde_json::from_str(&text).map_err(|e| e.to_string())?;
    let items = json
        .get("vorlagen")
        .and_then(|v| v.as_array())
        .ok_or_else(|| "vorlagen-Feld fehlt".to_string())?;
    let mut out = Vec::new();
    for item in items {
        let pfad = item.get("pfad").and_then(|v| v.as_str()).unwrap_or("").to_string();
        if pfad.is_empty() || !erlaubt_vorlage(&pfad) {
            continue;
        }
        out.push(VorlageEntry {
            pfad,
            phase: item
                .get("phase")
                .and_then(|v| v.as_str())
                .unwrap_or("")
                .to_string(),
            typ: item
                .get("typ")
                .and_then(|v| v.as_str())
                .unwrap_or("")
                .to_string(),
        });
    }
    Ok(out)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn rules_list_nicht_leer() {
        let rules = rules_list().expect("rules");
        assert!(!rules.is_empty());
    }

    #[test]
    fn pfad_traversal_abgewiesen() {
        assert!(rules_read("rules/../README.md").is_err());
    }

    #[test]
    fn vorlagen_nur_templates() {
        let v = vorlagen_list().expect("vorlagen");
        assert!(!v.is_empty());
        assert!(v.iter().all(|e| erlaubt_vorlage(&e.pfad)));
    }

    #[test]
    fn vorlagen_traversal_abgewiesen() {
        assert!(vorlagen_read("templates/../README.md").is_err());
        assert!(vorlagen_read("rules/DESK_RULES.md").is_err());
        assert!(vorlagen_read("templates/../../etc/passwd").is_err());
    }

    #[test]
    fn vorlagen_lesen_markdown() {
        let v = vorlagen_read("templates/briefkopf.md").expect("lesen");
        assert_eq!(v.format, "markdown");
        assert!(v.text.as_ref().is_some_and(|t| t.contains("{{PRAXISBEZEICHNUNG}}")));
        assert!(v.pdf_base64.is_none());
    }
}
