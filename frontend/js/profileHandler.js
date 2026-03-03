// frontend/js/profileHandler.js

class ProfileHandler {
    constructor() {
        this.currentUser = null;
        this.isEditing = false;
        this.escapeHandler = null;
        this.init();
    }

    async init() {
        await this.loadUserData();
        this.setupEventListeners();
        this.setupFormValidation();
        this.loadProfileData();
        this.loadSimilarUsers();
        this.loadRecentActivities();
        this.loadAchievementBadges();
    }

    async loadUserData() {
        try {
            const userData = localStorage.getItem('friendzone_user');

            if (userData) {
                this.currentUser = JSON.parse(userData);
            } else {
                console.log('Kullanıcı giriş yapmamış, demo modda devam ediliyor...');
                this.currentUser = this.createDemoUser();
            }

            this.updateUserInterface();
        } catch (error) {
            console.error('Kullanıcı verisi yüklenemedi:', error);
            this.currentUser = this.createDemoUser();
            this.updateUserInterface();
        }
    }

    createDemoUser() {
        return {
            id: 999,
            name: 'Ayşe Yılmaz',
            email: 'ayse.yilmaz@universite.edu.tr',
            university: 'Boğaziçi Üniversitesi',
            department: 'Psikoloji',
            year: '3',
            bio: 'Psikoloji öğrencisiyim. Müzik dinlemeyi, kitap okumayı ve doğa yürüyüşlerini seviyorum. Yeni insanlarla tanışmaktan keyif alıyorum!',
            isDemo: true,
            join_date: new Date('2024-01-15').toISOString()
        };
    }

    updateUserInterface() {
        if (!this.currentUser) return;

        const sidebarUsername = document.getElementById('sidebarUsername');
        const sidebarAvatar = document.getElementById('sidebarAvatar');
        const profileName = document.getElementById('profileName');
        const profileAvatar = document.getElementById('profileAvatar');
        const profileEmail = document.getElementById('profileEmail');
        const profileUniversity = document.getElementById('profileUniversity');
        const profileBio = document.getElementById('profileBio');

        if (sidebarUsername) sidebarUsername.textContent = this.currentUser.name;
        if (sidebarAvatar) sidebarAvatar.textContent = this.currentUser.name.charAt(0).toUpperCase();
        if (profileName) profileName.textContent = this.currentUser.name;
        if (profileAvatar) profileAvatar.textContent = this.currentUser.name.charAt(0).toUpperCase();
        if (profileEmail) profileEmail.innerHTML = `<i class="fas fa-envelope"></i> ${this.currentUser.email}`;
        if (profileUniversity && this.currentUser.university) {
            profileUniversity.innerHTML = `<i class="fas fa-graduation-cap"></i> ${this.currentUser.university}`;
        }
        if (profileBio && this.currentUser.bio) {
            profileBio.textContent = this.currentUser.bio;
        }
    }

