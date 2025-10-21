from backend.app import db
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)


class Community(db.Model):
    """Topluluk modeli"""

    __tablename__ = 'communities'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50))  # technology, sports, arts, outdoor, education, social
    tags = db.Column(db.Text)  # JSON formatında etiket listesi

    # Topluluk özellikleri
    compatibility_score = db.Column(db.Float, default=0.0)  # Grup uyumluluk skoru
    is_active = db.Column(db.Boolean, default=True)
    max_members = db.Column(db.Integer, default=10)

    # Sistem bilgileri
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # İlişkiler
    members = db.relationship('CommunityMember', back_populates='community', cascade='all, delete-orphan')
    creator = db.relationship('User', foreign_keys=[created_by])

    def __init__(self, name, description=None, category='general', tags=None,
                 max_members=10, created_by=None):
        self.name = name
        self.description = description
        self.category = category
        self.tags = json.dumps(tags) if tags else '[]'
        self.max_members = max_members
        self.created_by = created_by

    def to_dict(self, include_members=False):
        """Topluluk bilgilerini dictionary formatında döndür"""
        data = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'tags': json.loads(self.tags) if self.tags else [],
            'compatibility_score': self.compatibility_score,
            'max_members': self.max_members,
            'current_member_count': len(self.members),
            'is_active': self.is_active,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

        if include_members:
            data['members'] = [member.to_dict() for member in self.members]

        return data

    def get_member_users(self):
        """Topluluk üyelerinin kullanıcı bilgilerini getir"""
        return [member.user for member in self.members]

    def add_member(self, user_id, role='member'):
        """Topluluğa üye ekle"""
        from backend.models.user_model import User

        # Kullanıcı var mı kontrol et
        user = User.query.get(user_id)
        if not user:
            raise ValueError("Kullanıcı bulunamadı")

        # Zaten üye mi kontrol et
        existing_member = CommunityMember.query.filter_by(
            community_id=self.id, user_id=user_id
        ).first()

        if existing_member:
            raise ValueError("Kullanıcı zaten bu topluluğun üyesi")

        # Maksimum üye sayısı kontrolü
        if len(self.members) >= self.max_members:
            raise ValueError("Topluluk maksimum üye sayısına ulaştı")

        # Yeni üye ekle
        new_member = CommunityMember(
            community_id=self.id,
            user_id=user_id,
            role=role,
            joined_at=datetime.utcnow()
        )

        db.session.add(new_member)

        try:
            db.session.commit()
            logger.info(f"Kullanıcı {user_id} topluluğa eklendi: {self.name}")
            return new_member
        except Exception as e:
            db.session.rollback()
            logger.error(f"Üye ekleme hatası: {str(e)}")
            raise

    def remove_member(self, user_id):
        """Topluluktan üye çıkar"""
        member = CommunityMember.query.filter_by(
            community_id=self.id, user_id=user_id
        ).first()

        if member:
            db.session.delete(member)

            try:
                db.session.commit()
                logger.info(f"Kullanıcı {user_id} topluluktan çıkarıldı: {self.name}")
                return True
            except Exception as e:
                db.session.rollback()
                logger.error(f"Üye çıkarma hatası: {str(e)}")
                return False

        return False

    def update_compatibility_score(self, score):
        """Uyumluluk skorunu güncelle"""
        self.compatibility_score = score
        self.updated_at = datetime.utcnow()

        try:
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"Uyumluluk skoru güncelleme hatası: {str(e)}")
            return False

    @classmethod
    def find_by_category(cls, category):
        """Kategoriye göre toplulukları bul"""
        return cls.query.filter_by(category=category, is_active=True).all()

    @classmethod
    def find_recommended_communities(cls, user_id, limit=5):
        """Kullanıcı için önerilen toplulukları bul"""
        # Bu metod daha sonra ML algoritması ile geliştirilecek
        return cls.query.filter_by(is_active=True).limit(limit).all()

    def __repr__(self):
        return f'<Community {self.name} ({self.category})>'


class CommunityMember(db.Model):
    """Topluluk üyeliği modeli (many-to-many ilişki)"""

    __tablename__ = 'community_members'

    id = db.Column(db.Integer, primary_key=True)
    community_id = db.Column(db.Integer, db.ForeignKey('communities.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    role = db.Column(db.String(20), default='member')  # member, admin, moderator
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    # İlişkiler
    community = db.relationship('Community', back_populates='members')
    user = db.relationship('User', back_populates='communities')

    def to_dict(self):
        """Üyelik bilgilerini dictionary formatında döndür"""
        return {
            'id': self.id,
            'community_id': self.community_id,
            'user_id': self.user_id,
            'role': self.role,
            'joined_at': self.joined_at.isoformat() if self.joined_at else None,
            'is_active': self.is_active,
            'user': self.user.to_dict() if self.user else None
        }

    def __repr__(self):
        return f'<CommunityMember user:{self.user_id} community:{self.community_id}>'