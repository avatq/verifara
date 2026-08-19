"""
فحص C2PA / Content Credentials — قراءة مباشرة، بدون API مدفوع.
غياب C2PA يعني "لا معلومة"، مو "دليل تلاعب" — المعيار غير منتشر بعد.
"""
import c2pa
from typing import Any


def check_c2pa(file_path: str) -> dict[str, Any]:
    result: dict[str, Any] = {"available": False, "manifest_found": False}

    try:
        with c2pa.Reader(file_path) as reader:
            manifest_json = reader.json()

        import json
        data = json.loads(manifest_json)
        active_manifest = data.get("active_manifest")
        manifests = data.get("manifests", {})

        if not active_manifest or active_manifest not in manifests:
            result.update({"available": True, "manifest_found": False})
            return result

        manifest = manifests[active_manifest]
        claim_generator = manifest.get("claim_generator", None)
        title = manifest.get("title", None)

        actions = []
        for assertion in manifest.get("assertions", []):
            if assertion.get("label") == "c2pa.actions":
                actions = [a.get("action") for a in assertion.get("data", {}).get("actions", [])]

        signature_info = manifest.get("signature_info", {})
        issuer = signature_info.get("issuer", None)
        cert_serial = signature_info.get("cert_serial_number", None)

        result.update({
            "available": True,
            "manifest_found": True,
            "claim_generator": claim_generator,
            "title": title,
            "actions": actions,
            "issuer": issuer,
            "has_valid_signature": bool(issuer and cert_serial),
        })

    except c2pa.C2paError as e:
        result.update({"available": True, "manifest_found": False, "note": str(e)})
    except Exception as e:
        result["error"] = f"تعذّر فحص C2PA: {e}"

    return result
