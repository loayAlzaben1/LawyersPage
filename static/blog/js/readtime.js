// readtime.js - compute approximate read time from character count
(function(){
  function charsToReadTime(chars){
    // Approximate words assuming 5 chars per word, 200 wpm
    var words = Math.max(1, Math.round(chars / 5));
    var minutes = Math.max(1, Math.round(words / 200));
    return minutes + ' دقائق قراءة';
  }

  function init(){
    document.querySelectorAll('.read-time').forEach(function(span){
      var chars = parseInt(span.getAttribute('data-content') || '0', 10);
      span.textContent = charsToReadTime(chars);
    });
  }

  document.addEventListener('DOMContentLoaded', init);
  window.blogReadtime = { init: init };
})();
