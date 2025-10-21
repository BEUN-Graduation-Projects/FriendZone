from flask import Blueprint, request, jsonify
from backend.models.user_model import User
from backend.models.community_model import Community, CommunityMember
from backend.models.similarity_model import UserSimilarity
from backend.app import db
import logging

logger = logging.getLogger(__name__)

# Blueprint oluştur
community_bp = Blueprint('community', __name__)


@community_bp.route('/user/<int:user_id>', methods=['GET'])
def get_user_communities(user_id):
    """Kullanıcının topluluklarını getir"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({
                "success": False,
                "message": "Kullanıcı bulunamadı"
            }), 404

        # Kullanıcının üye olduğu toplulukları getir
        user_communities = []
        for membership in user.communities:
            if membership.is_active and membership.community.is_active:
                user_communities.append(membership.community.to_dict(include_members=True))

        return jsonify({
            "success": True,
            "communities": user_communities,
            "count": len(user_communities)
        })

    except Exception as e:
        logger.error(f"Kullanıcı toplulukları getirme hatası: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Topluluklar getirilemedi"
        }), 500


@community_bp.route('/<int:community_id>', methods=['GET'])
def get_community(community_id):
    """Belirli bir topluluğun detaylarını getir"""
    try:
        community = Community.query.get(community_id)
        if not community or not community.is_active:
            return jsonify({
                "success": False,
                "message": "Topluluk bulunamadı"
            }), 404

        return jsonify({
            "success": True,
            "community": community.to_dict(include_members=True)
        })

    except Exception as e:
        logger.error(f"Topluluk getirme hatası: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Topluluk getirilemedi"
        }), 500


@community_bp.route('/recommendations/<int:user_id>', methods=['GET'])
def get_community_recommendations(user_id):
    """Kullanıcı için topluluk önerileri getir"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({
                "success": False,
                "message": "Kullanıcı bulunamadı"
            }), 404

        # Basit öneri algoritması - kategorilere göre
        user_hobbies = user.get_hobbies_list()
        user_personality = user.personality_type

        # Kullanıcının hobilerine göre kategoriler belirle
        recommended_categories = set()

        tech_keywords = ["programlama", "yazılım", "ai", "teknoloji", "robotik", "veri"]
        sports_keywords = ["futbol", "basketbol", "yüzme", "spor", "fitness", "yoga"]
        arts_keywords = ["resim", "müzik", "sanat", "dans", "tiyatro", "fotoğraf"]

        for hobby in user_hobbies:
            hobby_lower = hobby.lower()
            if any(keyword in hobby_lower for keyword in tech_keywords):
                recommended_categories.add('technology')
            if any(keyword in hobby_lower for keyword in sports_keywords):
                recommended_categories.add('sports')
            if any(keyword in hobby_lower for keyword in arts_keywords):
                recommended_categories.add('arts')

        # Önerilen kategorilerdeki toplulukları getir
        recommended_communities = []
        for category in recommended_categories:
            category_communities = Community.find_by_category(category)
            for community in category_communities:
                # Kullanıcı zaten üye mi kontrol et
                is_member = any(member.user_id == user_id for member in community.members)
                if not is_member and community.is_active:
                    recommended_communities.append(community.to_dict())

        # Eğer öneri yoksa, genel toplulukları göster
        if not recommended_communities:
            general_communities = Community.query.filter_by(is_active=True).limit(5).all()
            recommended_communities = [community.to_dict() for community in general_communities]

        return jsonify({
            "success": True,
            "recommendations": recommended_communities,
            "count": len(recommended_communities)
        })

    except Exception as e:
        logger.error(f"Topluluk önerileri getirme hatası: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Öneriler getirilemedi"
        }), 500


@community_bp.route('/join', methods=['POST'])
def join_community():
    """Kullanıcıyı topluluğa ekle"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        community_id = data.get('community_id')

        if not user_id or not community_id:
            return jsonify({
                "success": False,
                "message": "Kullanıcı ID ve topluluk ID gereklidir"
            }), 400

        community = Community.query.get(community_id)
        if not community:
            return jsonify({
                "success": False,
                "message": "Topluluk bulunamadı"
            }), 404

        # Topluluğa üye ekle
        community.add_member(user_id)

        return jsonify({
            "success": True,
            "message": "Topluluğa başarıyla katıldınız",
            "community": community.to_dict(include_members=True)
        })

    except ValueError as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 400
    except Exception as e:
        logger.error(f"Topluluğa katılma hatası: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Topluluğa katılamadınız"
        }), 500


@community_bp.route('/leave', methods=['POST'])
def leave_community():
    """Kullanıcıyı topluluktan çıkar"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        community_id = data.get('community_id')

        if not user_id or not community_id:
            return jsonify({
                "success": False,
                "message": "Kullanıcı ID ve topluluk ID gereklidir"
            }), 400

        community = Community.query.get(community_id)
        if not community:
            return jsonify({
                "success": False,
                "message": "Topluluk bulunamadı"
            }), 404

        # Topluluktan çıkar
        success = community.remove_member(user_id)

        if success:
            return jsonify({
                "success": True,
                "message": "Topluluktan ayrıldınız"
            })
        else:
            return jsonify({
                "success": False,
                "message": "Topluluktan ayrılamadınız"
            }), 400

    except Exception as e:
        logger.error(f"Topluluktan ayrılma hatası: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Topluluktan ayrılamadınız"
        }), 500


@community_bp.route('/similar-users/<int:user_id>', methods=['GET'])
def get_similar_users(user_id):
    """Kullanıcının benzer kullanıcılarını getir"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({
                "success": False,
                "message": "Kullanıcı bulunamadı"
            }), 404

        # Benzer kullanıcıları getir
        similar_users = user.get_similar_users(limit=10)

        return jsonify({
            "success": True,
            "similar_users": similar_users,
            "count": len(similar_users)
        })

    except Exception as e:
        logger.error(f"Benzer kullanıcılar getirme hatası: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Benzer kullanıcılar getirilemedi"
        }), 500