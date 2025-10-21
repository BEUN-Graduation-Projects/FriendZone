from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate
import os
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

# Global nesneleri oluştur
db = SQLAlchemy()
migrate = Migrate()


def create_app():
    """Flask uygulaması oluşturma fabrika fonksiyonu"""
    app = Flask(__name__)

    # Temel konfigürasyon
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'gizli-anahtar-geliştirme'
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or 'sqlite:///friendzone.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Extensions'ı başlat
    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app)  # Frontend-backend iletişimi için

    # Modelleri import et (db tanımlandıktan sonra)
    from backend.models import user_model, community_model, similarity_model

    # Route'ları içe aktar ve kaydet
    from backend.routes.auth_routes import auth_bp
    from backend.routes.test_routes import test_bp
    from backend.routes.community_routes import community_bp
    from backend.routes.assistant_routes import assistant_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(test_bp, url_prefix='/api/test')
    app.register_blueprint(community_bp, url_prefix='/api/community')
    app.register_blueprint(assistant_bp, url_prefix='/api/assistant')

    # Kök route - sağlık kontrolü
    @app.route('/')
    def health_check():
        return jsonify({
            "status": "healthy",
            "message": "FriendZone API çalışıyor",
            "version": "1.0.0"
        })

    # Seed endpoint (sadece geliştirme için)
    @app.route('/api/seed', methods=['POST'])
    def seed_data():
        from backend.database.seed_data import seed_database
        result = seed_database(app)
        return jsonify(result)

    return app


if __name__ == '__main__':
    app = create_app()

    # Veritabanını başlat
    from backend.database.db_connection import init_db

    init_db(app)

    # Geliştirme modunda debug
    if app.config.get('ENV') == 'development':
        app.debug = True

    # Uygulamayı başlat
    app.run(
        host=os.environ.get('HOST', '0.0.0.0'),
        port=int(os.environ.get('PORT', 5000)),
        debug=os.environ.get('DEBUG', False)
    )