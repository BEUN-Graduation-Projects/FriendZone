import pandas as pd
import numpy as np
import json
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.feature_extraction.text import TfidfVectorizer
import logging
import os

logger = logging.getLogger(__name__)


class DataPreprocessor:
    """Kullanıcı verilerini ön işleme ve özellik çıkarımı sınıfı"""

    def __init__(self):
        self.personality_encoder = LabelEncoder()
        self.hobbies_vectorizer = TfidfVectorizer(max_features=50, stop_words=None)
        self.scaler = StandardScaler()
        self.is_fitted = False

    def preprocess_personality(self, personality_data):
        """Kişilik verilerini ön işleme"""
        try:
            # Kişilik tipini vektöre çevir
            if isinstance(personality_data, str):
                # String kişilik tipini işle (örn: "analytical_introvert")
                personality_features = self._encode_personality_type(personality_data)
            elif isinstance(personality_data, dict):
                # Detaylı kişilik testi sonuçlarını işle
                personality_features = self._process_personality_test(personality_data)
            else:
                raise ValueError("Geçersiz kişilik veri formatı")

            return personality_features

        except Exception as e:
            logger.error(f"Kişilik verisi işleme hatası: {str(e)}")
            return np.zeros(10)  # Varsayılan vektör

    def _encode_personality_type(self, personality_type):
        """Kişilik tipini vektöre çevir"""
        # Kişilik boyutları
        dimensions = {
            'analytical': 0, 'creative': 1, 'practical': 2,
            'introvert': 3, 'extrovert': 4, 'ambivert': 5,
            'organized': 6, 'flexible': 7, 'balanced': 8,
            'leader': 9, 'supporter': 10, 'specialist': 11
        }

        # Vektör oluştur
        vector = np.zeros(len(dimensions))

        # Kişilik tipindeki boyutları işaretle
        for dim in personality_type.split('_'):
            if dim in dimensions:
                vector[dimensions[dim]] = 1.0

        return vector

    def _process_personality_test(self, test_results):
        """Kişilik testi sonuçlarını işle"""
        # Test sonuçlarından özellik vektörü oluştur
        features = []

        # Sosyal eğilim
        social_scores = test_results.get('social', {})
        features.extend([
            social_scores.get('introvert', 0),
            social_scores.get('extrovert', 0),
            social_scores.get('ambivert', 0)
        ])

        # Problem çözme
        problem_scores = test_results.get('problem_solving', {})
        features.extend([
            problem_scores.get('analytical', 0),
            problem_scores.get('creative', 0),
            problem_scores.get('practical', 0)
        ])

        # Planlama
        planning_scores = test_results.get('planning', {})
        features.extend([
            planning_scores.get('organized', 0),
            planning_scores.get('flexible', 0)
        ])

        return np.array(features)

    def preprocess_hobbies(self, hobbies_list):
        """Hobi listesini vektöre çevir"""
        try:
            if not hobbies_list:
                return np.zeros(50)  # Varsayılan vektör

            # Hobileri stringe çevir ve TF-IDF vektörüne dönüştür
            hobbies_text = ' '.join(hobbies_list)

            if self.is_fitted:
                hobbies_vector = self.hobbies_vectorizer.transform([hobbies_text])
            else:
                hobbies_vector = self.hobbies_vectorizer.fit_transform([hobbies_text])

            return hobbies_vector.toarray().flatten()

        except Exception as e:
            logger.error(f"Hobi verisi işleme hatası: {str(e)}")
            return np.zeros(50)

    def create_user_embedding(self, personality_data, hobbies_list, university=None, department=None):
        """Kullanıcı için embedding vektörü oluştur"""
        try:
            # Kişilik vektörü
            personality_vector = self.preprocess_personality(personality_data)

            # Hobi vektörü
            hobbies_vector = self.preprocess_hobbies(hobbies_list)

            # Ek özellikler (üniversite, bölüm - opsiyonel)
            additional_features = self._encode_additional_features(university, department)

            # Tüm vektörleri birleştir
            user_embedding = np.concatenate([
                personality_vector,
                hobbies_vector,
                additional_features
            ])

            # Ölçeklendir
            if self.is_fitted:
                user_embedding = self.scaler.transform([user_embedding])[0]
            else:
                user_embedding = self.scaler.fit_transform([user_embedding])[0]
                self.is_fitted = True

            return user_embedding

        except Exception as e:
            logger.error(f"Kullanıcı embedding oluşturma hatası: {str(e)}")
            return None

    def _encode_additional_features(self, university, department):
        """Ek özellikleri kodla (basit one-hot benzeri)"""
        # Basit hash tabanlı kodlama
        university_hash = hash(university or "") % 10 / 10.0
        department_hash = hash(department or "") % 10 / 10.0

        return np.array([university_hash, department_hash])

    def fit(self, users_data):
        """Modeli kullanıcı verileri üzerinde eğit"""
        try:
            # Tüm kullanıcı verilerini işle
            all_embeddings = []

            for user in users_data:
                embedding = self.create_user_embedding(
                    user.get('personality_type'),
                    user.get('hobbies', []),
                    user.get('university'),
                    user.get('department')
                )
                if embedding is not None:
                    all_embeddings.append(embedding)

            # Scaler'ı fit et
            if all_embeddings:
                self.scaler.fit(all_embeddings)
                self.is_fitted = True

            logger.info(f"Preprocessor {len(all_embeddings)} kullanıcı ile eğitildi")

        except Exception as e:
            logger.error(f"Preprocessor eğitim hatası: {str(e)}")

    def save_model(self, filepath):
        """Modeli kaydet"""
        import joblib

        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            joblib.dump({
                'scaler': self.scaler,
                'hobbies_vectorizer': self.hobbies_vectorizer,
                'is_fitted': self.is_fitted
            }, filepath)
            logger.info(f"Model kaydedildi: {filepath}")

        except Exception as e:
            logger.error(f"Model kaydetme hatası: {str(e)}")

    def load_model(self, filepath):
        """Modeli yükle"""
        import joblib

        try:
            model_data = joblib.load(filepath)
            self.scaler = model_data['scaler']
            self.hobbies_vectorizer = model_data['hobbies_vectorizer']
            self.is_fitted = model_data['is_fitted']
            logger.info(f"Model yüklendi: {filepath}")

        except Exception as e:
            logger.error(f"Model yükleme hatası: {str(e)}")