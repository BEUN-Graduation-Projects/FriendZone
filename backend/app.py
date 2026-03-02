# backend/app.py
import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, jsonify, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_socketio import SocketIO
from dotenv import load_dotenv

# .env yüklemesi en başta olmalı
load_dotenv()

# Extensions - Tek bir noktadan yönetilmeli
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
cors = CORS()
socketio = SocketIO()


class Config:
    """Temel yapılandırma sınıfı"""
    SECRET_KEY = os.getenv("SECRET_KEY", "friendzone-super-secret")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///friendzone.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "jwt-secret-key")

    # Veritabanı bağlantı havuzu optimizasyonu
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_size": 10,
        "max_overflow": 20,
        "pool_recycle": 3600,
        "pool_pre_ping": True,
    }

    # Socket.IO yapılandırması
    SOCKETIO_CORS_ALLOWED_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")
    SOCKETIO_LOGGER = True if os.getenv("FLASK_ENV") == "development" else False
    SOCKETIO_ENGINEIO_LOGGER = True if os.getenv("FLASK_ENV") == "development" else False

    # Dosya yükleme ayarları
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')

    # Admin panel ayarları
    ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "FriendZone2024")


def create_app(config_class=Config):
    """Gelişmiş Application Factory - FriendZone ana uygulama oluşturucu"""

    # Template ve static klasör yollarını belirle
    template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'templates'))
    static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'static'))

    app = Flask(__name__,
                template_folder=template_dir,
                static_folder=static_dir)
    app.config.from_object(config_class)

    # Template filter'ları ekle
    @app.template_filter('strftime')
    def _strftime(date, fmt=None):
        if fmt:
            return date.strftime(fmt)
        return date.strftime('%d %B %Y')

    # Logging Yapılandırması
    configure_logging(app)

    # Extensions Init
    initialize_extensions(app)

    # Blueprint ve Hata Yönetimi
    register_blueprints(app)
    register_error_handlers(app)
    register_core_routes(app)

    # Socket.IO olaylarını içe aktar
    try:
        from backend import socket_events
        app.logger.info("✅ Socket.IO olayları yüklendi")
    except ImportError as e:
        app.logger.warning(f"⚠️ Socket.IO olayları yüklenemedi: {e}")

    # Veritabanı tablolarını oluştur
    with app.app_context():
        try:
            if app.config.get("ENV") == "development":
                db.create_all()
                app.logger.info("✅ Development ortamında tablolar oluşturuldu.")
        except Exception as e:
            app.logger.error(f"❌ Veritabanı başlatma hatası: {e}")

    app.logger.info("✅ FriendZone uygulaması başarıyla başlatıldı")
    return app


def initialize_extensions(app):
    """Tüm Flask extension'larını başlat"""

    # Veritabanı
    db.init_app(app)
    migrate.init_app(app, db)

    # JWT
    jwt.init_app(app)

    # CORS
    cors.init_app(
        app,
        resources={
            r"/api/*": {"origins": app.config.get("SOCKETIO_CORS_ALLOWED_ORIGINS")},
            r"/admin/*": {"origins": app.config.get("SOCKETIO_CORS_ALLOWED_ORIGINS")},
            r"/socket.io/*": {"origins": app.config.get("SOCKETIO_CORS_ALLOWED_ORIGINS")}
        },
        supports_credentials=True
    )

    # Socket.IO
    socketio.init_app(
        app,
        cors_allowed_origins=app.config.get("SOCKETIO_CORS_ALLOWED_ORIGINS"),
        logger=app.config.get("SOCKETIO_LOGGER"),
        engineio_logger=app.config.get("SOCKETIO_ENGINEIO_LOGGER"),
        async_mode='eventlet' if not app.debug else None,
        path='socket.io'
    )


def configure_logging(app):
    """Logging yapılandırması"""

    # Logs dizinini oluştur
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        os.mkdir(log_dir)

    # Dosya handler
    file_handler = RotatingFileHandler(
        os.path.join(log_dir, 'friendzone.log'),
        maxBytes=10 * 1024 * 1024,
        backupCount=10
    )
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)

    # Konsol handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))
    console_handler.setLevel(logging.DEBUG if app.debug else logging.INFO)

    app.logger.addHandler(file_handler)
    app.logger.addHandler(console_handler)
    app.logger.setLevel(logging.DEBUG if app.debug else logging.INFO)

    app.logger.info('🚀 FriendZone uygulaması başlatılıyor...')
    app.logger.info(f'🔧 Environment: {os.getenv("FLASK_ENV", "development")}')
    app.logger.info(f'🗄️  Database: {app.config["SQLALCHEMY_DATABASE_URI"]}')
    app.logger.info(f'📁 Template folder: {app.template_folder}')
    app.logger.info(f'📁 Static folder: {app.static_folder}')


def register_error_handlers(app):
    """Hata yakalayıcılar"""

    @app.errorhandler(404)
    def not_found_error(error):
        app.logger.warning(f"404 - Sayfa bulunamadı: {error}")
        if request.path.startswith('/api/'):
            return jsonify({"error": "Kaynak bulunamadı", "code": 404}), 404
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        app.logger.error(f"500 - Sunucu hatası: {error}")
        if request.path.startswith('/api/'):
            return jsonify({"error": "Sunucu hatası", "code": 500}), 500
        return render_template('500.html'), 500


def register_blueprints(app):
    """Blueprint'leri kaydet"""

    from backend.routes.auth_routes import auth_bp
    from backend.routes.community_routes import community_bp
    from backend.routes.assistant_routes import assistant_bp
    from backend.routes.test_routes import test_bp
    from backend.routes.chat_routes import chat_bp
    from backend.routes.admin_routes import admin_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(community_bp, url_prefix="/api/community")
    app.register_blueprint(assistant_bp, url_prefix="/api/assistant")
    app.register_blueprint(test_bp, url_prefix="/api/test")
    app.register_blueprint(chat_bp, url_prefix="/api/chat")
    app.register_blueprint(admin_bp, url_prefix="/admin")

    app.logger.info("📋 Blueprint'ler kaydedildi:")
    app.logger.info("   - /api/auth")
    app.logger.info("   - /api/community")
    app.logger.info("   - /api/assistant")
    app.logger.info("   - /api/test")
    app.logger.info("   - /api/chat")
    app.logger.info("   - /admin")


def register_core_routes(app):
    """Ana route'lar"""

    @app.route("/")
    def index():
        return jsonify({
            "name": "FriendZone API",
            "version": "2.0.0",
            "status": "online",
            "admin_panel": "/admin",
            "health_check": "/health"
        })

    @app.route("/health")
    def health_check():
        return jsonify({
            "status": "online",
            "environment": os.getenv("FLASK_ENV", "development"),
            "version": "2.0.0"
        }), 200


if __name__ == "__main__":
    app = create_app()
    port = int(os.getenv("PORT", 5000))
    host = os.getenv("HOST", "0.0.0.0")

    socketio.run(
        app,
        host=host,
        port=port,
        debug=True
    )