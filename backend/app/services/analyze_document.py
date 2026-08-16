from app.services.hashing import compute_sha256
from app.services.metadata_document import extract_pdf_metadata, assess_document_flags
from app.services.writing_stylometry import extract_pdf_text, compute_writing_stylometry, assess_writing_signal
from app.services.evidence_engine import EvidenceReport, EvidenceItem, EvidenceLevel


def analyze_document(file_path: str) -> EvidenceReport:
    file_hash = compute_sha256(file_path)

    metadata = extract_pdf_metadata(file_path)
    assessment = assess_document_flags(metadata)

    items: list[EvidenceItem] = []

    if assessment["status"] == "flagged":
        level = EvidenceLevel.MINOR
        summary = "توجد ملاحظات على بنية المستند تستحق المراجعة."
    elif assessment["status"] == "no_data":
        level = EvidenceLevel.LOW
        summary = "لا توجد بيانات وصفية كافية في المستند."
    else:
        level = EvidenceLevel.GOOD
        summary = "بنية المستند وبياناته الوصفية متسقة."

    items.append(EvidenceItem(
        key="document_metadata",
        label_ar="بيانات المستند وبنيته",
        level=level,
        summary_ar=summary,
        details={"metadata": metadata, "flags": assessment["flags"]},
    ))

    # AI-writing signals — إشارة إحصائية ضعيفة دائمًا بتصميم متعمّد (البند 14 + 25)
    text = extract_pdf_text(file_path)
    stylometry = compute_writing_stylometry(text)
    writing_assessment = assess_writing_signal(stylometry)

    items.append(EvidenceItem(
        key="ai_writing_signals",
        label_ar="إشارات أسلوبية في الكتابة",
        level=EvidenceLevel.LOW,  # ثابتة عمدًا — لا نمنحها GOOD ولا CONFLICT أبدًا
        summary_ar="مؤشرات إحصائية ضعيفة فقط — لا يمكن اعتبارها دليلاً على مصدر الكتابة.",
        details={"stylometry": stylometry, "flags": writing_assessment["flags"]},
    ))

    report = EvidenceReport(file_hash=file_hash, file_type="document", items=items)
    report.compute_overall()
    return report
