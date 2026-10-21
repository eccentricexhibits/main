// Builds exports/wireframe/remarkable-2027-wireframes.pdf from the wireframe review page
// (exports/wireframe/index.html). One PDF page for the overview, then one tall page per site page,
// each sized to its content so no wireframe is split across a page break.
//   OUT_DIR=exports/wireframe node scripts/export.mjs wireframe && node scripts/wireframe-pdf.mjs
import { readFile, writeFile, rm } from "node:fs/promises";
import { resolve, dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { chromium } from "playwright";
import { PDFDocument } from "pdf-lib";

const DIR = resolve(dirname(fileURLToPath(import.meta.url)), "../exports/wireframe");
const WIDTH = 1280;

// The page is authored as a body fragment (the Artifact host adds the skeleton); wrap it so it renders in standards mode.
const fragment = await readFile(join(DIR, "index.html"), "utf8");
const tmp = join(DIR, "_print.html");
await writeFile(tmp, `<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><style>body{margin:0}</style></head><body>${fragment}</body></html>`);

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: WIDTH, height: 1000 } });
await page.goto(`file://${tmp}#all`, { waitUntil: "networkidle" });
// Must outrank the page's own ".show-all [role=tabpanel][hidden]" rule, which is also !important.
await page.addStyleTag({ content: ".show-all .wrap .pdf-hide.pdf-hide { display: none !important; }" });
await page.evaluate(async () => {
  await document.fonts.ready;
  await Promise.all([...document.images].map((i) => (i.complete ? 0 : new Promise((r) => (i.onload = i.onerror = r)))));
});

// Each sheet = the elements to keep visible; everything else in .wrap is hidden while it prints.
const panels = await page.$$eval('[role="tabpanel"]', (ps) => ps.map((p) => `#${p.id}`));
const sheets = [[".head", ".ask"], ...panels.map((id, i) => (i === panels.length - 1 ? [id, ".next"] : [id]))];

const pdf = await PDFDocument.create();
for (const keep of sheets) {
  const height = await page.evaluate((keep) => {
    const wrap = document.querySelector(".wrap");
    const tabsBlock = document.querySelector(".tabs").parentElement;
    const shown = new Set(keep.map((s) => document.querySelector(s)));
    [...wrap.children, ...tabsBlock.children].forEach((el) => {
      if (el !== tabsBlock) el.classList.toggle("pdf-hide", !shown.has(el));
    });
    tabsBlock.classList.toggle("pdf-hide", !keep.some((s) => tabsBlock.querySelector(s)));
    return Math.ceil(document.documentElement.scrollHeight);
  }, keep);
  const bytes = await page.pdf({ width: `${WIDTH}px`, height: `${height + 2}px`, printBackground: true, pageRanges: "1" });
  const [p] = await pdf.copyPages(await PDFDocument.load(bytes), [0]);
  pdf.addPage(p);
}
await browser.close();
await rm(tmp);
await writeFile(join(DIR, "remarkable-2027-wireframes.pdf"), await pdf.save());
console.log(`ok  remarkable-2027-wireframes.pdf  (${pdf.getPageCount()} pages)`);
