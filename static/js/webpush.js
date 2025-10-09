// Client-side helper to register service worker and subscribe for push notifications
(async function(){
  if (!('serviceWorker' in navigator) || !('PushManager' in window)) return;
  try{
    const reg = await navigator.serviceWorker.register('/static/sw.js');
    console.log('ServiceWorker registered', reg);
    // Fetch VAPID public key from backend
    const r = await fetch('/webpush/vapid-public-key/');
    if (!r.ok) return;
    const vapidPublicKey = await r.text();
    function urlBase64ToUint8Array(base64String) {
      const padding = '='.repeat((4 - base64String.length % 4) % 4);
      const base64 = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/');
      const rawData = window.atob(base64);
      const outputArray = new Uint8Array(rawData.length);
      for (let i = 0; i < rawData.length; ++i) {
        outputArray[i] = rawData.charCodeAt(i);
      }
      return outputArray;
    }
    const sub = await reg.pushManager.getSubscription() || await reg.pushManager.subscribe({
      userVisibleOnly: true,
      applicationServerKey: urlBase64ToUint8Array(vapidPublicKey)
    });
    // Send subscription to server
    await fetch('/webpush/save-subscription/', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify(sub.toJSON())
    });
    console.log('Push subscription saved');
  }catch(e){ console.warn('Push reg failed', e); }
})();
