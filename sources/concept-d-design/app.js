const menu = document.querySelector('.menu-toggle');
const nav = document.querySelector('#navigation');
function closeMenu(){menu.setAttribute('aria-expanded','false');nav.classList.remove('is-open');menu.querySelector('.sr-only').textContent='Open menu';}
menu.addEventListener('click',()=>{const open=menu.getAttribute('aria-expanded')!=='true';menu.setAttribute('aria-expanded',String(open));nav.classList.toggle('is-open',open);menu.querySelector('.sr-only').textContent=open?'Close menu':'Open menu';});
nav.querySelectorAll('a').forEach(a=>a.addEventListener('click',closeMenu));
document.addEventListener('keydown',e=>{if(e.key==='Escape')closeMenu();});
const tabs=[...document.querySelectorAll('.day-tab')];
const programImage=document.querySelector('#program-image');
const programCaption=document.querySelector('#program-caption');
function selectDay(index){tabs.forEach((tab,i)=>{const selected=i===index;tab.setAttribute('aria-selected',String(selected));tab.tabIndex=selected?0:-1;document.getElementById(tab.getAttribute('aria-controls')).hidden=!selected;});programImage.src=index?'assets/remarkable-2026-workshop.jpeg':'assets/remarkable-2026-networking.jpeg';programImage.alt=index?'Researchers and industry participants in a hands-on workshop at Remarkable 2026':'A panel conversation on the Remarkable 2026 stage';programCaption.textContent=index?'Putting research into practice at Remarkable 2026':'On the Remarkable stage in 2026';}
tabs.forEach((tab,i)=>{tab.addEventListener('click',()=>selectDay(i));tab.addEventListener('keydown',e=>{let next;if(e.key==='ArrowRight')next=(i+1)%tabs.length;if(e.key==='ArrowLeft')next=(i+tabs.length-1)%tabs.length;if(e.key==='Home')next=0;if(e.key==='End')next=tabs.length-1;if(next!==undefined){e.preventDefault();selectDay(next);tabs[next].focus();}});});
const registration=document.querySelector('#registration-dialog');
const message=document.querySelector('#registration-message');
const choices=[...document.querySelectorAll('[data-register-choice]')];
function chooseRegistration(choice){choices.forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.registerChoice===choice)));message.textContent=choice==='inperson'?'In-person registration will use your invitation email address on the final event page.':choice==='virtual'?'Virtual registration and livestream details will be available on the final event page.':'Select an attendance option to preview the next step.';}
document.querySelectorAll('[data-register]').forEach(button=>button.addEventListener('click',()=>{closeMenu();chooseRegistration(button.dataset.register);registration.showModal();}));
choices.forEach(button=>button.addEventListener('click',()=>chooseRegistration(button.dataset.registerChoice)));
document.querySelectorAll('dialog').forEach(dialog=>{dialog.querySelector('[data-close]').addEventListener('click',()=>dialog.close());dialog.addEventListener('click',e=>{if(e.target===dialog){const r=dialog.getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)dialog.close();}});});
const gallery=document.querySelector('#gallery-dialog');
const photos=[
 {src:'assets/remarkable-2026-stage.jpeg',caption:'The stage is set. Remarkable 2026 at Hilton Toronto.',alt:'The Remarkable 2026 ballroom and main stage illuminated in magenta and cobalt'},
 {src:'assets/remarkable-2026-posters.jpeg',caption:'Ideas in conversation. The Remarkable 2026 poster session.',alt:'Researchers discussing a research poster at Remarkable 2026'},
 {src:'assets/remarkable-2026-conversation.jpeg',caption:'Connections between sessions. Remarkable 2026.',alt:'Members of the Vector community networking between conference sessions'},
 {src:'assets/remarkable-2026-workshop.jpeg',caption:'Research becomes practice. A Remarkable 2026 workshop.',alt:'Workshop participants gathered for a presentation at Remarkable 2026'},
 {src:'assets/remarkable-2026-collaboration.jpeg',caption:'A closer look at the work. Remarkable 2026.',alt:'A researcher explaining a poster to a conference attendee'}
];
let photoIndex=0;
function showPhoto(index){photoIndex=(index+photos.length)%photos.length;const photo=photos[photoIndex];document.querySelector('#gallery-image').src=photo.src;document.querySelector('#gallery-image').alt=photo.alt;document.querySelector('#gallery-caption').textContent=photo.caption;document.querySelector('#gallery-count').textContent=`${photoIndex+1} / ${photos.length}`;}
document.querySelectorAll('[data-gallery]').forEach(button=>button.addEventListener('click',()=>{showPhoto(Number(button.dataset.gallery));gallery.showModal();}));
document.querySelector('#gallery-prev').addEventListener('click',()=>showPhoto(photoIndex-1));
document.querySelector('#gallery-next').addEventListener('click',()=>showPhoto(photoIndex+1));
gallery.addEventListener('keydown',e=>{if(e.key==='ArrowRight'){e.preventDefault();showPhoto(photoIndex+1);}if(e.key==='ArrowLeft'){e.preventDefault();showPhoto(photoIndex-1);}});
