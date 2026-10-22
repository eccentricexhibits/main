/* Concept A, "Gradient Stage": the 2026 stage look rebuilt in the magenta-to-cobalt gradient.
   Centred overlay box with the letter-spaced wordmark; gradient bands for the hero, page headers and speakers. */
window.CONCEPT = {
  letter: "A",
  navLogo: "knockout",

  hero(copy, h) {
    const hero = copy.hero;
    const [, name, year] = hero.event_name.match(/^(.*?)\s*(\d{4})$/);
    return `<div class="container a-hero__inner">
      <p class="eyebrow a-hero__eyebrow">${h.esc(hero.eyebrow)}</p>
      <div class="a-box">
        ${h.anniversaryMark(copy, "a-anniv")}
        <h1 class="a-wordmark" aria-label="${h.esc(hero.event_name)}">
          <span class="a-wordmark__name" aria-hidden="true">${h.esc(name)}</span>
          <span class="a-wordmark__year" aria-hidden="true">${h.esc(year)}</span>
        </h1>
        <p class="a-box__tagline">${h.esc(hero.tagline)}</p>
        <p class="hero__meta">${h.meta(copy)}</p>
        ${h.ctas(copy)}
      </div>
      <p class="a-hero__fine"><span class="nowrap">${h.esc(hero.venue_address)}</span> <span class="sep" aria-hidden="true">·</span> <span>${h.esc(hero.small_print)}</span></p>
    </div>`;
  },

  pageHeader(copy, page, h) {
    const pc = copy[`${page}_page`];
    return `<div class="container page-hero__inner">
      <p class="eyebrow"><span class="nowrap">${h.esc(copy.hero.event_name)}</span> <span class="sep" aria-hidden="true">|</span> ${h.meta(copy)}</p>
      <h1 class="page-hero__title">${h.esc(pc.title)}</h1>
      <p class="page-hero__intro">${h.esc(pc.intro)}</p>
    </div>`;
  },
};
