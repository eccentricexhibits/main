/* Buildless shared renderer. All event copy remains in content/copy.json. */
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const arrow=(dir='right')=>`<svg class="ui-arrow" viewBox="0 0 24 24" fill="none" aria-hidden="true"${dir==='left'?' style="transform:rotate(180deg)"':''}><path d="M4 12h15m-6-6 6 6-6 6" stroke="currentColor" stroke-width="1.6"/></svg>`;
const upArrow='<svg class="ui-arrow" viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M6 18 18 6M6 6h12v12" stroke="currentColor" stroke-width="1.6"/></svg>';
const pagePaths={home:'index.html',agenda:'agenda.html',speakers:'speakers.html',faq:'faq.html'};
const slug=s=>s.toLowerCase().replace(/[^a-z0-9]+/g,'-').replace(/^-|-$/g,'');
const logo=(white=false)=>`<img src="assets/logos/logo-bilingual-${white?'knockout-white':'colour'}.png" width="2320" height="493" alt="Vector Institute | Institut Vecteur">`;
const photoDescriptions={
 'auditorium-crowd.jpg':'Packed auditorium during Remarkable 2026',
 'posters-conversation.jpg':'Researchers discussing a poster at Remarkable 2026',
 'executive-breakfast-networking.jpg':'Guests connecting at the executive breakfast',
 'workshop-room.jpg':'Attendees in a Remarkable 2026 workshop',
 'registration-desk.jpg':'An attendee receiving a badge at registration',
 'attendees-group-photo.jpg':'Attendees taking a group photo at Remarkable 2026',
 'executive-breakfast-panel.jpg':'A panel discussion at the executive breakfast',
 'networking-hallway.jpg':'Attendees networking between sessions',
 'audience-listening.jpg':'Attendees listening during a Remarkable 2026 session',
 'stage-fireside-chat.jpg':'A conversation on the Remarkable 2026 main stage',
 'auditorium-wide-stage.jpg':'The Remarkable 2026 main stage and auditorium'
};
const photoAlt=p=>photoDescriptions[p.split('/').pop()]||'Remarkable 2026 event photograph';
const img=(src,alt,cls='',lazy=true)=>`<img src="${esc(src)}" alt="${esc(alt)}" class="${cls}"${lazy?' loading="lazy"':''} decoding="async">`;
let copy;
const placeholder=(label,cls='',icon=upArrow)=>`<a class="${cls}" href="#" data-placeholder aria-disabled="true">${esc(label)}${icon}</a>`;
const moreLink=(url,label)=>`<a class="text-link" href="${url}">${esc(label)}${arrow()}</a>`;

/* Arrow seam: the official extended arrow cuts a photo away from a colour field, and
   wireSeams() gathers official Pixel Design copies along that cut. Pixels appear nowhere else. */
const seam=(photo,alt='',caption='')=>`<figure class="seam-art">${img(photo,alt,'seam-photo',false)}${caption?`<figcaption>${esc(caption)}</figcaption>`:''}</figure><canvas class="seam-pixels" aria-hidden="true"></canvas>${img('assets/brand-elements/vector-arrow-extended.svg','','seam-arrow',false)}`;

function nav(page){return `<a class="skip-link" href="#main-content">${esc(copy.ui.skip)}</a>
 <header class="site-header" id="top"><div class="container nav-inner">
 <a class="brand" href="index.html" aria-label="Vector Institute — Remarkable home">${logo()}</a>
 <nav class="nav-main" id="main-navigation" aria-label="Main">${copy.nav.map(n=>`<a href="${pagePaths[n.toLowerCase()]}"${n.toLowerCase()===page?' aria-current="page"':''}>${esc(n)}</a>`).join('')}</nav>
 <div class="nav-actions"><div class="language" role="group" aria-label="${esc(copy.language.label)}"><span aria-current="true">${esc(copy.language.current)}</span>${placeholder(copy.language.other,'', '')}</div>${placeholder(copy.nav_cta,'btn btn--primary')}
 <button class="menu-toggle" type="button" aria-label="${esc(copy.ui.open_menu)}" aria-expanded="false" aria-controls="main-navigation"><span></span><span></span></button></div></div></header>`;}

