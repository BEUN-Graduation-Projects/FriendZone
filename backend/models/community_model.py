# backend/models/community_model.py

from backend import db
from datetime import datetime
from sqlalchemy import UniqueConstraint, Index
from sqlalchemy.orm import relationship
import logging

logger = logging.getLogger(__name__)


# ==================================================
# COMMUNITY
# ==================================================

class Community(db.Model):
    __tablename__ = "communities"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False, index=True)
    description = db.Column(db.Text)

    category = db.Column(db.String(50), index=True)
    tags = db.Column(db.JSON, nullable=True)

    compatibility_score = db.Column(db.Float, default=0.0, index=True)
    is_active = db.Column(db.Boolean, default=True, index=True)

    max_members = db.Column(db.Integer, default=10)

    created_by = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # ---------------------------
    # Relationships
    # ---------------------------

    members = relationship(
        "CommunityMember",
        back_populates="community",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    creator = relationship(
        "User",
        foreign_keys=[created_by],
        lazy="selectin"
    )

    # Mesaj ilişkisi - ChatMessage ile bağlantı
    messages = relationship(
        "ChatMessage",
        back_populates="community",
        cascade="all, delete-orphan",
        lazy="dynamic"
    )

    # ChatRoom ilişkisi - Her topluluğun bir chat odası olabilir
    chat_room = relationship(
        "ChatRoom",
        back_populates="community",
        uselist=False,  # One-to-One ilişki
        cascade="all, delete-orphan"
    )

    # ---------------------------
    # Business Logic
    # ---------------------------

    def add_member(self, user_id: int, role: str = "member"):
        """
        Topluluğa yeni üye ekler.
        Commit işlemi dışarıda yapılmalıdır.

        Args:
            user_id: Eklenecek kullanıcının ID'si
            role: Üye rolü (admin, moderator, member)

        Returns:
            CommunityMember: Oluşturulan üyelik nesnesi

        Raises:
            ValueError: Topluluk doluysa veya kullanıcı zaten üyeyse
        """
        if self.is_full:
            raise ValueError(f"Topluluk maksimum kapasiteye ulaştı. (Maks: {self.max_members})")

        existing = db.session.query(CommunityMember).filter_by(
            community_id=self.id,
            user_id=user_id
        ).first()

        if existing:
            if existing.is_active:
                raise ValueError("Kullanıcı zaten bu topluluğun aktif üyesi.")
            else:
                # Pasif üyeyi yeniden aktif et
                existing.is_active = True
                existing.role = role
                db.session.add(existing)
                logger.info(f"Kullanıcı {user_id} yeniden topluluğa eklendi: {self.name}")
                return existing

        new_member = CommunityMember(
            community_id=self.id,
            user_id=user_id,
            role=role
        )

        db.session.add(new_member)
        logger.info(f"Kullanıcı {user_id} topluluğa eklendi: {self.name}")
        return new_member

    def remove_member(self, user_id: int, hard_delete: bool = False) -> bool:
        """
        Üyeyi topluluktan çıkarır.

        Args:
            user_id: Çıkarılacak kullanıcının ID'si
            hard_delete: True ise veritabanından siler, False ise pasif yapar

        Returns:
            bool: İşlem başarılı mı?
        """
        member = db.session.query(CommunityMember).filter_by(
            community_id=self.id,
            user_id=user_id
        ).first()

        if not member:
            logger.warning(f"Kullanıcı {user_id} toplulukta bulunamadı: {self.name}")
            return False

        if hard_delete:
            db.session.delete(member)
            logger.info(f"Kullanıcı {user_id} topluluktan kalıcı olarak silindi: {self.name}")
        else:
            member.is_active = False
            db.session.add(member)
            logger.info(f"Kullanıcı {user_id} topluluktan çıkarıldı: {self.name}")

        return True

    def update_compatibility_score(self, score: float):
        """Topluluk uyumluluk skorunu günceller"""
        self.compatibility_score = float(score)
        self.updated_at = datetime.utcnow()
        logger.info(f"Topluluk {self.name} uyumluluk skoru güncellendi: {score}")

    def get_online_members(self):
        """Çevrimiçi üyeleri getirir"""
        from backend.models.chat_room_model import ChatUserStatus

        online_users = []
        for member in self.members:
            if member.is_active:
                status = ChatUserStatus.query.filter_by(
                    user_id=member.user_id,
                    is_online=True
                ).first()
                if status:
                    online_users.append({
                        "user_id": member.user_id,
                        "name": member.user.name if member.user else "Unknown",
                        "last_seen": status.last_seen
                    })
        return online_users

    def get_or_create_chat_room(self):
        """Topluluğun chat odasını getirir, yoksa oluşturur"""
        from backend.models.chat_room_model import ChatRoom

        if self.chat_room:
            return self.chat_room

        # Chat odası yoksa oluştur
        room = ChatRoom.create_for_community(
            community_id=self.id,
            community_name=self.name,
            max_members=self.max_members * 2  # Chat odası kapasitesi topluluk kapasitesinin 2 katı
        )
        logger.info(f"Topluluk için yeni chat odası oluşturuldu: {self.name}")
        return room

    def get_member_count_by_role(self, role: str) -> int:
        """Belirli roldeki üye sayısını döndürür"""
        return len([m for m in self.members if m.role == role and m.is_active])

    # ---------------------------
    # Properties
    # ---------------------------

    @property
    def current_member_count(self) -> int:
        """Aktif üye sayısı"""
        return len([m for m in self.members if m.is_active])

    @property
    def is_full(self) -> bool:
        """Topluluk dolu mu?"""
        return self.current_member_count >= self.max_members

    @property
    def available_slots(self) -> int:
        """Boş kontenjan sayısı"""
        return max(0, self.max_members - self.current_member_count)

    @property
    def total_messages_count(self) -> int:
        """Topluluktaki toplam mesaj sayısı"""
        return self.messages.count()

    # ---------------------------
    # Serialization
    # ---------------------------

    def to_dict(self, include_members: bool = False, include_stats: bool = False):
        """
        Topluluk bilgilerini dictionary olarak döndürür

        Args:
            include_members: Üye listesini dahil et
            include_stats: İstatistikleri dahil et
        """
        data = {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "tags": self.tags or [],
            "compatibility_score": self.compatibility_score,
            "max_members": self.max_members,
            "current_member_count": self.current_member_count,
            "available_slots": self.available_slots,
            "is_full": self.is_full,
            "is_active": self.is_active,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

        if include_members:
            data["members"] = [
                m.to_dict(include_user=True)
                for m in self.members
                if m.is_active
            ]

        if include_stats:
            data["stats"] = {
                "total_messages": self.total_messages_count,
                "online_members": len(self.get_online_members()),
                "roles_distribution": {
                    "admin": self.get_member_count_by_role("admin"),
                    "moderator": self.get_member_count_by_role("moderator"),
                    "member": self.get_member_count_by_role("member")
                },
                "has_chat_room": self.chat_room is not None
            }

        return data

    # ---------------------------
    # Query Helpers
    # ---------------------------

    @classmethod
    def active_by_category(cls, category: str):
        """Kategoriye göre aktif toplulukları getir"""
        return cls.query.filter_by(
            category=category,
            is_active=True
        ).all()

    @classmethod
    def recommended(cls, limit: int = 5):
        """Uyumluluk skoruna göre önerilen topluluklar"""
        return (
            cls.query
            .filter_by(is_active=True)
            .order_by(cls.compatibility_score.desc())
            .limit(limit)
            .all()
        )

    @classmethod
    def search_by_name(cls, query: str, limit: int = 10):
        """İsimle topluluk ara"""
        return cls.query.filter(
            cls.name.ilike(f'%{query}%'),
            cls.is_active == True
        ).limit(limit).all()

    @classmethod
    def get_communities_for_user(cls, user_id: int):
        """Kullanıcının üye olduğu toplulukları getir"""
        from backend.models.community_model import CommunityMember

        member_communities = db.session.query(CommunityMember.community_id).filter_by(
            user_id=user_id,
            is_active=True
        ).subquery()

        return cls.query.filter(cls.id.in_(member_communities)).all()

    def __repr__(self):
        return f"<Community {self.id} | {self.name}>"


# ==================================================
# COMMUNITY MEMBER (JOIN TABLE)
# ==================================================

class CommunityMember(db.Model):
    __tablename__ = "community_members"

    __table_args__ = (
        UniqueConstraint("community_id", "user_id", name="uq_community_user"),
        Index("idx_community_user", "community_id", "user_id"),
    )

    id = db.Column(db.Integer, primary_key=True)

    community_id = db.Column(
        db.Integer,
        db.ForeignKey("communities.id", ondelete="CASCADE"),
        nullable=False
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    role = db.Column(db.String(20), default="member", index=True)  # admin, moderator, member
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True, index=True)

    # Ek bilgiler (opsiyonel)
    last_active = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    message_count = db.Column(db.Integer, default=0)

    # Relationships
    community = relationship("Community", back_populates="members")
    user = relationship("User", back_populates="communities", lazy="selectin")

    def update_last_active(self):
        """Son aktif zamanını güncelle"""
        self.last_active = datetime.utcnow()

    def increment_message_count(self):
        """Mesaj sayısını artır"""
        self.message_count += 1
        self.update_last_active()

    def to_dict(self, include_user: bool = False):
        """Üyelik bilgilerini dictionary olarak döndür"""
        data = {
            "id": self.id,
            "community_id": self.community_id,
            "user_id": self.user_id,
            "role": self.role,
            "joined_at": self.joined_at.isoformat() if self.joined_at else None,
            "last_active": self.last_active.isoformat() if self.last_active else None,
            "is_active": self.is_active,
            "message_count": self.message_count
        }

        if include_user and self.user:
            data["user"] = self.user.to_dict()

        return data

    def __repr__(self):
        status = "active" if self.is_active else "inactive"
        return f"<CommunityMember u:{self.user_id} c:{self.community_id} ({self.role}, {status})>"