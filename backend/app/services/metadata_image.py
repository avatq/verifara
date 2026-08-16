"""
تحليل Metadata للصور (EXIF).
يطابق البند رقم 6 من المواصفات: Camera / Lens / Date / GPS / Software / Color Profile
مع فحص "Consistency" بسيط — إشارات وليست أحكام قطعية.
"""
from PIL import Image, ExifTags
from typing import Any


def extract_image_metadata(file_path: str) -> dict[str, Any]:
    """يستخرج EXIF المتاح من الصورة ويرجعه بصيغة مقروءة."""
    result: dict[str, Any] = {
        "available": False,
        "camera_make": None,
        "camera_model": None,
        "lens": None,
        "datetime_original": None,
        "gps_present": False,
        "software": None,
        "orientation": None,
        "color_profile": None,
        "dimensions": None,
        "raw_tags_count": 0,
    }

    try:
        with Image.open(file_path) as img:
            result["dimensions"] = f"{img.width}x{img.height}"
            result["color_profile"] = img.info.get("icc_profile") and "Embedded ICC profile" or img.mode

            exif = img.getexif()
            if not exif:
                return result

            tags = {ExifTags.TAGS.get(k, k): v for k, v in exif.items()}
            result["raw_tags_count"] = len(tags)
            result["available"] = len(tags) > 0

            result["camera_make"] = tags.get("Make")
            result["camera_model"] = tags.get("Model")
            result["software"] = tags.get("Software")
            result["orientation"] = tags.get("Orientation")
            result["datetime_original"] = tags.get("DateTimeOriginal") or tags.get("DateTime")

            # GPS IFD منفصل عن الوسوم العادية
            gps_ifd = exif.get_ifd(ExifTags.IFD.GPSInfo) if hasattr(ExifTags, "IFD") else None
            result["gps_present"] = bool(gps_ifd)

            # عدسة الكاميرا غالبًا داخل EXIF IFD الفرعي
            try:
                exif_ifd = exif.get_ifd(ExifTags.IFD.Exif)
                lens_tags = {ExifTags.TAGS.get(k, k): v for k, v in exif_ifd.items()}
                result["lens"] = lens_tags.get("LensModel")
            except Exception:
                pass

    except Exception as e:
        result["error"] = f"تعذّر قراءة الصورة: {e}"

    return result


def assess_metadata_consistency(metadata: dict[str, Any]) -> dict[str, Any]:
    """
    فحص اتساق أولي (Rule-based) — البند 6:
    لا يثبت شيئًا بمفرده، لكنه يرصد تناقضات ظاهرة تستحق التنويه في التقرير.
    مثال حقيقي يمكن رصده هنا: وجود اسم أداة توليد/تعديل AI معروفة داخل حقل Software
    مع غياب أي بيانات كاميرا (Make/Model).
    """
    flags: list[str] = []

    known_ai_software_markers = [
        "midjourney", "dall-e", "dalle", "stable diffusion", "firefly ai",
        "runway", "leonardo.ai", "adobe firefly",
    ]

    software = (metadata.get("software") or "").lower()
    has_camera_info = bool(metadata.get("camera_make") or metadata.get("camera_model"))

    for marker in known_ai_software_markers:
        if marker in software:
            flags.append(f"حقل Software يحتوي إشارة إلى أداة توليد بالذكاء الاصطناعي: '{marker}'")

    if not metadata.get("available"):
        flags.append("لا توجد بيانات EXIF على الإطلاق — شائع في: لقطات الشاشة، الصور المُصدّرة من مواقع التواصل، أو بعض أدوات التوليد")

    if metadata.get("available") and not has_camera_info and metadata.get("software"):
        flags.append("توجد بيانات EXIF وبرنامج معالجة، لكن بلا معلومات كاميرا — يستحق مراجعة يدوية")

    status = "suspicious" if any("توليد بالذكاء" in f for f in flags) else (
        "no_data" if not metadata.get("available") else "consistent"
    )

    return {"status": status, "flags": flags}
