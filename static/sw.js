const cacheName = "vehicules-pwa-cache-v1";
const assets = [
  "/",
  "/static/css/styles.css",  // à adapter selon ton projet
  "/static/icons/icon-192x192.png",
  "/static/icons/icon-512x512.png"
];

self.addEventListener("install", event => {
  event.waitUntil(
    caches.open(cacheName).then(cache => cache.addAll(assets))
  );
});

self.addEventListener("fetch", event => {
  event.respondWith(
    caches.match(event.request).then(res => res || fetch(event.request))
  );
});
