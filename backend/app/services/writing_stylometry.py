"""
البند 14: AI-writing signals كإشارة إضافية فقط.

هام جدًا (البند 25 من مواصفاتك): لا نبني "AI text detector" حقيقي هنا —
هذا يحتاج نماذج مدرّبة ومصادر بيانات واسعة خارج نطاق هذه المرحلة.
بدلاً من ذلك نحسب مقاييس إحصائية معروفة في تحليل النصوص (stylometry) مثل:

- Burstiness (التذبذب في طول الجُمل): الكتابة البشرية عادة تتفاوت طولها
  بشكل غير منتظم أكثر من النصوص المولّدة، التي تميل لإيقاع أكثر انتظامًا
  (هذا معروف في أدبيات "perplexity/burstiness" لكشف نصوص LLM، لكنه ليس قاطعًا
  ويفشل بسهولة مع نصوص بشرية منظمة أو نصوص AI معدَّلة يدويًا).
- تكرار المفردات (Vocabulary repetition / type-token ratio).

هذه أرقام وصفية فقط — نعرضها بصراحة كـ "إشارة ضعيفة" دائمًا، ولا نصنّفها أبدًا
كـ GOOD/CONFLICT لأنها ببساطة غير موثوقة كفاية لذلك (سبق أن حذّرت من هذا في مستندك).
"""
import re
import statistics
from typing import Any


def extract_pdf_text(file_path: str, max_chars: int = 50_000) -> str:
    import pymupdf as fitz
    try:
        doc = fitz.open(file_path)
        text_parts = []
        total = 0
        for page in doc:
            t = page.get_text()
            text_parts.append(t)
            total += len(t)
            if total >= max_chars:
                break
        doc.close()
        return "".join(text_parts)[:max_chars]
    except Exception:
        return ""


def compute_writing_stylometry(text: str) -> dict[str, Any]:
    result: dict[str, Any] = {"available": False}

    sentences = [s.strip() for s in re.split(r"(?<=[.!?؟])\s+", text) if s.strip()]
    if len(sentences) < 5:
        result["reason"] = "النص قصير جدًا (أقل من 5 جُمل) لحساب مقاييس إحصائية موثوقة"
        return result

    sentence_lengths = [len(s.split()) for s in sentences]
    mean_len = statistics.mean(sentence_lengths)
    stdev_len = statistics.stdev(sentence_lengths) if len(sentence_lengths) > 1 else 0.0
    burstiness = round(stdev_len / mean_len, 4) if mean_len > 0 else 0.0

    words = re.findall(r"\b\w+\b", text.lower())
    unique_words = set(words)
    type_token_ratio = round(len(unique_words) / len(words), 4) if words else 0.0

    result.update({
        "available": True,
        "sentence_count": len(sentences),
        "mean_sentence_length_words": round(mean_len, 2),
        "burstiness_score": burstiness,   # كل ما قلّ عن ~0.4، زاد انتظام طول الجُمل بشكل غير معتاد بشريًا
        "type_token_ratio": type_token_ratio,  # كل ما قلّ، زاد تكرار المفردات
    })
    return result


def assess_writing_signal(stylometry: dict[str, Any]) -> dict[str, Any]:
    """
    دائمًا LOW — هذه الطبقة لا تستحق GOOD أو CONFLICT أبدًا بتصميم متعمّد،
    لأن الأبحاث المذكورة في مستندك (البند 8) تؤكد أن هذه المؤشرات
    غير مستقرة بما يكفي لتُعامَل كدليل قوي.
    """
    if not stylometry.get("available"):
        return {"flags": [stylometry.get("reason", "لا يوجد نص كافٍ للتحليل")]}

    flags = []
    if stylometry["burstiness_score"] < 0.35:
        flags.append(
            f"انتظام غير معتاد في أطوال الجُمل (burstiness={stylometry['burstiness_score']}) "
            "— هذا نمط يظهر أحيانًا في نصوص مولّدة، لكنه يظهر أيضًا في الكتابة الأكاديمية/الرسمية المنظّمة"
        )
    if stylometry["type_token_ratio"] < 0.35:
        flags.append(
            f"تكرار مرتفع نسبيًا في المفردات (type-token ratio={stylometry['type_token_ratio']}) "
            "— إشارة ضعيفة وحدها، شائعة أيضًا في النصوص التقنية المتخصصة"
        )
    if not flags:
        flags.append("لا توجد إشارات أسلوبية لافتة — هذا لا يثبت أن الكتابة بشرية")

    return {"flags": flags}
