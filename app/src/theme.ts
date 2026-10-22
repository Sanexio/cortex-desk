const STORAGE_KEY = "cortex-desk-theme";
const DEFAULT = "praxis2025";

export type ThemeKey = "praxis2025" | "cyber-dark";

export function readTheme(): ThemeKey {
  const raw = localStorage.getItem(STORAGE_KEY);
  if (raw === "cyber-dark" || raw === "praxis2025") return raw;
  return DEFAULT;
}

export function applyTheme(key: ThemeKey): void {
  document.documentElement.setAttribute("data-theme", key);
  localStorage.setItem(STORAGE_KEY, key);
}

export function cycleTheme(): ThemeKey {
  const next = readTheme() === "praxis2025" ? "cyber-dark" : "praxis2025";
  applyTheme(next);
  return next;
}

applyTheme(readTheme());
