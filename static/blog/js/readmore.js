// readmore.js: expand/collapse long excerpts in the blog index
(function(window){
  var limit = 300; // chars

  function initReadmore(root){
    root = root || document;
    // Find uninitialized cards (or all) and wire them
    Array.prototype.slice.call(root.querySelectorAll('.blog-card')).forEach(function(card){
      if (card.dataset.readmoreInit === '1') return; // already initialized
      var excerpt = card.querySelector('.excerpt');
      if (!excerpt) return;
      var fullText = excerpt.textContent.trim();
      if (fullText.length <= limit) {
    var btn = card.querySelector('.btn-readmore-new');
        if (btn && btn.dataset.inline === 'true') btn.style.display = 'none';
        card.dataset.readmoreInit = '1';
        return;
      }

      // create collapsed text
      var short = fullText.slice(0, limit).replace(/\s+\S+$/, '...');
      excerpt.dataset.fullText = fullText;
      excerpt.textContent = short;

      // wire inline expand for the new button
  var btn = card.querySelector('.btn-readmore-new');
  if (btn && btn.dataset.inline === 'true'){
        btn.addEventListener('click', function(e){
          e.preventDefault();
          if (btn.dataset.expanded === 'true'){
            excerpt.textContent = short;
            btn.dataset.expanded = 'false';
            if (btn.tagName.toLowerCase() === 'button') btn.textContent = 'اقرأ المزيد'; else btn.textContent = 'اقرأ المزيد';
          } else {
            excerpt.textContent = fullText;
            btn.dataset.expanded = 'true';
            if (btn.tagName.toLowerCase() === 'button') btn.textContent = 'اطوِ المقال'; else btn.textContent = 'اطوِ المقال';
          }
        });
      }

      card.dataset.readmoreInit = '1';
    });
  }

  // Auto-init on DOMContentLoaded
  document.addEventListener('DOMContentLoaded', function(){
    initReadmore(document);
    // Auto-expand if URL contains ?expand=1 or ?expand=true
    try{
      var params = new URLSearchParams(window.location.search);
      var shouldExpand = params.get('expand') === '1' || params.get('expand') === 'true';
      if (shouldExpand){
        Array.prototype.slice.call(document.querySelectorAll('.blog-card')).forEach(function(card){
          var btn = card.querySelector('.btn-readmore-new');
          var excerpt = card.querySelector('.excerpt');
          if (btn && btn.dataset.inline === 'true' && excerpt){
            // set full text
            if (excerpt.dataset.fullText) excerpt.textContent = excerpt.dataset.fullText;
            btn.dataset.expanded = 'true';
            btn.textContent = 'اطوِ المقال';
          }
        });
      } else {
        // support per-card auto-expand via attribute on button
        Array.prototype.slice.call(document.querySelectorAll('.btn-readmore-new[data-auto-expand="true"]')).forEach(function(btn){
          var card = btn.closest('.blog-card');
          if (!card) return;
          var excerpt = card.querySelector('.excerpt');
          if (excerpt && excerpt.dataset.fullText){
            excerpt.textContent = excerpt.dataset.fullText;
            btn.dataset.expanded = 'true';
            btn.textContent = 'اطوِ المقال';
          }
        });
      }
    }catch(e){/* ignore URL parsing errors */}
  });

  // Expose to global so other scripts can re-init after AJAX append
  window.blogReadmore = { init: initReadmore };

})(window);
