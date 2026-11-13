// Le moteur reste celui du journal publié : les prochaines corrections sont suivies.
importScripts('https://republikgarden-a11y.github.io/tradeatlas/gardenz-actuz/sw.js');
// Une seule migration des anciens onglets Netlify, sans effacer les favoris.
self.addEventListener('activate', event => event.waitUntil((async () => {
  const state = await caches.open('actuz-netlify-migration-20261113');
  const marker = new Request(new URL('/migration-effectuee', self.location.origin));
  if (await state.match(marker)) return;
  await state.put(marker, new Response('ok'));
  for (const client of await self.clients.matchAll({type:'window', includeUncontrolled:true})) {
    const url = new URL(client.url);
    if (url.origin !== self.location.origin) continue;
    if (url.pathname === '/reparer-cache.html') { url.pathname='/'; url.search=''; url.hash=''; }
    try { await client.navigate(url.href); } catch {}
  }
})()));
