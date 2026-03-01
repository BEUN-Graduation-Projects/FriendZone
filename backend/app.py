# backend/app.py

import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, jsonify
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

    # Flask template ve static klasörleri
    TEMPLATE_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
    STATIC_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')


def create_app(config_class=Config):
    """Gelişmiş Application Factory - FriendZone ana uygulama oluşturucu"""

    app = Flask(__name__,
                template_folder=config_class.TEMPLATE_FOLDER,
                static_folder=config_class.STATIC_FOLDER)
    app.config.from_object(config_class)

    # Logging Yapılandırması
    configure_logging(app)

    # Extensions Init
    initialize_extensions(app)

    # Blueprint ve Hata Yönetimi
    register_blueprints(app)
    register_error_handlers(app)
    register_core_routes(app)

    # Socket.IO olaylarını içe aktar (circular import'u önlemek için burada yap)
    try:
        from backend import socket_events
        app.logger.info("✅ Socket.IO olayları yüklendi")
    except ImportError as e:
        app.logger.warning(f"⚠️ Socket.IO olayları yüklenemedi: {e}")

    # Veritabanı tablolarını oluştur (sadece development ortamında)
    with app.app_context():
        try:
            if app.config.get("ENV") == "development":
                db.create_all()
                app.logger.info("✅ Development ortamında tablolar oluşturuldu.")

                # Test verilerini kontrol et
                from backend.models.user_model import User
                if User.query.count() == 0:
                    app.logger.info("📝 Test verileri ekleniyor...")
                    try:
                        from backend.database.seed_data import seed_database
                        seed_database(app)
                        app.logger.info("✅ Test verileri eklendi")
                    except ImportError:
                        app.logger.warning("⚠️ Seed verileri bulunamadı")
        except Exception as e:
            app.logger.error(f"❌ Veritabanı başlatma hatası: {e}")

    app.logger.info("✅ FriendZone uygulaması başarıyla başlatıldı")
    return app


def initialize_extensions(app):
    """Tüm Flask extension'larını başlat"""

    # Veritabanı
    db.init_app(app)
    migrate.init_app(app, db)

    # JWT (JSON Web Token)
    jwt.init_app(app)

    # CORS ayarları - production'da daha spesifik yapılmalı
    cors.init_app(
        app,
        resources={
            r"/api/*": {"origins": app.config.get("SOCKETIO_CORS_ALLOWED_ORIGINS")},
            r"/admin/*": {"origins": app.config.get("SOCKETIO_CORS_ALLOWED_ORIGINS")},
            r"/socket.io/*": {"origins": app.config.get("SOCKETIO_CORS_ALLOWED_ORIGINS")}
        },
        supports_credentials=True
    )

    # Socket.IO - CORS ayarları ile
    socketio.init_app(
        app,
        cors_allowed_origins=app.config.get("SOCKETIO_CORS_ALLOWED_ORIGINS"),
        logger=app.config.get("SOCKETIO_LOGGER"),
        engineio_logger=app.config.get("SOCKETIO_ENGINEIO_LOGGER"),
        async_mode='eventlet' if not app.debug else None,
        path='socket.io'
    )

    app.logger.info("✅ Extension'lar başlatıldı:")
    app.logger.info("   - Database (SQLAlchemy)")
    app.logger.info("   - Migrate")
    app.logger.info("   - JWT")
    app.logger.info("   - CORS")
    app.logger.info("   - Socket.IO")


def configure_logging(app):
    """Hataları dosyaya ve konsola logla - production-ready logging"""

    # Logs dizinini oluştur
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        os.mkdir(log_dir)
        app.logger.info(f"📁 Logs dizini oluşturuldu: {log_dir}")

    # Dosya handler - rotasyonlu
    file_handler = RotatingFileHandler(
        os.path.join(log_dir, 'friendzone.log'),
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=10
    )
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)

    # Konsol handler - development için
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))
    console_handler.setLevel(logging.DEBUG if app.debug else logging.INFO)

    # Root logger'a handler'ları ekle
    app.logger.addHandler(file_handler)
    app.logger.addHandler(console_handler)
    app.logger.setLevel(logging.DEBUG if app.debug else logging.INFO)

    # Werkzeug logger'ı da ayarla
    logging.getLogger('werkzeug').setLevel(logging.INFO)

    # Başlangıç log'u
    app.logger.info('🚀 FriendZone uygulaması başlatılıyor...')
    app.logger.info(f'🔧 Environment: {os.getenv("FLASK_ENV", "development")}')
    app.logger.info(f'🗄️  Database: {app.config["SQLALCHEMY_DATABASE_URI"]}')
    app.logger.info(f'📁 Template folder: {app.template_folder}')
    app.logger.info(f'📁 Static folder: {app.static_folder}')


