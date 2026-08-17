"""
Image Forensics — البند 7 من المواصفات (نسخة v2 — مبنية على التجمّع المكاني).

## لماذا أُعيد بناء هذا الملف
النسخة الأولى قارنت كل "مربع" (block) بمتوسط الصورة كاملة. هذا يُنتج
false positives كثيرة على صور حقيقية تحتوي طبيعيًا أكثر من نسيج واحد
(مثال حقيقي واجهناه: صورة شخص يحمل بطاقة هوية — البطاقة سطح بلاستيكي
أملس، والجلد/الشعر سطح ذو نسيج طبيعي؛ الفرق بينهما طبيعي 100% وليس دليل تلاعب).

## المبدأ العلمي الأصح (مستخدم فعليًا بأدبيات Digital Image Forensics)
التلاعب الحقيقي (لصق/تركيب منطقة من مصدر آخر) يترك بقعة واحدة متجمّعة
ومتلاصقة (spatially contiguous) ذات خصائص مختلفة عن محيطها المباشر.
اختلاف نسيج طبيعي بين جسمين مختلفين بالصورة (بطاقة + يد، سماء + مبنى)
لا يُنتج هذا النمط تحديدًا — كل منطقة متسقة داخليًا مع نفسها بس مختلفة
عن المنطقة الثانية بشكل واسع ومتوقّع منطقيًا من محتوى الصورة نفسه.

لذلك النسخة الجديدة لا تكتفي بـ"نسبة المربعات الشاذة"، بل تتحقق:
1. هل هذي المربعات الشاذة متجاورة فعليًا (تكوّن مكوّن متصل واحد)؟
2. هل حجم هذا المكوّن معقول لبقعة تلاعب (مو صغير جدًا = ضوضاء عشوائية،
   ومو كبير جدًا = على الأغلب نسيج طبيعي واسع مثل خلفية أو جسم كامل)؟
3. هل هذا المكوّن داخلي (لا يلامس حواف الصورة بشكل كامل) — لصقات
   التلاعب غالبًا داخل الصورة، بينما جسم طبيعي كامل (كخلفية) يلامس الحواف؟

هذا لا يزال heuristic (قواعد مصمَّمة يدويًا، مو نموذج مدرَّب على بيانات)
وما زال يحتاج معايرة على مجموعة اختبار أوسع بكثير قبل الاعتماد عليه
بمنتج مدفوع — لكنه أصح علميًا من مقارنة كل مربع بمتوسط الصورة كاملة.
"""
import io
import numpy as np
import cv2
from PIL import Image
from scipy import ndimage
from typing import Any

MAX_DIMENSION = 1600


def _load_and_downscale(file_path: str) -> Image.Image:
    img = Image.open(file_path).convert("RGB")
    if max(img.size) > MAX_DIMENSION:
        ratio = MAX_DIMENSION / max(img.size)
        new_size = (int(img.width * ratio), int(img.height * ratio))
        img = img.resize(new_size, Image.LANCZOS)
    return img


def _block_grid(arr_2d: np.ndarray, block_size: int) -> tuple[np.ndarray, int, int]:
    h, w = arr_2d.shape
    rows = h // block_size
    cols = w // block_size
    grid = np.zeros((rows, cols))
    for r in range(rows):
        for c in range(cols):
            block = arr_2d[r * block_size:(r + 1) * block_size, c * block_size:(c + 1) * block_size]
            grid[r, c] = np.mean(block)
    return grid, rows, cols


def _largest_interior_cluster(outlier_mask: np.ndarray) -> dict[str, Any]:
    if outlier_mask.sum() == 0:
        return {"found": False, "size_ratio": 0.0, "touches_border": True}

    labeled, num_features = ndimage.label(outlier_mask)
    if num_features == 0:
        return {"found": False, "size_ratio": 0.0, "touches_border": True}

    sizes = ndimage.sum(outlier_mask, labeled, range(1, num_features + 1))
    largest_label = np.argmax(sizes) + 1
    largest_size = sizes[np.argmax(sizes)]
    total_blocks = outlier_mask.size
    size_ratio = float(largest_size / total_blocks)

    component_mask = labeled == largest_label
    rows_with, cols_with = np.where(component_mask)
    h, w = outlier_mask.shape
    touches_border = (
        rows_with.min() == 0 or rows_with.max() == h - 1 or
        cols_with.min() == 0 or cols_with.max() == w - 1
    )

    return {
        "found": True,
        "size_ratio": round(size_ratio, 4),
        "touches_border": bool(touches_border),
        "cluster_block_count": int(largest_size),
    }


