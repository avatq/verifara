"""
Image Forensics — البند 7 من المواصفات.
هذه أول طبقة تحليل لا تعتمد على بيانات يمكن حذفها بسهولة (مثل EXIF)،
بل على خصائص فيزيائية للصورة نفسها بعد الضغط والالتقاط.

نبني هنا إشارتين حقيقيتين وقابلتين للتفسير:

1) Error Level Analysis (ELA):
   نعيد حفظ الصورة بجودة JPEG معروفة (90) ونقارنها بالأصل.
   المناطق التي "أُعيد ضغطها" بمستوى مختلف عن باقي الصورة (نتيجة تعديل موضعي:
   لصق، طمس، تركيب) تُظهر مستوى خطأ مختلفًا عن محيطها.
   هذا أسلوب معروف في الطب الشرعي الرقمي (Digital Image Forensics) — إشارة، وليست إثباتًا.

2) Noise Consistency:
   نحسب بقايا الضوضاء (noise residual) عبر مرشّح تمرير عالٍ (High-pass filter)
   ثم نقيس تباين شدة الضوضاء بين مناطق الصورة (Blocks).
   الصور الملتقطة بكاميرا حقيقية عادة لها نمط ضوضاء متجانس نسبيًا ناتج عن الحساس (sensor noise).
   تفاوت حاد بين المناطق قد يشير إلى دمج مصادر مختلفة، أو لصورة مولّدة بالكامل بالذكاء الاصطناعي
   (التي أحيانًا تفتقر لنمط ضوضاء الحساس الطبيعي أو تُظهر نمطًا اصطناعيًا موحدًا جدًا).
"""
import io
import numpy as np
import cv2
from PIL import Image
from typing import Any


