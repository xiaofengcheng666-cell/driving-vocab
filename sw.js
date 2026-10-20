// Network first, so every launch gets the latest version; if the network is slow (over 2.5 s) or
// offline, the copy saved on the device is shown instead. Audio is left to the browser (Safari's
// <audio> needs real range responses).
const CACHE = 'freya-cards-v3';
const PAGE = './';
const WAIT_MS = 2500;

self.addEventListener('install', e => {
  self.skipWaiting();
  e.waitUntil(caches.open(CACHE).then(c => c.add(new Request(PAGE, { cache: 'no-store' }))));
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys()
      .then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', e => {
  if (e.request.method !== 'GET' || e.request.mode !== 'navigate') return;
  e.respondWith(caches.open(CACHE).then(async c => {
    const fresh = fetch(e.request.url, { cache: 'no-store' }).then(res => {
      if (res.ok) c.put(PAGE, res.clone());
      return res;
    });
    e.waitUntil(fresh.catch(() => {}));
    const cached = await c.match(PAGE);
    if (!cached) return fresh;
    const slow = new Promise(r => setTimeout(() => r(cached), WAIT_MS));
    return Promise.race([fresh.then(r => r.ok ? r : cached, () => cached), slow]);
  }));
});
