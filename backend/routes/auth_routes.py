# backend/routes/auth_routes.py

from flask import Blueprint, request, jsonify
from backend.models.user_model import User
from backend.app import db
import hashlib
import jwt
import datetime
from backend.utils.helpers import success_response, error_response
import logging

logger = logging.getLogger(__name__)

# BLUEPRINT TANIMI - BU SATIR ÇOK ÖNEMLİ!
auth_bp = Blueprint('auth', __name__)

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
        print(f"📝 Kayıt isteği alındı: {data}")

        # Validasyon
        if not data.get('name') or not data.get('email') or not data.get('password'):
            print("❌ Eksik alanlar var")
            return error_response("İsim, email ve şifre gereklidir", 400)

        # Email formatı kontrolü
        if not data['email'].endswith('.edu.tr'):
            print("❌ Email .edu.tr ile bitmiyor")
            return error_response("Sadece .edu.tr uzantılı email adresleri kabul edilir", 400)

        # Email kontrolü - zaten var mı?
        existing_user = User.query.filter_by(email=data['email'].lower().strip()).first()
        if existing_user:
            print(f"❌ Email zaten kayıtlı: {data['email']}")
            return error_response("Bu email adresi zaten kayıtlı", 400)

        new_user = User(
            name=data['name'].strip(),
            email=data['email'].lower().strip(),
            password=data['password'],
            university=data.get('university'),
            department=data.get('department'),
            year=data.get('year')
        )

        print(f"👤 Yeni kullanıcı oluşturuluyor: {new_user.email}")

        db.session.add(new_user)
        db.session.commit()

        print(f"✅ Kullanıcı veritabanına kaydedildi: ID: {new_user.id}")

        token = generate_token(new_user.id)

        return success_response({
            'user': new_user.to_dict(),
            'token': token
        }, "Kullanıcı başarıyla kaydedildi", 201)

    except Exception as e:
        db.session.rollback()
        print(f"❌ HATA: {str(e)}")
        import traceback
        traceback.print_exc()
        return error_response(f"Kayıt işlemi başarısız: {str(e)}", 500)

@auth_bp.route('/login', methods=['POST'])
def login():
    """Kullanıcı giriş endpoint'i"""
    try:
        data = request.get_json()
        print(f"📝 Giriş isteği alındı: {data.get('email')}")

        if not data or not data.get('email') or not data.get('password'):
            return error_response("Email ve şifre gereklidir", 400)

        # Kullanıcıyı bul
        user = User.query.filter_by(email=data['email'].lower().strip()).first()
        if not user:
            print(f"❌ Kullanıcı bulunamadı: {data['email']}")
            return error_response("Geçersiz email veya şifre", 401)

        if not user.check_password(data['password']):
            print(f"❌ Şifre yanlış: {data['email']}")
            return error_response("Geçersiz email veya şifre", 401)

        if not user.is_active:
            print(f"❌ Hesap pasif: {data['email']}")
            return error_response("Hesap askıya alınmış", 403)


        token = generate_token(user.id)

        print(f"✅ Giriş başarılı: {user.email}")

        return success_response({
            'user': user.to_dict(),
            'token': token
        }, "Giriş başarılı")

    except Exception as e:
        print(f"❌ HATA: {str(e)}")
        import traceback
        traceback.print_exc()
        return error_response("Giriş işlemi başarısız", 500)

@auth_bp.route('/profile', methods=['GET'])
def get_profile():
    """Kullanıcı profil bilgilerini getir"""
    try:
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
        print(f"❌ HATA: {str(e)}")
        return error_response("Profil bilgileri alınamadı", 500)

@auth_bp.route('/profile', methods=['PUT'])
def update_profile():
    """Kullanıcı profil bilgilerini güncelle"""
    try:
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


        updatable_fields = ['name', 'university', 'department', 'year']

        for field in updatable_fields:
            if field in data:
                setattr(user, field, data[field])

        db.session.commit()

        print(f"✅ Profil güncellendi: {user.email}")

        return success_response({
            'user': user.to_dict()
        }, "Profil başarıyla güncellendi")

    except Exception as e:
        db.session.rollback()
        print(f"❌ HATA: {str(e)}")
        return error_response("Profil güncellenemedi", 500)