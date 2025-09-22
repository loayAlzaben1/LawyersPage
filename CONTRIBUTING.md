## الإسهام والمراجعات — إرشادات سريعة

نشكرك على رغبتك في الإسهام. هذه التعليمات تساعدك على تجهيز بيئتك المحلية وإجبار قواعد الجودة (pre-commit) على التشغيل محليًا قبل رفع PR.

الخطوات الأساسية (مفضّل تشغيلها محليًا قبل إنشاء PR):

1. تثبيت التبعيات في الـ virtualenv:

```powershell
# داخل بيئة افتراضية
pip install -r requirements.txt
```

2. تثبيت pre-commit وتفعيل الـ hooks لمستنسخة المستودع:

```bash
# تثبيت pre-commit إن لم يكن مثبتًا
pip install --user pre-commit

# في جذر المشروع
pre-commit install

# لتشغيل جميع الفحوص مرة واحدة (سيفحص ruff و black hooks وغيره)
pre-commit run --all-files
```

ملاحظات خاصة بنظام Windows (PowerShell):

```powershell
# ثبت المتطلبات عبر pip ثم شغّل
pip install -r requirements.txt
py -m pip install --user pre-commit
py -m pre_commit install
py -m pre_commit run --all-files
```

3. استخدام الأدوات يدوياً (اختياري)

- لتشغيل ruff مباشرة:
  ```bash
  ruff check .
  ruff check --fix .
  ```
- لتنسيق الكود عبر black:
  ```bash
  black .
  ```

بدلاً من تشغيل الأوامر السابقة يدويًا يمكنك استخدام الهدف التالي من Makefile:

```bash
make fix-style
# يقوم بتشغيل ruff --fix ثم black .
```

4. نصيحة عمل سريعة

- قبل رفع PR: شغّل `pre-commit run --all-files` وستظهر لك الأخطاء أو سيقوم formatters بالإصلاحات التي يمكنك إضافتها ثم إعادة الالتزام.
- استخدم `make install-precommit` أو `make prepare-scripts` لتجهيز البيئة محليًا (المشروع يتضمّن Makefile للمساعدة).

بيئة CI
- تم إعداد GitHub Actions في `.github/workflows/ci.yml` لتثبيت التبعيات ثم تشغيل `pre-commit run --all-files` قبل تشغيل الاختبارات والتغطية. أي فشل في hooks سيمنع PR من المرور تلقائيًا.

شكراً لإسهامك — إذا رغبت، أدرج مثالاً صغيراً عن كيفية إصلاح أخطاء ruff/black تلقائيًا يمكنني إضافته هنا.
