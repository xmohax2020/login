# الدليل الكامل (من الصفر إلى التشغيل)

هذا الملف مكتوب ليشرح لك التطبيق كأنك تشغله أول مرة.

## 1) فهم الفكرة بسرعة

### الأداة تعمل على 3 مراحل:
1. **Prepare**: تجهيز ملفات التصميم (مقاسات متعددة).
2. **Metadata**: توليد بيانات أولية (عنوان/وصف/وسوم).
3. **Assist**: مراجعة/تعديل/تتبع حالة قبل الرفع اليدوي.

### الأداة لا تقوم بـ:
- توليد صور جديدة من الصفر.
- نشر تلقائي على Redbubble.

---

## 2) الشرح العملي (واحد واحد)

### 2.1 تثبيت
```bash
git clone <YOUR_REPO_URL>
cd rb-uploader-assistant
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2.2 تجهيز البيئة
```bash
python scripts/sync_db.py
mkdir -p input_designs exports data
```

### 2.3 ضع ملفاتك
ضع الصور داخل `input_designs/`.

### 2.4 شغل التحضير
```bash
python scripts/prepare.py --niche general --skip-duplicates
```

### 2.5 تحقق من النتائج
```bash
python scripts/validate.py --metadata data/designs.csv
```

### 2.6 افتح الواجهة
```bash
uvicorn app.main:app --reload --port 8080
```
وافتح: `http://127.0.0.1:8080/`

---

## 3) كيف تستخدمه يومياً؟
1. أضف تصاميم جديدة.
2. شغل `prepare.py`.
3. شغل `validate.py`.
4. راجع من Dashboard.
5. غيّر الحالة إلى `ready`.
6. ارفع يدوياً على Redbubble.
7. بعد الرفع غيّر الحالة `uploaded` ثم `published`.

---

## 4) فهم الملفات الناتجة
- `exports/<slug>/...png`: المقاسات النهائية.
- `data/designs.csv`: البيانات الوصفية.
- `data/app.db`: قاعدة البيانات.

---

## 5) شرح بسيط للـ API
- `/health`: يتأكد أن السيرفر شغال.
- `/designs`: يعرض كل التصاميم.
- `/designs?status=ready`: فلترة حسب الحالة.
- `/designs/{id}/status`: تغيير الحالة.
- `/designs/{id}/metadata`: تعديل metadata.
- `/audit-logs`: سجل العمليات.

---

## 6) هل تنشر الأداة تلقائياً؟
**لا**.
- الأداة تجهز فقط.
- أنت ترفع على Redbubble بنفسك.

---

## 7) أفضل طريقة للعمل مع فريق
- المصمم: يضع الملفات.
- المشغل: يشغل prepare/validate.
- المراجع: يراجع metadata في Dashboard.
- الناشر: يرفع يدوياً ويحدث الحالة.

---

## 8) Troubleshooting سريع

### validate فشل
- غالباً title قصير/طويل أو tags قليلة.
- عدل metadata ثم أعد validate.

### ما فيه بيانات في Dashboard
- تأكد أنك شغلت `prepare.py`.

### مشكلة مكتبات ناقصة
- أعد تفعيل `.venv` ثم `pip install -r requirements.txt`.

---

## 9) ماذا أطور لاحقاً؟
- تحسين قوالب metadata حسب niche.
- دعم SVG متقدم.
- إضافة auth للمستخدمين.
- بناء صفحة تقارير KPI.
