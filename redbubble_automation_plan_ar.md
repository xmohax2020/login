# خطة تنفيذ فعلية لبناء أداة رفع تصاميم شبه أوتوماتيكية على Redbubble

> المطلوب كان: **"اعملها الخطة"**. هذه نسخة عملية جدًا: ماذا سنبني، بأي ترتيب، وبأي مخرجات يومية حتى تصل لنسخة MVP شغالة.

---

## 1) الهدف النهائي خلال 14 يوم

بناء أداة داخلية اسمها `rb-uploader-assistant` تعمل كالتالي:

1. تستقبل ملفات التصميم الخام من مجلد `input_designs/`.
2. تولّد تلقائيًا نسخ المقاسات المطلوبة في `exports/<slug>/`.
3. تولّد Metadata أولية (عنوان/وصف/وسوم) في ملف قابل للمراجعة.
4. تعرض Dashboard فيها:
   - معاينة التصميم
   - زر نسخ العنوان والوصف والوسوم
   - زر فتح صفحة الرفع يدويًا
   - تتبع الحالة (`draft -> ready -> uploaded -> published`)
5. تمنع تكرار العمل عبر `sha256` لكل تصميم.

> **النتيجة:** رفع أسرع 3x إلى 5x بدون المخاطرة ببوت كامل قد يسبب مشاكل حساب.

---

## 2) قواعد الأمان والالتزام (غير قابلة للتفاوض)

- لا نعمل bypass لـ CAPTCHA أو أي حماية.
- لا ننفّذ نشر تلقائي 100% داخل Redbubble.
- آخر خطوة (النشر) تبقى بشرية.
- كل تصميم يمر بمراجعة بشرية قبل الضغط النهائي.

---

## 3) اختيار التقنية (نسخة سريعة وقابلة للتطوير)

- **Backend/API:** Python + FastAPI
- **معالجة صور:** Pillow
- **قاعدة بيانات:** SQLite
- **واجهة بسيطة:** HTML + JS (بدون تعقيد React في البداية)
- **تشغيل:** Docker اختياري أو تشغيل محلي مباشر

هيكل المشروع:

```text
rb-uploader-assistant/
  app/
    main.py
    services/
      image_pipeline.py
      metadata_pipeline.py
      dedupe.py
    db/
      models.py
      sqlite.py
    web/
      index.html
      app.js
  input_designs/
  exports/
  data/
    designs.csv
    app.db
  configs/
    sizes.yaml
  scripts/
    prepare.py
    validate.py
    seed.py
```

---

## 4) نموذج البيانات المطلوب

### جدول `designs`
- `id` (uuid)
- `slug`
- `original_file`
- `sha256`
- `title`
- `description`
- `tags` (json text)
- `collection`
- `maturity`
- `status` (`draft|ready|uploaded|published`)
- `created_at`
- `updated_at`

### جدول `assets`
- `id`
- `design_id`
- `size_name` (مثل: sticker, tshirt, poster)
- `width`
- `height`
- `file_path`

---

## 5) خطة تنفيذ يوم-بيوم (14 يوم)

## الأسبوع 1 (بناء الأساس)

### اليوم 1
- إنشاء المشروع والهيكل.
- إعداد FastAPI + SQLite.
- endpoint صحي: `GET /health`.

**مخرج اليوم:** تطبيق يشتغل + قاعدة بيانات جاهزة.

### اليوم 2
- بناء `image_pipeline.py`:
  - قراءة PNG/SVG (حسب المتاح)
  - توليد مقاسات من `configs/sizes.yaml`
  - حفظ كل النتائج في `exports/<slug>/`

**مخرج اليوم:** سكربت `prepare` ينجح على 3 تصاميم تجريبية.

### اليوم 3
- بناء dedupe عبر `sha256`.
- إذا الملف مكرر: وسمه `duplicate` وعدم إعادة المعالجة.

**مخرج اليوم:** منع الرفع المكرر بنسبة 100% للحالات المتطابقة.

