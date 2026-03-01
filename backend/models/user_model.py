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
    # Relationships
    # --------------------------------------------------

    communities = relationship(
        "CommunityMember",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    similarities = relationship(
        "UserSimilarity",
        foreign_keys="UserSimilarity.user_id",
        back_populates="user",
        lazy="selectin"
    )

    # Chat ilişkileri
    messages = relationship(
        "ChatMessage",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="dynamic"
    )

    chat_status = relationship(
        "ChatUserStatus",
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
    # CRUD Operations (YENİ EKLENEN METODLAR)
    # --------------------------------------------------

    @classmethod
    def create_user(cls, user_data):
        """
        Yeni kullanıcı oluştur - transaction güvenli

        Args:
            user_data (dict): {
                'name': str,
                'email': str,
                'password': str,
                'university': str (opsiyonel),
                'department': str (opsiyonel),
                'year': int (opsiyonel)
            }

        Returns:
            User: Oluşturulan kullanıcı nesnesi

        Raises:
            ValueError: Email zaten kayıtlıysa
            Exception: Diğer hatalarda
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

    def save_test_results(self, personality_data=None, hobbies_data=None):
        """
        Test sonuçlarını kaydet - atomic transaction

        Args:
            personality_data (dict, optional): {
                'type': str (örn: 'analytical_introvert'),
                'scores': dict (kişilik skorları)
            }
            hobbies_data (list, optional): Hobi listesi (örn: ['programlama', 'müzik'])

        Returns:
            bool: İşlem başarılı mı?

        Raises:
            Exception: Hata durumunda
        """
        try:
            # Kişilik testi sonuçları
            if personality_data:
                self.personality_type = personality_data.get('type')
                self.personality_scores = personality_data.get('scores', {})
                logger.info(f"📊 Kişilik testi kaydedildi: {self.personality_type}")

            # Hobi sonuçları
            if hobbies_data is not None:
                # Hobileri listeye çevir (eğer string gelirse)
                if isinstance(hobbies_data, str):
                    try:
                        hobbies_data = json.loads(hobbies_data)
                    except:
                        hobbies_data = [h.strip() for h in hobbies_data.split(',')]

                self.hobbies = hobbies_data
                logger.info(f"🎯 Hobiler kaydedildi: {len(hobbies_data)} aktivite")

            # Test tamamlanma durumunu güncelle
            self.is_test_completed = bool(self.personality_type and self.hobbies)
            self.updated_at = datetime.utcnow()

            db.session.commit()

            status = "tamamlandı" if self.is_test_completed else "kısmi tamamlandı"
            logger.info(f"✅ Test sonuçları {status}: {self.email}")

            return True

        except Exception as e:
            db.session.rollback()
            logger.error(f"❌ Test kaydetme hatası: {str(e)}")
            raise

    def update_profile(self, profile_data):
        """
        Kullanıcı profilini güncelle

        Args:
            profile_data (dict): Güncellenecek alanlar

        Returns:
            bool: İşlem başarılı mı?
        """
        try:
            updatable_fields = ['name', 'university', 'department', 'year']

            for field in updatable_fields:
                if field in profile_data:
                    setattr(self, field, profile_data[field])

            self.updated_at = datetime.utcnow()
            db.session.commit()

            logger.info(f"✅ Profil güncellendi: {self.email}")
            return True

        except Exception as e:
            db.session.rollback()
            logger.error(f"❌ Profil güncelleme hatası: {str(e)}")
            raise

    # --------------------------------------------------
    # Business Logic
    # --------------------------------------------------

    def get_similar_users(self, limit=5):
        """
        Daha performanslı sorgu - benzer kullanıcıları getir
        """
        from backend.models.similarity_model import UserSimilarity

        similarities = (
            db.session.query(UserSimilarity)
            .filter(
                (UserSimilarity.user_id == self.id) |
                (UserSimilarity.similar_user_id == self.id)
            )
            .order_by(UserSimilarity.similarity_score.desc())
            .limit(limit)
            .all()
        )

        similar_users = []

        for sim in similarities:
            other_user_id = (
                sim.similar_user_id
                if sim.user_id == self.id
                else sim.user_id
            )

            similar_user = db.session.get(User, other_user_id)

            if similar_user and similar_user.id != self.id:
                similar_users.append({
                    "user": similar_user.to_dict(),
                    "similarity_score": sim.similarity_score
                })

        return similar_users

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

    def is_online(self):
        """Kullanıcının çevrimiçi olup olmadığını kontrol et"""
        from backend.models.chat_room_model import ChatUserStatus

        latest_status = self.chat_status.filter_by(is_online=True).first()
        return latest_status is not None

    # --------------------------------------------------
    # Serialization
    # --------------------------------------------------

    def to_dict(self, include_sensitive=False):
        """
        Kullanıcı bilgilerini dictionary formatında döndür

        Args:
            include_sensitive (bool): Hassas bilgileri dahil et (şifre hariç)
        """
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
            "is_online": self.is_online(),
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

    # --------------------------------------------------
    # Class Methods
    # --------------------------------------------------

    @classmethod
    def find_by_email(cls, email: str):
        """Email ile kullanıcı bul"""
        return cls.query.filter_by(email=email.lower().strip()).first()

    @classmethod
    def find_by_id(cls, user_id: int):
        """ID ile kullanıcı bul"""
        return cls.query.get(user_id)

    @classmethod
    def get_active_test_users(cls):
        """Testi tamamlamış aktif kullanıcıları getir"""
        return cls.query.filter_by(
            is_test_completed=True,
            is_active=True
        ).all()

    @classmethod
    def search_by_name(cls, query: str, limit: int = 10):
        """İsimle kullanıcı ara"""
        return cls.query.filter(
            cls.name.ilike(f'%{query}%'),
            cls.is_active == True
        ).limit(limit).all()

    # --------------------------------------------------
    # Representation
    # --------------------------------------------------

    def __repr__(self):
        return f"<User {self.id} | {self.email}>"