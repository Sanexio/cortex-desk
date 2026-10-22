import { invoke } from "@tauri-apps/api/core";
import { applyTheme, cycleTheme, readTheme } from "./theme";

interface LicenseOverview {
  state: string;
  gebucht: boolean;
  hinweis: string;
}

interface RuleEntry {
  pfad: string;
  titel: string;
}

interface VorlageEntry {
  pfad: string;
  phase: string;
  typ: string;
}

interface AppInfo {
  version: string;
  app_id: string;
  bundle_id: string;
  klasse: string;
}

function el<K extends keyof HTMLElementTagNameMap>(
  tag: K,
  className?: string,
  text?: string,
): HTMLElementTagNameMap[K] {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}

function isTauri(): boolean {
  return "__TAURI_INTERNALS__" in window;
}

async function loadRules(): Promise<RuleEntry[]> {
  if (!isTauri()) return [];
  return invoke<RuleEntry[]>("rules_list");
}

async function loadRule(path: string): Promise<string> {
  return invoke<string>("rules_read", { pfad: path });
}

async function loadVorlagen(): Promise<VorlageEntry[]> {
  if (!isTauri()) return [];
  return invoke<VorlageEntry[]>("vorlagen_list");
}

async function loadLicense(): Promise<LicenseOverview> {
  if (!isTauri()) {
    return {
      state: "browser",
      gebucht: true,
      hinweis: "Vorschau im Browser — Lizenzprüfung nur in der nativen App.",
    };
  }
  return invoke<LicenseOverview>("lizenz_ueberblick");
}

async function loadInfo(): Promise<AppInfo | null> {
  if (!isTauri()) return null;
  return invoke<AppInfo>("app_info");
}

async function checkUpdate(line: HTMLElement): Promise<void> {
  line.textContent = "Suche nach Updates …";
  try {
    const version = await invoke<string | null>("updater_check");
    line.textContent = version
      ? `Update verfügbar: ${version}`
      : "Kein Update verfügbar (Stub-Feed).";
  } catch (err) {
    line.textContent = `Update-Prüfung: ${String(err)}`;
  }
}

function renderTabs(active: string, onSelect: (id: string) => void): HTMLElement {
  const nav = el("nav", "tabs");
  for (const tab of [
    ["regeln", "Regelwerk"],
    ["vorlagen", "Vorlagen"],
    ["status", "Status"],
  ] as const) {
    const btn = el("button", tab[0] === active ? "active" : undefined, tab[1]);
    btn.addEventListener("click", () => onSelect(tab[0]));
    nav.appendChild(btn);
  }
  return nav;
}

async function render(): Promise<void> {
  const mount = document.getElementById("app");
  if (!mount) return;
  mount.replaceChildren();

  const shell = el("div", "shell");
  const header = el("header");
  const title = el("h1", undefined, "Cortex Desk");
  const badge = el("span", "badge", "K0 · Regelwerk");
  const themeBtn = el("button", undefined, "Design umschalten");
  themeBtn.addEventListener("click", () => {
    const key = cycleTheme();
    themeBtn.textContent =
      key === "praxis2025" ? "Cyberpunk" : "Praxis 2025";
  });
  themeBtn.textContent = readTheme() === "praxis2025" ? "Cyberpunk" : "Praxis 2025";
  header.append(title, badge, themeBtn);
  shell.appendChild(header);

  let active = "regeln";
  const body = el("div");
  shell.appendChild(body);

  async function paint(): Promise<void> {
    body.replaceChildren(renderTabs(active, (id) => {
      active = id;
      void paint();
    }));

    const license = await loadLicense();
    if (active !== "status" && !license.gebucht) {
      const locked = el("section", "card");
      locked.append(el("h2", undefined, "Nicht gebucht"), el("p", undefined, "Signierte Freischaltung erforderlich. In-App-Kauf: Freischaltung ohne Zahlung."));
      const status = el("button", "primary", "Lizenzstatus öffnen");
      status.addEventListener("click", () => { active = "status"; void paint(); });
      locked.append(status);
      body.append(locked);
      return;
    }

    if (active === "regeln") {
      const card = el("section", "card");
      card.appendChild(el("h2", undefined, "Öffentliches Regelwerk"));
      card.appendChild(
        el(
          "p",
          "muted",
          "Kuratierte Regeln und Schemata aus dem eingebauten Framework — nur Platzhalter und Framework-Text, keine Tenant-Daten.",
        ),
      );
      const list = el("ul", "rules");
      const viewer = el("pre", "viewer");
      viewer.textContent = "Datei auswählen …";
      const rules = await loadRules();
      for (const rule of rules) {
        const li = el("li");
        const btn = el("button", "link", rule.titel || rule.pfad);
        btn.addEventListener("click", () => {
          void loadRule(rule.pfad).then((text) => {
            viewer.textContent = text;
          });
        });
        li.appendChild(btn);
        list.appendChild(li);
      }
      card.append(list, viewer);
      body.appendChild(card);
    }

    if (active === "vorlagen") {
      const card = el("section", "card");
      card.appendChild(el("h2", undefined, "Phase-B-Vorlagen (Platzhalter)"));
      const vorlagen = await loadVorlagen();
      const ul = el("ul", "rules");
      const viewer = el("pre", "viewer", "Vorlage auswählen …");
      for (const v of vorlagen) {
        const li = el("li");
        const btn = el("button", "link", v.pfad);
        btn.addEventListener("click", () => {
          void invoke<string>("vorlagen_read", { pfad: v.pfad }).then(text => { viewer.textContent = text; }).catch(err => { viewer.textContent = String(err); });
        });
        li.appendChild(btn);
        li.appendChild(el("span", "muted", ` · ${v.phase} · ${v.typ}`));
        ul.appendChild(li);
      }
      card.append(ul, viewer);
      body.appendChild(card);
    }

    if (active === "status") {
      const lic = await loadLicense();
      const info = await loadInfo();
      const card = el("section", "card");
      card.appendChild(el("h2", undefined, "Lizenz & Marketplace"));
      card.appendChild(el("p", undefined, lic.hinweis));
      card.appendChild(
        el("p", "mono", `Zustand: ${lic.state} · gebucht: ${lic.gebucht ? "ja" : "nein"}`),
      );
      if (info) {
        card.appendChild(
          el(
            "p",
            "mono",
            `${info.app_id} · ${info.bundle_id} · v${info.version} · ${info.klasse}`,
          ),
        );
      }
      const updateLine = el("p", "muted");
      const updateBtn = el("button", undefined, "Nach Updates suchen");
      updateBtn.addEventListener("click", () => void checkUpdate(updateLine));
      if (!isTauri()) updateBtn.disabled = true;
      card.append(updateBtn, updateLine);

      const dash = el("section", "card");
      dash.appendChild(el("h2", undefined, "Dashboard-Plugin (TOSORT)"));
      dash.appendChild(
        el(
          "p",
          "muted",
          "Das Harness-Plugin benötigt einen lokalen ARCHIV-Pfad und bleibt im Dashboard. In der Einzel-App ist nur der K0-Regelwerks-Katalog enthalten.",
        ),
      );
      body.append(card, dash);
    }
  }

  mount.appendChild(shell);
  await paint();
}

void render();
