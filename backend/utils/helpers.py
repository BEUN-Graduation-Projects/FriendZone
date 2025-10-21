import json
from datetime import datetime
from backend import db


def json_serializer(obj):
    """JSON serialization için helper fonksiyon"""
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"{type(obj)} tipi serializable değil")


def to_dict(model_instance):
    """SQLAlchemy model instance'ını dictionary'e çevir"""
    if not model_instance:
        return None

    result = {}
    for column in model_instance.__table__.columns:
        value = getattr(model_instance, column.name)
        result[column.name] = value

    return result


def success_response(data=None, message="Başarılı", status_code=200):
    """Başarılı response formatı"""
    response = {
        "success": True,
        "message": message,
        "data": data,
        "timestamp": datetime.now().isoformat()
    }
    return response, status_code


def error_response(message="Bir hata oluştu", status_code=400, details=None):
    """Hata response formatı"""
    response = {
        "success": False,
        "message": message,
        "details": details,
        "timestamp": datetime.now().isoformat()
    }
    return response, status_code