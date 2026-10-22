/* Concept D, "Spotlight": a black stage with oversized Karbon type, real Remarkable photography and the magenta
   Vector arrow. Adapted from a design made in a separate AI chat (sources/concept-d-design/): its look is kept,
   but the structure, copy and type sizes follow the shared four-page layout like A, B and C. */

const D_ARROW = "assets/brand-elements/vector-arrow-magenta.svg";
const D_HERO_PHOTO = "assets/photos-2026/auditorium-fireside-screens.jpg";
const D_DAYS_PHOTO = "assets/photos-2026/stage-fireside-chat.jpg";
const D_HILTON = "assets/logos/hilton-white.svg"; // 1137 x 422; decorative, as "Hilton Toronto" is written beside it

window.CONCEPT = {
  letter: "D",
  navLogo: "knockout",
  agendaTabs: true,

  hero(copy, h) {
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
        <span class="d-details__venue"><img class="d-hilton" src="${h.asset(D_HILTON)}" alt="" width="1137" height="422"><strong class="nowrap">${h.esc(hero.venue)}</strong> <span class="d-details__address nowrap">${h.esc(hero.venue_address)}</span></span>
      </p>
    </div>
    <div class="d-rule" aria-hidden="true"></div>`;
  },

  pageHeader(copy, page, h) {
    const pc = copy[`${page}_page`];
    return `<div class="container page-hero__inner">
      <p class="eyebrow"><span class="nowrap">${h.esc(copy.hero.event_name)}</span> <span class="sep" aria-hidden="true">|</span> ${h.meta(copy)}</p>
      <h1 class="page-hero__title">${h.esc(pc.title)}</h1>
      <p class="page-hero__intro">${h.esc(pc.intro)}</p>
    </div>
    <div class="d-rule" aria-hidden="true"></div>`;
  },

  after(copy, page) {
    if (page !== "home") return;
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
