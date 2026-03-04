# backend/models/chat_room_model.py

from backend.app import db
from datetime import datetime
from sqlalchemy import Index, UniqueConstraint

class ChatRoom(db.Model):
    """Sanal topluluk sohbet odası"""
    __tablename__ = 'chat_rooms'

    id = db.Column(db.Integer, primary_key=True)
    community_id = db.Column(db.Integer, db.ForeignKey('communities.id'), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)

    # Oda özellikleri
    description = db.Column(db.String(200), nullable=True)
    is_active = db.Column(db.Boolean, default=True, index=True)
    is_private = db.Column(db.Boolean, default=False)

    # Kapasite ve kısıtlamalar
    max_members = db.Column(db.Integer, default=50)
    current_members = db.Column(db.Integer, default=0)

    # Oda ayarları (JSON olarak sakla)
    settings = db.Column(db.JSON, default={
        'allow_files': True,
        'allow_links': True,
        'slow_mode': False,
        'slow_mode_interval': 0,
        'language': 'tr',
        'auto_delete': False,
        'auto_delete_days': 30
    })

    # Zaman damgaları
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_activity = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    # ---------------------------
    # Relationships - DİKKAT: Burada backref KULLANMA!
    # ---------------------------
    community = db.relationship(
        "Community",
        back_populates="chat_room",  # backref değil, back_populates!
        uselist=False
    )

    messages = db.relationship(
        "ChatMessage",
        back_populates="room",  # backref değil, back_populates!
        lazy="dynamic",
        cascade="all, delete-orphan",
        foreign_keys="[ChatMessage.room_id]"  # Hangi foreign key'i kullanacağını belirt
    )

    online_users = db.relationship(
        "ChatUserStatus",
        back_populates="room",
        lazy="dynamic",
        cascade="all, delete-orphan"
    )

    def __init__(self, community_id, name, **kwargs):
        self.community_id = community_id
        self.name = name
        self.description = kwargs.get('description', '')
        self.is_private = kwargs.get('is_private', False)
        self.max_members = kwargs.get('max_members', 50)
        if 'settings' in kwargs:
            self.settings.update(kwargs['settings'])

    @classmethod
    def create_for_community(cls, community_id, community_name, **kwargs):
        """Topluluk için sohbet odası oluştur"""
        room_name = kwargs.get('room_name', f"{community_name} Sohbet Odası")

        room = cls(
            community_id=community_id,
            name=room_name,
            description=kwargs.get('description', f"{community_name} topluluğunun resmi sohbet odası"),
            is_private=kwargs.get('is_private', False),
            max_members=kwargs.get('max_members', 50),
            settings=kwargs.get('settings', {})
        )

        db.session.add(room)
        db.session.commit()

        return room

    def get_online_users(self):
        """Çevrimiçi kullanıcıları getir"""
        return self.online_users.filter_by(is_online=True).all()

    def get_online_count(self):
        """Çevrimiçi kullanıcı sayısını getir"""
        return self.online_users.filter_by(is_online=True).count()

    def get_recent_messages(self, limit=50):
        """Son mesajları getir"""
        return self.messages.order_by(ChatMessage.timestamp.desc()).limit(limit).all()

    def update_activity(self):
        """Son aktivite zamanını güncelle"""
        self.last_activity = datetime.utcnow()
        db.session.commit()

    def update_member_count(self):
        """Üye sayısını güncelle"""
        self.current_members = self.online_users.filter_by(is_online=True).count()
        db.session.commit()

    def to_dict(self):
        """API yanıtları için dictionary dönüşümü"""
        return {
            'id': self.id,
            'community_id': self.community_id,
            'community_name': self.community.name if self.community else None,
            'name': self.name,
            'description': self.description,
            'is_active': self.is_active,
            'is_private': self.is_private,
            'max_members': self.max_members,
            'current_members': self.current_members,
            'online_count': self.get_online_count(),
            'settings': self.settings,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_activity': self.last_activity.isoformat() if self.last_activity else None
        }

    def __repr__(self):
        return f"<ChatRoom {self.id} | {self.name}>"


class ChatUserStatus(db.Model):
    """Kullanıcıların çevrimiçi durumu"""
    __tablename__ = 'chat_user_status'

    __table_args__ = (
        UniqueConstraint('user_id', 'room_id', name='uq_user_room'),
        Index('idx_user_room_status', 'user_id', 'room_id', 'is_online'),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('chat_rooms.id'), nullable=False)

    # Durum bilgileri
    is_online = db.Column(db.Boolean, default=False, index=True)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, index=True)
    socket_id = db.Column(db.String(100), nullable=True)

    # İstatistikler
    total_messages = db.Column(db.Integer, default=0)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_message_at = db.Column(db.DateTime, nullable=True)

    # Relationships - back_populates kullan!
    user = db.relationship("User", back_populates="chat_statuses")
    room = db.relationship("ChatRoom", back_populates="online_users")

    def __init__(self, user_id, room_id, **kwargs):
        self.user_id = user_id
        self.room_id = room_id
        self.socket_id = kwargs.get('socket_id')
        self.is_online = kwargs.get('is_online', True)

    @classmethod
    def update_status(cls, user_id, room_id, is_online, socket_id=None):
        """Kullanıcı durumunu güncelle"""
        status = cls.query.filter_by(user_id=user_id, room_id=room_id).first()

        if not status:
            status = cls(user_id=user_id, room_id=room_id)
            db.session.add(status)

        old_status = status.is_online
        status.is_online = is_online
        status.last_seen = datetime.utcnow()
        if socket_id:
            status.socket_id = socket_id

        db.session.commit()

        # Eğer durum değiştiyse ve online ise, oda aktivitesini güncelle
        if old_status != is_online:
            room = ChatRoom.query.get(room_id)
            if room:
                room.update_member_count()
                if is_online:
                    room.update_activity()

        return status

    @classmethod
    def get_online_users_in_room(cls, room_id):
        """Odaki çevrimiçi kullanıcıları getir"""
        return cls.query.filter_by(room_id=room_id, is_online=True).all()

    @classmethod
    def disconnect_user(cls, user_id, socket_id=None):
        """Kullanıcının tüm bağlantılarını kapat"""
        query = cls.query.filter_by(user_id=user_id)
        if socket_id:
            query = query.filter_by(socket_id=socket_id)

        statuses = query.all()
        for status in statuses:
            status.is_online = False
            status.last_seen = datetime.utcnow()

        db.session.commit()

        # Etkilenen odaların member count'larını güncelle
        for status in statuses:
            room = ChatRoom.query.get(status.room_id)
            if room:
                room.update_member_count()

    def to_dict(self):
        """API yanıtları için dictionary dönüşümü"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'username': self.user.name if self.user else None,
            'room_id': self.room_id,
            'is_online': self.is_online,
            'last_seen': self.last_seen.isoformat() if self.last_seen else None,
            'total_messages': self.total_messages,
            'joined_at': self.joined_at.isoformat() if self.joined_at else None,
            'last_message_at': self.last_message_at.isoformat() if self.last_message_at else None
        }

    def __repr__(self):
        status = "online" if self.is_online else "offline"
        return f"<ChatUserStatus u:{self.user_id} r:{self.room_id} ({status})>"