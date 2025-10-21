import os
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()


class Config:
    """Uygulama konfigürasyon sınıfı"""

    # Temel Flask config
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'gizli-anahtar-geliştirme-modu'

    # Veritabanı config
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///friendzone.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # OpenAI API config
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

    # Sunucu config
    HOST = os.environ.get('HOST') or '0.0.0.0'
    PORT = int(os.environ.get('PORT') or 5000)

    # Ortam değişkeni
    ENV = os.environ.get('FLASK_ENV') or 'development'