# rb-uploader-assistant

أداة داخلية لتسريع تجهيز ملفات التصميم قبل الرفع اليدوي على Redbubble.

## ✅ ماذا تفعل الأداة؟
- تأخذ صورك من `input_designs/`.
- تنشئ نسخ مقاسات متعددة في `exports/<slug>/`.
- تولّد metadata أولية (title/description/tags).
- تحفظ النتائج في قاعدة SQLite + ملف CSV.
- تعطيك Dashboard لمراجعة وتعديل وتغيير الحالة.

## ❌ ماذا لا تفعل الأداة؟
- لا تولّد صور جديدة من الصفر (ليست مولد صور AI).
- لا تنشر تلقائياً على Redbubble.
- لا تتجاوز CAPTCHA أو أي حماية.

> الخلاصة: الأداة **Prep + Assist** وليست Auto-Publisher.

---

## 1) المتطلبات
- Python 3.10 أو أعلى
- pip
- نظام Linux/macOS أو WSL على Windows

---

## 2) التشغيل خطوة بخطوة (نسخة GitHub)

### الخطوة 1: تنزيل المشروع
```bash
git clone <YOUR_REPO_URL>
cd rb-uploader-assistant
```

### الخطوة 2: إنشاء بيئة بايثون
```bash
python -m venv .venv
source .venv/bin/activate
```

### الخطوة 3: تثبيت المتطلبات
```bash
pip install -r requirements.txt
```

### الخطوة 4: تهيئة قاعدة البيانات
```bash
python scripts/sync_db.py
```

### الخطوة 5: ضع التصاميم داخل المجلد
ضع ملفاتك (PNG/JPG/JPEG/WEBP) داخل:
```text
input_designs/
```

### الخطوة 6: تجهيز المقاسات + metadata
```bash
python scripts/prepare.py --input input_designs --output exports --metadata data/designs.csv --niche general --skip-duplicates
```

### الخطوة 7: فحص metadata
```bash
python scripts/validate.py --metadata data/designs.csv
```

### الخطوة 8: تشغيل الواجهة
```bash
uvicorn app.main:app --reload --port 8080
```

### الخطوة 9: افتح من المتصفح
- Dashboard: `http://127.0.0.1:8080/`
- Health: `http://127.0.0.1:8080/health`

---

## 3) ماذا أفعل بعد فتح الـ Dashboard؟
1. راجع التصميم والعنوان والوسوم.
2. عدّل metadata إذا احتجت.
3. غيّر الحالة:
   - `draft` → `ready`
   - بعد الرفع اليدوي: `uploaded`
   - بعد النشر: `published`
4. من Redbubble ارفع الملفات **يدوياً**.

---

## 4) الحالات (Status)
- `draft`: مسودة/تحتاج مراجعة
- `ready`: جاهز للرفع
- `uploaded`: تم الرفع
- `published`: تم النشر
- `duplicate`: ملف مكرر (نفس SHA256)

---

## 5) API المختصرة
- `GET /health`
- `GET /designs?status=ready`
- `GET /designs/{id}`
- `POST /designs/{id}/status`
- `POST /designs/{id}/metadata`
- `POST /designs/{id}/regenerate-metadata?niche=general`
- `GET /audit-logs?limit=50`

---

## 6) Docker (اختياري)
```bash
docker compose up --build
```
ثم افتح `http://127.0.0.1:8080/`

---

## 7) مشاكل شائعة وحلولها

### المشكلة: `ModuleNotFoundError`
الحل: تأكد أنك داخل بيئة `.venv` وشغلت:
```bash
source .venv/bin/activate
pip install -r requirements.txt
```

### المشكلة: `Validation failed`
الحل: راجع `data/designs.csv` أو عدّل من Dashboard (العنوان 20-80، الوسوم 10-20، بدون تكرار).

### المشكلة: لا تظهر تصاميم في الواجهة
الحل: تأكد أنك وضعت صور في `input_designs/` ثم شغلت `prepare.py`.

---

## 8) هل الأداة مناسبة لك؟
الأداة مناسبة إذا كنت تريد:
- تسريع تجهيز ونشر الأعمال يدوياً.
- تقليل الأخطاء والتكرار.
- الاحتفاظ بسجل واضح للحالات.

غير مناسبة إذا كنت تريد:
- توليد صور AI تلقائي.
- نشر تلقائي 100% بدون تدخل بشري.