def register_error_handlers(app):
    """Global hata yakalayıcılar - tüm hataları merkezi yönet"""

    @app.errorhandler(404)
    def not_found_error(error):
        app.logger.warning(f"404 - Sayfa bulunamadı: {error}")
        if request.path.startswith('/api/'):
            return jsonify({
                "success": False,
                "error": "Kaynak bulunamadı",
                "code": 404,
                "message": "İstediğiniz API endpoint'i mevcut değil"
            }), 404
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()  # Veritabanı işlemini geri al
        app.logger.error(f"500 - Sunucu hatası: {error}")
        if request.path.startswith('/api/'):
            return jsonify({
                "success": False,
                "error": "Sunucu hatası",
                "code": 500,
                "message": "Bir şeyler ters gitti. Lütfen daha sonra tekrar deneyin"
            }), 500
        return render_template('500.html'), 500

    @app.errorhandler(401)
    def unauthorized_error(error):
        app.logger.warning(f"401 - Yetkisiz erişim: {error}")
        if request.path.startswith('/api/'):
            return jsonify({
                "success": False,
                "error": "Yetkisiz erişim",
                "code": 401,
                "message": "Bu işlem için giriş yapmanız gerekiyor"
            }), 401
        return redirect(url_for('auth.login'))

    @app.errorhandler(403)
    def forbidden_error(error):
        app.logger.warning(f"403 - Yasaklı erişim: {error}")
        if request.path.startswith('/api/'):
            return jsonify({
                "success": False,
                "error": "Erişim yasak",
                "code": 403,
                "message": "Bu kaynağa erişim yetkiniz yok"
            }), 403
        return render_template('403.html'), 403

    @app.errorhandler(400)
    def bad_request_error(error):
        app.logger.warning(f"400 - Geçersiz istek: {error}")
        return jsonify({
            "success": False,
            "error": "Geçersiz istek",
            "code": 400,
            "message": "Lütfen gönderdiğiniz verileri kontrol edin"
        }), 400


def register_blueprints(app):
    """Tüm blueprint'leri uygulamaya kaydet - modüler yapı"""

    # Circular importları önlemek için yerel import
    try:
        from backend.routes.auth_routes import auth_bp
        app.register_blueprint(auth_bp, url_prefix="/api/auth")
        app.logger.info("   ✅ /api/auth - Kimlik doğrulama")
    except ImportError as e:
        app.logger.error(f"   ❌ Auth blueprint yüklenemedi: {e}")

    try:
        from backend.routes.community_routes import community_bp
        app.register_blueprint(community_bp, url_prefix="/api/community")
        app.logger.info("   ✅ /api/community - Topluluk yönetimi")
    except ImportError as e:
        app.logger.error(f"   ❌ Community blueprint yüklenemedi: {e}")

    try:
        from backend.routes.assistant_routes import assistant_bp
        app.register_blueprint(assistant_bp, url_prefix="/api/assistant")
        app.logger.info("   ✅ /api/assistant - GPT asistan")
    except ImportError as e:
        app.logger.error(f"   ❌ Assistant blueprint yüklenemedi: {e}")

    try:
        from backend.routes.test_routes import test_bp
        app.register_blueprint(test_bp, url_prefix="/api/test")
        app.logger.info("   ✅ /api/test - Test yönetimi")
    except ImportError as e:
        app.logger.error(f"   ❌ Test blueprint yüklenemedi: {e}")

    try:
        from backend.routes.chat_routes import chat_bp
        app.register_blueprint(chat_bp, url_prefix="/api/chat")
        app.logger.info("   ✅ /api/chat - Sohbet")
    except ImportError as e:
        app.logger.error(f"   ❌ Chat blueprint yüklenemedi: {e}")

    try:
        from backend.routes.admin_routes import admin_bp
        app.register_blueprint(admin_bp, url_prefix="/admin")
        app.logger.info("   ✅ /admin - Admin paneli")
    except ImportError as e:
        app.logger.warning(f"   ⚠️ Admin blueprint yüklenemedi: {e}")


