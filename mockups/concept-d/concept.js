/* Concept D, "Spotlight": a black stage with oversized Karbon type, real Remarkable photography and the magenta
   Vector arrow. Adapted from a design made in a separate AI chat (sources/concept-d-design/): its look is kept,
   but the structure, copy and type sizes follow the shared four-page layout like A, B and C. */

const D_ARROW = "assets/brand-elements/vector-arrow-magenta.svg";
const D_HERO_PHOTO = "assets/photos-2026/auditorium-fireside-screens.jpg";
const D_DAYS_PHOTO = "assets/photos-2026/stage-fireside-chat.jpg";
const D_PIXELS = "assets/brand-elements/pixel-pattern-magenta.svg";
const D_HERO = "split"; // home hero: "split" (current) or "stage" (the previous version, kept on file)
// Split hero frame: 700 px tall; the photo's edge meets the bottom 70 px into the frame. The frame's width follows the
// screen (see after()), so the arrow keeps its full height and the photo its edge at any width.
const D_SPLIT = { H: 700, seam: 70 };
let dArrowSplit = null; // the shared arrowSplit helper, kept by heroSplit for after()
// Inner-page headers: one photo on the right, cut along the magenta arrow (brand guide p. 6); on a phone, the photo
// below the text instead, faded in from black. Not the photos B uses.
const D_PAGE_PHOTOS = {
  // align: the desktop crop (agenda keeps the speaker clear of the edge); phone: the phone crop (object-position)
  agenda: { src: "assets/photos-2026/stage-remarkable-backdrop.jpg", align: "xMaxYMid", phone: "65% 50%" },
  speakers: { src: "assets/photos-2026/speaker-at-podium.jpg", phone: "50% 0%" }, // her face is near the top
  faq: { src: "assets/photos-2026/posters-discussion.jpg", phone: "50% 20%" },
};

/* Home hero, "stage" (previous, kept on file): the full-width REMARKABLE 2027 wordmark above the tagline and a
   rounded photo with the magenta arrow on its corner. To bring it back, set D_HERO = "stage". */
function heroStage(copy, h) {
  const hero = copy.hero;
  const [, name, year] = hero.event_name.match(/^(.*?)\s*(\d{4})$/);
  return `<div class="container d-hero">
    <p class="eyebrow d-hero__eyebrow">${h.esc(hero.eyebrow)}</p>
    <div class="d-masthead">
      <h1 class="d-masthead__title" aria-label="${h.esc(hero.event_name)}">
        <span class="d-masthead__name" aria-hidden="true">${h.esc(name)}</span>
        <span class="d-masthead__year" aria-hidden="true">${h.esc(year)}</span>
      </h1>
    </div>
    <div class="d-hero__grid">
      <div class="d-hero__copy">
        <p class="d-hero__tagline">${h.esc(hero.tagline)}</p>
        ${h.ctas(copy)}
        <p class="small-print">${h.esc(hero.small_print)}</p>
      </div>
      <div class="d-hero__media">
        <img class="d-hero__photo" src="${h.asset(D_HERO_PHOTO)}" alt="${h.esc(h.photoAlt(D_HERO_PHOTO))}">
        <img class="d-arrow" src="${h.asset(D_ARROW)}" alt="">
      </div>
    </div>
    <p class="d-details">
      <strong class="nowrap">${h.esc(hero.dates)}</strong>
      <span class="d-details__venue"><strong class="nowrap">${h.esc(hero.venue)}</strong> <span class="d-details__address nowrap">${h.esc(hero.venue_address)}</span></span>
    </p>
  </div>
  <div class="d-rule" aria-hidden="true"></div>`;
}

/* Home hero, "split" (current): adapted from the requester's Karbon-and-pixels mockup. Text on black on the left;
   on the right a 2026 photo running to the edge, cut along the extended magenta arrow, whose tip touches the top.
   Phones: no split; the photo follows the text and fades in from black, as on the inner pages. */