const calendarIcon='<svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M5 4h14a1 1 0 0 1 1 1v15H4V5a1 1 0 0 1 1-1Zm-1 5h16M8 2v5m8-5v5" stroke="currentColor" stroke-width="1.5"/></svg>';
const locationIcon='<svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M19 9c0 5-7 12-7 12S5 14 5 9a7 7 0 1 1 14 0Z" stroke="currentColor" stroke-width="1.5"/><circle cx="12" cy="9" r="2.5" stroke="currentColor" stroke-width="1.5"/></svg>';
const eventDetails=(cls='')=>`<ul class="event-details ${cls}"><li>${calendarIcon}<span>${esc(copy.hero.dates)}</span></li><li>${locationIcon}<span><strong>${esc(copy.hero.venue)}</strong> ${esc(copy.hero.venue_address)}</span></li></ul>`;

function heroActions(cls){const h=copy.hero;return `<div class="hero-actions ${cls}"><div class="hero-ctas">${placeholder(h.cta_primary,'btn btn--white')}${placeholder(h.cta_secondary,'btn btn--glass')}</div><p class="hero-invitation">${esc(h.small_print)}</p></div>`;}
function hero(){const h=copy.hero;const match=h.event_name.match(/^(.*?)\s(\d{4})$/);return `<section class="hero"><div class="hero-main seam" data-split=".5" data-field="#BD15A7,#7B27D0" data-palette="#FFFFFF,#48C0D9,#FF9E00">
 ${seam('assets/photos-2026/auditorium-crowd.jpg',photoAlt('auditorium-crowd.jpg'),'Remarkable 2026')}
 <div class="hero-stage seam-stage"><div class="hero-copy seam-copy"><p class="eyebrow">${esc(h.eyebrow)}</p><h1><span class="hero-name">${esc(match[1])}</span> <span class="hero-year">${esc(match[2])}</span></h1><p class="hero-tagline">${esc(h.tagline).replace(' come to life',' <span>come to life</span>')}</p>${heroActions('hero-actions--desktop')}${eventDetails('event-details--glass hero-details--desktop')}</div></div></div>
 <div class="hero-mobile">${heroActions('hero-actions--mobile')}${eventDetails('hero-details--mobile')}</div></section>`;}

