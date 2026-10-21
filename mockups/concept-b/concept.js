/* Concept B, "Arrow Split": the brand's extended arrow cuts through real Remarkable photos.
   The split is one SVG: photos clipped to diagonals parallel to the arrow shaft, the official magenta
   arrow (not recoloured) laid over the seam, and the magenta pixel pattern once, on the gradient. */

/* Arrow geometry, measured from vector-arrow-extended-magenta.svg (rendered height = 1, width = 0.5244):
   the shaft's centre line sits at x = 0.080 + K * (0.9 - y), so it leans right by K per unit of height. */
const K = 0.4017;

function split(h, { W, H, photos, seam, pattern }) {
  const ROOT = h.ROOT;
  const Ha = H * 1.05;                                   // arrow slightly taller than the frame, so its tail runs off the bottom
  const Ax = seam - 0.08 * Ha - K * (0.9 * Ha - H);      // places the shaft centre at x = seam on the bottom edge
  const top = (x) => x + K * H;                          // where a line through (x, bottom) meets the top edge
  const regions = [];
  if (photos.length === 2) {
    const left = seam - photos[0].width;
    regions.push({ p: photos[0], pts: [[left, H], [top(left), 0], [top(seam), 0], [seam, H]], x: left, w: top(seam) - left });
  }
  regions.push({ p: photos.at(-1), pts: [[seam, H], [top(seam), 0], [W, 0], [W, H]], x: seam, w: W - seam });
  const id = Math.random().toString(36).slice(2, 7);
  const label = photos.map((p) => h.photoAlt(p.src)).join(". ");
  return `<svg class="b-split__svg" viewBox="0 0 ${W} ${H}" preserveAspectRatio="xMinYMid slice" role="img" aria-label="${h.esc(label)}">
    <defs>${regions.map((r, i) => `<clipPath id="c${id}${i}"><polygon points="${r.pts.map((p) => p.join(",")).join(" ")}"/></clipPath>`).join("")}</defs>
    ${regions.map((r, i) => `<image href="${ROOT}${r.p.src}" x="${r.x}" y="0" width="${r.w}" height="${H}" preserveAspectRatio="${r.p.align || "xMidYMid"} slice" clip-path="url(#c${id}${i})"/>`).join("")}
    ${pattern ? `<image class="b-pixels" href="${ROOT}assets/brand-elements/pixel-pattern-magenta.svg" x="${pattern.x}" y="${pattern.y}" width="${pattern.w}" height="${pattern.w * 175 / 185}"/>` : ""}
    <image href="${ROOT}assets/brand-elements/vector-arrow-extended-magenta.svg" x="${Ax}" y="0" width="${Ha * 0.5244}" height="${Ha}"/>
  </svg>`;
}

const PAGE_PHOTOS = {
  agenda: "assets/photos-2026/auditorium-keynote.jpg",
  speakers: "assets/photos-2026/workshop-speaker-smiling.jpg",
  faq: "assets/photos-2026/registration-desk.jpg",
};

window.CONCEPT = {
  letter: "B",
  dayPhotos: [{ src: "assets/photos-2026/stage-remarkable-backdrop.jpg" }, { src: "assets/photos-2026/posters-discussion.jpg" }],

  hero(copy, h) {
    const hero = copy.hero;
    return `<div class="container b-hero__inner">
      <div class="b-hero__copy">
        <p class="eyebrow">${h.esc(hero.eyebrow)}</p>
        <h1 class="b-hero__title">${h.esc(hero.tagline)}</h1>
        <div class="b-lockup">
          ${h.anniversarySlot(copy, "b-anniv")}
          <div class="b-lockup__text">
            <p class="b-lockup__name">${h.esc(hero.event_name)}</p>
            <p class="hero__meta">${h.meta(copy)}</p>
            <p class="b-lockup__address">${h.esc(hero.venue_address)}</p>
          </div>
        </div>
        ${h.ctas(copy)}
        <p class="small-print">${h.esc(hero.small_print)}</p>
      </div>
    </div>
    <div class="b-split">${split(h, {
      W: 800, H: 760, seam: 400,
      photos: [{ src: "assets/photos-2026/stage-fireside-chat.jpg", width: 380, align: "xMidYMid" }, { src: "assets/photos-2026/networking-crowd.jpg", align: "xMidYMid" }],
      pattern: { x: 22, y: 26, w: 150 },
    })}</div>`;
  },

  pageHeader(copy, page, h) {
    const pc = copy[`${page}_page`];
    return `<div class="container page-hero__inner">
      <p class="eyebrow"><span class="nowrap">${h.esc(copy.hero.event_name)}</span> <span class="sep" aria-hidden="true">|</span> ${h.meta(copy)}</p>
      <h1 class="page-hero__title">${h.esc(pc.title)}</h1>
      <p class="page-hero__intro">${h.esc(pc.intro)}</p>
    </div>
    <div class="b-split b-split--page">${split(h, { W: 640, H: 480, seam: 260, photos: [{ src: PAGE_PHOTOS[page] }], pattern: { x: 70, y: 22, w: 120 } })}</div>`;
  },
};
