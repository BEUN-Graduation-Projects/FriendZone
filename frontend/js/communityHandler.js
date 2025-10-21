class CommunityHandler {
    constructor() {
        this.userCommunities = [];
        this.recommendedCommunities = [];
        this.allCommunities = [];
        this.similarUsers = [];
        this.init();
    }

    async init() {
        await this.loadUserCommunities();
        await this.loadRecommendedCommunities();
        await this.loadAllCommunities();
        await this.loadSimilarUsers();
        this.setupEventListeners();
        this.loadUserData();
    }

    async loadUserCommunities() {
        try {
            const user = JSON.parse(localStorage.getItem('friendzone_user'));
            const response = await fetch(`/api/community/user/${user.id}`, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('friendzone_token')}`
                }
            });

            const data = await response.json();

            if (data.success) {
                this.userCommunities = data.communities;
                this.renderUserCommunities();
            }
        } catch (error) {
            console.error('Kullanıcı toplulukları yüklenemedi:', error);
        }
    }

    async loadRecommendedCommunities() {
        const loadingElement = document.getElementById('recommendationsLoading');

        try {
            const user = JSON.parse(localStorage.getItem('friendzone_user'));
            const response = await fetch(`/api/community/recommendations/${user.id}`, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('friendzone_token')}`
                }
            });

            const data = await response.json();

            if (data.success) {
                this.recommendedCommunities = data.recommendations;
                this.renderRecommendedCommunities();
            }

            loadingElement.style.display = 'none';
        } catch (error) {
            console.error('Önerilen topluluklar yüklenemedi:', error);
            loadingElement.style.display = 'none';
            this.showRecommendationsError();
        }
    }

    async loadAllCommunities() {
        const loadingElement = document.getElementById('communitiesLoading');
        const emptyElement = document.getElementById('communitiesEmpty');

        try {
            // This would normally come from an API
            // For now, we'll generate sample data
            this.allCommunities = this.generateSampleCommunities();
            this.renderAllCommunities();

            loadingElement.style.display = 'none';

            if (this.allCommunities.length === 0) {
                emptyElement.style.display = 'block';
            }
        } catch (error) {
            console.error('Topluluklar yüklenemedi:', error);
            loadingElement.style.display = 'none';
            emptyElement.style.display = 'block';
        }
    }

    async loadSimilarUsers() {
        const loadingElement = document.getElementById('similarUsersLoading');

        try {
            const user = JSON.parse(localStorage.getItem('friendzone_user'));
            const response = await fetch(`/api/community/similar-users/${user.id}`, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('friendzone_token')}`
                }
            });

            const data = await response.json();

            if (data.success) {
                this.similarUsers = data.similar_users;
                this.renderSimilarUsers();
            }

            loadingElement.style.display = 'none';
        } catch (error) {
            console.error('Benzer kullanıcılar yüklenemedi:', error);
            loadingElement.style.display = 'none';
        }
    }

    generateSampleCommunities() {
        return [
            {
                id: 1,
                name: "Teknoloji Meraklıları",
                description: "Yazılım, AI ve teknoloji trendleri hakkında konuşmak isteyen öğrenciler",
                category: "technology",
                member_count: 24,
                compatibility_score: 0.92,
                max_members: 30,
                tags: ["programming", "ai", "innovation"],
                is_member: false
            },
            {
                id: 2,
                name: "Spor ve Sağlık",
                description: "Fitness, spor aktiviteleri ve sağlıklı yaşam üzerine paylaşımlar",
                category: "sports",
                member_count: 18,
                compatibility_score: 0.85,
                max_members: 25,
                tags: ["fitness", "health", "sports"],
                is_member: true
            },
            {
                id: 3,
                name: "Sanat ve Kültür",
                description: "Resim, müzik, tiyatro ve diğer sanat formlarını sevenler",
                category: "arts",
                member_count: 15,
                compatibility_score: 0.78,
                max_members: 20,
                tags: ["art", "music", "culture"],
                is_member: false
            },
            {
                id: 4,
                name: "Doğa Kaşifleri",
                description: "Doğa yürüyüşü, kamp ve açık hava aktiviteleri sevenler",
                category: "outdoor",
                member_count: 12,
                compatibility_score: 0.88,
                max_members: 20,
                tags: ["nature", "hiking", "camping"],
                is_member: false
            }
        ];
    }

    renderUserCommunities() {
        const container = document.getElementById('userCommunitiesList');

        if (this.userCommunities.length === 0) {
            container.innerHTML = `
                <div class="sidebar-community">
                    <div class="community-dot"></div>
                    <span>Henüz topluluğun yok</span>
                </div>
            `;
            return;
        }

        container.innerHTML = this.userCommunities.map(community => `
            <div class="sidebar-community ${community.id === 1 ? 'active' : ''}" 
                 data-community-id="${community.id}">
                <div class="community-dot"></div>
                <span>${community.name}</span>
            </div>
        `).join('');
    }

    renderRecommendedCommunities() {
        const container = document.getElementById('recommendationsGrid');

        if (this.recommendedCommunities.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon">
                        <i class="fas fa-users"></i>
                    </div>
                    <h3>Henüz öneri yok</h3>
                    <p>Testleri tamamladıktan sonra öneriler burada görünecek</p>
                </div>
            `;
            return;
        }

        container.innerHTML = this.recommendedCommunities.map(community => `
            <div class="community-card recommended" data-community-id="${community.id}">
                <div class="community-header">
                    <div class="community-icon">
                        <i class="fas ${this.getCategoryIcon(community.category)}"></i>
                    </div>
                    <div class="community-info">
                        <div class="community-name">${community.name}</div>
                        <div class="community-category">${this.formatCategory(community.category)}</div>
                        <div class="community-description">${community.description}</div>
                    </div>
                </div>
                
                <div class="community-stats">
                    <div class="stat">
                        <div class="stat-number">${community.member_count}</div>
                        <div class="stat-label">Üye</div>
                    </div>
                    <div class="compatibility-score">
                        <div class="score-value">%${Math.round(community.compatibility_score * 100)}</div>
                        <div class="score-label">Uyum</div>
                    </div>
                </div>
                
                <div class="community-actions">
                    <button class="btn btn-primary btn-join ${community.is_member ? 'btn-joined' : ''}" 
                            data-community-id="${community.id}">
                        <i class="fas ${community.is_member ? 'fa-check' : 'fa-plus'}"></i>
                        ${community.is_member ? 'Katıldın' : 'Topluluğa Katıl'}
                    </button>
                </div>
            </div>
        `).join('');
    }

    renderAllCommunities() {
        const container = document.getElementById('communitiesGrid');

        container.innerHTML = this.allCommunities.map(community => `
            <div class="community-card" data-community-id="${community.id}">
                <div class="community-header">
                    <div class="community-icon">
                        <i class="fas ${this.getCategoryIcon(community.category)}"></i>
                    </div>
                    <div class="community-info">
                        <div class="community-name">${community.name}</div>
                        <div class="community-category">${this.formatCategory(community.category)}</div>
                        <div class="community-description">${community.description}</div>
                    </div>
                </div>
                
                <div class="community-stats">
                    <div class="stat">
                        <div class="stat-number">${community.member_count}/${community.max_members}</div>
                        <div class="stat-label">Üye</div>
                    </div>
                    <div class="compatibility-score">
                        <div class="score-value">%${Math.round(community.compatibility_score * 100)}</div>
                        <div class="score-label">Uyum</div>
                    </div>
                </div>
                
                <div class="community-actions">
                    <button class="btn btn-primary btn-join ${community.is_member ? 'btn-joined' : ''}" 
                            data-community-id="${community.id}">
                        <i class="fas ${community.is_member ? 'fa-check' : 'fa-plus'}"></i>
                        ${community.is_member ? 'Katıldın' : 'Topluluğa Katıl'}
                    </button>
                </div>
            </div>
        `).join('');
    }

    renderSimilarUsers() {
        const container = document.getElementById('similarUsersGrid');

        if (this.similarUsers.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon">
                        <i class="fas fa-user-friends"></i>
                    </div>
                    <h3>Henüz benzer kullanıcı bulunamadı</h3>
                    <p>Daha fazla öğrenci katıldıkça benzerlikler görünecek</p>
                </div>
            `;
            return;
        }

        container.innerHTML = this.similarUsers.map(user => `
            <div class="user-card">
                <div class="user-avatar">${user.user.name.charAt(0).toUpperCase()}</div>
                <div class="user-name">${user.user.name}</div>
                <div class="user-university">${user.user.university}</div>
                <div class="similarity-score">%${Math.round(user.similarity_score * 100)} Uyum</div>
                
                <div class="user-hobbies">
                    ${user.user.hobbies.slice(0, 3).map(hobby => `
                        <span class="hobby-tag">${hobby}</span>
                    `).join('')}
                    ${user.user.hobbies.length > 3 ? `<span class="hobby-tag">+${user.user.hobbies.length - 3}</span>` : ''}
                </div>
                
                <div class="user-actions">
                    <button class="btn btn-secondary btn-small">
                        <i class="fas fa-user-plus"></i>
                        Takip Et
                    </button>
                    <button class="btn btn-primary btn-small">
                        <i class="fas fa-comment"></i>
                        Mesaj
                    </button>
                </div>
            </div>
        `).join('');
    }

    getCategoryIcon(category) {
        const icons = {
            'technology': 'laptop-code',
            'sports': 'running',
            'arts': 'palette',
            'outdoor': 'mountain',
            'education': 'graduation-cap',
            'social': 'users'
        };
        return icons[category] || 'users';
    }

    formatCategory(category) {
        const categories = {
            'technology': 'Teknoloji',
            'sports': 'Spor',
            'arts': 'Sanat',
            'outdoor': 'Açık Hava',
            'education': 'Eğitim',
            'social': 'Sosyal'
        };
        return categories[category] || category;
    }

    setupEventListeners() {
        // Create community modal
        document.getElementById('createCommunityBtn').addEventListener('click', () => {
            this.showCreateCommunityModal();
        });

        document.getElementById('createFirstCommunityBtn').addEventListener('click', () => {
            this.showCreateCommunityModal();
        });

        // Modal close
        document.getElementById('closeModalBtn').addEventListener('click', () => {
            this.hideCreateCommunityModal();
        });

        document.getElementById('cancelCreateBtn').addEventListener('click', () => {
            this.hideCreateCommunityModal();
        });

        // Create community form
        document.getElementById('createCommunityForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleCreateCommunity();
        });

        // Join community buttons
        document.addEventListener('click', (e) => {
            if (e.target.closest('.btn-join')) {
                const button = e.target.closest('.btn-join');
                this.handleJoinCommunity(button.dataset.communityId, button);
            }
        });

        // Search and filter
        document.getElementById('communitySearch').addEventListener('input', (e) => {
            this.handleSearch(e.target.value);
        });

        document.getElementById('categoryFilter').addEventListener('change', (e) => {
            this.handleFilter(e.target.value);
        });
    }

    showCreateCommunityModal() {
        document.getElementById('createCommunityModal').classList.add('show');
    }

    hideCreateCommunityModal() {
        document.getElementById('createCommunityModal').classList.remove('show');
    }

    async handleCreateCommunity() {
        const form = document.getElementById('createCommunityForm');
        const formData = new FormData(form);
        const data = {
            name: formData.get('name'),
            description: formData.get('description'),
            category: formData.get('category'),
            max_members: parseInt(formData.get('max_members')),
            tags: formData.get('tags') ? formData.get('tags').split(',').map(tag => tag.trim()) : []
        };

        const submitBtn = form.querySelector('button[type="submit"]');
        this.setLoadingState(submitBtn, true);

        try {
            const user = JSON.parse(localStorage.getItem('friendzone_user'));
            const response = await fetch('/api/community/create', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('friendzone_token')}`
                },
                body: JSON.stringify({
                    ...data,
                    created_by: user.id
                })
            });

            const result = await response.json();

            if (response.ok) {
                this.hideCreateCommunityModal();
                form.reset();
                this.showSuccess('Topluluk başarıyla oluşturuldu!');
                this.loadUserCommunities();
                this.loadAllCommunities();
            } else {
                throw new Error(result.message || 'Topluluk oluşturulamadı');
            }

        } catch (error) {
            console.error('Topluluk oluşturma hatası:', error);
            this.showError('Topluluk oluşturulurken bir hata oluştu: ' + error.message);
        } finally {
            this.setLoadingState(submitBtn, false);
        }
    }

    async handleJoinCommunity(communityId, button) {
        if (button.classList.contains('btn-joined')) {
            // Already joined, show community page
            window.location.href = `community.html?id=${communityId}`;
            return;
        }

        this.setLoadingState(button, true);

        try {
            const user = JSON.parse(localStorage.getItem('friendzone_user'));
            const response = await fetch('/api/community/join', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('friendzone_token')}`
                },
                body: JSON.stringify({
                    user_id: user.id,
                    community_id: communityId
                })
            });

            const result = await response.json();

            if (response.ok) {
                button.classList.add('btn-joined');
                button.innerHTML = '<i class="fas fa-check"></i> Katıldın';
                this.showSuccess('Topluluğa başarıyla katıldın!');
                this.loadUserCommunities();
            } else {
                throw new Error(result.message || 'Topluluğa katılamadı');
            }

        } catch (error) {
            console.error('Topluluğa katılma hatası:', error);
            this.showError('Topluluğa katılırken bir hata oluştu: ' + error.message);
        } finally {
            this.setLoadingState(button, false);
        }
    }

    handleSearch(query) {
        const communities = document.querySelectorAll('.community-card');
        communities.forEach(card => {
            const name = card.querySelector('.community-name').textContent.toLowerCase();
            const description = card.querySelector('.community-description').textContent.toLowerCase();
            const searchTerm = query.toLowerCase();

            if (name.includes(searchTerm) || description.includes(searchTerm)) {
                card.style.display = 'block';
            } else {
                card.style.display = 'none';
            }
        });
    }

    handleFilter(category) {
        const communities = document.querySelectorAll('.community-card');
        communities.forEach(card => {
            const communityCategory = card.querySelector('.community-category').textContent.toLowerCase();
            const categoryTerm = this.formatCategory(category).toLowerCase();

            if (!category || communityCategory === categoryTerm) {
                card.style.display = 'block';
            } else {
                card.style.display = 'none';
            }
        });
    }

    setLoadingState(button, isLoading) {
        if (isLoading) {
            button.classList.add('btn-loading');
            button.disabled = true;
        } else {
            button.classList.remove('btn-loading');
            button.disabled = false;
        }
    }

    showSuccess(message) {
        if (window.app && window.app.showNotification) {
            window.app.showNotification(message, 'success');
        } else {
            alert(message);
        }
    }

    showError(message) {
        if (window.app && window.app.showNotification) {
            window.app.showNotification(message, 'error');
        } else {
            alert('Hata: ' + message);
        }
    }

    loadUserData() {
        const user = JSON.parse(localStorage.getItem('friendzone_user'));
        if (user) {
            document.getElementById('userName').textContent = user.name;
            document.getElementById('userAvatar').textContent = user.name.charAt(0).toUpperCase();
        }
    }

    showRecommendationsError() {
        const container = document.getElementById('recommendationsGrid');
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">
                    <i class="fas fa-exclamation-triangle"></i>
                </div>
                <h3>Öneriler yüklenemedi</h3>
                <p>Lütfen daha sonra tekrar deneyin</p>
            </div>
        `;
    }
}

// Initialize community handler
document.addEventListener('DOMContentLoaded', () => {
    window.communityHandler = new CommunityHandler();
});