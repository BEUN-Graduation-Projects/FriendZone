from backend.app import db
from backend.models.user_model import User
from backend.models.community_model import Community
from backend.models.similarity_model import UserSimilarity
import logging
from datetime import datetime

# Logger setup
logger = logging.getLogger(__name__)


def seed_personality_questions():
    """Kişilik testi sorularını döndür"""
    return [
        {
            "id": 1,
            "question": "Sosyal ortamlarda nasıl hissedersiniz?",
            "options": [
                {"value": "introvert", "text": "Sessiz ve gözlemci"},
                {"value": "extrovert", "text": "Enerjik ve konuşkan"},
                {"value": "ambivert", "text": "Duruma göre değişir"}
            ]
        },
        {
            "id": 2,
            "question": "Problem çözerken hangi yaklaşımı tercih edersiniz?",
            "options": [
                {"value": "analytical", "text": "Mantıksal analiz"},
                {"value": "creative", "text": "Yaratıcı çözümler"},
                {"value": "practical", "text": "Pratik yaklaşımlar"}
            ]
        },
        {
            "id": 3,
            "question": "Plan yapma konusunda nasılsınız?",
            "options": [
                {"value": "organized", "text": "Detaylı plan yaparım"},
                {"value": "flexible", "text": "Esnek ve spontane"},
                {"value": "balanced", "text": "Orta yol bulurum"}
            ]
        },
        {
            "id": 4,
            "question": "Takım çalışmasında hangi rolü alırsınız?",
            "options": [
                {"value": "leader", "text": "Liderlik ederim"},
                {"value": "supporter", "text": "Destek sağlarım"},
                {"value": "specialist", "text": "Uzmanlık alanımda katkı sağlarım"}
            ]
        },
        {
            "id": 5,
            "question": "Yeni insanlarla tanışmak sizin için?",
            "options": [
                {"value": "exciting", "text": "Heyecan verici"},
                {"value": "challenging", "text": "Zorlayıcı"},
                {"value": "neutral", "text": "Nötr"}
            ]
        }
    ]


def seed_hobbies_categories():
    """Hobi kategorilerini döndür"""
    return [
        {
            "id": "sports",
            "name": "Spor ve Fitness",
            "activities": ["Futbol", "Basketbol", "Yüzme", "Koşu", "Yoga", "Fitness"]
        },
        {
            "id": "arts",
            "name": "Sanat ve Tasarım",
            "activities": ["Resim", "Müzik", "Fotoğrafçılık", "Dans", "Tiyatro", "Yazarlık"]
        },
        {
            "id": "technology",
            "name": "Teknoloji ve Bilim",
            "activities": ["Programlama", "Robotik", "AI/Makine Öğrenimi", "Elektronik", "Veri Analizi"]
        },
        {
            "id": "outdoor",
            "name": "Açık Hava ve Doğa",
            "activities": ["Doğa Yürüyüşü", "Kamp", "Dağcılık", "Bisiklet", "Balıkçılık"]
        },
        {
            "id": "education",
            "name": "Eğitim ve Gelişim",
            "activities": ["Kitap Okuma", "Dil Öğrenme", "Online Kurslar", "Araştırma", "Sunum Hazırlama"]
        },
        {
            "id": "social",
            "name": "Sosyal ve Topluluk",
            "activities": ["Gönüllülük", "Kulüp Aktiviteleri", "Organizasyon", "Network", "Mentorluk"]
        }
    ]


def create_sample_users():
    """Örnek kullanıcılar oluştur"""
    sample_users = [
        {
            "name": "Ahmet Yılmaz",
            "email": "ahmet@university.edu.tr",
            "password": "hashed_password_123",
            "personality_type": "analytical_introvert",
            "hobbies": ["Programlama", "Kitap Okuma", "Müzik"],
            "university": "İstanbul Teknik Üniversitesi",
            "department": "Bilgisayar Mühendisliği"
        },
        {
            "name": "Ayşe Demir",
            "email": "ayse@university.edu.tr",
            "password": "hashed_password_123",
            "personality_type": "creative_ambivert",
            "hobbies": ["Resim", "Dans", "Doğa Yürüyüşü"],
            "university": "Boğaziçi Üniversitesi",
            "department": "Psikoloji"
        },
        {
            "name": "Mehmet Kaya",
            "email": "mehmet@university.edu.tr",
            "password": "hashed_password_123",
            "personality_type": "social_extrovert",
            "hobbies": ["Futbol", "Gönüllülük", "Network"],
            "university": "Orta Doğu Teknik Üniversitesi",
            "department": "İşletme"
        },
        {
            "name": "Zeynep Şahin",
            "email": "zeynep@university.edu.tr",
            "password": "hashed_password_123",
            "personality_type": "organized_leader",
            "hobbies": ["Yoga", "Dil Öğrenme", "Organizasyon"],
            "university": "Hacettepe Üniversitesi",
            "department": "Tıp"
        }
    ]
    return sample_users


def create_sample_communities():
    """Örnek topluluklar oluştur"""
    sample_communities = [
        {
            "name": "Teknoloji Meraklıları",
            "description": "Yazılım, AI ve teknoloji trendleri hakkında konuşmak isteyen öğrenciler",
            "category": "technology",
            "tags": ["programming", "ai", "innovation"]
        },
        {
            "name": "Spor ve Sağlık",
            "description": "Fitness, spor aktiviteleri ve sağlıklı yaşam üzerine paylaşımlar",
            "category": "sports",
            "tags": ["fitness", "health", "sports"]
        },
        {
            "name": "Sanat ve Kültür",
            "description": "Resim, müzik, tiyatro ve diğer sanat formlarını sevenler",
            "category": "arts",
            "tags": ["art", "music", "culture"]
        },
        {
            "name": "Doğa Kaşifleri",
            "description": "Doğa yürüyüşü, kamp ve açık hava aktiviteleri sevenler",
            "category": "outdoor",
            "tags": ["nature", "hiking", "camping"]
        }
    ]
    return sample_communities


def seed_database(app):
    """Veritabanını örnek verilerle doldur"""
    try:
        with app.app_context():
            # Kullanıcıları oluştur
            sample_users = create_sample_users()
            for user_data in sample_users:
                user = User(**user_data)
                db.session.add(user)

            # Toplulukları oluştur
            sample_communities = create_sample_communities()
            for community_data in sample_communities:
                community = Community(**community_data)
                db.session.add(community)

            # Değişiklikleri kaydet
            db.session.commit()
            logger.info("✅ Örnek veriler başarıyla eklendi")

            return {
                "success": True,
                "message": f"{len(sample_users)} kullanıcı ve {len(sample_communities)} topluluk eklendi"
            }

    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ Veritabanı seed hatası: {str(e)}")
        return {
            "success": False,
            "message": f"Seed işlemi başarısız: {str(e)}"
        }


def clear_database(app):
    """Veritabanını temizle (sadece geliştirme için)"""
    try:
        with app.app_context():
            # Tabloları temizle
            db.session.query(UserSimilarity).delete()
            db.session.query(Community).delete()
            db.session.query(User).delete()
            db.session.commit()
            logger.info("🗑️ Veritabanı temizlendi")

    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ Veritabanı temizleme hatası: {str(e)}")
        raise


if __name__ == "__main__":
    from backend.app import create_app

    app = create_app()

    # Veritabanını seed et
    result = seed_database(app)
    print(result["message"])