"""
عميل Hive — كشف الصور المولّدة بالذكاء الاصطناعي عبر Vision Language Model (V3 self-serve).
ملاحظة: النموذج المتخصص 96-98% يتطلب مشروع V2 مؤسسي (تواصل مبيعات) — غير متاح ذاتيًا.
البديل هنا: Hive VLM عام موجَّه بطلب تصنيف واضح.
"""
import os
import json
import httpx
from typing import Any

HIVE_VLM_ENDPOINT = "https://api.thehive.ai/api/v3/chat/completions"

CLASSIFICATION_PROMPT = (
    "You are an expert image forensics analyst. Examine this image carefully for signs "
    "of AI generation (e.g. unnatural textures, impossible lighting, artifacts typical of "
    "diffusion models, unnatural symmetry, warped details in hands/text/backgrounds). "
    "Respond with ONLY a JSON object, no other text, in exactly this format: "
    '{"ai_generated": true or false, "confidence": a number from 0.0 to 1.0, '
    '"reasoning": "one short sentence explaining the key visual evidence"}'
)


async def check_ai_generated(file_path: str) -> dict[str, Any]:
    api_key = os.getenv("HIVE_API_KEY")
    result: dict[str, Any] = {"available": False}

    if not api_key:
        result["error"] = "HIVE_API_KEY غير مضبوط في متغيرات البيئة"
        return result

    try:
        import base64
        with open(file_path, "rb") as f:
            image_bytes = f.read()
        ext = file_path.rsplit(".", 1)[-1].lower()
        mime = "image/jpeg" if ext in ("jpg", "jpeg") else f"image/{ext}"
        b64_data = base64.b64encode(image_bytes).decode()
        data_url = f"data:{mime};base64,{b64_data}"

        payload = {
            "model": "hive/vision-language-model",
            "max_tokens": 200,
            "messages": [{
                "role": "user",
                "content": [
                    {"type": "text", "text": CLASSIFICATION_PROMPT},
                    {"type": "image_url", "image_url": {"url": data_url}},
                ],
            }],
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                HIVE_VLM_ENDPOINT,
                headers={
                    "authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )

        if response.status_code != 200:
            error_msg = f"Hive VLM رجع status {response.status_code}: {response.text[:300]}"
            print(f"[HIVE ERROR] {error_msg}")
            result["error"] = error_msg
            return result

        data = response.json()
        content = data["choices"][0]["message"]["content"].strip()

        if content.startswith("```"):
            content = content.strip("`").removeprefix("json").strip()

        parsed = json.loads(content)

        ai_generated = bool(parsed.get("ai_generated", False))
        confidence = float(parsed.get("confidence", 0.5))
        reasoning = parsed.get("reasoning", "")

        result.update({
            "available": True,
            "ai_generated_score": confidence if ai_generated else round(1 - confidence, 4),
            "not_ai_generated_score": round(1 - confidence, 4) if ai_generated else confidence,
            "reasoning": reasoning,
            "model_type": "hive_vlm_general_purpose",
        })

    except Exception as e:
        print(f"[HIVE ERROR] exception: {type(e).__name__}: {e}")
        result["error"] = f"تعذّر الاتصال بـ Hive VLM: {e}"

    return result
