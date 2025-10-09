self.addEventListener('install', function(event) {
  console.log('Service Worker installing.');
  self.skipWaiting();
});

self.addEventListener('activate', function(event) {
  console.log('Service Worker activated.');
});

self.addEventListener('fetch', function(event) {
  // We can add caching strategies here later if desired.
});

/* Push handling (merged from sw.js) */
self.addEventListener('push', function(event) {
  let payload = {};
  try { payload = event.data.json(); } catch(e) { payload = { title: 'Notification', body: event.data ? event.data.text() : '' }; }
  const title = payload.title || 'تنبيه';
  const body = payload.body || 'حدث جديد على الموقع.';
  const icon = payload.icon || '/static/img/android-chrome-192x192.png';
  const tag = payload.tag || 'site-update';
  event.waitUntil(self.registration.showNotification(title, { body: body, icon: icon, tag: tag }));
});

self.addEventListener('notificationclick', function(event) {
  event.notification.close();
  event.waitUntil(clients.matchAll({ type: 'window', includeUncontrolled: true }).then(function(clientList) {
    if (clientList.length > 0) {
      let client = clientList[0];
      for (let i=0;i<clientList.length;i++){
        if (clientList[i].focused) client = clientList[i];
      }
      return client.focus();
    }
    return clients.openWindow('/');
  }));
});
