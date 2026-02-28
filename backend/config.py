import os
from datetime import timedelta
from dotenv import load_dotenv

# Environment yüklemesi
load_dotenv()


class BaseConfig:
    """FriendZone Temel Yapılandırma - Tüm ortamlar için ortak."""

    # --- Flask Core ---
    APP_NAME = "FriendZone"
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-key-change-me-12345")
    FLASK_ENV = os.getenv("FLASK_ENV", "development")

    # --- Database (SQLAlchemy) ---
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///friendzone.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Bağlantı havuzu: Çoklu kullanıcıda (mezuniyet sunumu sırasında) kopmaları önler
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_size": 10,
        "max_overflow": 20,
        "pool_recycle": 1800,
        "pool_pre_ping": True,
    }

    # --- JWT (Kimlik Doğrulama) ---
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "jwt-secret-98765")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    JWT_ERROR_MESSAGE_KEY = "message"

    # --- AI & ML Parametreleri (Senin Projen İçin Kritik) ---
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    VECTOR_DB_URL = os.getenv("PINECONE_URL")  # Pinecone kullanıyorsan
    SIMILARITY_THRESHOLD = 0.65  # Eşleşme alt sınırı
    MAX_RECOMMENDATIONS = 10  # Bir seferde kaç arkadaş önerilecek?

    # --- Dosya Yükleme (Profil Fotoğrafları vb.) ---
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # Maksimum 5MB yükleme izni
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

    # --- Güvenlik ---
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = True if FLASK_ENV == "production" else False
    SESSION_COOKIE_SAMESITE = "Lax"


class DevelopmentConfig(BaseConfig):
    """Geliştirme Ortamı - Hata ayıklama açık."""
    DEBUG = True
    SQLALCHEMY_ECHO = False  # Sorguları terminale basmak istersen True yap


class ProductionConfig(BaseConfig):
    """Üretim Ortamı - Maksimum Güvenlik."""
    DEBUG = False
    TESTING = False

    # Güvenlik Kontrolleri
    def __init__(self):
        if self.SECRET_KEY == "dev-key-change-me-12345":
            raise ValueError("❌ KRİTİK: Production'da varsayılan SECRET_KEY kullanılamaz!")

        if "sqlite" in self.SQLALCHEMY_DATABASE_URI:
            import logging
            logging.warning("⚠️ UYARI: Production'da SQLite performansı düşük olabilir. PostgreSQL önerilir.")


class TestingConfig(BaseConfig):
    """Test Ortamı - Hafif ve İzole."""
    TESTING = True
    DEBUG = True
    # Bellek içi (In-memory) veritabanı testleri çok hızlandırır
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    # Testlerde JWT süresini kısa tutabiliriz
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(seconds=5)


# Ortama göre config seçici sözlük
config_by_name = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig
}

# Aktif config'e erişim kolaylığı
active_config = config_by_name.get(os.getenv("FLASK_ENV", "development"), DevelopmentConfig)