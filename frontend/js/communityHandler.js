// frontend/js/communityHandler.js

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
            const token = localStorage.getItem('friendzone_token');

            if (!user || !token) return;

            const response = await fetch(`/api/community/user/${user.id}`, {
                headers: { 'Authorization': `Bearer ${token}` }
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
        if (!loadingElement) return;

        try {
            const user = JSON.parse(localStorage.getItem('friendzone_user'));
            const token = localStorage.getItem('friendzone_token');

            if (!user || !token) return;

            const response = await fetch(`/api/community/recommendations/${user.id}`, {
                headers: { 'Authorization': `Bearer ${token}` }
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
        }
    }

    async loadAllCommunities() {
        const loadingElement = document.getElementById('communitiesLoading');
        const emptyElement = document.getElementById('communitiesEmpty');
        if (!loadingElement) return;

        try {
            this.allCommunities = this.generateSampleCommunities();
            this.renderAllCommunities();

            loadingElement.style.display = 'none';

            if (this.allCommunities.length === 0 && emptyElement) {
                emptyElement.style.display = 'block';
            }
        } catch (error) {
            console.error('Topluluklar yüklenemedi:', error);
            loadingElement.style.display = 'none';
            if (emptyElement) emptyElement.style.display = 'block';
        }
    }

    async loadSimilarUsers() {
        const loadingElement = document.getElementById('similarUsersLoading');
        if (!loadingElement) return;

        try {
            const user = JSON.parse(localStorage.getItem('friendzone_user'));
            const token = localStorage.getItem('friendzone_token');

            if (!user || !token) return;

            const response = await fetch(`/api/community/similar-users/${user.id}`, {
                headers: { 'Authorization': `Bearer ${token}` }
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
                max_members: 30,
                compatibility_score: 0.92,
                tags: ["programming", "ai", "innovation"],
                is_member: false
            },
            {
                id: 2,
                name: "Spor ve Sağlık",
                description: "Fitness, spor aktiviteleri ve sağlıklı yaşam üzerine paylaşımlar",
                category: "sports",
                member_count: 18,
                max_members: 25,
                compatibility_score: 0.85,
                tags: ["fitness", "health", "sports"],
                is_member: false
            },
            {
                id: 3,
                name: "Sanat ve Kültür",
                description: "Resim, müzik, tiyatro ve diğer sanat formlarını sevenler",
                category: "arts",
                member_count: 15,
                max_members: 20,
                compatibility_score: 0.78,
                tags: ["art", "music", "culture"],
                is_member: false
            }
        ];
    }

    renderUserCommunities() {
        const container = document.getElementById('userCommunitiesList');
        if (!container) return;

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
            <div class="sidebar-community" data-community-id="${community.id}">
                <div class="community-dot"></div>
                <span>${community.name}</span>
            </div>
        `).join('');
    }

    renderRecommendedCommunities() {
        const container = document.getElementById('recommendationsGrid');
        if (!container) return;

        if (this.recommendedCommunities.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon"><i class="fas fa-users"></i></div>
                    <h3>Henüz öneri yok</h3>
                    <p>Testleri tamamladıktan sonra öneriler burada görünecek</p>
                </div>
            `;
            return;
        }

        container.innerHTML = this.recommendedCommunities.map(community => `
            <div class="community-card recommended" data-community-id="${community.id}">
                <div class="community-header">
                    <div class="community-icon"><i class="fas ${this.getCategoryIcon(community.category)}"></i></div>
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
                    <button class="btn btn-primary btn-join" data-community-id="${community.id}">
                        <i class="fas fa-plus"></i> Topluluğa Katıl
                    </button>
                </div>
            </div>
        `).join('');
    }

    renderAllCommunities() {
        const container = document.getElementById('communitiesGrid');
        if (!container) return;

        container.innerHTML = this.allCommunities.map(community => `
            <div class="community-card" data-community-id="${community.id}">
                <div class="community-header">
                    <div class="community-icon"><i class="fas ${this.getCategoryIcon(community.category)}"></i></div>
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
                    <button class="btn btn-primary btn-join" data-community-id="${community.id}">
                        <i class="fas fa-plus"></i> Topluluğa Katıl
                    </button>
                </div>
            </div>
        `).join('');
    }

    renderSimilarUsers(users) {
        const container = document.getElementById('similarUsersGrid');
        if (!container) return;

        const usersToRender = users || this.similarUsers;

        if (usersToRender.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon"><i class="fas fa-user-friends"></i></div>
                    <h3>Henüz benzer kullanıcı bulunamadı</h3>
                </div>
            `;
            return;
        }

        container.innerHTML = usersToRender.slice(0, 4).map(user => `
            <div class="user-card">
                <div class="user-avatar">${(user.user?.name || '?').charAt(0).toUpperCase()}</div>
                <div class="user-name">${user.user?.name || 'İsimsiz'}</div>
                <div class="similarity-score">%${Math.round(user.similarity_score * 100)} Uyum</div>
                <div class="user-actions">
                    <button class="btn btn-secondary btn-small"><i class="fas fa-user-plus"></i></button>
                    <button class="btn btn-primary btn-small"><i class="fas fa-comment"></i></button>
                </div>
            </div>
        `).join('');
    }

    getCategoryIcon(category) {
        const icons = { 'technology': 'fa-laptop-code', 'sports': 'fa-running', 'arts': 'fa-palette', 'outdoor': 'fa-mountain', 'education': 'fa-graduation-cap', 'social': 'fa-users' };
        return icons[category] || 'fa-users';
    }

    formatCategory(category) {
        const categories = { 'technology': 'Teknoloji', 'sports': 'Spor', 'arts': 'Sanat', 'outdoor': 'Açık Hava', 'education': 'Eğitim', 'social': 'Sosyal' };
        return categories[category] || category;
    }

    setupEventListeners() {
        const createCommunityBtn = document.getElementById('createCommunityBtn');
        if (createCommunityBtn) {
            createCommunityBtn.addEventListener('click', () => this.showCreateCommunityModal());
        }

        const createFirstCommunityBtn = document.getElementById('createFirstCommunityBtn');
        if (createFirstCommunityBtn) {
            createFirstCommunityBtn.addEventListener('click', () => this.showCreateCommunityModal());
        }

        const closeModalBtn = document.getElementById('closeModalBtn');
        if (closeModalBtn) {
            closeModalBtn.addEventListener('click', () => this.hideCreateCommunityModal());
        }

        const cancelCreateBtn = document.getElementById('cancelCreateBtn');
        if (cancelCreateBtn) {
            cancelCreateBtn.addEventListener('click', () => this.hideCreateCommunityModal());
        }

        const createCommunityForm = document.getElementById('createCommunityForm');
        if (createCommunityForm) {
            createCommunityForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleCreateCommunity();
            });
        }

        document.addEventListener('click', (e) => {
            if (e.target.closest('.btn-join')) {
                const button = e.target.closest('.btn-join');
                this.handleJoinCommunity(button.dataset.communityId, button);
            }
        });

        const searchInput = document.getElementById('communitySearch');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => this.handleSearch(e.target.value));
        }

        const categoryFilter = document.getElementById('categoryFilter');
        if (categoryFilter) {
            categoryFilter.addEventListener('change', (e) => this.handleFilter(e.target.value));
        }
    }

    showCreateCommunityModal() {
        const modal = document.getElementById('createCommunityModal');
        if (modal) modal.classList.add('show');
    }

    hideCreateCommunityModal() {
        const modal = document.getElementById('createCommunityModal');
        if (modal) modal.classList.remove('show');
    }

    async handleCreateCommunity() {
        const form = document.getElementById('createCommunityForm');
        if (!form) return;

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
            const token = localStorage.getItem('friendzone_token');

            if (!user || !token) {
                window.location.href = 'login.html';
                return;
            }

            const response = await fetch('/api/community/create', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({ ...data, created_by: user.id })
            });

            if (response.ok) {
                this.hideCreateCommunityModal();
                form.reset();
                this.showSuccess('Topluluk başarıyla oluşturuldu!');
                this.loadUserCommunities();
                this.loadAllCommunities();
            } else {
                throw new Error('Topluluk oluşturulamadı');
            }
        } catch (error) {
            console.error('Topluluk oluşturma hatası:', error);
            this.showError('Topluluk oluşturulurken bir hata oluştu');
        } finally {
            this.setLoadingState(submitBtn, false);
        }
    }

    async handleJoinCommunity(communityId, button) {
        this.setLoadingState(button, true);

        try {
            const user = JSON.parse(localStorage.getItem('friendzone_user'));
            const token = localStorage.getItem('friendzone_token');

            if (!user || !token) {
                window.location.href = 'login.html';
                return;
            }

            const response = await fetch('/api/community/join', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({ user_id: user.id, community_id: parseInt(communityId) })
            });

            if (response.ok) {
                button.innerHTML = '<i class="fas fa-check"></i> Katıldın';
                button.classList.add('btn-joined');
                this.showSuccess('Topluluğa başarıyla katıldın!');
                this.loadUserCommunities();
            } else {
                throw new Error('Topluluğa katılamadı');
            }
        } catch (error) {
            console.error('Topluluğa katılma hatası:', error);
            this.showError('Topluluğa katılırken bir hata oluştu');
        } finally {
            this.setLoadingState(button, false);
        }
    }

    handleSearch(query) {
        const communities = document.querySelectorAll('.community-card');
        communities.forEach(card => {
            const name = card.querySelector('.community-name')?.textContent.toLowerCase() || '';
            const description = card.querySelector('.community-description')?.textContent.toLowerCase() || '';
            const searchTerm = query.toLowerCase();

            card.style.display = (name.includes(searchTerm) || description.includes(searchTerm)) ? 'block' : 'none';
        });
    }

    handleFilter(category) {
        const communities = document.querySelectorAll('.community-card');
        communities.forEach(card => {
            const communityCategory = card.querySelector('.community-category')?.textContent.toLowerCase() || '';

            if (!category || communityCategory === this.formatCategory(category).toLowerCase()) {
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
            const userName = document.getElementById('userName');
            const userAvatar = document.getElementById('userAvatar');
            const userStatus = document.getElementById('userStatus');

            if (userName) userName.textContent = user.name || 'Kullanıcı';
            if (userAvatar) userAvatar.textContent = (user.name || 'K').charAt(0).toUpperCase();
            if (userStatus) userStatus.textContent = 'Çevrimiçi';
        }
    }
}

// Initialize community handler
document.addEventListener('DOMContentLoaded', () => {
    window.communityHandler = new CommunityHandler();
});