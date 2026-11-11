'use strict';
(function(root,factory){const api=factory();if(typeof module==='object'&&module.exports)module.exports=api;else root.GardenzTranslation=api;})(typeof window!=='undefined'?window:this,()=>{
  function valid(item){
    const t=item.translation;
    return !!(t&&t.targetLanguage==='fr'&&t.sourceLanguage===item.language&&t.sourceTitle===item.title&&t.sourceExcerpt===(item.excerpt||'')&&typeof t.title==='string'&&t.title.trim()&&(!item.excerpt||(typeof t.excerpt==='string'&&t.excerpt.trim())));
  }
  function display(item,enabled){
    if(!enabled||item.language==='fr')return {title:item.title,excerpt:item.excerpt||'',language:item.language,translated:false,unavailable:false};
    if(valid(item))return {title:item.translation.title,excerpt:item.translation.excerpt||'',language:'fr',translated:true,unavailable:false};
    return {title:item.title,excerpt:'La traduction française de ce titre et de cet extrait n’est pas disponible. « Lire en français » ouvre la traduction de l’article complet.',language:item.language,translated:false,unavailable:true};
  }
  function readerURL(item,enabled,original=false){
    let url;try{url=new URL(item.url);if(!['https:','http:'].includes(url.protocol))return '';}catch{return '';}
    if(!enabled||item.language==='fr'||original)return url.href;
    const translated=new URL('https://translate.google.com/translate');
    translated.searchParams.set('sl',['en','de'].includes(item.language)?item.language:'auto');
    translated.searchParams.set('tl','fr');translated.searchParams.set('hl','fr');translated.searchParams.set('u',url.href);
    return translated.href;
  }
  function savedCorpus(latest,stored,selected){const ids=new Set(selected);return [...new Map([...Object.values(stored),...latest].map(item=>[item.id,item])).values()].filter(item=>ids.has(item.id));}
  return {valid,display,readerURL,savedCorpus};
});
