"""
Evidence Engine — قلب المنتج (البند 16 من المواصفات).
يجمّع نتائج كل الطبقات (hash / metadata / forensics / ai-signals / provenance)
في تقييم واحد بدون اختزاله في رقم مضلِّل مثل "82% Real".

كل عنصر يُصنَّف إلى واحدة من:
  GOOD      🟢  دليل قوي / متسق
  MINOR     🟡  ملاحظة بسيطة لا تُغيّر التقييم العام
  LOW       🔵  إشارة ضعيفة أو غياب بيانات كافية
  NA        ⚪  غير قابل للتطبيق على هذا نوع الملف
  CONFLICT  🔴  تناقض واضح يستحق مراجعة يدوية
"""
from enum import Enum
from dataclasses import dataclass, field
from typing import Any


class EvidenceLevel(str, Enum):
    GOOD = "good"
    MINOR = "minor"
    LOW = "low"
    NA = "na"
    CONFLICT = "conflict"


@dataclass
class EvidenceItem:
    key: str            # مثال: "metadata", "provenance"
    label_ar: str        # عنوان يُعرض للمستخدم
    level: EvidenceLevel
    summary_ar: str
    details: dict[str, Any] = field(default_factory=dict)


@dataclass
class EvidenceReport:
    file_hash: str
    file_type: str  # "image" | "document" | "video" | "audio"
    items: list[EvidenceItem]
    overall_assessment: str = ""
    evidence_confidence: int = 0  # 0-100

    def compute_overall(self) -> None:
        """
        يحسب تقييمًا عامًا مبسطًا من نتائج العناصر.
        هذا حساب توضيحي (heuristic) للمرحلة 1 — قابل للتوسعة لاحقًا
        بأوزان مختلفة لكل نوع ملف ولكل طبقة أدلة.
        """
        weights = {
            EvidenceLevel.GOOD: 1.0,
            EvidenceLevel.MINOR: 0.75,
            EvidenceLevel.LOW: 0.5,
            EvidenceLevel.CONFLICT: 0.0,
            EvidenceLevel.NA: None,  # لا يُحتسب في المعدل
        }

        scored = [weights[i.level] for i in self.items if weights[i.level] is not None]
        if scored:
            self.evidence_confidence = round((sum(scored) / len(scored)) * 100)
        else:
            self.evidence_confidence = 0

        has_conflict = any(i.level == EvidenceLevel.CONFLICT for i in self.items)

        if has_conflict:
            self.overall_assessment = "يحتاج مراجعة — تم رصد تناقضات"
        elif self.evidence_confidence >= 75:
            self.overall_assessment = "Likely Authentic — يرجَّح أنه أصلي"
        elif self.evidence_confidence >= 45:
            self.overall_assessment = "Inconclusive — غير حاسم، يحتاج أدلة إضافية"
        else:
            self.overall_assessment = "Low Confidence — إشارات ضعيفة، لا يمكن ترجيح الأصالة"

    def to_dict(self) -> dict[str, Any]:
        return {
            "file_hash": self.file_hash,
            "file_type": self.file_type,
            "overall_assessment": self.overall_assessment,
            "evidence_confidence": self.evidence_confidence,
            "items": [
                {
                    "key": i.key,
                    "label": i.label_ar,
                    "level": i.level.value,
                    "summary": i.summary_ar,
                    "details": i.details,
                }
                for i in self.items
            ],
        }
