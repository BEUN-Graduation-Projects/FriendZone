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
            // Hide loading state after a short delay
            setTimeout(() => {
                document.getElementById('loadingState').style.display = 'none';
            }, 1000);

            // For now, we'll use the categories data to create hobbies
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
            'Dil Öğrenme': 'fa-language',
            'Gönüllülük': 'fa-hands-helping',
            'Network': 'fa-network-wired'
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
                        <div class="hobby-description">${hobby.description}</div>
                        <div class="hobby-category">${hobby.categoryName}</div>
                    </div>
                </div>
            </div>
        `).join('');

        container.innerHTML = hobbiesHTML;
    }

    setupEventListeners() {
        // Category filter
        document.addEventListener('click', (e) => {
            if (e.target.closest('.category-btn')) {
                const btn = e.target.closest('.category-btn');
                const category = btn.dataset.category;
                this.filterByCategory(category, btn);
            }
        });

        // Hobby selection
        document.getElementById('hobbiesGrid').addEventListener('click', (e) => {
            const hobbyCard = e.target.closest('.hobby-card');
            if (hobbyCard && !hobbyCard.classList.contains('disabled')) {
                this.toggleHobbySelection(hobbyCard.dataset.hobbyId);
            }
        });

        // Clear selection
        document.getElementById('clearSelectionBtn').addEventListener('click', () => {
            this.clearSelection();
        });

        // Submit hobbies
        document.getElementById('submitHobbiesBtn').addEventListener('click', () => {
            this.submitHobbies();
        });
    }

    filterByCategory(category, button) {
        // Update active button
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
        const count = this.selectedHobbies.size;
        document.getElementById('selectedCount').textContent = count;

        // Update selection info
        const selectionInfo = document.querySelector('.selection-info');
        if (count >= this.maxSelection) {
            if (!document.querySelector('.limit-warning')) {
                const warning = document.createElement('div');
                warning.className = 'limit-warning';
                warning.innerHTML = `<i class="fas fa-exclamation-triangle"></i> Maksimum ${this.maxSelection} hobi seçebilirsin`;
                selectionInfo.appendChild(warning);
            }
        } else {
            const warning = document.querySelector('.limit-warning');
            if (warning) warning.remove();
        }
    }

    updateSelectedHobbiesList() {
        const container = document.getElementById('selectedHobbiesList');
        const selectedHobbies = Array.from(this.selectedHobbies).map(id => {
            const hobby = this.hobbies.find(h => h.id === id);
            return hobby;
        });

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
        const isValid = this.selectedHobbies.size >= this.minSelection &&
                       this.selectedHobbies.size <= this.maxSelection;

        btn.disabled = !isValid;

        if (this.selectedHobbies.size < this.minSelection) {
            btn.title = `En az ${this.minSelection} hobi seçmelisin`;
        } else {
            btn.title = '';
        }
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
            const response = await fetch('/api/test/submit-hobbies', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('friendzone_token')}`
                },
                body: JSON.stringify({
                    user_id: user.id,
                    hobbies: Array.from(this.selectedHobbies)
                })
            });

            const result = await response.json();

            if (response.ok) {
                this.showSuccess(result);
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

    showSuccess(result) {
        // Update UI to show success
        const mainContent = document.querySelector('.hobbies-content');
        mainContent.innerHTML = `
            <div class="success-state">
                <div class="success-icon">
                    <i class="fas fa-check-circle"></i>
                </div>
                <h2>Harika! Hobilerin Kaydedildi</h2>
                <p>Senin için özel topluluklar oluşturuluyor...</p>
                <div class="community-assignment">
                    <div class="assignment-info">
                        <i class="fas fa-robot"></i>
                        <span>AI topluluk eşleştirmesi yapılıyor</span>
                    </div>
                    <div class="loading-spinner"></div>
                </div>
                <div class="success-actions">
                    <a href="communities.html" class="btn btn-primary btn-large">
                        <i class="fas fa-users"></i>
                        Topluluklarımı Gör
                    </a>
                </div>
            </div>
        `;

        // Add success styles
        const style = document.createElement('style');
        style.textContent = `
            .success-state {
                text-align: center;
                padding: 60px 20px;
            }
            .success-icon {
                width: 100px;
                height: 100px;
                background: linear-gradient(135deg, var(--accent-success), var(--accent-primary));
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 40px;
                color: white;
                margin: 0 auto 24px;
            }
            .success-state h2 {
                font-size: 2rem;
                font-weight: 700;
                color: var(--text-primary);
                margin-bottom: 16px;
            }
            .success-state p {
                font-size: 1.125rem;
                color: var(--text-secondary);
                margin-bottom: 32px;
            }
            .community-assignment {
                background: var(--bg-secondary);
                padding: 20px;
                border-radius: var(--border-radius);
                margin-bottom: 32px;
            }
            .assignment-info {
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 12px;
                margin-bottom: 16px;
                color: var(--text-secondary);
            }
            .assignment-info i {
                color: var(--accent-primary);
            }
        `;
        document.head.appendChild(style);

        // Redirect after delay
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
            document.getElementById('userName').textContent = user.name;
            document.getElementById('userAvatar').textContent = user.name.charAt(0).toUpperCase();
        }
    }

    loadPersonalityData() {
        const user = JSON.parse(localStorage.getItem('friendzone_user'));
        if (user && user.personality_type) {
            document.getElementById('personalityBadge').textContent = user.personality_type;
            document.getElementById('personalityPreview').style.display = 'block';
        }
    }
}

// Initialize hobbies handler
document.addEventListener('DOMContentLoaded', () => {
    window.hobbiesHandler = new HobbiesHandler();
});