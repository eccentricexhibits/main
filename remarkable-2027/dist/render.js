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

/* Arrow seam: the official extended arrow cuts a photo away from a colour field.
   wireSeams() breaks the photo into pixels along that cut. Pixels appear nowhere else. */
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
function hero(){const h=copy.hero;const match=h.event_name.match(/^(.*?)\s(\d{4})$/);return `<section class="hero"><div class="hero-main seam" data-split=".5" data-field="#BD15A7,#7B27D0">
 ${seam('assets/photos-2026/auditorium-crowd.jpg',photoAlt('auditorium-crowd.jpg'),'Remarkable 2026')}
 <div class="hero-stage seam-stage"><div class="hero-copy seam-copy"><p class="eyebrow">${esc(h.eyebrow)}</p><h1><span class="hero-name">${esc(match[1])}</span> <span class="hero-year">${esc(match[2])}</span></h1><p class="hero-tagline">${esc(h.tagline).replace(' come to life',' <span>come to life</span>')}</p>${heroActions('hero-actions--desktop')}${eventDetails('event-details--glass hero-details--desktop')}</div></div></div>
 <div class="hero-mobile">${heroActions('hero-actions--mobile')}${eventDetails('hero-details--mobile')}</div></section>`;}

function intro(){return `<section class="intro section"><div class="container"><p class="intro-lead">${esc(copy.intro[0])}</p><div class="intro-cards">${copy.intro.slice(1).map(p=>`<div class="intro-card"><p>${esc(p)}</p></div>`).join('')}</div><p class="intro-closer">${esc(copy.intro_closer)}</p></div></section>`;}
function stats(){return `<section class="stats" aria-labelledby="stats-heading"><div class="container"><div class="panel stats-panel"><h2 class="stats-caption" id="stats-heading">${esc(copy.stats.caption)}</h2><div class="stats-grid">${copy.stats.items.map(s=>`<div class="stat"><div class="stat-value">${esc(s.value)}</div><p class="stat-label">${esc(s.label)}</p></div>`).join('')}</div></div></div></section>`;}
function days(){const photos=['stage-fireside-chat.jpg','workshop-room.jpg'];return `<section class="section home-agenda"><div class="container"><div class="section-head"><h2>${esc(copy.agenda_page.title)}</h2>${moreLink('agenda.html',copy.home_links.agenda)}</div><div class="days-grid">${copy.days.map((d,i)=>`<article class="day day--${i+1}"><div class="day-media">${img('assets/photos-2026/'+photos[i],photoAlt(photos[i]),'day-photo')}<span class="day-number" aria-hidden="true">0${i+1}</span></div><div class="day-copy"><p class="day-meta"><span class="chip">${esc(d.label)} · ${esc(d.length)}</span><span class="day-date">${esc(d.date)}</span></p><h3><a href="agenda.html#day-${i+1}">${esc(d.title)}</a></h3><p class="day-description">${esc(d.body)}</p><span class="day-go" aria-hidden="true">${arrow()}</span></div></article>`).join('')}</div><p class="section-foot">${esc(copy.agenda_note)}</p></div></section>`;}
function speakersHome(){return `<section class="section speakers-home"><div class="container"><div class="panel speakers-panel"><div class="speakers-intro"><h2>${esc(copy.speakers_heading)}</h2>${copy.speakers_note?`<p>${esc(copy.speakers_note)}</p>`:''}${moreLink('speakers.html',copy.home_links.speakers)}</div><div class="speaker-grid">${copy.speakers.map(s=>`<article class="speaker-card"><a class="speaker-photo-link" href="speakers.html#${slug(s.name)}" tabindex="-1" aria-hidden="true">${img(s.photo,s.name,'portrait')}</a><div class="speaker-text"><h3><a href="speakers.html#${slug(s.name)}">${esc(s.name)}</a></h3><p class="role">${esc(s.title)}</p><p class="organization">${esc(s.org)}</p></div></article>`).join('')}</div></div></div></section>`;}
function recap(){return `<section class="recap-section"><div class="container"><div class="recap-block seam" data-split=".5" data-field="#313CFF">${seam(copy.recap.thumbnail,photoAlt(copy.recap.thumbnail))}<div class="recap-stage seam-stage"><div class="recap-copy seam-copy"><h2>${esc(copy.recap.heading)}</h2></div></div><button class="play" disabled aria-label="${esc(copy.ui.video_placeholder)}"><svg viewBox="0 0 24 28" aria-hidden="true"><path d="M2 2 22 14 2 26Z" fill="currentColor"/></svg></button></div></div></section>`;}
function gallery(){return `<section class="section gallery" aria-labelledby="gallery-heading"><div class="container"><div class="section-head"><div><h2 id="gallery-heading">${esc(copy.gallery.heading)}</h2><p>${esc(copy.gallery.note)}</p></div><div class="gallery-controls"><span class="gallery-range" aria-live="polite"></span><button class="round-btn gallery-prev" type="button" aria-label="Previous photos" aria-controls="gallery-track">${arrow('left')}</button><button class="round-btn gallery-next" type="button" aria-label="Next photos" aria-controls="gallery-track">${arrow()}</button></div></div><div class="gallery-track" id="gallery-track" tabindex="0" role="region" aria-label="Remarkable 2026 photo gallery">${copy.gallery.photos.map(p=>`<figure>${img(p,photoAlt(p))}</figure>`).join('')}</div></div></section>`;}
function funders(){const names=['Government of Canada','Government of Ontario','CIFAR'];return `<section class="funders"><div class="container"><div class="panel funder-row"><h2>${esc(copy.funders_heading)}</h2><div class="funder-logos">${copy.funders.map((p,i)=>`<div class="funder-logo">${img(p,names[i])}</div>`).join('')}</div></div></div></section>`;}
function footer(){const f=copy.footer;return `<footer class="footer"><div class="footer-shell"><div class="container"><div class="footer-contact"><div><p>${esc(f.contact_line)}</p><a class="footer-email" href="mailto:${esc(f.contact)}">${esc(f.contact)}</a></div><p class="footer-hashtag">${esc(f.hashtag)}</p></div><div class="footer-body"><div class="footer-brand"><a class="brand" href="index.html">${logo()}</a><p>${esc(f.ontario_credit)}</p></div><nav class="footer-links" aria-label="Vector Institute">${f.links.flat().map(l=>placeholder(l,'','')).join('')}</nav><div class="footer-socials"><p>${esc(f.socials_label)}</p>${f.socials.map(s=>placeholder(s,'','')).join('')}</div></div><p class="footer-legal">${esc(f.legal)}</p><div class="footer-bottom"><span>${esc(f.copyright)}</span><a href="#top">Back to top ${upArrow}</a></div></div></div></footer>`;}

