/* Remarkable 2027 mockups: shared renderer.
   Loads content/copy.json and builds one of four pages, chosen by <body data-page="home|agenda|speakers|faq">.
   Every page gets the same nav (with EN/FR switch) and footer; the home page also gets funders.
   Each concept sets window.CONCEPT (in its concept.js) before this script runs:
     letter                "A" | "B" | "C"               (frame label)
     label                 replaces the whole frame label (optional, e.g. the wireframe)
     navLogo               "colour" | "knockout"          (nav logo variant, default colour)
     hero(copy, h)         inner HTML of the home hero (optional)
     pageHeader(copy, page, h)  inner HTML of the header band on agenda/speakers/faq (optional)
     dayPhotos             [{src, alt}, ...]               (optional photo per day card)
     after(copy)           runs once everything is in the DOM (optional)
   When all fonts and images have loaded, <html data-ready="true"> is set for the export script. */

const ROOT = "../../";

const PHOTO_ALT = {
  "attendees-group-photo.jpg": "Group of attendees taking a selfie in front of the Vector backdrop",
  "audience-listening.jpg": "Attendees listening closely during a session",
  "auditorium-crowd.jpg": "Packed auditorium during a Remarkable 2026 session",
  "auditorium-fireside-screens.jpg": "Full auditorium watching a fireside chat on the main screens",
  "auditorium-keynote.jpg": "Keynote speaker on stage with the talk shown on large screens",
  "auditorium-room-overview.jpg": "Overview of the auditorium during a fireside chat",
  "auditorium-wide-stage.jpg": "Wide view of the Remarkable 2026 main stage and auditorium",
  "executive-breakfast-networking.jpg": "Guests greeting each other at the executive breakfast",
  "executive-breakfast-panel.jpg": "Panel discussion at the executive breakfast beside a Vector banner",
  "networking-crowd.jpg": "Attendees talking in a busy hallway between sessions",
  "networking-hallway.jpg": "Crowd networking in the reception hall",
  "posters-conversation.jpg": "Researchers talking beside their poster",
  "posters-discussion.jpg": "Researchers discussing a poster at the Remarkable 2026 poster session",
  "registration-desk.jpg": "Staff handing out name badges at the registration desk",
  "speaker-at-podium.jpg": "Speaker addressing the audience from the Vector podium",
  "stage-fireside-chat.jpg": "Two speakers in a fireside chat in front of the Remarkable backdrop",
  "stage-remarkable-backdrop.jpg": "Speaker presenting in front of the Remarkable backdrop",
  "workshop-room.jpg": "Attendees seated in a full workshop room",
  "workshop-speaker-smiling.jpg": "Smiling workshop presenter at Remarkable 2026",
};

const PAGES = { Home: "index.html", Agenda: "agenda.html", Speakers: "speakers.html", FAQ: "faq.html" };
const PAGE_OF = { home: "Home", agenda: "Agenda", speakers: "Speakers", faq: "FAQ" };

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

