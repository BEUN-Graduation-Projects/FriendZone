from flask import Blueprint, request, jsonify
from backend.models.user_model import User
from backend.models.community_model import Community, CommunityMember
from backend.app import db
import logging

logger = logging.getLogger(__name__)
community_bp = Blueprint('community', __name__)

@community_bp.route('/join', methods=['POST'])
def join_community():
    try:
        data = request.get_json()
        user_id = int(data.get('user_id'))
        community_id = int(data.get('community_id'))
        user = User.query.get(user_id)
        community = Community.query.get(community_id)
        if not user or not community:
            return jsonify({'success': False, 'message': 'Kullanıcı veya topluluk bulunamadı'}), 404

        existing = CommunityMember.query.filter_by(community_id=community_id, user_id=user_id).first()
        if existing and existing.is_active:
            return jsonify({'success': True, 'message': 'Zaten üyesiniz', 'already_member': True})
        elif existing:
            existing.is_active = True
            db.session.commit()
            return jsonify({'success': True, 'message': 'Tekrar katıldınız'})
        else:
            new_member = CommunityMember(community_id=community_id, user_id=user_id, role='member', is_active=True)
            db.session.add(new_member)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Topluluğa katıldınız'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@community_bp.route('/recommendations/<int:user_id>', methods=['GET'])
def get_community_recommendations(user_id):
    try:
        communities = Community.query.filter_by(is_active=True).all()
        result = []
        for c in communities:
            member_count = CommunityMember.query.filter_by(community_id=c.id, is_active=True).count()
            is_member = CommunityMember.query.filter_by(community_id=c.id, user_id=user_id, is_active=True).first() is not None
            result.append({
                'id': c.id,
                'name': c.name,
                'description': c.description,
                'category': c.category,
                'member_count': member_count,
                'max_members': c.max_members,
                'compatibility_score': c.compatibility_score or 0.75,
                'tags': c.tags or [],
                'is_member': is_member
            })
        return jsonify({'success': True, 'recommendations': result})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@community_bp.route('/user/<int:user_id>', methods=['GET'])
def get_user_communities(user_id):
    try:
        memberships = CommunityMember.query.filter_by(user_id=user_id, is_active=True).all()
        communities = []
        for m in memberships:
            c = m.community
            if c and c.is_active:
                communities.append({
                    'id': c.id,
                    'name': c.name,
                    'description': c.description,
                    'category': c.category,
                    'role': m.role,
                    'joined_at': m.joined_at.isoformat() if m.joined_at else None
                })
        return jsonify({'success': True, 'communities': communities})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@community_bp.route('/<int:community_id>', methods=['GET'])
def get_community(community_id):
    community = Community.query.get(community_id)
    if not community:
        return jsonify({'success': False, 'message': 'Topluluk bulunamadı'}), 404
    return jsonify({'success': True, 'community': community.to_dict(include_members=True)})

@community_bp.route('/create', methods=['POST'])
def create_community():
    try:
        data = request.get_json()
        name = data.get('name')
        description = data.get('description')
        category = data.get('category')
        created_by = int(data.get('created_by'))
        max_members = data.get('max_members', 10)
        tags = data.get('tags', [])

        existing = Community.query.filter_by(name=name).first()
        if existing:
            return jsonify({'success': False, 'message': 'Bu isimde topluluk zaten var'}), 400

        new_community = Community(
            name=name,
            description=description,
            category=category,
            created_by=created_by,
            max_members=max_members,
            tags=tags,
            is_active=True
        )
        db.session.add(new_community)
        db.session.commit()

        # Oluşturanı admin olarak ekle
        new_community.add_member(created_by, role='admin')
        db.session.commit()
        return jsonify({'success': True, 'message': 'Topluluk oluşturuldu', 'community': new_community.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@community_bp.route('/leave', methods=['POST'])
def leave_community():
    try:
        data = request.get_json()
        user_id = int(data.get('user_id'))
        community_id = int(data.get('community_id'))
        membership = CommunityMember.query.filter_by(community_id=community_id, user_id=user_id).first()
        if not membership:
            return jsonify({'success': False, 'message': 'Üyelik bulunamadı'}), 404
        membership.is_active = False
        db.session.commit()
        return jsonify({'success': True, 'message': 'Topluluktan ayrıldınız'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@community_bp.route('/similar-users/<int:user_id>', methods=['GET'])
def get_similar_users(user_id):
    # Örnek – gerçek similarity motoru için düzenlenebilir
    sample = [
        {'user': {'id': 2, 'name': 'Demo Kullanıcı', 'university': 'Demo Üni', 'hobbies': ['Programlama']}, 'similarity_score': 0.85}
    ]
    return jsonify({'success': True, 'similar_users': sample})