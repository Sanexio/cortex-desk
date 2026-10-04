import { copyFile, mkdir } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { execFileSync } from 'node:child_process';
const root = new URL('./', import.meta.url);
execFileSync(process.execPath, ['--check', fileURLToPath(new URL('src/index.js', root))]);
await mkdir(new URL('dist/', root), { recursive: true });
for (const file of ['index.js', 'style.css']) {
  await copyFile(new URL(`src/${file}`, root), new URL(`dist/${file}`, root));
}
console.log('TOSORT plugin build: 2 files');
