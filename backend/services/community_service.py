import logging
from typing import List, Dict, Any, Optional
from backend.models.community_model import Community, CommunityMember
from backend.models.user_model import User
from backend.app import db

logger = logging.getLogger(__name__)


class CommunityService:
    """Topluluk servisi - Topluluk yönetimi business logic"""

    def create_community(self, name: str, description: str, category: str,
                         created_by: int, tags: List[str] = None,
                         max_members: int = 10) -> Optional[Community]:
        """Yeni topluluk oluştur"""
        try:
            # İsim kontrolü
            existing_community = Community.query.filter_by(name=name).first()
            if existing_community:
                raise ValueError("Bu isimde bir topluluk zaten var")

            # Yeni topluluk oluştur
            new_community = Community(
                name=name,
                description=description,
                category=category,
                tags=tags,
                max_members=max_members,
                created_by=created_by
            )

            db.session.add(new_community)
            db.session.commit()

            # Oluşturanı topluluğa admin olarak ekle
            new_community.add_member(created_by, role='admin')

            logger.info(f"Yeni topluluk oluşturuldu: {name} by user {created_by}")

            return new_community

        except ValueError as e:
            db.session.rollback()
            raise e
        except Exception as e:
            db.session.rollback()
            logger.error(f"Topluluk oluşturma hatası: {str(e)}")
            return None

    def get_community_with_members(self, community_id: int) -> Optional[Dict[str, Any]]:
        """Topluluğu ve üyeleriyle birlikte getir"""
        try:
            community = Community.query.get(community_id)
            if not community or not community.is_active:
                return None

            community_data = community.to_dict(include_members=True)

            # Üye istatistikleri ekle
            member_stats = self._calculate_member_stats(community.members)
            community_data['member_stats'] = member_stats

            return community_data

        except Exception as e:
            logger.error(f"Topluluk getirme hatası: {str(e)}")
            return None

    def get_user_communities(self, user_id: int) -> List[Dict[str, Any]]:
        """Kullanıcının topluluklarını getir"""
        try:
            user = User.query.get(user_id)
            if not user:
                return []

            communities = []
            for membership in user.communities:
                if membership.is_active and membership.community.is_active:
                    community_data = membership.community.to_dict(include_members=True)
                    community_data['user_role'] = membership.role
                    communities.append(community_data)

            return communities

        except Exception as e:
            logger.error(f"Kullanıcı toplulukları getirme hatası: {str(e)}")
            return []

    def join_community(self, user_id: int, community_id: int) -> bool:
        """Kullanıcıyı topluluğa ekle"""
        try:
            community = Community.query.get(community_id)
            if not community:
                raise ValueError("Topluluk bulunamadı")

            # Zaten üye mi kontrol et
            existing_member = CommunityMember.query.filter_by(
                community_id=community_id, user_id=user_id
            ).first()

            if existing_member:
                if existing_member.is_active:
                    raise ValueError("Zaten bu topluluğun üyesisiniz")
                else:
                    # Yeniden aktif et
                    existing_member.is_active = True
                    db.session.commit()
                    return True

            # Yeni üye ekle
            community.add_member(user_id)
            return True

        except ValueError as e:
            raise e
        except Exception as e:
            db.session.rollback()
            logger.error(f"Topluluğa katılma hatası: {str(e)}")
            return False

    def leave_community(self, user_id: int, community_id: int) -> bool:
        """Kullanıcıyı topluluktan çıkar"""
        try:
            membership = CommunityMember.query.filter_by(
                community_id=community_id, user_id=user_id
            ).first()

            if not membership:
                raise ValueError("Topluluk üyeliği bulunamadı")

            # Admin kontrolü (son admin topluluktan ayrılamaz)
            if membership.role == 'admin':
                admin_count = CommunityMember.query.filter_by(
                    community_id=community_id, role='admin', is_active=True
                ).count()

                if admin_count <= 1:
                    raise ValueError("Son admin topluluktan ayrılamaz")

            # Üyeliği pasif yap
            membership.is_active = False
            db.session.commit()

            logger.info(f"Kullanıcı {user_id} topluluk {community_id}'den ayrıldı")
            return True

        except ValueError as e:
            raise e
        except Exception as e:
            db.session.rollback()
            logger.error(f"Topluluktan ayrılma hatası: {str(e)}")
            return False

    def update_community(self, community_id: int, updates: Dict[str, Any],
                         user_id: int) -> bool:
        """Topluluk bilgilerini güncelle"""
        try:
            community = Community.query.get(community_id)
            if not community:
                raise ValueError("Topluluk bulunamadı")

            # Yetki kontrolü
            membership = CommunityMember.query.filter_by(
                community_id=community_id, user_id=user_id
            ).first()

            if not membership or membership.role not in ['admin', 'moderator']:
                raise ValueError("Topluluğu güncelleme yetkiniz yok")

            # Güncellenebilir alanlar
            updatable_fields = ['name', 'description', 'category', 'tags', 'max_members']

            for field in updatable_fields:
                if field in updates:
                    if field == 'tags' and isinstance(updates[field], list):
                        setattr(community, field, updates[field])
                    else:
                        setattr(community, field, updates[field])

            db.session.commit()

            logger.info(f"Topluluk güncellendi: {community_id} by user {user_id}")
            return True

        except ValueError as e:
            db.session.rollback()
            raise e
        except Exception as e:
            db.session.rollback()
            logger.error(f"Topluluk güncelleme hatası: {str(e)}")
            return False

    def get_community_analytics(self, community_id: int, user_id: int) -> Optional[Dict[str, Any]]:
        """Topluluk analitiklerini getir"""
        try:
            community = Community.query.get(community_id)
            if not community:
                return None

            # Yetki kontrolü
            membership = CommunityMember.query.filter_by(
                community_id=community_id, user_id=user_id
            ).first()

            if not membership or membership.role not in ['admin', 'moderator']:
                raise ValueError("Analitiklere erişim yetkiniz yok")

            analytics = {
                'total_members': len(community.members),
                'active_members': len([m for m in community.members if m.is_active]),
                'member_growth': self._calculate_member_growth(community_id),
                'compatibility_score': community.compatibility_score,
                'category_distribution': self._get_member_categories(community.members),
                'engagement_metrics': self._calculate_engagement_metrics(community_id)
            }

            return analytics

        except ValueError as e:
            raise e
        except Exception as e:
            logger.error(f"Analitik getirme hatası: {str(e)}")
            return None

    def _calculate_member_stats(self, members: List[CommunityMember]) -> Dict[str, Any]:
        """Üye istatistiklerini hesapla"""
        if not members:
            return {}

        total_members = len(members)
        active_members = len([m for m in members if m.is_active])

        # Rol dağılımı
        roles = {}
        for member in members:
            if member.is_active:
                roles[member.role] = roles.get(member.role, 0) + 1

        return {
            'total_members': total_members,
            'active_members': active_members,
            'roles': roles
        }

    def _calculate_member_growth(self, community_id: int) -> Dict[str, int]:
        """Üye büyüme istatistikleri"""
        # Basit implementasyon - gerçek uygulamada tarih bazlı hesaplama yapılır
        return {
            'last_week': 5,
            'last_month': 15,
            'total': CommunityMember.query.filter_by(
                community_id=community_id, is_active=True
            ).count()
        }

    def _get_member_categories(self, members: List[CommunityMember]) -> Dict[str, int]:
        """Üye kategorileri dağılımı"""
        categories = {}

        for member in members:
            if member.is_active:
                user = member.user
                department = user.department or 'Belirtilmemiş'
                categories[department] = categories.get(department, 0) + 1

        return categories

    def _calculate_engagement_metrics(self, community_id: int) -> Dict[str, float]:
        """Katılım metrikleri"""
        # Basit implementasyon - gerçek uygulamada etkileşim verileri kullanılır
        return {
            'activity_rate': 0.75,
            'response_time': 2.5,  # saat
            'satisfaction_score': 4.2  # 5 üzerinden
        }

    def search_communities(self, query: str, category: str = None,
                           limit: int = 10) -> List[Dict[str, Any]]:
        """Toplulukları ara"""
        try:
            search_query = Community.query.filter_by(is_active=True)

            if query:
                search_query = search_query.filter(
                    Community.name.ilike(f'%{query}%') |
                    Community.description.ilike(f'%{query}%')
                )

            if category:
                search_query = search_query.filter_by(category=category)

            communities = search_query.limit(limit).all()

            return [community.to_dict() for community in communities]

        except Exception as e:
            logger.error(f"Topluluk arama hatası: {str(e)}")
            return []


# Global servis instance'ı
community_service = CommunityService()