function intro(){return `<section class="intro section"><div class="container"><p class="intro-lead">${esc(copy.intro[0])}</p><div class="intro-cards">${copy.intro.slice(1).map(p=>`<div class="intro-card"><p>${esc(p)}</p></div>`).join('')}</div><p class="intro-closer">${esc(copy.intro_closer)}</p></div></section>`;}
function stats(){return `<section class="stats" aria-labelledby="stats-heading"><div class="container"><div class="panel stats-panel"><h2 class="stats-caption" id="stats-heading">${esc(copy.stats.caption)}</h2><div class="stats-grid">${copy.stats.items.map(s=>`<div class="stat"><div class="stat-value">${esc(s.value)}</div><p class="stat-label">${esc(s.label)}</p></div>`).join('')}</div></div></div></section>`;}
function days(){const photos=['stage-fireside-chat.jpg','workshop-room.jpg'];return `<section class="section home-agenda"><div class="container"><div class="section-head"><h2>${esc(copy.agenda_page.title)}</h2>${moreLink('agenda.html',copy.home_links.agenda)}</div><div class="days-grid">${copy.days.map((d,i)=>`<article class="day day--${i+1}"><div class="day-media">${img('assets/photos-2026/'+photos[i],photoAlt(photos[i]),'day-photo')}<span class="day-number" aria-hidden="true">0${i+1}</span></div><div class="day-copy"><p class="day-meta"><span class="chip">${esc(d.label)} · ${esc(d.length)}</span><span class="day-date">${esc(d.date)}</span></p><h3><a href="agenda.html#day-${i+1}">${esc(d.title)}</a></h3><p class="day-description">${esc(d.body)}</p><span class="day-go" aria-hidden="true">${arrow()}</span></div></article>`).join('')}</div><p class="section-foot">${esc(copy.agenda_note)}</p></div></section>`;}
function speakersHome(){return `<section class="section speakers-home"><div class="container"><div class="panel speakers-panel"><div class="speakers-intro"><h2>${esc(copy.speakers_heading)}</h2>${copy.speakers_note?`<p>${esc(copy.speakers_note)}</p>`:''}${moreLink('speakers.html',copy.home_links.speakers)}</div><div class="speaker-grid">${copy.speakers.map(s=>`<article class="speaker-card"><a class="speaker-photo-link" href="speakers.html#${slug(s.name)}" tabindex="-1" aria-hidden="true">${img(s.photo,s.name,'portrait')}</a><div class="speaker-text"><h3><a href="speakers.html#${slug(s.name)}">${esc(s.name)}</a></h3><p class="role">${esc(s.title)}</p><p class="organization">${esc(s.org)}</p></div></article>`).join('')}</div></div></div></section>`;}
function recap(){return `<section class="recap-section"><div class="container"><div class="recap-block seam" data-split=".5" data-field="#313CFF" data-palette="#FFFFFF,#48C0D9,#FF9E00">${seam(copy.recap.thumbnail,photoAlt(copy.recap.thumbnail))}<div class="recap-stage seam-stage"><div class="recap-copy seam-copy"><h2>${esc(copy.recap.heading)}</h2></div></div><button class="play" disabled aria-label="${esc(copy.ui.video_placeholder)}"><svg viewBox="0 0 24 28" aria-hidden="true"><path d="M2 2 22 14 2 26Z" fill="currentColor"/></svg></button></div></div></section>`;}
function gallery(){return `<section class="section gallery" aria-labelledby="gallery-heading"><div class="container"><div class="section-head"><div><h2 id="gallery-heading">${esc(copy.gallery.heading)}</h2><p>${esc(copy.gallery.note)}</p></div><div class="gallery-controls"><span class="gallery-range" aria-live="polite"></span><button class="round-btn gallery-prev" type="button" aria-label="Previous photos" aria-controls="gallery-track">${arrow('left')}</button><button class="round-btn gallery-next" type="button" aria-label="Next photos" aria-controls="gallery-track">${arrow()}</button></div></div><div class="gallery-track" id="gallery-track" tabindex="0" role="region" aria-label="Remarkable 2026 photo gallery">${copy.gallery.photos.map(p=>`<figure>${img(p,photoAlt(p))}</figure>`).join('')}</div></div></section>`;}
function funders(){const names=['Government of Canada','Government of Ontario','CIFAR'];return `<section class="funders"><div class="container"><div class="panel funder-row"><h2>${esc(copy.funders_heading)}</h2><div class="funder-logos">${copy.funders.map((p,i)=>`<div class="funder-logo">${img(p,names[i])}</div>`).join('')}</div></div></div></section>`;}
function footer(){const f=copy.footer;return `<footer class="footer"><div class="footer-shell"><div class="container"><div class="footer-contact"><div><p>${esc(f.contact_line)}</p><a class="footer-email" href="mailto:${esc(f.contact)}">${esc(f.contact)}</a></div><p class="footer-hashtag">${esc(f.hashtag)}</p></div><div class="footer-body"><div class="footer-brand"><a class="brand" href="index.html">${logo()}</a><p>${esc(f.ontario_credit)}</p></div><nav class="footer-links" aria-label="Vector Institute">${f.links.flat().map(l=>placeholder(l,'','')).join('')}</nav><div class="footer-socials"><p>${esc(f.socials_label)}</p>${f.socials.map(s=>placeholder(s,'','')).join('')}</div></div><p class="footer-legal">${esc(f.legal)}</p><div class="footer-bottom"><span>${esc(f.copyright)}</span><a href="#top">Back to top ${upArrow}</a></div></div></div></footer>`;}