    async loadProfileData() {
        try {
            const response = await fetch(`/api/user/profile/${this.currentUser.id}`, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('friendzone_token')}`
                }
            });

            if (response.ok) {
                const data = await response.json();
                this.updateProfileDetails(data.profile);
            } else {
                this.showFallbackData();
            }
        } catch (error) {
            console.error('Profil verisi yüklenemedi:', error);
            this.showFallbackData();
        }
    }

    updateProfileDetails(profile) {
        const infoUniversity = document.getElementById('infoUniversity');
        const infoDepartment = document.getElementById('infoDepartment');
        const infoYear = document.getElementById('infoYear');
        const infoJoinDate = document.getElementById('infoJoinDate');

        if (infoUniversity) infoUniversity.textContent = profile.university || 'Belirtilmemiş';
        if (infoDepartment) infoDepartment.textContent = profile.department || 'Belirtilmemiş';
        if (infoYear) infoYear.textContent = this.formatYear(profile.year);
        if (infoJoinDate) infoJoinDate.textContent = this.formatDate(profile.join_date);

        const statCommunities = document.getElementById('statCommunities');
        const statFriends = document.getElementById('statFriends');
        const statActivities = document.getElementById('statActivities');
        const statCompatibility = document.getElementById('statCompatibility');

        if (statCommunities) statCommunities.textContent = profile.stats?.communities || 0;
        if (statFriends) statFriends.textContent = profile.stats?.friends || 0;
        if (statActivities) statActivities.textContent = profile.stats?.activities || 0;
        if (statCompatibility) statCompatibility.textContent = `%${profile.stats?.compatibility || 0}`;

        if (profile.personality) {
            this.updatePersonalitySection(profile.personality);
        }

        if (profile.hobbies && profile.hobbies.length > 0) {
            this.updateHobbiesSection(profile.hobbies);
        } else {
            const hobbiesEmpty = document.getElementById('hobbiesEmpty');
            if (hobbiesEmpty) hobbiesEmpty.style.display = 'block';
        }

        if (profile.communities && profile.communities.length > 0) {
            this.updateCommunitiesSection(profile.communities);
        } else {
            const communitiesEmpty = document.getElementById('communitiesEmpty');
            if (communitiesEmpty) communitiesEmpty.style.display = 'block';
        }
    }

    updatePersonalitySection(personality) {
        const personalityType = document.getElementById('personalityType');
        const personalityScore = document.getElementById('personalityScore');
        const personalityTraits = document.getElementById('personalityTraits');
        const personalityDescription = document.getElementById('personalityDescription');

        if (personalityType) {
            personalityType.innerHTML = `<i class="fas fa-award"></i> <span>${personality.type}</span>`;
        }
        if (personalityScore) personalityScore.textContent = `%${personality.accuracy || 0}`;

        if (personalityTraits) {
            personalityTraits.innerHTML = personality.traits.map(trait => `
                <div class="trait-item">
                    <div class="trait-name">${trait.name}</div>
                    <div class="trait-value">${trait.value}/10</div>
                </div>
            `).join('');
        }

        if (personalityDescription) {
            personalityDescription.textContent = personality.description || 'Kişilik testi henüz tamamlanmamış.';
        }
    }

    updateHobbiesSection(hobbies) {
        const hobbiesGrid = document.getElementById('hobbiesGrid');
        if (!hobbiesGrid) return;

        hobbiesGrid.innerHTML = hobbies.map(hobby => `
            <div class="hobby-item">
                <div class="hobby-icon">
                    <i class="fas ${this.getHobbyIcon(hobby.category)}"></i>
                </div>
                <div class="hobby-name">${hobby.name}</div>
            </div>
        `).join('');

        const hobbiesEmpty = document.getElementById('hobbiesEmpty');
        if (hobbiesEmpty) hobbiesEmpty.style.display = 'none';
    }

    updateCommunitiesSection(communities) {
        const communitiesList = document.getElementById('profileCommunities');
        if (!communitiesList) return;

        communitiesList.innerHTML = communities.map(community => `
            <div class="community-item" data-community-id="${community.id}">
                <div class="community-icon">
                    <i class="fas ${this.getCategoryIcon(community.category)}"></i>
                </div>
                <div class="community-info">
                    <div class="community-name">${community.name}</div>
                    <div class="community-meta">
                        <span>${community.member_count} üye</span>
                        <span>%${Math.round(community.compatibility * 100)} uyum</span>
                    </div>
                </div>
            </div>
        `).join('');

        const communitiesEmpty = document.getElementById('communitiesEmpty');
        if (communitiesEmpty) communitiesEmpty.style.display = 'none';
    }

    async loadSimilarUsers() {
        try {
            const response = await fetch(`/api/user/similar/${this.currentUser.id}`, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('friendzone_token')}`
                }
            });

            if (response.ok) {
                const data = await response.json();
                this.renderSimilarUsers(data.similar_users);
            }
        } catch (error) {
            console.error('Benzer kullanıcılar yüklenemedi:', error);
            this.renderSimilarUsers(this.generateSampleSimilarUsers());
        }
    }

    renderSimilarUsers(users) {
        const container = document.getElementById('similarUsersList');
        if (!container) return;

        if (!users || users.length === 0) {
            container.innerHTML = `
                <div class="empty-state" style="padding: 20px;">
                    <p>Henüz benzer kullanıcı bulunamadı</p>
                </div>
            `;
            return;
        }

        container.innerHTML = users.map(user => `
            <div class="similar-user">
                <div class="user-avatar-small">${(user.name || '?').charAt(0).toUpperCase()}</div>
                <div class="user-info-small">
                    <div class="user-name-small">${user.name}</div>
                    <div class="user-meta">%${Math.round(user.similarity * 100)} uyum</div>
                </div>
            </div>
        `).join('');
    }

    async loadRecentActivities() {
        try {
            const response = await fetch(`/api/user/activities/${this.currentUser.id}`, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('friendzone_token')}`
                }
            });

            if (response.ok) {
                const data = await response.json();
                this.renderRecentActivities(data.activities);
            }
        } catch (error) {
            console.error('Son aktiviteler yüklenemedi:', error);
            this.renderRecentActivities(this.generateSampleActivities());
        }
    }

    renderRecentActivities(activities) {
        const container = document.getElementById('recentActivityList');
        if (!container) return;

        if (!activities || activities.length === 0) {
            container.innerHTML = `
                <div class="empty-state" style="padding: 20px;">
                    <p>Henüz aktivite yok</p>
                </div>
            `;
            return;
        }

        container.innerHTML = activities.map(activity => `
            <div class="activity-item-small">
                <div class="activity-icon-small">
                    <i class="fas ${activity.icon}"></i>
                </div>
                <div class="activity-content-small">
                    <div class="activity-text-small">${activity.text}</div>
                    <div class="activity-time">${this.formatTime(activity.timestamp)}</div>
                </div>
            </div>
        `).join('');
    }

    async loadAchievementBadges() {
        try {
            const response = await fetch(`/api/user/badges/${this.currentUser.id}`, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('friendzone_token')}`
                }
            });

            if (response.ok) {
                const data = await response.json();
                this.renderAchievementBadges(data.badges);
            }
        } catch (error) {
            console.error('Rozetler yüklenemedi:', error);
            this.renderAchievementBadges(this.generateSampleBadges());
        }
    }

    renderAchievementBadges(badges) {
        const container = document.getElementById('achievementBadges');
        if (!container) return;

        container.innerHTML = badges.map(badge => `
            <div class="badge-item ${badge.unlocked ? '' : 'locked'}" title="${badge.description}">
                <div class="badge-icon ${badge.unlocked ? '' : 'locked'}">
                    <i class="fas ${badge.icon}"></i>
                </div>
                <div class="badge-name">${badge.name}</div>
                <div class="badge-desc">${badge.unlocked ? 'Kazanıldı' : 'Kilitli'}</div>
            </div>
        `).join('');
    }

    setupEventListeners() {
        document.querySelectorAll('.nav-item[data-section]').forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                this.switchSection(item.dataset.section);
            });
        });

        const editProfileBtn = document.getElementById('editProfileBtn');
        if (editProfileBtn) {
            editProfileBtn.addEventListener('click', () => this.openEditModal());
        }

        const editAvatarBtn = document.getElementById('editAvatarBtn');
        if (editAvatarBtn) {
            editAvatarBtn.addEventListener('click', () => this.handleAvatarEdit());
        }

        const closeEditModalBtn = document.getElementById('closeEditModalBtn');
        if (closeEditModalBtn) {
            closeEditModalBtn.addEventListener('click', () => this.closeEditModal());
        }

        const cancelEditBtn = document.getElementById('cancelEditBtn');
        if (cancelEditBtn) {
            cancelEditBtn.addEventListener('click', () => this.closeEditModal());
        }

        const editProfileForm = document.getElementById('editProfileForm');
        if (editProfileForm) {
            editProfileForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleProfileUpdate();
            });
        }

        const shareProfileBtn = document.getElementById('shareProfileBtn');
        if (shareProfileBtn) {
            shareProfileBtn.addEventListener('click', () => this.shareProfile());
        }

        const retakeTestBtn = document.getElementById('retakeTestBtn');
        if (retakeTestBtn) {
            retakeTestBtn.addEventListener('click', () => this.retakePersonalityTest());
        }

        const editHobbiesBtn = document.getElementById('editHobbiesBtn');
        if (editHobbiesBtn) {
            editHobbiesBtn.addEventListener('click', () => {
                window.location.href = 'hobbies.html';
            });
        }

        document.addEventListener('click', (e) => {
            const communityItem = e.target.closest('.community-item');
            if (communityItem) {
                const communityId = communityItem.dataset.communityId;
                window.location.href = `community.html?id=${communityId}`;
            }
        });
    }

    switchSection(sectionId) {
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active');
        });
        const activeNav = document.querySelector(`[data-section="${sectionId}"]`);
        if (activeNav) activeNav.classList.add('active');

        document.querySelectorAll('.profile-section').forEach(section => {
            section.classList.remove('active');
        });
        const activeSection = document.getElementById(`${sectionId}Section`);
        if (activeSection) activeSection.classList.add('active');
    }

    openEditModal() {
        const modal = document.getElementById('editProfileModal');
        const form = document.getElementById('editProfileForm');
        if (!modal || !form) return;

        form.reset();

        const editName = document.getElementById('editName');
        const editBio = document.getElementById('editBio');
        const editUniversity = document.getElementById('editUniversity');
        const editDepartment = document.getElementById('editDepartment');
        const editYear = document.getElementById('editYear');

        if (editName) editName.value = this.currentUser.name || '';
        if (editBio) editBio.value = this.currentUser.bio || '';
        if (editUniversity) editUniversity.value = this.currentUser.university || '';
        if (editDepartment) editDepartment.value = this.currentUser.department || '';
        if (editYear) editYear.value = this.currentUser.year || '';

        this.populateUniversityOptions();

        modal.style.display = 'flex';
        setTimeout(() => {
            modal.classList.add('show');
            if (editName) editName.focus();
        }, 10);

        this.escapeHandler = (e) => {
            if (e.key === 'Escape') this.closeEditModal();
        };
        document.addEventListener('keydown', this.escapeHandler);
    }

    closeEditModal() {
        const modal = document.getElementById('editProfileModal');
        if (!modal) return;

        modal.classList.remove('show');

        if (this.escapeHandler) {
            document.removeEventListener('keydown', this.escapeHandler);
            this.escapeHandler = null;
        }

        setTimeout(() => {
            modal.style.display = 'none';
            this.clearFormValidation();
        }, 300);
    }

    populateUniversityOptions() {
        const universitySelect = document.getElementById('editUniversity');
        if (!universitySelect) return;

        const universities = [
            'İstanbul Teknik Üniversitesi',
            'Orta Doğu Teknik Üniversitesi',
            'Boğaziçi Üniversitesi',
            'İstanbul Üniversitesi',
            'Ankara Üniversitesi',
            'Hacettepe Üniversitesi',
            'Yıldız Teknik Üniversitesi',
            'Marmara Üniversitesi',
            'Ege Üniversitesi',
            'Dokuz Eylül Üniversitesi',
            'Akdeniz Üniversitesi',
            'Anadolu Üniversitesi'
        ];

        while (universitySelect.options.length > 1) {
            universitySelect.remove(1);
        }

        universities.forEach(university => {
            const option = document.createElement('option');
            option.value = university;
            option.textContent = university;
            universitySelect.appendChild(option);
        });
    }

    async handleProfileUpdate() {
        const form = document.getElementById('editProfileForm');
        if (!form) return;

        const formData = new FormData(form);
        const data = {
            name: formData.get('name'),
            bio: formData.get('bio'),
            university: formData.get('university'),
            department: formData.get('department'),
            year: formData.get('year')
        };

        const submitBtn = form.querySelector('button[type="submit"]');
        this.setLoadingState(submitBtn, true);

        try {
            const response = await fetch('/api/user/profile/update', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('friendzone_token')}`
                },
                body: JSON.stringify(data)
            });

            if (response.ok) {
                const result = await response.json();

                this.currentUser = { ...this.currentUser, ...data };
                localStorage.setItem('friendzone_user', JSON.stringify(this.currentUser));

                this.updateUserInterface();
                this.closeEditModal();
                this.showSuccess('Profil başarıyla güncellendi!');
            } else {
                throw new Error('Profil güncellenemedi');
            }
        } catch (error) {
            console.error('Profil güncelleme hatası:', error);
            this.showError('Profil güncellenirken bir hata oluştu: ' + error.message);
        } finally {
            this.setLoadingState(submitBtn, false);
        }
    }

    async handleAvatarEdit() {
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = 'image/*';

        input.onchange = async (e) => {
            const file = e.target.files[0];
            if (file) {
                await this.uploadAvatar(file);
            }
        };

        input.click();
    }

    async uploadAvatar(file) {
        const formData = new FormData();
        formData.append('avatar', file);

        try {
            const response = await fetch('/api/user/avatar/upload', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('friendzone_token')}`
                },
                body: formData
            });

            if (response.ok) {
                this.showSuccess('Profil fotoğrafı başarıyla güncellendi!');
            } else {
                throw new Error('Avatar yüklenemedi');
            }
        } catch (error) {
            console.error('Avatar yükleme hatası:', error);
            this.showError('Profil fotoğrafı yüklenirken bir hata oluştu');
        }
    }

    async shareProfile() {
        const profileUrl = `${window.location.origin}/profile.html?user=${this.currentUser.id}`;

        if (navigator.share) {
            try {
                await navigator.share({
                    title: `${this.currentUser.name} - FriendZone Profili`,
                    text: `${this.currentUser.name} adlı kullanıcının FriendZone profilini görüntüle`,
                    url: profileUrl
                });
            } catch (error) {
                console.log('Paylaşım iptal edildi');
            }
        } else {
            try {
                await navigator.clipboard.writeText(profileUrl);
                this.showSuccess('Profil linki panoya kopyalandı!');
            } catch (error) {
                const textArea = document.createElement('textarea');
                textArea.value = profileUrl;
                document.body.appendChild(textArea);
                textArea.select();
                document.execCommand('copy');
                document.body.removeChild(textArea);
                this.showSuccess('Profil linki panoya kopyalandı!');
            }
        }
    }

    async retakePersonalityTest() {
        if (confirm('Kişilik testini yeniden almak istediğinizden emin misiniz?')) {
            window.location.href = 'personality_test.html?retake=true';
        }
    }

    showFallbackData() {
        const fallbackData = {
            university: 'Örnek Üniversite',
            department: 'Bilgisayar Mühendisliği',
            year: '3',
            join_date: new Date().toISOString(),
            stats: {
                communities: 2,
                friends: 15,
                activities: 8,
                compatibility: 87
            },
            personality: {
                type: 'Analitik Düşünür',
                accuracy: 92,
                traits: [
                    { name: 'Dışadönüklük', value: 7 },
                    { name: 'Uyumluluk', value: 8 },
                    { name: 'Sorumluluk', value: 9 },
                    { name: 'Duygusal Denge', value: 6 },
                    { name: 'Açıklık', value: 8 }
                ],
                description: 'Analitik düşünme yeteneğiniz yüksek.'
            },
            hobbies: [
                { name: 'Kodlama', category: 'technology' },
                { name: 'Fitness', category: 'sports' },
                { name: 'Müzik', category: 'music' }
            ],
            communities: [
                { id: 1, name: 'Teknoloji Meraklıları', category: 'technology', member_count: 24, compatibility: 0.92 },
                { id: 2, name: 'Spor ve Sağlık', category: 'sports', member_count: 18, compatibility: 0.85 }
            ]
        };

        this.updateProfileDetails(fallbackData);
    }

    generateSampleSimilarUsers() {
        return [
            { name: 'Ayşe Demir', similarity: 0.89, university: 'Boğaziçi Üniversitesi' },
            { name: 'Mehmet Kaya', similarity: 0.85, university: 'ODTÜ' },
            { name: 'Zeynep Şahin', similarity: 0.82, university: 'Hacettepe Üniversitesi' }
        ];
    }

    generateSampleActivities() {
        return [
            { text: 'Teknoloji Meraklıları topluluğuna katıldın', icon: 'fa-user-plus', timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString() },
            { text: 'Kişilik testini tamamladın', icon: 'fa-brain', timestamp: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString() },
            { text: 'Hobi testini güncelledin', icon: 'fa-heart', timestamp: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString() }
        ];
    }

    generateSampleBadges() {
        return [
            { name: 'İlk Adım', icon: 'fa-star', description: 'İlk giriş yapma', unlocked: true },
            { name: 'Test Uzmanı', icon: 'fa-brain', description: 'Tüm testleri tamamlama', unlocked: true },
            { name: 'Sosyal Kelebek', icon: 'fa-users', description: '5 topluluğa katılma', unlocked: false },
            { name: 'Uyum Ustası', icon: 'fa-heart', description: '%90 üzeri uyum oranı', unlocked: true }
        ];
    }

    formatYear(year) {
        const years = { '1': '1. Sınıf', '2': '2. Sınıf', '3': '3. Sınıf', '4': '4. Sınıf', '5': 'Lisansüstü' };
        return years[year] || 'Belirtilmemiş';
    }

    formatDate(dateString) {
        if (!dateString) return 'Belirtilmemiş';
        const date = new Date(dateString);
        return date.toLocaleDateString('tr-TR');
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

    getHobbyIcon(category) {
        const icons = { 'sports': 'fa-running', 'arts': 'fa-palette', 'technology': 'fa-laptop-code', 'music': 'fa-music' };
        return icons[category] || 'fa-heart';
    }

    getCategoryIcon(category) {
        const icons = { 'technology': 'fa-laptop-code', 'sports': 'fa-running', 'arts': 'fa-palette', 'outdoor': 'fa-mountain', 'education': 'fa-graduation-cap', 'social': 'fa-users' };
        return icons[category] || 'fa-users';
    }

    setLoadingState(button, isLoading) {
        if (isLoading) {
            button.classList.add('btn-loading');
            button.disabled = true;
            button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> İşleniyor...';
        } else {
            button.classList.remove('btn-loading');
            button.disabled = false;
            button.innerHTML = '<i class="fas fa-save"></i> Değişiklikleri Kaydet';
        }
    }

    setupFormValidation() { }

    clearFormValidation() { }

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
}

// Initialize profile handler
document.addEventListener('DOMContentLoaded', () => {
    window.profileHandler = new ProfileHandler();
});