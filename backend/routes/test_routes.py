# backend/routes/test_routes.py

from flask import Blueprint, request, jsonify
from backend.models.user_model import User
from backend.app import db
import logging

logger = logging.getLogger(__name__)

# BLUEPRINT TANIMI - BU SATIR ÇOK ÖNEMLİ!
test_bp = Blueprint('test', __name__)

@test_bp.route('/personality', methods=['POST'])
def submit_personality():
    """Kişilik testi sonuçlarını kaydet"""
    try:
        data = request.get_json()
        print(f"📝 Kişilik testi verisi: {data}")

        user_id = data.get('user_id')
        personality_type = data.get('personality_type')

        if not user_id or not personality_type:
            return jsonify({'success': False, 'message': 'Eksik bilgi'}), 400

        user = User.query.get(user_id)
        if not user:
            return jsonify({'success': False, 'message': 'Kullanıcı bulunamadı'}), 404

        user.personality_type = personality_type
        user.is_test_completed = False  # Henüz tamamlanmadı (hobiler de gerekli)
        db.session.commit()

        logger.info(f"✅ Kişilik testi kaydedildi: {user.email} - {personality_type}")

        return jsonify({
            'success': True,
            'message': 'Kişilik testi kaydedildi',
            'personality_type': personality_type
        })

    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ Test hatası: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500


@test_bp.route('/hobbies', methods=['POST'])
def submit_hobbies():
    """Hobileri kaydet ve kullanıcıyı topluluğa ata"""
    try:
        data = request.get_json()
        print(f"📝 Hobi testi verisi: {data}")

        user_id = data.get('user_id')
        hobbies = data.get('hobbies')

        if not user_id or not hobbies:
            return jsonify({'success': False, 'message': 'Eksik bilgi'}), 400

        user = User.query.get(user_id)
        if not user:
            return jsonify({'success': False, 'message': 'Kullanıcı bulunamadı'}), 404

        # Hobileri kaydet
        user.hobbies = hobbies
        user.is_test_completed = True
        db.session.commit()

        logger.info(f"✅ Hobiler kaydedildi: {user.email} - {len(hobbies)} hobi")

        # TODO: ML ile topluluk ata (şimdilik varsayılan)
        community_id = 1  # Varsayılan topluluk

        return jsonify({
            'success': True,
            'message': 'Hobiler kaydedildi',
            'community_id': community_id
        })

    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ Hobi hatası: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500


@test_bp.route('/personality-questions', methods=['GET'])
def get_personality_questions():
    """Kişilik testi sorularını getir"""
    try:
        questions = [
            {
                "id": 1,
                "question": "Sosyal ortamlarda nasıl hissedersiniz?",
                "options": [
                    {"value": "E", "text": "Enerjik ve konuşkan"},
                    {"value": "I", "text": "Sessiz ve gözlemci"}
                ]
            },
            {
                "id": 2,
                "question": "Bir proje üzerinde çalışırken nasıl bir yaklaşım izlersiniz?",
                "options": [
                    {"value": "J", "text": "Planlı ve düzenli ilerlerim"},
                    {"value": "P", "text": "Esnek ve spontane davranırım"}
                ]
            },
            {
                "id": 3,
                "question": "Karar verirken daha çok neye güvenirsiniz?",
                "options": [
                    {"value": "T", "text": "Mantık ve analize"},
                    {"value": "F", "text": "Duygular ve insan faktörüne"}
                ]
            }
        ]

        return jsonify({
            'success': True,
            'questions': questions,
            'count': len(questions)
        })

    except Exception as e:
        logger.error(f"❌ Soru yükleme hatası: {str(e)}")
        return jsonify({'success': False, 'message': 'Sorular yüklenemedi'}), 500


@test_bp.route('/hobbies-categories', methods=['GET'])
def get_hobbies_categories():
    """Hobi kategorilerini getir"""
    try:
        categories = [
            {
                "id": "technology",
                "name": "Teknoloji ve Bilim",
                "activities": ["Programlama", "Robotik", "AI/Makine Öğrenimi", "Elektronik", "Veri Analizi"]
            },
            {
                "id": "sports",
                "name": "Spor ve Fitness",
                "activities": ["Futbol", "Basketbol", "Yüzme", "Koşu", "Yoga", "Fitness"]
            },
            {
                "id": "arts",
                "name": "Sanat ve Tasarım",
                "activities": ["Resim", "Müzik", "Fotoğrafçılık", "Dans", "Tiyatro", "Yazarlık"]
            },
            {
                "id": "outdoor",
                "name": "Açık Hava ve Doğa",
                "activities": ["Doğa Yürüyüşü", "Kamp", "Dağcılık", "Bisiklet"]
            },
            {
                "id": "education",
                "name": "Eğitim ve Gelişim",
                "activities": ["Kitap Okuma", "Dil Öğrenme", "Online Kurslar", "Araştırma"]
            },
            {
                "id": "social",
                "name": "Sosyal ve Topluluk",
                "activities": ["Gönüllülük", "Organizasyon", "Network", "Mentorluk"]
            }
        ]

        return jsonify({
            'success': True,
            'categories': categories,
            'count': len(categories)
        })

    except Exception as e:
        logger.error(f"❌ Kategori yükleme hatası: {str(e)}")
        return jsonify({'success': False, 'message': 'Kategoriler yüklenemedi'}), 500


@test_bp.route('/test-status/<int:user_id>', methods=['GET'])
def get_test_status(user_id):
    """Kullanıcının test durumunu getir"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'success': False, 'message': 'Kullanıcı bulunamadı'}), 404

        return jsonify({
            'success': True,
            'is_personality_completed': user.personality_type is not None,
            'is_hobbies_completed': user.hobbies is not None,
            'is_test_completed': user.is_test_completed,
            'personality_type': user.personality_type,
            'hobbies': user.hobbies if user.hobbies else []
        })

    except Exception as e:
        logger.error(f"❌ Test durumu hatası: {str(e)}")
        return jsonify({'success': False, 'message': 'Test durumu alınamadı'}), 500