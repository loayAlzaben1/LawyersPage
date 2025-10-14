// Client-side helper to register service worker and subscribe for push notifications
(async function(){
  if (!('serviceWorker' in navigator) || !('PushManager' in window)) return;
  try{
    // register service worker at site root so its scope covers the whole site
    const reg = await navigator.serviceWorker.register('/service-worker.js');
    console.log('ServiceWorker registered', reg);
    // Read VAPID public key injected into page by templates. Fallback to fetch if missing.
    let vapidPublicKey = window.SITE_VAPID_PUBLIC_KEY || null;
    if (!vapidPublicKey){
      try{
        const r = await fetch('/webpush/vapid-public-key/');
        if (r.ok) vapidPublicKey = await r.text();
      }catch(e){ console.warn('Failed to fetch VAPID key', e); }
    }
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
    // Send subscription to server (save)
    await fetch('/webpush/save-subscription/', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify(sub.toJSON())
    });
    console.log('Push subscription saved');

    // If user is authenticated, attempt to link this subscription to the user
    try{
      if (window.SITE_USER_AUTHENTICATED === true || window.SITE_USER_AUTHENTICATED === 'true'){
        // need CSRF token for Django POST
        function getCookie(name) {
          const value = `; ${document.cookie}`;
          const parts = value.split(`; ${name}=`);
          if (parts.length === 2) return parts.pop().split(';').shift();
        }
        const csrftoken = getCookie('csrftoken');
        await fetch('/webpush/link-subscription/', {
          method: 'POST',
          headers: {'Content-Type':'application/json', 'X-CSRFToken': csrftoken},
          body: JSON.stringify({ endpoint: sub.endpoint })
        });
        console.log('Linked subscription to user (attempted)');
      }
    }catch(e){ console.warn('link-subscription failed', e); }
  }catch(e){ console.warn('Push reg failed', e); }
})();
