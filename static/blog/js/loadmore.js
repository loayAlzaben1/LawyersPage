// loadmore.js: Fetch next pages and append card HTML
document.addEventListener('DOMContentLoaded', function(){
  var btn = document.getElementById('load-more-btn');
  if (!btn) return;
  var container = document.getElementById('cards-container');
  btn.addEventListener('click', function(){
    var next = btn.getAttribute('data-next-page');
    if (!next) return;
    btn.disabled = true;
    btn.textContent = 'جارٍ التحميل...';
    var xhr = new XMLHttpRequest();
    var url = window.location.pathname.replace(/\/$/, '') + '/page/?page=' + encodeURIComponent(next);
    xhr.open('GET', url, true);
    xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
    xhr.onreadystatechange = function(){
      if (xhr.readyState !== 4) return;
      if (xhr.status === 200){
        try{
          var data = JSON.parse(xhr.responseText);
          if (data.html){
            // create a temporary wrapper to parse the returned fragment
            var temp = document.createElement('div');
            temp.innerHTML = data.html;
            // append each child (cards are .col- elements)
            while (temp.firstChild){
              // append and keep a reference to the appended node for init
              var node = temp.firstChild;
              container.appendChild(node);

              // defensive: ensure any images inside the appended node have the expected class
              try{
                var imgs = node.querySelectorAll && node.querySelectorAll('img');
                if (imgs && imgs.length){
                  imgs.forEach(function(img){
                    if (!img.classList.contains('card-image')) img.classList.add('card-image');
                    // ensure sensible inline fallback so CSS has immediate min constraints
                    img.style.maxWidth = img.style.maxWidth || '100%';
                    img.style.objectFit = img.style.objectFit || 'cover';
                    // force browser to layout this node now
                    void img.offsetWidth;
                  });
                }
              }catch(_e){}

              // If blogReadmore is available, initialize the new node
              try{ if (window.blogReadmore && typeof window.blogReadmore.init === 'function'){ window.blogReadmore.init(node); } }catch(_e){}

              // trigger a resize event as a final reflow hint (some browsers recalc on resize)
              try{ window.dispatchEvent(new Event('resize')); }catch(_e){}
            }
          }
          if (data.has_next){
            var nextPage = parseInt(next, 10) + 1;
            btn.setAttribute('data-next-page', nextPage);
            btn.disabled = false;
            btn.textContent = 'تحميل المزيد';
          } else {
            btn.style.display = 'none';
          }
        } catch (e){
          console.error('Failed to parse loadmore response', e);
          btn.disabled = false;
          btn.textContent = 'تحميل المزيد';
        }
      } else {
        console.error('Load more failed', xhr.status);
        btn.disabled = false;
        btn.textContent = 'تحميل المزيد';
      }
    };
    xhr.send();
  });
});
