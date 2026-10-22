// Node 25 may expose its unconfigured localStorage in the jsdom global.
// Use a per-test Web Storage fixture so persistence tests are deterministic.
const stored = new Map<string, string>();
Object.defineProperty(window, "localStorage", { configurable: true, value: {
  get length() { return stored.size; },
  clear: () => stored.clear(),
  getItem: (key: string) => stored.get(key) ?? null,
  setItem: (key: string, value: string) => { stored.set(key, String(value)); },
  removeItem: (key: string) => { stored.delete(key); },
  key: (index: number) => [...stored.keys()][index] ?? null,
} });
