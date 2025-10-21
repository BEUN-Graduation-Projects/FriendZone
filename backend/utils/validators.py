import re
from backend.utils.helpers import error_response


def validate_email(email):
    """Email validasyonu"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_password(password):
    """Şifre validasyonu (en az 6 karakter)"""
    return len(password) >= 6


def validate_user_data(user_data):
    """Kullanıcı verisi validasyonu"""
    errors = []

    if not user_data.get('name') or len(user_data['name'].strip()) < 2:
        errors.append("İsim en az 2 karakter olmalıdır")

    if not user_data.get('email') or not validate_email(user_data['email']):
        errors.append("Geçerli bir email adresi giriniz")

    if not user_data.get('password') or not validate_password(user_data['password']):
        errors.append("Şifre en az 6 karakter olmalıdır")

    return errors