### اليوم 4
- بناء `metadata_pipeline.py`:
  - قالب عنوان
  - قالب وصف
  - توليد 15 وسم أولي
- حفظها في CSV + DB.

**مخرج اليوم:** بيانات قابلة للمراجعة لكل تصميم.

### اليوم 5
- بناء validation rules:
  - title بين 20–80 حرف
  - وصف غير فارغ
  - tags من 10 إلى 20
  - منع الوسوم المكررة

**مخرج اليوم:** تقرير Validation (`pass/fail`) لكل تصميم.

### اليوم 6
- API endpoints:
  - `GET /designs`
  - `GET /designs/{id}`
  - `POST /designs/{id}/status`
  - `POST /designs/{id}/regenerate-metadata`

**مخرج اليوم:** API كاملة لدورة حياة التصميم.

### اليوم 7
- واجهة Dashboard أولية:
  - جدول التصاميم
  - فلتر حسب الحالة
  - معاينة الصورة
  - أزرار نسخ metadata

**مخرج اليوم:** تجربة End-to-End محلية.

## الأسبوع 2 (تثبيت وتحسين)

### اليوم 8
- إضافة زر “Open Upload Page”.
- إضافة اختصار “Open export folder”.

### اليوم 9
- تحسين قوالب الوصف حسب النيتش (Minimal / Funny / Typography).

### اليوم 10
- إضافة Audit Log:
  - من غيّر الحالة؟
  - متى تم التعديل؟

### اليوم 11
- اختبارات وحدات:
  - image resize
  - dedupe
  - metadata validation

### اليوم 12
- تحسين الأداء (batch processing لعدد كبير من الملفات).

### اليوم 13
- وثائق تشغيل: `README` + `.env.example`.

### اليوم 14
- UAT (اختبار استخدام فعلي 20 تصميم) + إصلاحات أخيرة + تجميد MVP.

---

## 6) أوامر CLI المطلوبة (واضحة وسهلة)

- `prepare --input input_designs --output exports`
- `metadata generate --source exports --out data/designs.csv`
- `validate --metadata data/designs.csv`
- `sync-db --metadata data/designs.csv`
- `serve --port 8080`

---

## 7) تعريف Done (متى نقول خلصت؟)

نعتبر MVP مكتمل إذا تحقق التالي:

- معالجة 50 تصميم بدون أخطاء توقف.
- نسبة نجاح validation فوق 90% بعد المراجعة.
- تقليل وقت تجهيز التصميم الواحد إلى أقل من 3 دقائق.
- وجود Dashboard شغالة لتغيير الحالة والنسخ السريع.

---

## 8) مخاطر متوقعة + حلول مباشرة

- **اختلاف مقاسات المنتجات** → ملف `sizes.yaml` قابل للتحديث بدون تعديل كود.
- **وسوم ضعيفة الجودة** → إضافة قاموس niche + مراجعة بشرية.
- **مشاكل جودة الصورة** → فحص DPI/الأبعاد قبل التصدير.
- **خطر مخالفة السياسات** → إبقاء النشر النهائي يدوي.

---

## 9) أول Sprint Backlog جاهز (تبدأ به الآن)

1. إعداد مشروع FastAPI + SQLite.
2. بناء `prepare.py` لمعالجة الصور.
3. بناء `dedupe.py` بالـ SHA256.
4. بناء metadata generator + validator.
5. إنشاء Dashboard بسيط (قائمة + نسخ + تغيير حالة).

---

## 10) ما أحتاجه منك لتشغيل الخطة فورًا

- 10 تصاميم تجريبية (PNG).
- 2–3 نيتشات أساسية (مثال: cats, gaming, arabic quotes).
- أسلوب الكتابة المطلوب في الوصف (formal / fun / short).

بعد ما ترسلها، نقدر ننتقل مباشرة لخطوة التنفيذ الفعلي (Skeleton + CLI + Dashboard) بدون تأخير.
