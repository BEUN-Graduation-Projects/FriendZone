# backend/routes/community_routes.py

from flask import Blueprint, request, jsonify
from backend.models.user_model import User
from backend.models.community_model import Community, CommunityMember
from backend.app import db
import logging

logger = logging.getLogger(__name__)

community_bp = Blueprint('community', __name__)


@community_bp.route('/join', methods=['POST'])
def join_community():
    """Kullanıcıyı topluluğa ekle"""
    try:
        data = request.get_json()
        print("=" * 50)
        print("🔍 JOIN COMMUNITY ENDPOINT ÇALIŞTI")
        print(f"📥 Gelen veri: {data}")
        print(f"📥 Headers: {dict(request.headers)}")

        user_id = data.get('user_id')
        community_id = data.get('community_id')

        print(f"📝 user_id: {user_id} (tip: {type(user_id)})")
        print(f"📝 community_id: {community_id} (tip: {type(community_id)})")

        if not user_id or not community_id:
            return jsonify({
                'success': False,
                'message': 'Kullanıcı ID ve topluluk ID gereklidir'
            }), 400

        # ID'leri integer'a çevir
        try:
            user_id = int(user_id)
            community_id = int(community_id)
            print(f"✅ Dönüştürüldü: user_id={user_id}, community_id={community_id}")
        except (ValueError, TypeError) as e:
            print(f"❌ Dönüştürme hatası: {e}")
            return jsonify({
                'success': False,
                'message': 'Geçersiz ID formatı'
            }), 400

        # Kullanıcı var mı?
        user = User.query.get(user_id)
        if not user:
            print(f"❌ Kullanıcı bulunamadı: {user_id}")
            return jsonify({
                'success': False,
                'message': 'Kullanıcı bulunamadı'
            }), 404
        print(f"✅ Kullanıcı bulundu: {user.name}")

        # Topluluk var mı?
        community = Community.query.get(community_id)
        if not community:
            print(f"❌ Topluluk bulunamadı: {community_id}")
            return jsonify({
                'success': False,
                'message': 'Topluluk bulunamadı'
            }), 404
        print(f"✅ Topluluk bulundu: {community.name}")

        # Zaten üye mi?
        existing_member = CommunityMember.query.filter_by(
            community_id=community_id,
            user_id=user_id
        ).first()

        if existing_member:
            print(f"ℹ️ Kullanıcı zaten üye: aktif={existing_member.is_active}")
            if existing_member.is_active:
                return jsonify({
                    'success': True,
                    'message': 'Zaten bu topluluğun üyesisiniz',
                    'already_member': True
                }), 200
            else:
                # Pasif üyeyi yeniden aktif et
                existing_member.is_active = True
                db.session.commit()
                logger.info(f"✅ Kullanıcı {user_id} topluluğa yeniden katıldı: {community.name}")
                return jsonify({
                    'success': True,
                    'message': 'Topluluğa yeniden katıldınız'
                }), 200

        # Yeni üye oluştur
        new_member = CommunityMember(
            community_id=community_id,
            user_id=user_id,
            role='member',
            is_active=True
        )

        db.session.add(new_member)
        db.session.commit()

        logger.info(f"✅ Kullanıcı {user_id} topluluğa katıldı: {community.name}")
        print("=" * 50)

        return jsonify({
            'success': True,
            'message': 'Topluluğa başarıyla katıldınız',
            'community': community.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        print(f"❌ HATA: {str(e)}")
        import traceback
        traceback.print_exc()
        print("=" * 50)
        return jsonify({
            'success': False,
            'message': f'Topluluğa katılırken bir hata oluştu: {str(e)}'
        }), 500


@community_bp.route('/recommendations/<int:user_id>', methods=['GET'])
def get_community_recommendations(user_id):
    """Kullanıcı için topluluk önerileri getir - TÜM TOPLULUKLARI DÖNDÜR"""
    try:
        print(f"📝 Öneri isteği: user_id={user_id}")

        user = User.query.get(user_id)
        if not user:
            return jsonify({
                'success': False,
                'message': 'Kullanıcı bulunamadı'
            }), 404

        # VERİTABANINDAKİ TÜM AKTİF TOPLULUKLARI GETİR
        communities = Community.query.filter_by(is_active=True).all()

        recommendations = []
        for community in communities:
            # Kullanıcının zaten üye olup olmadığını kontrol et
            is_member = CommunityMember.query.filter_by(
                community_id=community.id,
                user_id=user_id,
                is_active=True
            ).first() is not None

            # Üye sayısını hesapla
            member_count = CommunityMember.query.filter_by(
                community_id=community.id,
                is_active=True
            ).count()

            recommendations.append({
                "id": community.id,
                "name": community.name,
                "description": community.description,
                "category": community.category,
                "member_count": member_count,
                "compatibility_score": community.compatibility_score or 0.75,  # Varsayılan uyum skoru
                "max_members": community.max_members,
                "tags": community.tags or [],
                "is_member": is_member
            })

        print(f"✅ {len(recommendations)} topluluk bulundu")
        return jsonify({
            'success': True,
            'recommendations': recommendations
        }), 200

    except Exception as e:
        logger.error(f"❌ Öneri hatası: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Öneriler getirilemedi'
        }), 500


@community_bp.route('/user/<int:user_id>', methods=['GET'])
def get_user_communities(user_id):
    """Kullanıcının topluluklarını getir"""
    try:
        print(f"📝 Kullanıcı toplulukları isteği: user_id={user_id}")

        user = User.query.get(user_id)
        if not user:
            return jsonify({
                'success': False,
                'message': 'Kullanıcı bulunamadı'
            }), 404

        # Kullanıcının üye olduğu toplulukları getir
        memberships = CommunityMember.query.filter_by(
            user_id=user_id,
            is_active=True
        ).all()

        communities = []
        for membership in memberships:
            community = membership.community
            if community and community.is_active:
                communities.append({
                    'id': community.id,
                    'name': community.name,
                    'description': community.description,
                    'category': community.category,
                    'role': membership.role,
                    'joined_at': membership.joined_at.isoformat() if membership.joined_at else None
                })

        return jsonify({
            'success': True,
            'communities': communities
        }), 200

    except Exception as e:
        logger.error(f"❌ Kullanıcı toplulukları hatası: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Topluluklar getirilemedi'
        }), 500


