// Small helper to show selected filename in Arabic next to file inputs
document.addEventListener('DOMContentLoaded', function () {
  var MAX_BYTES = 10 * 1024 * 1024; // 10 MB
  function humanFileSize(bytes) {
    if (bytes === 0) return '0 بايت';
    var sizes = ['بايت', 'ك.بايت', 'ميغابايت', 'غيغابايت'];
    var i = Math.floor(Math.log(bytes) / Math.log(1024));
    var value = (bytes / Math.pow(1024, i));
    return value.toFixed(value >= 10 || i === 0 ? 0 : 1) + ' ' + sizes[i];
  }

  document.querySelectorAll('input[type="file"]').forEach(function (input) {
    var info = document.createElement('div');
    info.className = 'file-info text-muted small mt-1';
    input.parentNode.insertBefore(info, input.nextSibling);

    input.addEventListener('change', function () {
      if (input.files && input.files.length > 0) {
        var parts = Array.from(input.files).map(function (f) {
          return f.name + ' (' + humanFileSize(f.size) + ')';
        });
        var names = parts.join(', ');
        var tooLarge = Array.from(input.files).some(function (f) { return f.size > MAX_BYTES; });
        info.textContent = 'الملف/الملفات المختارة: ' + names;
        if (tooLarge) {
          var warn = document.createElement('div');
          warn.className = 'text-danger small mt-1';
          warn.textContent = 'تحذير: أحد الملفات يتجاوز الحد المسموح 10 ميغابايت. الرجاء اختيار ملف أصغر.';
          // remove previous warning if any
          var prev = input.parentNode.querySelector('.file-size-warning');
          if (prev) prev.remove();
          warn.classList.add('file-size-warning');
          input.parentNode.insertBefore(warn, info.nextSibling);
        } else {
          var prevW = input.parentNode.querySelector('.file-size-warning');
          if (prevW) prevW.remove();
        }
      } else {
        info.textContent = 'لم يتم اختيار ملف';
        var prevW = input.parentNode.querySelector('.file-size-warning');
        if (prevW) prevW.remove();
      }
    });

    // initialize text
    if (!input.value) info.textContent = 'لم يتم اختيار ملف';
  });
});
