from flask import Blueprint, request, jsonify
from backend.models.user_model import User
from backend.models.community_model import Community, CommunityMember
from backend.app import db
import logging

logger = logging.getLogger(__name__)
test_bp = Blueprint('test', __name__)

@test_bp.route('/personality', methods=['POST'])
def submit_personality():
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        personality_type = data.get('personality_type')
        user = User.query.get(user_id)
        if not user:
            return jsonify({'success': False, 'message': 'Kullanıcı bulunamadı'}), 404
        user.personality_type = personality_type
        db.session.commit()
        return jsonify({'success': True, 'message': 'Kişilik testi kaydedildi'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@test_bp.route('/hobbies', methods=['POST'])
def submit_hobbies():
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        hobbies = data.get('hobbies')
        user = User.query.get(user_id)
        if not user:
            return jsonify({'success': False, 'message': 'Kullanıcı bulunamadı'}), 404
        user.hobbies = hobbies
        user.is_test_completed = True
        db.session.commit()

        # Otomatik topluluk atama: kullanıcının hobilerine en çok uyan topluluğu bul
        all_communities = Community.query.filter_by(is_active=True).all()
        best_community = None
        best_match_count = -1

        for community in all_communities:
            tags = community.tags or []
            match_count = sum(1 for hobby in hobbies if any(tag.lower() in hobby.lower() for tag in tags))
            if match_count > best_match_count:
                best_match_count = match_count
                best_community = community

        if not best_community and all_communities:
            best_community = all_communities[0]

        if best_community:
            existing = CommunityMember.query.filter_by(community_id=best_community.id, user_id=user_id).first()
            if not existing:
                new_member = CommunityMember(
                    community_id=best_community.id,
                    user_id=user_id,
                    role='member',
                    is_active=True
                )
                db.session.add(new_member)
                db.session.commit()
            community_id = best_community.id
        else:
            community_id = None

        return jsonify({
            'success': True,
            'message': 'Hobiler kaydedildi ve topluluğa atandınız',
            'community_id': community_id
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@test_bp.route('/personality-questions', methods=['GET'])
def get_personality_questions():
    # Örnek sorular – gerçek projede 25 soru kullanıyorsunuz
    questions = [{"id": 1, "question": "Yeni insanlarla tanışmaktan keyif alırım.", "options": [{"value": 1, "text": "Kesinlikle Katılmıyorum"}, {"value": 5, "text": "Kesinlikle Katılıyorum"}]}]
    return jsonify({"success": True, "questions": questions})

@test_bp.route('/hobbies-categories', methods=['GET'])
def get_hobbies_categories():
    categories = [
        {"id": "technology", "name": "Teknoloji", "activities": ["Programlama", "Yapay Zeka", "Robotik"]},
        {"id": "sports", "name": "Spor", "activities": ["Futbol", "Basketbol", "Yüzme"]},
        {"id": "arts", "name": "Sanat", "activities": ["Resim", "Müzik", "Tiyatro"]}
    ]
    return jsonify({"success": True, "categories": categories})

@test_bp.route('/test-status/<int:user_id>', methods=['GET'])
def get_test_status(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'success': False, 'message': 'Kullanıcı bulunamadı'}), 404
    return jsonify({
        'success': True,
        'is_personality_completed': bool(user.personality_type),
        'is_hobbies_completed': bool(user.hobbies),
        'is_test_completed': user.is_test_completed,
        'personality_type': user.personality_type,
        'hobbies': user.hobbies or []
    })