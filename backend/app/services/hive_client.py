"""
عميل Hive Moderation API — كشف حقيقي للصور المولّدة بالذكاء الاصطناعي.
المرجع الرسمي: https://docs.thehive.ai/docs/ai-image-and-video-detection
التسعير: ~$0.001 لكل صورة (حسب الاستخدام الفعلي، بدون اشتراك ثابت).
أمان مهم: مفتاح الـ API يُقرأ فقط من متغير بيئة HIVE_API_KEY.
"""
import os
import httpx
from typing import Any

HIVE_ENDPOINT = "https://api.thehive.ai/api/v2/task/sync"


async def check_ai_generated(file_path: str) -> dict[str, Any]:
    api_key = os.getenv("HIVE_API_KEY")
    result: dict[str, Any] = {"available": False}

    if not api_key:
        result["error"] = "HIVE_API_KEY غير مضبوط في متغيرات البيئة"
        return result

    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            with open(file_path, "rb") as f:
                response = await client.post(
                    HIVE_ENDPOINT,
                    headers={"authorization": f"Token {api_key}"},
                    files={"media": f},
                )

        if response.status_code != 200:
            result["error"] = f"Hive API رجع status {response.status_code}: {response.text[:200]}"
            return result

        data = response.json()
        status_list = data.get("status", [])
        if not status_list or status_list[0].get("status", {}).get("code") != "0":
            result["error"] = "Hive API لم يرجع نتيجة ناجحة"
            return result

        output = status_list[0]["response"]["output"][0]["classes"]
        classes = {c["class"]: c["score"] for c in output}

        ai_score = classes.get("ai_generated", 0.0)
        not_ai_score = classes.get("not_ai_generated", 0.0)

        source_classes = {
            k: v for k, v in classes.items()
            if k not in ("ai_generated", "not_ai_generated", "none", "inconclusive", "inconclusive_video")
        }
        top_source = max(source_classes.items(), key=lambda x: x[1]) if source_classes else None

        result.update({
            "available": True,
            "ai_generated_score": round(ai_score, 4),
            "not_ai_generated_score": round(not_ai_score, 4),
            "likely_source": top_source[0] if top_source and top_source[1] > 0.3 else None,
            "likely_source_score": round(top_source[1], 4) if top_source and top_source[1] > 0.3 else None,
        })

    except Exception as e:
        result["error"] = f"تعذّر الاتصال بـ Hive API: {e}"

    return result
