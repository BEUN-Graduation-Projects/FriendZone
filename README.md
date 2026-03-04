# 🧠 FriendZone

<div align="center">

![FriendZone Logo](https://img.shields.io/badge/FriendZone-University%20Social%20Platform-blue?style=for-the-badge&logo=react)
![Python](https://img.shields.io/badge/Python-3.9+-green?style=flat-square&logo=python)
![Flask](https://img.shields.io/badge/Flask-2.2.5-red?style=flat-square&logo=flask)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-blue?style=flat-square&logo=postgresql)
![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)

**Üniversite öğrencileri için AI destekli, kişilik ve hobi tabanlı sosyal topluluk platformu**

[🚀 Canlı Demo](https://friendzone-demo.com) • [📚 Dokümantasyon](docs/) • [🐛 Hata Bildir](https://github.com/BEUN-Graduation-Projects/FriendZone/issues)

</div>



## 🎯 Proje Hakkında

**FriendZone**, üniversite öğrencilerinin kişilik özellikleri ve ilgi alanlarına göre **makine öğrenimi (ML)** tabanlı bir şekilde sanal topluluklar oluşturmasını sağlayan sosyal bir platformdur. Bu proje, bir **üniversite bitirme projesi** kapsamında geliştirilmiştir.

> **Temel Misyon**: Öğrencileri sadece ortak ilgi alanlarına göre değil, aynı zamanda kişilik tiplerine göre eşleştirerek daha anlamlı ve kalıcı sosyal bağlantılar kurmalarını sağlamak.

### 🎯 Projenin Amacı

FriendZone, öğrencilerin:

- 🧍‍♂️ **Kendi kişilik tipi** ve **hobilerine** göre benzer öğrencilerle tanışmasını,
- 🧑‍🤝‍🧑 **Ortak sanal topluluklar** (community'ler) içinde etkileşime geçmesini,
- 🤖 **GPT tabanlı bir asistan** aracılığıyla grup içinde öneriler, sohbet konuları ve etkinlik fikirleri almasını sağlar.

> 💡 **Kısacası FriendZone**, "Spotify Blend" veya "Netflix öneri motoru" gibi davranır; ancak odak noktası insan eşleşmesidir.

---

## ✨ Özellikler

### 👤 Kullanıcı Yönetimi
- **Üniversite email doğrulaması** (`.edu.tr` uzantılı email zorunluluğu)
- JWT tabanlı kimlik doğrulama
- Profil yönetimi (fotoğraf, biyografi, üniversite bilgileri)

### 🧪 Kişilik Testi (16Personalities Tabanlı)
- 12 soruluk MBTI (Myers-Briggs) tabanlı kişilik testi
- 16 farklı kişilik tipi (ISTJ, ENFP, INFJ, vb.)
- Her kişilik tipi için detaylı açıklama ve analiz
- Test sonuçlarının veritabanına kaydedilmesi

### 🎨 Hobi Testi
- 6 ana kategori ve 30'dan fazla hobi seçeneği
- En az 3, en fazla 8 hobi seçme zorunluluğu
- Kategori bazlı hobi filtreleme
- Seçilen hobilerin görsel olarak listelenmesi

### 🤝 Topluluk Yönetimi
- Kişilik ve hobi bazlı **akıllı topluluk önerileri**
- Topluluk oluşturma (admin/moderator yetkileri)
- Topluluk içi üye listesi ve online/offline durum takibi
- Topluluk istatistikleri (üye sayısı, uyum skoru, aktiflik)

### 💬 Gerçek Zamanlı Sohbet
- Socket.IO ile anlık mesajlaşma
- Online kullanıcı takibi
- "Yazıyor..." göstergesi
- Mesaj geçmişi ve bildirimler
- Dosya paylaşımı desteği

### 🤖 GPT Asistan
- Topluluk içi sohbet konusu önerileri
- Buz kırıcı soru üretimi
- Etkinlik ve aktivite önerileri
- Özelleştirilmiş sohbet asistanı

### 📊 Admin Paneli
- Kullanıcı yönetimi (ekleme, düzenleme, silme)
- Topluluk yönetimi
- Test sonuçları analizi
- Detaylı istatistikler ve grafikler
- Veritabanı yedekleme ve export

### 🔐 Güvenlik
- Şifre hash'leme (bcrypt)
- JWT token kimlik doğrulama
- CORS koruması
- Rate limiting
- SQL injection koruması

---

## 🏗️ Mimari Yapı

FriendZone, **modern ve ölçeklenebilir** bir mimari üzerine inşa edilmiştir:

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Kullanıcı Tarayıcısı                        │
│                         (HTML/CSS/JavaScript)                       │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │      Socket.IO          │
                    │   (Gerçek Zamanlı)      │
                    └────────────┬────────────┘
                                 │
┌────────────────────────────────▼────────────────────────────────────┐
│                         Flask Backend (Python)                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────┐ │
│  │   Routes     │  │   Services   │  │     ML       │  │  Utils   │ │
│  │  (API)       │  │  (Business   │  │   (Scikit-   │  │(Helpers, │ │
│  │              │  │    Logic)    │  │    learn)    │  │  Logger) │ │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────┘ │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │        PostgreSQL       │
                    │       (Veritabanı)      │
                    └─────────────────────────┘
```

### 🔄 Veri Akışı

1. Kullanıcı kayıt olur → Veritabanına kaydedilir
2. Kişilik testi çözer → MBTI tipi hesaplanır
3. Hobi testi çözer → İlgi alanları belirlenir
4. ML algoritması benzer kullanıcıları bulur
5. Kullanıcı uygun topluluğa atanır
6. Gerçek zamanlı sohbet başlar
7. GPT asistan öneriler sunar

---

## 📁 Klasör Yapısı

```
FriendZone/
│
├── 📄 .env                         # Çevre değişkenleri
├── 📄 .gitignore                    # Git ignore dosyası
├── 📄 README.md                      # Proje dokümantasyonu
├── 📄 requirements.txt                # Python bağımlılıkları
├── 📄 start.sh                        # Başlatma script'i
│
├── 📁 backend/                         # Backend uygulaması
│   ├── 📄 __init__.py
│   ├── 📄 app.py                        # Flask uygulama fabrikası
│   ├── 📄 config.py                      # Yapılandırma
│   ├── 📄 socket_events.py               # Socket.IO olayları
│   │
│   ├── 📁 database/                      # Veritabanı işlemleri
│   │   ├── 📄 __init__.py
│   │   ├── 📄 db_connection.py            # Veritabanı bağlantısı
│   │   └── 📄 seed_data.py                 # Test verileri
│   │
│   ├── 📁 ml/                             # Makine öğrenmesi katmanı
│   │   ├── 📄 __init__.py
│   │   ├── 📄 preprocessing.py             # Veri ön işleme
│   │   ├── 📄 similarity_engine.py         # Benzerlik hesaplama
│   │   ├── 📄 community_assigner.py        # Topluluk atama
│   │   └── 📄 clustering_model.py          # Kümeleme modeli
│   │
│   ├── 📁 models/                         # Veritabanı modelleri
│   │   ├── 📄 __init__.py
│   │   ├── 📄 user_model.py                 # Kullanıcı modeli
│   │   ├── 📄 community_model.py            # Topluluk modeli
│   │   ├── 📄 chat_model.py                 # Sohbet mesaj modeli
│   │   ├── 📄 chat_room_model.py            # Sohbet odası modeli
│   │   ├── 📄 similarity_model.py           # Benzerlik modeli
│   │   └── 📄 test_model.py                 # Test sonuç modeli
│   │
│   ├── 📁 routes/                          # API route'ları
│   │   ├── 📄 __init__.py
│   │   ├── 📄 auth_routes.py                # Kimlik doğrulama
│   │   ├── 📄 test_routes.py                # Test işlemleri
│   │   ├── 📄 community_routes.py           # Topluluk işlemleri
│   │   ├── 📄 chat_routes.py                # Sohbet işlemleri
│   │   ├── 📄 assistant_routes.py           # GPT asistan
│   │   └── 📄 admin_routes.py               # Admin paneli
│   │
│   ├── 📁 services/                         # Servis katmanı
│   │   ├── 📄 __init__.py
│   │   ├── 📄 gpt_service.py                 # GPT entegrasyonu
│   │   ├── 📄 community_service.py           # Topluluk servisi
│   │   └── 📄 recommendation_service.py      # Öneri servisi
│   │
│   ├── 📁 static/                            # Statik dosyalar
│   │   ├── 📁 admin/
│   │   │   ├── 📁 css/
│   │   │   └── 📁 js/
│   │   └── 📁 uploads/                        # Yüklenen dosyalar
│   │
│   ├── 📁 templates/                         # HTML şablonları
│   │   └── 📁 admin/
│   │       ├── 📄 base.html
│   │       ├── 📄 login.html
│   │       ├── 📄 index.html
│   │       ├── 📄 users.html
│   │       ├── 📄 communities.html
│   │       ├── 📄 tests.html
│   │       └── 📄 analytics.html
│   │
│   └── 📁 utils/                             # Yardımcı araçlar
│       ├── 📄 __init__.py
│       ├── 📄 helpers.py                       # Yardımcı fonksiyonlar
│       ├── 📄 logger.py                         # Loglama
│       └── 📄 validators.py                     # Validasyon
│
├── 📁 frontend/                           # Frontend dosyaları
│   ├── 📄 index.html
│   ├── 📄 login.html
│   ├── 📄 signup.html
│   ├── 📄 personality_test.html
│   ├── 📄 hobbies.html
│   ├── 📄 communities.html
│   ├── 📄 community.html
│   ├── 📄 profile.html
│   ├── 📄 chat.html
│   │
│   ├── 📁 css/                             # CSS dosyaları
│   │   ├── 📄 style.css                      # Ana stil
│   │   ├── 📄 auth.css                        # Giriş/kayıt stilleri
│   │   ├── 📄 test.css                        # Test stilleri
│   │   ├── 📄 hobbies.css                     # Hobi stilleri
│   │   ├── 📄 community.css                   # Topluluk stilleri
│   │   ├── 📄 profile.css                     # Profil stilleri
│   │   └── 📄 chat.css                        # Sohbet stilleri
│   │
│   ├── 📁 js/                               # JavaScript dosyaları
│   │   ├── 📄 main.js                          # Ana uygulama
│   │   ├── 📄 auth.js                          # Kimlik doğrulama
│   │   ├── 📄 sidebar.js                       # Sidebar yönetimi
│   │   ├── 📄 testHandler.js                   # Test işlemleri
│   │   ├── 📄 hobbiesHandler.js                 # Hobi işlemleri
│   │   ├── 📄 communityHandler.js               # Topluluk işlemleri
│   │   ├── 📄 communityManager.js               # Topluluk yönetimi
│   │   ├── 📄 profileHandler.js                 # Profil işlemleri
│   │   ├── 📄 chatHandler.js                    # Sohbet işlemleri
│   │   └── 📄 gptAssistant.js                   # GPT asistan
│   │
│   └── 📁 assets/                            # Görsel ve medya
│       ├── 📁 images/
│       ├── 📁 icons/
│       └── 📁 sounds/
│
├── 📁 data/                                 # Veri dosyaları
│   ├── 📁 raw/                                # Ham veriler
│   │   ├── 📄 personality_questions.json
│   │   └── 📄 hobbies_categories.json
│   │
│   └── 📁 processed/                          # İşlenmiş veriler
│       └── 📄 user_vectors.npy
│
└── 📁 docs/                                  # Dokümantasyon
    ├── 📄 API.md
    └── 📄 DEPLOYMENT.md
```

---

## ⚙️ Teknolojiler

### Backend
| Teknoloji | Versiyon | Açıklama |
|-----------|----------|----------|
| Python | 3.9+ | Ana programlama dili |
| Flask | 2.2.5 | Web framework |
| Flask-SQLAlchemy | 3.0.5 | ORM ve veritabanı yönetimi |
| Flask-Migrate | 4.0.5 | Veritabanı migration |
| Flask-CORS | 4.0.0 | Cross-Origin Resource Sharing |
| Flask-JWT-Extended | 4.5.2 | JWT kimlik doğrulama |
| Flask-SocketIO | 5.3.4 | Gerçek zamanlı iletişim |
| PostgreSQL | 15+ | Ana veritabanı |
| SQLite | - | Geliştirme veritabanı |
| Redis | - | Cache ve session yönetimi |

### AI/ML
| Teknoloji | Versiyon | Açıklama |
|-----------|----------|----------|
| scikit-learn | 1.5.0 | Makine öğrenmesi algoritmaları |
| numpy | 1.24.3 | Sayısal hesaplamalar |
| pandas | 2.0.3 | Veri analizi |
| joblib | 1.3.2 | Model serialization |
| OpenAI | 0.28.0 | GPT entegrasyonu |

### Frontend
| Teknoloji | Açıklama |
|-----------|----------|
| HTML5 | Sayfa yapısı |
| CSS3 | Stil ve animasyonlar |
| JavaScript (ES6) | Dinamik içerik |
| Socket.IO Client | Gerçek zamanlı iletişim |
| Chart.js | Grafik ve istatistikler |
| Font Awesome | İkonlar |
| Google Fonts | Tipografi |

---

## 🚀 Kurulum

### Ön Gereksinimler

- Python 3.9 veya üzeri
- PostgreSQL 15 veya üzeri
- Node.js (opsiyonel, frontend geliştirme için)
- Git

### Backend Kurulumu

```bash
# 1. Projeyi klonla
git clone https://github.com/BEUN-Graduation-Projects/FriendZone.git
cd FriendZone

# 2. Sanal ortam oluştur
python3 -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate  # Windows

# 3. Bağımlılıkları yükle
pip install --upgrade pip
pip install -r requirements.txt

# 4. Environment dosyasını oluştur
cat > .env << 'EOF'
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://friendzone_user:friendzone_pass@localhost:5432/friendzone_db
JWT_SECRET_KEY=jwt-secret-key
OPENAI_API_KEY=your-openai-api-key
ADMIN_USERNAME=admin
ADMIN_PASSWORD=FriendZone2024
CORS_ORIGINS=http://localhost:5001,http://127.0.0.1:5001
PORT=5001
HOST=0.0.0.0
EOF

# 5. Flask uygulamasını ayarla
export FLASK_APP=backend/app.py
export FLASK_ENV=development
export FLASK_DEBUG=1
```

### PostgreSQL Kurulumu

```bash
# 1. PostgreSQL'i yükle (Mac)
brew install postgresql@15
brew services start postgresql@15

# 2. PostgreSQL'e bağlan
psql postgres

# 3. Kullanıcı ve veritabanı oluştur (SQL prompt'unda)
CREATE USER friendzone_user WITH PASSWORD 'friendzone_pass';
CREATE DATABASE friendzone_db OWNER friendzone_user;
GRANT ALL PRIVILEGES ON DATABASE friendzone_db TO friendzone_user;
\q

# 4. Bağlantıyı test et
psql -U friendzone_user -d friendzone_db -h localhost -c "SELECT 1;"

# 5. Migration'ları çalıştır
flask db init
flask db migrate -m "Initial migration"
flask db upgrade

# 6. Test verilerini ekle (opsiyonel)
curl -X POST http://localhost:5001/api/seed
```

### Frontend Kurulumu

Frontend dosyaları zaten proje içinde olduğu için ek bir kurulum gerektirmez. Sadece statik dosyaların doğru yerde olduğundan emin olun:

```bash
# Statik dosyaları Flask'ın servis edebileceği yere kopyala
mkdir -p static/css static/js
cp frontend/css/*.css static/css/
cp frontend/js/*.js static/js/
cp -r frontend/assets static/ 2>/dev/null || echo "Assets klasörü yok"
```

### Uygulamayı Çalıştırma

```bash
# 1. PostgreSQL servisini başlat
brew services start postgresql@15

# 2. Backend'i başlat
cd ~/PycharmProjects/FriendZone
source .venv/bin/activate
export FLASK_APP=backend/app.py
export FLASK_ENV=development
export FLASK_DEBUG=1
flask run --host=0.0.0.0 --port=5001 --debug

# 3. Tarayıcıda aç
open http://localhost:5001
```

---

## 🎯 Kullanım Akışı

### 1. Kayıt ve Giriş
```
signup.html → login.html → personality_test.html → hobbies.html → communities.html
```

| Adım | Sayfa | Açıklama |
|------|-------|----------|
| 1 | `signup.html` | Üniversite emaili ile kayıt ol |
| 2 | `login.html` | Kayıtlı hesapla giriş yap |
| 3 | `personality_test.html` | 12 soruluk kişilik testini çöz |
| 4 | `hobbies.html` | İlgi alanlarını seç (en az 3 hobi) |
| 5 | `communities.html` | Önerilen toplulukları keşfet |

### 2. Topluluk Süreci

1. **Topluluk Önerileri**: AI, kişilik tipin ve hobilerine göre sana en uygun toplulukları önerir
2. **Topluluğa Katılma**: İlgini çeken topluluğa katıl
3. **Sohbet**: Topluluk içinde diğer üyelerle gerçek zamanlı sohbet et
4. **Aktiviteler**: Topluluk içindeki etkinliklere katıl
5. **GPT Asistan**: Sohbet konuları, etkinlik önerileri ve buz kırıcılar için AI asistanı kullan

### 3. Profil Yönetimi

- Profil bilgilerini düzenle (`profile.html`)
- Test sonuçlarını görüntüle
- Üye olduğun toplulukları listele
- Benzer kullanıcıları keşfet
- Rozetleri ve başarıları görüntüle

---

## 🧠 AI ve Makine Öğrenmesi

FriendZone'un en güçlü yanı, **akıllı eşleştirme algoritmalarıdır**.

### Kişilik Analizi

12 soruluk test, **MBTI (Myers-Briggs Type Indicator)** temellidir. Her soru 4 ana boyuttan birini ölçer:

| Boyut | Kısaltma | Açıklama |
|-------|----------|----------|
| Dışadönüklük/İçedönüklük | E/I | Enerji kaynağı |
| Duyumsama/Sezgi | S/N | Bilgi işleme |
| Düşünme/Hissetme | T/F | Karar verme |
| Yargılama/Algılama | J/P | Yaşam tarzı |

16 farklı kişilik tipi:

| Tip | Açıklama |
|-----|----------|
| **ISTJ** | Mantıklı, düzenli ve güvenilir |
| **ISFJ** | Koruyucu, sıcak kanlı ve fedakar |
| **INFJ** | Yaratıcı, idealist ve hassas |
| **INTJ** | Stratejik, mantıklı ve bağımsız |
| **ISTP** | Pratik, esnek ve gözlemci |
| **ISFP** | Sanatçı ruhlu, uyumlu |
| **INFP** | İdealist, yaratıcı |
| **INTP** | Analitik, yenilikçi |
| **ESTP** | Enerjik, mantıklı |
| **ESFP** | Canlı, eğlenceli |
| **ENFP** | Yaratıcı, sosyal |
| **ENTP** | Tartışmacı, meraklı |
| **ESTJ** | Lider, düzenli |
| **ESFJ** | Popüler, yardımsever |
| **ENFJ** | Karizmatik, ilham verici |
| **ENTJ** | Kararlı, lider ruhlu |

### Hobi Eşleştirme

6 ana kategori ve 30'dan fazla hobi:

```
Teknoloji: Programlama, Yapay Zeka, Robotik, Web Tasarım, Mobil Uygulama
Spor: Futbol, Basketbol, Yüzme, Koşu, Yoga, Fitness, Tenis
Sanat: Resim, Müzik, Fotoğrafçılık, Dans, Tiyatro, Yazarlık
Doğa: Kamp, Doğa Yürüyüşü, Dağcılık, Bisiklet
Eğitim: Kitap Okuma, Dil Öğrenme, Online Kurs, Araştırma
Sosyal: Gönüllülük, Organizasyon, Network, Mentorluk
```

### Topluluk Öneri Sistemi

**Cosine Similarity** algoritması kullanılarak hesaplanır:

```python
# Kullanıcı vektörü = Kişilik tipi vektörü + Hobi vektörü + Akademik vektör
user_vector = personality_vector + hobbies_vector + academic_vector

# Benzerlik hesaplama
similarity = cosine_similarity(user_vector, other_user_vector)

# Kümeleme (K-means)
clusters = KMeans(n_clusters=5).fit_predict(all_user_vectors)
```

### GPT Asistan Entegrasyonu

OpenAI GPT-3.5/4 ile:

- **Sohbet Konusu Önerileri**: Topluluk temasına uygun 3-5 sohbet konusu
- **Buz Kırıcı Sorular**: Üyelerin birbirini tanıması için eğlenceli sorular
- **Etkinlik Önerileri**: Online/offline etkinlik fikirleri
- **Özelleştirilmiş Asistan**: Topluluk hakkında sorulara cevap

---

## 📊 Veritabanı Şeması

### Ana Tablolar

#### `users`
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    university VARCHAR(100),
    department VARCHAR(100),
    year INTEGER,
    personality_type VARCHAR(50),
    personality_scores JSON,
    hobbies JSON,
    is_test_completed BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### `communities`
```sql
CREATE TABLE communities (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    category VARCHAR(50),
    tags JSON,
    compatibility_score FLOAT DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    max_members INTEGER DEFAULT 10,
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### `community_members`
```sql
CREATE TABLE community_members (
    id SERIAL PRIMARY KEY,
    community_id INTEGER REFERENCES communities(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(20) DEFAULT 'member',
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    message_count INTEGER DEFAULT 0,
    UNIQUE(community_id, user_id)
);
```

#### `chat_messages`
```sql
CREATE TABLE chat_messages (
    id SERIAL PRIMARY KEY,
    community_id INTEGER REFERENCES communities(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id),
    content TEXT NOT NULL,
    message_type VARCHAR(20) DEFAULT 'text',
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    edited BOOLEAN DEFAULT FALSE,
    edited_at TIMESTAMP,
    reply_to INTEGER REFERENCES chat_messages(id) ON DELETE SET NULL,
    reactions JSON DEFAULT '{}',
    metadata_json JSON
);
```

#### `chat_rooms`
```sql
CREATE TABLE chat_rooms (
    id SERIAL PRIMARY KEY,
    community_id INTEGER UNIQUE REFERENCES communities(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    description VARCHAR(200),
    is_active BOOLEAN DEFAULT TRUE,
    is_private BOOLEAN DEFAULT FALSE,
    max_members INTEGER DEFAULT 50,
    current_members INTEGER DEFAULT 0,
    settings JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### `user_similarities`
```sql
CREATE TABLE user_similarities (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    similar_user_id INTEGER REFERENCES users(id),
    similarity_score FLOAT NOT NULL,
    similarity_type VARCHAR(20) DEFAULT 'overall',
    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);
```

### İlişkiler

```
users 1───* community_members *───1 communities
users 1───* chat_messages *───1 communities
users 1───* user_similarities *───1 users
communities 1───1 chat_rooms
chat_rooms 1───* chat_user_status *───1 users
users 1───1 personality_test_results
users 1───1 hobby_results
```

---

## 👑 Admin Paneli

Admin paneli, sistem yöneticileri için **tam kontrol** sağlar.

### Erişim
```
URL: http://localhost:5001/admin
Kullanıcı: admin
Şifre: FriendZone2024
```

### Dashboard
- **KPI Kartları**: Toplam kullanıcı, aktif kullanıcı, online kullanıcı, topluluk sayısı
- **Grafikler**: Son 7 günlük kayıtlar, kişilik tipi dağılımı, kategori dağılımı
- **Hızlı İstatistikler**: Toplam mesaj, günlük mesaj, ortalama üye/topluluk

### Kullanıcı Yönetimi
- Kullanıcı listesi (ID, isim, email, üniversite, bölüm, kişilik tipi, hobiler)
- Arama, filtreleme ve sıralama
- Kullanıcı detayları (üye olduğu topluluklar, mesaj sayısı, aktiviteler)
- Kullanıcı düzenleme ve silme
- CSV export

### Topluluk Yönetimi
- Topluluk listesi (ID, isim, kategori, üye sayısı, mesaj sayısı, uyum skoru)
- Topluluk oluşturma ve düzenleme
- Üye listesi ve yönetimi
- Topluluk istatistikleri

### Test Sonuçları
- Kişilik tipi dağılımı (grafik)
- En popüler hobiler (liste)
- Kategori bazlı hobi analizi
- Test tamamlama oranları

### Analitikler
- Günlük aktif kullanıcı trendi
- Mesaj trafiği analizi
- Saatlik aktivite dağılımı
- En aktif topluluklar ve kullanıcılar
- Retention (tutunma) analizi

---

## 🔐 Güvenlik

### Kimlik Doğrulama
- JWT (JSON Web Token) tabanlı authentication
- Token süresi: 1 saat (access token), 30 gün (refresh token)
- Şifreler bcrypt ile hash'lenir

### Veritabanı Güvenliği
- SQL injection koruması (SQLAlchemy ORM)
- Hassas veriler şifrelenir
- Veritabanı yedekleme sistemi

### API Güvenliği
- CORS yapılandırması
- Rate limiting (dakikada 100 istek)
- Input validasyonu
- XSS koruması

### Session Yönetimi
- HTTP-only cookies
- SameSite=Lax
- Secure flag (production'da)



## 🤝 Katkıda Bulunma

1. Bu repository'yi fork edin
2. Yeni bir branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Değişikliklerinizi commit edin (`git commit -m 'Add some amazing feature'`)
4. Branch'inizi push edin (`git push origin feature/amazing-feature`)
5. Pull Request açın

### Kod Standartları
- Python: PEP 8
- JavaScript: ESLint
- HTML/CSS: Prettier

---

## 📄 Lisans

Bu proje **MIT lisansı** altında lisanslanmıştır. Detaylar için [LICENSE](LICENSE) dosyasına bakın.



---

<div align="center">

**⭐ Bu projeyi beğendiyseniz yıldız vermeyi unutmayın! ⭐**

[⬆ Yukarı Çık](#-friendzone)

</div>
