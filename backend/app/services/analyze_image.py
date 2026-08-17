"""
يُنفّذ Pipeline الصورة للمرحلة 1:
Hash -> Metadata/EXIF -> Consistency check -> Evidence Report
(طبقات C2PA / AI-signals / Source Evidence تُضاف لاحقًا كخدمات منفصلة
 وتُدمج هنا فقط عبر إضافة EvidenceItem جديد — الهيكل مصمم للتوسّع)
"""
from app.services.hashing import compute_sha256
from app.services.metadata_image import extract_image_metadata, assess_metadata_consistency
from app.services.forensics_image import error_level_analysis, noise_consistency_analysis, assess_forensic_signals
from app.services.evidence_engine import EvidenceReport, EvidenceItem, EvidenceLevel


def analyze_image(file_path: str) -> EvidenceReport:
    file_hash = compute_sha256(file_path)

    metadata = extract_image_metadata(file_path)
    consistency = assess_metadata_consistency(metadata)

    items: list[EvidenceItem] = []

    # عنصر: Metadata
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

    # عنصر: Technical Forensics (ELA + Noise consistency) — تحليل حقيقي على بكسلات الصورة
    ela = error_level_analysis(file_path)
    noise = noise_consistency_analysis(file_path)
    forensic_assessment = assess_forensic_signals(ela, noise)

    forensic_level_map = {
        "low": EvidenceLevel.GOOD,
        "moderate": EvidenceLevel.MINOR,
        "high": EvidenceLevel.CONFLICT,
    }
    forensic_summary_map = {
        "low": "لا توجد إشارات تلاعب واضحة في التحليل الفني الأولي (ELA + نمط الضوضاء).",
        "moderate": "توجد إشارة فنية واحدة تستحق مراجعة — ليست دليلاً قاطعًا على التعديل.",
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
            "note": "يعتمد الآن على التجمّع المكاني للبقع المشبوهة (لا نسبة عامة) لتقليل false positives على صور تحتوي أكثر من نسيج طبيعي. ما زال heuristic يحتاج معايرة.",
        },
    ))

    # عنصر: Provenance (C2PA) — سيُستبدل بفحص حقيقي في خطوة لاحقة، الآن NA/placeholder صريح
    items.append(EvidenceItem(
        key="provenance",
        label_ar="مصدر المحتوى (C2PA / Content Credentials)",
        level=EvidenceLevel.NA,
        summary_ar="فحص C2PA لم يُفعَّل بعد في هذه المرحلة من التطوير.",
        details={"status": "not_implemented_yet"},
    ))

    report = EvidenceReport(file_hash=file_hash, file_type="image", items=items)
    report.compute_overall()
    return report
