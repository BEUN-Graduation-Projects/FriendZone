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

            const response = await fetch(`/api/community/${communityId}`, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('friendzone_token')}`
                }
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

    async loadCommunityMembers() {
        try {
            if (!this.currentCommunity) return;

            this.communityMembers = this.generateSampleMembers();
            this.renderCommunityMembers();

        } catch (error) {
            console.error('Üyeler yüklenemedi:', error);
        }
    }

    async loadChatMessages() {
        try {
            if (!this.currentCommunity) return;

            this.chatMessages = this.generateSampleMessages();
            this.renderChatMessages();

        } catch (error) {
            console.error('Sohbet mesajları yüklenemedi:', error);
        }
    }

    async loadActivities() {
        try {
            if (!this.currentCommunity) return;

            this.activities = this.generateSampleActivities();
            this.renderActivities();

        } catch (error) {
            console.error('Aktiviteler yüklenemedi:', error);
        }
    }

    generateSampleMembers() {
        return [
            {
                id: 1,
                name: "Ahmet Yılmaz",
                role: "admin",
                university: "İstanbul Teknik Üniversitesi",
                department: "Bilgisayar Mühendisliği",
                joined_at: "2024-01-15",
                is_online: true
            },
            {
                id: 2,
                name: "Ayşe Demir",
                role: "member",
                university: "Boğaziçi Üniversitesi",
                department: "Psikoloji",
                joined_at: "2024-01-20",
                is_online: true
            },
            {
                id: 3,
                name: "Mehmet Kaya",
                role: "member",
                university: "Orta Doğu Teknik Üniversitesi",
                department: "İşletme",
                joined_at: "2024-01-22",
                is_online: false
            },
            {
                id: 4,
                name: "Zeynep Şahin",
                role: "member",
                university: "Hacettepe Üniversitesi",
                department: "Tıp",
                joined_at: "2024-01-25",
                is_online: true
            }
        ];
    }

    generateSampleMessages() {
        return [
            {
                id: 1,
                user_id: 1,
                user_name: "Ahmet Yılmaz",
                content: "Merhaba arkadaşlar! Bu hafta sonu için mini bir kodlama workshop'u düzenlemeyi düşünüyorum, ilgilenen var mı?",
                timestamp: "2024-01-28T14:30:00Z",
                type: "message"
            },
            {
                id: 2,
                user_id: 2,
                user_name: "Ayşe Demir",
                content: "Harika fikir! Ben katılmak istiyorum. Hangi konu üzerinde çalışmayı düşünüyorsun?",
                timestamp: "2024-01-28T14:32:00Z",
                type: "message"
            },
            {
                id: 3,
                user_id: 4,
                user_name: "Zeynep Şahin",
                content: "Ben de katılmak istiyorum. Python ile başlangıç seviyesinde bir proje yapabiliriz belki?",
                timestamp: "2024-01-28T14:35:00Z",
                type: "message"
            },
            {
                id: 4,
                user_id: 3,
                user_name: "Mehmet Kaya",
                content: "Mükemmel! Cuma akşamı uygun olan var mı?",
                timestamp: "2024-01-28T14:40:00Z",
                type: "message"
            }
        ];
    }

    generateSampleActivities() {
        return [
            {
                id: 1,
                type: "event_created",
                user_name: "Ahmet Yılmaz",
                content: "Kodlama Workshop'u oluşturuldu",
                timestamp: "2024-01-28T14:30:00Z",
                icon: "fa-calendar-plus"
            },
            {
                id: 2,
                type: "member_joined",
                user_name: "Zeynep Şahin",
                content: "topluluğa katıldı",
                timestamp: "2024-01-25T10:15:00Z",
                icon: "fa-user-plus"
            },
            {
                id: 3,
                type: "discussion_started",
                user_name: "Ayşe Demir",
                content: "yeni bir konu başlattı: 'AI Etik Kuralları'",
                timestamp: "2024-01-24T16:20:00Z",
                icon: "fa-comments"
            },
            {
                id: 4,
                type: "resource_shared",
                user_name: "Mehmet Kaya",
                content: "yeni bir kaynak paylaştı: 'Web Geliştirme Rehberi'",
                timestamp: "2024-01-23T11:45:00Z",
                icon: "fa-share-alt"
            }
        ];
    }

    renderCommunityData() {
        if (!this.currentCommunity) return;

        document.getElementById('communityName').textContent = this.currentCommunity.name;
        document.getElementById('communityDescription').textContent = this.currentCommunity.description;
        document.getElementById('memberCountText').textContent = `${this.currentCommunity.member_count} üye`;
        document.getElementById('sidebarMemberCount').textContent = `${this.currentCommunity.member_count} üye`;
        document.getElementById('compatibilityScore').innerHTML = `
            <i class="fas fa-heart"></i>
            %${Math.round(this.currentCommunity.compatibility_score * 100)} uyum
        `;
        document.getElementById('communityCategory').innerHTML = `
            <i class="fas fa-tag"></i>
            ${this.formatCategory(this.currentCommunity.category)}
        `;

        const iconElement = document.getElementById('communityHeaderIcon');
        iconElement.className = `fas ${this.getCategoryIcon(this.currentCommunity.category)}`;

        this.renderCommunitySidebar();
        this.renderCommunityStats();
    }

    renderCommunitySidebar() {
        const container = document.getElementById('communitySidebarInfo');
        container.innerHTML = `
            <div class="sidebar-community active">
                <div class="community-dot"></div>
                <span>${this.currentCommunity.name}</span>
            </div>
        `;
    }

    renderCommunityMembers() {
        const container = document.getElementById('membersList');
        container.innerHTML = this.communityMembers.map(member => `
            <div class="member-item ${member.is_online ? 'online' : 'offline'}">
                <div class="member-avatar">
                    ${member.name.charAt(0).toUpperCase()}
                    <div class="status-indicator ${member.is_online ? 'online' : 'offline'}"></div>
                </div>
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
        container.innerHTML = this.chatMessages.map(message => `
            <div class="chat-message">
                <div class="message-avatar">
                    ${message.user_name.charAt(0).toUpperCase()}
                </div>
                <div class="message-content">
                    <div class="message-header">
                        <span class="message-sender">${message.user_name}</span>
                        <span class="message-time">${this.formatTime(message.timestamp)}</span>
                    </div>
                    <div class="message-text">${message.content}</div>
                </div>
            </div>
        `).join('');

        container.scrollTop = container.scrollHeight;
    }

    renderActivities() {
        const container = document.getElementById('activitiesList');
        container.innerHTML = this.activities.map(activity => `
            <div class="activity-item">
                <div class="activity-icon">
                    <i class="fas ${activity.icon}"></i>
                </div>
                <div class="activity-content">
                    <div class="activity-text">
                        <strong>${activity.user_name}</strong> ${activity.content}
                    </div>
                    <div class="activity-time">${this.formatTime(activity.timestamp)}</div>
                </div>
            </div>
        `).join('');
    }

    renderCommunityStats() {
        const container = document.getElementById('communityStats');
        const stats = this.calculateCommunityStats();

        container.innerHTML = `
            <div class="stat-item">
                <div class="stat-value">${stats.activeMembers}</div>
                <div class="stat-label">Aktif Üye</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">${stats.avgCompatibility}%</div>
                <div class="stat-label">Ort. Uyum</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">${stats.activitiesThisWeek}</div>
                <div class="stat-label">Bu Hafta</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">${stats.responseTime}h</div>
                <div class="stat-label">Yanıt Süresi</div>
            </div>
        `;
    }

    calculateCommunityStats() {
        const activeMembers = this.communityMembers.filter(m => m.is_online).length;
        const avgCompatibility = Math.round(this.currentCommunity.compatibility_score * 100);
        const activitiesThisWeek = this.activities.filter(a =>
            new Date(a.timestamp) > new Date(Date.now() - 7 * 24 * 60 * 60 * 1000)
        ).length;

        return {
            activeMembers,
            avgCompatibility,
            activitiesThisWeek,
            responseTime: 2.5
        };
    }

    setupEventListeners() {
        document.getElementById('sendMessageBtn').addEventListener('click', () => {
            this.sendMessage();
        });

        document.getElementById('messageInput').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.sendMessage();
            }
        });

        document.getElementById('leaveCommunityBtn').addEventListener('click', () => {
            this.leaveCommunity();
        });

        document.getElementById('clearChatBtn').addEventListener('click', () => {
            this.clearChat();
        });

        document.getElementById('gptAssistantBtn').addEventListener('click', () => {
            this.openAssistantModal();
        });

        document.querySelectorAll('.assistant-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const type = btn.dataset.type;
                this.handleAssistantAction(type);
            });
        });
    }

    sendMessage() {
        const input = document.getElementById('messageInput');
        const message = input.value.trim();

        if (!message) return;

        const user = JSON.parse(localStorage.getItem('friendzone_user'));
        const newMessage = {
            id: Date.now(),
            user_id: user.id,
            user_name: user.name,
            content: message,
            timestamp: new Date().toISOString(),
            type: 'message'
        };

        this.chatMessages.push(newMessage);
        this.renderChatMessages();

        input.value = '';

        setTimeout(() => {
            this.simulateResponse(message);
        }, 1000 + Math.random() * 2000);
    }

    simulateResponse(originalMessage) {
        const responses = [
            "Harika fikir! Ben de katılıyorum.",
            "Bunu daha önce hiç düşünmemiştim, ilginç.",
            "Bu konuda biraz daha detay verebilir misin?",
            "Evet kesinlikle! Hadi bunu birlikte geliştirelim.",
            "Bu hafta sonu için plan yapabiliriz."
        ];

        const randomUser = this.communityMembers[Math.floor(Math.random() * this.communityMembers.length)];
        const response = {
            id: Date.now(),
            user_id: randomUser.id,
            user_name: randomUser.name,
            content: responses[Math.floor(Math.random() * responses.length)],
            timestamp: new Date().toISOString(),
            type: 'message'
        };

        this.chatMessages.push(response);
        this.renderChatMessages();
    }

    async leaveCommunity() {
        if (!confirm('Bu topluluktan ayrılmak istediğinizden emin misiniz?')) {
            return;
        }

        try {
            const user = JSON.parse(localStorage.getItem('friendzone_user'));
            const response = await fetch('/api/community/leave', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('friendzone_token')}`
                },
                body: JSON.stringify({
                    user_id: user.id,
                    community_id: this.currentCommunity.id
                })
            });

            const result = await response.json();

            if (response.ok) {
                this.showSuccess('Topluluktan ayrıldınız');
                setTimeout(() => {
                    window.location.href = 'communities.html';
                }, 1500);
            } else {
                throw new Error(result.message || 'Topluluktan ayrılamadı');
            }

        } catch (error) {
            console.error('Topluluktan ayrılma hatası:', error);
            this.showError('Topluluktan ayrılırken bir hata oluştu: ' + error.message);
        }
    }

    clearChat() {
        if (!confirm('Tüm sohbet geçmişini temizlemek istediğinizden emin misiniz?')) {
            return;
        }

        this.chatMessages = [];
        this.renderChatMessages();
        this.showSuccess('Sohbet geçmişi temizlendi');
    }

    openAssistantModal() {
        document.getElementById('assistantModal').classList.add('show');
    }

    handleAssistantAction(type) {
        if (!window.gptAssistant) {
            this.showError('AI asistanı henüz hazır değil');
            return;
        }

        const promptMap = {
            topic: 'Bu topluluk için 3 ilgi çekici sohbet konusu öner',
            icebreaker: 'Bu topluluk için 5 eğlenceli buz kırıcı soru üret',
            activity: 'Bu topluluk için 3 uygulanabilir etkinlik öner'
        };

        window.gptAssistant.getSuggestion(type, promptMap[type]);
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

    formatTime(timestamp) {
        const date = new Date(timestamp);
        const now = new Date();
        const diffMs = now - date;
        const diffMins = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMs / 3600000);
        const diffDays = Math.floor(diffMs / 86400000);

        if (diffMins < 1) return 'şimdi';
        if (diffMins < 60) return `${diffMins} dk önce`;
        if (diffHours < 24) return `${diffHours} sa önce`;
        if (diffDays < 7) return `${diffDays} gün önce`;

        return date.toLocaleDateString('tr-TR');
    }

    showFallbackCommunity() {
        this.currentCommunity = {
            id: 1,
            name: "Teknoloji Meraklıları",
            description: "Yazılım, AI ve teknoloji trendleri hakkında konuşmak isteyen öğrenciler",
            category: "technology",
            member_count: 24,
            compatibility_score: 0.92,
            max_members: 30,
            tags: ["programming", "ai", "innovation"]
        };
        this.renderCommunityData();
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
}

document.addEventListener('DOMContentLoaded', () => {
    window.communityManager = new CommunityManager();
});