// ASLTalk service worker: page = network first (so your edits always show), libraries/model = cached after first load
const CACHE='asltalk-v1', CDN=['cdn.jsdelivr.net','storage.googleapis.com','cdn.tailwindcss.com'];
self.addEventListener('install',e=>{e.waitUntil(caches.open(CACHE).then(c=>c.addAll(['./','index.html','manifest.json','icon-192.png','icon-512.png']).catch(()=>{})).then(()=>self.skipWaiting()));});
self.addEventListener('activate',e=>{e.waitUntil(caches.keys().then(k=>Promise.all(k.filter(x=>x!==CACHE).map(x=>caches.delete(x)))).then(()=>self.clients.claim()));});
self.addEventListener('fetch',e=>{
  const r=e.request,u=new URL(r.url); if(r.method!=='GET') return;
  const same=u.origin===location.origin; if(!same&&!CDN.includes(u.hostname)) return;
  const store=res=>{if(res&&(res.ok||res.type==='opaque')){const cp=res.clone();caches.open(CACHE).then(c=>c.put(r,cp));}return res;};
  if(same) e.respondWith(fetch(r).then(store).catch(()=>caches.match(r)));
  else e.respondWith(caches.match(r).then(hit=>hit||fetch(r).then(store)));
});