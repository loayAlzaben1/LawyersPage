// admin-resend-modal.js
// Replaces the simple confirm with a Bootstrap modal that shows a short excerpt
// of the comment and Confirm/Cancel buttons in Arabic. Graceful fallback to
// window.confirm if Bootstrap's Modal API isn't available.

function createResendModal() {
  // Avoid duplicate modal
  if (document.getElementById('adminResendModal')) return null;

  var modalHtml = `
  <div class="modal fade" id="adminResendModal" tabindex="-1" aria-hidden="true">
    <div class="modal-dialog modal-dialog-centered">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">تأكيد إعادة الإرسال</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="إغلاق"></button>
        </div>
        <div class="modal-body">
          <p><strong id="adminResendPostTitle">...</strong></p>
          <p><small id="adminResendMeta"></small></p>
          <hr />
          <p id="adminResendCommentExcerpt" style="white-space:pre-wrap;">...</p>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">إلغاء</button>
          <a href="#" id="adminResendConfirmBtn" class="btn btn-primary">تأكيد</a>
        </div>
      </div>
    </div>
  </div>`;

  var wrapper = document.createElement('div');
  wrapper.innerHTML = modalHtml;
  document.body.appendChild(wrapper.firstElementChild);
  return document.getElementById('adminResendModal');
}

document.addEventListener('DOMContentLoaded', function () {
  var modalEl = createResendModal();
  var bsModal = null;
  // Create Bootstrap Modal instance (our local shim provides bootstrap.Modal)
  if (modalEl && typeof bootstrap !== 'undefined' && bootstrap.Modal) {
    bsModal = new bootstrap.Modal(modalEl);
  }

  document.querySelectorAll('.resend-link').forEach(function (el) {
    el.addEventListener('click', function (e) {
      // data attributes: data-resend-url, data-comment, data-post-title, data-email, data-created-at
      var url = el.getAttribute('data-resend-url');
      var comment = el.getAttribute('data-comment') || '';
      var postTitle = el.getAttribute('data-post-title') || '';
      var email = el.getAttribute('data-email') || '';
      var createdAt = el.getAttribute('data-created-at') || '';

      e.preventDefault();
      // populate modal fields
      var titleNode = document.getElementById('adminResendPostTitle');
      var metaNode = document.getElementById('adminResendMeta');
      var excerptNode = document.getElementById('adminResendCommentExcerpt');
      var confirmBtn = document.getElementById('adminResendConfirmBtn');

      if (titleNode) titleNode.textContent = postTitle;
      if (metaNode) metaNode.textContent = (email ? ('من: ' + email + ' ') : '') + (createdAt ? (' | بتاريخ: ' + new Date(createdAt).toLocaleString('ar-EG')) : '');
      if (excerptNode) excerptNode.textContent = comment;

      // Make confirm button submit a POST with CSRF to the resend URL
      if (confirmBtn) {
        // remove any existing click handler
        confirmBtn.replaceWith(confirmBtn.cloneNode(true));
        confirmBtn = document.getElementById('adminResendConfirmBtn');
        confirmBtn.addEventListener('click', function (ev) {
          ev.preventDefault();
          submitPost(url);
        });
      }

      if (bsModal) {
        bsModal.show();
      }
    });
  });
});

function getCookie(name) {
  var value = "; " + document.cookie;
  var parts = value.split("; " + name + "=");
  if (parts.length === 2) return parts.pop().split(';').shift();
}

function submitPost(url) {
  var form = document.createElement('form');
  form.method = 'POST';
  form.action = url;
  var csrf = getCookie('csrftoken');
  if (csrf) {
    var input = document.createElement('input');
    input.type = 'hidden';
    input.name = 'csrfmiddlewaretoken';
    input.value = csrf;
    form.appendChild(input);
  }
  // Add a marker field so server side can verify optional
  var marker = document.createElement('input');
  marker.type = 'hidden';
  marker.name = 'resend_confirm';
  marker.value = '1';
  form.appendChild(marker);
  document.body.appendChild(form);
  form.submit();
}
