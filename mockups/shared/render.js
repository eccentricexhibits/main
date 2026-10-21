/* Remarkable 2027 mockups: shared renderer.
   Loads content/copy.json and builds the 10 home-page sections in a fixed order.
   Each concept sets window.CONCEPT before this script runs:
     letter      "A" | "B" | "C"               (frame label)
     navLogo     "colour" | "knockout"          (nav logo variant, default colour)
     hero(copy)  returns the inner HTML of the hero section (optional)
     dayPhotos   [{src, alt}, ...]               (optional photo per day card)
     after(copy) runs once everything is in the DOM (optional)
   When all fonts and images have loaded, <html data-ready="true"> is set for the export script. */

const ROOT = "../../";

const PHOTO_ALT = {
  "auditorium-wide-stage.jpg": "Wide view of the Remarkable 2026 main stage and a full auditorium",
  "stage-fireside-chat.jpg": "Two speakers in a fireside chat on the Remarkable 2026 stage",
  "networking-crowd.jpg": "Attendees networking in a busy hallway at Remarkable 2026",
  "stage-remarkable-backdrop.jpg": "Speaker presenting in front of the Remarkable backdrop",
  "posters-discussion.jpg": "Researchers discussing a poster at the Remarkable 2026 poster session",
  "speaker-at-podium.jpg": "Speaker addressing the audience from the podium at Remarkable 2026",
  "workshop-speaker-smiling.jpg": "Smiling workshop presenter at Remarkable 2026",
  "auditorium-keynote.jpg": "Keynote session in the Remarkable 2026 auditorium",
  "audience-listening.jpg": "Audience members listening to a talk at Remarkable 2026",
};

const FUNDER_ALT = {
  "canada.png": "Government of Canada",
  "ontario.png": "Government of Ontario",
  "cifar.png": "CIFAR",
};

const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
const file = (p) => p.split("/").pop();
const asset = (p) => ROOT + p;
const photoAlt = (p) => PHOTO_ALT[file(p)] || "Remarkable 2026 event photo";

const ICONS = {
  x: `<img src="${ROOT}assets/social-icons/x-white.png" alt="" width="18" height="18">`,
  bluesky: `<img src="${ROOT}assets/social-icons/bluesky-white.png" alt="" width="18" height="18">`,
  linkedin: `<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true" fill="currentColor"><path d="M4.98 3.5a2.5 2.5 0 1 1 0 5 2.5 2.5 0 0 1 0-5zM3 9.75h4v11H3v-11zm6.5 0h3.83v1.5h.06c.53-1 1.84-2.06 3.79-2.06 4.05 0 4.8 2.66 4.8 6.12v5.44h-4v-4.82c0-1.15-.02-2.63-1.6-2.63-1.6 0-1.85 1.25-1.85 2.55v4.9h-4v-11z"/></svg>`,
  youtube: `<svg viewBox="0 0 24 24" width="20" height="18" aria-hidden="true" fill="currentColor"><path d="M23 7.2a3 3 0 0 0-2.1-2.1C19 4.6 12 4.6 12 4.6s-7 0-8.9.5A3 3 0 0 0 1 7.2 31 31 0 0 0 .5 12 31 31 0 0 0 1 16.8a3 3 0 0 0 2.1 2.1c1.9.5 8.9.5 8.9.5s7 0 8.9-.5a3 3 0 0 0 2.1-2.1c.4-1.6.5-4.8.5-4.8s0-3.2-.5-4.8zM9.75 15.02V8.98L15.5 12l-5.75 3.02z"/></svg>`,
};

/* "X @VectorInst" -> { icon, label } */
function social(entry) {
  const key = entry.split(" ")[0].toLowerCase();
  return { key, icon: ICONS[key] || "", label: entry };
}

function logo(variant, cls = "") {
  const src = variant === "knockout" ? "logo-bilingual-knockout-white.png" : "logo-bilingual-colour.png";
  return `<img class="logo ${cls}" src="${ROOT}assets/logos/${src}" alt="Vector Institute | Institut Vecteur" width="2320" height="493">`;
}

function anniversarySlot(copy, cls = "") {
  return `<div class="anniv ${cls}" role="img" aria-label="${esc(copy.hero.anniversary_slot)}"><span class="anniv__label">10th anniversary mark</span></div>`;
}

