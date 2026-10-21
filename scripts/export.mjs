// Remarkable 2027 mockups: export script.
// Serves the repo root, screenshots every frame with Playwright, checks each page
// (broken images, horizontal overflow) and builds the review PDF.
//
//   node scripts/export.mjs                 -> every concept frame (4 pages x desktop/mobile + banner, per concept)
//                                              + exports/remarkable-2027-concepts-review.pdf
//   node scripts/export.mjs concept-a       -> only the frames whose name starts with "concept-a"
//   node scripts/export.mjs skeleton        -> shared skeleton preview (not part of the deliverables)
//   OUT_DIR=exports/wireframe node scripts/export.mjs wireframe   -> greyscale wireframe of all four pages
//   OUT_DIR=some/dir node scripts/export.mjs ...   -> write PNGs somewhere else

import { createServer } from "node:http";
import { readFile, mkdir, writeFile, access, rm } from "node:fs/promises";
import { tmpdir } from "node:os";
import { extname, join, resolve, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { chromium } from "playwright";
import { PDFDocument } from "pdf-lib";

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const OUT = resolve(ROOT, process.env.OUT_DIR || "exports");
// The review PDF embeds JPEG copies of the frames (PNG keeps the PDF near 30 MB); the PNGs in OUT stay lossless.
const PDF_IMAGES = join(tmpdir(), "remarkable-pdf-frames");
const PDF_NAME = "remarkable-2027-concepts-review.pdf";
const REVIEW_DATE = "Oct 23, 2026";

const DESKTOP = { width: 1440, height: 900 };
const MOBILE = { width: 390, height: 844 };
const BANNER = { width: 1478, height: 300 };

const CONCEPTS = [
  { id: "a", name: "Concept A — Gradient Stage", rationale: "Continuity — the 2026 stage look, rebuilt in the new magenta-to-cobalt brand gradient." },
  { id: "b", name: "Concept B — Arrow Split", rationale: "Momentum — the brand arrow cuts through real Remarkable photos; the most energetic option." },
  { id: "c", name: "Concept C — Open Canvas", rationale: "Modern editorial — white space and bold type, with colour used only as an accent." },
];

const PAGES = [
  { file: "index", key: "home", title: "Home" },
  { file: "agenda", key: "agenda", title: "Agenda" },
  { file: "speakers", key: "speakers", title: "Speakers" },
  { file: "faq", key: "faq", title: "FAQ" },
];

const pageFrames = (folder, prefix, extra = {}) =>
  PAGES.flatMap((p) => [
    { name: `${prefix}-${p.key}-desktop`, url: `mockups/${folder}/${p.file}.html`, viewport: DESKTOP, fullPage: true, label: `${p.title} · desktop 1440 px`, ...extra },
    { name: `${prefix}-${p.key}-mobile`, url: `mockups/${folder}/${p.file}.html`, viewport: MOBILE, fullPage: true, label: `${p.title} · mobile 390 px`, ...extra },
  ]);

const FRAMES = CONCEPTS.flatMap((c) => [
  ...pageFrames(`concept-${c.id}`, `concept-${c.id}`, { concept: c }),
  { name: `concept-${c.id}-banner`, url: `mockups/concept-${c.id}/banner.html`, viewport: BANNER, fullPage: false, concept: c, label: "Email banner · 1478 × 300" },
]);

const EXTRA = [...pageFrames("skeleton", "skeleton"), ...pageFrames("wireframe", "wireframe")];

const TYPES = {
  ".html": "text/html; charset=utf-8", ".css": "text/css", ".js": "text/javascript", ".mjs": "text/javascript",
  ".json": "application/json", ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
  ".svg": "image/svg+xml", ".otf": "font/otf", ".woff2": "font/woff2",
};

function serve() {
  const server = createServer(async (req, res) => {
    const path = decodeURIComponent(new URL(req.url, "http://x").pathname);
    const [dir, file] = path.startsWith("/pdf-frames/") ? [PDF_IMAGES, join(PDF_IMAGES, path.slice(12))] : [ROOT, join(ROOT, path)];
    if (!file.startsWith(dir)) return res.writeHead(403).end();
    try {
      const body = await readFile(file);
      res.writeHead(200, { "content-type": TYPES[extname(file).toLowerCase()] || "application/octet-stream" }).end(body);
    } catch {
      res.writeHead(404).end("not found");
    }
  });
  return new Promise((r) => server.listen(0, "127.0.0.1", () => r(server)));
}

async function shoot(browser, base, f) {
  const page = await browser.newPage({ viewport: f.viewport, deviceScaleFactor: 1 });
  const problems = [];
  page.on("pageerror", (e) => problems.push(`JS error: ${e.message}`));
  page.on("response", (r) => r.status() >= 400 && problems.push(`HTTP ${r.status()} ${r.url().replace(base, "")}`));
  await page.goto(`${base}/${f.url}`, { waitUntil: "networkidle" });
  await page.waitForFunction(() => document.documentElement.dataset.ready === "true", null, { timeout: 15000 });
  const check = await page.evaluate(() => ({
    broken: document.documentElement.dataset.broken || "",
    overflow: document.documentElement.scrollWidth - document.documentElement.clientWidth,
    missingAlt: [...document.images].filter((i) => !i.hasAttribute("alt")).length,
  }));
  if (check.broken) problems.push(`broken images: ${check.broken}`);
  if (check.overflow > 0) problems.push(`horizontal overflow: ${check.overflow}px`);
  if (check.missingAlt) problems.push(`${check.missingAlt} image(s) without alt`);
  const path = join(OUT, `${f.name}.png`);
  await page.screenshot({ path, fullPage: f.fullPage, animations: "disabled" });
  await page.screenshot({ path: join(PDF_IMAGES, `${f.name}.jpg`), type: "jpeg", quality: 88, fullPage: f.fullPage, animations: "disabled" });
  const size = await page.evaluate(() => [document.documentElement.scrollWidth, document.documentElement.scrollHeight]);
  await page.close();
  console.log(`${problems.length ? "!!" : "ok"}  ${f.name}.png  ${f.fullPage ? size.join(" x ") : `${f.viewport.width} x ${f.viewport.height}`}`);
  problems.forEach((p) => console.log(`      ${p}`));
  return problems.length;
}

const esc = (s) => s.replace(/&/g, "&amp;").replace(/</g, "&lt;");
const PAGE_CSS = `
  @import url("${"https://fonts.googleapis.com/css2?family=Open+Sans:wght@400;700&display=swap"}");
  @font-face { font-family: Karbon; src: url("/fonts/Karbon-Medium.otf"); font-weight: 500; }
  html, body { margin: 0; background: #E9E8E8; font-family: "Open Sans", sans-serif; color: #000; }
  .head { padding: 40px 48px 32px; }
  .bar { height: 6px; background: linear-gradient(90deg, #EB088A, #313CFF); }
  .k { font: 700 13px/1.4 "Open Sans"; letter-spacing: .12em; text-transform: uppercase; color: #444; }
  h1 { font: 500 44px/1.15 Karbon, "Open Sans"; margin: 8px 0 6px; }
  .r { font-size: 20px; margin: 0; }
  .frame { padding: 0 48px 48px; }
  .frame img { display: block; background: #fff; }
`;

async function buildPdf(browser, base) {
  const pdf = await PDFDocument.create();
  const add = async (html, width, height) => {
    const page = await browser.newPage({ viewport: { width, height } });
    await page.setContent(html, { waitUntil: "networkidle" });
    await page.evaluate(() => document.fonts.ready);
    const bytes = await page.pdf({ width: `${width}px`, height: `${height}px`, printBackground: true, pageRanges: "1" });
    await page.close();
    const src = await PDFDocument.load(bytes);
    const [p] = await pdf.copyPages(src, [0]);
    pdf.addPage(p);
  };

  // Cover
  const list = CONCEPTS.map((c) => `<li><b>${esc(c.name)}</b><br>${esc(c.rationale)}</li>`).join("");
  await add(
    `<html><head><base href="${base}/"><style>${PAGE_CSS}
      body { width: 1536px; height: 960px; position: relative; background: #fff; }
      .cover { padding: 120px 120px 0; }
      .cover h1 { font-size: 64px; margin: 24px 0 16px; }
      .cover .sub { font-size: 24px; margin: 0 0 64px; }
      .cover ul { list-style: none; padding: 0; margin: 0; display: grid; gap: 28px; font-size: 20px; max-width: 1100px; }
      .cover img { height: 52px; }
      .foot { position: absolute; left: 120px; bottom: 64px; font-size: 16px; color: #444; }
    </style></head><body><div class="bar"></div><div class="cover">
      <img src="assets/logos/logo-bilingual-colour.png" alt="Vector Institute | Institut Vecteur">
      <h1>Remarkable 2027 — Registration site concepts — internal draft — ${REVIEW_DATE}</h1>
      <p class="sub">Three registration-site directions · Home, Agenda, Speakers and FAQ pages at desktop 1440 px and mobile 390 px, plus a 1478 × 300 email banner for each · placeholder copy</p>
      <ul>${list}</ul>
      <p class="foot">Frames follow in order A, B, C. All speakers, companies and sessions are fictitious; portraits and event photos are from Remarkable 2026 and are temporary.</p>
    </div></body></html>`,
    1536,
    960
  );

  // Frames
  for (const f of FRAMES) {
    const png = join(OUT, `${f.name}.png`);
    const buf = await readFile(png);
    const w = buf.readUInt32BE(16), h = buf.readUInt32BE(20);
    const first = f.name.endsWith("-home-desktop");
    const headH = first ? 168 : 112;
    const width = Math.max(w + 96, 1200);
    await add(
      `<html><head><base href="${base}/"><style>${PAGE_CSS} body { width: ${width}px; }</style></head><body>
        <div class="bar"></div>
        <div class="head" style="height:${headH - 6}px;box-sizing:border-box">
          <div class="k">${esc(f.concept.name)} · ${esc(f.label)}</div>
          ${first ? `<h1>${esc(f.concept.name.split(" — ")[1])}</h1><p class="r">${esc(f.concept.rationale)}</p>` : ""}
        </div>
        <div class="frame"><img src="pdf-frames/${f.name}.jpg" width="${w}" height="${h}" alt=""></div>
      </body></html>`,
      width,
      headH + h + 48
    );
  }
  await writeFile(join(OUT, PDF_NAME), await pdf.save());
  console.log(`ok  ${PDF_NAME}  (${pdf.getPageCount()} pages)`);
}

const filters = process.argv.slice(2);
const targets = filters.length ? [...FRAMES, ...EXTRA].filter((f) => filters.some((x) => f.name.startsWith(x))) : FRAMES;

await mkdir(OUT, { recursive: true });
await mkdir(PDF_IMAGES, { recursive: true });
const server = await serve();
const base = `http://127.0.0.1:${server.address().port}`;
const browser = await chromium.launch();
let issues = 0;
try {
  for (const f of targets) {
    await access(join(ROOT, f.url)).then(
      async () => (issues += await shoot(browser, base, f)),
      () => console.log(`--  ${f.name}: ${f.url} not built yet, skipped`)
    );
  }
  if (!filters.length) await buildPdf(browser, base);
} finally {
  await browser.close();
  server.close();
  await rm(PDF_IMAGES, { recursive: true, force: true });
}
if (issues) {
  console.log(`\n${issues} problem(s) found — see above.`);
  process.exitCode = 1;
}
