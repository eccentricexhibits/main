(() => {
  'use strict';
  const pages = {index:'Home',agenda:'Agenda',speakers:'Speakers',faq:'FAQ'};
  const widths = [320,390,430];
  const sections = {
    index:[['','Opening'],['about','The meeting point'],['experience-title','The experience'],['speakers-title','The people'],['recap-title','A look back'],['gallery-title','The gallery'],['closing-title','Join us']],
    agenda:[['','Opening'],['day-tab-1','The schedule'],['venue','The venue'],['closing-title','Join us']],
    speakers:[['','Opening'],['speakers','The speakers'],['on-stage','On stage'],['closing-title','Join us']],
    faq:[['','Opening'],['topic-1','Questions & answers'],['venue','The venue'],['closing-title','Join us']]
  };
  const frame = document.getElementById('phone-preview');
  const buttons = [...document.querySelectorAll('[data-page]')];
  const select = document.getElementById('phone-width');
  const jump = document.getElementById('section-jump');
  const query = new URLSearchParams(location.search);
  let page = Object.hasOwn(pages,query.get('page')) ? query.get('page') : 'index';
  let width = widths.includes(Number(query.get('width'))) ? Number(query.get('width')) : 390;

  function refresh() {
    const previousSection = jump.dataset.page === page ? jump.value : '';
    jump.replaceChildren(...sections[page].map(([value,label]) => new Option(label,value)));
    jump.value = previousSection;
    jump.dataset.page = page;
    buttons.forEach(b => b.setAttribute('aria-pressed',String(b.dataset.page === page)));
    document.getElementById('page-name').textContent = pages[page];
    document.getElementById('open-page').href = page + '.html';
    frame.title = 'Remarkable 2027 mobile ' + pages[page];
    document.getElementById('review-status').textContent = pages[page] + ' page selected.';
    document.getElementById('width-label').textContent = width + ' px';
    document.documentElement.style.setProperty('--preview-width',width + 'px');
    select.value = String(width);
    const url = new URL(location.href);
    url.searchParams.set('page',page);
    url.searchParams.set('width',String(width));
    history.replaceState(null,'',url);
  }
  buttons.forEach(button => button.addEventListener('click',() => {
    if (page === button.dataset.page) return;
    page = button.dataset.page;
    frame.src = page + '.html';
    refresh();
  }));
  select.addEventListener('change',() => {width=Number(select.value);refresh();});
  jump.addEventListener('change',() => {
    const url = new URL(frame.contentWindow.location.href);
    url.hash = jump.value;
    frame.src = url.href;
  });
  frame.addEventListener('load',() => {
    try {
      const current = new URL(frame.contentWindow.location.href).pathname.split('/').pop().replace(/\.html$/,'') || 'index';
      if (Object.hasOwn(pages,current)) {page=current;refresh();}
    } catch (_) { /* A linked external destination does not change the preview selection. */ }
  });
  refresh();
  if (frame.getAttribute('src') !== page + '.html') frame.src = page + '.html';
})();
