// engage.js - optimistic like/save toggles
(function(){
  function getCookie(name){
    var v = document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)');
    return v ? v.pop() : '';
  }
  var csrftoken = getCookie('csrftoken');

  function toggleButton(btn, pressed){
    btn.setAttribute('aria-pressed', pressed ? 'true' : 'false');
  }

  function postJSON(url, data){
    return fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrftoken,
        'X-Requested-With': 'XMLHttpRequest'
      },
      body: JSON.stringify(data || {})
    }).then(function(resp){
      if (!resp.ok) throw new Error('Network response was not ok');
      return resp.json();
    });
  }

  function init(root){
    root = root || document;
    root.querySelectorAll('.btn-like').forEach(function(btn){
      if (btn.dataset.engaged === '1') return;
      btn.addEventListener('click', function(){
        var postId = btn.getAttribute('data-post-id');
        var countEl = btn.querySelector('.count');
        var current = parseInt(countEl.textContent || '0', 10);
        // optimistic toggle
        var pressed = btn.getAttribute('aria-pressed') === 'true';
        toggleButton(btn, !pressed);
        countEl.textContent = pressed ? Math.max(0, current - 1) : (current + 1);
        // fire API
        postJSON('/api/posts/'+postId+'/like/', { toggle: !pressed }).catch(function(){
          // rollback on error
          toggleButton(btn, pressed);
          countEl.textContent = current;
        });
      });
      btn.dataset.engaged = '1';
    });

    root.querySelectorAll('.btn-save').forEach(function(btn){
      if (btn.dataset.engaged === '1') return;
      btn.addEventListener('click', function(){
        var postId = btn.getAttribute('data-post-id');
        var pressed = btn.getAttribute('aria-pressed') === 'true';
        toggleButton(btn, !pressed);
        postJSON('/api/posts/'+postId+'/save/', { save: !pressed }).catch(function(){
          toggleButton(btn, pressed);
        });
      });
      btn.dataset.engaged = '1';
    });
  }

  document.addEventListener('DOMContentLoaded', function(){ init(document); });
  window.blogEngage = { init: init };
})();