def error_level_analysis(file_path: str, quality: int = 90) -> dict[str, Any]:
    result: dict[str, Any] = {"available": False}
    try:
        original = Image.open(file_path).convert("RGB")

        buffer = io.BytesIO()
        original.save(buffer, format="JPEG", quality=quality)
        buffer.seek(0)
        recompressed = Image.open(buffer)

        orig_arr = np.asarray(original, dtype=np.int16)
        recomp_arr = np.asarray(recompressed, dtype=np.int16)

        if orig_arr.shape != recomp_arr.shape:
            result["error"] = "تعذّر مقارنة الأبعاد بعد إعادة الضغط"
            return result

        diff = np.abs(orig_arr - recomp_arr).astype(np.uint8)
        ela_gray = cv2.cvtColor(diff, cv2.COLOR_RGB2GRAY)

        mean_error = float(np.mean(ela_gray))
        max_error = float(np.max(ela_gray))
        std_error = float(np.std(ela_gray))

        # نقسّم الصورة إلى مربعات (blocks) ونحسب متوسط الخطأ بكل منها
        # لرصد وجود منطقة "شاذة" واضحة (تدل على تعديل موضعي) لا مجرد ضوضاء عامة
        h, w = ela_gray.shape
        block_size = max(16, min(h, w) // 8)
        block_means = []
        for y in range(0, h - block_size, block_size):
            for x in range(0, w - block_size, block_size):
                block = ela_gray[y:y + block_size, x:x + block_size]
                block_means.append(float(np.mean(block)))

        if block_means:
            block_arr = np.array(block_means)
            outlier_ratio = float(np.mean(block_arr > (np.mean(block_arr) + 2 * np.std(block_arr) + 1e-6)))
        else:
            outlier_ratio = 0.0

        result.update({
            "available": True,
            "mean_error_level": round(mean_error, 3),
            "max_error_level": round(max_error, 3),
            "std_error_level": round(std_error, 3),
            "block_outlier_ratio": round(outlier_ratio, 4),
        })
    except Exception as e:
        result["error"] = f"تعذّر تنفيذ Error Level Analysis: {e}"

    return result


def noise_consistency_analysis(file_path: str) -> dict[str, Any]:
    result: dict[str, Any] = {"available": False}
    try:
        img = cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            result["error"] = "تعذّر فتح الصورة عبر OpenCV"
            return result

        # مرشّح تمرير عالٍ بسيط: الصورة - نسخة مموّهة منها = بقايا الضوضاء عالية التردد
        blurred = cv2.GaussianBlur(img, (5, 5), 0)
        noise_residual = cv2.absdiff(img, blurred)

        h, w = noise_residual.shape
        block_size = max(16, min(h, w) // 8)
        block_variances = []
        for y in range(0, h - block_size, block_size):
            for x in range(0, w - block_size, block_size):
                block = noise_residual[y:y + block_size, x:x + block_size]
                block_variances.append(float(np.var(block)))

        if not block_variances:
            result["error"] = "الصورة صغيرة جدًا لتقسيمها إلى مناطق تحليل"
            return result

        variances = np.array(block_variances)
        mean_var = float(np.mean(variances))
        std_var = float(np.std(variances))
        # معامل التباين (Coefficient of Variation): كل ما زاد، زاد تفاوت نمط الضوضاء بين المناطق
        cv_ratio = float(std_var / mean_var) if mean_var > 1e-6 else 0.0

        # إشارة إضافية أهم من CV وحدها: نسبة المناطق "الملساء بشكل غير طبيعي"
        # (تباين ضوضاء قريب من الصفر) بينما باقي الصورة فيها ضوضاء حساس طبيعية.
        # هذا نمط شائع جدًا في: لصق منطقة من مصدر آخر، أو تنعيم مفتعل، أو أجزاء مولّدة بالذكاء الاصطناعي.
        low_variance_threshold = max(mean_var * 0.15, 1.0)
        flat_block_ratio = float(np.mean(variances < low_variance_threshold)) if mean_var > 3.0 else 0.0

        result.update({
            "available": True,
            "mean_noise_variance": round(mean_var, 4),
            "noise_variation_coefficient": round(cv_ratio, 4),
            "flat_region_ratio": round(flat_block_ratio, 4),
        })
    except Exception as e:
        result["error"] = f"تعذّر تحليل نمط الضوضاء: {e}"

    return result


def assess_forensic_signals(ela: dict[str, Any], noise: dict[str, Any]) -> dict[str, Any]:
    """
    يحوّل القياسات الرقمية الخام إلى تصنيف Low/Moderate/High مع تفسير واضح.
    العتبات هنا مبدئية (heuristic) — تحتاج معايرة لاحقًا على بيانات حقيقية متنوعة،
    وهذا مذكور بوضوح في الإخراج نفسه حتى لا نمنح ثقة زائفة في الأرقام.
    """
    flags: list[str] = []
    signal = "low"

    if ela.get("available"):
        if ela["block_outlier_ratio"] > 0.08:
            flags.append(f"نسبة {round(ela['block_outlier_ratio']*100,1)}% من مناطق الصورة تُظهر مستوى خطأ ضغط شاذًا عن محيطها — قد يشير لتعديل موضعي (لصق/طمس)")
            signal = "moderate"

    if noise.get("available"):
        if noise.get("flat_region_ratio", 0) > 0.10:
            flags.append(f"نسبة {round(noise['flat_region_ratio']*100,1)}% من مناطق الصورة ملساء بشكل غير طبيعي مقارنة ببقية الصورة — إشارة شائعة على لصق منطقة من مصدر آخر أو محتوى مولّد جزئيًا")
            signal = "high"
        elif noise["noise_variation_coefficient"] > 0.10:
            flags.append("تفاوت ملحوظ في نمط الضوضاء بين مناطق الصورة — قد يشير لدمج مصادر متعددة أو غياب نمط ضوضاء حساس كاميرا طبيعي")
            signal = "moderate" if signal == "low" else signal

    if not flags:
        flags.append("لا توجد إشارات forensic ملحوظة في هذا الفحص الأولي")

    return {"signal_level": signal, "flags": flags}