const bannerPhotos={agenda:'stage-fireside-chat.jpg',speakers:'audience-listening.jpg',faq:'registration-desk.jpg'};
function pageHeader(page){const c=copy[page+'_page'];return `<section class="page-header"><div class="page-banner seam" data-split=".62" data-field="#BD15A7,#7B27D0" data-palette="#FFFFFF,#48C0D9,#FF9E00">${seam('assets/photos-2026/'+bannerPhotos[page])}<div class="page-heading seam-stage"><div class="page-copy seam-copy"><p class="page-kicker">${esc(copy.hero.event_name)}</p><h1>${esc(c.title)}</h1>${eventDetails('event-details--glass')}</div></div></div><div class="container"><p class="page-intro">${withEmail(c.intro)}</p></div></section>`;}
/* Session formats are colour-coded with brand colours: main stage, talks, hands-on, breaks. */
const toneOf=type=>({'Keynote':'magenta','Welcome':'magenta','Fireside chat':'magenta','Panel':'magenta','Close':'magenta','Research talks':'cobalt','Lightning talks':'cobalt','Workshops':'turquoise','Posters':'turquoise'}[type]||'tangerine');
function highlights(day,i){const indices=i?[1,2,3]:[2,5,8];const people=[copy.speakers[0],copy.speakers[4],copy.speakers[2]];const photos=['workshop-room.jpg','stage-fireside-chat.jpg','posters-conversation.jpg'];return `<div class="highlights"><h3 class="highlight-heading">Featured sessions</h3><div class="highlight-grid">${indices.map((j,k)=>{const item=day.sessions[j];const portrait=i?'assets/photos-2026/'+photos[k]:people[k].photo;return `<a class="highlight-card" href="#session-${i+1}-${j+1}"><div class="highlight-top"><span class="chip chip--dot" data-tone="${toneOf(item.type)}">${esc(item.type)}</span>${upArrow}</div><h4>${esc(item.title)}</h4><div class="highlight-footer">${img(portrait,i?photoAlt(photos[k]):people[k].name,i?'highlight-event':'highlight-portrait')}<p>${esc(i?item.time:people[k].name)}</p></div></a>`;}).join('')}</div></div>`;}
function agenda(){return `<section class="page-content"><div class="container">${copy.agenda_page.note?`<p class="draft-note">${esc(copy.agenda_page.note)}</p>`:''}<div class="agenda-tabs" role="tablist" aria-label="Agenda day">${copy.days.map((d,i)=>`<button id="tab-${i+1}" class="agenda-tab" type="button" role="tab" aria-selected="${i===0}" aria-controls="day-${i+1}" tabindex="${i===0?'0':'-1'}" data-day="${i+1}"><span class="tab-day">${esc(d.label)}</span><span class="tab-date">${esc(d.date)}<span class="tab-length">${esc(d.length)}</span></span>${arrow()}</button>`).join('')}</div>${copy.agenda_page.days.map((day,i)=>`<div class="agenda-panel" role="tabpanel" id="day-${i+1}" aria-labelledby="tab-${i+1}"${i?' hidden':''} tabindex="0"><div class="agenda-day-head"><h2>${esc(copy.days[i].title)}</h2><p>${esc(copy.agenda_note)}</p></div>${highlights(day,i)}<h3 class="schedule-heading">Full program</h3><div class="schedule">${day.sessions.map((s,j)=>`<article id="session-${i+1}-${j+1}" class="session${['Arrivals','Break','Lunch','Reception','Close'].includes(s.type)?' session--break':''}"><p class="session-time">${esc(s.time)}</p><div class="session-body"><p class="session-type chip chip--dot" data-tone="${toneOf(s.type)}">${esc(s.type)}</p><h3>${esc(s.title)}</h3>${s.body?`<p class="session-description">${esc(s.body)}</p>`:''}${s.speakers?`<p class="session-speakers">${esc(s.speakers)}</p>`:''}</div><div class="session-place"><span>${esc(s.where)}</span>${s.livestream?`<span class="livestream">${esc(copy.agenda_page.livestream_label)}</span>`:''}</div></article>`).join('')}</div></div>`).join('')}</div></section>`;}
function speakers(){return `<section class="page-content"><div class="container profiles">${copy.speakers.map(s=>`<article class="speaker-profile" id="${slug(s.name)}">${img(s.photo,s.name,'portrait')}<div class="profile-copy"><div class="profile-heading"><h2>${esc(s.name)}</h2><p class="profile-role">${esc(s.title)}</p><p class="profile-org">${esc(s.org)}</p></div><p class="profile-bio">${esc(s.bio)}</p><span class="chip chip--magenta">${esc(s.session)}</span></div></article>`).join('')}<p class="speakers-more">${esc(copy.speakers_page.more)}</p></div></section>`;}
function withEmail(s){return esc(s).replace(/events@vectorinstitute\.ai/g,'<a href="mailto:events@vectorinstitute.ai">events@vectorinstitute.ai</a>');}
function faq(){return `<section class="page-content"><div class="container faq-layout"><nav class="faq-nav" aria-label="FAQ topics"><p>Topics</p>${copy.faq_page.groups.map(g=>`<a href="#${slug(g.heading)}">${esc(g.heading)}${arrow()}</a>`).join('')}</nav><div>${copy.faq_page.groups.map(g=>`<section class="faq-group" id="${slug(g.heading)}"><h2>${img('assets/brand-elements/vector-arrow-compact.svg','','faq-heading-arrow',false)}${esc(g.heading)}</h2>${g.items.map((q,k)=>`<details class="faq-item"${k?'':' open'}><summary>${esc(q.q)}<span class="faq-icon" aria-hidden="true"></span></summary><p class="faq-answer">${withEmail(q.a)}</p></details>`).join('')}</section>`).join('')}</div></div></section>`;}

/* Official extended arrow, in its 194 x 390 viewBox: the shaft leaves the bottom edge
   at x 11.24 and the tip touches the top edge at x 167.31. */
