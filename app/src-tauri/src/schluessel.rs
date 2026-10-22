pub fn oeffentlich_bytes() -> [u8; 32] {
    let raw = env!("CORTEX_LIZENZ_OEFFENTLICH_BYTES");
    let parts: Vec<u8> = raw
        .split(',')
        .map(|s| s.parse().expect("Build-Schluessel Bytes"))
        .collect();
    let mut out = [0u8; 32];
    assert_eq!(parts.len(), 32);
    for (i, b) in parts.into_iter().enumerate() {
        out[i] = b;
    }
    out
}
