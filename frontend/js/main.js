// Ana JavaScript Dosyası
class FriendZoneApp {
    constructor() {
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.setupAnimations();
        this.checkAuthStatus();
    }

    setupEventListeners() {
        // Sidebar toggle
        const sidebarToggle = document.querySelector('.sidebar-toggle');
        const sidebar = document.querySelector('.sidebar');

        if (sidebarToggle && sidebar) {
            sidebarToggle.addEventListener('click', () => {
                sidebar.classList.toggle('collapsed');
            });
        }

        // Nav item active state
        const navItems = document.querySelectorAll('.nav-item');
        navItems.forEach(item => {
            item.addEventListener('click', (e) => {
                if (!item.classList.contains('active')) {
                    navItems.forEach(nav => nav.classList.remove('active'));
                    item.classList.add('active');
                }
            });
        });

        // Smooth scrolling for anchor links
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });
    }

    setupAnimations() {
        // Intersection Observer for scroll animations
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate-in');
                }
            });
        }, observerOptions);

        // Observe elements for animation
        document.querySelectorAll('.feature-card, .step').forEach(el => {
            observer.observe(el);
        });
    }

    checkAuthStatus() {
        const token = localStorage.getItem('friendzone_token');
        const userProfile = document.querySelector('.user-profile');

        if (token && userProfile) {
            // Kullanıcı giriş yapmış
            this.updateUserProfile();
        }
    }

    async updateUserProfile() {
        try {
            const token = localStorage.getItem('friendzone_token');
            const response = await fetch('/api/auth/profile', {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (response.ok) {
                const data = await response.json();
                const user = data.data.user;

                this.updateUIWithUserData(user);
            }
        } catch (error) {
            console.error('Profil bilgileri yüklenemedi:', error);
        }
    }

    updateUIWithUserData(user) {
        // Avatar güncelle
        const avatar = document.querySelector('.avatar');
        if (avatar && user.name) {
            const initials = user.name.split(' ').map(n => n[0]).join('').toUpperCase();
            avatar.textContent = initials;
        }

        // Kullanıcı bilgilerini güncelle
        const username = document.querySelector('.username');
        const status = document.querySelector('.status');

        if (username) username.textContent = user.name;
        if (status) status.textContent = `@${user.email.split('@')[0]}`;

        // Nav items güncelle
        this.updateNavigationForLoggedInUser();
    }

    updateNavigationForLoggedInUser() {
        const navSection = document.querySelector('.nav-section:nth-child(2)');
        if (navSection) {
            navSection.innerHTML = `
                <h3>PROFİL</h3>
                <a href="profile.html" class="nav-item">
                    <i class="fas fa-user"></i>
                    <span>Profilim</span>
                </a>
                <a href="communities.html" class="nav-item">
                    <i class="fas fa-users"></i>
                    <span>Topluluklarım</span>
                </a>
                <a href="#" class="nav-item" id="logout-btn">
                    <i class="fas fa-sign-out-alt"></i>
                    <span>Çıkış Yap</span>
                </a>
            `;

            // Logout event listener ekle
            document.getElementById('logout-btn').addEventListener('click', (e) => {
                e.preventDefault();
                this.logout();
            });
        }
    }

    logout() {
        localStorage.removeItem('friendzone_token');
        localStorage.removeItem('friendzone_user');
        window.location.href = 'index.html';
    }

    // Utility functions
    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <i class="fas fa-${this.getNotificationIcon(type)}"></i>
                <span>${message}</span>
            </div>
            <button class="notification-close">
                <i class="fas fa-times"></i>
            </button>
        `;

        document.body.appendChild(notification);

        // Animasyon için
        setTimeout(() => notification.classList.add('show'), 100);

        // Kapatma butonu
        notification.querySelector('.notification-close').addEventListener('click', () => {
            notification.classList.remove('show');
            setTimeout(() => notification.remove(), 300);
        });

        // Otomatik kapanma
        setTimeout(() => {
            if (notification.parentNode) {
                notification.classList.remove('show');
                setTimeout(() => notification.remove(), 300);
            }
        }, 5000);
    }

    getNotificationIcon(type) {
        const icons = {
            success: 'check-circle',
            error: 'exclamation-circle',
            warning: 'exclamation-triangle',
            info: 'info-circle'
        };
        return icons[type] || 'info-circle';
    }

    // API helper
    async apiCall(endpoint, options = {}) {
        const token = localStorage.getItem('friendzone_token');
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
                ...(token && { 'Authorization': `Bearer ${token}` })
            }
        };

        try {
            const response = await fetch(endpoint, { ...defaultOptions, ...options });
            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.message || 'API hatası');
            }

            return data;
        } catch (error) {
            console.error('API çağrısı hatası:', error);
            throw error;
        }
    }
}

// Uygulamayı başlat
document.addEventListener('DOMContentLoaded', () => {
    window.app = new FriendZoneApp();
});

// CSS Animasyonları için global styles
const style = document.createElement('style');
style.textContent = `
    .notification {
        position: fixed;
        top: 20px;
        right: 20px;
        background: var(--bg-tertiary);
        border: 1px solid var(--border-primary);
        border-radius: var(--border-radius);
        padding: 16px;
        max-width: 400px;
        box-shadow: var(--shadow-lg);
        transform: translateX(400px);
        opacity: 0;
        transition: all 0.3s ease;
        z-index: 1000;
    }

    .notification.show {
        transform: translateX(0);
        opacity: 1;
    }

    .notification-success {
        border-left: 4px solid var(--accent-success);
    }

    .notification-error {
        border-left: 4px solid var(--accent-danger);
    }

    .notification-warning {
        border-left: 4px solid var(--accent-warning);
    }

    .notification-info {
        border-left: 4px solid var(--accent-primary);
    }

    .notification-content {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-right: 30px;
    }

    .notification-close {
        position: absolute;
        top: 12px;
        right: 12px;
        background: none;
        border: none;
        color: var(--text-muted);
        cursor: pointer;
        padding: 4px;
        border-radius: 4px;
    }

    .notification-close:hover {
        background: var(--bg-accent);
        color: var(--text-primary);
    }

    /* Scroll animations */
    .feature-card, .step {
        opacity: 0;
        transform: translateY(30px);
        transition: all 0.6s ease;
    }

    .feature-card.animate-in, .step.animate-in {
        opacity: 1;
        transform: translateY(0);
    }

    .sidebar.collapsed {
        width: 72px;
    }

    .sidebar.collapsed .logo span,
    .sidebar.collapsed .user-info,
    .sidebar.collapsed .nav-item span,
    .sidebar.collapsed .nav-section h3,
    .sidebar.collapsed .connection-status span {
        display: none;
    }

    .sidebar.collapsed .nav-item {
        justify-content: center;
        padding: 12px;
    }
`;
document.head.appendChild(style);