const ARROW={shaft:11.23645,tip:167.314,width:194,height:390};
function wireArrowGeometry(){
 document.querySelectorAll('.seam').forEach(section=>{
  const layout=()=>{const r=section.getBoundingClientRect();const k=r.height/ARROW.height;const mobile=matchMedia('(max-width:759px)').matches;
   const splitStart=mobile?r.width-4-(ARROW.width-ARROW.shaft)*k:r.width*Number(section.dataset.split||.5);
   section.style.setProperty('--split-start',splitStart+'px');
   section.style.setProperty('--split-run',(ARROW.tip-ARROW.shaft)*k+'px');
   section.style.setProperty('--arrow-left',(splitStart-ARROW.shaft*k)+'px');
   const stage=section.querySelector('.seam-stage');if(stage)section.style.setProperty('--copy-max',Math.max(260,splitStart-(stage.getBoundingClientRect().left-r.left)-40)+'px');
   section.dispatchEvent(new Event('seamlayout'));
  };
  layout();new ResizeObserver(layout).observe(section);document.fonts.ready.then(layout);
 });
 window.addEventListener('resize',()=>document.querySelectorAll('.seam').forEach(s=>s.dispatchEvent(new Event('seamresize'))),{passive:true});
}

/* Pixel tapestry. Every shape is a whole copy of the official Pixel Design (Symbol Compilation
   for Swoogo PDF): the same 34 cells in the same arrangement, only scaled and coloured, never
   rotated, mirrored, cropped or broken up. Copies gather along the arrow:
   - Stencil copies straddle the cut: cells on the photo side are knocked out to show the colour
     field, cells on the open side are white.
   - A stream of smaller copies hugs the cut: white, turquoise and tangerine in the colour field,
     knocked out of the photo on the other side. They shrink and thin out away from the arrow, as
     the pattern "comes into focus and advances" (brand guide p.11).
   - One tangerine copy sits over the top of the photo, clear of the people in it.
   Copies never overlap each other, the arrowhead or any copy text. Placement is seeded, so the
   tapestry is the same on every visit and only rescales with the panel. */
const PIXEL_CELLS=[[1081.9829,1661],[931.9829,1511],[1681.9829,1361],[1531.9829,1211],[1381.9829,1211],[1081.9829,1361],[931.9829,1211],[2010.8701,911],[1681.9829,1061],[1531.9829,911],[1381.9829,1061],[1381.9829,911],[1231.9829,1061],[1081.9829,911],[1860.8701,761],[1710.8701,611],[1229.9829,600],[929.9829,600],[1379.9829,450],[1379.9829,300],[1079.9829,450],[929.9829,300],[929.9829,450],[150,499.5479],[0,349.5479],[1529.9829,150],[1379.9829,0],[1229.9829,150],[779.9829,150],[629.9829,0],[479.9829,0],[150,199.5479],[0,49.5479],[1529.9829,300]];
const PIXEL_W=2160.8701,PIXEL_H=1811,PIXEL_UNIT=150;
/* t: position along the arrow (0 tail, 1 tip). off: horizontal offset from the cut, in arrow
   heights (negative = colour-field side). f: cell size as a fraction of the arrow height. */
