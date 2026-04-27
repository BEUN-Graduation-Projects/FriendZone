# backend/models/test_model.py

from backend.app import db
from datetime import datetime


class PersonalityTestResult(db.Model):
    """Kişilik testi sonuçları modeli"""
    __tablename__ = 'personality_test_results'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Test sonuçları
    personality_type = db.Column(db.String(50), nullable=False)  # MBTI tipi veya özel tip
    personality_scores = db.Column(db.JSON, nullable=True)  # Detaylı skorlar


    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # İlişki
    user = db.relationship('User', backref=db.backref('personality_test', uselist=False))

    def __repr__(self):
        return f"<PersonalityTestResult {self.user_id}: {self.personality_type}>"


class HobbyResult(db.Model):
    """Hobi testi sonuçları modeli"""
    __tablename__ = 'hobby_results'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Hobi listesi (JSON formatında)
    hobbies = db.Column(db.JSON, nullable=False)


    created_at = db.Column(db.DateTime, default=datetime.utcnow)


    user = db.relationship('User', backref=db.backref('hobby_result', uselist=False))

    def __repr__(self):
        return f"<HobbyResult {self.user_id}: {len(self.hobbies)} hobbies>"