const bannerPhotos={agenda:'stage-fireside-chat.jpg',speakers:'audience-listening.jpg',faq:'registration-desk.jpg'};
function pageHeader(page){const c=copy[page+'_page'];return `<section class="page-header"><div class="page-banner seam" data-split=".62" data-field="#BD15A7,#7B27D0">${seam('assets/photos-2026/'+bannerPhotos[page])}<div class="page-heading seam-stage"><div class="page-copy seam-copy"><p class="page-kicker">${esc(copy.hero.event_name)}</p><h1>${esc(c.title)}</h1>${eventDetails('event-details--glass')}</div></div></div><div class="container"><p class="page-intro">${withEmail(c.intro)}</p></div></section>`;}
function highlights(day,i){const indices=i?[1,2,3]:[2,5,8];const people=[copy.speakers[0],copy.speakers[4],copy.speakers[2]];const photos=['workshop-room.jpg','stage-fireside-chat.jpg','posters-conversation.jpg'];return `<div class="highlights"><h3 class="highlight-heading">Featured sessions</h3><div class="highlight-grid">${indices.map((j,k)=>{const item=day.sessions[j];const portrait=i?'assets/photos-2026/'+photos[k]:people[k].photo;return `<a class="highlight-card" href="#session-${i+1}-${j+1}"><div class="highlight-top"><span class="chip">${esc(item.type)}</span>${upArrow}</div><h4>${esc(item.title)}</h4><div class="highlight-footer">${img(portrait,i?photoAlt(photos[k]):people[k].name,i?'highlight-event':'highlight-portrait')}<p>${esc(i?item.time:people[k].name)}</p></div></a>`;}).join('')}</div></div>`;}
function agenda(){return `<section class="page-content"><div class="container">${copy.agenda_page.note?`<p class="draft-note">${esc(copy.agenda_page.note)}</p>`:''}<div class="agenda-tabs" role="tablist" aria-label="Agenda day">${copy.days.map((d,i)=>`<button id="tab-${i+1}" class="agenda-tab" type="button" role="tab" aria-selected="${i===0}" aria-controls="day-${i+1}" tabindex="${i===0?'0':'-1'}" data-day="${i+1}"><span class="tab-day">${esc(d.label)}</span><span class="tab-date">${esc(d.date)}<span class="tab-length">${esc(d.length)}</span></span>${arrow()}</button>`).join('')}</div>${copy.agenda_page.days.map((day,i)=>`<div class="agenda-panel" role="tabpanel" id="day-${i+1}" aria-labelledby="tab-${i+1}"${i?' hidden':''} tabindex="0"><div class="agenda-day-head"><h2>${esc(copy.days[i].title)}</h2><p>${esc(copy.agenda_note)}</p></div>${highlights(day,i)}<h3 class="schedule-heading">Full program</h3><div class="schedule">${day.sessions.map((s,j)=>`<article id="session-${i+1}-${j+1}" class="session${['Arrivals','Break','Lunch','Reception','Close'].includes(s.type)?' session--break':''}"><p class="session-time">${esc(s.time)}</p><div class="session-body"><p class="session-type chip">${esc(s.type)}</p><h3>${esc(s.title)}</h3>${s.body?`<p class="session-description">${esc(s.body)}</p>`:''}${s.speakers?`<p class="session-speakers">${esc(s.speakers)}</p>`:''}</div><div class="session-place"><span>${esc(s.where)}</span>${s.livestream?`<span class="livestream">${esc(copy.agenda_page.livestream_label)}</span>`:''}</div></article>`).join('')}</div></div>`).join('')}</div></section>`;}
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

