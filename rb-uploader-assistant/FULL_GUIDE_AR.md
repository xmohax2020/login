# دليل إرشادات كامل لاستخدام وتطوير rb-uploader-assistant

## A) الهدف من التطبيق
هذا التطبيق يبني مسار عمل فعلي لتجهيز التصاميم قبل الرفع اليدوي على Redbubble:
- توحيد المقاسات.
- تخفيض الأخطاء البشرية.
- تسريع الإنتاج اليومي.

## B) تشغيل لأول مرة
1. تثبيت المتطلبات وتشغيل DB.
2. إدخال ملفات في input_designs.
3. تشغيل prepare ثم validate.
4. فتح dashboard والعمل على الحالات.

## C) سياسة العمل الآمن
- عدم تجاوز CAPTCHA أو أنظمة حماية.
- عدم عمل Auto-publish 100%.
- مراجعة بشرية إلزامية قبل النشر النهائي.

## D) شرح المكونات
- `scripts/prepare.py`: يحوّل الصور ويولّد metadata.
- `scripts/validate.py`: فحص شروط الجودة.
- `app/main.py`: واجهات API ولوحة الويب.
- `app/db/sqlite.py`: قاعدة البيانات + audit logs.

## E) أفضل إعداد تشغيل يومي
```bash
python scripts/prepare.py --niche general --skip-duplicates
python scripts/validate.py --metadata data/designs.csv
uvicorn app.main:app --port 8080
```

## F) خطوات فريق التصميم
1. المصمم يضع ملفاته.
2. مسؤول التشغيل يشغل prepare/validate.
3. مسؤول الجودة يراجع dashboard.
4. مسؤول النشر يرفع يدويًا ويحدّث status.

## G) Checklists
### قبل الرفع
- [ ] العنوان واضح.
- [ ] الوسوم غير مكررة.
- [ ] المقاسات موجودة في exports.
- [ ] الحالة = ready.

### بعد الرفع
- [ ] تغيير الحالة إلى uploaded/published.
- [ ] حفظ أي ملاحظات في سجل داخلي الفريق.

## H) استكشاف الأخطاء
- خطأ import app: شغل السكربتات من داخل جذر المشروع.
- فشل validate: صحح title/tags/description.
- لا تظهر بيانات في UI: تأكد أن prepare اشتغل بنجاح.

## I) خطة التوسعة
- إضافة auth بسيط.
- إضافة export JSON بجانب CSV.
- إضافة batch controls في UI.
- إضافة unit/integration tests أكثر.
