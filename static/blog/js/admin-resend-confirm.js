document.addEventListener('DOMContentLoaded', function () {
  document.querySelectorAll('.resend-link').forEach(function (el) {
    el.addEventListener('click', function (e) {
      var ok = confirm('هل تود إعادة إرسال هذا الإشعار؟ هذه العملية سترسل بريدًا للمستلم.');
      if (!ok) {
        e.preventDefault();
      }
    });
  });
});
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
  if (modalEl && typeof bootstrap !== 'undefined' && bootstrap.Modal) {
    try {
      bsModal = new bootstrap.Modal(modalEl);
    } catch (e) {
      bsModal = null;
    }
  }

  document.querySelectorAll('.resend-link').forEach(function (el) {
    el.addEventListener('click', function (e) {
      // We expect data-resend-url and data-comment attributes
      var url = el.getAttribute('data-resend-url');
      var comment = el.getAttribute('data-comment') || '';

      if (bsModal && modalEl) {
        e.preventDefault();
        // set excerpt and confirm button
        var excerptNode = document.getElementById('adminResendCommentExcerpt');
        var confirmBtn = document.getElementById('adminResendConfirmBtn');
        if (excerptNode) excerptNode.textContent = comment;
        if (confirmBtn) confirmBtn.setAttribute('href', url);
        bsModal.show();
      } else {
        // fallback
        var ok = confirm('هل تود إعادة إرسال هذا الإشعار؟\n\n' + (comment ? comment : ''));
        if (!ok) {
          e.preventDefault();
        }
      }
    });
  });
});
