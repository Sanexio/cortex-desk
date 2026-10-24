/** Einfache, HTML-sichere Markdown-Vorschau (kein externes Parser-Paket). */

export function escapeHtml(raw: string): string {
  return raw
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

export function markdownToHtml(md: string): string {
  const lines = escapeHtml(md).split("\n");
  const out: string[] = [];
  let inCode = false;
  let codeBuf: string[] = [];

  const flushCode = () => {
    if (codeBuf.length) {
      out.push(`<pre class="md-code"><code>${codeBuf.join("\n")}</code></pre>`);
      codeBuf = [];
    }
  };

  for (const line of lines) {
    if (line.startsWith("```")) {
      if (inCode) {
        flushCode();
        inCode = false;
      } else {
        inCode = true;
      }
      continue;
    }
    if (inCode) {
      codeBuf.push(line);
      continue;
    }
    if (/^#{1,6}\s/.test(line)) {
      const level = line.match(/^#+/)?.[0].length ?? 1;
      const text = line.replace(/^#{1,6}\s+/, "");
      out.push(`<h${level}>${inlineMarkdown(text)}</h${level}>`);
      continue;
    }
    if (/^[-*]\s+/.test(line)) {
      out.push(`<li>${inlineMarkdown(line.replace(/^[-*]\s+/, ""))}</li>`);
      continue;
    }
    if (line.trim() === "") {
      out.push("<br />");
      continue;
    }
    out.push(`<p>${inlineMarkdown(line)}</p>`);
  }
  flushCode();
  return out.join("\n");
}

function inlineMarkdown(text: string): string {
  return text
    .replace(/`([^`]+)`/g, "<code>$1</code>")
    .replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>")
    .replace(/\*([^*]+)\*/g, "<em>$1</em>");
}
