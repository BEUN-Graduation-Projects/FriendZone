// frontend/js/hobbiesHandler.js

class HobbiesHandler {
    constructor() {
        this.selectedHobbies = new Set();
        this.categories = [];
        this.hobbies = [];
        this.currentCategory = 'all';
        this.maxSelection = 8;
        this.minSelection = 3;
        this.init();
    }

    async init() {
        await this.loadCategories();
        await this.loadHobbies();
        this.setupEventListeners();
        this.updateSelectionCount();
        this.loadUserData();
        this.loadPersonalityData();
    }

    async loadCategories() {
        try {
            const response = await fetch('/api/test/hobbies-categories');
            const data = await response.json();

            if (data.success) {
                this.categories = data.categories;
                this.renderCategories();
            } else {
                throw new Error('Kategoriler yüklenemedi');
            }
        } catch (error) {
            console.error('Kategori yükleme hatası:', error);
            this.showFallbackCategories();
        }
    }

    async loadHobbies() {
        try {
            setTimeout(() => {
                document.getElementById('loadingState').style.display = 'none';
            }, 1000);

            this.hobbies = this.generateHobbiesFromCategories();
            this.renderHobbies();
        } catch (error) {
            console.error('Hobi yükleme hatası:', error);
            document.getElementById('loadingState').style.display = 'none';
            document.getElementById('emptyState').style.display = 'block';
        }
    }

    generateHobbiesFromCategories() {
        const hobbies = [];
        this.categories.forEach(category => {
            category.activities.forEach(activity => {
                hobbies.push({
                    id: `${category.id}_${activity.toLowerCase().replace(/\s+/g, '_')}`,
                    name: activity,
                    description: this.getHobbyDescription(activity, category.name),
                    category: category.id,
                    categoryName: category.name,
                    icon: this.getHobbyIcon(activity)
                });
            });
        });
        return hobbies;
    }

    getHobbyDescription(activity, category) {
        const descriptions = {
            'Programlama': 'Kod yazmayı ve yazılım geliştirmeyi seviyorum',
            'Robotik': 'Robot tasarımı ve programlama ile ilgileniyorum',
            'AI/Makine Öğrenimi': 'Yapay zeka ve veri bilimi projeleri yapıyorum',
            'Futbol': 'Takım sporlarını ve futbol oynamayı seviyorum',
            'Basketbol': 'Basketbol oynamak ve izlemek hoşuma gidiyor',
            'Yoga': 'Zihin ve beden sağlığı için yoga yapıyorum',
            'Resim': 'Sanat ve resim yapmak benim için terapi gibi',
            'Müzik': 'Enstrüman çalmak ve müzik dinlemek hayatımın parçası',
            'Fotoğrafçılık': 'Doğa ve portre fotoğrafçılığı ile ilgileniyorum',
            'Doğa Yürüyüşü': 'Doğada yürüyüş yapmak ve kamp atmak',
            'Kitap Okuma': 'Farklı türlerde kitaplar okumayı seviyorum',
            'Dil Öğrenme': 'Yeni diller öğrenmek ve kültürleri keşfetmek'
        };

        return descriptions[activity] || `${activity} ile ilgileniyorum`;
    }

    getHobbyIcon(activity) {
        const iconMap = {
            'Programlama': 'fa-code',
            'Robotik': 'fa-robot',
            'AI/Makine Öğrenimi': 'fa-brain',
            'Futbol': 'fa-futbol',
            'Basketbol': 'fa-basketball-ball',
            'Yoga': 'fa-spa',
            'Resim': 'fa-palette',
            'Müzik': 'fa-music',
            'Fotoğrafçılık': 'fa-camera',
            'Doğa Yürüyüşü': 'fa-hiking',
            'Kitap Okuma': 'fa-book',
            'Dil Öğrenme': 'fa-language'
        };

        return iconMap[activity] || 'fa-heart';
    }

    showFallbackCategories() {
        this.categories = [
            {
                id: "technology",
                name: "Teknoloji ve Bilim",
                activities: ["Programlama", "Robotik", "AI/Makine Öğrenimi", "Elektronik", "Veri Analizi"]
            },
            {
                id: "sports",
                name: "Spor ve Fitness",
                activities: ["Futbol", "Basketbol", "Yüzme", "Koşu", "Yoga", "Fitness"]
            },
            {
                id: "arts",
                name: "Sanat ve Tasarım",
                activities: ["Resim", "Müzik", "Fotoğrafçılık", "Dans", "Tiyatro", "Yazarlık"]
            },
            {
                id: "outdoor",
                name: "Açık Hava ve Doğa",
                activities: ["Doğa Yürüyüşü", "Kamp", "Dağcılık", "Bisiklet", "Balıkçılık"]
            },
            {
                id: "education",
                name: "Eğitim ve Gelişim",
                activities: ["Kitap Okuma", "Dil Öğrenme", "Online Kurslar", "Araştırma"]
            },
            {
                id: "social",
                name: "Sosyal ve Topluluk",
                activities: ["Gönüllülük", "Kulüp Aktiviteleri", "Organizasyon", "Network"]
            }
        ];
        this.renderCategories();
    }

