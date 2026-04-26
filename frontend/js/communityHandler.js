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
            const res = await fetch(`http://localhost:5001/api/community/user/${user.id}`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            const data = await res.json();
            if (data.success) {
                this.userCommunities = data.communities;
                this.renderUserCommunities();
            }
        } catch (error) {
            console.error('Kullanıcı toplulukları yüklenemedi:', error);
        }
    }

    async loadRecommendedCommunities() {
        try {
            const user = JSON.parse(localStorage.getItem('friendzone_user'));
            const token = localStorage.getItem('friendzone_token');
            if (!user || !token) return;
            const res = await fetch(`http://localhost:5001/api/community/recommendations/${user.id}`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            const data = await res.json();
            if (data.success) {
                this.recommendedCommunities = data.recommendations.filter(c => !c.is_member).slice(0, 3);
                this.renderRecommendedCommunities();
            }
            document.getElementById('recommendationsLoading').style.display = 'none';
        } catch (error) {
            console.error('Öneri yüklenemedi:', error);
            document.getElementById('recommendationsLoading').style.display = 'none';
        }
    }

    async loadAllCommunities() {
        try {
            const user = JSON.parse(localStorage.getItem('friendzone_user'));
            const token = localStorage.getItem('friendzone_token');
            if (!user || !token) return;
            const res = await fetch(`http://localhost:5001/api/community/recommendations/${user.id}`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            const data = await res.json();
            if (data.success) {
                this.allCommunities = data.recommendations;
                this.renderAllCommunities();
            }
            document.getElementById('communitiesLoading').style.display = 'none';
        } catch (error) {
            console.error('Topluluklar yüklenemedi:', error);
            document.getElementById('communitiesLoading').style.display = 'none';
        }
    }

    async loadSimilarUsers() {
        // Benzer kullanıcılar için gerçek endpoint yoksa boş bırak
        document.getElementById('similarUsersLoading').style.display = 'none';
    }

    renderUserCommunities() {
        const container = document.getElementById('userCommunitiesList');
        if (!container) return;
        if (this.userCommunities.length === 0) {
            container.innerHTML = '<div class="sidebar-community"><div class="community-dot"></div><span>Henüz topluluğun yok</span></div>';
            return;
        }
        container.innerHTML = this.userCommunities.map(c => `
            <div class="sidebar-community" data-community-id="${c.id}">
                <div class="community-dot"></div>
                <span>${c.name}</span>
            </div>
        `).join('');
    }

    renderRecommendedCommunities() {
        const container = document.getElementById('recommendationsGrid');
        if (!container) return;
        if (this.recommendedCommunities.length === 0) {
            container.innerHTML = '<div class="empty-state"><div class="empty-icon"><i class="fas fa-users"></i></div><h3>Henüz öneri yok</h3></div>';
            return;
        }
        container.innerHTML = this.recommendedCommunities.map(c => this.communityCardHTML(c, true)).join('');
    }

    renderAllCommunities() {
        const container = document.getElementById('communitiesGrid');
        if (!container) return;
        if (this.allCommunities.length === 0) {
            container.innerHTML = '<div class="empty-state"><div class="empty-icon"><i class="fas fa-users"></i></div><h3>Hiç topluluk yok</h3></div>';
            return;
        }
        container.innerHTML = this.allCommunities.map(c => this.communityCardHTML(c, false)).join('');
    }

    communityCardHTML(c, recommended) {
        return `
            <div class="community-card ${recommended ? 'recommended' : ''}" data-community-id="${c.id}">
                <div class="community-header">
                    <div class="community-icon"><i class="fas ${this.getCategoryIcon(c.category)}"></i></div>
                    <div class="community-info">
                        <div class="community-name">${c.name}</div>
                        <div class="community-category">${this.formatCategory(c.category)}</div>
                        <div class="community-description">${c.description}</div>
                    </div>
                </div>
                <div class="community-stats">
                    <div class="stat"><div class="stat-number">${c.member_count}/${c.max_members}</div><div class="stat-label">Üye</div></div>
                    <div class="compatibility-score"><div class="score-value">%${Math.round(c.compatibility_score * 100)}</div><div class="score-label">Uyum</div></div>
                </div>
                <div class="community-actions">
                    <button class="btn btn-primary btn-join" data-community-id="${c.id}">
                        <i class="fas ${c.is_member ? 'fa-check' : 'fa-plus'}"></i> ${c.is_member ? 'Katıldın' : 'Topluluğa Katıl'}
                    </button>
                </div>
            </div>
        `;
    }

    getCategoryIcon(cat) {
        const icons = { technology: 'fa-laptop-code', sports: 'fa-running', arts: 'fa-palette', outdoor: 'fa-mountain', education: 'fa-graduation-cap', social: 'fa-users' };
        return icons[cat] || 'fa-users';
    }

    formatCategory(cat) {
        const cats = { technology: 'Teknoloji', sports: 'Spor', arts: 'Sanat', outdoor: 'Açık Hava', education: 'Eğitim', social: 'Sosyal' };
        return cats[cat] || cat;
    }

    setupEventListeners() {
        document.addEventListener('click', async (e) => {
            const btn = e.target.closest('.btn-join');
            if (btn) {
                const communityId = btn.dataset.communityId;
                await this.handleJoinCommunity(communityId, btn);
            }
        });
        document.getElementById('createCommunityBtn')?.addEventListener('click', () => this.showCreateCommunityModal());
        document.getElementById('closeModalBtn')?.addEventListener('click', () => this.hideCreateCommunityModal());
        document.getElementById('cancelCreateBtn')?.addEventListener('click', () => this.hideCreateCommunityModal());
        document.getElementById('createCommunityForm')?.addEventListener('submit', (e) => { e.preventDefault(); this.handleCreateCommunity(); });
        document.getElementById('communitySearch')?.addEventListener('input', (e) => this.handleSearch(e.target.value));
        document.getElementById('categoryFilter')?.addEventListener('change', (e) => this.handleFilter(e.target.value));
    }

    async handleJoinCommunity(communityId, button) {
        button.disabled = true;
        try {
            const user = JSON.parse(localStorage.getItem('friendzone_user'));
            const token = localStorage.getItem('friendzone_token');
            if (!user || !token) throw new Error('Oturum açık değil');
            const res = await fetch('http://localhost:5001/api/community/join', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
                body: JSON.stringify({ user_id: user.id, community_id: parseInt(communityId) })
            });
            const data = await res.json();
            if (data.success) {
                button.innerHTML = '<i class="fas fa-check"></i> Katıldın';
                button.classList.add('btn-joined');
                this.loadUserCommunities();
                this.loadAllCommunities();
            } else {
                alert(data.message);
            }
        } catch (error) {
            alert('Topluluğa katılırken hata oluştu: ' + error.message);
        } finally {
            button.disabled = false;
        }
    }

    showCreateCommunityModal() { document.getElementById('createCommunityModal')?.classList.add('show'); }
    hideCreateCommunityModal() { document.getElementById('createCommunityModal')?.classList.remove('show'); }

    async handleCreateCommunity() {
        const form = document.getElementById('createCommunityForm');
        const data = {
            name: form.name.value,
            description: form.description.value,
            category: form.category.value,
            max_members: parseInt(form.max_members.value),
            tags: form.tags.value.split(',').map(t => t.trim()).filter(t => t)
        };
        const user = JSON.parse(localStorage.getItem('friendzone_user'));
        const token = localStorage.getItem('friendzone_token');
        const res = await fetch('http://localhost:5001/api/community/create', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
            body: JSON.stringify({ ...data, created_by: user.id })
        });
        if (res.ok) {
            this.hideCreateCommunityModal();
            this.loadAllCommunities();
        } else {
            alert('Topluluk oluşturulamadı');
        }
    }

    handleSearch(query) { /* basit filtreleme */ }
    handleFilter(category) { /* basit filtreleme */ }
    loadUserData() { /* sidebar kullanıcı bilgilerini yükle */ }
}

document.addEventListener('DOMContentLoaded', () => { window.communityHandler = new CommunityHandler(); });