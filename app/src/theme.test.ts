import { describe, expect, it, beforeEach } from "vitest";
import { readTheme, applyTheme } from "./theme";

describe("theme", () => {
  beforeEach(() => {
    localStorage.clear();
    document.documentElement.setAttribute("data-theme", "praxis2025");
  });

  it("defaults to praxis2025", () => {
    expect(readTheme()).toBe("praxis2025");
  });

  it("persists cyber-dark", () => {
    applyTheme("cyber-dark");
    expect(readTheme()).toBe("cyber-dark");
    expect(document.documentElement.getAttribute("data-theme")).toBe("cyber-dark");
  });
});
