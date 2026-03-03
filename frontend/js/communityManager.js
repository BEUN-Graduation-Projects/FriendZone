// frontend/js/communityManager.js

class CommunityManager {
    constructor() {
        this.currentCommunity = null;
        this.communityMembers = [];
        this.chatMessages = [];
        this.activities = [];
        this.init();
    }

    async init() {
        await this.loadCommunityData();
        await this.loadCommunityMembers();
        await this.loadChatMessages();
        await this.loadActivities();
        this.setupEventListeners();
        this.loadUserData();
    }

    async loadCommunityData() {
        try {
            const urlParams = new URLSearchParams(window.location.search);
            const communityId = urlParams.get('id') || 1;

            const token = localStorage.getItem('friendzone_token');
            const response = await fetch(`/api/community/${communityId}`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });

            const data = await response.json();

            if (data.success) {
                this.currentCommunity = data.community;
                this.renderCommunityData();
            } else {
                throw new Error('Topluluk yüklenemedi');
            }
        } catch (error) {
            console.error('Topluluk verisi yüklenemedi:', error);
            this.showFallbackCommunity();
        }
    }

    loadCommunityMembers() {
        this.communityMembers = this.generateSampleMembers();
        this.renderCommunityMembers();
    }

    loadChatMessages() {
        this.chatMessages = this.generateSampleMessages();
        this.renderChatMessages();
    }

    loadActivities() {
        this.activities = this.generateSampleActivities();
        this.renderActivities();
    }

    generateSampleMembers() {
        return [
            { id: 1, name: "Ahmet Yılmaz", role: "admin", university: "İTÜ", department: "Bilgisayar", joined_at: "2024-01-15", is_online: true },
            { id: 2, name: "Ayşe Demir", role: "member", university: "Boğaziçi", department: "Psikoloji", joined_at: "2024-01-20", is_online: true },
            { id: 3, name: "Mehmet Kaya", role: "member", university: "ODTÜ", department: "İşletme", joined_at: "2024-01-22", is_online: false }
        ];
    }

    generateSampleMessages() {
        return [
            { id: 1, user_id: 1, user_name: "Ahmet Yılmaz", content: "Merhaba arkadaşlar! Bu hafta sonu için bir workshop düzenleyelim mi?", timestamp: new Date(Date.now() - 30 * 60000).toISOString() },
            { id: 2, user_id: 2, user_name: "Ayşe Demir", content: "Harika fikir! Ben katılmak isterim.", timestamp: new Date(Date.now() - 25 * 60000).toISOString() }
        ];
    }

    generateSampleActivities() {
        return [
            { id: 1, type: "event_created", user_name: "Ahmet Yılmaz", content: "yeni bir etkinlik oluşturdu", timestamp: new Date(Date.now() - 30 * 60000).toISOString(), icon: "fa-calendar-plus" },
            { id: 2, type: "member_joined", user_name: "Zeynep Şahin", content: "topluluğa katıldı", timestamp: new Date(Date.now() - 2 * 24 * 60 * 60000).toISOString(), icon: "fa-user-plus" }
        ];
    }

    renderCommunityData() {
        if (!this.currentCommunity) return;

        const elements = {
            communityName: document.getElementById('communityName'),
            communityDescription: document.getElementById('communityDescription'),
            memberCountText: document.getElementById('memberCountText'),
            sidebarMemberCount: document.getElementById('sidebarMemberCount'),
            compatibilityScore: document.getElementById('compatibilityScore'),
            communityCategory: document.getElementById('communityCategory'),
            communityHeaderIcon: document.getElementById('communityHeaderIcon')
        };

        if (elements.communityName) elements.communityName.textContent = this.currentCommunity.name;
        if (elements.communityDescription) elements.communityDescription.textContent = this.currentCommunity.description;
        if (elements.memberCountText) elements.memberCountText.textContent = `${this.currentCommunity.member_count || 0} üye`;
        if (elements.sidebarMemberCount) elements.sidebarMemberCount.textContent = `${this.currentCommunity.member_count || 0} üye`;
        if (elements.compatibilityScore) {
            elements.compatibilityScore.innerHTML = `<i class="fas fa-heart"></i> %${Math.round((this.currentCommunity.compatibility_score || 0.85) * 100)} uyum`;
        }
        if (elements.communityCategory) {
            elements.communityCategory.innerHTML = `<i class="fas fa-tag"></i> ${this.formatCategory(this.currentCommunity.category)}`;
        }
        if (elements.communityHeaderIcon) {
            elements.communityHeaderIcon.className = `fas ${this.getCategoryIcon(this.currentCommunity.category)}`;
        }

        this.renderCommunitySidebar();
        this.renderCommunityStats();
    }

    renderCommunitySidebar() {
        const container = document.getElementById('communitySidebarInfo');
        if (!container || !this.currentCommunity) return;

        container.innerHTML = `
            <div class="sidebar-community active">
                <div class="community-dot"></div>
                <span>${this.currentCommunity.name}</span>
            </div>
        `;
    }

    renderCommunityMembers() {
        const container = document.getElementById('membersList');
        if (!container) return;

        container.innerHTML = this.communityMembers.map(member => `
            <div class="member-item ${member.is_online ? 'online' : 'offline'}">
                <div class="member-avatar">${member.name.charAt(0).toUpperCase()}</div>
                <div class="member-info">
                    <div class="member-name">
                        ${member.name}
                        ${member.role === 'admin' ? '<span class="role-badge">Admin</span>' : ''}
                    </div>
                    <div class="member-department">${member.department}</div>
                </div>
            </div>
        `).join('');
    }

    renderChatMessages() {
        const container = document.getElementById('chatMessages');
        if (!container) return;

        container.innerHTML = this.chatMessages.map(msg => `
            <div class="chat-message">
                <div class="message-avatar">${msg.user_name.charAt(0).toUpperCase()}</div>
                <div class="message-content">
                    <div class="message-header">
                        <span class="message-sender">${msg.user_name}</span>
                        <span class="message-time">${this.formatTime(msg.timestamp)}</span>
                    </div>
                    <div class="message-text">${msg.content}</div>
                </div>
            </div>
        `).join('');

        container.scrollTop = container.scrollHeight;
    }

    renderActivities() {
        const container = document.getElementById('activitiesList');
        if (!container) return;

        container.innerHTML = this.activities.map(activity => `
            <div class="activity-item">
                <div class="activity-icon"><i class="fas ${activity.icon}"></i></div>
                <div class="activity-content">
                    <div class="activity-text"><strong>${activity.user_name}</strong> ${activity.content}</div>
                    <div class="activity-time">${this.formatTime(activity.timestamp)}</div>
                </div>
            </div>
        `).join('');
    }

    renderCommunityStats() {
        const container = document.getElementById('communityStats');
        if (!container) return;

        const stats = this.calculateCommunityStats();

        container.innerHTML = `
            <div class="stat-item"><div class="stat-value">${stats.activeMembers}</div><div class="stat-label">Aktif Üye</div></div>
            <div class="stat-item"><div class="stat-value">${stats.avgCompatibility}%</div><div class="stat-label">Ort. Uyum</div></div>
            <div class="stat-item"><div class="stat-value">${stats.activitiesThisWeek}</div><div class="stat-label">Bu Hafta</div></div>
            <div class="stat-item"><div class="stat-value">${stats.responseTime}h</div><div class="stat-label">Yanıt Süresi</div></div>
        `;
    }

    calculateCommunityStats() {
        const activeMembers = this.communityMembers.filter(m => m.is_online).length;
        const avgCompatibility = Math.round((this.currentCommunity?.compatibility_score || 0.85) * 100);
        const activitiesThisWeek = this.activities.filter(a =>
            new Date(a.timestamp) > new Date(Date.now() - 7 * 24 * 60 * 60 * 1000)
        ).length;

        return { activeMembers, avgCompatibility, activitiesThisWeek, responseTime: 2.5 };
    }

    setupEventListeners() {
        const sendBtn = document.getElementById('sendMessageBtn');
        if (sendBtn) sendBtn.addEventListener('click', () => this.sendMessage());

        const msgInput = document.getElementById('messageInput');
        if (msgInput) {
            msgInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') this.sendMessage();
            });
        }

        const leaveBtn = document.getElementById('leaveCommunityBtn');
        if (leaveBtn) leaveBtn.addEventListener('click', () => this.leaveCommunity());

        const clearBtn = document.getElementById('clearChatBtn');
        if (clearBtn) clearBtn.addEventListener('click', () => this.clearChat());

        const gptBtn = document.getElementById('gptAssistantBtn');
        if (gptBtn) gptBtn.addEventListener('click', () => this.openAssistantModal());

        document.querySelectorAll('.assistant-btn').forEach(btn => {
            btn.addEventListener('click', () => this.handleAssistantAction(btn.dataset.type));
        });
    }

    sendMessage() {
        const input = document.getElementById('messageInput');
        if (!input) return;

        const message = input.value.trim();
        if (!message) return;

        const user = JSON.parse(localStorage.getItem('friendzone_user')) || { name: 'Misafir', id: 999 };
        const newMessage = {
            id: Date.now(),
            user_id: user.id,
            user_name: user.name,
            content: message,
            timestamp: new Date().toISOString()
        };

        this.chatMessages.push(newMessage);
        this.renderChatMessages();
        input.value = '';

        setTimeout(() => this.simulateResponse(message), 1000 + Math.random() * 2000);
    }

    simulateResponse(originalMessage) {
        const responses = ["Harika fikir!", "Kesinlikle katılıyorum.", "Bunu daha önce düşünmemiştim."];
        const randomUser = this.communityMembers[Math.floor(Math.random() * this.communityMembers.length)];

        this.chatMessages.push({
            id: Date.now(),
            user_id: randomUser.id,
            user_name: randomUser.name,
            content: responses[Math.floor(Math.random() * responses.length)],
            timestamp: new Date().toISOString()
        });

        this.renderChatMessages();
    }

    async leaveCommunity() {
        if (!confirm('Bu topluluktan ayrılmak istediğinizden emin misiniz?')) return;

        try {
            const user = JSON.parse(localStorage.getItem('friendzone_user'));
            const token = localStorage.getItem('friendzone_token');

            if (!user || !token) {
                window.location.href = 'login.html';
                return;
            }

            const response = await fetch('/api/community/leave', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({ user_id: user.id, community_id: this.currentCommunity.id })
            });

            if (response.ok) {
                this.showSuccess('Topluluktan ayrıldınız');
                setTimeout(() => window.location.href = 'communities.html', 1500);
            } else {
                throw new Error('Topluluktan ayrılamadı');
            }
        } catch (error) {
            console.error('Ayrılma hatası:', error);
            this.showError('Topluluktan ayrılırken bir hata oluştu');
        }
    }

    clearChat() {
        if (!confirm('Tüm sohbet geçmişini temizlemek istediğinizden emin misiniz?')) return;
        this.chatMessages = [];
        this.renderChatMessages();
        this.showSuccess('Sohbet geçmişi temizlendi');
    }

    openAssistantModal() {
        const modal = document.getElementById('assistantModal');
        if (modal) modal.classList.add('show');
    }

    handleAssistantAction(type) {
        if (window.gptAssistant) {
            window.gptAssistant.getSuggestion(type);
        } else {
            this.showError('AI asistanı henüz hazır değil');
        }
    }

    getCategoryIcon(category) {
        const icons = { 'technology': 'fa-laptop-code', 'sports': 'fa-running', 'arts': 'fa-palette', 'outdoor': 'fa-mountain', 'education': 'fa-graduation-cap', 'social': 'fa-users' };
        return icons[category] || 'fa-users';
    }

    formatCategory(category) {
        const categories = { 'technology': 'Teknoloji', 'sports': 'Spor', 'arts': 'Sanat', 'outdoor': 'Açık Hava', 'education': 'Eğitim', 'social': 'Sosyal' };
        return categories[category] || category;
    }

    formatTime(timestamp) {
        const date = new Date(timestamp);
        const now = new Date();
        const diffMins = Math.floor((now - date) / 60000);

        if (diffMins < 1) return 'şimdi';
        if (diffMins < 60) return `${diffMins} dk önce`;
        if (diffMins < 1440) return `${Math.floor(diffMins / 60)} sa önce`;
        return `${Math.floor(diffMins / 1440)} gün önce`;
    }

    showFallbackCommunity() {
        this.currentCommunity = {
            id: 1,
            name: "Teknoloji Meraklıları",
            description: "Yazılım, AI ve teknoloji trendleri hakkında konuşan öğrenciler",
            category: "technology",
            member_count: 24,
            compatibility_score: 0.92
        };
        this.renderCommunityData();
    }

    showSuccess(message) {
        if (window.app?.showNotification) window.app.showNotification(message, 'success');
        else alert(message);
    }

    showError(message) {
        if (window.app?.showNotification) window.app.showNotification(message, 'error');
        else alert('Hata: ' + message);
    }

    loadUserData() {
        const user = JSON.parse(localStorage.getItem('friendzone_user'));
        if (user) {
            const userName = document.getElementById('userName');
            const userAvatar = document.getElementById('userAvatar');
            if (userName) userName.textContent = user.name || 'Kullanıcı';
            if (userAvatar) userAvatar.textContent = (user.name || 'K').charAt(0).toUpperCase();
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.communityManager = new CommunityManager();
});