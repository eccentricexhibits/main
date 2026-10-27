(() => {
  'use strict';
  const bundle = JSON.parse(document.getElementById('mockup-data').textContent);
  window.REMARKABLE_MOCKUP = bundle;
  const pages = {index:'Home',agenda:'Agenda',speakers:'Speakers',faq:'FAQ'};
  const sizes = {desktop:[1280,1440,1600],mobile:[320,390,430]};
  const sections = {
    index:[['','Opening'],['about','The meeting point'],['experience-title','The experience'],['speakers-title','The people'],['recap-title','A look back'],['gallery-title','The gallery'],['closing-title','Join us']],
    agenda:[['','Opening'],['day-tab-1','The schedule'],['venue','The venue'],['closing-title','Join us']],
    speakers:[['','Opening'],['speakers','The speakers'],['on-stage','On stage'],['closing-title','Join us']],
    faq:[['','Opening'],['topic-1','Questions & answers'],['venue','The venue'],['closing-title','Join us']]
  };
  const query = new URLSearchParams(location.search);
  const state = {
    page:Object.hasOwn(pages,query.get('page'))?query.get('page'):'index',
    mode:query.get('mode')==='mobile'?'mobile':'desktop',
    desktopWidth:1440,mobileWidth:390,search:'',hash:''
  };
  const requestedWidth = Number(query.get('width'));
  if(sizes[state.mode].includes(requestedWidth)) state[state.mode+'Width']=requestedWidth;
  const frame = document.getElementById('event-preview');
  const stage = document.querySelector('.preview-stage');
  const widthSelect = document.getElementById('preview-width');
  const sectionSelect = document.getElementById('section-jump');
  const modeButtons = [...document.querySelectorAll('[data-mode]')];
  const pageButtons = [...document.querySelectorAll('[data-page]')];

  function remember() {
    try {
      const url = new URL(location.href);
      url.searchParams.set('page',state.page);
      url.searchParams.set('mode',state.mode);
      url.searchParams.set('width',String(state[state.mode+'Width']));
      history.replaceState(null,'',url);
    } catch (_) { /* The file remains usable in browsers that restrict local-file history. */ }
  }
  function fitPreview() {
    const box=stage.getBoundingClientRect(),style=getComputedStyle(stage);
    const availableWidth=Math.max(200,box.width-Number(style.paddingLeft.replace('px',''))-Number(style.paddingRight.replace('px','')));
    const availableHeight=Math.max(280,box.height-Number(style.paddingTop.replace('px',''))-Number(style.paddingBottom.replace('px','')));
    const width=state[state.mode+'Width'],border=state.mode==='mobile'?8:1;
    const scale=Math.min(1,availableWidth/(width+border*2));
    const height=state.mode==='mobile'?Math.min(844,Math.max(280,(availableHeight/scale)-border*2)):Math.max(280,(availableHeight/scale)-border*2);
    const root=document.documentElement.style;
    root.setProperty('--viewport-width',width+'px');
    root.setProperty('--viewport-height',Math.floor(height)+'px');
    root.setProperty('--preview-scale',String(scale));
    root.setProperty('--display-width',((width+border*2)*scale)+'px');
    root.setProperty('--display-height',((Math.floor(height)+border*2)*scale)+'px');
    document.getElementById('dimension-caption').textContent=width+' px'+(scale<.99?' · Fit to window':'');
  }
  function refreshControls() {
    document.body.dataset.mode=state.mode;
    modeButtons.forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.mode===state.mode)));
    pageButtons.forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.page===state.page)));
    widthSelect.replaceChildren(...sizes[state.mode].map(n=>new Option(n+' px',String(n))));
    widthSelect.value=String(state[state.mode+'Width']);
    sectionSelect.replaceChildren(...sections[state.page].map(([value,label])=>new Option(label,value)));
    sectionSelect.value=sections[state.page].some(([id])=>id===state.hash.slice(1))?state.hash.slice(1):'';
    frame.title='Remarkable 2027 '+state.mode+' '+pages[state.page];
    const caption=pages[state.page]+' · '+(state.mode==='desktop'?'Desktop':'Mobile');
    document.getElementById('view-caption').textContent=caption;
    document.getElementById('view-status').textContent=caption+' mockup selected.';
    fitPreview();remember();
  }
  function anchorSection() {
    const target=state.hash&&frame.contentDocument?.getElementById(state.hash.slice(1));
    if(target&&!state.hash.startsWith('#session-')) target.scrollIntoView({block:'start',behavior:'instant'});
  }
  function renderPage() {
    const route=JSON.stringify({search:state.search,hash:state.hash});
    const setup='window.REMARKABLE_COPY=parent.REMARKABLE_MOCKUP.copy;window.REMARKABLE_ASSETS=parent.REMARKABLE_MOCKUP.assets;window.REMARKABLE_PREVIEW_ROUTE='+route+';';
    const lt=String.fromCharCode(60);
    const script=lt+'script>'+setup+bundle.app+lt+'/script>';
    frame.srcdoc=bundle.pages[state.page]
      .replace(lt+'/head>',()=>lt+'style>'+bundle.styles+lt+'/style>'+lt+'/head>')
      .replace(lt+'/body>',()=>script+lt+'/body>');
  }
  function navigate(page,search='',hash='') {
    state.page=page;state.search=search;state.hash=hash;
    refreshControls();renderPage();
  }
  frame.addEventListener('load',()=>{
    const doc=frame.contentDocument;
    if(!doc) return;
    doc.addEventListener('click',event=>{
      const link=event.target.closest('a[href]');
      if(!link||link.target==='_blank'||event.ctrlKey||event.metaKey||event.shiftKey||event.altKey) return;
      const href=link.getAttribute('href');
      if(href.startsWith('#')) {
        event.preventDefault();state.hash=href;
        sectionSelect.value=sections[state.page].some(([id])=>id===href.slice(1))?href.slice(1):'';
        anchorSection();return;
      }
      const url=new URL(href,'https://mockup.invalid/'+state.page+'.html');
      const page=url.pathname.split('/').pop().replace(/\.html$/,'');
      if(url.origin==='https://mockup.invalid'&&Object.hasOwn(pages,page)) {
        event.preventDefault();navigate(page,url.search,url.hash);
      }
    });
    anchorSection();
  });
  modeButtons.forEach(button=>button.addEventListener('click',()=>{
    if(state.mode===button.dataset.mode) return;
    state.mode=button.dataset.mode;refreshControls();requestAnimationFrame(anchorSection);
  }));
  pageButtons.forEach(button=>button.addEventListener('click',()=>{
    if(state.page!==button.dataset.page) navigate(button.dataset.page);
  }));
  widthSelect.addEventListener('change',()=>{state[state.mode+'Width']=Number(widthSelect.value);refreshControls();requestAnimationFrame(anchorSection);});
  sectionSelect.addEventListener('change',()=>{
    state.hash=sectionSelect.value?'#'+sectionSelect.value:'';
    if(state.hash) anchorSection();else frame.contentWindow.scrollTo({top:0,behavior:'instant'});
  });
  new ResizeObserver(fitPreview).observe(stage);
  refreshControls();renderPage();
})();
