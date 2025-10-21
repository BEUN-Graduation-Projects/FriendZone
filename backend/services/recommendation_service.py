import logging
from typing import List, Dict, Any
from backend.models.user_model import User
from backend.models.community_model import Community
from backend.ml.preprocessing import DataPreprocessor
from backend.ml.similarity_engine import SimilarityEngine
from backend.ml.community_assigner import CommunityAssigner

logger = logging.getLogger(__name__)


class RecommendationService:
    """Öneri servisi - ML tabanlı öneriler"""

    def __init__(self):
        self.preprocessor = DataPreprocessor()
        self.similarity_engine = SimilarityEngine(self.preprocessor)
        self.community_assigner = CommunityAssigner(self.similarity_engine)
        self._initialize_ml_models()

    def _initialize_ml_models(self):
        """ML modellerini başlat"""
        try:
            # Testi tamamlamış kullanıcıları yükle
            users_with_tests = User.get_users_with_test_results()

            if users_with_tests:
                user_data = []
                for user in users_with_tests:
                    user_dict = user.to_dict()
                    user_data.append(user_dict)
                    self.similarity_engine.add_user(str(user.id), user_dict)

                # Preprocessor'ı eğit
                self.preprocessor.fit(user_data)

                logger.info(f"ML modelleri {len(users_with_tests)} kullanıcı ile başlatıldı")
            else:
                logger.info("ML modelleri başlatıldı (henüz kullanıcı yok)")

        except Exception as e:
            logger.error(f"ML model başlatma hatası: {str(e)}")

    def get_similar_users(self, user_id: int, limit: int = 5) -> List[Dict[str, Any]]:
        """Benzer kullanıcıları getir"""
        try:
            user = User.query.get(user_id)
            if not user or not user.is_test_completed:
                return []

            # ML ile benzer kullanıcıları bul
            similar_users = self.similarity_engine.find_similar_users(
                str(user_id), top_k=limit
            )

            return similar_users

        except Exception as e:
            logger.error(f"Benzer kullanıcı öneri hatası: {str(e)}")
            return self._get_fallback_similar_users(user_id, limit)

    def get_community_recommendations(self, user_id: int, limit: int = 5) -> List[Dict[str, Any]]:
        """Topluluk önerileri getir"""
        try:
            user = User.query.get(user_id)
            if not user or not user.is_test_completed:
                return self._get_fallback_communities(limit)

            # ML ile topluluk önerileri
            user_data = user.to_dict()
            recommendations = self.community_assigner.get_community_recommendations(
                str(user_id), top_k=limit
            )

            # Önerileri zenginleştir
            enriched_recommendations = []
            for rec in recommendations:
                community = Community.query.filter_by(
                    id=rec['community_id'].replace('community_', '')
                ).first()

                if community:
                    enriched_rec = community.to_dict()
                    enriched_rec['compatibility_score'] = rec['compatibility_score']
                    enriched_recommendations.append(enriched_rec)

            return enriched_recommendations

        except Exception as e:
            logger.error(f"Topluluk öneri hatası: {str(e)}")
            return self._get_fallback_communities(limit)

    def assign_user_to_community(self, user_id: int) -> str:
        """Kullanıcıyı topluluğa ata"""
        try:
            user = User.query.get(user_id)
            if not user or not user.is_test_completed:
                return "community_001"  # Varsayılan topluluk

            user_data = user.to_dict()
            community_id = self.community_assigner.assign_user_to_community(
                str(user_id), user_data
            )

            logger.info(f"Kullanıcı {user_id} topluluğa atandı: {community_id}")
            return community_id

        except Exception as e:
            logger.error(f"Topluluk atama hatası: {str(e)}")
            return "community_001"

    def get_personalized_suggestions(self, user_id: int) -> Dict[str, Any]:
        """Kişiselleştirilmiş öneriler getir"""
        try:
            user = User.query.get(user_id)
            if not user:
                return {}

            suggestions = {
                "similar_users": self.get_similar_users(user_id, 3),
                "community_recommendations": self.get_community_recommendations(user_id, 3),
                "personalized_activities": self._get_personalized_activities(user),
                "learning_recommendations": self._get_learning_recommendations(user)
            }

            return suggestions

        except Exception as e:
            logger.error(f"Kişiselleştirilmiş öneri hatası: {str(e)}")
            return {}

    def _get_personalized_activities(self, user: User) -> List[str]:
        """Kişiselleştirilmiş etkinlik önerileri"""
        personality = user.personality_type or ""
        hobbies = user.get_hobbies_list()

        activities = []

        # Kişilik tipine göre öneriler
        if 'introvert' in personality:
            activities.extend([
                "Bireysel proje çalışması",
                "Küçük grup tartışmaları",
                "Online workshop katılımı"
            ])
        elif 'extrovert' in personality:
            activities.extend([
                "Sosyal etkinlik organizasyonu",
                "Büyük grup sunumları",
                "Network etkinlikleri"
            ])

        # Hobilerine göre öneriler
        if any(hobby in hobbies for hobby in ['Programlama', 'Yazılım', 'Teknoloji']):
            activities.extend([
                "Hackathon katılımı",
                "Open source proje geliştirme",
                "Teknoloji workshop'ları"
            ])

        if any(hobby in hobbies for hobby in ['Resim', 'Müzik', 'Sanat']):
            activities.extend([
                "Yaratıcı atölye çalışmaları",
                "Sergi ziyaretleri",
                "Sanat projeleri"
            ])

        return activities[:5] if activities else [
            "Haftalık topluluk buluşması",
            "Ortak kitap okuma",
            "Skill paylaşım oturumları"
        ]

    def _get_learning_recommendations(self, user: User) -> List[str]:
        """Öğrenme önerileri"""
        department = user.department or ""
        hobbies = user.get_hobbies_list()

        recommendations = []

        # Bölüme göre öneriler
        if 'Bilgisayar' in department or 'Mühendis' in department:
            recommendations.extend([
                "Python ve veri bilimi kursları",
                "Web geliştirme tutorial'ları",
                "AI/Makine öğrenimi temelleri"
            ])
        elif 'İşletme' in department or 'Ekonomi' in department:
            recommendations.extend([
                "Girişimcilik webinar'ları",
                "Pazarlama stratejileri",
                "Finansal okuryazarlık"
            ])

        # Hobilerine göre öneriler
        if 'Dil Öğrenme' in hobbies:
            recommendations.append("Online dil kursları ve pratik grupları")

        if 'Kitap Okuma' in hobbies:
            recommendations.append("Kitap kulübü ve okuma listeleri")

        return recommendations[:3] if recommendations else [
            "Online kurs platformları",
            "Webinar ve workshop takibi",
            "Akran öğrenme grupları"
        ]

    def _get_fallback_similar_users(self, user_id: int, limit: int) -> List[Dict[str, Any]]:
        """Fallback benzer kullanıcılar"""
        # Aynı üniversite/bölümden kullanıcılar
        user = User.query.get(user_id)
        if not user:
            return []

        similar_users = User.query.filter(
            User.id != user_id,
            User.is_test_completed == True,
            User.is_active == True
        ).limit(limit).all()

        return [
            {
                'user': u.to_dict(),
                'similarity_score': 0.7  # Varsayılan skor
            }
            for u in similar_users
        ]

    def _get_fallback_communities(self, limit: int) -> List[Dict[str, Any]]:
        """Fallback topluluk önerileri"""
        communities = Community.query.filter_by(
            is_active=True
        ).limit(limit).all()

        return [
            {
                **community.to_dict(),
                'compatibility_score': 0.8  # Varsayılan skor
            }
            for community in communities
        ]


# Global servis instance'ı
recommendation_service = RecommendationService()