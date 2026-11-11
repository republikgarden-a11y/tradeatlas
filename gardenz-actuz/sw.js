// The shell is refreshed from the network; read articles/images remain available offline.
const CACHE='gardenz-actuz-v3-755f782cfcd2';
const FILES=["./", "index.html", "app.css", "app.js", "journal.css", "install.css", "live.css", "live.js", "translation.js", "manifest.webmanifest", "assets/fraktur.ttf", "assets/icon-192.png", "assets/icon-512.png", "editions.json", "data/latest.json", "data/index.json"];
const scopeURL=new URL(self.registration.scope);
const keyFor=url=>new Request(url.origin+url.pathname);
self.addEventListener('install',event=>event.waitUntil((async()=>{
  const cache=await caches.open(CACHE);
  await Promise.all(FILES.map(async file=>{
    const request=new Request(new URL(file,scopeURL),{cache:'reload'}),response=await fetch(request);
    if(!response.ok)throw new Error('Cache incomplet : '+file);
    await cache.put(keyFor(new URL(request.url)),response);
  }));
  await self.skipWaiting();
})()));
self.addEventListener('activate',event=>event.waitUntil((async()=>{
  const cache=await caches.open(CACHE);
  // Preserve previously read daily archives and image bytes across shell upgrades.
  for(const name of await caches.keys()){
    if(!name.startsWith('gardenz-actuz-')||name===CACHE)continue;
    const previous=await caches.open(name);
    for(const request of await previous.keys()){
      if(/\/(?:assets\/|data\/history\/)/.test(new URL(request.url).pathname)&&!await cache.match(request)){
        const response=await previous.match(request);if(response)await cache.put(request,response);
      }
    }
    await caches.delete(name);
  }
  await self.clients.claim();
})()));
async function cachePut(key,response){
  const cache=await caches.open(CACHE);await cache.put(key,response.clone());
  const keys=await cache.keys();
  if(keys.length>350){
    const pinned=new Set(FILES.map(file=>new URL(file,scopeURL).href));
    for(const old of keys){if(!pinned.has(old.url)){await cache.delete(old);if((await cache.keys()).length<=300)break;}}
  }
}
function offlineResponse(response){
  const headers=new Headers(response.headers);headers.set('X-Gardenz-Cache','offline');
  return new Response(response.body,{status:response.status,statusText:response.statusText,headers});
}
self.addEventListener('fetch',event=>{
  const request=event.request,url=new URL(request.url);
  if(request.method!=='GET'||url.origin!==scopeURL.origin||!url.pathname.startsWith(scopeURL.pathname)||url.pathname.endsWith('/sw.js'))return;
  const key=request.mode==='navigate'?keyFor(new URL('index.html',scopeURL)):keyFor(url);
  if(/\/assets\/.*\.(?:jpg|jpeg|png|webp|ttf|woff2)$/.test(url.pathname)){
    event.respondWith((async()=>{
      const cached=await caches.match(key);if(cached)return cached;
      const response=await fetch(request);if(response.ok){try{await cachePut(key,response)}catch{}}return response;
    })());return;
  }
  event.respondWith((async()=>{
    try{
      const response=await fetch(request,{cache:'no-store'});if(!response.ok)throw new Error('HTTP '+response.status);
      try{await cachePut(key,response)}catch{}return response;
    }catch(error){const cached=await caches.match(key);if(cached)return offlineResponse(cached);throw error;}
  })());
});
