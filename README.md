# موقع محامية - ملخص المشروع

[![CI](https://github.com/<OWNER>/<REPO>/actions/workflows/ci.yml/badge.svg)](https://github.com/<OWNER>/<REPO>/actions/workflows/ci.yml)
[![Codecov](https://codecov.io/gh/<OWNER>/<REPO>/branch/main/graph/badge.svg?token=YOUR_TOKEN_HERE)](https://codecov.io/gh/<OWNER>/<REPO>)

## 🎯 الهدف

إنشاء موقع إلكتروني باللغة العربية (مع إمكانية إضافة الإنجليزية لاحقًا) لمكتب محامية أردنية. الموقع بسيط، ودود، سهل الاستخدام، ومتجاوب مع الهواتف. يتيح للعملاء:

- معرفة الخدمات القانونية المقدمة
- حجز موعد وإرسال وصف للمشكلة مع مرفقات (PDF/صور)
- التواصل المباشر عبر الهاتف أو واتساب
- قراءة مقالات ونصائح قانونية
- الاطلاع على الأسئلة الشائعة (FAQ)

---

## 🗂️ خريطة الموقع (Sitemap) وURLs مقترحة

- /                    → الصفحة الرئيسية
- /about/              → من أنا (نبذة قصيرة عن المحامية)
- /services/           → صفحة الخدمات (قائمة مختصرة لكل خدمة)
- /appointment/        → حجز موعد (نموذج + رفع مستندات)
- /blog/               → مقالات ونصائح (قائمة)
- /blog/<slug>/        → صفحة المقال الكامل
- /faq/                → أسئلة شائعة
- /contact/            → تواصل معنا (هاتف، واتساب، نموذج)
- /admin/              → لوحة إدارة Django

---

## 🔑 الميزات الأساسية المطلوبة

- دعم كامل للعربية (RTL) مع إمكانية إضافة الإنجليزية لاحقًا
- تصميم بسيط وودود، ألوان هادئة (مقترح: أزرق هادئ أو أخضر فاتح، خلفية بيضاء)
- واجهة متجاوبة 100% (Mobile First)
- نموذج حجز موعد مع إمكانية رفع ملفات (PDF/صور)، وحفظ بيانات كل طلب
- زر/رابط دردشة واتساب مباشر
- روابط وسائل التواصل الاجتماعي (عند التوفر)
- لوحة تحكم لإدارة المقالات والخدمات والرسائل
- قابلية التوسّع: إضافة لغات، خدمات إضافية، خرائط، مراجعات عملاء

---

## 🎨 اقتراح تصميم سريع

- الألوان: أزرق هادئ (#2C7BE5) أو أخضر فاتح (#2BB673)، درجات رمادية للنصوص.
- الخط العربي المقترح: Tajawal أو Cairo (قابل للتضمين عبر Google Fonts).
- أيقونات: رموز بسيطة (⚖️ — 📑 — 📞).
- التركيز على زر واضح لحجز الموعد في الواجهة الرئيسية.
- تنسيق RTL للعربية: يجب تحميل CSS/الاتجاه المناسب عند اختيار اللغة العربية.

---

## 🧭 نماذج/حقول رئيسية

### حجز موعد (Appointment)
- الاسم
- رقم الهاتف
- البريد الإلكتروني (اختياري)
- الخدمة/التخصص (قائمة اختيارات)
- وصف المشكلة (نص)
- رفع مرفقات (PDF، صور) — حد أقصى مقترح: 10MB
- تاريخ/الوقت المفضّل (اختياري)
- موافقة على سياسة الخصوصية

### تواصل سريع (Contact)
- الاسم
- الهاتف أو البريد
- الموضوع
- الرسالة

---

## ⚙️ مقترحات تقنية (Stack & Libraries)

- Backend: Django (مناسب لإدارة المحتوى، لوحة Admin قوية)
- الترجمة/المحتوى متعدد اللغات: django-parler أو django-modeltranslation (أقترح **django-parler** لإدارة الحقول المترجمة بسهولة مع لوحة إدارة مرتّبة).
- Frontend CSS: Bootstrap RTL (سهل وسريع) أو Tailwind + RTL plugin (مرن لكن إعداد أكثر). سأستخدم Bootstrap RTL كبداية لتسريع التطوير.
- Forms: Django forms + django-crispy-forms (اختياري لتحسين صيغ HTML)
- Handling uploads: use Django's default File storage for now (local MEDIA_ROOT); لاحقًا S3 أو خدمة سحابية.
- Images: Pillow
- Emails: SMTP عبر ملف إعدادات (ENV variables) — يمكن اختبار محلياً عبر console backend
- Optional: reCAPTCHA أو Honeypot لحماية نماذج من السبام

---

## 🗂️ نماذج بيانات مقترحة (Django models) — موجز

- LawyerProfile: full_name, title, bio (translatable), photo, phone, email, office_address, working_hours, social_links
- Service: title (translatable), slug, description (translatable), order
- Appointment: name, email, phone, service(FK), preferred_datetime, message, attachment(FileField), status
- ContactMessage: name, email, phone, subject, message, created_at
- BlogPost: title(slug, translatable), content(translatable), published_at, author, featured_image
- Testimonial: client_name, content, approved

---

## ✅ أولويات التنفيذ (مراحل سريعة)

1. إنشاء README (تم)
2. Scaffold مشروع Django مع إعداد i18n وRTL
3. تنفيذ النماذج الأساسية وAdmin
4. بناء واجهة بسيطة (قوالب Django) متجاوبة + Bootstrap RTL
5. نماذج تواصل وحجز مع رفع ملفات وإشعارات بريدية
6. اختبار ونشر على استضافة مجانية (مثلاً: Render أو Vercel for static + backend elsewhere) أو استخدام Heroku-like أو VPS

---

## 📦 ما سأبدأ به بعد README

- إنشاء Scaffold لمشروع Django: مشروع باسم `lawyer_site` مع تطبيق رئيسي `core` وتطبيق `blog`، ملف `requirements.txt`, `Dockerfile` بسيط، و `README.md` (هذا الملف موجود الآن).

هل تفضّلين أن أبدأ فوراً بعمل scaffold لمشروع Django الآن باستخدام الخيارات الافتراضية (django-parler, Bootstrap RTL) أم تفضّلين تغيير شيء في المقترحات أعلاه قبل أن أبدأ؟

---

تم إعداد هذا الملف ليكون مرجع المشروع عند البدء بالتطوير. يمكنك تعديل أي نص أو إضافة بيانات (مثل: اسم المحامية، صورة، نصوص قانونية، رقم هاتف فعلي) وسأضمّنها مباشرة في القوالب عند إنشائي scaffold.

---

## تشغيل بنية Docker (اختبار/نشر سريع)

ملف `docker-compose.yml` جاهز لتشغيل ثلاثة خدمات: `web` (Django + Gunicorn)، `db` (Postgres) و`nginx` كعكسية أمامية لتقديم static وproxy للـ web.

قبل التشغيل: حدّث ملف `.env` بالقيم المناسبة (خاصة قواعد البيانات ومفتاح Django).

لتشغيل ما يلي في PowerShell من جذر المشروع:

```powershell
docker-compose up --build
```

ستكون الواجهة متاحة محليًا على http://localhost:8000 (NGINX سيستمع على المنفذ 8000 ويعيد توجيه الطلبات إلى الحاوية web).

ملاحظات أمان ونشر:
- تأكد من ضبط متغيرات البيئة الإنتاجية (DJANGO_DEBUG=0، مفاتيح سرية، كلمات مرور DB قوية).
- يفضّل استخدام خدمة لإدارة الشهادات SSL (Let's Encrypt) أو ضبط HTTPS في طبقة الـ proxy.


---

## 🛠️ تشغيل المشروع محليًا (PowerShell)

اتبع الخطوات التالية لتشغيل المشروع على جهازك المحلي (Windows PowerShell):

1. انسخ ملف البيئة وأضف القيم المناسبة:

```powershell
cp .env.example .env
```

2. أنشئ بيئة افتراضية وفعّلها:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

3. ثبّت الاعتمادات وادمج قواعد البيانات:

```powershell
pip install -r requirements.txt
python manage.py migrate
```

4. (اختياري) أنشئ حساب مدير للموقع:

```powershell
python manage.py createsuperuser
```

5. شغّل الخادم محليًا:

```powershell
python manage.py runserver
```

بعدها افتح المتصفح على http://127.0.0.1:8000/ وسترى الموقع.

ملاحظات:
- إعدادات البريد الافتراضية تستخدم الـ Console backend (يعرض رسائل البريد في الطرفية)؛ لتفعيل بريد حقيقي حدّث متغيرات البيئة في `.env` و`settings.py`.
- ملفات الرفع تحفظ محليًا داخل مجلد `media/` أثناء التطوير. للحماية والنسخ الاحتياطي استخدم تخزين سحابي (S3) عند النشر.

### حماية النماذج ورفع الملفات

- الأن يتضمن المشروع تحققًا بسيطًا لملفات المرفقات: الحد الأقصى 10MB وأنواع مسموح بها PDF وJPG وPNG.
- تم إضافة "honeypot" في نموذج التواصل لاكتشاف البوتات. إذا كنت تفضل استخدام Google reCAPTCHA، قم بإضافة `RECAPTCHA_SITE_KEY` و`RECAPTCHA_SECRET_KEY` إلى ملف `.env` ثم ربط الحقول في القوالب و`forms.py` باستخدام مكتبة مثل `django-recaptcha`.

### إعدادات أمان Django للإنتاج

ملف `settings.py` يحتوي على إعدادات أمان يمكن تمكينها في بيئة الإنتاج عن طريق متغيرات البيئة التالية:

- `USE_X_FORWARDED_PROTO=1` — إذا كانت هناك proxy تقدم X-Forwarded-Proto (مثل Nginx/Load Balancer).
- `SECURE_HSTS_SECONDS` — مدة HSTS بالثواني (افتراضي 31536000).
- `SECURE_HSTS_INCLUDE_SUBDOMAINS` — تضمين النطاقات الفرعية في HSTS.
- `SECURE_HSTS_PRELOAD` — تمكين preload.
- `SECURE_SSL_REDIRECT` — إعادة توجيه جميع الطلبات إلى HTTPS.
- `SESSION_COOKIE_SECURE` و `CSRF_COOKIE_SECURE` — تأمين الكوكيز فقط عبر HTTPS.
- `X_FRAME_OPTIONS` — قيمة رأس X-Frame-Options (افتراضي DENY).


لتفعيل هذه الإعدادات على الخادم الإنتاجي، تأكد من ضبط `DJANGO_DEBUG=0` وتهيئة المتغيرات أعلاه في `.env` أو في إعدادات البيئة على مزود الاستضافة.


---

## ⏱️ Celery (مهام معالجة الخلفية)

هذا المشروع يحتوي على تطبيق Celery في `lawyer_site/celery.py`. يمكن لـ Celery اكتشاف المهام تلقائيًا من ملفات `tasks.py` في التطبيقات.

إعدادات البيئات (أضف إلى `.env` أو متغيرات بيئة الخادم):

- `CELERY_BROKER_URL` — مثال: `redis://localhost:6379/0`
- `CELERY_RESULT_BACKEND` — مثال: `redis://localhost:6379/1` (اختياري)

مثال:

```
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1
```

تشغيل عامل (worker) محليًا (PowerShell):

```powershell
# فعّل البيئة الافتراضية أولاً
#.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
celery -A lawyer_site worker --loglevel=info
```

تشغيل عامل مع تزامن 4:

```powershell
celery -A lawyer_site worker --loglevel=info --concurrency=4
```

مراقبة المهام باستخدام Flower (اختياري):

```powershell
pip install flower
celery -A lawyer_site flower --port=5555
# افتح http://localhost:5555
```

الملاحظات:
- على بيئة الإنتاج، استخدم خدمة رسائل مُدارة (مثل Redis سلحساب خارجي) وشغّل العمال في عملية منفصلة (systemd، Docker، إلخ).
- تأكد من تثبيت `pywebpush` في بيئة العمال إذا أردت دعم إرسال إشعارات الويب من المهام.
- المهام التي أنشأتها للتو: `core.tasks.send_pushes_for_post` تُستخدم لإرسال الإشعارات عند نشر مقال جديد.

### تشغيل Redis + Celery + Flower باستخدام Docker Compose

If you have Docker available you can start Redis, a Celery worker and Flower using the supplied compose file:

```powershell
docker-compose -f docker-compose.yml -f docker-compose.celery.yml up --build
```

This will expose:
- Redis on localhost:6379
- Flower on localhost:5555

Stop the services with Ctrl+C or run:

```powershell
docker-compose -f docker-compose.yml -f docker-compose.celery.yml down
```

