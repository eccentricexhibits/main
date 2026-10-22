/* Concept B, "Arrow Split": the brand's extended arrow cuts through real Remarkable photos.
   The split (arrowSplit in shared/render.js) is one SVG: photos clipped to diagonals parallel to the arrow shaft, the official magenta
   arrow (not recoloured) laid over the seam, and the magenta pixel pattern once, on the gradient. */

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
    <div class="b-split">${h.arrowSplit({
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
    <div class="b-split b-split--page">${h.arrowSplit({ W: 640, H: 480, seam: 260, photos: [{ src: PAGE_PHOTOS[page] }], pattern: { x: 70, y: 22, w: 120 } })}</div>`;
  },
};
