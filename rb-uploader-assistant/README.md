# rb-uploader-assistant (Complete MVP Guide)

`rb-uploader-assistant` أداة **Prep + Assist** لتجهيز ملفات التصميم قبل رفعها على Redbubble:
- تجهيز المقاسات تلقائيًا.
- توليد metadata أولية.
- حفظ الحالة في قاعدة بيانات.
- لوحة مراجعة وتعديل قبل الرفع اليدوي النهائي.

> ملاحظة مهمة: الأداة لا تنفذ نشر تلقائي نهائي داخل Redbubble (التأكيد النهائي يدوي).

## 1) المتطلبات
- Python 3.10+
- pip

## 2) التشغيل السريع
```bash
cd rb-uploader-assistant
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python scripts/sync_db.py
python scripts/prepare.py --input input_designs --output exports --metadata data/designs.csv --niche general --skip-duplicates
python scripts/validate.py --metadata data/designs.csv
uvicorn app.main:app --reload --port 8080
```

افتح:
- Dashboard: `http://127.0.0.1:8080/`
- Health: `http://127.0.0.1:8080/health`

## 3) هيكل المشروع
```text
app/main.py                  # API + static web
app/db/sqlite.py             # DB schema + CRUD + audit logs
app/services/image_pipeline.py
app/services/metadata_pipeline.py
app/services/dedupe.py
app/web/index.html
app/web/app.js
scripts/prepare.py
scripts/validate.py
scripts/sync_db.py
configs/sizes.yaml
data/
exports/
input_designs/
```

## 4) دورة العمل اليومية
1. ضع التصاميم في `input_designs/`.
2. نفذ `prepare.py` لإنشاء `exports/<slug>/` و`data/designs.csv`.
3. نفذ `validate.py`.
4. افتح Dashboard وراجع/عدّل metadata.
5. حدث الحالة: `ready` ثم `uploaded` ثم `published`.

## 5) أوامر مفيدة
### تجهيز
```bash
python scripts/prepare.py --niche "arabic-quotes" --skip-duplicates
```

### التحقق
```bash
python scripts/validate.py --metadata data/designs.csv
```

### تشغيل API
```bash
uvicorn app.main:app --reload --port 8080
```

## 6) API Endpoints
- `GET /health`
- `GET /designs?status=ready`
- `GET /designs/{id}`
- `POST /designs/{id}/status`
- `POST /designs/{id}/metadata`
- `POST /designs/{id}/regenerate-metadata?niche=general`
- `GET /audit-logs?limit=50`

## 7) حالات التصميم
- `draft`
- `ready`
- `uploaded`
- `published`
- `duplicate`

## 8) التحقق والجودة
- العنوان: 20-80 حرف
- الوصف: إلزامي
- الوسوم: 10-20 وسم بدون تكرار

## 9) أسئلة شائعة
### لماذا تصميم معين status = duplicate؟
عند استخدام `--skip-duplicates` وإذا `sha256` موجود مسبقًا.

### لماذا validate يفشل؟
افتح `data/designs.csv` وصحح القيم أو عدل عبر Dashboard.

## 10) تطوير لاحق مقترح
- دعم SVG متقدم.
- تصدير قوالب منتجات أكثر.
- صلاحيات مستخدمين وسجل تدقيق أوسع.