    renderCategories() {
        const container = document.querySelector('.categories-scroll');
        if (!container) return;

        const categoriesHTML = `
            <button class="category-btn active" data-category="all">
                <i class="fas fa-th-large"></i>
                Tümü
            </button>
            ${this.categories.map(category => `
                <button class="category-btn" data-category="${category.id}">
                    <i class="fas fa-${this.getCategoryIcon(category.id)}"></i>
                    ${category.name}
                </button>
            `).join('')}
        `;
        container.innerHTML = categoriesHTML;
    }

    getCategoryIcon(categoryId) {
        const icons = {
            'technology': 'laptop-code',
            'sports': 'running',
            'arts': 'palette',
            'outdoor': 'mountain',
            'education': 'graduation-cap',
            'social': 'users'
        };
        return icons[categoryId] || 'circle';
    }

    renderHobbies() {
        const container = document.getElementById('hobbiesGrid');
        if (!container) return;

        const filteredHobbies = this.currentCategory === 'all'
            ? this.hobbies
            : this.hobbies.filter(hobby => hobby.category === this.currentCategory);

        if (filteredHobbies.length === 0) {
            document.getElementById('emptyState').style.display = 'block';
            container.style.display = 'none';
            return;
        }

        document.getElementById('emptyState').style.display = 'none';
        container.style.display = 'grid';

        const hobbiesHTML = filteredHobbies.map(hobby => `
            <div class="hobby-card ${this.selectedHobbies.has(hobby.id) ? 'selected' : ''} 
                                  ${this.selectedHobbies.size >= this.maxSelection && !this.selectedHobbies.has(hobby.id) ? 'disabled' : ''}" 
                 data-hobby-id="${hobby.id}">
                <div class="hobby-content">
                    <div class="hobby-icon">
                        <i class="fas ${hobby.icon}"></i>
                    </div>
                    <div class="hobby-info">
                        <div class="hobby-name">${hobby.name}</div>
                        <div class="hobby-category">${hobby.categoryName}</div>
                    </div>
                </div>
            </div>
        `).join('');

        container.innerHTML = hobbiesHTML;
    }

    setupEventListeners() {
        document.addEventListener('click', (e) => {
            if (e.target.closest('.category-btn')) {
                const btn = e.target.closest('.category-btn');
                const category = btn.dataset.category;
                this.filterByCategory(category, btn);
            }
        });

        const hobbiesGrid = document.getElementById('hobbiesGrid');
        if (hobbiesGrid) {
            hobbiesGrid.addEventListener('click', (e) => {
                const hobbyCard = e.target.closest('.hobby-card');
                if (hobbyCard && !hobbyCard.classList.contains('disabled')) {
                    this.toggleHobbySelection(hobbyCard.dataset.hobbyId);
                }
            });
        }

        const clearBtn = document.getElementById('clearSelectionBtn');
        if (clearBtn) {
            clearBtn.addEventListener('click', () => this.clearSelection());
        }

        const submitBtn = document.getElementById('submitHobbiesBtn');
        if (submitBtn) {
            submitBtn.addEventListener('click', () => this.submitHobbies());
        }
    }

