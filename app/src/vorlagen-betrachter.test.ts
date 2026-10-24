import { describe, expect, it } from "vitest";
import { escapeHtml, markdownToHtml } from "./markdown-preview";
import { filterVorlagen, vorlageLabel } from "./vorlagen-betrachter";

describe("vorlagen-betrachter", () => {
  const sample = [
    { pfad: "templates/briefkopf.md", phase: "B.4", typ: "markdown-strukturvorlage" },
    { pfad: "templates/amtsanfrage-steuer.md", phase: "B.4", typ: "markdown-strukturvorlage" },
  ];

  it("filtert nach Suchbegriff", () => {
    const hit = filterVorlagen(sample, "briefkopf");
    expect(hit).toHaveLength(1);
    expect(hit[0].pfad).toContain("briefkopf");
    expect(filterVorlagen(sample, "kein-treffer")).toHaveLength(0);
  });

  it("erzeugt lesbare Labels", () => {
    expect(vorlageLabel("templates/briefkopf.md")).toBe("briefkopf");
  });
});

describe("markdown-preview", () => {
  it("escaped HTML", () => {
    expect(escapeHtml("<script>")).toBe("&lt;script&gt;");
  });

  it("rendert Überschriften", () => {
    expect(markdownToHtml("# Titel")).toContain("<h1>Titel</h1>");
  });
});
