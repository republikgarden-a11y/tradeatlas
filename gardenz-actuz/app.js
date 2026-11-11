'use strict';
const $ = id => document.getElementById(id);
const normalize = value => value.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase().replace(/[’']/g, ' ');
const dateLabel = value => new Intl.DateTimeFormat('fr-FR', {day:'numeric',month:'long',year:'numeric',timeZone:'Europe/Paris'}).format(new Date(value+'T12:00:00Z'));
let editions = [], current, installPrompt;
const safeStore = {get(key){try{return localStorage.getItem(key)}catch{return null}},set(key,value){try{localStorage.setItem(key,value)}catch{}}};
if(safeStore.get('gardenz-colors')==='true') document.body.classList.add('original');
function syncColors(){const on=document.body.classList.contains('original');$('colors').textContent=on?'Images en sépia':'Images en couleurs';$('colors').setAttribute('aria-pressed',String(on));}
syncColors();
$('colors').addEventListener('click',()=>{document.body.classList.toggle('original');safeStore.set('gardenz-colors',String(document.body.classList.contains('original')));syncColors()});
function writeURL(push=true, article=''){
  const url=new URL(location.href);url.search='';url.hash=article;
  if(current)url.searchParams.set('date',current.date);
  url.searchParams.set('view','archives');
  if($('query').value.trim())url.searchParams.set('q',$('query').value.trim());
  if($('date-filter').value)url.searchParams.set('jour',$('date-filter').value);
  history[push?'pushState':'replaceState']({},'',url);
}
function showEdition(date,{push=true,article='',focus=false}={}){
  current=editions.find(e=>e.date===date)||editions[0];
  $('edition').innerHTML=current.html;
  $('new-edition').hidden=current.date===editions[0].date;
  $('edition-select').value=current.date;
  const index=editions.indexOf(current);
  $('previous').disabled=index===editions.length-1;
  $('next').disabled=index===0;
  $('latest').disabled=index===0;
  $('edition').hidden=false;$('results').hidden=true;
  if(!document.getElementById('live-panel')||document.getElementById('live-panel').hidden) document.title=`Gardenz Actuz — ${dateLabel(current.date)}`;
  if(push)writeURL(true,article);
  if(article)requestAnimationFrame(()=>{const target=document.getElementById(article);if(target){target.setAttribute('tabindex','-1');target.focus({preventScroll:true});target.scrollIntoView({behavior:'instant',block:'start'})}});
  else if(focus){$('content').focus({preventScroll:true});$('content').scrollIntoView({behavior:'instant',block:'start'})}
}
function clearSearch(){ $('query').value='';$('date-filter').value=''; }
function openDate(date,article=''){clearSearch();showEdition(date,{article,focus:!article})}
function matches(article,edition,terms){
  const [y,m,d]=edition.date.split('-');
  const dates=`${edition.date} ${d}/${m}/${y} ${+d}/${+m}/${y} ${d}-${m}-${y} ${dateLabel(edition.date)}`;
  const haystack=normalize(`${article.text} ${dates}`);
  return terms.every(term=>haystack.includes(term));
}
function node(tag,className,text){const el=document.createElement(tag);if(className)el.className=className;if(text!==undefined)el.textContent=text;return el}
function runSearch({push=true,focus=false}={}){
  const query=$('query').value.trim(), date=$('date-filter').value;
  if(!query&&!date){showEdition(current.date,{push,focus});return}
  const terms=normalize(query).split(/\s+/).filter(Boolean);
  const hits=[];
  editions.filter(e=>!date||e.date===date).forEach(e=>e.articles.filter(a=>matches(a,e,terms)).forEach(a=>hits.push({edition:e,article:a})));
  $('edition').hidden=true;$('results').hidden=false;
  $('results-title').textContent=query?`« ${query} »`:'Les articles de cette date';
  $('results-count').textContent=`${hits.length} ${hits.length===1?'article trouvé':'articles trouvés'}${date?' · édition du '+dateLabel(date):' · toutes les éditions'}`;
  const list=$('result-list');list.replaceChildren();
  if(!hits.length){const empty=node('div','empty-state');empty.append(node('h2','','Aucun article dans ces archives.'),node('p','','Essaie un autre mot-clé ou retire le filtre de date. Seules les éditions disponibles dans le kiosque sont recherchées.'));list.append(empty)}
  hits.forEach(({edition:e,article:a})=>{
    const card=node('article','result-card'+(a.image?'':' no-image'));
    if(a.image){const figure=node('figure');const img=node('img');img.src=a.image;img.alt='';img.loading='lazy';figure.append(img);if(a.creditHTML)figure.insertAdjacentHTML('beforeend',a.creditHTML);card.append(figure)}
    const copy=node('div');copy.append(node('div','result-meta',`Édition du ${dateLabel(e.date)} · ${a.region}`));
    const h=node('h2'),link=node('a','result-link',a.title);link.href=`?date=${e.date}#${a.id}`;
    link.addEventListener('click',event=>{if(event.button===0&&!event.metaKey&&!event.ctrlKey&&!event.shiftKey&&!event.altKey){event.preventDefault();openDate(e.date,a.id)}});
    h.append(link);copy.append(h,node('p','',a.summary),node('p','result-source',`${a.sourceDate}${a.status?' · '+a.status:''}`));card.append(copy);list.append(card);
  });
  document.title=`Recherche ${query||dateLabel(date)} — Gardenz Actuz`;
  if(push)writeURL();
  if(focus){$('content').focus({preventScroll:true});$('content').scrollIntoView({behavior:'instant',block:'start'})}
}
function route(){
  const url=new URL(location.href);
  if(!url.searchParams.has('date')&&url.searchParams.get('view')!=='archives'&&editions.length&&current)return;
  clearSearch();
  showEdition(url.searchParams.get('date'),{push:false});
  $('query').value=url.searchParams.get('q')||'';
  const filter=url.searchParams.get('jour')||'';
  $('date-filter').value=/^\d{4}-\d{2}-\d{2}$/.test(filter)?filter:'';
  if($('query').value||$('date-filter').value)runSearch({push:false});
  else if(url.hash){let id;try{id=decodeURIComponent(url.hash.slice(1))}catch{id=''};showEdition(current.date,{push:false,article:id})}
}
$('edition-select').addEventListener('change',e=>openDate(e.target.value));
$('previous').addEventListener('click',()=>{const i=editions.indexOf(current);if(i<editions.length-1)openDate(editions[i+1].date)});
$('next').addEventListener('click',()=>{const i=editions.indexOf(current);if(i>0)openDate(editions[i-1].date)});
$('latest').addEventListener('click',()=>openDate(editions[0].date));
$('search-form').addEventListener('submit',e=>{e.preventDefault();if(editions.length)runSearch({focus:true})});
$('reset-search').addEventListener('click',()=>openDate(current.date));
$('query').addEventListener('search',()=>{if(editions.length&&!$('query').value)runSearch()});
$('date-filter').addEventListener('change',()=>{if(editions.length)runSearch()});
addEventListener('popstate',()=>{if(editions.length)route()});
$('print').addEventListener('click',()=>window.print());
// Native installation is capability-based; platform detection only selects the fallback guide.
const standaloneQuery=matchMedia('(display-mode: standalone)');
let installedThisSession=false;
const isInstalled=()=>installedThisSession||standaloneQuery.matches||navigator.standalone===true;
function installPlatform(){
  const ua=navigator.userAgent;
  if(/FBAN|FBAV|Instagram|TikTok|Bytedance|Line\/|MicroMessenger|ChatGPT|; wv\)/i.test(ua))return 'embedded';
  if(/iPhone|iPad|iPod/i.test(ua)||(/Macintosh/i.test(ua)&&navigator.maxTouchPoints>1))return 'ios';
  if(/Android/i.test(ua))return 'android';
  return 'desktop';
}
function updateInstallUI(){
  const installed=isInstalled();
  $('install').hidden=installed;
  $('install-dock').hidden=installed;
  document.body.classList.toggle('has-install-dock',!installed);
  $('install').textContent=installPrompt?'Installer l’app':'Ajouter l’app';
  $('install-mobile').textContent=installPrompt?'Installer maintenant':'Ajouter l’app';
  $('install-now').disabled=!installPrompt;
  if($('install-dialog').open)renderInstallGuide();
}
function renderInstallGuide(){
  const installed=isInstalled();
  const platform=installPlatform();
  const guide=installed?'installed':installPrompt?'native':platform;
  ['native','ios','android','desktop','embedded'].forEach(id=>$('install-'+id).hidden=guide!==id);
  $('installed-message').hidden=!installed;
  $('install-no-settings').hidden=installed||platform==='desktop';
  $('install-title').textContent=installed?'Gardenz Actuz est déjà là.':guide==='native'?'Installe ton journal en un geste.':guide==='embedded'?'Ouvre ton journal dans le navigateur.':platform==='ios'?'Gardenz Actuz sur iPhone.':platform==='android'?'Ajoute Gardenz Actuz à ton téléphone.':'Gardenz Actuz sur ton ordinateur.';
  if(/iPad/i.test(navigator.userAgent)||(/Macintosh/i.test(navigator.userAgent)&&navigator.maxTouchPoints>1))$('install-title').textContent=installed?'Gardenz Actuz est déjà là.':'Gardenz Actuz sur iPad.';
  $('install-intro').textContent=installed?'L’icône te permet de retrouver le journal à tout moment.':guide==='native'?'Une confirmation, puis tu retrouves Gardenz Actuz parmi tes applications.':platform==='ios'?'Trois gestes, une seule fois.':'Retrouve le journal depuis ton écran d’accueil.';
  if(platform==='embedded')$('site-address').value=location.href;
}
function help(){renderInstallGuide();if(!$('install-dialog').open)$('install-dialog').showModal()}
async function requestInstall(){
  if(isInstalled()){help();return}
  if(!installPrompt){help();return}
  // prompt() must run directly in the click handler, while user activation is still present.
  const prompt=installPrompt;installPrompt=null;
  try{
    const choice=await prompt.prompt();
    if(choice?.outcome==='accepted'&&$('install-dialog').open)$('install-dialog').close();
  }catch{help()}
  updateInstallUI();
}
$('help').addEventListener('click',help);
$('close-dialog').addEventListener('click',()=>$('install-dialog').close());
$('install-dialog').addEventListener('click',e=>{if(e.target===$('install-dialog')){const r=e.target.getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)e.target.close()}});
addEventListener('beforeinstallprompt',e=>{e.preventDefault();installPrompt=e;updateInstallUI()});
['install','install-mobile','install-now'].forEach(id=>$(id).addEventListener('click',requestInstall));
addEventListener('appinstalled',()=>{installedThisSession=true;installPrompt=null;if($('install-dialog').open)$('install-dialog').close();updateInstallUI()});
standaloneQuery.addEventListener?.('change',updateInstallUI);
$('copy-address').addEventListener('click',async()=>{
  try{await navigator.clipboard.writeText($('site-address').value);$('copy-feedback').textContent='Lien copié. Ouvre-le dans Safari ou Chrome.'}
  catch{$('site-address').focus();$('site-address').select();$('copy-feedback').textContent='Sélectionne « Copier » pour récupérer cette adresse.'}
});
updateInstallUI();
$('reload').addEventListener('click',()=>location.reload());
let offlineReady=false;
function connection(){ $('connection').textContent=!navigator.onLine?'Hors connexion · archives locales':offlineReady?'Archives prêtes hors connexion':'En ligne'; }
addEventListener('online',()=>{connection();refreshEditions()});addEventListener('offline',()=>{connection();if(editions.length)$('sync-status').textContent=`Hors connexion · dernière édition conservée : ${dateLabel(editions[0].date)}`});connection();
let refreshing=false, lastChecked=0, corpusSignature='';
function validEditions(value){
  return Array.isArray(value)&&value.length>0&&value.every(e=>e&&/^\d{4}-\d{2}-\d{2}$/.test(e.date)&&typeof e.html==='string'&&e.html.length>0&&Number.isInteger(e.count)&&Array.isArray(e.articles)&&e.articles.every(a=>a&&typeof a.id==='string'&&typeof a.text==='string'&&typeof a.title==='string'))&&new Set(value.map(e=>e.date)).size===value.length;
}
function fillEditions(){
  const select=$('edition-select');select.replaceChildren();
  editions.forEach(e=>{const opt=node('option','',dateLabel(e.date));opt.value=e.date;select.append(opt)});select.disabled=false;
  $('archive-count').textContent=`${editions.length} éditions · ${editions.reduce((n,e)=>n+e.count,0)} articles et brèves`;
}
async function refreshEditions(){
  if(refreshing)return;
  refreshing=true;$('refresh-editions').disabled=true;
  $('sync-status').textContent='Vérification des éditions publiées…';
  try{
    const response=await fetch('editions.json',{cache:'no-store',signal:AbortSignal.timeout(20000)});if(!response.ok)throw Error('Archives indisponibles');
    const incoming=await response.json();if(!validEditions(incoming))throw Error('Archives invalides');
    incoming.sort((a,b)=>b.date.localeCompare(a.date));
    const signature=JSON.stringify(incoming), initial=editions.length===0;
    if(signature!==corpusSignature){
      const date=current?.date;editions=incoming;corpusSignature=signature;fillEditions();
      if(initial)route();
      else{
        const scroll=window.scrollY;
        current=editions.find(e=>e.date===date)||editions[0];
        if($('query').value||$('date-filter').value)runSearch({push:false});
        else showEdition(current.date,{push:false});
        window.scrollTo(0,scroll);
      }
      $('new-edition-label').textContent=`Nouvelle édition disponible : ${dateLabel(editions[0].date)}.`;
    }
    const cached=response.headers.get('X-Gardenz-Cache')==='offline'||!navigator.onLine;
    lastChecked=Date.now();
    $('sync-status').textContent=cached?`Archives hors connexion · dernière édition : ${dateLabel(editions[0].date)}. Vérification réseau impossible.`:`Vérifié à ${new Intl.DateTimeFormat('fr-FR',{hour:'2-digit',minute:'2-digit',timeZone:'Europe/Paris'}).format(new Date())} (Paris) · dernière édition publiée : ${dateLabel(editions[0].date)}`;
  }catch(error){
    $('sync-status').textContent=editions.length?`Vérification impossible · archives conservées jusqu’au ${dateLabel(editions[0].date)}. Réessaie avec une connexion.`:'Chargement impossible. Vérifie ta connexion puis réessaie.';
    if(!editions.length){$('archive-count').textContent='Archives indisponibles';$('edition').replaceChildren(node('h2','','Le journal n’a pas pu se charger.'),node('p','summary','Vérifie ta connexion puis utilise « Vérifier les nouveautés ».'));}
    console.error(error);
  }finally{refreshing=false;$('refresh-editions').disabled=false}
}
$('refresh-editions').addEventListener('click',()=>refreshEditions());
$('read-new-edition').addEventListener('click',()=>openDate(editions[0].date));
document.addEventListener('visibilitychange',()=>{if(document.visibilityState==='visible')refreshEditions()});
addEventListener('pageshow',event=>{if(event.persisted)refreshEditions()});
setInterval(()=>{if(document.visibilityState==='visible'&&Date.now()-lastChecked>240000)refreshEditions()},300000);
async function start(){
    await refreshEditions();
    if('serviceWorker' in navigator){
      const controlled=!!navigator.serviceWorker.controller;
      navigator.serviceWorker.addEventListener('controllerchange',()=>{if(controlled)$('update').hidden=false});
      navigator.serviceWorker.register('sw.js',{updateViaCache:'none'}).then(registration=>{registration.update().catch(()=>{});return navigator.serviceWorker.ready}).then(()=>{offlineReady=true;connection()}).catch(()=>{$('connection').textContent='En ligne · mode hors connexion indisponible'});
    }
}
start();