def register_core_routes(app):
    """Ana uygulama route'ları - health check ve utility endpoint'leri"""

    @app.route("/")
    def index():
        """Ana sayfa - frontend'e yönlendir"""
        return jsonify({
            "name": "FriendZone API",
            "version": "2.0.0",
            "status": "online",
            "documentation": "/docs",
            "admin_panel": "/admin",
            "health_check": "/health"
        })

    @app.route("/health")
    def health_check():
        """Sistem sağlık kontrolü - monitoring için"""

        # Veritabanı bağlantısını test et
        db_status = "connected"
        try:
            db.session.execute("SELECT 1")
        except Exception as e:
            db_status = f"error: {str(e)}"
            app.logger.error(f"Veritabanı bağlantı hatası: {e}")

        # Socket.IO durumunu kontrol et
        socketio_status = "running" if socketio.async_mode else "initialized"

        return jsonify({
            "success": True,
            "status": "online",
            "environment": os.getenv("FLASK_ENV", "development"),
            "database": db_status,
            "socketio": socketio_status,
            "version": "2.0.0",
            "name": "FriendZone API",
            "timestamp": __import__('datetime').datetime.now().isoformat()
        }), 200

    @app.route("/info")
    def app_info():
        """Uygulama bilgileri"""
        return jsonify({
            "name": "FriendZone",
            "description": "Üniversite öğrencileri için AI destekli sosyal topluluk platformu",
            "version": "2.0.0",
            "author": "BEUN Graduation Projects",
            "repository": "https://github.com/BEUN-Graduation-Projects/FriendZone",
            "features": [
                "Kişilik testi",
                "Hobi eşleştirme",
                "AI destekli topluluk önerileri",
                "Sanal topluluk odaları",
                "Real-time sohbet",
                "GPT asistan",
                "Admin paneli"
            ],
            "technologies": ["Flask", "SQLAlchemy", "Socket.IO", "OpenAI", "scikit-learn"]
        })

    if app.debug:
        @app.route("/api/seed", methods=["POST"])
        def seed_data():
            """Test verilerini doldur - sadece development ortamında"""
            try:
                from backend.database.seed_data import seed_database
                result = seed_database(app)
                app.logger.info("🧪 Test verileri başarıyla eklendi")
                return jsonify({
                    "success": True,
                    "message": "Test verileri eklendi",
                    "details": result
                }), 200
            except Exception as e:
                app.logger.error(f"Seed hatası: {str(e)}")
                return jsonify({
                    "success": False,
                    "error": str(e),
                    "message": "Test verileri eklenirken hata oluştu"
                }), 500

        @app.route("/api/clear", methods=["POST"])
        def clear_data():
            """Veritabanını temizle - sadece development ortamında"""
            try:
                from backend.database.seed_data import clear_database
                clear_database(app)
                app.logger.info("🧹 Veritabanı temizlendi")
                return jsonify({
                    "success": True,
                    "message": "Veritabanı başarıyla temizlendi"
                }), 200
            except Exception as e:
                app.logger.error(f"Temizleme hatası: {str(e)}")
                return jsonify({
                    "success": False,
                    "error": str(e),
                    "message": "Veritabanı temizlenirken hata oluştu"
                }), 500


# Ana çalıştırma bloğu
if __name__ == "__main__":
    # Uygulamayı oluştur
    app = create_app()

    # Port ve host ayarları
    port = int(os.getenv("PORT", 5000))
    host = os.getenv("HOST", "0.0.0.0")
    debug = os.getenv("FLASK_ENV", "development") == "development"

    app.logger.info(f"🌐 Sunucu başlatılıyor: {host}:{port}")
    app.logger.info(f"🐛 Debug modu: {debug}")
    app.logger.info(f"📊 Admin panel: http://{host}:{port}/admin")

    try:
        if debug:
            # Development: Flask ile çalıştır
            app.logger.info("⚡ Development modunda Socket.IO ile çalıştırılıyor...")
            socketio.run(
                app,
                host=host,
                port=port,
                debug=True,
                allow_unsafe_werkzeug=True  # Werkzeug reloader için
            )
        else:
            # Production: Eventlet ile çalıştır
            app.logger.info("🚀 Production modunda Eventlet ile çalıştırılıyor...")
            socketio.run(
                app,
                host=host,
                port=port,
                debug=False
            )
    except KeyboardInterrupt:
        app.logger.info("👋 Sunucu durduruluyor...")
    except Exception as e:
        app.logger.error(f"❌ Sunucu başlatılamadı: {e}")