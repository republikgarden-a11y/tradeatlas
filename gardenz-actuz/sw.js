// All included editions and source images are cached together for offline reading.
const CACHE='gardenz-actuz-c29f99113798';
const FILES=["./", "app.css", "app.js", "assets/005b162afeebabf1c9a2.jpg", "assets/060c49d213ff6c28fc27.png", "assets/078aae4d93ca6ebf.png", "assets/0bcf0bd82ecc89390d03.jpg", "assets/0faacc044abaaafc90af.jpg", "assets/10f1f4b64b690b5f.png", "assets/177587d78e92a12e0fe7.png", "assets/2f6dbe948a5ce289.jpg", "assets/32b323feddbc3886716d.png", "assets/392d99c7ddaf1982cb5d.png", "assets/3f87d88b80f0efa7.jpg", "assets/41d17ccacded0ee5.png", "assets/42aa497aa0ceddf9ae50.jpg", "assets/42b7f8f75efc71f6.png", "assets/5de8858b7690d90e9b1b.png", "assets/6476cc23b457bb48.webp", "assets/6aeeb6d760c17d2f71d5.jpg", "assets/7070352cba50892ad0b5.jpg", "assets/76d94454c7eb5f4d350e.jpg", "assets/7f866e7d2425bc538110.jpg", "assets/859f5d15fbaf4311e052.jpg", "assets/88b0f93845143d8defe6.jpg", "assets/95ffe380fbd0cd377918.jpg", "assets/9f14d137049e0996e1fb.png", "assets/a94ef8618c38c88f.webp", "assets/aa7db3ef59787621.webp", "assets/ae559f27c610abea8748.jpg", "assets/b1f23a58ad7356f43787.png", "assets/bf4254ccaff3dcc21718.jpg", "assets/bfb9313e05c89a93.jpg", "assets/c1d88f1c9dd46533f938.webp", "assets/c5786292c33ef09b.jpg", "assets/c57f57a415ac508b9417.jpg", "assets/deeef8528065dac0b939.jpg", "assets/e02985fed52baa3dddf6.jpg", "assets/ef4b5ae78b49224c7190.jpg", "assets/f4af56e9ba21fcce7df0.png", "assets/fa76081a5dc96f8e4573.jpg", "assets/fraktur.ttf", "assets/icon-180.png", "assets/icon-192.png", "assets/icon-512.png", "assets/live-42095fcae4b380b97e27.webp", "assets/live-9cd057629423b66cd1a6.webp", "assets/live-a7825e91d82c5ae69c85.webp", "assets/live-be8b258ef8f5ec2a3f1b.webp", "assets/live-d0d93b7c94120b464166.webp", "assets/live-e30b3b9bf4cf7848ad6d.webp", "data/history/2026-11-11.json", "data/latest.json", "editions.json", "index.html", "install.css", "journal.css", "live.css", "live.js", "manifest.webmanifest"];
self.addEventListener('install',event=>event.waitUntil(caches.open(CACHE).then(cache=>cache.addAll(FILES)).then(()=>self.skipWaiting())));
self.addEventListener('activate',event=>event.waitUntil(caches.keys().then(keys=>Promise.all(keys.filter(key=>key.startsWith('gardenz-actuz-')&&key!==CACHE).map(key=>caches.delete(key)))).then(()=>self.clients.claim())));
self.addEventListener('fetch',event=>{
 const request=event.request,url=new URL(request.url);
 if(request.method!=='GET'||url.origin!==self.location.origin)return;
 if(request.mode==='navigate'){
  event.respondWith(fetch(request).then(response=>response.ok?response:caches.match('./index.html')).catch(()=>caches.match('./index.html')));return;
 }
 if(url.pathname.endsWith('/sw.js'))return;
 if(url.pathname.endsWith('/data/latest.json')||url.pathname.endsWith('/editions.json')||url.pathname.endsWith('/app.js')||url.pathname.endsWith('.css')||url.pathname.endsWith('/manifest.webmanifest')){
  event.respondWith((async()=>{
    try{
      const response=await fetch(request,{cache:'no-store'});
      if(!response.ok)throw new Error('HTTP '+response.status);
      const cache=await caches.open(CACHE);await cache.put(request,response.clone());return response;
    }catch(error){
      const cached=await caches.match(request);
      if(!cached)throw error;
      const headers=new Headers(cached.headers);headers.set('X-Gardenz-Cache','offline');
      return new Response(cached.body,{status:cached.status,statusText:cached.statusText,headers});
    }
  })());return;
 }
 event.respondWith(caches.match(request).then(cached=>cached||fetch(request)));
});
