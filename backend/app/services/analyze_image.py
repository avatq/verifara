"""
يُنفّذ Pipeline الصورة الكامل:
Hash -> Metadata/EXIF -> Forensics (محلي) -> C2PA -> AI Detection (Sightengine) -> Evidence Report
"""
from app.services.hashing import compute_sha256
from app.services.metadata_image import extract_image_metadata, assess_metadata_consistency
from app.services.forensics_image import error_level_analysis, noise_consistency_analysis, assess_forensic_signals
from app.services.c2pa_check import check_c2pa
from app.services.sightengine_client import check_ai_generated
from app.services.evidence_engine import EvidenceReport, EvidenceItem, EvidenceLevel


async def analyze_image(file_path: str) -> EvidenceReport:
    file_hash = compute_sha256(file_path)

    metadata = extract_image_metadata(file_path)
    consistency = assess_metadata_consistency(metadata)

    items: list[EvidenceItem] = []

    if consistency["status"] == "suspicious":
        level = EvidenceLevel.CONFLICT
        summary = "تم رصد إشارة تعارض في بيانات EXIF تستحق المراجعة."
    elif consistency["status"] == "no_data":
        level = EvidenceLevel.LOW
        summary = "لا توجد بيانات EXIF متاحة للتحقق منها."
    else:
        level = EvidenceLevel.GOOD
        summary = "بيانات EXIF متوفرة ومتسقة."

    items.append(EvidenceItem(
        key="metadata",
        label_ar="البيانات الوصفية (Metadata)",
        level=level,
        summary_ar=summary,
        details={"metadata": metadata, "flags": consistency["flags"]},
    ))

    ela = error_level_analysis(file_path)
    noise = noise_consistency_analysis(file_path)
    forensic_assessment = assess_forensic_signals(ela, noise)

    forensic_level_map = {
        "low": EvidenceLevel.GOOD,
        "moderate": EvidenceLevel.MINOR,
        "high": EvidenceLevel.CONFLICT,
    }
    forensic_summary_map = {
        "low": "لا توجد إشارات تلاعب موضعي واضحة في التحليل الفني.",
        "moderate": "توجد إشارة فنية واحدة تستحق مراجعة — ليست دليلاً قاطعًا.",
        "high": "توجد أكثر من إشارة فنية متقاربة تستدعي مراجعة يدوية دقيقة.",
    }

    items.append(EvidenceItem(
        key="forensics",
        label_ar="التحليل الفني (Technical Forensics)",
        level=forensic_level_map[forensic_assessment["signal_level"]],
        summary_ar=forensic_summary_map[forensic_assessment["signal_level"]],
        details={
            "error_level_analysis": ela,
            "noise_consistency": noise,
            "flags": forensic_assessment["flags"],
            "note": "يكشف تلاعبًا موضعيًا (لصق/تركيب) — مو توليد AI كامل، والذي تكشفه طبقة AI Analysis المنفصلة.",
        },
    ))

    ai_result = await check_ai_generated(file_path)

    if ai_result.get("available"):
        ai_score = ai_result["ai_generated_score"]
        if ai_score >= 0.65:
            ai_level = EvidenceLevel.CONFLICT
            ai_summary = f"احتمال توليد بالذكاء الاصطناعي مرتفع ({round(ai_score*100,1)}%)."
        elif ai_score >= 0.35:
            ai_level = EvidenceLevel.MINOR
            ai_summary = f"نتيجة غير حاسمة ({round(ai_score*100,1)}% احتمال توليد AI) — تحتاج مراجعة."
        else:
            ai_level = EvidenceLevel.GOOD
            ai_summary = f"لا توجد إشارات قوية على التوليد بالذكاء الاصطناعي ({round(ai_score*100,1)}%)."

        if ai_result.get("likely_source"):
            ai_summary += f" المصدر المرجَّح: {ai_result['likely_source']}."

        items.append(EvidenceItem(
            key="ai_analysis",
            label_ar="تحليل الذكاء الاصطناعي (AI Analysis)",
            level=ai_level,
            summary_ar=ai_summary,
            details=ai_result,
            score_percent=round(ai_score * 100, 1),
        ))
    else:
        items.append(EvidenceItem(
            key="ai_analysis",
            label_ar="تحليل الذكاء الاصطناعي (AI Analysis)",
            level=EvidenceLevel.NA,
            summary_ar="تعذّر تنفيذ الفحص عبر Sightengine في هذه اللحظة.",
            details=ai_result,
        ))

    c2pa_result = check_c2pa(file_path)

    AI_ISSUER_MARKERS = [
        "google", "gemini", "imagen", "openai", "dall-e", "dalle", "sora",
        "adobe firefly", "midjourney", "stability", "meta ai", "bing image creator",
        "leonardo.ai", "runway",
    ]

    if c2pa_result.get("manifest_found"):
        if c2pa_result.get("ai_indicated_by_source_type"):
            level = EvidenceLevel.CONFLICT
            summary = (
                f"بيانات C2PA الرسمية تُصرّح بوضوح: {c2pa_result.get('ai_source_type_label')} "
                "(حقل digitalSourceType المعياري) — إفصاح صريح من الأداة نفسها."
            )
        else:
            issuer = (c2pa_result.get("issuer") or "").lower()
            generator = (c2pa_result.get("claim_generator") or "").lower()
            combined = f"{issuer} {generator}"
            indicates_ai_by_name = any(marker in combined for marker in AI_ISSUER_MARKERS)

            if indicates_ai_by_name:
                level = EvidenceLevel.MINOR
                summary = (
                    "بيانات C2PA لا تحتوي إفصاح AI رسمي (digitalSourceType)، "
                    "لكن اسم الجهة/الأداة يطابق مولّد AI معروف — إشارة أضعف تستحق مراجعة."
                )
            else:
                level = EvidenceLevel.GOOD
                summary = "تم العثور على بيانات C2PA موقّعة رقميًا — لا إشارة AI رسمية أو باسم الأداة."

        if c2pa_result.get("issuer"):
            summary += f" الجهة المُصدرة: {c2pa_result['issuer']}."
        summary += " ملاحظة: C2PA يوثّق السجل التاريخي، وغيابه لا يثبت التلاعب."
    elif c2pa_result.get("available"):
        level = EvidenceLevel.NA
        summary = "لا توجد بيانات C2PA بالملف — شائع جدًا (المعيار غير منتشر بعد)، ليس دليل تلاعب."
    else:
        level = EvidenceLevel.NA
        summary = "تعذّر تنفيذ فحص C2PA في هذه اللحظة."

    items.append(EvidenceItem(
        key="provenance",
        label_ar="مصدر المحتوى (C2PA / Content Credentials)",
        level=level,
        summary_ar=summary,
        details=c2pa_result,
    ))

    report = EvidenceReport(file_hash=file_hash, file_type="image", items=items)
    report.compute_overall()
    return report