def error_level_analysis(file_path: str, quality: int = 90) -> dict[str, Any]:
    result: dict[str, Any] = {"available": False}
    try:
        original = _load_and_downscale(file_path)

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
        std_error = float(np.std(ela_gray))

        block_size = max(16, min(ela_gray.shape) // 12)
        grid, rows, cols = _block_grid(ela_gray, block_size)

        if grid.size < 9:
            result.update({"available": True, "mean_error_level": round(mean_error, 3),
                            "std_error_level": round(std_error, 3), "cluster": {"found": False}})
            return result

        threshold = np.mean(grid) + 2 * np.std(grid) + 1e-6
        outlier_mask = grid > threshold
        cluster = _largest_interior_cluster(outlier_mask)

        result.update({
            "available": True,
            "mean_error_level": round(mean_error, 3),
            "std_error_level": round(std_error, 3),
            "grid_shape": [rows, cols],
            "cluster": cluster,
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

        h0, w0 = img.shape
        if max(h0, w0) > MAX_DIMENSION:
            ratio = MAX_DIMENSION / max(h0, w0)
            img = cv2.resize(img, (int(w0 * ratio), int(h0 * ratio)), interpolation=cv2.INTER_AREA)

        blurred = cv2.GaussianBlur(img, (5, 5), 0)
        noise_residual = cv2.absdiff(img, blurred)

        block_size = max(16, min(noise_residual.shape) // 12)

        h, w = noise_residual.shape
        rows, cols = h // block_size, w // block_size
        var_grid = np.zeros((rows, cols))
        for r in range(rows):
            for c in range(cols):
                block = noise_residual[r * block_size:(r + 1) * block_size, c * block_size:(c + 1) * block_size]
                var_grid[r, c] = np.var(block)

        if var_grid.size < 9:
            result.update({"available": True, "cluster": {"found": False}})
            return result

        mean_var = float(np.mean(var_grid))
        median_var = float(np.median(var_grid))
        low_threshold = max(median_var * 0.12, 1.0) if mean_var > 3.0 else 0

        flat_mask = var_grid < low_threshold
        cluster = _largest_interior_cluster(flat_mask)

        result.update({
            "available": True,
            "mean_noise_variance": round(mean_var, 4),
            "median_noise_variance": round(median_var, 4),
            "grid_shape": [rows, cols],
            "cluster": cluster,
        })
    except Exception as e:
        result["error"] = f"تعذّر تحليل نمط الضوضاء: {e}"

    return result


def assess_forensic_signals(ela: dict[str, Any], noise: dict[str, Any]) -> dict[str, Any]:
    flags: list[str] = []
    matches: list[str] = []

    MIN_CLUSTER_RATIO = 0.008
    MAX_CLUSTER_RATIO = 0.35

    for name, data in [("ELA", ela), ("نمط الضوضاء", noise)]:
        cluster = data.get("cluster", {})
        if not cluster.get("found"):
            continue
        ratio = cluster.get("size_ratio", 0)
        touches_border = cluster.get("touches_border", True)

        if MIN_CLUSTER_RATIO <= ratio <= MAX_CLUSTER_RATIO and not touches_border:
            matches.append(name)
            flags.append(
                f"({name}) وُجدت بقعة داخلية متجمّعة (~{round(ratio*100,1)}% من مساحة الصورة) "
                "بخصائص مختلفة عن محيطها المباشر ولا تلامس حواف الصورة — "
                "نمط يستدعي مراجعة يدوية لاحتمال لصق/تركيب موضعي"
            )

    if len(matches) >= 2:
        signal = "high"
    elif len(matches) == 1:
        signal = "moderate"
    else:
        signal = "low"

    if not flags:
        flags.append("لا توجد بقعة متجمّعة مشبوهة داخل الصورة في هذا الفحص الأولي")

    return {"signal_level": signal, "flags": flags}
