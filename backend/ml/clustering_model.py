import numpy as np
import joblib
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import logging
import os
from typing import Dict, List, Any, Tuple

logger = logging.getLogger(__name__)


class ClusteringModel:
    """Kullanıcı kümeleme modeli sınıfı"""

    def __init__(self, n_clusters: int = 5, random_state: int = 42):
        self.n_clusters = n_clusters
        self.random_state = random_state
        self.model = KMeans(n_clusters=n_clusters, random_state=random_state)
        self.is_trained = False
        self.cluster_centers_ = None
        self.labels_ = None

    def train(self, embeddings: np.ndarray) -> Dict[str, Any]:
        """Modeli kullanıcı embedding'leri üzerinde eğit"""
        try:
            if len(embeddings) < self.n_clusters:
                logger.warning(f"Yeterli veri yok: {len(embeddings)} örnek, {self.n_clusters} küme")
                return {"success": False, "message": "Yeterli veri yok"}

            # Modeli eğit
            self.labels_ = self.model.fit_predict(embeddings)
            self.cluster_centers_ = self.model.cluster_centers_
            self.is_trained = True

            # Kümeleme kalitesini değerlendir
            if len(np.unique(self.labels_)) > 1:
                silhouette_avg = silhouette_score(embeddings, self.labels_)
            else:
                silhouette_avg = 0.0

            # Küme istatistikleri
            cluster_counts = np.bincount(self.labels_)
            cluster_stats = {
                f"cluster_{i}": int(count) for i, count in enumerate(cluster_counts)
            }

            logger.info(f"Kümeleme modeli eğitildi: {self.n_clusters} küme, silhouette score: {silhouette_avg:.3f}")

            return {
                "success": True,
                "silhouette_score": float(silhouette_avg),
                "cluster_stats": cluster_stats,
                "n_clusters": self.n_clusters,
                "n_samples": len(embeddings)
            }

        except Exception as e:
            logger.error(f"Kümeleme eğitim hatası: {str(e)}")
            return {"success": False, "error": str(e)}

    def predict(self, embeddings: np.ndarray) -> np.ndarray:
        """Yeni embedding'ler için küme tahmini yap"""
        try:
            if not self.is_trained:
                raise ValueError("Model eğitilmemiş, önce train() metodunu çağırın")

            if len(embeddings.shape) == 1:
                embeddings = embeddings.reshape(1, -1)

            return self.model.predict(embeddings)

        except Exception as e:
            logger.error(f"Küme tahmin hatası: {str(e)}")
            return np.array([-1] * len(embeddings))  # Geçersiz küme

    def find_optimal_clusters(self, embeddings: np.ndarray, max_k: int = 10) -> int:
        """Optimal küme sayısını bul (Elbow method)"""
        try:
            if len(embeddings) < 2:
                return 1

            max_k = min(max_k, len(embeddings) - 1)
            inertias = []
            k_range = range(1, max_k + 1)

            for k in k_range:
                kmeans = KMeans(n_clusters=k, random_state=self.random_state)
                kmeans.fit(embeddings)
                inertias.append(kmeans.inertia_)

            # Elbow point hesapla (basit yaklaşım)
            if len(inertias) >= 3:
                # İkinci türevdeki en büyük düşüşü bul
                differences = np.diff(inertias)
                second_diff = np.diff(differences)
                optimal_k = np.argmax(np.abs(second_diff)) + 2  # +2 because of double diff
            else:
                optimal_k = 2  # Varsayılan

            optimal_k = max(2, min(optimal_k, max_k))
            logger.info(f"Optimal küme sayısı bulundu: {optimal_k}")

            return optimal_k

        except Exception as e:
            logger.error(f"Optimal küme bulma hatası: {str(e)}")
            return 2  # Varsayılan

    def get_cluster_characteristics(self, user_data: List[Dict], embeddings: np.ndarray) -> Dict[int, Dict[str, Any]]:
        """Kümelerin karakteristik özelliklerini analiz et"""
        try:
            if not self.is_trained:
                return {}

            cluster_chars = {}

            for cluster_id in range(self.n_clusters):
                # Küme üyelerini bul
                cluster_mask = (self.labels_ == cluster_id)
                cluster_embeddings = embeddings[cluster_mask]
                cluster_users = [user_data[i] for i in range(len(user_data)) if cluster_mask[i]]

                if len(cluster_users) == 0:
                    continue

                # Kişilik tipleri analizi
                personality_types = [user.get('personality_type', '') for user in cluster_users]
                common_personality = self._find_common_pattern(personality_types)

                # Hobiler analizi
                all_hobbies = []
                for user in cluster_users:
                    hobbies = user.get('hobbies', [])
                    if isinstance(hobbies, list):
                        all_hobbies.extend(hobbies)

                common_hobbies = self._find_common_items(all_hobbies, top_n=5)

                # Üniversite/Bölüm dağılımı
                universities = [user.get('university', '') for user in cluster_users if user.get('university')]
                common_university = self._find_common_items(universities, top_n=3)

                cluster_chars[cluster_id] = {
                    "size": len(cluster_users),
                    "common_personality": common_personality,
                    "common_hobbies": common_hobbies,
                    "common_universities": common_university,
                    "cluster_center": self.cluster_centers_[
                        cluster_id].tolist() if self.cluster_centers_ is not None else []
                }

            return cluster_chars

        except Exception as e:
            logger.error(f"Küme karakteristik analiz hatası: {str(e)}")
            return {}

    def _find_common_pattern(self, items: List[str]) -> str:
        """Ortak pattern'leri bul"""
        if not items:
            return "unknown"

        # Kişilik tiplerindeki ortak kelimeleri bul
        all_words = []
        for item in items:
            if isinstance(item, str):
                words = item.split('_')
                all_words.extend(words)

        from collections import Counter
        word_counts = Counter(all_words)
        common_words = [word for word, count in word_counts.most_common(2) if count > 1]

        return '_'.join(common_words) if common_words else "mixed"

    def _find_common_items(self, items: List[str], top_n: int = 5) -> List[str]:
        """En yaygın item'leri bul"""
        from collections import Counter
        item_counts = Counter(items)
        return [item for item, count in item_counts.most_common(top_n)]

    def save_model(self, filepath: str):
        """Modeli kaydet"""
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)

            model_data = {
                'model': self.model,
                'is_trained': self.is_trained,
                'cluster_centers_': self.cluster_centers_,
                'labels_': self.labels_,
                'n_clusters': self.n_clusters,
                'random_state': self.random_state
            }

            joblib.dump(model_data, filepath)
            logger.info(f"Kümeleme modeli kaydedildi: {filepath}")

        except Exception as e:
            logger.error(f"Model kaydetme hatası: {str(e)}")

    def load_model(self, filepath: str) -> bool:
        """Modeli yükle"""
        try:
            if os.path.exists(filepath):
                model_data = joblib.load(filepath)
                self.model = model_data['model']
                self.is_trained = model_data['is_trained']
                self.cluster_centers_ = model_data['cluster_centers_']
                self.labels_ = model_data['labels_']
                self.n_clusters = model_data['n_clusters']
                self.random_state = model_data['random_state']

                logger.info(f"Kümeleme modeli yüklendi: {filepath}")
                return True
            else:
                logger.warning(f"Model dosyası bulunamadı: {filepath}")
                return False

        except Exception as e:
            logger.error(f"Model yükleme hatası: {str(e)}")
            return False

    def get_similar_users_in_cluster(self, user_embedding: np.ndarray, cluster_id: int,
                                     all_embeddings: np.ndarray, all_user_ids: List[str],
                                     top_k: int = 5) -> List[Tuple[str, float]]:
        """Aynı kümedeki benzer kullanıcıları bul"""
        try:
            if not self.is_trained:
                return []

            # Aynı kümedeki kullanıcıları bul
            cluster_mask = (self.labels_ == cluster_id)
            cluster_embeddings = all_embeddings[cluster_mask]
            cluster_user_ids = [all_user_ids[i] for i in range(len(all_user_ids)) if cluster_mask[i]]

            if len(cluster_embeddings) == 0:
                return []

            # Benzerlik hesapla
            from sklearn.metrics.pairwise import cosine_similarity

            if len(user_embedding.shape) == 1:
                user_embedding = user_embedding.reshape(1, -1)

            similarities = cosine_similarity(user_embedding, cluster_embeddings)[0]

            # Benzer kullanıcıları sırala
            similar_users = []
            for i, similarity in enumerate(similarities):
                similar_users.append((cluster_user_ids[i], float(similarity)))

            # Benzerliğe göre sırala ve top_k kadar al
            similar_users.sort(key=lambda x: x[1], reverse=True)
            return similar_users[:top_k]

        except Exception as e:
            logger.error(f"Küme içi benzer kullanıcı bulma hatası: {str(e)}")
            return []