/* The agency's 10th-anniversary mark, full colour on a white disc (it is black and magenta, so it can't sit on the gradient directly) */
function anniversaryMark(copy, cls = "") {
  const m = copy.hero.anniversary_mark;
  return `<div class="anniv-mark ${cls}"><img src="${asset(m.src)}" alt="${esc(m.alt)}" width="620" height="646"></div>`;
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

/* Intro: bold lead sentence, body paragraphs, bold closer (structure from the reg-site copy doc) */
function intro(copy) {
  const [lead, ...rest] = copy.intro;
  return `<p class="intro__lead">${esc(lead)}</p>
    ${rest.map((t) => `<p class="intro__text">${esc(t)}</p>`).join("")}
    <p class="intro__closer">${esc(copy.intro_closer)}</p>`;
}

const ARROW = `<svg class="arrow-icon" viewBox="0 0 20 20" aria-hidden="true"><path d="M4 10h11m-4-4 4 4-4 4" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>`;
const moreLink = (href, label) => `<a class="more-link" href="${href}">${esc(label)}${ARROW}</a>`;

function defaultHero(copy) {
  const h = copy.hero;
  return `<div class="container hero__inner">
    <div class="hero__copy">
      <p class="eyebrow">${esc(h.eyebrow)}</p>
      <h1 class="hero__title">${esc(h.event_name)}</h1>
      <p class="hero__tagline">${esc(h.tagline)}</p>
      <p class="hero__meta">${meta(copy)}</p>
      <p class="hero__address">${esc(h.venue_address)}</p>
      ${ctas(copy)}
      <p class="small-print">${esc(h.small_print)}</p>
    </div>
    ${anniversarySlot(copy)}
  </div>`;
}

function defaultPageHeader(copy, page) {
  const pc = copy[`${page}_page`];
  return `<div class="container page-hero__inner">
    <p class="eyebrow"><span class="nowrap">${esc(copy.hero.event_name)}</span> <span class="sep" aria-hidden="true">|</span> ${meta(copy)}</p>
    <h1 class="page-hero__title">${esc(pc.title)}</h1>
    <p class="page-hero__intro">${esc(pc.intro)}</p>
  </div>`;
}

function nav(copy, variant, page) {
  const links = copy.nav
    .map((l) => `<li><a href="${PAGES[l]}"${PAGE_OF[page] === l ? ' aria-current="page"' : ""}>${esc(l)}</a></li>`)
    .join("");
  const lang = copy.language;
  return `<header class="nav">
    <div class="container nav__inner">
      <a class="nav__logo" href="index.html">${logo(variant)}</a>
      <nav class="nav__links" aria-label="Main"><ul>${links}</ul></nav>
      <div class="nav__actions">
        <div class="lang" role="group" aria-label="${esc(lang.label)}">
          <span class="lang__opt lang__opt--current" aria-current="true">${esc(lang.current)}</span>
          <a class="lang__opt" href="#fr" lang="fr" hreflang="fr" aria-label="${esc(lang.other_name)}">${esc(lang.other)}</a>
        </div>
        <a class="btn btn--primary btn--nav" href="#register">${esc(copy.nav_cta)}</a>
        <button class="nav__burger" type="button" aria-label="Open menu" aria-expanded="false"><span></span><span></span><span></span></button>
      </div>
    </div>
  </header>`;
}

/* ---------- Shared blocks ---------- */

function dayCards(copy, C, withLink) {
  const days = copy.days
    .map((d, i) => {
      const ph = C.dayPhotos && C.dayPhotos[i];
      return `<article class="day">
        ${ph ? `<img class="day__photo" src="${asset(ph.src)}" alt="${esc(ph.alt || photoAlt(ph.src))}">` : ""}
        <div class="day__body">
          <p class="day__label">${esc(d.label)}</p>
          <p class="day__meta"><span class="day__date nowrap">${esc(d.date)}<span class="sep" aria-hidden="true">·</span></span> <span class="day__length nowrap">${esc(d.length)}</span></p>
          <h3 class="day__title">${esc(d.title)}</h3>
          <p class="day__text">${esc(d.body)}</p>
        </div>
      </article>`;
    })
    .join("");
  return `<div class="days__grid">${days}</div>
    <div class="days__foot"><p class="days__note">${esc(copy.agenda_note)}</p>${withLink ? moreLink("agenda.html", copy.home_links.agenda) : ""}</div>`;
}

function speakerPhoto(sp) {
  return `<div class="speaker__ring"><img class="speaker__photo" src="${asset(sp.photo)}" alt="Portrait of ${esc(sp.name)}"></div>`;
}

function speakerCard(sp, full) {
  return `<li class="speaker">
    ${speakerPhoto(sp)}
    <div class="speaker__info">
      ${full ? `<p class="speaker__session">${esc(sp.session)}</p>` : ""}
      <h3 class="speaker__name">${esc(sp.name)}</h3>
      <p class="speaker__title">${esc(sp.title)}</p>
      <p class="speaker__org">${esc(sp.org)}</p>
      ${full ? `<p class="speaker__bio">${esc(sp.bio)}</p>` : ""}
    </div>
  </li>`;
}

function funders(copy) {
  const items = copy.funders.map((f) => `<li class="funder funder--${file(f).replace(".png", "")}"><img src="${asset(f)}" alt="${FUNDER_ALT[file(f)]}"></li>`).join("");
  return `<section class="funders" aria-labelledby="funders-h">
    <div class="container">
      <h2 class="funders__title" id="funders-h">${esc(copy.funders_heading)}</h2>
      <ul class="funders__row">${items}</ul>
    </div>
  </section>`;
}

function gallery(copy) {
  const g = copy.gallery;
  const slides = g.photos.map((p, i) => `<li class="gallery__slide"><img src="${asset(p)}" alt="${esc(photoAlt(p))}" ${i > 3 ? 'loading="lazy"' : ""}></li>`).join("");
  const dots = g.photos.map((_, i) => `<span class="gallery__dot${i === 0 ? " is-active" : ""}"></span>`).join("");
  return `<section class="gallery" aria-labelledby="gallery-h">
    <div class="container gallery__head">
      <div>
        <h2 class="section-title" id="gallery-h">${esc(g.heading)}</h2>
        <p class="section-note">${esc(g.note)}</p>
      </div>
      <div class="gallery__controls">
        <button class="gallery__btn gallery__btn--prev" type="button" aria-label="Previous photos" disabled>${ARROW}</button>
        <button class="gallery__btn gallery__btn--next" type="button" aria-label="Next photos">${ARROW}</button>
      </div>
    </div>
    <div class="gallery__viewport" tabindex="0" aria-label="Photo carousel, use the arrow buttons or scroll to browse">
      <ul class="gallery__track">${slides}</ul>
    </div>
    <div class="container"><div class="gallery__dots" aria-hidden="true">${dots}</div></div>
  </section>`;
}

/* Carousel: manual only (buttons / scroll). Nothing advances on its own. */
function wireGallery() {
  const vp = document.querySelector(".gallery__viewport");
  if (!vp) return;
  const prev = document.querySelector(".gallery__btn--prev");
  const next = document.querySelector(".gallery__btn--next");
  const dots = [...document.querySelectorAll(".gallery__dot")];
  const step = () => vp.querySelector(".gallery__slide").getBoundingClientRect().width + 24;
  prev.addEventListener("click", () => vp.scrollBy({ left: -step(), behavior: "smooth" }));
  next.addEventListener("click", () => vp.scrollBy({ left: step(), behavior: "smooth" }));
  vp.addEventListener("scroll", () => {
    const max = vp.scrollWidth - vp.clientWidth;
    prev.disabled = vp.scrollLeft <= 2;
    next.disabled = vp.scrollLeft >= max - 2;
    const i = Math.round(vp.scrollLeft / step());
    dots.forEach((d, k) => d.classList.toggle("is-active", k === i));
  });
}

function footer(copy) {
  const f = copy.footer;
  const socials = f.socials
    .map(social)
    .map((so) => `<li><a class="social social--${so.key}" href="#${so.key}">${so.icon}<span>${esc(so.label)}</span></a></li>`)
    .join("");
  const links = f.links.map((col) => `<ul>${col.map((l) => `<li><a href="#">${esc(l)}</a></li>`).join("")}</ul>`).join("");
  return `<footer class="footer">
    <div class="container">
      <div class="footer__top">
        <div class="footer__brand">
          ${logo("knockout", "footer__logo")}
          <p class="footer__credit">${esc(f.ontario_credit)}</p>
        </div>
        <div class="footer__col">
          <p class="footer__h">${esc(f.contact_line)}</p>
          <p><a href="mailto:${esc(f.contact)}">${esc(f.contact)}</a></p>
          <p class="footer__hashtag">${esc(f.hashtag)}</p>
        </div>
        <div class="footer__col">
          <p class="footer__h">${esc(f.socials_label)}</p>
          <ul class="footer__socials">${socials}</ul>
        </div>
        <nav class="footer__links" aria-label="Vector Institute">${links}</nav>
      </div>
      <div class="footer__bottom">
        <p class="footer__legal">${esc(f.legal)}</p>
        <p class="footer__copy">${esc(f.copyright)}</p>
      </div>
    </div>
  </footer>`;
}

/* ---------- Pages ---------- */

function homePage(copy, C, h) {
  const s = copy.stats;
  const stats = s.items.map((it) => `<li class="stat"><span class="stat__value">${esc(it.value)}</span><span class="stat__label">${esc(it.label)}</span></li>`).join("");
  return `
  <section class="hero" id="home">${C.hero ? C.hero(copy, h) : defaultHero(copy)}</section>

  <section class="intro" aria-label="About Remarkable">
    <div class="container"><div class="intro__body">${intro(copy)}</div></div>
  </section>

  <section class="stats" aria-labelledby="stats-h">
    <div class="container">
      <h2 class="stats__caption" id="stats-h">${esc(s.caption)}</h2>
      <ul class="stats__grid">${stats}</ul>
    </div>
  </section>

  <section class="days" aria-labelledby="days-h">
    <div class="container">
      <h2 class="visually-hidden" id="days-h">${esc(copy.days.map((d) => d.label).join(" and "))}</h2>
      ${dayCards(copy, C, true)}
    </div>
  </section>

  <section class="speakers speakers--teaser" aria-labelledby="speakers-h">
    <div class="container">
      <div class="section-head">
        <h2 class="section-title" id="speakers-h">${esc(copy.speakers_heading)}</h2>
        <p class="section-note">${esc(copy.speakers_note)}</p>
      </div>
      <ul class="speakers__grid">${copy.speakers.map((sp) => speakerCard(sp, false)).join("")}</ul>
      <div class="section-foot">${moreLink("speakers.html", copy.home_links.speakers)}</div>
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

  ${gallery(copy)}
  ${funders(copy)}`;
}

function agendaPage(copy, C) {
  const ap = copy.agenda_page;
  const tabs = copy.days.map((d, i) => `<a class="day-tabs__tab${i === 0 ? " is-active" : ""}" href="#day-${i + 1}"${i === 0 ? ' aria-current="true"' : ""}><span class="day-tabs__label">${esc(d.label)}</span><span class="day-tabs__date">${esc(d.date)}</span></a>`).join("");
  const days = copy.days
    .map((d, i) => {
      const rows = ap.days[i].sessions
        .map(
          (s) => `<li class="session session--${s.type.toLowerCase().replace(/[^a-z]+/g, "-")}">
          <p class="session__time">${esc(s.time)}</p>
          <div class="session__main">
            <p class="session__type">${esc(s.type)}</p>
            <h3 class="session__title">${esc(s.title)}</h3>
            ${s.body ? `<p class="session__body">${esc(s.body)}</p>` : ""}
            ${s.speakers ? `<p class="session__speakers">${esc(s.speakers)}</p>` : ""}
          </div>
          <div class="session__where">
            ${s.where ? `<p>${esc(s.where)}</p>` : ""}
            ${s.livestream ? `<p class="tag tag--live">${esc(ap.livestream_label)}</p>` : ""}
          </div>
        </li>`
        )
        .join("");
      return `<section class="agenda-day" id="day-${i + 1}" aria-labelledby="day-${i + 1}-h">
        <header class="agenda-day__head">
          <p class="day__label">${esc(d.label)}</p>
          <p class="day__meta"><span class="nowrap">${esc(d.date)}<span class="sep" aria-hidden="true">·</span></span> <span class="nowrap">${esc(d.length)}</span></p>
          <h2 class="agenda-day__title" id="day-${i + 1}-h">${esc(d.title)}</h2>
          <p class="agenda-day__text">${esc(d.body)}</p>
        </header>
        <ol class="sessions">${rows}</ol>
      </section>`;
    })
    .join("");
  return `
  <section class="page-hero">${C.pageHeader ? C.pageHeader(copy, "agenda", helpers) : defaultPageHeader(copy, "agenda")}</section>
  <section class="agenda">
    <div class="container">
      <nav class="day-tabs" aria-label="Agenda days">${tabs}</nav>
      <p class="agenda__note">${esc(ap.note)}</p>
      ${days}
    </div>
  </section>`;
}

function speakersPage(copy, C) {
  const sp = copy.speakers_page;
  return `
  <section class="page-hero">${C.pageHeader ? C.pageHeader(copy, "speakers", helpers) : defaultPageHeader(copy, "speakers")}</section>
  <section class="speakers speakers--full" aria-label="${esc(sp.title)}">
    <div class="container">
      <ul class="speakers__grid">${copy.speakers.map((s) => speakerCard(s, true)).join("")}</ul>
      <p class="speakers__more">${esc(sp.more)}</p>
    </div>
  </section>`;
}

function faqPage(copy, C) {
  const fp = copy.faq_page;
  const groups = fp.groups
    .map(
      (g, gi) => `<section class="faq-group" aria-labelledby="faq-${gi}">
        <h2 class="faq-group__title" id="faq-${gi}">${esc(g.heading)}</h2>
        <div class="faq-group__items">
          ${g.items.map((it) => `<details class="faq" open><summary class="faq__q">${esc(it.q)}<span class="faq__icon" aria-hidden="true"></span></summary><p class="faq__a">${esc(it.a)}</p></details>`).join("")}
        </div>
      </section>`
    )
    .join("");
  return `
  <section class="page-hero">${C.pageHeader ? C.pageHeader(copy, "faq", helpers) : defaultPageHeader(copy, "faq")}</section>
  <section class="faqs"><div class="container">${groups}</div></section>`;
}

const helpers = { logo, anniversarySlot, anniversaryMark, ctas, meta, intro, moreLink, esc, asset, photoAlt, ROOT };

async function waitForAssets() {
  await document.fonts.ready;
  const imgs = [...document.images];
  imgs.forEach((im) => (im.loading = "eager"));
  await Promise.all(imgs.map((im) => (im.complete ? Promise.resolve() : new Promise((r) => { im.onload = im.onerror = r; }))));
  const broken = imgs.filter((im) => !im.naturalWidth).map((im) => im.getAttribute("src"));
  document.documentElement.dataset.broken = broken.join(",");
}

async function render() {
  const C = window.CONCEPT || {};
  const page = document.body.dataset.page || "home";
  const copy = await fetch(ROOT + "content/copy.json").then((r) => r.json());
  const label = (C.label || copy.frame_label.replace("{X}", C.letter || "?")) + (page === "home" ? "" : ` · ${PAGE_OF[page]}`);
  const content = { home: homePage, agenda: agendaPage, speakers: speakersPage, faq: faqPage }[page](copy, C, helpers);
  document.body.classList.add(`page-${page}`);
  document.body.insertAdjacentHTML(
    "afterbegin",
    `<p class="frame-label">${esc(label)}</p>${nav(copy, C.navLogo || "colour", page)}<main>${content}</main>${footer(copy)}`
  );
  wireGallery();
  if (C.after) C.after(copy, page);
  await waitForAssets();
  document.documentElement.dataset.ready = "true";
}

render();
