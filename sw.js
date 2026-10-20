// Opens the word cards instantly from the device: the page is served from cache and refreshed in the
// background, so a new version shows up on the next launch. Audio is left to the browser (Safari's
// <audio> needs real range responses).
const CACHE = 'freya-cards-v1';
const PAGE = './';

self.addEventListener('install', e => {
  self.skipWaiting();
  e.waitUntil(caches.open(CACHE).then(c => c.add(PAGE)));
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
    const cached = await c.match(PAGE);
    const fresh = fetch(e.request).then(res => {
      if (res.ok) c.put(PAGE, res.clone());
      return res;
    });
    if (cached) {
      e.waitUntil(fresh.catch(() => {}));
      return cached;
    }
    return fresh;
  }));
});
