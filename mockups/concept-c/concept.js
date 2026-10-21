/* Concept C, "Open Canvas": modern editorial. White space and big black type; colour only as an accent
   (the gradient band behind "2027", thin gradient rules, magenta names and the pixel pattern). */
window.CONCEPT = {
  letter: "C",

  hero(copy, h) {
    const hero = copy.hero;
    const [, name, year] = hero.event_name.match(/^(.*?)\s*(\d{4})$/);
    return `<div class="container c-hero__inner">
      <div class="c-hero__copy">
        <p class="eyebrow">${h.esc(hero.eyebrow)}</p>
        <div class="c-lockup">
          <h1 class="c-title"><span class="c-title__name">${h.esc(name)}</span> <span class="c-title__year">${h.esc(year)}</span></h1>
          ${h.anniversarySlot(copy, "c-anniv")}
        </div>
        <hr class="c-rule">
        <p class="c-hero__tagline">${h.esc(hero.tagline)}</p>
        <p class="hero__meta">${h.meta(copy)}</p>
        <p class="hero__address">${h.esc(hero.venue_address)}</p>
        ${h.ctas(copy)}
        <p class="small-print">${h.esc(hero.small_print)}</p>
      </div>
      <figure class="c-hero__media">
        <img class="c-hero__photo" src="${h.ROOT}assets/photos-2026/speaker-at-podium.jpg" alt="${h.esc(h.photoAlt("speaker-at-podium.jpg"))}">
        <img class="c-pixels" src="${h.ROOT}assets/brand-elements/pixel-pattern-magenta.svg" alt="">
      </figure>
    </div>`;
  },

  pageHeader(copy, page, h) {
    const pc = copy[`${page}_page`];
    return `<div class="container page-hero__inner">
      <p class="eyebrow"><span class="nowrap">${h.esc(copy.hero.event_name)}</span> <span class="sep" aria-hidden="true">|</span> ${h.meta(copy)}</p>
      <h1 class="page-hero__title"><span class="c-band">${h.esc(pc.title)}</span></h1>
      <hr class="c-rule">
      <p class="page-hero__intro">${h.esc(pc.intro)}</p>
    </div>`;
  },
};
