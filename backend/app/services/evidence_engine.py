"""
Evidence Engine — قلب المنتج.
"""
from enum import Enum
from dataclasses import dataclass, field
from typing import Any, Optional


class EvidenceLevel(str, Enum):
    GOOD = "good"
    MINOR = "minor"
    LOW = "low"
    NA = "na"
    CONFLICT = "conflict"


class Verdict(str, Enum):
    NOT_AI = "not_ai"
    AI_GENERATED = "ai_generated"
    INCONCLUSIVE = "inconclusive"


@dataclass
class EvidenceItem:
    key: str
    label_ar: str
    level: EvidenceLevel
    summary_ar: str
    details: dict[str, Any] = field(default_factory=dict)
    score_percent: Optional[float] = None


@dataclass
class EvidenceReport:
    file_hash: str
    file_type: str
    items: list[EvidenceItem]
    overall_assessment: str = ""
    evidence_confidence: int = 0
    verdict: str = Verdict.INCONCLUSIVE.value
    verdict_label_ar: str = ""
    confidence_label_ar: str = ""
    classification: str = "unknown"
    classification_label_ar: str = ""

    def compute_overall(self) -> None:
        weights = {
            EvidenceLevel.GOOD: 1.0,
            EvidenceLevel.MINOR: 0.75,
            EvidenceLevel.LOW: 0.5,
            EvidenceLevel.CONFLICT: 0.0,
            EvidenceLevel.NA: None,
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

        self._compute_verdict()
        self._compute_classification()

    def _compute_verdict(self) -> None:
        ai_item = next((i for i in self.items if i.key == "ai_analysis"), None)

        if not ai_item or ai_item.level == EvidenceLevel.NA or ai_item.score_percent is None:
            self.verdict = Verdict.INCONCLUSIVE.value
            self.verdict_label_ar = "غير حاسم — بيانات AI Analysis غير متاحة حاليًا"
            self.confidence_label_ar = "منخفضة"
            return

        ai_score = ai_item.score_percent / 100

        if ai_score >= 0.65:
            self.verdict = Verdict.AI_GENERATED.value
            self.verdict_label_ar = "AI — يبدو أن المحتوى مولَّد بالذكاء الاصطناعي"
        elif ai_score <= 0.35:
            self.verdict = Verdict.NOT_AI.value
            self.verdict_label_ar = "NOT AI — يبدو أن المحتوى حقيقي"
        else:
            self.verdict = Verdict.INCONCLUSIVE.value
            self.verdict_label_ar = "غير حاسم — الإشارات متعارضة أو ضعيفة"

        distance_from_uncertain = abs(ai_score - 0.5)
        has_conflict_elsewhere = any(
            i.level == EvidenceLevel.CONFLICT and i.key != "ai_analysis" for i in self.items
        )

        if has_conflict_elsewhere:
            self.confidence_label_ar = "متوسطة"
        elif distance_from_uncertain >= 0.4:
            self.confidence_label_ar = "عالية"
        elif distance_from_uncertain >= 0.2:
            self.confidence_label_ar = "متوسطة"
        else:
            self.confidence_label_ar = "منخفضة"

    def _compute_classification(self) -> None:
        ai_item = next((i for i in self.items if i.key == "ai_analysis"), None)
        forensics_item = next((i for i in self.items if i.key == "forensics"), None)
        metadata_item = next((i for i in self.items if i.key == "metadata" or i.key == "document_metadata"), None)
        provenance_item = next((i for i in self.items if i.key == "provenance"), None)

        ai_score = (ai_item.score_percent / 100) if (ai_item and ai_item.score_percent is not None) else None
        c2pa_ai_source = provenance_item.details.get("ai_source_type_label") if provenance_item else None
        has_camera_data = False
        if metadata_item:
            md = metadata_item.details.get("metadata", {})
            has_camera_data = bool(md.get("camera_make") or md.get("camera_model"))

        if c2pa_ai_source and "معدَّل" in c2pa_ai_source:
            self.classification = "ai_assisted"
            self.classification_label_ar = "AI-Assisted — محتوى حقيقي معدَّل بأدوات ذكاء اصطناعي"
            return

        if ai_score is not None and ai_score >= 0.65:
            self.classification = "ai_generated"
            self.classification_label_ar = "AI-Generated — مولَّد بالكامل بالذكاء الاصطناعي"
            return

        forensics_flagged = forensics_item and forensics_item.level in (EvidenceLevel.MINOR, EvidenceLevel.CONFLICT)
        if forensics_flagged and (ai_score is None or ai_score < 0.65):
            self.classification = "ai_assisted"
            self.classification_label_ar = "AI-Assisted — إشارات تعديل موضعي تستدعي مراجعة"
            return

        if ai_score is not None and ai_score <= 0.35 and has_camera_data:
            self.classification = "camera_capture"
            self.classification_label_ar = "Camera Capture — التقاط كاميرا حقيقي موثَّق"
            return

        self.classification = "unknown"
        self.classification_label_ar = "Unknown — الأدلة غير كافية للتصنيف"

    def to_dict(self) -> dict[str, Any]:
        return {
            "file_hash": self.file_hash,
            "file_type": self.file_type,
            "overall_assessment": self.overall_assessment,
            "evidence_confidence": self.evidence_confidence,
            "verdict": self.verdict,
            "verdict_label": self.verdict_label_ar,
            "confidence_label": self.confidence_label_ar,
            "classification": self.classification,
            "classification_label": self.classification_label_ar,
            "items": [
                {
                    "key": i.key,
                    "label": i.label_ar,
                    "level": i.level.value,
                    "summary": i.summary_ar,
                    "details": i.details,
                    "score_percent": i.score_percent,
                }
                for i in self.items
            ],
        }
