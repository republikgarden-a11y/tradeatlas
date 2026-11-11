'use strict';
(()=>{
const el=id=>document.getElementById(id),readStore=(key,fallback)=>{try{return JSON.parse(localStorage.getItem(key))||fallback}catch{return fallback}};
let news=null,saved=new Set(readStore('actuz-saved',[])),onlySaved=false,active='live',busy=false;
const dateLabel=d=>new Date(d).toLocaleString('fr-FR',{timeZone:'Europe/Paris',day:'numeric',month:'long',hour:'2-digit',minute:'2-digit'});
function node(tag,text,cls){const n=document.createElement(tag);if(text!==undefined)n.textContent=text;if(cls)n.className=cls;return n}
function safeURL(s){try{const u=new URL(s,location.href);return ['https:','http:'].includes(u.protocol)?u.href:''}catch{return ''}}
function setView(view){active=view;const live=view==='live';el('live-panel').hidden=!live;el('archive-panel').hidden=live;document.querySelectorAll('[data-view]').forEach(b=>b.setAttribute('aria-selected',String(b.dataset.view===view)));if(!live)el('edition-select').focus();}
document.querySelectorAll('[data-view]').forEach(b=>b.addEventListener('click',()=>setView(b.dataset.view)));
function render(){
 if(!news)return;
 const age=news.lastSuccess?(Date.now()-new Date(news.lastSuccess))/3600000:Infinity;
 el('news-status').textContent=news.status==='error'?'Collecte en échec — derniers articles conservés':age>30?'La collecte a du retard':news.status==='partial'?'Collecte partielle':'Sources actualisées';
 el('news-checked').textContent=(news.lastSuccess?'Dernière collecte réussie : '+dateLabel(news.lastSuccess)+' · Paris':'Aucune collecte réussie')+' · '+news.sources.filter(s=>s.ok).length+'/'+news.sources.length+' sources accessibles';
 const query=el('live-query').value.toLocaleLowerCase('fr'),language=el('live-language').value;
 const items=[...news.items].sort((a,b)=>(a.language!=="fr")-(b.language!=="fr")||new Date(b.publishedAt)-new Date(a.publishedAt)).filter(i=>(!language||i.language===language)&&(!onlySaved||saved.has(i.id))&&(!query||(i.title+' '+i.excerpt+' '+i.source).toLocaleLowerCase('fr').includes(query)));
 el('news-list').replaceChildren();el('live-count').textContent=items.length+' article'+(items.length!==1?'s':'')+' · '+(onlySaved?'ta sélection':'collectés sur les 30 derniers jours');
 if(!items.length)el('news-list').append(node('p',onlySaved?'Aucun article enregistré avec ces filtres.':'Aucun article ne correspond. Essaie un autre mot ou une autre langue.','empty-news'));
 for(const i of items){
  const article=node('article',undefined,'news-item'+(!i.image?' no-image':''));
  if(i.image&&/^assets\/live-[\w-]+\.(jpg|png|webp)$/.test(i.image)){
   const figure=node('figure',undefined,'news-image'),a=node('a');a.href=safeURL(i.url);a.target='_blank';a.rel='noopener';const img=node('img');img.src=i.image;img.alt='Visuel publié par '+i.source;img.loading='lazy';img.decoding='async';img.addEventListener('error',()=>{figure.remove();article.classList.add('no-image')},{once:true});a.append(img);figure.append(a,node('figcaption',i.credit));article.append(figure);
  }
  const copy=node('div',undefined,'news-copy');copy.append(node('p',i.source+' · '+dateLabel(i.publishedAt)+' Paris · '+({fr:'Français',en:'Anglais',de:'Allemand'}[i.language]||i.language),'news-meta'));
  const h=node('h2'),a=node('a',i.title);a.href=safeURL(i.url);a.target='_blank';a.rel='noopener';h.append(a);copy.append(h);
  if(i.excerpt)copy.append(node('p',i.excerpt+'…','news-excerpt'));
  copy.append(node('p','Titre et extrait de la source · vérification éditoriale non réalisée.','news-meta'));
  const tail=node('div',undefined,'news-tail'),link=node('a','Lire la source');link.href=safeURL(i.url);link.target='_blank';link.rel='noopener';tail.append(link);
  const b=node('button',saved.has(i.id)?'Enregistré':'Garder pour plus tard','save-news');b.type='button';b.setAttribute('aria-pressed',String(saved.has(i.id)));b.addEventListener('click',()=>{saved.has(i.id)?saved.delete(i.id):saved.add(i.id);try{localStorage.setItem('actuz-saved',JSON.stringify([...saved]))}catch{}render()});tail.append(b);copy.append(tail);article.append(copy);el('news-list').append(article);
 }
 const list=el('sources-health');list.replaceChildren();for(const s of news.sources){list.append(node('li',s.name+' — '+(s.ok?'accessible, '+s.count+' publication(s) dans les dernières 24 h':'indisponible lors du dernier contrôle')))}
}
async function refresh(){if(busy)return;busy=true;el('refresh-news').disabled=true;try{
 const r=await fetch('data/latest.json?t='+Date.now(),{cache:'no-store',signal:AbortSignal.timeout(12000)});if(!r.ok)throw Error('HTTP');const data=await r.json();if(!Array.isArray(data.items)||!Array.isArray(data.sources))throw Error('Format');news=data;try{localStorage.setItem('actuz-news-cache',JSON.stringify(data))}catch{}render();
}catch{if(!news)news=readStore('actuz-news-cache',null);if(news)render();el('news-status').textContent='Réseau indisponible — contenu conservé';el('news-checked').textContent=news?.lastSuccess?'Dernière collecte réussie : '+dateLabel(news.lastSuccess):'Réessaie quand la connexion est disponible.';}finally{busy=false;el('refresh-news').disabled=false}}
el('refresh-news').addEventListener('click',refresh);el('live-query').addEventListener('input',render);el('live-language').addEventListener('change',render);el('saved-toggle').addEventListener('click',()=>{onlySaved=!onlySaved;el('saved-toggle').setAttribute('aria-pressed',String(onlySaved));render()});
addEventListener('online',refresh);document.addEventListener('visibilitychange',()=>{if(!document.hidden)refresh()});setInterval(refresh,300000);
if(new URL(location.href).searchParams.has('date'))setView('archives');refresh();
})();
