# backend/models/user_model.py

from backend.app import db
from datetime import datetime
from sqlalchemy.orm import relationship
from sqlalchemy import Index
from werkzeug.security import generate_password_hash, check_password_hash
import logging
import json

logger = logging.getLogger(__name__)


class User(db.Model):
    """
    Production-ready User modeli
    """

    __tablename__ = "users"

    # --------------------------------------------------
    # Columns
    # --------------------------------------------------

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)

    university = db.Column(db.String(100), index=True)
    department = db.Column(db.String(100))
    year = db.Column(db.Integer)

    # Personality
    personality_type = db.Column(db.String(50), index=True)
    personality_scores = db.Column(db.JSON, nullable=True)

    # Hobbies
    hobbies = db.Column(db.JSON, nullable=True)

    # System
    is_test_completed = db.Column(db.Boolean, default=False, index=True)
    is_active = db.Column(db.Boolean, default=True, index=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # --------------------------------------------------
    # Relationships - DİKKAT: Burada class isimleri STRING olmalı!
    # --------------------------------------------------

    communities = relationship(
        "CommunityMember",  # String olarak yaz!
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    similarities = relationship(
        "UserSimilarity",  # String olarak yaz!
        foreign_keys="UserSimilarity.user_id",
        back_populates="user",
        lazy="selectin"
    )

    # Chat ilişkileri
    messages = relationship(
        "ChatMessage",  # String olarak yaz!
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="dynamic"
    )

    chat_statuses = relationship(
        "ChatUserStatus",  # String olarak yaz!
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="dynamic"
    )

    # --------------------------------------------------
    # Constructor
    # --------------------------------------------------

    def __init__(self, name, email, password, **kwargs):
        self.name = name
        self.email = email.lower().strip()
        self.set_password(password)

        self.university = kwargs.get("university")
        self.department = kwargs.get("department")
        self.year = kwargs.get("year")
        self.personality_type = kwargs.get("personality_type")
        self.personality_scores = kwargs.get("personality_scores")
        self.hobbies = kwargs.get("hobbies")

    # --------------------------------------------------
    # Password Methods
    # --------------------------------------------------

    def set_password(self, raw_password: str):
        self.password_hash = generate_password_hash(raw_password)

    def check_password(self, raw_password: str) -> bool:
        return check_password_hash(self.password_hash, raw_password)

    # --------------------------------------------------
    # CRUD Operations
    # --------------------------------------------------

    @classmethod
    def create_user(cls, user_data):
        """
        Yeni kullanıcı oluştur - transaction güvenli
        """
        try:
            # Email benzersizlik kontrolü
            existing_user = cls.query.filter_by(email=user_data['email'].lower().strip()).first()
            if existing_user:
                raise ValueError("Bu email adresi zaten kayıtlı")

            # Yeni kullanıcı oluştur
            user = cls(
                name=user_data['name'].strip(),
                email=user_data['email'].lower().strip(),
                password=user_data['password'],
                university=user_data.get('university'),
                department=user_data.get('department'),
                year=user_data.get('year')
            )

            db.session.add(user)
            db.session.commit()

            logger.info(f"✅ Yeni kullanıcı oluşturuldu: {user.email} (ID: {user.id})")
            return user

        except ValueError as e:
            db.session.rollback()
            logger.warning(f"⚠️ Kullanıcı oluşturma hatası (validasyon): {str(e)}")
            raise
        except Exception as e:
            db.session.rollback()
            logger.error(f"❌ Kullanıcı oluşturma hatası: {str(e)}")
            raise

    # --------------------------------------------------
    # Business Logic
    # --------------------------------------------------

    def get_hobbies_list(self):
        """Hobileri liste olarak döndür"""
        if not self.hobbies:
            return []

        if isinstance(self.hobbies, str):
            try:
                return json.loads(self.hobbies)
            except:
                return [h.strip() for h in self.hobbies.split(',')]

        return self.hobbies

    def to_dict(self, include_sensitive=False):
        """Kullanıcı bilgilerini dictionary formatında döndür"""
        data = {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "university": self.university,
            "department": self.department,
            "year": self.year,
            "personality_type": self.personality_type,
            "personality_scores": self.personality_scores or {},
            "hobbies": self.get_hobbies_list(),
            "is_test_completed": self.is_test_completed,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

        if include_sensitive:
            # Community ve similarity bilgileri
            data["communities"] = [
                {
                    "id": m.community.id,
                    "name": m.community.name,
                    "role": m.role
                }
                for m in self.communities if m.is_active
            ]

        return data

    @classmethod
    def find_by_email(cls, email: str):
        """Email ile kullanıcı bul"""
        return cls.query.filter_by(email=email.lower().strip()).first()

    def __repr__(self):
        return f"<User {self.id} | {self.email}>"