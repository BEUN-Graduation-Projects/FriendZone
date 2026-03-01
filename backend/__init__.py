# backend/__init__.py

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_socketio import SocketIO
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize extensions (SINGLETON pattern - TEK bir noktada tanımla)
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
cors = CORS()
socketio = SocketIO()


def create_app(config_object=None):
    """Application factory pattern"""
    app = Flask(__name__,
                template_folder='templates',
                static_folder='static')

    # Load config
    if config_object:
        app.config.from_object(config_object)
    else:
        app.config.from_mapping(
            SECRET_KEY=os.getenv('SECRET_KEY', 'dev-key'),
            SQLALCHEMY_DATABASE_URI=os.getenv('DATABASE_URL', 'sqlite:///friendzone.db'),
            SQLALCHEMY_TRACK_MODIFICATIONS=False,
            JWT_SECRET_KEY=os.getenv('JWT_SECRET_KEY', 'jwt-dev-key')
        )

    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cors.init_app(app)
    socketio.init_app(app, cors_allowed_origins="*")

    # Register blueprints (import işlemlerini burada yap!)
    with app.app_context():
        # Auth routes
        try:
            from backend.routes.auth_routes import auth_bp
            app.register_blueprint(auth_bp, url_prefix='/api/auth')
            app.logger.info("✅ /api/auth - Kimlik doğrulama")
        except Exception as e:
            app.logger.error(f"❌ Auth blueprint yüklenemedi: {e}")

        # Community routes
        try:
            from backend.routes.community_routes import community_bp
            app.register_blueprint(community_bp, url_prefix='/api/community')
            app.logger.info("✅ /api/community - Topluluk yönetimi")
        except Exception as e:
            app.logger.error(f"❌ Community blueprint yüklenemedi: {e}")

        # Assistant routes
        try:
            from backend.routes.assistant_routes import assistant_bp
            app.register_blueprint(assistant_bp, url_prefix='/api/assistant')
            app.logger.info("✅ /api/assistant - GPT asistan")
        except Exception as e:
            app.logger.error(f"❌ Assistant blueprint yüklenemedi: {e}")

        # Test routes
        try:
            from backend.routes.test_routes import test_bp
            app.register_blueprint(test_bp, url_prefix='/api/test')
            app.logger.info("✅ /api/test - Test yönetimi")
        except Exception as e:
            app.logger.error(f"❌ Test blueprint yüklenemedi: {e}")

        # Chat routes
        try:
            from backend.routes.chat_routes import chat_bp
            app.register_blueprint(chat_bp, url_prefix='/api/chat')
            app.logger.info("✅ /api/chat - Sohbet")
        except Exception as e:
            app.logger.error(f"❌ Chat blueprint yüklenemedi: {e}")

        # Admin routes
        try:
            from backend.routes.admin_routes import admin_bp
            app.register_blueprint(admin_bp, url_prefix='/admin')
            app.logger.info("✅ /admin - Admin paneli")
        except Exception as e:
            app.logger.warning(f"⚠️ Admin blueprint yüklenemedi: {e}")

    return app