@community_bp.route('/<int:community_id>', methods=['GET'])
def get_community(community_id):
    """Belirli bir topluluğun detaylarını getir"""
    try:
        print(f"📝 Topluluk detay isteği: community_id={community_id}")

        community = Community.query.get(community_id)
        if not community or not community.is_active:
            return jsonify({
                'success': False,
                'message': 'Topluluk bulunamadı'
            }), 404

        return jsonify({
            'success': True,
            'community': community.to_dict(include_members=True)
        }), 200

    except Exception as e:
        logger.error(f"❌ Topluluk detay hatası: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Topluluk getirilemedi'
        }), 500


@community_bp.route('/similar-users/<int:user_id>', methods=['GET'])
def get_similar_users(user_id):
    """Kullanıcının benzer kullanıcılarını getir"""
    try:
        print(f"📝 Benzer kullanıcılar isteği: user_id={user_id}")

        user = User.query.get(user_id)
        if not user:
            return jsonify({
                'success': False,
                'message': 'Kullanıcı bulunamadı'
            }), 404

        # Örnek benzer kullanıcılar - gerçek uygulamada ML ile hesaplanacak
        sample_users = [
            {
                'user': {
                    'id': 1,
                    'name': 'Ahmet Yılmaz',
                    'university': 'İstanbul Teknik Üniversitesi',
                    'hobbies': ['Programlama', 'Robotik', 'Yapay Zeka']
                },
                'similarity_score': 0.89
            },
            {
                'user': {
                    'id': 2,
                    'name': 'Ayşe Demir',
                    'university': 'Boğaziçi Üniversitesi',
                    'hobbies': ['Veri Analizi', 'Makine Öğrenimi', 'Yapay Zeka']
                },
                'similarity_score': 0.85
            },
            {
                'user': {
                    'id': 4,
                    'name': 'Mehmet Kaya',
                    'university': 'Orta Doğu Teknik Üniversitesi',
                    'hobbies': ['Yazılım', 'Web Geliştirme', 'Mobil Uygulama']
                },
                'similarity_score': 0.82
            }
        ]

        return jsonify({
            'success': True,
            'similar_users': sample_users
        }), 200

    except Exception as e:
        logger.error(f"❌ Benzer kullanıcılar hatası: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Benzer kullanıcılar getirilemedi'
        }), 500


