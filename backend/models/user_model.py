from backend.app import db
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)


class User(db.Model):
    """Kullanıcı modeli"""

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    university = db.Column(db.String(100))
    department = db.Column(db.String(100))
    year = db.Column(db.Integer)  # 1, 2, 3, 4

    # Kişilik testi sonuçları
    personality_type = db.Column(db.String(50))  # analytical_introvert, creative_extrovert vb.
    personality_scores = db.Column(db.Text)  # JSON formatında detaylı skorlar

    # Hobi bilgileri
    hobbies = db.Column(db.Text)  # JSON formatında hobi listesi

    # Sistem bilgileri
    is_test_completed = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # İlişkiler
    communities = db.relationship('CommunityMember', back_populates='user', cascade='all, delete-orphan')
    similarities = db.relationship('UserSimilarity', foreign_keys='UserSimilarity.user_id', back_populates='user')

    def __init__(self, name, email, password_hash, university=None, department=None, year=None,
                 personality_type=None, hobbies=None, personality_scores=None):
        self.name = name
        self.email = email
        self.password_hash = password_hash
        self.university = university
        self.department = department
        self.year = year
        self.personality_type = personality_type
        self.hobbies = json.dumps(hobbies) if hobbies else None
        self.personality_scores = json.dumps(personality_scores) if personality_scores else None

    def to_dict(self):
        """Kullanıcı bilgilerini dictionary formatında döndür"""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'university': self.university,
            'department': self.department,
            'year': self.year,
            'personality_type': self.personality_type,
            'hobbies': json.loads(self.hobbies) if self.hobbies else [],
            'personality_scores': json.loads(self.personality_scores) if self.personality_scores else {},
            'is_test_completed': self.is_test_completed,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def get_personality_vector(self):
        """Kişilik skorlarını vektör formatında döndür"""
        if not self.personality_scores:
            return {}
        return json.loads(self.personality_scores)

    def get_hobbies_list(self):
        """Hobi listesini döndür"""
        if not self.hobbies:
            return []
        return json.loads(self.hobbies)

    def update_test_results(self, personality_type, personality_scores, hobbies):
        """Test sonuçlarını güncelle"""
        self.personality_type = personality_type
        self.personality_scores = json.dumps(personality_scores) if personality_scores else None
        self.hobbies = json.dumps(hobbies) if hobbies else None
        self.is_test_completed = True
        self.updated_at = datetime.utcnow()

        try:
            db.session.commit()
            logger.info(f"Kullanıcı test sonuçları güncellendi: {self.email}")
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"Test sonuçları güncelleme hatası: {str(e)}")
            return False

    def get_similar_users(self, limit=5):
        """Benzer kullanıcıları getir"""
        from backend.models.similarity_model import UserSimilarity

        similarities = UserSimilarity.query.filter(
            (UserSimilarity.user_id == self.id) | (UserSimilarity.similar_user_id == self.id)
        ).order_by(UserSimilarity.similarity_score.desc()).limit(limit).all()

        similar_users = []
        for sim in similarities:
            if sim.user_id == self.id:
                similar_user = User.query.get(sim.similar_user_id)
            else:
                similar_user = User.query.get(sim.user_id)

            if similar_user and similar_user.id != self.id:
                similar_users.append({
                    'user': similar_user.to_dict(),
                    'similarity_score': sim.similarity_score
                })

        return similar_users

    @classmethod
    def find_by_email(cls, email):
        """Email ile kullanıcı bul"""
        return cls.query.filter_by(email=email).first()

    @classmethod
    def get_users_with_test_results(cls):
        """Testi tamamlamış kullanıcıları getir"""
        return cls.query.filter_by(is_test_completed=True, is_active=True).all()

    def __repr__(self):
        return f'<User {self.name} ({self.email})>'