/* Pixel seam. Cells sit on one square grid. On the photo side of the arrow, cells are knocked
   out of the image and show the colour field behind it; on the open side they break away into the colour field, thinning with distance and
   stepping up and to the right like the Pixel Design. Fragments near the cut take the photo's
   colours; farther out they turn to fading white. Cells keep clear of the copy. */
const cellRandom=(col,row,salt)=>{let h=Math.imul(col+7919,374761393)^Math.imul(row+104729,668265263)^Math.imul(salt+1,2246822519);h=Math.imul(h^h>>>13,1274126177);return((h^h>>>16)>>>0)/4294967296;};
function textBox(el){if(/^(P|H1|H2)$/.test(el.tagName)){const range=document.createRange();range.selectNodeContents(el);return range.getBoundingClientRect();}return el.getBoundingClientRect();}
function buildSeam(section){
 const r=section.getBoundingClientRect(),W=r.width,H=r.height;
 const arrowEl=section.querySelector('.seam-arrow'),a=arrowEl.getBoundingClientRect();if(!a.height||!W)return null;
 const k=a.height/ARROW.height,bottom={x:a.left-r.left+ARROW.shaft*k,y:a.top-r.top+a.height},top={x:a.left-r.left+ARROW.tip*k,y:a.top-r.top};
 const edgeX=y=>bottom.x+(top.x-bottom.x)*(bottom.y-y)/(bottom.y-top.y);
 const c=Math.round(Math.min(24,Math.max(12,H/36)));
 const photo=section.querySelector('.seam-photo');const photoOn=!!(photo&&photo.naturalWidth&&photo.getClientRects().length);
 const clear=12*k+c*.25,spread=Math.min(W*.24,c*12),band=c*3;
 const avoid=[...section.querySelectorAll('.seam-copy p,.seam-copy h1,.seam-copy h2,.seam-copy .btn,.seam-copy li,.play,.seam-art figcaption')].map(textBox).filter(b=>b.width).map(b=>({l:b.left-r.left-14,t:b.top-r.top-14,r:b.right-r.left+14,b:b.bottom-r.top+14}));
 const blocked=(x,y)=>avoid.some(b=>x+c>b.l&&x<b.r&&y+c>b.t&&y<b.b);
 const cols=Math.ceil(W/c),rows=Math.ceil(H/c),chosen=new Set(),cells=[];
 for(let row=rows-1;row>=0;row--){const yc=row*c+c/2;if(yc<top.y||yc>bottom.y)continue;const ex=edgeX(yc);
  for(let col=Math.max(0,Math.floor((ex-clear-spread)/c));col<cols;col++){const x=col*c,cx=x+c/2,y=row*c;
   const open=cx<ex,d=open?ex-clear-cx:cx-ex-clear;if(d<0)continue;if(!open&&(!photoOn||d>band))break;if(open&&d>spread)continue;
   let p=open?.36*Math.pow(1-d/spread,2):.7*Math.pow(1-d/band,1.6);
   if(open&&chosen.has((col-1)+','+(row+1)))p+=.32;
   if(cellRandom(col,row,1)>=p||blocked(x,y))continue;
   chosen.add(col+','+row);
   const white=open&&(!photoOn||d>spread*.45||cellRandom(col,row,2)<.25);
   const mirror=Math.min(cols-1,Math.floor((ex+clear+(ex-clear-cx))/c));
   cells.push({x,y,src:mirror,row,white,hole:!open,alpha:white?(.35+.6*cellRandom(col,row,3))*(1-.5*d/spread):1,delay:(d/(open?spread:band))*650+cellRandom(col,row,4)*240});
  }}
 let mosaic=null;
 if(photoOn){const b=photo.getBoundingClientRect(),s=Math.max(b.width/photo.naturalWidth,b.height/photo.naturalHeight),dw=photo.naturalWidth*s,dh=photo.naturalHeight*s,dx=b.left-r.left+(b.width-dw)/2,dy=b.top-r.top+(b.height-dh)/2;
  const mid=document.createElement('canvas');mid.width=cols*4;mid.height=rows*4;mid.getContext('2d').drawImage(photo,dx*4/c,dy*4/c,dw*4/c,dh*4/c);
  mosaic=document.createElement('canvas');mosaic.width=cols;mosaic.height=rows;const m=mosaic.getContext('2d');m.imageSmoothingQuality='high';m.drawImage(mid,0,0,cols,rows);}
 const field=section.dataset.field||'';const stops=field.split(',');
 return {W,H,c,cells,mosaic,fieldAt:x=>{if(stops.length<2)return stops[0]||'#FFFFFF';const t=Math.min(1,Math.max(0,x/W)),[a,b]=stops.map(h=>h.match(/\w\w/g).map(v=>parseInt(v,16)));return 'rgb('+a.map((v,i)=>Math.round(v+(b[i]-v)*t)).join(',')+')';}};
}
function paintSeam(canvas,seam,elapsed=Infinity){
 const dpr=Math.min(2,window.devicePixelRatio||1);if(canvas.width!==Math.round(seam.W*dpr)||canvas.height!==Math.round(seam.H*dpr)){canvas.width=Math.round(seam.W*dpr);canvas.height=Math.round(seam.H*dpr);}
 const ctx=canvas.getContext('2d');ctx.setTransform(dpr,0,0,dpr,0,0);ctx.clearRect(0,0,seam.W,seam.H);ctx.imageSmoothingEnabled=false;
 let pending=false;
 for(const cell of seam.cells){const t=Math.min(1,Math.max(0,(elapsed-cell.delay)/420));if(t<1)pending=true;if(!t)continue;
  const e=1-Math.pow(1-t,3),size=seam.c*(.3+.7*e),off=(seam.c-size)/2;ctx.globalAlpha=cell.alpha*e;
  if(cell.hole){ctx.fillStyle=seam.fieldAt(cell.x+seam.c/2);ctx.fillRect(cell.x+off,cell.y+off,size,size);}
  else if(cell.white||!seam.mosaic){ctx.fillStyle='#FFFFFF';ctx.fillRect(cell.x+off,cell.y+off,size,size);}
  else ctx.drawImage(seam.mosaic,cell.src,cell.row,1,1,cell.x+off,cell.y+off,size,size);}
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
