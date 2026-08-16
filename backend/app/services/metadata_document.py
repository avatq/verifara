"""
تحليل المستندات (PDF أولاً — البنود 13/14 من المواصفات).
نستخرج: metadata حقيقية، بنية المستند، عدد الصفحات، الخطوط المضمّنة،
ونطلق أعلام (flags) على التناقضات الشائعة، بدون أي حكم قطعي على "الحقيقة".
"""
import pymupdf as fitz  # PyMuPDF (fitz is the legacy import name for the same package)
from typing import Any


def extract_pdf_metadata(file_path: str) -> dict[str, Any]:
    result: dict[str, Any] = {
        "available": False,
        "title": None,
        "author": None,
        "creator_software": None,
        "producer_software": None,
        "creation_date": None,
        "modification_date": None,
        "pdf_version": None,
        "page_count": 0,
        "embedded_fonts": [],
        "has_embedded_files": False,
        "text_char_count": 0,
    }

    try:
        doc = fitz.open(file_path)
        meta = doc.metadata or {}
        result["available"] = any(meta.values())
        result["title"] = meta.get("title") or None
        result["author"] = meta.get("author") or None
        result["creator_software"] = meta.get("creator") or None
        result["producer_software"] = meta.get("producer") or None
        result["creation_date"] = meta.get("creationDate") or None
        result["modification_date"] = meta.get("modDate") or None
        result["pdf_version"] = doc.metadata.get("format") if doc.metadata else None
        result["page_count"] = doc.page_count
        result["has_embedded_files"] = len(doc.embfile_names()) > 0

        fonts = set()
        for page in doc:
            for f in page.get_fonts():
                # f = (xref, ext, type, basefont, name, encoding, ...)
                fonts.add(f[3])
        result["embedded_fonts"] = sorted(fonts)

        text_len = 0
        for page in doc:
            text_len += len(page.get_text())
        result["text_char_count"] = text_len

        doc.close()
    except Exception as e:
        result["error"] = f"تعذّر قراءة ملف PDF: {e}"

    return result


def assess_document_flags(metadata: dict[str, Any]) -> dict[str, Any]:
    """
    فحص أعلام أولية على بنية/بيانات المستند (البند 13).
    """
    flags: list[str] = []

    if metadata.get("creation_date") and metadata.get("modification_date"):
        if metadata["creation_date"] != metadata["modification_date"]:
            flags.append("تاريخ الإنشاء يختلف عن تاريخ آخر تعديل — طبيعي، لكن يُسجَّل في الجدول الزمني")

    if not metadata.get("available"):
        flags.append("لا توجد بيانات وصفية (metadata) في الملف — قد تكون أُزيلت عمدًا أو الملف أُنشئ من أداة لا تُضيفها")

    if metadata.get("page_count", 0) == 0:
        flags.append("لم يتم استخراج أي صفحات — الملف قد يكون تالفًا أو محميًا")

    if metadata.get("text_char_count", 0) == 0 and metadata.get("page_count", 0) > 0:
        flags.append("لا يوجد نص قابل للاستخراج رغم وجود صفحات — قد يكون المستند صورًا ممسوحة ضوئيًا (Scanned) ويحتاج OCR")

    status = "no_data" if not metadata.get("available") else (
        "flagged" if flags else "consistent"
    )

    return {"status": status, "flags": flags}