const TAPESTRY=[
 {kind:'solid',t:.9,off:.32,f:1/110,color:2,photoSide:true}
];
const seededRandom=seed=>()=>{seed=seed+0x6D2B79F5|0;let t=Math.imul(seed^seed>>>15,1|seed);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296;};
function textBox(el){if(/^(P|H1|H2)$/.test(el.tagName)){const range=document.createRange();range.selectNodeContents(el);return range.getBoundingClientRect();}return el.getBoundingClientRect();}
function buildSeam(section){
 const r=section.getBoundingClientRect(),W=r.width,H=r.height;
 const arrowEl=section.querySelector('.seam-arrow'),a=arrowEl.getBoundingClientRect();if(!a.height||!W)return null;
 const A=a.height,k=A/ARROW.height,ax=a.left-r.left,ay=a.top-r.top;
 const bottom={x:ax+ARROW.shaft*k,y:ay+A},top={x:ax+ARROW.tip*k,y:ay};
 const edgeX=y=>bottom.x+(top.x-bottom.x)*(bottom.y-y)/(bottom.y-top.y);
 const shaftHalf=12*k,radius=parseFloat(getComputedStyle(section).borderTopLeftRadius)||0;
 const photo=section.querySelector('.seam-photo');const photoOn=!!(photo&&photo.naturalWidth&&photo.getClientRects().length);
 const palette=(section.dataset.palette||'#FFFFFF').split(',');
 const pad=16,avoid=[...section.querySelectorAll('.seam-copy p,.seam-copy h1,.seam-copy h2,.seam-copy .btn,.seam-copy li,.play,.seam-art figcaption')].map(textBox).filter(b=>b.width).map(b=>({l:b.left-r.left-pad,t:b.top-r.top-pad,r:b.right-r.left+pad,b:b.bottom-r.top+pad}));
 avoid.push({l:ax+88*k-8,t:ay-8,r:ax+ARROW.width*k+8,b:ay+94*k+8});
 const hits=(b,list)=>list.some(o=>b.r>o.l&&b.l<o.r&&b.b>o.t&&b.t<o.b);
 const fits=b=>{if(b.l<10||b.t<10||b.r>W-10||b.b>H-10)return false;
  const inCorner=(x,y)=>{const cx=x<radius?radius:x>W-radius?W-radius:null,cy=y<radius?radius:y>H-radius?H-radius:null;return cx!==null&&cy!==null&&Math.hypot(x-cx,y-cy)>radius-10;};
  return ![[b.l,b.t],[b.r,b.t],[b.l,b.b],[b.r,b.b]].some(p=>inCorner(...p));};
 const placed=[],instances=[];
 for(const item of TAPESTRY){
  const kind=item.kind==='stencil'&&!photoOn?'solid':item.kind;if(item.photoSide&&!photoOn)continue;
  let found=null;
  search:for(const scale of [1,.85,.7,.55])for(const dt of [0,.04,-.04,.08,-.08,.12,-.12,.18,-.18,.24,-.24])for(const om of [1,1.25,.8]){
   const cs=Math.max(4,item.f*A*scale),w=PIXEL_W/PIXEL_UNIT*cs,h=PIXEL_H/PIXEL_UNIT*cs;
   const cy=bottom.y-(item.t+dt)*(bottom.y-top.y),cx=edgeX(cy)+item.off*om*A;
   const b={l:cx-w/2,t:cy-h/2,r:cx+w/2,b:cy+h/2};
   if(!fits(b)||hits({l:b.l-12,t:b.t-12,r:b.r+12,b:b.b+12},placed)||hits(b,avoid))continue;
   if(kind==='solid'&&(item.photoSide?b.l<Math.max(edgeX(b.t),edgeX(b.b))+shaftHalf+10:b.r>Math.min(edgeX(b.t),edgeX(b.b))-shaftHalf-10))continue;
   found={b,cs};break search;}
  if(!found)continue;placed.push(found.b);
  const kk=found.cs/PIXEL_UNIT,cells=PIXEL_CELLS.map(([x,y])=>{const l=Math.round(found.b.l+x*kk),t=Math.round(found.b.t+y*kk),rr=Math.round(found.b.l+(x+PIXEL_UNIT)*kk),bb=Math.round(found.b.t+(y+PIXEL_UNIT)*kk);
   return {l,t,w:rr-l,h:bb-t,order:x-y,hole:kind==='stencil'&&l+(rr-l)/2>edgeX(t+(bb-t)/2)};});
  instances.push({kind,color:palette[(item.color||0)%palette.length],cells,delay:instances.length*140});
 }
 const random=seededRandom(2027),spread=Math.min(W*.26,A*.3),limit=Math.round(A/22);
 for(let i=0;i<2400&&instances.length<limit+TAPESTRY.length;i++){
  const t=random(),u=random(),pick=random(),jitter=random(),photoSide=photoOn&&random()<.24;
  const d=photoSide?u*A*.05:Math.pow(u,2.4)*spread,cs=Math.max(2.6,(A/118+(A/270-A/118)*Math.min(1,d/spread))*(.6+.8*jitter)*(photoSide?.95:1)),w=PIXEL_W/PIXEL_UNIT*cs,h=PIXEL_H/PIXEL_UNIT*cs;
  const cy=bottom.y-t*(bottom.y-top.y);let b;
  /* A copy may tuck under the arrow, but no visible cell may cross the cut. */
  if(photoSide){const l=edgeX(cy-h/2)-shaftHalf*.8+d;b={l,t:cy-h/2,r:l+w,b:cy+h/2};}
  else{const rr=edgeX(cy+h/2)+shaftHalf*.8-d;b={l:rr-w,t:cy-h/2,r:rr,b:cy+h/2};}
  if(!fits(b)||hits({l:b.l-4,t:b.t-4,r:b.r+4,b:b.b+4},placed)||hits(b,avoid))continue;
  placed.push(b);const kk=cs/PIXEL_UNIT,color=palette[pick<.18?1:pick<.3?2:0];
  instances.push({kind:photoSide?'hole':'solid',color,alpha:photoSide||color!==palette[0]?1:1-.4*d/spread,d,
   cells:PIXEL_CELLS.map(([x,y])=>{const l=Math.round(b.l+x*kk),tt=Math.round(b.t+y*kk);return {l,t:tt,w:Math.round(b.l+(x+PIXEL_UNIT)*kk)-l,h:Math.round(b.t+(y+PIXEL_UNIT)*kk)-tt,order:x-y};})});
 }
 instances.forEach(inst=>{if(inst.d!==undefined)inst.delay=200+inst.d/spread*700;});
 const field=(section.dataset.field||'#FFFFFF').split(',');
 return {W,H,instances,field};
}
function paintSeam(canvas,seam,elapsed=Infinity){
 const dpr=Math.min(2,window.devicePixelRatio||1);if(canvas.width!==Math.round(seam.W*dpr)||canvas.height!==Math.round(seam.H*dpr)){canvas.width=Math.round(seam.W*dpr);canvas.height=Math.round(seam.H*dpr);}
 const ctx=canvas.getContext('2d');ctx.setTransform(dpr,0,0,dpr,0,0);ctx.clearRect(0,0,seam.W,seam.H);
 let fieldFill=seam.field[0];if(seam.field.length>1){fieldFill=ctx.createLinearGradient(0,0,seam.W,0);fieldFill.addColorStop(0,seam.field[0]);fieldFill.addColorStop(1,seam.field[1]);}
 let pending=false;
 for(const inst of seam.instances){
  const orders=inst.cells.map(c=>c.order),lo=Math.min(...orders),span=(Math.max(...orders)-lo)||1;
  for(const cell of inst.cells){const t=Math.min(1,Math.max(0,(elapsed-inst.delay-(cell.order-lo)/span*520)/380));if(t<1)pending=true;if(!t)continue;
   const e=1-Math.pow(1-t,3),w=cell.w*(.3+.7*e),h=cell.h*(.3+.7*e),x=cell.l+(cell.w-w)/2,y=cell.t+(cell.h-h)/2;ctx.globalAlpha=e*(inst.alpha??1);
   ctx.fillStyle=inst.kind==='hole'||cell.hole?fieldFill:inst.kind==='stencil'?'#FFFFFF':inst.color;ctx.fillRect(x,y,w,h);
  }}
 ctx.globalAlpha=1;return pending;
}
function wireSeams(){
 const reduced=matchMedia('(prefers-reduced-motion: reduce)').matches;
 document.querySelectorAll('.seam').forEach(section=>{
  const canvas=section.querySelector('.seam-pixels'),photo=section.querySelector('.seam-photo');let seam=null,shown=false,frame=0;
  const rebuild=()=>{cancelAnimationFrame(frame);frame=requestAnimationFrame(()=>{seam=buildSeam(section);if(seam&&shown)paintSeam(canvas,seam);});};
  const play=()=>{shown=true;seam=seam||buildSeam(section);if(!seam)return;if(reduced){paintSeam(canvas,seam);return;}const start=performance.now();const step=now=>{if(paintSeam(canvas,seam,now-start))frame=requestAnimationFrame(step);};frame=requestAnimationFrame(step);};
  const ready=Promise.all([document.fonts.ready,photo&&!photo.complete?new Promise(r=>{photo.addEventListener('load',r,{once:true});photo.addEventListener('error',r,{once:true});}):null]);
  ready.then(()=>{section.addEventListener('seamlayout',rebuild);section.addEventListener('seamresize',rebuild);seam=buildSeam(section);
   if(!('IntersectionObserver' in window)){play();return;}
   const io=new IntersectionObserver(entries=>{if(entries.some(e=>e.isIntersecting)){io.disconnect();play();}},{threshold:.3});io.observe(section);});
 });
}
function wireInteractions(){
 wireArrowGeometry();wireSeams();
 const header=document.querySelector('.site-header'),toggle=document.querySelector('.menu-toggle');
 const onScroll=()=>header.classList.toggle('is-scrolled',scrollY>8);onScroll();window.addEventListener('scroll',onScroll,{passive:true});
 function closeMenu(){header.classList.remove('nav-open');toggle.setAttribute('aria-expanded','false');toggle.setAttribute('aria-label',copy.ui.open_menu);}
 toggle.addEventListener('click',()=>{const open=toggle.getAttribute('aria-expanded')!=='true';header.classList.toggle('nav-open',open);toggle.setAttribute('aria-expanded',String(open));toggle.setAttribute('aria-label',open?copy.ui.close_menu:copy.ui.open_menu);});
 document.addEventListener('keydown',e=>{if(e.key==='Escape'&&header.classList.contains('nav-open')){closeMenu();toggle.focus();}});
 document.addEventListener('click',e=>{if(!header.contains(e.target))closeMenu();});
 document.querySelectorAll('[data-placeholder]').forEach(a=>a.addEventListener('click',e=>e.preventDefault()));
 const tabs=[...document.querySelectorAll('[role=tab]')];
 const selectDay=(n,focus=false,updateUrl=true)=>{tabs.forEach((t,i)=>{const on=i===n-1;t.setAttribute('aria-selected',String(on));t.tabIndex=on?0:-1;document.getElementById('day-'+(i+1)).hidden=!on;if(on&&focus)t.focus();});if(updateUrl)history.replaceState(null,'','#day-'+n);};
 tabs.forEach((tab,i)=>{tab.addEventListener('click',()=>selectDay(i+1));tab.addEventListener('keydown',e=>{let next;if(e.key==='ArrowRight'||e.key==='ArrowDown')next=(i+1)%tabs.length;if(e.key==='ArrowLeft'||e.key==='ArrowUp')next=(i+tabs.length-1)%tabs.length;if(e.key==='Home')next=0;if(e.key==='End')next=tabs.length-1;if(next!==undefined){e.preventDefault();selectDay(next+1,true);}});});
 if(tabs.length){const hashDay=()=>{const m=location.hash.match(/^#(?:day-|session-)([12])(?:-|$)/);return m?Number(m[1]):null;};selectDay(hashDay()||1,false,false);window.addEventListener('hashchange',()=>{const n=hashDay();if(n)selectDay(n,false,false);});}
 const track=document.querySelector('.gallery-track');
 if(track){const prev=document.querySelector('.gallery-prev'),next=document.querySelector('.gallery-next'),range=document.querySelector('.gallery-range');const reduced=matchMedia('(prefers-reduced-motion: reduce)');
 const update=()=>{const items=[...track.children];const width=items[0].getBoundingClientRect().width;const gap=parseFloat(getComputedStyle(track).gap)||0;const first=Math.min(items.length-1,Math.max(0,Math.round(track.scrollLeft/(width+gap))));const visible=Math.max(1,Math.floor((track.clientWidth+gap)/(width+gap)));range.textContent=String(first+1).padStart(2,'0')+(visible>1?'–'+String(Math.min(items.length,first+visible)).padStart(2,'0'):'')+' / '+String(items.length).padStart(2,'0');prev.disabled=track.scrollLeft<5;next.disabled=track.scrollLeft>=track.scrollWidth-track.clientWidth-5;};
 const move=dir=>{const item=track.firstElementChild;const step=item.getBoundingClientRect().width+(parseFloat(getComputedStyle(track).gap)||0);const visible=Math.max(1,Math.floor((track.clientWidth+24)/step));track.scrollBy({left:dir*step*visible,behavior:reduced.matches?'instant':'smooth'});};
 prev.addEventListener('click',()=>move(-1));next.addEventListener('click',()=>move(1));track.addEventListener('scroll',update,{passive:true});track.addEventListener('keydown',e=>{if(e.key==='ArrowRight'||e.key==='ArrowLeft'){e.preventDefault();move(e.key==='ArrowRight'?1:-1);}});new ResizeObserver(update).observe(track);update();
 }
}
async function render(){if(window.REMARKABLE_COPY){copy=window.REMARKABLE_COPY;}else{const response=await fetch('content/copy.json');if(!response.ok)throw new Error('Event content could not be loaded');copy=await response.json();}const page=document.body.dataset.page||'home';const main=page==='home'?hero()+intro()+stats()+days()+speakersHome()+recap()+gallery()+funders():pageHeader(page)+({agenda,speakers,faq}[page]());document.body.innerHTML=nav(page)+`<main id="main-content" tabindex="-1">${main}</main>`+footer();wireInteractions();await document.fonts.ready;await Promise.all([...document.images].filter(i=>i.loading!=='lazy').map(i=>i.complete?Promise.resolve():new Promise(r=>{i.onload=r;i.onerror=r;})));document.documentElement.dataset.ready='true';if(location.hash&&!location.hash.startsWith('#day-'))document.getElementById(decodeURIComponent(location.hash.slice(1)))?.scrollIntoView();}
render().catch(e=>{console.error(e);document.body.innerHTML='<main class="container section"><h1>Remarkable 2027</h1><p>The event preview could not load. Please refresh the page.</p></main>';});
