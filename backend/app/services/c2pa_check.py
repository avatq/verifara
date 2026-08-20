"""
فحص C2PA / Content Credentials — يعتمد على digitalSourceType الرسمي.
"""
import c2pa
import json
from typing import Any

AI_SOURCE_TYPES = {
    "trainedAlgorithmicMedia": "مولَّد بالكامل بالذكاء الاصطناعي",
    "compositeWithTrainedAlgorithmicMedia": "محتوى حقيقي معدَّل بأدوات ذكاء اصطناعي",
}


def check_c2pa(file_path: str) -> dict[str, Any]:
    result: dict[str, Any] = {"available": False, "manifest_found": False}

    try:
        with c2pa.Reader(file_path) as reader:
            manifest_json = reader.json()

        data = json.loads(manifest_json)
        active_manifest = data.get("active_manifest")
        manifests = data.get("manifests", {})

        if not active_manifest or active_manifest not in manifests:
            result.update({"available": True, "manifest_found": False})
            return result

        manifest = manifests[active_manifest]
        claim_generator = manifest.get("claim_generator", None)
        title = manifest.get("title", None)

        actions_data = []
        digital_source_types: list[str] = []
        for assertion in manifest.get("assertions", []):
            if assertion.get("label") in ("c2pa.actions", "c2pa.actions.v2"):
                for action in assertion.get("data", {}).get("actions", []):
                    actions_data.append(action.get("action"))
                    dst = action.get("digitalSourceType", "")
                    if dst:
                        short_type = dst.rstrip("/").split("/")[-1]
                        digital_source_types.append(short_type)

        ai_matches = [t for t in digital_source_types if t in AI_SOURCE_TYPES]

        signature_info = manifest.get("signature_info", {})
        issuer = signature_info.get("issuer", None)

        result.update({
            "available": True,
            "manifest_found": True,
            "claim_generator": claim_generator,
            "title": title,
            "actions": actions_data,
            "digital_source_types": digital_source_types,
            "ai_indicated_by_source_type": bool(ai_matches),
            "ai_source_type_label": AI_SOURCE_TYPES.get(ai_matches[0]) if ai_matches else None,
            "issuer": issuer,
            "honesty_note": (
                "digitalSourceType حقل رسمي بالمعيار لكن غير إلزامي — "
                "وجوده دليل قوي على أصل AI، لكن غيابه لا ينفي احتمال AI بالضرورة."
            ),
        })

    except c2pa.C2paError as e:
        result.update({"available": True, "manifest_found": False, "note": str(e)})
    except Exception as e:
        result["error"] = f"تعذّر فحص C2PA: {e}"

    return result
