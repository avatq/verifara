"""
خدمة البصمة الرقمية (SHA-256)
هذه أول طبقة في الـ Pipeline: UPLOAD -> Fingerprint -> ...
لا تثبت أن الملف "حقيقي"، لكنها تثبت هوية النسخة التي تم تحليلها،
وتُستخدم لاحقًا في: مقارنة الملفات، الربط بين التقرير والملف، كشف التكرار.
"""
import hashlib
from pathlib import Path


CHUNK_SIZE = 1024 * 1024  # 1MB — لتفادي تحميل الملفات الكبيرة (فيديو) بالكامل بالذاكرة


def compute_sha256(file_path: str | Path) -> str:
    """يحسب SHA-256 لملف على القرص بدون تحميله كاملاً في الذاكرة."""
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(CHUNK_SIZE):
            sha256.update(chunk)
    return sha256.hexdigest()


def compute_sha256_bytes(data: bytes) -> str:
    """نسخة بديلة عندما يكون الملف موجودًا كـ bytes في الذاكرة (ملفات صغيرة)."""
    return hashlib.sha256(data).hexdigest()
