import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv

# .env yüklemesi en başta olmalı
load_dotenv()

# Extensions - Tek bir noktadan yönetilmeli
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
cors = CORS()


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "friendzone-super-secret")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///friendzone.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "jwt-secret-key")
    # Veritabanı bağlantı havuzu optimizasyonu
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_size": 10,
        "pool_recycle": 3600,
        "pool_pre_ping": True,
    }


def create_app(config_class=Config):
    """Gelişmiş Application Factory"""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Logging Yapılandırması
    configure_logging(app)

    # Extensions Init
    initialize_extensions(app)

    # Blueprint ve Hata Yönetimi
    register_blueprints(app)
    register_error_handlers(app)
    register_core_routes(app)

    return app


def initialize_extensions(app):
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    # CORS ayarlarını biraz daha spesifik hale getirebilirsin
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})


def configure_logging(app):
    """Hataları dosyaya ve konsola loglar"""
    if not os.path.exists('logs'):
        os.mkdir('logs')

    file_handler = RotatingFileHandler('logs/friendzone.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('FriendZone Startup')


def register_error_handlers(app):
    """Global Hata Yakalayıcılar"""

    @app.errorhandler(404)
    def not_found_error(error):
        return jsonify({"error": "Resource not found", "code": 404}), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        app.logger.error(f"Server Error: {error}")
        return jsonify({"error": "Internal server error", "code": 500}), 500


def register_blueprints(app):
    # Circular importları önlemek için yerel import
    from backend.routes.auth_routes import auth_bp
    from backend.routes.community_routes import community_bp
    from backend.routes.assistant_routes import assistant_bp
    from backend.routes.test_routes import test_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(community_bp, url_prefix="/api/community")
    app.register_blueprint(assistant_bp, url_prefix="/api/assistant")
    app.register_blueprint(test_bp, url_prefix="/api/test")


def register_core_routes(app):
    @app.route("/health")
    def health_check():
        return jsonify({
            "status": "online",
            "environment": os.getenv("FLASK_ENV", "development"),
            "version": "1.1.0"
        }), 200

    if app.debug:
        @app.route("/api/seed", methods=["POST"])
        def seed_data():
            try:
                from backend.database.seed_data import seed_database
                seed_database()
                return jsonify({"message": "Database seeded successfully"}), 200
            except Exception as e:
                return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app = create_app()
    port = int(os.getenv("PORT", 5000))
    # Production'da app.run kullanılmaz (Gunicorn/UWSGI tercih edilir)
    app.run(host="0.0.0.0", port=port)