// Writes the four page shells (index, agenda, speakers, faq) into every mockups/<concept>/ folder
// that has a concept.js. Pages are identical apart from data-page; render.js builds the content.
//   node scripts/pages.mjs
import { readdir, writeFile, access } from "node:fs/promises";
import { join, resolve, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const MOCKUPS = resolve(dirname(fileURLToPath(import.meta.url)), "../mockups");
const PAGES = { index: ["home", "Home"], agenda: ["agenda", "Agenda"], speakers: ["speakers", "Speakers"], faq: ["faq", "FAQ"] };

for (const dir of await readdir(MOCKUPS)) {
  const folder = join(MOCKUPS, dir);
  if (!(await access(join(folder, "concept.js")).then(() => true, () => false))) continue;
  const name = dir === "skeleton" ? "Shared skeleton" : `Concept ${dir.slice(-1).toUpperCase()}`;
  for (const [file, [page, title]] of Object.entries(PAGES)) {
    await writeFile(
      join(folder, `${file}.html`),
      `<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>${title} — Remarkable 2027 — ${name}</title>
  <link rel="stylesheet" href="../shared/base.css">
  <link rel="stylesheet" href="concept.css">
</head>
<body data-page="${page}">
  <script src="concept.js"></script>
  <script src="../shared/render.js" type="module"></script>
</body>
</html>
`
    );
  }
  console.log(`${dir}: ${Object.keys(PAGES).map((f) => `${f}.html`).join(", ")}`);
}