    filterByCategory(category, button) {
        document.querySelectorAll('.category-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        button.classList.add('active');

        this.currentCategory = category;
        this.renderHobbies();
    }

    toggleHobbySelection(hobbyId) {
        if (this.selectedHobbies.has(hobbyId)) {
            this.selectedHobbies.delete(hobbyId);
        } else {
            if (this.selectedHobbies.size < this.maxSelection) {
                this.selectedHobbies.add(hobbyId);
            }
        }

        this.renderHobbies();
        this.updateSelectionCount();
        this.updateSelectedHobbiesList();
        this.updateSubmitButton();
    }

    clearSelection() {
        this.selectedHobbies.clear();
        this.renderHobbies();
        this.updateSelectionCount();
        this.updateSelectedHobbiesList();
        this.updateSubmitButton();
    }

    updateSelectionCount() {
        const countElement = document.getElementById('selectedCount');
        if (countElement) {
            countElement.textContent = this.selectedHobbies.size;
        }
    }

    updateSelectedHobbiesList() {
        const container = document.getElementById('selectedHobbiesList');
        if (!container) return;

        const selectedHobbies = Array.from(this.selectedHobbies).map(id => {
            return this.hobbies.find(h => h.id === id);
        }).filter(h => h);

        if (selectedHobbies.length === 0) {
            container.innerHTML = '<div class="empty-selection">Henüz hobi seçilmedi</div>';
            return;
        }

        container.innerHTML = selectedHobbies.map(hobby => `
            <div class="selected-hobby-item">
                <i class="fas ${hobby.icon}"></i>
                <span>${hobby.name}</span>
            </div>
        `).join('');
    }

    updateSubmitButton() {
        const btn = document.getElementById('submitHobbiesBtn');
        if (!btn) return;

        const isValid = this.selectedHobbies.size >= this.minSelection &&
                       this.selectedHobbies.size <= this.maxSelection;

        btn.disabled = !isValid;
    }

    async submitHobbies() {
        if (this.selectedHobbies.size < this.minSelection) {
            alert(`En az ${this.minSelection} hobi seçmelisiniz`);
            return;
        }

        const submitBtn = document.getElementById('submitHobbiesBtn');
        this.setLoadingState(submitBtn, true);

        try {
            const user = JSON.parse(localStorage.getItem('friendzone_user'));
            const token = localStorage.getItem('friendzone_token');

            const selectedHobbyNames = Array.from(this.selectedHobbies).map(id => {
                const hobby = this.hobbies.find(h => h.id === id);
                return hobby ? hobby.name : id;
            });

            const response = await fetch('/api/test/hobbies', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    user_id: user.id,
                    hobbies: selectedHobbyNames
                })
            });

            const result = await response.json();

            if (response.ok && result.success) {
                user.hobbies = selectedHobbyNames;
                user.is_test_completed = true;
                localStorage.setItem('friendzone_user', JSON.stringify(user));

                this.showSuccess();
            } else {
                throw new Error(result.message || 'Hobiler kaydedilemedi');
            }
        } catch (error) {
            console.error('Hobi gönderme hatası:', error);
            alert('Hobiler kaydedilirken bir hata oluştu: ' + error.message);
        } finally {
            this.setLoadingState(submitBtn, false);
        }
    }

    showSuccess() {
        const mainContent = document.querySelector('.hobbies-content');
        if (!mainContent) return;

        mainContent.innerHTML = `
            <div class="success-state">
                <div class="success-icon">
                    <i class="fas fa-check-circle"></i>
                </div>
                <h2>Harika! Hobilerin Kaydedildi</h2>
                <p>Senin için özel topluluklar oluşturuluyor...</p>
                <div class="success-actions">
                    <a href="communities.html" class="btn btn-primary btn-large">
                        <i class="fas fa-users"></i>
                        Topluluklarımı Gör
                    </a>
                </div>
            </div>
        `;

        setTimeout(() => {
            window.location.href = 'communities.html';
        }, 3000);
    }

    setLoadingState(button, isLoading) {
        if (isLoading) {
            button.classList.add('btn-loading');
            button.disabled = true;
            button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> İşleniyor...';
        } else {
            button.classList.remove('btn-loading');
            button.disabled = false;
            button.innerHTML = '<i class="fas fa-paper-plane"></i> Hobileri Kaydet ve Topluluklara Katıl';
        }
    }

    loadUserData() {
        const user = JSON.parse(localStorage.getItem('friendzone_user'));
        if (user) {
            const userNameEl = document.getElementById('userName');
            const userAvatarEl = document.getElementById('userAvatar');

            if (userNameEl) userNameEl.textContent = user.name || 'Kullanıcı';
            if (userAvatarEl) userAvatarEl.textContent = (user.name || 'K').charAt(0).toUpperCase();
        }
    }

    loadPersonalityData() {
        const user = JSON.parse(localStorage.getItem('friendzone_user'));
        if (user && user.personality_type) {
            const personalityBadge = document.getElementById('personalityBadge');
            const personalityPreview = document.getElementById('personalityPreview');

            if (personalityBadge) personalityBadge.textContent = user.personality_type;
            if (personalityPreview) personalityPreview.style.display = 'block';
        }
    }
}

// Initialize hobbies handler
document.addEventListener('DOMContentLoaded', () => {
    window.hobbiesHandler = new HobbiesHandler();
});