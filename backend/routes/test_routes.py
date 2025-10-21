from flask import Blueprint, request, jsonify
from backend.models.user_model import User
from backend.app import db
from backend.ml.preprocessing import DataPreprocessor
from backend.ml.similarity_engine import SimilarityEngine
from backend.ml.community_assigner import CommunityAssigner
import logging
import json

logger = logging.getLogger(__name__)

# Blueprint oluştur
test_bp = Blueprint('test', __name__)

# ML bileşenlerini başlat
preprocessor = DataPreprocessor()
similarity_engine = SimilarityEngine(preprocessor)
community_assigner = CommunityAssigner(similarity_engine)


@test_bp.route('/personality-questions', methods=['GET'])
def get_personality_questions():
    """Kişilik testi sorularını getir"""
    try:
        questions = [
            {
                "id": 1,
                "question": "Sosyal ortamlarda nasıl hissedersiniz?",
                "type": "social",
                "options": [
                    {"value": "introvert", "text": "Sessiz ve gözlemci", "score": 1},
                    {"value": "extrovert", "text": "Enerjik ve konuşkan", "score": 3},
                    {"value": "ambivert", "text": "Duruma göre değişir", "score": 2}
                ]
            },
            {
                "id": 2,
                "question": "Problem çözerken hangi yaklaşımı tercih edersiniz?",
                "type": "problem_solving",
                "options": [
                    {"value": "analytical", "text": "Mantıksal analiz", "score": 1},
                    {"value": "creative", "text": "Yaratıcı çözümler", "score": 3},
                    {"value": "practical", "text": "Pratik yaklaşımlar", "score": 2}
                ]
            },
            {
                "id": 3,
                "question": "Plan yapma konusunda nasılsınız?",
                "type": "planning",
                "options": [
                    {"value": "organized", "text": "Detaylı plan yaparım", "score": 1},
                    {"value": "flexible", "text": "Esnek ve spontane", "score": 3},
                    {"value": "balanced", "text": "Orta yol bulurum", "score": 2}
                ]
            },
            {
                "id": 4,
                "question": "Takım çalışmasında hangi rolü alırsınız?",
                "type": "team_role",
                "options": [
                    {"value": "leader", "text": "Liderlik ederim", "score": 1},
                    {"value": "supporter", "text": "Destek sağlarım", "score": 3},
                    {"value": "specialist", "text": "Uzmanlık alanımda katkı sağlarım", "score": 2}
                ]
            },
            {
                "id": 5,
                "question": "Yeni insanlarla tanışmak sizin için?",
                "type": "social_interaction",
                "options": [
                    {"value": "exciting", "text": "Heyecan verici", "score": 3},
                    {"value": "challenging", "text": "Zorlayıcı", "score": 1},
                    {"value": "neutral", "text": "Nötr", "score": 2}
                ]
            }
        ]

        return jsonify({
            "success": True,
            "questions": questions,
            "count": len(questions)
        })

    except Exception as e:
        logger.error(f"Kişilik soruları getirme hatası: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Sorular yüklenemedi"
        }), 500


@test_bp.route('/hobbies-categories', methods=['GET'])
def get_hobbies_categories():
    """Hobi kategorilerini getir"""
    try:
        categories = [
            {
                "id": "technology",
                "name": "Teknoloji ve Bilim",
                "activities": ["Programlama", "Robotik", "AI/Makine Öğrenimi", "Elektronik", "Veri Analizi",
                               "Web Geliştirme"]
            },
            {
                "id": "sports",
                "name": "Spor ve Fitness",
                "activities": ["Futbol", "Basketbol", "Yüzme", "Koşu", "Yoga", "Fitness", "Voleybol", "Tenis"]
            },
            {
                "id": "arts",
                "name": "Sanat ve Tasarım",
                "activities": ["Resim", "Müzik", "Fotoğrafçılık", "Dans", "Tiyatro", "Yazarlık", "Grafik Tasarım",
                               "Heykel"]
            },
            {
                "id": "outdoor",
                "name": "Açık Hava ve Doğa",
                "activities": ["Doğa Yürüyüşü", "Kamp", "Dağcılık", "Bisiklet", "Balıkçılık", "Koşu", "Yürüyüş"]
            },
            {
                "id": "education",
                "name": "Eğitim ve Gelişim",
                "activities": ["Kitap Okuma", "Dil Öğrenme", "Online Kurslar", "Araştırma", "Sunum Hazırlama",
                               "Seminer"]
            },
            {
                "id": "social",
                "name": "Sosyal ve Topluluk",
                "activities": ["Gönüllülük", "Kulüp Aktiviteleri", "Organizasyon", "Network", "Mentorluk",
                               "Topluluk Projeleri"]
            }
        ]

        return jsonify({
            "success": True,
            "categories": categories,
            "count": len(categories)
        })

    except Exception as e:
        logger.error(f"Hobi kategorileri getirme hatası: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Kategoriler yüklenemedi"
        }), 500


