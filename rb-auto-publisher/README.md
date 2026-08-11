# rb-auto-publisher (New Project)

مشروع جديد مستقل لأتمتة نشر التصاميم (رفع تلقائي) بطريقة قابلة للتحكم.

## مهم جدًا
- الأداة لا تتجاوز CAPTCHA.
- أول تشغيل يحتاج تسجيل دخول يدوي مرة واحدة من المتصفح.
- بعد حفظ Session State يمكن تنفيذ الرفع التلقائي.
- استخدمها على مسؤوليتك مع الالتزام بسياسات Redbubble.

## الفكرة
- إدخال CSV فيه بيانات التصاميم.
- سكربت Playwright يفتح صفحة الرفع ويملأ الحقول ويرفع الملف.
- نمطين:
  - `dry-run`: اختبار بدون ضغط publish.
  - `publish`: نشر فعلي.

## التشغيل
```bash
cd rb-auto-publisher
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium
```

### 1) حفظ جلسة الدخول
```bash
python scripts/save_login_session.py --base-url https://www.redbubble.com --state-file data/state.json
```
> سيفتح المتصفح، سجل دخولك يدويًا، ثم اضغط Enter في الطرفية.

### 2) جهز CSV
أنشئ `data/designs.csv` مثل:
```csv
file_path,title,description,tags,maturity,is_public,default_status
/path/design1.png,My Design,Great design,"tag1,tag2,tag3",safe,true,draft
```

### 3) تنفيذ dry-run
```bash
python scripts/publish.py --config configs/redbubble.yaml --csv data/designs.csv --mode dry-run
```

### 4) تنفيذ نشر فعلي
```bash
python scripts/publish.py --config configs/redbubble.yaml --csv data/designs.csv --mode publish
```

## ملاحظات
- selectors تختلف حسب تغييرات واجهة Redbubble، عدل ملف `configs/redbubble.yaml` عند الحاجة.
- لو الصفحة طلبت تحقق إضافي، الأداة تتوقف ليدخله المستخدم يدويًا.
