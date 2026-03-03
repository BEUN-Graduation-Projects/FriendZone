# backend/routes/auth_routes.py

from flask import Blueprint, request, jsonify
from backend.models.user_model import User
from backend.app import db
import hashlib
import jwt
import datetime
from backend.utils.helpers import success_response, error_response
from backend.utils.validators import validate_user_data
import logging

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__)
SECRET_KEY = "friendzone_secret_key_2023"


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def generate_token(user_id):
    payload = {
        'user_id': user_id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')


@auth_bp.route('/register', methods=['POST'])
def register():
    """Kullanıcı kayıt endpoint'i"""
    try:
        data = request.get_json()
        print("📝 Kayıt verisi:", data)  # Debug için

        # Validasyon
        if not data.get('name') or not data.get('email') or not data.get('password'):
            return error_response("İsim, email ve şifre gereklidir", 400)

        # Email kontrolü
        if User.query.filter_by(email=data['email'].lower().strip()).first():
            return error_response("Bu email adresi zaten kayıtlı", 400)

        # Yeni kullanıcı oluştur - User modelinin create_user metodunu kullan
        new_user = User(
            name=data['name'].strip(),
            email=data['email'].lower().strip(),
            password=data['password']
        )

        db.session.add(new_user)
        db.session.commit()

        print(f"✅ Yeni kullanıcı oluşturuldu: {new_user.email} (ID: {new_user.id})")

        # Token oluştur
        token = generate_token(new_user.id)

        return success_response({
            'user': new_user.to_dict(),
            'token': token
        }, "Kullanıcı başarıyla kaydedildi", 201)

    except Exception as e:
        db.session.rollback()
        print(f"❌ Kayıt hatası: {str(e)}")
        import traceback
        traceback.print_exc()
        return error_response(f"Kayıt işlemi başarısız: {str(e)}", 500)