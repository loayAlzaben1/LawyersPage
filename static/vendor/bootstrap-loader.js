(function () {
  // Try to load a local bootstrap bundle first. If it fails, load from CDN.
  function loadScript(src, onload, onerror) {
    var s = document.createElement('script');
    s.src = src;
    s.async = false;
    s.onload = onload;
    s.onerror = onerror;
    document.head.appendChild(s);
  }

  var local = '/static/vendor/bootstrap.bundle.min.js';
  var cdn = 'https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js';

  loadScript(local, function () {
    // loaded local successfully
    console.log('Loaded local bootstrap bundle');
  }, function () {
    // fallback to CDN
    console.warn('Local bootstrap bundle not found, loading from CDN');
    loadScript(cdn, function () { console.log('Loaded bootstrap from CDN'); }, function () { console.error('Failed to load bootstrap bundle'); });
  });
})();