function heroSplit(copy, h) {
  dArrowSplit = h.arrowSplit;
  const hero = copy.hero;
  const [, name, year] = hero.event_name.match(/^(.*?)\s*(\d{4})$/);
  return `<div class="d-sh">
      <div class="container d-sh__inner">
        <div class="d-sh__copy">
          <p class="eyebrow">${h.esc(hero.eyebrow)}</p>
          <h1 class="d-sh__title" aria-label="${h.esc(hero.event_name)}">
            <span class="d-sh__name" aria-hidden="true">${h.esc(name)}</span>
            <span class="d-sh__year" aria-hidden="true">${h.esc(year)}<img class="d-sh__pixels" src="${h.asset(D_PIXELS)}" alt=""></span>
          </h1>
          <p class="d-sh__tagline">${h.esc(hero.tagline)}</p>
          ${h.ctas(copy)}
          <p class="small-print">${h.esc(hero.small_print)}</p>
        </div>
      </div>
      <div class="d-sh__split">${h.arrowSplit({ W: 820, H: D_SPLIT.H, seam: D_SPLIT.seam, photos: [{ src: D_HERO_PHOTO }], touchTop: true })}</div>
    </div>
    <div class="d-fade d-sh__fade"><img src="${h.asset(D_HERO_PHOTO)}" alt="${h.esc(h.photoAlt(D_HERO_PHOTO))}"></div>
    <div class="container">
      <p class="d-details">
        <strong class="nowrap">${h.esc(hero.dates)}</strong>
        <span class="d-details__venue"><strong class="nowrap">${h.esc(hero.venue)}</strong> <span class="d-details__address nowrap">${h.esc(hero.venue_address)}</span></span>
      </p>
    </div>
    <div class="d-rule" aria-hidden="true"></div>`;
}

window.CONCEPT = {
  letter: "D",
  navLogo: "knockout",
  agendaTabs: true,

  hero(copy, h) {
    return D_HERO === "stage" ? heroStage(copy, h) : heroSplit(copy, h);
  },

  pageHeader(copy, page, h) {
    const pc = copy[`${page}_page`];
    return `<div class="container page-hero__inner">
      <p class="eyebrow"><span class="nowrap">${h.esc(copy.hero.event_name)}</span> <span class="sep" aria-hidden="true">|</span> ${h.meta(copy)}</p>
      <h1 class="page-hero__title">${h.esc(pc.title)}</h1>
      <p class="page-hero__intro">${h.esc(pc.intro)}</p>
    </div>
    <div class="d-split">${h.arrowSplit({ W: 780, H: 480, seam: 160, photos: [D_PAGE_PHOTOS[page]], touchTop: true })}</div>
    <div class="d-fade"><img src="${h.asset(D_PAGE_PHOTOS[page].src)}" alt="${h.esc(h.photoAlt(D_PAGE_PHOTOS[page].src))}" style="object-position: ${D_PAGE_PHOTOS[page].phone}"></div>
    <div class="d-rule" aria-hidden="true"></div>`;
  },

  after(copy, page) {
    if (page !== "home") return;
    // Split hero: redraw the frame at the region's real proportions (820 x 700 at 1440; wider on bigger screens)
    const split = document.querySelector(".d-sh__split");
    if (split && dArrowSplit) {
      const fit = () => {
        const r = split.getBoundingClientRect();
        if (!r.height) return; // phones: the split is hidden
        const W = Math.round((r.width * D_SPLIT.H) / r.height);
        split.innerHTML = dArrowSplit({ W, H: D_SPLIT.H, seam: D_SPLIT.seam, photos: [{ src: D_HERO_PHOTO }], touchTop: true });
      };
      fit();
      window.addEventListener("resize", fit);
    }
    // Photo beside the two day panels (the grey "program" band of the design)
    document.querySelector(".days .container").insertAdjacentHTML(
      "afterbegin",
      `<img class="d-days__photo" src="../../${D_DAYS_PHOTO}" alt="Two speakers in a fireside chat in front of the Remarkable backdrop">`
    );
    // A trailing "+" on a stat is set in magenta (solid colour, never gradient)
    document.querySelectorAll(".stat__value").forEach((el) => {
      el.innerHTML = el.textContent.replace(/\+$/, '<span class="d-plus">+</span>');
    });
  },
};
