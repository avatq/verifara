# Verifara / AuthentiCheck — دليل التشغيل

## وش موجود الآن (المرحلة 1)

**Backend (FastAPI)** — شغّال ومُختبر فعليًا:
- `POST /api/v1/analyze/image` → SHA-256 + EXIF metadata + Technical Forensics حقيقي (ELA + تحليل نمط الضوضاء)
- `POST /api/v1/analyze/document` → SHA-256 + PDF metadata/بنية + إشارات أسلوبية للكتابة (stylometry)
- `GET /health`

**Frontend (Next.js)** — صفحة رفع ملف تتصل مباشرة بالـ backend وتعرض Evidence Report.

## ما هو ناقص لسه (بالترتيب المقترح)

1. C2PA / Content Credentials verification حقيقي
2. تقرير PDF قابل للتحميل (بند 17 بمواصفاتك)
3. رابط تقرير عام قابل للمشاركة (بند 18)
4. Source/reverse-image investigation (يحتاج API خارجي مدفوع)
5. Video + Audio pipelines (المرحلة 2 و3 حسب خطتك)
6. قاعدة بيانات فعلية (حاليًا لا يوجد تخزين — كل تحليل مستقل)

---

## تشغيل Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate          # على Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

تأكد إنه شغّال: افتح `http://localhost:8000/health` — لازم يرجع `{"status":"ok",...}`

## تشغيل Frontend

```bash
cd frontend
npm install
```

**قبل التشغيل** — رجّع خطوط Google الحقيقية (كانت معطّلة عندي بسبب قيود شبكة بيئة البرمجة فقط):

افتح `src/app/layout.tsx` واستبدل السطرين:
```ts
const bodyFont = { variable: "--font-body" };
const displayFont = { variable: "--font-display" };
```
بـ:
```ts
import { Inter, Sora } from "next/font/google";
const bodyFont = Inter({ subsets: ["latin"], variable: "--font-body" });
const displayFont = Sora({ subsets: ["latin"], weight: ["600", "700", "800"], variable: "--font-display" });
```
(احذف استيراد `next/font/google` المعلّق أعلى نفس الملف واستبدله بالسطر الفعلي)

ثم:
```bash
echo "NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1" > .env.local
npm run dev
```

افتح `http://localhost:3000` — ارفع صورة JPG/PNG أو ملف PDF وشوف التقرير الحقيقي.

---

## جرّب الفرق بنفسك

- ارفع صورة عادية من موبايلك (فيها EXIF كاملة) → لاحظ الفرق عن صورة مسحوبة من الإنترنت (بدون EXIF غالبًا)
- جرّب صورة عدّلتها بفوتوشوب (لصق/دمج) → لاحظ عنصر "التحليل الفني" هل يلتقط شي
- ارفع PDF فيه فقرة طويلة من نص AI (مثلاً من ChatGPT) وقارنها بمستند كتبته بنفسك → لاحظ قيمة burstiness

## ملاحظة مهمة

العتبات المستخدمة بالتحليل الفني (forensics) والأسلوبي (stylometry) **مبدئية**،
معايَرة على أمثلة اختبار بسيطة صنعتها أنا، مو على بيانات حقيقية متنوعة واسعة.
لو لاحظت نتائج غريبة على ملفات حقيقية، هذا متوقع في هذه المرحلة — خبّرني بالأمثلة
وأقدر أعاير العتبات بناءً عليها.
