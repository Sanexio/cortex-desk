import { invoke } from "@tauri-apps/api/core";
import { markdownToHtml } from "./markdown-preview";

export interface VorlageEntry {
  pfad: string;
  phase: string;
  typ: string;
}

export interface VorlageInhalt {
  format: string;
  text: string | null;
  pdf_base64: string | null;
}

export function vorlageLabel(pfad: string): string {
  const base = pfad.split("/").pop() ?? pfad;
  return base.replace(/\.(md|txt|pdf)$/i, "").replace(/-/g, " ");
}

export function filterVorlagen(
  items: VorlageEntry[],
  query: string,
): VorlageEntry[] {
  const q = query.trim().toLowerCase();
  if (!q) return items;
  return items.filter((v) => {
    const hay = `${v.pfad} ${v.phase} ${v.typ} ${vorlageLabel(v.pfad)}`.toLowerCase();
    return hay.includes(q);
  });
}

export async function loadVorlageInhalt(pfad: string): Promise<VorlageInhalt> {
  return invoke<VorlageInhalt>("vorlagen_read", { pfad });
}

export function copyTextToClipboard(text: string): Promise<void> {
  return navigator.clipboard.writeText(text);
}

type El = <K extends keyof HTMLElementTagNameMap>(
  tag: K,
  className?: string,
  text?: string,
) => HTMLElementTagNameMap[K];

export interface VorlagenMountOptions {
  el: El;
  vorlagen: VorlageEntry[];
  isTauri: boolean;
}

export function mountVorlagenBetrachter(
  container: HTMLElement,
  options: VorlagenMountOptions,
): void {
  const { el, vorlagen, isTauri } = options;
  container.replaceChildren();

  const card = el("section", "card vorlagen-card");
  card.appendChild(el("h2", undefined, "K0-Vorlagen (nur lesen)"));
  card.appendChild(
    el(
      "p",
      "muted",
      "Strukturvorlagen aus dem Repository — Markdown-, Text- und PDF-Vorschau, ohne Schreibzugriff auf Desk-Daten.",
    ),
  );

  const toolbar = el("div", "vorlagen-toolbar");
  const search = el("input") as HTMLInputElement;
  search.type = "search";
  search.placeholder = "Suchen (Pfad, Phase, Typ) …";
  search.className = "vorlagen-search";
  const copyBtn = el("button", undefined, "In Zwischenablage");
  copyBtn.disabled = true;
  const modeBtn = el("button", undefined, "Quelltext");
  modeBtn.disabled = true;
  toolbar.append(search, copyBtn, modeBtn);
  card.appendChild(toolbar);

  const layout = el("div", "vorlagen-layout");
  const list = el("ul", "rules vorlagen-list");
  const panel = el("div", "vorlagen-panel");
  const meta = el("p", "mono muted", "Keine Vorlage ausgewählt.");
  const viewer = el("div", "vorlagen-viewer");
  viewer.appendChild(el("p", "muted", "Vorlage aus der Liste wählen …"));
  panel.append(meta, viewer);
  layout.append(list, panel);
  card.append(layout);
  container.appendChild(card);

  let selected: VorlageEntry | null = null;
  let rawText = "";
  let showSource = false;
  let pdfUrl: string | null = null;

  const revokePdf = () => {
    if (pdfUrl) {
      URL.revokeObjectURL(pdfUrl);
      pdfUrl = null;
    }
  };

  const renderViewer = () => {
    viewer.replaceChildren();
    if (!selected) {
      viewer.appendChild(el("p", "muted", "Vorlage aus der Liste wählen …"));
      return;
    }
    if (!isTauri) {
      viewer.appendChild(
        el("p", "muted", "Vorschau nur in der nativen App verfügbar."),
      );
      return;
    }
    if (pdfUrl) {
      const embed = document.createElement("embed");
      embed.className = "pdf-embed";
      embed.type = "application/pdf";
      embed.src = pdfUrl;
      viewer.appendChild(embed);
      return;
    }
    if (showSource || rawText === "") {
      const pre = el("pre", "viewer");
      pre.textContent = rawText || "—";
      viewer.appendChild(pre);
      return;
    }
    const article = el("article", "md-preview");
    article.innerHTML = markdownToHtml(rawText);
    viewer.appendChild(article);
  };

  const selectVorlage = (v: VorlageEntry) => {
    selected = v;
    revokePdf();
    rawText = "";
    showSource = false;
    modeBtn.textContent = "Quelltext";
    modeBtn.disabled = !isTauri;
    copyBtn.disabled = !isTauri;
    meta.textContent = `${v.pfad} · ${v.phase} · ${v.typ}`;
    renderViewer();
    if (!isTauri) return;
    void loadVorlageInhalt(v.pfad)
      .then((inhalt) => {
        if (inhalt.format === "pdf" && inhalt.pdf_base64) {
          const binary = atob(inhalt.pdf_base64);
          const bytes = new Uint8Array(binary.length);
          for (let i = 0; i < binary.length; i += 1) {
            bytes[i] = binary.charCodeAt(i);
          }
          const blob = new Blob([bytes], { type: "application/pdf" });
          pdfUrl = URL.createObjectURL(blob);
          copyBtn.disabled = true;
          modeBtn.disabled = true;
        } else {
          rawText = inhalt.text ?? "";
          copyBtn.disabled = rawText.length === 0;
          const isMd = inhalt.format === "markdown";
          showSource = !isMd;
          modeBtn.disabled = !isMd;
          modeBtn.textContent = showSource ? "Vorschau" : "Quelltext";
        }
        renderViewer();
      })
      .catch((err) => {
        viewer.replaceChildren();
        viewer.appendChild(el("p", "muted", String(err)));
      });
  };

  const paintList = () => {
    list.replaceChildren();
    const filtered = filterVorlagen(vorlagen, search.value);
    for (const v of filtered) {
      const li = el("li");
      const btn = el("button", "link", vorlageLabel(v.pfad));
      if (selected?.pfad === v.pfad) {
        btn.classList.add("active");
      }
      btn.addEventListener("click", () => selectVorlage(v));
      li.append(
        btn,
        el("span", "muted", ` · ${v.phase}`),
        el("span", "mono muted", ` ${v.pfad}`),
      );
      list.appendChild(li);
    }
    if (filtered.length === 0) {
      list.appendChild(el("li", "muted", "Keine Treffer."));
    }
  };

  search.addEventListener("input", () => paintList());
  copyBtn.addEventListener("click", () => {
    if (!rawText) return;
    void copyTextToClipboard(rawText).then(() => {
      copyBtn.textContent = "Kopiert";
      window.setTimeout(() => {
        copyBtn.textContent = "In Zwischenablage";
      }, 1200);
    });
  });
  modeBtn.addEventListener("click", () => {
    showSource = !showSource;
    modeBtn.textContent = showSource ? "Vorschau" : "Quelltext";
    renderViewer();
  });

  paintList();
  if (vorlagen.length > 0) {
    selectVorlage(vorlagen[0]);
  }
}
