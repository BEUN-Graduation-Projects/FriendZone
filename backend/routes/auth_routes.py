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

# Blueprint oluştur
auth_bp = Blueprint('auth', __name__)

# Basit bir secret key (production'da environment variable'dan alınmalı)
SECRET_KEY = "friendzone_secret_key_2023"


def hash_password(password):
    """Şifreyi hash'le"""
    return hashlib.sha256(password.encode()).hexdigest()


def generate_token(user_id):
    """JWT token oluştur"""
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

        # Validasyon
        errors = validate_user_data(data)
        if errors:
            return error_response("Validasyon hatası", 400, errors)

        # Email kontrolü
        if User.find_by_email(data['email']):
            return error_response("Bu email adresi zaten kayıtlı", 400)

        # Yeni kullanıcı oluştur
        new_user = User(
            name=data['name'].strip(),
            email=data['email'].lower().strip(),
            password_hash=hash_password(data['password']),
            university=data.get('university'),
            department=data.get('department'),
            year=data.get('year')
        )

        db.session.add(new_user)
        db.session.commit()

        # Token oluştur
        token = generate_token(new_user.id)

        logger.info(f"Yeni kullanıcı kaydoldu: {new_user.email}")

        return success_response({
            'user': new_user.to_dict(),
            'token': token
        }, "Kullanıcı başarıyla kaydedildi", 201)

    except Exception as e:
        db.session.rollback()
        logger.error(f"Kayıt hatası: {str(e)}")
        return error_response("Kayıt işlemi başarısız", 500)


@auth_bp.route('/login', methods=['POST'])
def login():
    """Kullanıcı giriş endpoint'i"""
    try:
        data = request.get_json()

        if not data or not data.get('email') or not data.get('password'):
            return error_response("Email ve şifre gereklidir", 400)

        # Kullanıcıyı bul
        user = User.find_by_email(data['email'].lower().strip())
        if not user or user.password_hash != hash_password(data['password']):
            return error_response("Geçersiz email veya şifre", 401)

        if not user.is_active:
            return error_response("Hesap askıya alınmış", 403)

        # Token oluştur
        token = generate_token(user.id)

        logger.info(f"Kullanıcı giriş yaptı: {user.email}")

        return success_response({
            'user': user.to_dict(),
            'token': token
        }, "Giriş başarılı")

    except Exception as e:
        logger.error(f"Giriş hatası: {str(e)}")
        return error_response("Giriş işlemi başarısız", 500)


@auth_bp.route('/profile', methods=['GET'])
def get_profile():
    """Kullanıcı profil bilgilerini getir"""
    try:
        # Basit token doğrulama (gerçek uygulamada daha güvenli yapılmalı)
        token = request.headers.get('Authorization')
        if not token or not token.startswith('Bearer '):
            return error_response("Token gereklidir", 401)

        token = token.split(' ')[1]

        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            user_id = payload['user_id']
        except jwt.ExpiredSignatureError:
            return error_response("Token süresi dolmuş", 401)
        except jwt.InvalidTokenError:
            return error_response("Geçersiz token", 401)

        user = User.query.get(user_id)
        if not user:
            return error_response("Kullanıcı bulunamadı", 404)

        return success_response({
            'user': user.to_dict()
        }, "Profil bilgileri getirildi")

    except Exception as e:
        logger.error(f"Profil getirme hatası: {str(e)}")
        return error_response("Profil bilgileri alınamadı", 500)


@auth_bp.route('/profile', methods=['PUT'])
def update_profile():
    """Kullanıcı profil bilgilerini güncelle"""
    try:
        # Token doğrulama
        token = request.headers.get('Authorization')
        if not token or not token.startswith('Bearer '):
            return error_response("Token gereklidir", 401)

        token = token.split(' ')[1]

        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            user_id = payload['user_id']
        except jwt.ExpiredSignatureError:
            return error_response("Token süresi dolmuş", 401)
        except jwt.InvalidTokenError:
            return error_response("Geçersiz token", 401)

        user = User.query.get(user_id)
        if not user:
            return error_response("Kullanıcı bulunamadı", 404)

        data = request.get_json()

        # Güncellenebilir alanlar
        updatable_fields = ['name', 'university', 'department', 'year']

        for field in updatable_fields:
            if field in data:
                setattr(user, field, data[field])

        db.session.commit()

        logger.info(f"Profil güncellendi: {user.email}")

        return success_response({
            'user': user.to_dict()
        }, "Profil başarıyla güncellendi")

    except Exception as e:
        db.session.rollback()
        logger.error(f"Profil güncelleme hatası: {str(e)}")
        return error_response("Profil güncellenemedi", 500)