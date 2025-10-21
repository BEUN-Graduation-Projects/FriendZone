FriendZone - Üniversite Öğrencileri için Akıllı Topluluk Platformu

https://img.shields.io/badge/FriendZone-Social%2520Platform-blue
https://img.shields.io/badge/version-1.0.0-green
https://img.shields.io/badge/license-MIT-lightgrey

🎯 Proje Hakkında

FriendZone, üniversite öğrencilerinin kişilik özellikleri ve ilgi alanlarına göre makine öğrenimi tabanlı bir şekilde sanal topluluklar oluşturmasını sağlayan yenilikçi bir sosyal platformdur.

🚀 Spotify Blend veya Netflix öneri motoru gibi çalışır, ancak odak noktası insan eşleşmesi ve topluluk oluşturmadır.
✨ Özellikler

🧠 Akıllı Eşleştirme Sistemi

Kişilik Testi: Kapsamlı kişilik analizi ile kullanıcı profili oluşturma
Hobi Testi: İlgi alanlarına göre özelleştirilmiş öneriler
ML Tabanlı Eşleşme: Cosine similarity ile benzer kullanıcıların bulunması
Dinamik Topluluklar: Otomatik topluluk oluşturma ve yönetimi
💬 Sosyal Özellikler

Grup Sohbeti: Topluluk üyeleri arasında gerçek zamanlı mesajlaşma
Etkinlik Yönetimi: Topluluk etkinlikleri oluşturma ve katılım
Profil Paylaşımı: Kişisel profilleri paylaşma özelliği
Benzer Kullanıcılar: Ortak ilgi alanlarına sahip kişileri keşfetme
🤖 AI Asistan Entegrasyonu

GPT Destekli Öneriler: Topluluklar için sohbet konuları önerme
Buz Kırıcı Sorular: Grup etkileşimini artıran soru önerileri
Etkinlik Fikirleri: Topluluk etkinlikleri için yaratıcı fikirler
Akıllı Öneriler: Kullanıcı davranışlarına göre kişiselleştirilmiş içerik
🎨 Modern Kullanıcı Arayüzü

Responsive Tasarım: Tüm cihazlarda mükemmel görünüm
Karanlık/Açık Mod: Kullanıcı tercihine göre tema desteği
İnteraktif Bileşenler: Modern ve kullanıcı dostu arayüz
Gerçek Zamanlı Güncellemeler: Anlık bildirimler ve güncellemeler
🏗️ Teknoloji Stack'i

Frontend

HTML5 - Yapısal temel
CSS3 - Modern stiller ve animasyonlar
JavaScript (ES6+) - İnteraktif işlevsellik
Font Awesome - İkon kütüphanesi
Google Fonts - Typography
Backend

Python Flask - Web framework
SQLAlchemy - ORM ve veritabanı yönetimi
JWT - Kimlik doğrulama sistemi
RESTful API - Modern API mimarisi
Makine Öğrenimi

scikit-learn - Benzerlik algoritmaları
pandas/numpy - Veri işleme
Cosine Similarity - Kullanıcı eşleştirme
Clustering - Topluluk gruplandırma
GPT Entegrasyonu

OpenAI API - Yapay zeka destekli öneriler
Özelleştirilmiş Prompt'lar - Bağlama uygun yanıtlar
📁 Proje Yapısı

text
FriendZone/
├── backend/
│   ├── app.py                 # Flask uygulaması
│   ├── config.py              # Yapılandırma ayarları
│   ├── models/                # Veritabanı modelleri
│   ├── routes/                # API route'ları
│   ├── ml/                    # ML algoritmaları
│   ├── services/              # GPT ve diğer servisler
│   └── database/              # Veritabanı bağlantıları
├── frontend/
│   ├── *.html                 # Tüm HTML sayfaları
│   ├── css/                   # Stil dosyaları
│   ├── js/                    # JavaScript modülleri
│   └── assets/                Görseller ve fontlar
├── data/                      # Veri setleri
└── docs/                      # Dokümantasyon
🚀 Kurulum ve Çalıştırma

Ön Gereksinimler

Python 3.8+
Node.js (opsiyonel, geliştirme için)
Modern web tarayıcısı
1. Backend Kurulumu

bash
# Proje dizinine git
cd FriendZone/backend

# Gerekli paketleri yükle
pip install -r requirements.txt

# Ortam değişkenlerini ayarla
cp .env.example .env
# .env dosyasını düzenle ve API key'leri ekle

# Veritabanını başlat
python database/seed_data.py

# Flask uygulamasını çalıştır
python app.py
2. Frontend Kurulumu

bash
# Frontend dizinine git
cd FriendZone/frontend

# Yerel sunucu ile çalıştır (opsiyonel)
# Python kullanarak:
python -m http.server 8000

# Veya doğrudan HTML dosyalarını tarayıcıda açın
3. Ortam Değişkenleri

.env dosyasında aşağıdaki değişkenleri ayarlayın:

env
FLASK_ENV=development
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///friendzone.db
OPENAI_API_KEY=your-openai-api-key
PORT=5000
HOST=0.0.0.0
🎮 Kullanım Kılavuzu

1. Kayıt ve Giriş

Yeni kullanıcılar signup.html üzerinden kayıt olabilir
Mevcut kullanıcılar login.html ile giriş yapabilir
Demo mod: Giriş yapmadan profil sayfasını görüntüleyebilirsiniz
2. Kişilik ve Hobi Testleri

personality_test.html - Kapsamlı kişilik analizi
hobbies.html - İlgi alanları belirleme testi
Test sonuçları ML modeli ile işlenerek öneriler oluşturulur
3. Topluluk Keşfi

communities.html - Önerilen toplulukları görüntüleme
community.html - Topluluk detay sayfası
AI asistan ile etkileşim kurma
4. Profil Yönetimi

profile.html - Kişisel profil yönetimi
Ayarlar, gizlilik kontrolleri
Başarı rozetleri ve istatistikler
🔧 API Endpoints

Kimlik Doğrulama

POST /api/auth/register - Kullanıcı kaydı
POST /api/auth/login - Kullanıcı girişi
POST /api/auth/logout - Çıkış
Kullanıcı İşlemleri

GET /api/user/profile/:id - Profil bilgileri
POST /api/user/profile/update - Profil güncelleme
GET /api/user/similar/:id - Benzer kullanıcılar
Topluluk İşlemleri

GET /api/community/user/:id - Kullanıcı toplulukları
GET /api/community/recommendations/:id - Önerilen topluluklar
POST /api/community/join - Topluluğa katılma
POST /api/community/create - Yeni topluluk oluşturma
AI Asistan

POST /api/assistant/suggest - GPT önerileri
POST /api/assistant/chat - AI sohbeti
🤝 Katkıda Bulunma

FriendZone açık kaynaklı bir projedir ve katkılarınızı bekliyoruz!

Katkı Süreci

Fork edin ve repository'i klonlayın
Yeni bir branch oluşturun: git checkout -b feature/AmazingFeature
Değişikliklerinizi commit edin: git commit -m 'Add AmazingFeature'
Branch'inizi push edin: git push origin feature/AmazingFeature
Pull Request oluşturun
Geliştirme Kuralları

Kod standartlarına uyun
Testleri yazın ve çalıştırın
Dokümantasyonu güncelleyin
Anlamlı commit mesajları kullanın
📝 Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için LICENSE dosyasına bakın.
