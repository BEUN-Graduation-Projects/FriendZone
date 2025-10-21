import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
import logging
import os
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class SimilarityEngine:
    """Kullanıcı benzerlik hesaplama motoru"""

    def __init__(self, preprocessor):
        self.preprocessor = preprocessor
        self.user_embeddings = {}  # user_id -> embedding
        self.user_data = {}  # user_id -> user_data

    def add_user(self, user_id: str, user_data: Dict[str, Any]):
        """Kullanıcı ekle ve embedding oluştur"""
        try:
            embedding = self.preprocessor.create_user_embedding(
                user_data.get('personality_type'),
                user_data.get('hobbies', []),
                user_data.get('university'),
                user_data.get('department')
            )

            if embedding is not None:
                self.user_embeddings[user_id] = embedding
                self.user_data[user_id] = user_data
                logger.info(f"Kullanıcı eklendi: {user_id}")

        except Exception as e:
            logger.error(f"Kullanıcı ekleme hatası: {str(e)}")

    def calculate_similarity(self, user_id1: str, user_id2: str) -> float:
        """İki kullanıcı arasındaki benzerliği hesapla"""
        try:
            if user_id1 not in self.user_embeddings or user_id2 not in self.user_embeddings:
                return 0.0

            embedding1 = self.user_embeddings[user_id1].reshape(1, -1)
            embedding2 = self.user_embeddings[user_id2].reshape(1, -1)

            similarity = cosine_similarity(embedding1, embedding2)[0][0]
            return float(similarity)

        except Exception as e:
            logger.error(f"Benzerlik hesaplama hatası: {str(e)}")
            return 0.0

    def find_similar_users(self, user_id: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Benzer kullanıcıları bul"""
        try:
            if user_id not in self.user_embeddings:
                return []

            target_embedding = self.user_embeddings[user_id].reshape(1, -1)
            similarities = []

            for other_id, embedding in self.user_embeddings.items():
                if other_id == user_id:
                    continue

                other_embedding = embedding.reshape(1, -1)
                similarity = cosine_similarity(target_embedding, other_embedding)[0][0]
                similarities.append((other_id, similarity))

            # Benzerliğe göre sırala
            similarities.sort(key=lambda x: x[1], reverse=True)

            # Top_k kadar döndür
            results = []
            for other_id, similarity in similarities[:top_k]:
                user_info = self.user_data[other_id].copy()
                user_info['similarity_score'] = similarity
                user_info['user_id'] = other_id
                results.append(user_info)

            return results

        except Exception as e:
            logger.error(f"Benzer kullanıcı bulma hatası: {str(e)}")
            return []

    def find_user_clusters(self, n_clusters: int = 4) -> Dict[str, int]:
        """Kullanıcıları kümelere ayır"""
        try:
            if len(self.user_embeddings) < n_clusters:
                # Yeterli kullanıcı yoksa, herkesi aynı kümeye ata
                return {user_id: 0 for user_id in self.user_embeddings.keys()}

            # Embedding'leri numpy array'e çevir
            user_ids = list(self.user_embeddings.keys())
            embeddings = np.array([self.user_embeddings[uid] for uid in user_ids])

            # K-means kümeleme
            kmeans = KMeans(n_clusters=min(n_clusters, len(user_ids)), random_state=42)
            clusters = kmeans.fit_predict(embeddings)

            # Kullanıcı ID -> küme eşlemesi
            cluster_assignments = {}
            for user_id, cluster in zip(user_ids, clusters):
                cluster_assignments[user_id] = int(cluster)

            logger.info(f"{len(user_ids)} kullanıcı {len(set(clusters))} kümeye ayrıldı")
            return cluster_assignments

        except Exception as e:
            logger.error(f"Kümeleme hatası: {str(e)}")
            return {}

    def calculate_group_compatibility(self, user_ids: List[str]) -> float:
        """Grup uyumluluğunu hesapla"""
        try:
            if len(user_ids) < 2:
                return 1.0

            total_similarity = 0.0
            pair_count = 0

            for i in range(len(user_ids)):
                for j in range(i + 1, len(user_ids)):
                    similarity = self.calculate_similarity(user_ids[i], user_ids[j])
                    total_similarity += similarity
                    pair_count += 1

            return total_similarity / pair_count if pair_count > 0 else 0.0

        except Exception as e:
            logger.error(f"Grup uyumluluğu hesaplama hatası: {str(e)}")
            return 0.0

    def save_embeddings(self, filepath: str):
        """Embedding'leri kaydet"""
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            np.save(filepath, self.user_embeddings)
            logger.info(f"Embedding'ler kaydedildi: {filepath}")

        except Exception as e:
            logger.error(f"Embedding kaydetme hatası: {str(e)}")

    def load_embeddings(self, filepath: str):
        """Embedding'leri yükle"""
        try:
            if os.path.exists(filepath):
                self.user_embeddings = np.load(filepath, allow_pickle=True).item()
                logger.info(f"Embedding'ler yüklendi: {filepath}")

        except Exception as e:
            logger.error(f"Embedding yükleme hatası: {str(e)}")