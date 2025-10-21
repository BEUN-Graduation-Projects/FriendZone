from backend.app import db
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class UserSimilarity(db.Model):
    """Kullanıcı benzerlik modeli"""

    __tablename__ = 'user_similarities'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    similar_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    similarity_score = db.Column(db.Float, nullable=False)  # 0-1 arası benzerlik skoru

    # Benzerlik türü
    similarity_type = db.Column(db.String(20), default='overall')  # overall, personality, hobbies

    # Sistem bilgileri
    calculated_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    # İlişkiler
    user = db.relationship('User', foreign_keys=[user_id], back_populates='similarities')
    similar_user = db.relationship('User', foreign_keys=[similar_user_id])

    def __init__(self, user_id, similar_user_id, similarity_score, similarity_type='overall'):
        self.user_id = user_id
        self.similar_user_id = similar_user_id
        self.similarity_score = similarity_score
        self.similarity_type = similarity_type

    def to_dict(self):
        """Benzerlik bilgilerini dictionary formatında döndür"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'similar_user_id': self.similar_user_id,
            'similarity_score': self.similarity_score,
            'similarity_type': self.similarity_type,
            'calculated_at': self.calculated_at.isoformat() if self.calculated_at else None,
            'is_active': self.is_active,
            'similar_user': self.similar_user.to_dict() if self.similar_user else None
        }

    @classmethod
    def update_similarity(cls, user_id, similar_user_id, similarity_score, similarity_type='overall'):
        """Benzerlik skorunu güncelle veya oluştur"""
        # Mevcut benzerlik kaydını bul
        similarity = cls.query.filter_by(
            user_id=user_id,
            similar_user_id=similar_user_id,
            similarity_type=similarity_type
        ).first()

        if similarity:
            # Güncelle
            similarity.similarity_score = similarity_score
            similarity.calculated_at = datetime.utcnow()
        else:
            # Yeni oluştur
            similarity = cls(
                user_id=user_id,
                similar_user_id=similar_user_id,
                similarity_score=similarity_score,
                similarity_type=similarity_type
            )
            db.session.add(similarity)

        try:
            db.session.commit()
            logger.info(f"Benzerlik skoru güncellendi: {user_id} - {similar_user_id}")
            return similarity
        except Exception as e:
            db.session.rollback()
            logger.error(f"Benzerlik güncelleme hatası: {str(e)}")
            return None

    @classmethod
    def get_similar_users(cls, user_id, similarity_type='overall', limit=10, min_score=0.5):
        """Kullanıcının benzer kullanıcılarını getir"""
        similarities = cls.query.filter(
            cls.user_id == user_id,
            cls.similarity_type == similarity_type,
            cls.similarity_score >= min_score,
            cls.is_active == True
        ).order_by(cls.similarity_score.desc()).limit(limit).all()

        return similarities

    @classmethod
    def calculate_and_store_similarities(cls, user_id, ml_engine):
        """ML motoru kullanarak benzerlikleri hesapla ve sakla"""
        from backend.models.user_model import User

        user = User.query.get(user_id)
        if not user or not user.is_test_completed:
            return []

        # Tüm testi tamamlamış kullanıcıları getir
        all_users = User.get_users_with_test_results()

        similarities = []
        for other_user in all_users:
            if other_user.id == user_id:
                continue

            # Benzerlik skorunu hesapla
            similarity_score = ml_engine.calculate_similarity(
                user.to_dict(),
                other_user.to_dict()
            )

            if similarity_score > 0.3:  # Minimum eşik
                # Benzerlik kaydını oluştur/güncelle
                similarity = cls.update_similarity(
                    user_id,
                    other_user.id,
                    similarity_score
                )

                if similarity:
                    similarities.append(similarity)

        logger.info(f"{user_id} için {len(similarities)} benzerlik kaydı oluşturuldu")
        return similarities

    @classmethod
    def clear_old_similarities(cls, user_id=None, days_old=7):
        """Eski benzerlik kayıtlarını temizle"""
        from datetime import timedelta

        cutoff_date = datetime.utcnow() - timedelta(days=days_old)

        query = cls.query.filter(cls.calculated_at < cutoff_date)
        if user_id:
            query = query.filter(
                (cls.user_id == user_id) | (cls.similar_user_id == user_id)
            )

        deleted_count = query.delete()

        try:
            db.session.commit()
            logger.info(f"{deleted_count} eski benzerlik kaydı silindi")
            return deleted_count
        except Exception as e:
            db.session.rollback()
            logger.error(f"Eski benzerlikleri temizleme hatası: {str(e)}")
            return 0

    def __repr__(self):
        return f'<UserSimilarity {self.user_id}-{self.similar_user_id}: {self.similarity_score}>'