@community_bp.route('/create', methods=['POST'])
def create_community():
    """Yeni topluluk oluştur"""
    try:
        data = request.get_json()
        print("="*50)
        print("🔍 CREATE COMMUNITY ENDPOINT ÇALIŞTI")
        print(f"📥 Gelen veri: {data}")

        name = data.get('name')
        description = data.get('description')
        category = data.get('category')
        created_by = data.get('created_by')
        max_members = data.get('max_members', 10)
        tags = data.get('tags', [])

        print(f"📝 name: {name}")
        print(f"📝 description: {description}")
        print(f"📝 category: {category}")
        print(f"📝 created_by: {created_by}")
        print(f"📝 max_members: {max_members}")
        print(f"📝 tags: {tags}")

        if not name or not created_by:
            return jsonify({
                'success': False,
                'message': 'Topluluk adı ve oluşturan kullanıcı gereklidir'
            }), 400

        # created_by'yi integer'a çevir
        try:
            created_by = int(created_by)
        except (ValueError, TypeError):
            return jsonify({
                'success': False,
                'message': 'Geçersiz kullanıcı ID formatı'
            }), 400

        # Kullanıcı var mı?
        user = User.query.get(created_by)
        if not user:
            print(f"❌ Kullanıcı bulunamadı: {created_by}")
            return jsonify({
                'success': False,
                'message': 'Kullanıcı bulunamadı'
            }), 404
        print(f"✅ Kullanıcı bulundu: {user.name}")

        # Aynı isimde topluluk var mı?
        existing = Community.query.filter_by(name=name).first()
        if existing:
            print(f"❌ Aynı isimde topluluk var: {name}")
            return jsonify({
                'success': False,
                'message': 'Bu isimde bir topluluk zaten var'
            }), 400

        # Yeni topluluk oluştur
        new_community = Community(
            name=name,
            description=description,
            category=category,
            created_by=created_by,
            max_members=max_members,
            tags=tags if tags else [],
            is_active=True
        )

        db.session.add(new_community)
        db.session.commit()
        print(f"✅ Topluluk veritabanına eklendi: ID={new_community.id}")

        # Oluşturan kişiyi admin olarak ekle
        try:
            new_member = CommunityMember(
                community_id=new_community.id,
                user_id=created_by,
                role='admin',
                is_active=True
            )
            db.session.add(new_member)
            db.session.commit()
            print(f"✅ Oluşturan kullanıcı admin olarak eklendi")
        except Exception as e:
            print(f"⚠️ Üye eklenirken hata (admin zaten eklenmiş olabilir): {e}")
            db.session.rollback()

        logger.info(f"✅ Yeni topluluk oluşturuldu: {name} (ID: {new_community.id})")
        print("="*50)

        return jsonify({
            'success': True,
            'message': 'Topluluk başarıyla oluşturuldu',
            'community': new_community.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        print(f"❌ HATA: {str(e)}")
        import traceback
        traceback.print_exc()
        print("="*50)
        return jsonify({
            'success': False,
            'message': f'Topluluk oluşturulurken bir hata oluştu: {str(e)}'
        }), 500


@community_bp.route('/leave', methods=['POST'])
def leave_community():
    """Kullanıcıyı topluluktan çıkar"""
    try:
        data = request.get_json()
        print(f"📝 Topluluktan ayrılma isteği: {data}")

        user_id = data.get('user_id')
        community_id = data.get('community_id')

        if not user_id or not community_id:
            return jsonify({
                'success': False,
                'message': 'Kullanıcı ID ve topluluk ID gereklidir'
            }), 400

        # ID'leri integer'a çevir
        try:
            user_id = int(user_id)
            community_id = int(community_id)
        except (ValueError, TypeError):
            return jsonify({
                'success': False,
                'message': 'Geçersiz ID formatı'
            }), 400

        membership = CommunityMember.query.filter_by(
            community_id=community_id,
            user_id=user_id
        ).first()

        if not membership:
            return jsonify({
                'success': False,
                'message': 'Topluluk üyeliği bulunamadı'
            }), 404

        # Admin kontrolü (son admin topluluktan ayrılamaz)
        if membership.role == 'admin':
            admin_count = CommunityMember.query.filter_by(
                community_id=community_id,
                role='admin',
                is_active=True
            ).count()

            if admin_count <= 1:
                return jsonify({
                    'success': False,
                    'message': 'Son admin topluluktan ayrılamaz'
                }), 400

        # Üyeliği pasif yap
        membership.is_active = False
        db.session.commit()

        logger.info(f"✅ Kullanıcı {user_id} topluluktan ayrıldı: {community_id}")

        return jsonify({
            'success': True,
            'message': 'Topluluktan başarıyla ayrıldınız'
        }), 200

    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ Topluluktan ayrılma hatası: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'Topluluktan ayrılırken bir hata oluştu: {str(e)}'
        }), 500