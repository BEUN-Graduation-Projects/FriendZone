import numpy as np
from typing import List, Dict, Any, Tuple
import logging
from .similarity_engine import SimilarityEngine

logger = logging.getLogger(__name__)


class CommunityAssigner:
    """Kullanıcıları topluluklara atama sınıfı"""

    def __init__(self, similarity_engine: SimilarityEngine, min_community_size: int = 3, max_community_size: int = 10):
        self.similarity_engine = similarity_engine
        self.min_community_size = min_community_size
        self.max_community_size = max_community_size
        self.communities = []  # Topluluk listesi: [{"id": str, "members": List[str], "compatibility": float}]

    def assign_user_to_community(self, user_id: str, user_data: Dict[str, Any]) -> str:
        """Kullanıcıyı uygun topluluğa ata veya yeni topluluk oluştur"""
        try:
            # Önce kullanıcıyı similarity engine'e ekle
            self.similarity_engine.add_user(user_id, user_data)

            # Mevcut toplulukları kontrol et
            best_community_id = self._find_best_community(user_id)

            if best_community_id:
                # Kullanıcıyı mevcut topluluğa ekle
                self._add_user_to_community(user_id, best_community_id)
                logger.info(f"Kullanıcı {user_id} mevcut topluluğa eklendi: {best_community_id}")
                return best_community_id
            else:
                # Yeni topluluk oluştur
                new_community_id = self._create_new_community(user_id)
                logger.info(f"Yeni topluluk oluşturuldu: {new_community_id}")
                return new_community_id

        except Exception as e:
            logger.error(f"Kullanıcı atama hatası: {str(e)}")
            return self._create_new_community(user_id)  # Fallback

    def _find_best_community(self, user_id: str, min_compatibility: float = 0.6) -> str:
        """Kullanıcı için en uygun topluluğu bul"""
        best_community_id = None
        best_score = min_compatibility

        for community in self.communities:
            # Topluluk dolu mu kontrol et
            if len(community['members']) >= self.max_community_size:
                continue

            # Uyumluluk skorunu hesapla
            compatibility = self._calculate_community_compatibility(user_id, community['members'])

            if compatibility > best_score:
                best_score = compatibility
                best_community_id = community['id']

        return best_community_id

    def _calculate_community_compatibility(self, user_id: str, community_members: List[str]) -> float:
        """Kullanıcı ile topluluk arasındaki uyumluluğu hesapla"""
        if not community_members:
            return 1.0

        total_similarity = 0.0
        valid_pairs = 0

        for member_id in community_members:
            if member_id != user_id:
                similarity = self.similarity_engine.calculate_similarity(user_id, member_id)
                total_similarity += similarity
                valid_pairs += 1

        return total_similarity / valid_pairs if valid_pairs > 0 else 0.0

    def _create_new_community(self, user_id: str) -> str:
        """Yeni topluluk oluştur"""
        community_id = f"community_{len(self.communities) + 1:03d}"

        new_community = {
            "id": community_id,
            "members": [user_id],
            "compatibility": 1.0,  # Tek kullanıcılı topluluk
            "category": self._detect_community_category([user_id])
        }

        self.communities.append(new_community)
        return community_id

    def _add_user_to_community(self, user_id: str, community_id: str):
        """Kullanıcıyı topluluğa ekle"""
        for community in self.communities:
            if community['id'] == community_id:
                community['members'].append(user_id)

                # Uyumluluk skorunu güncelle
                community['compatibility'] = self.similarity_engine.calculate_group_compatibility(community['members'])
                break

    def _detect_community_category(self, member_ids: List[str]) -> str:
        """Topluluk kategorisini tespit et"""
        if not member_ids:
            return "general"

        # Üyelerin hobilerine göre kategori belirle
        all_hobbies = []
        for user_id in member_ids:
            user_data = self.similarity_engine.user_data.get(user_id, {})
            hobbies = user_data.get('hobbies', [])
            all_hobbies.extend(hobbies)

        # En yaygın hobi kategorisini bul
        category_scores = {
            "technology": 0,
            "sports": 0,
            "arts": 0,
            "outdoor": 0,
            "education": 0,
            "social": 0
        }

        tech_keywords = ["programlama", "yazılım", "ai", "teknoloji", "robotik"]
        sports_keywords = ["futbol", "basketbol", "yüzme", "spor", "fitness", "yoga"]
        arts_keywords = ["resim", "müzik", "sanat", "dans", "tiyatro", "fotoğraf"]
        outdoor_keywords = ["doğa", "kamp", "yürüyüş", "bisiklet", "açık hava"]
        education_keywords = ["kitap", "okuma", "dil", "kurs", "eğitim", "araştırma"]
        social_keywords = ["gönüllü", "network", "organizasyon", "topluluk"]

        for hobby in all_hobbies:
            hobby_lower = hobby.lower()

            if any(keyword in hobby_lower for keyword in tech_keywords):
                category_scores["technology"] += 1
            if any(keyword in hobby_lower for keyword in sports_keywords):
                category_scores["sports"] += 1
            if any(keyword in hobby_lower for keyword in arts_keywords):
                category_scores["arts"] += 1
            if any(keyword in hobby_lower for keyword in outdoor_keywords):
                category_scores["outdoor"] += 1
            if any(keyword in hobby_lower for keyword in education_keywords):
                category_scores["education"] += 1
            if any(keyword in hobby_lower for keyword in social_keywords):
                category_scores["social"] += 1

        # En yüksek skorlu kategoriyi döndür
        return max(category_scores.items(), key=lambda x: x[1])[0]

    def get_community_recommendations(self, user_id: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Kullanıcı için topluluk önerileri oluştur"""
        try:
            recommendations = []

            for community in self.communities:
                if user_id in community['members']:
                    continue  # Zaten üye olduğu toplulukları atla

                compatibility = self._calculate_community_compatibility(user_id, community['members'])

                if compatibility > 0.5:  # Minimum uyumluluk eşiği
                    recommendations.append({
                        "community_id": community['id'],
                        "compatibility_score": compatibility,
                        "member_count": len(community['members']),
                        "category": community.get('category', 'general')
                    })

            # Uyumluluk skoruna göre sırala
            recommendations.sort(key=lambda x: x['compatibility_score'], reverse=True)
            return recommendations[:top_k]

        except Exception as e:
            logger.error(f"Topluluk önerisi hatası: {str(e)}")
            return []

    def optimize_communities(self):
        """Toplulukları optimize et (periodik olarak çalıştırılabilir)"""
        try:
            # Kümeleme ile toplulukları yeniden düzenle
            cluster_assignments = self.similarity_engine.find_user_clusters(len(self.communities) or 4)

            if not cluster_assignments:
                return

            # Yeni topluluklar oluştur
            new_communities = []
            cluster_members = {}

            # Kümeleri grupla
            for user_id, cluster_id in cluster_assignments.items():
                if cluster_id not in cluster_members:
                    cluster_members[cluster_id] = []
                cluster_members[cluster_id].append(user_id)

            # Her küme için topluluk oluştur
            for cluster_id, members in cluster_members.items():
                if len(members) >= self.min_community_size:
                    # Küme yeterince büyükse topluluk oluştur
                    community_id = f"optimized_community_{cluster_id:03d}"
                    compatibility = self.similarity_engine.calculate_group_compatibility(members)

                    new_communities.append({
                        "id": community_id,
                        "members": members,
                        "compatibility": compatibility,
                        "category": self._detect_community_category(members)
                    })
                else:
                    # Küçük kümeleri genel topluluklara dağıt
                    for member in members:
                        self._assign_small_cluster_user(member, new_communities)

            self.communities = new_communities
            logger.info(f"Topluluklar optimize edildi: {len(self.communities)} topluluk")

        except Exception as e:
            logger.error(f"Topluluk optimizasyon hatası: {str(e)}")

    def _assign_small_cluster_user(self, user_id: str, communities: List[Dict[str, Any]]):
        """Küçük kümedeki kullanıcıyı uygun topluluğa ata"""
        best_community = None
        best_score = 0.5  # Minimum eşik

        for community in communities:
            compatibility = self._calculate_community_compatibility(user_id, community['members'])
            if compatibility > best_score and len(community['members']) < self.max_community_size:
                best_score = compatibility
                best_community = community

        if best_community:
            best_community['members'].append(user_id)
            best_community['compatibility'] = self.similarity_engine.calculate_group_compatibility(
                best_community['members'])
        else:
            # Yeni topluluk oluştur
            self._create_new_community(user_id)