# Model yöneticisi sınıfı
class ClusteringModelManager:
    """Kümeleme modeli yöneticisi"""

    def __init__(self, models_dir: str = "backend/ml/models"):
        self.models_dir = models_dir
        self.models = {}  # model_name -> ClusteringModel
        os.makedirs(models_dir, exist_ok=True)

    def create_model(self, model_name: str, n_clusters: int = 5) -> ClusteringModel:
        """Yeni model oluştur"""
        model = ClusteringModel(n_clusters=n_clusters)
        self.models[model_name] = model
        return model

    def get_model(self, model_name: str) -> ClusteringModel:
        """Modeli getir"""
        return self.models.get(model_name)

    def save_all_models(self):
        """Tüm modelleri kaydet"""
        for model_name, model in self.models.items():
            filepath = os.path.join(self.models_dir, f"{model_name}.pkl")
            model.save_model(filepath)

    def load_model(self, model_name: str) -> bool:
        """Modeli diskten yükle"""
        filepath = os.path.join(self.models_dir, f"{model_name}.pkl")
        model = ClusteringModel()
        success = model.load_model(filepath)

        if success:
            self.models[model_name] = model

        return success


# Global model manager instance
clustering_manager = ClusteringModelManager()

if __name__ == "__main__":
    # Test kodu
    print("ClusteringModel test ediliyor...")

    # Örnek embedding'ler oluştur
    np.random.seed(42)
    test_embeddings = np.random.rand(100, 10)

    # Model oluştur ve eğit
    model = ClusteringModel(n_clusters=3)
    result = model.train(test_embeddings)

    print("Eğitim sonucu:", result)

    # Modeli kaydet
    model.save_model("backend/ml/clustering_model.pkl")
    print("Model kaydedildi")