/* Dates | venue, each kept on one line */
function meta(copy) {
  return `<span class="nowrap">${esc(copy.hero.dates)}</span> <span class="sep" aria-hidden="true">|</span> <span class="nowrap">${esc(copy.hero.venue)}</span>`;
}

function ctas(copy) {
  return `<div class="cta-row">
      <a class="btn btn--primary" href="#register">${esc(copy.hero.cta_primary)}</a>
      <a class="btn btn--secondary" href="#virtual">${esc(copy.hero.cta_secondary)}</a>
    </div>`;
}

function defaultHero(copy) {
  const h = copy.hero;
  return `<div class="container hero__inner">
    <div class="hero__copy">
      <p class="eyebrow">${esc(h.eyebrow)}</p>
      <h1 class="hero__title">${esc(h.event_name)}</h1>
      <p class="hero__tagline">${esc(h.tagline)}</p>
      <p class="hero__meta">${meta(copy)}</p>
      ${ctas(copy)}
      <p class="small-print">${esc(h.small_print)}</p>
    </div>
    ${anniversarySlot(copy)}
  </div>`;
}

function nav(copy, variant) {
  const links = copy.nav
    .map((l, i) => `<li><a href="#${l.toLowerCase().replace(/\s+/g, "-")}"${i === 0 ? ' aria-current="page"' : ""}${l === "Log in" ? ' class="nav__login"' : ""}>${esc(l)}</a></li>`)
    .join("");
  return `<header class="nav">
    <div class="container nav__inner">
      <a class="nav__logo" href="#home">${logo(variant)}</a>
      <nav class="nav__links" aria-label="Main"><ul>${links}</ul></nav>
      <div class="nav__actions">
        <a class="btn btn--primary btn--nav" href="#register">${esc(copy.nav_cta)}</a>
        <button class="nav__burger" type="button" aria-label="Open menu" aria-expanded="false"><span></span><span></span><span></span></button>
      </div>
    </div>
  </header>`;
}

