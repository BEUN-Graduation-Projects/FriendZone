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
            // Kullanıcı giriş yapmamışsa demo kullanıcı oluştur
            console.log('Kullanıcı giriş yapmamış, demo modda devam ediliyor...');
            this.currentUser = this.createDemoUser();
        }

        this.updateUserInterface();

    } catch (error) {
        console.error('Kullanıcı verisi yüklenemedi:', error);
        // Hata durumunda da demo kullanıcı ile devam et
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

        // Update sidebar
        document.getElementById('sidebarUsername').textContent = this.currentUser.name;
        document.getElementById('sidebarAvatar').textContent = this.currentUser.name.charAt(0).toUpperCase();

        // Update profile header
        document.getElementById('profileName').textContent = this.currentUser.name;
        document.getElementById('profileAvatar').textContent = this.currentUser.name.charAt(0).toUpperCase();
        document.getElementById('profileEmail').innerHTML = `<i class="fas fa-envelope"></i>${this.currentUser.email}`;
        
        if (this.currentUser.university) {
            document.getElementById('profileUniversity').innerHTML = `<i class="fas fa-graduation-cap"></i>${this.currentUser.university}`;
        }
        
        if (this.currentUser.bio) {
            document.getElementById('profileBio').textContent = this.currentUser.bio;
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
        // Personal Information
        document.getElementById('infoUniversity').textContent = profile.university || 'Belirtilmemiş';
        document.getElementById('infoDepartment').textContent = profile.department || 'Belirtilmemiş';
        document.getElementById('infoYear').textContent = this.formatYear(profile.year);
        document.getElementById('infoJoinDate').textContent = this.formatDate(profile.join_date);

        // Stats
        document.getElementById('statCommunities').textContent = profile.stats?.communities || 0;
        document.getElementById('statFriends').textContent = profile.stats?.friends || 0;
        document.getElementById('statActivities').textContent = profile.stats?.activities || 0;
        document.getElementById('statCompatibility').textContent = `%${profile.stats?.compatibility || 0}`;

        // Personality Profile
        if (profile.personality) {
            this.updatePersonalitySection(profile.personality);
        }

        // Hobbies
        if (profile.hobbies && profile.hobbies.length > 0) {
            this.updateHobbiesSection(profile.hobbies);
        } else {
            document.getElementById('hobbiesEmpty').style.display = 'block';
        }

        // Communities
        if (profile.communities && profile.communities.length > 0) {
            this.updateCommunitiesSection(profile.communities);
        } else {
            document.getElementById('communitiesEmpty').style.display = 'block';
        }
    }

    updatePersonalitySection(personality) {
        document.getElementById('personalityType').innerHTML = `
            <i class="fas fa-award"></i>
            <span>${personality.type}</span>
        `;
        document.getElementById('personalityScore').textContent = `%${personality.accuracy || 0}`;

        // Traits
        const traitsContainer = document.getElementById('personalityTraits');
        traitsContainer.innerHTML = personality.traits.map(trait => `
            <div class="trait-item">
                <div class="trait-name">${trait.name}</div>
                <div class="trait-value">${trait.value}/10</div>
            </div>
        `).join('');

        // Description
        document.getElementById('personalityDescription').textContent = personality.description;
    }

    updateHobbiesSection(hobbies) {
        const hobbiesGrid = document.getElementById('hobbiesGrid');
        hobbiesGrid.innerHTML = hobbies.map(hobby => `
            <div class="hobby-item">
                <div class="hobby-icon">
                    <i class="fas ${this.getHobbyIcon(hobby.category)}"></i>
                </div>
                <div class="hobby-name">${hobby.name}</div>
            </div>
        `).join('');

        document.getElementById('hobbiesEmpty').style.display = 'none';
    }

    updateCommunitiesSection(communities) {
        const communitiesList = document.getElementById('profileCommunities');
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

        document.getElementById('communitiesEmpty').style.display = 'none';
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
                <div class="user-avatar-small">${user.name.charAt(0).toUpperCase()}</div>
                <div class="user-info-small">
                    <div class="user-name-small">${user.name}</div>
                    <div class="user-meta">%${Math.round(user.similarity * 100)} uyum • ${user.university}</div>
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
        // Navigation
        document.querySelectorAll('.nav-item[data-section]').forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                this.switchSection(item.dataset.section);
            });
        });

        // Edit Profile
        document.getElementById('editProfileBtn').addEventListener('click', () => {
            this.openEditModal();
        });

        document.getElementById('editAvatarBtn').addEventListener('click', () => {
            this.handleAvatarEdit();
        });

        // Edit Profile Modal
        document.getElementById('closeEditModalBtn').addEventListener('click', () => {
            this.closeEditModal();
        });

        document.getElementById('cancelEditBtn').addEventListener('click', () => {
            this.closeEditModal();
        });

        document.getElementById('editProfileForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleProfileUpdate();
        });

        // Share Profile
        document.getElementById('shareProfileBtn').addEventListener('click', () => {
            this.shareProfile();
        });

        // Retake Test
        document.getElementById('retakeTestBtn').addEventListener('click', () => {
            this.retakePersonalityTest();
        });

        // Edit Hobbies
        document.getElementById('editHobbiesBtn').addEventListener('click', () => {
            window.location.href = 'hobbies.html';
        });

        // Settings
        document.getElementById('saveSettingsBtn').addEventListener('click', () => {
            this.saveSettings();
        });

        document.getElementById('resetSettingsBtn').addEventListener('click', () => {
            this.resetSettings();
        });

        document.getElementById('deleteAccountBtn').addEventListener('click', () => {
            this.deleteAccount();
        });

        document.getElementById('exportDataBtn').addEventListener('click', () => {
            this.exportData();
        });

        // Community clicks
        document.addEventListener('click', (e) => {
            const communityItem = e.target.closest('.community-item');
            if (communityItem) {
                const communityId = communityItem.dataset.communityId;
                window.location.href = `community.html?id=${communityId}`;
            }
        });

        // Bio character count
        const bioTextarea = document.getElementById('editBio');
        if (bioTextarea) {
            bioTextarea.addEventListener('input', () => {
                this.updateCharCount(bioTextarea, 'bioCharCount', 200);
            });
        }
    }

    setupFormValidation() {
        const form = document.getElementById('editProfileForm');
        
        form.addEventListener('submit', (e) => {
            if (!this.validateForm()) {
                e.preventDefault();
                return false;
            }
        });

        // Real-time validation
        form.querySelectorAll('input, select, textarea').forEach(input => {
            input.addEventListener('blur', () => {
                this.validateField(input);
            });
            
            input.addEventListener('input', () => {
                // Hata mesajını temizle ama border rengini koru
                const errorElement = input.parentNode.querySelector('.form-error');
                if (errorElement && input.value.trim()) {
                    errorElement.style.display = 'none';
                }
            });
        });
    }

    switchSection(sectionId) {
        // Update navigation
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active');
        });
        document.querySelector(`[data-section="${sectionId}"]`).classList.add('active');

        // Update sections
        document.querySelectorAll('.profile-section').forEach(section => {
            section.classList.remove('active');
        });
        document.getElementById(`${sectionId}Section`).classList.add('active');
    }

    openEditModal() {
        const modal = document.getElementById('editProfileModal');
        const form = document.getElementById('editProfileForm');

        // Formu temizle
        form.reset();

        // Mevcut verilerle doldur
        document.getElementById('editName').value = this.currentUser.name || '';
        document.getElementById('editBio').value = this.currentUser.bio || '';
        document.getElementById('editUniversity').value = this.currentUser.university || '';
        document.getElementById('editDepartment').value = this.currentUser.department || '';
        document.getElementById('editYear').value = this.currentUser.year || '';

        // Karakter sayısını güncelle
        this.updateCharCount(document.getElementById('editBio'), 'bioCharCount', 200);

        // Üniversite seçeneklerini doldur
        this.populateUniversityOptions();

        modal.style.display = 'flex';
        setTimeout(() => {
            modal.classList.add('show');
            // İlk inputa focus
            document.getElementById('editName').focus();
        }, 10);

        // ESC tuşu ile kapatma
        this.escapeHandler = (e) => {
            if (e.key === 'Escape') {
                this.closeEditModal();
            }
        };
        document.addEventListener('keydown', this.escapeHandler);
    }

    closeEditModal() {
        const modal = document.getElementById('editProfileModal');
        modal.classList.remove('show');
        
        // ESC tuşu listener'ını temizle
        if (this.escapeHandler) {
            document.removeEventListener('keydown', this.escapeHandler);
            this.escapeHandler = null;
        }
        
        setTimeout(() => {
            modal.style.display = 'none';
            // Form validation state'ini temizle
            this.clearFormValidation();
        }, 300);
    }

    populateUniversityOptions() {
        const universitySelect = document.getElementById('editUniversity');
        
        // Örnek üniversite listesi
        const universities = [
            'İstanbul Teknik Üniversitesi',
            'Orta Doğu Teknik Üniversitesi',
            'Boğaziçi Üniversitesi',
            'İstanbul Üniversitesi',
            'Ankara Üniversitesi',
            'Hacettepe Üniversitesi',
            'Ege Üniversitesi',
            'Gazi Üniversitesi',
            'Marmara Üniversitesi',
            'Yıldız Teknik Üniversitesi',
            'Dokuz Eylül Üniversitesi',
            'Akdeniz Üniversitesi',
            'Anadolu Üniversitesi',
            'Selçuk Üniversitesi',
            'Erciyes Üniversitesi'
        ];

        // Mevcut seçenekleri temizle (ilk option hariç)
        while (universitySelect.options.length > 1) {
            universitySelect.remove(1);
        }

        // Üniversiteleri ekle
        universities.forEach(university => {
            const option = document.createElement('option');
            option.value = university;
            option.textContent = university;
            universitySelect.appendChild(option);
        });
    }

    async handleProfileUpdate() {
        const form = document.getElementById('editProfileForm');
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
                
                // Update local storage
                this.currentUser = { ...this.currentUser, ...data };
                localStorage.setItem('friendzone_user', JSON.stringify(this.currentUser));
                
                // Update UI
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
                const result = await response.json();
                this.showSuccess('Profil fotoğrafı başarıyla güncellendi!');
                // Avatar would be updated via the updated user data
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
            // Fallback: copy to clipboard
            try {
                await navigator.clipboard.writeText(profileUrl);
                this.showSuccess('Profil linki panoya kopyalandı!');
            } catch (error) {
                // Fallback for older browsers
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
        if (confirm('Kişilik testini yeniden almak istediğinizden emin misiniz? Mevcut sonuçlarınız güncellenecektir.')) {
            window.location.href = 'personality_test.html?retake=true';
        }
    }

    async saveSettings() {
        const visibility = document.querySelector('input[name="visibility"]:checked').value;
        const notifications = {
            community: document.getElementById('notifCommunity').checked,
            messages: document.getElementById('notifMessages').checked,
            recommendations: document.getElementById('notifRecommendations').checked
        };

        try {
            const response = await fetch('/api/user/settings/update', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('friendzone_token')}`
                },
                body: JSON.stringify({
                    visibility,
                    notifications
                })
            });

            if (response.ok) {
                this.showSuccess('Ayarlar başarıyla kaydedildi!');
            } else {
                throw new Error('Ayarlar kaydedilemedi');
            }
        } catch (error) {
            console.error('Ayarlar kaydetme hatası:', error);
            this.showError('Ayarlar kaydedilirken bir hata oluştu');
        }
    }

    resetSettings() {
        if (confirm('Tüm ayarları varsayılan değerlere sıfırlamak istediğinizden emin misiniz?')) {
            document.querySelector('input[name="visibility"][value="public"]').checked = true;
            document.getElementById('notifCommunity').checked = true;
            document.getElementById('notifMessages').checked = true;
            document.getElementById('notifRecommendations').checked = false;
            this.showSuccess('Ayarlar varsayılan değerlere sıfırlandı');
        }
    }

    async deleteAccount() {
        if (confirm('HESABINIZI SİLMEK ÜZERESİNİZ! Bu işlem geri alınamaz. Tüm verileriniz kalıcı olarak silinecektir. Emin misiniz?')) {
            const confirmation = prompt('Lütfen emin olduğunuzu doğrulamak için "SİL" yazın:');
            if (confirmation === 'SİL') {
                try {
                    const response = await fetch('/api/user/delete', {
                        method: 'DELETE',
                        headers: {
                            'Authorization': `Bearer ${localStorage.getItem('friendzone_token')}`
                        }
                    });

                    if (response.ok) {
                        localStorage.removeItem('friendzone_user');
                        localStorage.removeItem('friendzone_token');
                        this.showSuccess('Hesabınız başarıyla silindi');
                        setTimeout(() => {
                            window.location.href = 'index.html';
                        }, 2000);
                    } else {
                        throw new Error('Hesap silinemedi');
                    }
                } catch (error) {
                    console.error('Hesap silme hatası:', error);
                    this.showError('Hesap silinirken bir hata oluştu');
                }
            }
        }
    }

    async exportData() {
        try {
            const response = await fetch('/api/user/data/export', {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('friendzone_token')}`
                }
            });

            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `friendzone-data-${this.currentUser.id}.json`;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
                this.showSuccess('Verileriniz indiriliyor...');
            } else {
                throw new Error('Veri indirilemedi');
            }
        } catch (error) {
            console.error('Veri indirme hatası:', error);
            this.showError('Veriler indirilirken bir hata oluştu');
        }
    }

    // Form Validation Methods
    validateForm() {
        const form = document.getElementById('editProfileForm');
        const inputs = form.querySelectorAll('input[required], select[required]');
        let isValid = true;

        inputs.forEach(input => {
            if (!this.validateField(input)) {
                isValid = false;
            }
        });

        return isValid;
    }

    validateField(field) {
        const value = field.value.trim();
        let isValid = true;
        let errorMessage = '';

        // Required validation
        if (field.hasAttribute('required') && !value) {
            isValid = false;
            errorMessage = 'Bu alan zorunludur';
        }

        // Email validation
        if (field.type === 'email' && value) {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(value)) {
                isValid = false;
                errorMessage = 'Geçerli bir e-posta adresi girin';
            }
        }

        // Name validation
        if (field.id === 'editName' && value) {
            if (value.length < 2) {
                isValid = false;
                errorMessage = 'İsim en az 2 karakter olmalıdır';
            }
        }

        // Update field state
        if (!isValid) {
            field.classList.add('error');
            this.showFieldError(field, errorMessage);
        } else {
            field.classList.remove('error');
            this.hideFieldError(field);
        }

        return isValid;
    }

    showFieldError(field, message) {
        let errorElement = field.parentNode.querySelector('.form-error');
        
        if (!errorElement) {
            errorElement = document.createElement('div');
            errorElement.className = 'form-error';
            field.parentNode.appendChild(errorElement);
        }
        
        errorElement.textContent = message;
        errorElement.style.display = 'block';
    }

    hideFieldError(field) {
        const errorElement = field.parentNode.querySelector('.form-error');
        if (errorElement) {
            errorElement.style.display = 'none';
        }
    }

    clearFormValidation() {
        const form = document.getElementById('editProfileForm');
        const inputs = form.querySelectorAll('input, select, textarea');
        
        inputs.forEach(input => {
            input.classList.remove('error');
            const errorElement = input.parentNode.querySelector('.form-error');
            if (errorElement) {
                errorElement.style.display = 'none';
            }
        });
    }

    updateCharCount(textarea, countElementId, maxLength) {
        const countElement = document.getElementById(countElementId);
        if (countElement && textarea) {
            const currentLength = textarea.value.length;
            countElement.textContent = currentLength;
            
            if (currentLength > maxLength * 0.8) {
                countElement.style.color = 'var(--accent-warning)';
            } else {
                countElement.style.color = 'var(--text-muted)';
            }
        }
    }

    // Utility Methods
    formatYear(year) {
        const years = {
            '1': '1. Sınıf',
            '2': '2. Sınıf',
            '3': '3. Sınıf',
            '4': '4. Sınıf',
            '5': 'Lisansüstü'
        };
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
        const icons = {
            'sports': 'fa-running',
            'arts': 'fa-palette',
            'music': 'fa-music',
            'technology': 'fa-laptop-code',
            'reading': 'fa-book',
            'gaming': 'fa-gamepad',
            'travel': 'fa-plane',
            'food': 'fa-utensils'
        };
        return icons[category] || 'fa-heart';
    }

    getCategoryIcon(category) {
        const icons = {
            'technology': 'fa-laptop-code',
            'sports': 'fa-running',
            'arts': 'fa-palette',
            'outdoor': 'fa-mountain',
            'education': 'fa-graduation-cap',
            'social': 'fa-users'
        };
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

    showSuccess(message) {
        if (window.app && window.app.showNotification) {
            window.app.showNotification(message, 'success');
        } else {
            // Basit bir success mesajı göster
            const notification = document.createElement('div');
            notification.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                background: var(--accent-success);
                color: white;
                padding: 12px 20px;
                border-radius: var(--border-radius);
                box-shadow: var(--shadow-lg);
                z-index: 10000;
                animation: slideIn 0.3s ease;
            `;
            notification.textContent = message;
            document.body.appendChild(notification);
            
            setTimeout(() => {
                notification.remove();
            }, 3000);
        }
    }

    showError(message) {
        if (window.app && window.app.showNotification) {
            window.app.showNotification(message, 'error');
        } else {
            alert('Hata: ' + message);
        }
    }

    // Fallback and Sample Data Methods
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
                description: 'Analitik düşünme yeteneğiniz yüksek. Problem çözmede başarılısınız ve detaylara önem veriyorsunuz. Takım çalışmasında etkili bir rol oynuyorsunuz.'
            },
            hobbies: [
                { name: 'Kodlama', category: 'technology' },
                { name: 'Fitness', category: 'sports' },
                { name: 'Müzik', category: 'music' },
                { name: 'Okuma', category: 'reading' }
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
            { name: 'Zeynep Şahin', similarity: 0.82, university: 'Hacettepe Üniversitesi' },
            { name: 'Can Öztürk', similarity: 0.78, university: 'İTÜ' }
        ];
    }

    generateSampleActivities() {
        return [
            { text: 'Teknoloji Meraklıları topluluğuna katıldın', icon: 'fa-user-plus', timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString() },
            { text: 'Kişilik testini tamamladın', icon: 'fa-brain', timestamp: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString() },
            { text: 'Hobi testini güncelledin', icon: 'fa-heart', timestamp: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString() },
            { text: 'Profil bilgilerini düzenledin', icon: 'fa-edit', timestamp: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString() }
        ];
    }

    generateSampleBadges() {
        return [
            { name: 'İlk Adım', icon: 'fa-star', description: 'İlk giriş yapma', unlocked: true },
            { name: 'Test Uzmanı', icon: 'fa-brain', description: 'Tüm testleri tamamlama', unlocked: true },
            { name: 'Sosyal Kelebek', icon: 'fa-users', description: '5 topluluğa katılma', unlocked: false },
            { name: 'Aktif Üye', icon: 'fa-comments', description: '50 mesaj gönderme', unlocked: false },
            { name: 'Uyum Ustası', icon: 'fa-heart', description: '%90 üzeri uyum oranı', unlocked: true },
            { name: 'Veteran', icon: 'fa-calendar', description: '30 gün aktif kalma', unlocked: false }
        ];
    }
}

// Initialize profile handler
document.addEventListener('DOMContentLoaded', () => {
    window.profileHandler = new ProfileHandler();
});