@test_bp.route('/submit-personality', methods=['POST'])
def submit_personality_test():
    """Kişilik testi sonuçlarını işle"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        answers = data.get('answers', [])

        if not user_id or not answers:
            return jsonify({
                "success": False,
                "message": "Kullanıcı ID ve cevaplar gereklidir"
            }), 400

        # Kullanıcıyı bul
        user = User.query.get(user_id)
        if not user:
            return jsonify({
                "success": False,
                "message": "Kullanıcı bulunamadı"
            }), 404

        # Cevapları işle ve kişilik tipini belirle
        personality_result = process_personality_answers(answers)

        # Kullanıcıyı güncelle (hobiler henüz eklenmedi)
        user.update_test_results(
            personality_type=personality_result['personality_type'],
            personality_scores=personality_result['scores'],
            hobbies=None  # Hobiler ayrı endpoint'ten eklenecek
        )

        logger.info(f"Kişilik testi tamamlandı: {user.email} - {personality_result['personality_type']}")

        return jsonify({
            "success": True,
            "personality_type": personality_result['personality_type'],
            "scores": personality_result['scores'],
            "message": "Kişilik testi başarıyla kaydedildi"
        })

    except Exception as e:
        logger.error(f"Kişilik testi gönderme hatası: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Test sonuçları kaydedilemedi"
        }), 500


@test_bp.route('/submit-hobbies', methods=['POST'])
def submit_hobbies():
    """Hobi tercihlerini işle"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        hobbies = data.get('hobbies', [])

        if not user_id:
            return jsonify({
                "success": False,
                "message": "Kullanıcı ID gereklidir"
            }), 400

        # Kullanıcıyı bul
        user = User.query.get(user_id)
        if not user:
            return jsonify({
                "success": False,
                "message": "Kullanıcı bulunamadı"
            }), 404

        # Kişilik testi tamamlandı mı kontrol et
        if not user.is_test_completed:
            return jsonify({
                "success": False,
                "message": "Önce kişilik testini tamamlamalısınız"
            }), 400

        # Hobileri güncelle
        user.hobbies = json.dumps(hobbies)
        db.session.commit()

        # ML ile topluluğa ata
        user_data = user.to_dict()
        community_id = community_assigner.assign_user_to_community(str(user.id), user_data)

        logger.info(f"Hobiler kaydedildi ve topluluğa atandı: {user.email} -> {community_id}")

        return jsonify({
            "success": True,
            "community_id": community_id,
            "message": "Hobiler başarıyla kaydedildi ve topluluğa atandınız"
        })

    except Exception as e:
        db.session.rollback()
        logger.error(f"Hobi gönderme hatası: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Hobiler kaydedilemedi"
        }), 500


@test_bp.route('/test-status/<int:user_id>', methods=['GET'])
def get_test_status(user_id):
    """Kullanıcının test durumunu getir"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({
                "success": False,
                "message": "Kullanıcı bulunamadı"
            }), 404

        return jsonify({
            "success": True,
            "is_personality_completed": user.personality_type is not None,
            "is_hobbies_completed": user.hobbies is not None,
            "is_test_completed": user.is_test_completed,
            "personality_type": user.personality_type,
            "hobbies": json.loads(user.hobbies) if user.hobbies else []
        })

    except Exception as e:
        logger.error(f"Test durumu getirme hatası: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Test durumu alınamadı"
        }), 500


def process_personality_answers(answers):
    """Kişilik testi cevaplarını işle ve sonuç üret"""
    scores = {
        'social': {'introvert': 0, 'extrovert': 0, 'ambivert': 0},
        'problem_solving': {'analytical': 0, 'creative': 0, 'practical': 0},
        'planning': {'organized': 0, 'flexible': 0, 'balanced': 0},
        'team_role': {'leader': 0, 'supporter': 0, 'specialist': 0},
        'social_interaction': {'exciting': 0, 'challenging': 0, 'neutral': 0}
    }

    # Cevapları skorlara ekle
    for answer in answers:
        question_type = answer.get('type')
        selected_value = answer.get('value')
        selected_score = answer.get('score', 1)

        if question_type in scores and selected_value in scores[question_type]:
            scores[question_type][selected_value] += selected_score

    # Baskın kişilik özelliklerini belirle
    dominant_traits = []

    for category, traits in scores.items():
        dominant_trait = max(traits.items(), key=lambda x: x[1])
        if dominant_trait[1] > 0:  # Sadece pozitif skorları al
            dominant_traits.append(dominant_trait[0])

    # Kişilik tipini oluştur
    personality_type = '_'.join(dominant_traits[:2]) if dominant_traits else 'balanced'

    return {
        'personality_type': personality_type,
        'scores': scores
    }