function sections(copy, C) {
  const s = copy.stats;
  const stats = s.items.map((it) => `<li class="stat"><span class="stat__value">${esc(it.value)}</span><span class="stat__label">${esc(it.label)}</span></li>`).join("");

  const days = copy.days
    .map((d, i) => {
      const ph = C.dayPhotos && C.dayPhotos[i];
      return `<article class="day">
        ${ph ? `<img class="day__photo" src="${asset(ph.src)}" alt="${esc(ph.alt || photoAlt(ph.src))}">` : ""}
        <div class="day__body">
          <p class="day__label">${esc(d.label)}</p>
          <p class="day__meta"><span class="day__date nowrap">${esc(d.date)}</span> <span class="sep" aria-hidden="true">·</span> <span class="day__length nowrap">${esc(d.length)}</span></p>
          <h3 class="day__title">${esc(d.title)}</h3>
          <p class="day__text">${esc(d.body)}</p>
        </div>
      </article>`;
    })
    .join("");

  const speakers = copy.speakers
    .map(
      (sp) => `<li class="speaker">
        <div class="speaker__ring"><img class="speaker__photo" src="${asset(sp.photo)}" alt="Portrait of ${esc(sp.name)}"></div>
        <h3 class="speaker__name">${esc(sp.name)}</h3>
        <p class="speaker__title">${esc(sp.title)}</p>
        <p class="speaker__org">${esc(sp.org)}</p>
      </li>`
    )
    .join("");

  const themes = copy.themes
    .map((t, i) => `<li class="theme"><span class="theme__index" aria-hidden="true">0${i + 1}</span><h3 class="theme__title">${esc(t.title)}</h3><p class="theme__text">${esc(t.body)}</p></li>`)
    .join("");

  const funders = copy.funders.map((f) => `<li class="funder funder--${file(f).replace(".png", "")}"><img src="${asset(f)}" alt="${FUNDER_ALT[file(f)]}"></li>`).join("");

  const f = copy.footer;
  const socials = f.socials
    .map(social)
    .map((so) => `<li><a class="social social--${so.key}" href="#${so.key}">${so.icon}<span>${esc(so.label)}</span></a></li>`)
    .join("");

  return `
  <section class="hero" id="home">${C.hero ? C.hero(copy, { logo, anniversarySlot, ctas, meta, esc, asset, photoAlt, ROOT }) : defaultHero(copy)}</section>

  <section class="intro" aria-label="About Remarkable">
    <div class="container"><p class="intro__text">${esc(copy.intro)}</p></div>
  </section>

  <section class="stats" aria-labelledby="stats-h">
    <div class="container">
      <h2 class="stats__caption" id="stats-h">${esc(s.caption)}</h2>
      <ul class="stats__grid">${stats}</ul>
    </div>
  </section>

  <section class="days" id="agenda" aria-labelledby="days-h">
    <div class="container">
      <h2 class="visually-hidden" id="days-h">${esc(copy.days.map((d) => d.label).join(" and "))}</h2>
      <div class="days__grid">${days}</div>
    </div>
  </section>

  <section class="speakers" id="speakers" aria-labelledby="speakers-h">
    <div class="container">
      <div class="section-head">
        <h2 class="section-title" id="speakers-h">${esc(copy.speakers_heading)}</h2>
        <p class="section-note">${esc(copy.speakers_note)}</p>
      </div>
      <ul class="speakers__grid">${speakers}</ul>
    </div>
  </section>

  <section class="themes" aria-labelledby="themes-h">
    <div class="container">
      <div class="section-head">
        <h2 class="section-title" id="themes-h">${esc(copy.themes_heading)}</h2>
        <p class="section-note">${esc(copy.themes_note)}</p>
      </div>
      <ul class="themes__grid">${themes}</ul>
    </div>
  </section>

  <section class="recap" aria-labelledby="recap-h">
    <div class="container">
      <h2 class="section-title" id="recap-h">${esc(copy.recap.heading)}</h2>
      <div class="recap__media">
        <img class="recap__thumb" src="${asset(copy.recap.thumbnail)}" alt="${esc(photoAlt(copy.recap.thumbnail))}">
        <button class="recap__play" type="button" aria-label="Play the Remarkable 2026 recap video">
          <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M8 5.5v13l11-6.5z" fill="currentColor"/></svg>
        </button>
      </div>
    </div>
  </section>

  <section class="funders" id="partners" aria-labelledby="funders-h">
    <div class="container">
      <h2 class="funders__title" id="funders-h">${esc(copy.funders_heading)}</h2>
      <ul class="funders__row">${funders}</ul>
    </div>
  </section>

  <footer class="footer">
    <div class="container">
      <div class="footer__top">
        <div class="footer__brand">
          ${logo("knockout", "footer__logo")}
          <p class="footer__credit">${esc(f.ontario_credit)}</p>
        </div>
        <div class="footer__col">
          <h2 class="footer__h">Contact</h2>
          <p><a href="mailto:${esc(f.contact)}">${esc(f.contact)}</a></p>
          <p class="footer__hashtag">${esc(f.hashtag)}</p>
        </div>
        <div class="footer__col">
          <h2 class="footer__h">Follow</h2>
          <ul class="footer__socials">${socials}</ul>
        </div>
      </div>
      <div class="footer__bottom">
        <p class="footer__legal">${esc(f.legal)}</p>
        <p class="footer__copy">${esc(f.copyright)}</p>
      </div>
    </div>
  </footer>`;
}

async function waitForAssets() {
  await document.fonts.ready;
  const imgs = [...document.images];
  await Promise.all(imgs.map((im) => (im.complete ? Promise.resolve() : new Promise((r) => { im.onload = im.onerror = r; }))));
  const broken = imgs.filter((im) => !im.naturalWidth).map((im) => im.getAttribute("src"));
  document.documentElement.dataset.broken = broken.join(",");
}

async function render() {
  const C = window.CONCEPT || {};
  const copy = await fetch(ROOT + "content/copy.json").then((r) => r.json());
  const label = copy.frame_label.replace("{X}", C.letter || "?");
  document.body.insertAdjacentHTML(
    "afterbegin",
    `<p class="frame-label">${esc(label)}</p>${nav(copy, C.navLogo || "colour")}<main>${sections(copy, C)}</main>`
  );
  if (C.after) C.after(copy);
  await waitForAssets();
  document.documentElement.dataset.ready = "true";
}

render();
