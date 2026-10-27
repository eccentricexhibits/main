(() => {
  'use strict';
  const C = window.REMARKABLE_COPY;
  const page = document.body.dataset.page || 'index';
  // Alternate inner-page header (split arrow photo): ?hero=split on the live pages, or set by the review viewer.
  if (window.REMARKABLE_ALT_HERO || /[?&]hero=split\b/.test(location.search)) document.documentElement.classList.add('alt-hero');
  const HERO_PHOTOS = {
    agenda: {src:'assets/photos-2026/stage-remarkable-backdrop.jpg', alt:'The Remarkable 2026 main stage backdrop.', align:'xMaxYMid', phone:'65% 50%'},
    speakers: {src:'assets/photos-2026/speaker-at-podium.jpg', alt:'A speaker at the podium at Remarkable 2026.', align:'xMidYMin', phone:'50% 0%'},
    faq: {src:'assets/photos-2026/posters-discussion.jpg', alt:'Attendees discussing research posters at Remarkable 2026.', align:'xMidYMid', phone:'50% 20%'}
  };
  const E = s => String(s ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const arrow = (cls = '', white = false) => `<span class="vector-arrow ${cls}${white ? ' is-white' : ''}" aria-hidden="true"></span>`;
  const pixels = cls => `<span class="vector-pixels ${cls || ''}" aria-hidden="true"></span>`;
  const ornamentPair = (shape, cls) => `<span class="ornament-stack ${cls}" aria-hidden="true"><span class="vector-${shape} ornament-shadow"></span><span class="vector-${shape} ornament-solid"></span></span>`;
  const photo = (src, alt, cls = '', eager = false) => `<img src="${E(src)}" alt="${E(alt)}" class="${cls}" loading="${eager ? 'eager' : 'lazy'}" decoding="async">`;
  const sectionLabel = (n, text) => `<div class="section-label"><span>${n}</span><span>${text}</span></div>`;
  const registerButton = (text = 'Register in person', cls = 'button-dark', kind = 'inperson') => `<button class="button ${cls}" data-register="${kind}"><span>${text}</span>${arrow('button-arrow')}</button>`;
  const textLink = (href, text, cls = '') => `<a class="text-link ${cls}" href="${href}">${text}${arrow('link-arrow')}</a>`;

  function header() {
    const links = ['Home', 'Agenda', 'Speakers', 'FAQ'];
    const paths = ['index', 'agenda', 'speakers', 'faq'];
    return `<header class="site-header" id="top"><div class="header-inner">
      <a class="brand" href="index.html" aria-label="Vector Institute, Remarkable 2027 home">${photo('assets/logos/logo-bilingual-knockout-white.png','Vector Institute | Institut Vecteur','',true)}</a>
      <button class="menu-toggle" aria-controls="site-nav" aria-expanded="false"><span class="menu-label">Menu</span><span class="menu-lines" aria-hidden="true"></span></button>
      <nav class="site-nav" id="site-nav" aria-label="Main navigation">${links.map((n, i) => `<a href="${paths[i]}.html"${paths[i] === page ? ' aria-current="page"' : ''}>${n}</a>`).join('')}<button class="nav-register" data-register="choose">Register ${arrow('button-arrow')}</button></nav>
    </div></header>`;
  }

  function editionRow() {
    return `<div class="edition-row"><a href="index.html">Remarkable <span>2027</span></a><p>February 18–19, 2027 <span class="meta-divider">/</span> Hilton Toronto</p></div>`;
  }

  function closing() {
    return `<section class="closing" aria-labelledby="closing-title"><div class="wrap closing-inner">
      <div class="closing-copy"><h2 id="closing-title">Be part of<br>what comes next.</h2><div class="closing-actions">${registerButton('Register now','closing-register','choose')}</div></div>
      ${pixels('closing-pixels')}
    </div></section>`;
  }

  function footer() {
    return `<section class="funders wrap" aria-label="Event funders"><p>${E(C.funders_heading)}</p><div class="funder-logos">${C.funders.map((p,i) => photo(p, ['Government of Canada','Government of Ontario','CIFAR'][i])).join('')}</div><p class="ontario-credit">${E(C.footer.ontario_credit)}</p></section>
    <footer class="site-footer"><div class="wrap"><div class="footer-top"><a class="brand" href="index.html">${photo('assets/logos/logo-bilingual-knockout-white.png','Vector Institute | Institut Vecteur')}</a><div class="footer-contact"><p>Keep the conversation going.</p><a href="mailto:${E(C.footer.contact)}">${E(C.footer.contact)}</a></div><a class="back-top" href="#top" aria-label="Back to top">${arrow()}<span>Back to top</span></a></div>
      <div class="footer-links"><p>${E(C.footer.hashtag)}</p><nav aria-label="Footer navigation"><a href="index.html">Home</a><a href="agenda.html">Agenda</a><a href="speakers.html">Speakers</a><a href="faq.html">FAQ</a></nav><span>Remarkable in progress.</span></div>
      <p class="legal">${E(C.footer.legal)}</p><div class="footer-bottom"><span>© Vector Institute · 2027</span></div></div></footer>`;
  }

  function speakerCard(s, i, big = false) {
    return `<article class="speaker-card${big ? ' speaker-card-full' : ''}" id="speaker-${i + 1}"><button class="speaker-open" data-speaker="${i}" aria-label="View ${E(s.name)}'s profile"><span class="portrait">${photo(s.photo,s.name)}</span><span class="speaker-copy"><span class="speaker-session">${E(s.session)}</span><span class="speaker-name">${E(s.name)}</span><span class="speaker-role">${E(s.title)}</span><span class="speaker-org">${E(s.org)}</span><span class="profile-link">View profile <span aria-hidden="true">+</span></span></span></button></article>`;
  }

  function home() {
    return `<main id="main">
      <section class="home-hero wrap" aria-labelledby="event-title"><div class="hero-kicker"><p>Vector Institute presents</p><p>Hilton Toronto</p></div>
        <h1 class="event-title" id="event-title"><span class="event-word">Remarkable</span><span class="sr-only"> 2027</span></h1>
        <div class="hero-composition"><div class="hero-left"><div class="hero-year" aria-hidden="true">2027<span class="year-period">.</span></div><p class="hero-date">February 18–19, 2027</p>${arrow('mobile-hero-arrow')}<h2>Where AI possibilities<br>come to life.</h2><div class="hero-actions">${registerButton('Register now','button-dark button-hero','inperson')}</div></div>
          <div class="hero-visual">${photo('assets/photos-2026/auditorium-crowd.jpg','The Remarkable 2026 community gathered in a magenta-lit auditorium.','hero-photo',true)}${arrow('hero-arrow')}<span class="photo-caption"><strong>R E M A R K A B L E</strong><small>THE COMMUNITY · 2026</small></span></div></div>
      </section>
      <div class="event-ribbon"><div class="wrap"><span>World-class research.</span><span>Real-world impact.</span><span>Remarkable in progress.</span></div></div>
      <section class="about-section wrap section-space" id="about">${sectionLabel('01', 'The meeting point')}<div class="about-grid"><h2 class="display-heading">AI ambition.<br>Meet <span>AI action.</span></h2><div class="about-copy"><p class="lead">${E(C.intro[0])}</p><p>${E(C.intro[1])}</p><p>${E(C.intro[2])}</p></div></div></section>
      <section class="experience-section" aria-labelledby="experience-title"><div class="wrap section-space">${sectionLabel('02','The experience')}<div class="experience-heading"><h2 class="display-heading" id="experience-title">Two days.<br>New possibilities.</h2><p>${E(C.intro[3])}</p></div>
        <div class="day-stories">${C.days.map((d,i) => `<a class="day-story" href="agenda.html?day=${i + 1}"><span class="day-number">0${i+1}</span><span class="day-story-main"><span class="day-date">${E(d.date)} <span>/ ${E(d.length)}</span></span><span class="day-title">${E(d.title)}</span><span class="day-body">${E(d.body)}</span></span>${arrow('day-arrow')}</a>`).join('')}</div>
        <div class="experience-bottom"><p>${E(C.intro_closer)}</p>${textLink('agenda.html', 'Explore the program')}</div></div></section>
      <section class="home-speakers" aria-labelledby="speakers-title"><div class="wrap section-space">${sectionLabel('03','The people')}<div class="section-title-row"><h2 class="display-heading" id="speakers-title">Brilliant minds.<br>Big conversations.</h2>${textLink('speakers.html','Meet the speakers')}</div><div class="speaker-trio">${C.speakers.slice(0,3).map((s,i)=>speakerCard(s,i)).join('')}</div></div></section>
      <section class="recap-section wrap section-space" aria-labelledby="recap-title">${sectionLabel('04','A look back, a step forward')}<div class="recap-grid"><div class="recap-copy"><h2 class="display-heading" id="recap-title">This is<br>remarkable.</h2><p>Research. Connections. The moments that move us forward.</p><button class="text-link" data-recap>Watch the 2026 recap <span class="play-small" aria-hidden="true">▶</span></button></div><button class="recap-image" data-recap aria-label="Remarkable 2026 recap">${photo('assets/photos-2026/stage-fireside-chat.jpg','A conversation on stage at Remarkable 2026.')}<span class="play-disc" aria-hidden="true">▶</span></button></div>
        <div class="stats-header"><p>${E(C.stats.caption)}</p></div><div class="stats-grid">${C.stats.items.map(s=>`<div><span class="stat-value">${E(s.value)}</span><span class="stat-label">${E(s.label)}</span></div>`).join('')}</div>
      </section>
      <section class="gallery-section" aria-labelledby="gallery-title"><div class="wrap"><div class="gallery-heading"><div><p class="eyebrow">Remarkable 2026 in photos</p><h2 id="gallery-title">More than a conference.</h2></div><div class="gallery-controls"><button data-gallery="-1" aria-label="Previous photos">←</button><span id="gallery-position" aria-live="polite">01 / 09</span><button data-gallery="1" aria-label="Next photos">→</button></div></div><div class="gallery-track" id="gallery-track">${C.gallery.photos.map((p,i)=>`<button class="gallery-photo" data-photo="${i}" aria-label="Open photo ${i+1} of Remarkable 2026">${photo(p, galleryCaption(i))}<span>${String(i+1).padStart(2,'0')} <span>${galleryCaption(i)}</span></span></button>`).join('')}</div></div></section>
      ${closing()}
    </main>`;
  }

  function innerHeader(title, label, extraClass = '', ornament = '') {
    const hp = HERO_PHOTOS[page];
    const split = hp ? `<div class="inner-split" aria-hidden="true"></div>` : '';
    const fade = hp ? `<div class="inner-fade" aria-hidden="true">${photo(hp.src, '', '', true).replace('<img ', `<img style="object-position:${hp.phone}" `)}</div>` : '';
    return `<section class="inner-hero wrap ${extraClass}">${editionRow()}<div class="inner-title-row"><div><p class="eyebrow">${label}</p><h1>${title}</h1></div>${ornament}${split}</div>${fade}</section>`;
  }

  /* Split header: the photo is cut along the shaft of the extended Vector arrow (brand guide p. 6).
     Arrow path from assets/brand-elements/vector-arrow-extended.svg (194 x 390); its shaft centre line is
     x = 11.2 + K * (390 - y), so it leans right by K per unit of height. The frame is redrawn at its real
     proportions, so nothing is cropped and the arrow tip touches the top edge. */
  const ARROW_PATH = 'M167.314 0L106.322 26.684L95.732 51.671L143.899 32.362L0 389.936L22.473 390L162.07 39.437L183.41 87.036L194 61.837Z';
  const ARROW_K = 0.4006;
  function drawSplit(el) {
    const hp = HERO_PHOTOS[page]; const r = el.getBoundingClientRect();
    if (!hp || r.width < 10 || r.height < 10) return;
    const H = 480, W = Math.round(r.width * H / r.height);
    const seam = Math.min(160, W * .25);                 // where the shaft meets the bottom edge
    const Ha = H * 1.08, s = Ha / 390;                   // arrow slightly taller than the frame; tail runs off the bottom
    const Ax = seam - s * (11.2 + ARROW_K * (390 - H / s));
    const topX = seam + ARROW_K * H;
    const src = (window.REMARKABLE_ASSETS && window.REMARKABLE_ASSETS[hp.src]) || hp.src;
    const id = 'split-' + page;
    el.innerHTML = `<svg viewBox="0 0 ${W} ${H}" preserveAspectRatio="xMinYMid slice" width="100%" height="100%" focusable="false">
      <defs><clipPath id="${id}"><polygon points="${seam},${H} ${topX},0 ${W},0 ${W},${H}"/></clipPath></defs>
      <image href="${E(src)}" x="${seam}" y="0" width="${W - seam}" height="${H}" preserveAspectRatio="${hp.align} slice" clip-path="url(#${id})"/>
      <path d="${ARROW_PATH}" fill="#EB088A" transform="translate(${Ax.toFixed(2)} 0) scale(${s.toFixed(4)})"/>
    </svg>`;
  }


  function agenda() {
    return `<main id="main">${innerHeader('Agenda.','The program','agenda-hero',ornamentPair('pluses','agenda-hero-pluses'))}
      <section class="agenda-section wrap" aria-label="Conference schedule"><div class="agenda-intro"><p class="lead">${E(C.agenda_page.intro)}</p><p class="small-note">Agenda subject to change.<br>All times Eastern Standard Time (EST).</p></div>
      <div class="agenda-tabs" role="tablist" aria-label="Select conference day">${C.days.map((d,i)=>`<button id="day-tab-${i+1}" role="tab" aria-selected="${i===0}" aria-controls="day-panel-${i+1}" tabindex="${i===0?0:-1}" data-day="${i}"><span class="agenda-tab-day">Day 0${i+1}</span><span class="agenda-tab-date"><span class="agenda-tab-weekday">${E(d.date.split(', ')[0])},</span> <span class="agenda-tab-calendar">${E(d.date.split(', ')[1])}</span><small>${E(d.length)}</small></span>${arrow('agenda-tab-arrow')}</button>`).join('')}</div>
      ${C.days.map((d,i)=>`<div class="day-panel" id="day-panel-${i+1}" role="tabpanel" aria-labelledby="day-tab-${i+1}"${i===0?'':' hidden'}><div class="schedule-layout"><aside class="day-sidebar"><span class="eyebrow">February 2027</span><div class="calendar-day">${i===0?'18':'19'}<span>${i===0?'THU':'FRI'}</span></div><h2>${E(d.title)}</h2><p>${E(d.body)}</p><span class="sidebar-note">${i===0?'Main-stage sessions are livestreamed.':'Join us in person for workshops and networking.'}</span></aside><div class="session-list">${C.agenda_page.days[i].sessions.map((s,j)=>`<details class="session${['Break','Lunch','Arrivals','Close','Reception'].includes(s.type)?' session-break':''}" id="session-${i+1}-${j}"><summary><span class="session-time">${E(s.time)}</span><span class="session-title-block"><span class="session-type">${E(s.type)}</span><span class="session-title">${E(s.title)}</span></span><span class="disclosure-plus" aria-hidden="true"></span></summary><div class="session-body">${s.body?`<p>${E(s.body)}</p>`:''}${s.speakers?`<p class="session-speakers">${E(s.speakers)}</p>`:''}<div class="session-meta"><span>${E(s.where)}</span>${s.livestream?'<span class="live-label"><span aria-hidden="true"></span>Livestreamed</span>':''}</div></div></details>`).join('')}</div></div></div>`).join('')}
      </section>${venue()}${closing()}</main>`;
  }

  function speakers() {
    return `<main id="main">${innerHeader('Speakers.','The people','speakers-hero',ornamentPair('pixels','speaker-hero-pixels'))}
      <section class="speakers-section wrap" id="speakers"><div class="speakers-intro"><p class="lead">${E(C.speakers_page.intro)}</p><p>Big ideas begin with<br>remarkable people.</p></div><div class="all-speakers">${C.speakers.map((s,i)=>speakerCard(s,i,true)).join('')}</div></section>
      <section class="speaker-program" id="on-stage" aria-labelledby="on-stage-title"><div class="wrap speaker-program-grid"><div class="speaker-program-copy">${sectionLabel('ON STAGE','Ideas into action')}<h2 id="on-stage-title">See where the<br>conversation goes.</h2>${textLink('agenda.html','Explore the agenda')}</div><figure class="speaker-program-visual">${photo('assets/photos-2026/executive-breakfast-panel.jpg','A panel conversation on stage at Remarkable 2026.','speaker-program-photo')}</figure></div></section>${closing()}</main>`;
  }

  function faq() {
    return `<main id="main">${innerHeader('Good<br>questions.','Frequently asked questions','faq-hero',ornamentPair('arrow','faq-hero-arrow'))}
      <section class="faq-section wrap"><div class="faq-intro"><p class="lead">Answers to common questions about attending Remarkable 2027.</p><p>Can’t find what you need?<br><a href="mailto:events@vectorinstitute.ai">Get in touch with our team.</a></p></div><div class="faq-layout"><nav class="faq-topics" aria-label="FAQ topics">${C.faq_page.groups.map((g,i)=>`<a href="#topic-${i+1}"><span>0${i+1}</span><span class="topic-label">${E(g.heading)}</span><span class="topic-down" aria-hidden="true">↓</span></a>`).join('')}</nav><div class="faq-groups">${C.faq_page.groups.map((g,i)=>`<section class="faq-group" id="topic-${i+1}" aria-labelledby="topic-title-${i+1}"><div class="faq-group-heading"><span>0${i+1}</span><h2 id="topic-title-${i+1}">${E(g.heading)}</h2></div>${g.items.map((q,j)=>`<details class="faq-item"${i===0&&j===0?' open':''}><summary><span>${E(q.q)}</span><span class="disclosure-plus" aria-hidden="true"></span></summary><div class="faq-answer"><p>${E(q.a).replace(/events@vectorinstitute\.ai/g,'<a href="mailto:events@vectorinstitute.ai">events@vectorinstitute.ai</a>')}</p></div></details>`).join('')}</section>`).join('')}</div></div></section>${venue()}${closing()}</main>`;
  }

  function venue() {
    return `<section class="venue-section" id="venue"><div class="wrap venue-grid"><div>${sectionLabel('THE VENUE','Meet us in Toronto')}<h2>Right at the<br>heart of it.</h2><p>Hilton Toronto<br>145 Richmond St W<br>Toronto, Ontario</p>${textLink('faq.html#topic-3','Plan your visit')}</div>${photo('assets/photos-2026/registration-desk.jpg','Welcoming the Remarkable community at the registration desk in 2026.','venue-photo')}</div></section>`;
  }

  function galleryCaption(i) {
    return ['A community in conversation','Research, up close','Connections that count','Ideas put into practice','A remarkable welcome','Better, together','Big conversations','Between the sessions','New perspectives'][i];
  }

  document.getElementById('app').innerHTML = header() + ({index:home,agenda,speakers,faq}[page]||home)() + footer() + `<dialog class="detail-dialog" id="detail-dialog" aria-labelledby="dialog-title"><button class="dialog-close" aria-label="Close dialog">×</button><div class="dialog-content" id="dialog-content"></div></dialog>`;

  const menu = document.querySelector('.menu-toggle');
  const nav = document.getElementById('site-nav');
  function closeMenu() {menu.setAttribute('aria-expanded','false');nav.classList.remove('is-open');}
  menu.addEventListener('click',()=>{const open=menu.getAttribute('aria-expanded')!=='true';menu.setAttribute('aria-expanded',String(open));nav.classList.toggle('is-open',open);});
  document.addEventListener('keydown',e=>{if(e.key==='Escape')closeMenu();});
  window.matchMedia('(min-width: 861px)').addEventListener('change',e=>{if(e.matches)closeMenu();});

  const dialog = document.getElementById('detail-dialog');
  const dialogContent = document.getElementById('dialog-content');
  let restoreFocus;
  function openDialog(html, cls='') {restoreFocus=document.activeElement;dialogContent.innerHTML=html;dialog.className='detail-dialog '+cls;dialog.showModal();document.body.classList.add('dialog-open');}
  function closeDialog() {dialog.close();}
  dialog.querySelector('.dialog-close').addEventListener('click',closeDialog);
  dialog.addEventListener('click',e=>{if(e.target===dialog){const r=dialog.getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)closeDialog();}});
  dialog.addEventListener('close',()=>{document.body.classList.remove('dialog-open');restoreFocus?.focus({preventScroll:true});});

  document.addEventListener('click',e=>{
    const registration=e.target.closest('[data-register]');
    if(registration){closeMenu();const kind=registration.dataset.register;openDialog(`<p class="eyebrow">Remarkable 2027 · Registration</p><h2 id="dialog-title">${kind==='virtual'?'Join from anywhere.':kind==='inperson'?'Be in the room.':'Join the remarkable.'}</h2><p class="dialog-lead">February 18–19, 2027<br>Hilton Toronto + virtual livestream</p><div class="registration-options"><div><h3>In person</h3><p>Use the email address associated with your invitation.</p></div><div><h3>Virtually</h3><p>The main-stage livestream is open to everyone. Viewing details will be shared after registration.</p></div></div><a class="button button-dark" href="mailto:events@vectorinstitute.ai">Contact the event team ${arrow('button-arrow')}</a>`);}
    const speaker=e.target.closest('[data-speaker]');
    if(speaker){const i=Number(speaker.dataset.speaker),s=C.speakers[i];openDialog(`<div class="profile-dialog-top"><span class="portrait">${photo(s.photo,s.name,'',true)}</span><div><p class="eyebrow">Speaker</p><h2 id="dialog-title">${E(s.name)}</h2><p>${E(s.title)}<br><strong>${E(s.org)}</strong></p></div></div><p class="profile-bio">${E(s.bio)}</p><div class="profile-session"><span class="eyebrow">On the program</span><p>${E(s.session)}</p>${textLink('agenda.html?day=1#session-1-'+[2,3,8,7,5,9][i], 'View the agenda')}</div>`,'profile-dialog');}
    if(e.target.closest('[data-recap]')){openDialog(`<p class="eyebrow">A look back</p><h2 id="dialog-title">Remarkable 2026.</h2>${photo('assets/photos-2026/stage-fireside-chat.jpg','A fireside conversation at Remarkable 2026.','recap-dialog-image',true)}<p class="dialog-lead">A meeting of remarkable minds.</p><button class="button button-dark" data-explore-photos>Explore the photos ${arrow('button-arrow')}</button>`);}
    const photoBtn=e.target.closest('[data-photo]');
    if(photoBtn)showPhoto(Number(photoBtn.dataset.photo));
    const nextPhoto=e.target.closest('[data-lightbox]');
    if(nextPhoto)showPhoto(Number(nextPhoto.dataset.lightbox));
    if(e.target.closest('[data-explore-photos]'))showPhoto(0);
  });

  function showPhoto(i) {
    i=(i+C.gallery.photos.length)%C.gallery.photos.length;
    const html=`<p class="eyebrow">Remarkable 2026 · ${String(i+1).padStart(2,'0')} / 09</p><h2 id="dialog-title" class="lightbox-title">${galleryCaption(i)}</h2>${photo(C.gallery.photos[i],galleryCaption(i),'lightbox-image',true)}<div class="lightbox-controls"><button class="text-link" data-lightbox="${i-1}" aria-label="Previous photo">← Previous</button><button class="text-link" data-lightbox="${i+1}" aria-label="Next photo">Next →</button></div>`;
    if(dialog.open){dialogContent.innerHTML=html;dialog.className='detail-dialog photo-dialog';dialog.querySelector('.dialog-close').focus();}else openDialog(html,'photo-dialog');
  }

  const gallery=document.getElementById('gallery-track');
  if(gallery){let galleryIndex=0;document.querySelectorAll('[data-gallery]').forEach(b=>b.addEventListener('click',()=>{const cards=[...gallery.children];galleryIndex=Math.max(0,Math.min(cards.length-1,galleryIndex+Number(b.dataset.gallery)));gallery.scrollTo({left:cards[galleryIndex].offsetLeft,behavior:window.matchMedia('(prefers-reduced-motion: reduce)').matches?'instant':'smooth'});}));gallery.addEventListener('scroll',()=>{const cards=[...gallery.children];galleryIndex=cards.reduce((best,card,i)=>Math.abs(card.offsetLeft-gallery.scrollLeft)<Math.abs(cards[best].offsetLeft-gallery.scrollLeft)?i:best,0);document.getElementById('gallery-position').textContent=`${String(galleryIndex+1).padStart(2,'0')} / 09`;},{passive:true});}

  const dayTabs=[...document.querySelectorAll('[data-day]')];
  function selectDay(i, updateURL=true) {dayTabs.forEach((t,j)=>{t.setAttribute('aria-selected',String(j===i));t.tabIndex=j===i?0:-1;document.getElementById(`day-panel-${j+1}`).hidden=j!==i;});if(updateURL){const url=new URL(location.href);url.searchParams.set('day',String(i+1));url.hash='';history.replaceState(null,'',url);}}
  dayTabs.forEach((tab,i)=>{tab.addEventListener('click',()=>selectDay(i));tab.addEventListener('keydown',e=>{if(['ArrowLeft','ArrowRight','Home','End'].includes(e.key)){e.preventDefault();const n=e.key==='Home'?0:e.key==='End'?dayTabs.length-1:(i+(e.key==='ArrowRight'?1:-1)+dayTabs.length)%dayTabs.length;selectDay(n);dayTabs[n].focus();}});});
  if(dayTabs.length){const n=Number(new URLSearchParams(location.search).get('day'));const hashMatch=location.hash.match(/^#session-(\d)-/);selectDay(hashMatch?Number(hashMatch[1])-1:n===2?1:0,false);if(hashMatch){const target=document.getElementById(location.hash.slice(1));if(target){target.open=true;requestAnimationFrame(()=>target.scrollIntoView({block:'center'}));}}}

  const splits=document.querySelectorAll('.inner-split');
  if(splits.length){const redraw=()=>splits.forEach(drawSplit);redraw();if('ResizeObserver' in window){const ro=new ResizeObserver(redraw);splits.forEach(el=>ro.observe(el));}}

  const revealTargets=document.querySelectorAll('.about-grid,.experience-heading,.day-story,.speaker-card,.recap-grid,.stats-grid,.gallery-heading');
  if('IntersectionObserver' in window && !window.matchMedia('(prefers-reduced-motion: reduce)').matches){const observer=new IntersectionObserver(entries=>{entries.forEach(entry=>{if(entry.isIntersecting){entry.target.classList.add('in-view');observer.unobserve(entry.target);}});},{threshold:.06});revealTargets.forEach(el=>{el.classList.add('reveal');observer.observe(el);});}
})();
