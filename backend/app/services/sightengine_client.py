"""
عميل Sightengine — كشف الصور المولّدة بالذكاء الاصطناعي.
دقة معلنة 98.3%، self-serve فعليًا.
المرجع: https://sightengine.com/docs/ai-generated-image-detection
"""
import os
import httpx
from typing import Any

SIGHTENGINE_ENDPOINT = "https://api.sightengine.com/1.0/check.json"


async def check_ai_generated(file_path: str) -> dict[str, Any]:
    api_user = os.getenv("SIGHTENGINE_API_USER")
    api_secret = os.getenv("SIGHTENGINE_API_SECRET")
    result: dict[str, Any] = {"available": False}

    if not api_user or not api_secret:
        result["error"] = "SIGHTENGINE_API_USER أو SIGHTENGINE_API_SECRET غير مضبوطين"
        return result

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            with open(file_path, "rb") as f:
                response = await client.post(
                    SIGHTENGINE_ENDPOINT,
                    files={"media": f},
                    data={
                        "models": "genai",
                        "api_user": api_user,
                        "api_secret": api_secret,
                    },
                )

        if response.status_code != 200:
            error_msg = f"Sightengine رجع status {response.status_code}: {response.text[:300]}"
            print(f"[SIGHTENGINE ERROR] {error_msg}")
            result["error"] = error_msg
            return result

        data = response.json()
        if data.get("status") != "success":
            print(f"[SIGHTENGINE ERROR] status != success: {str(data)[:300]}")
            result["error"] = "Sightengine لم يرجع نتيجة ناجحة"
            return result

        ai_score = float(data["type"]["ai_generated"])
        generators = data["type"].get("ai_generators", {})
        top_generator = max(generators.items(), key=lambda x: x[1]) if generators else None

        result.update({
            "available": True,
            "ai_generated_score": round(ai_score, 4),
            "not_ai_generated_score": round(1 - ai_score, 4),
            "likely_source": top_generator[0] if top_generator and top_generator[1] > 0.3 else None,
            "likely_source_score": round(top_generator[1], 4) if top_generator and top_generator[1] > 0.3 else None,
            "model_type": "sightengine_genai_specialized",
        })

    except Exception as e:
        print(f"[SIGHTENGINE ERROR] exception: {type(e).__name__}: {e}")
        result["error"] = f"تعذّر الاتصال بـ Sightengine: {e}"

    return result
