"""
AuthentiCheck (Verifara) — إعدادات التطبيق المركزية
كل القيم القابلة للتغيير بين بيئة التطوير والإنتاج توضع هنا فقط.
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # عام
    APP_NAME: str = "Verifara / AuthentiCheck"
    API_V1_PREFIX: str = "/api/v1"
    ENVIRONMENT: str = "development"  # development | production

    # حدود الرفع
    MAX_UPLOAD_SIZE_MB: int = 500
    ALLOWED_IMAGE_EXT: tuple = (".jpg", ".jpeg", ".png", ".webp")
    ALLOWED_DOC_EXT: tuple = (".pdf", ".docx", ".txt", ".csv")
    ALLOWED_VIDEO_EXT: tuple = (".mp4", ".mov", ".webm", ".avi")
    ALLOWED_AUDIO_EXT: tuple = (".mp3", ".wav", ".m4a")

    # تخزين مؤقت للملفات أثناء التحليل (المرحلة 1: تخزين محلي — لاحقًا S3)
    UPLOAD_DIR: str = "/tmp/verifara_uploads"
    DELETE_FILE_AFTER_ANALYSIS_DEFAULT: bool = True

    # قاعدة البيانات (تُملأ لاحقًا عند ربط PostgreSQL فعليًا)
    DATABASE_URL: str = "postgresql://verifara:verifara@localhost:5432/verifara"

    # قائمة الانتظار (تُستخدم في المرحلة 2 عند إضافة الفيديو/الصوت)
    REDIS_URL: str = "redis://localhost:6379/0"

    class Config:
        env_file = ".env"


@lru_cache
def get_settings() -> Settings:
    return Settings()
