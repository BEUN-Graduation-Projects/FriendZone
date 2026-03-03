// frontend/js/main.js

class FriendZoneApp {
    constructor() {
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.setupAnimations();
        this.checkAuthStatus();
        this.setupLogoutButton();
    }

    setupEventListeners() {
        const sidebarToggle = document.querySelector('.sidebar-toggle');
        const sidebar = document.querySelector('.sidebar');

        if (sidebarToggle && sidebar) {
            sidebarToggle.addEventListener('click', () => {
                sidebar.classList.toggle('collapsed');
            });
        }

        const navItems = document.querySelectorAll('.nav-item');
        navItems.forEach(item => {
            item.addEventListener('click', (e) => {
                if (!item.classList.contains('active')) {
                    navItems.forEach(nav => nav.classList.remove('active'));
                    item.classList.add('active');
                }
            });
        });

        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({ behavior: 'smooth' });
                }
            });
        });
    }

    setupAnimations() {
        const observerOptions = { threshold: 0.1, rootMargin: '0px 0px -50px 0px' };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate-in');
                }
            });
        }, observerOptions);

        document.querySelectorAll('.feature-card, .step').forEach(el => {
            observer.observe(el);
        });
    }

    checkAuthStatus() {
        const token = localStorage.getItem('friendzone_token');
        const user = JSON.parse(localStorage.getItem('friendzone_user'));

        if (token && user) {
            this.updateNavigationForLoggedInUser(user);
            this.updateUIWithUserData(user);
        }
    }

    setupLogoutButton() {
        document.addEventListener('click', (e) => {
            if (e.target.closest('#logout-btn')) {
                e.preventDefault();
                this.logout();
            }
        });
    }

    updateNavigationForLoggedInUser(user) {
        const navSections = document.querySelectorAll('.nav-section');
        navSections.forEach(section => {
            const profileNav = section.querySelector('a[href="profile.html"]');
            if (profileNav) return;
        });

        const userProfile = document.querySelector('.user-profile');
        if (userProfile) {
            userProfile.style.cursor = 'pointer';
            userProfile.addEventListener('click', () => {
                window.location.href = 'profile.html';
            });
        }
    }

    updateUIWithUserData(user) {
        const avatar = document.querySelector('.avatar');
        if (avatar && user.name) {
            if (avatar.querySelector('img')) {
                avatar.querySelector('img').alt = user.name;
            } else {
                const initials = user.name.split(' ').map(n => n[0]).join('').toUpperCase();
                avatar.innerHTML = `<span>${initials}</span>`;
            }
        }

        const username = document.querySelector('.username');
        if (username) username.textContent = user.name || 'Kullanıcı';

        const status = document.querySelector('.status');
        if (status) status.textContent = 'Çevrimiçi';

        const logoutItems = document.querySelectorAll('.nav-item');
        let hasLogout = false;
        logoutItems.forEach(item => {
            if (item.querySelector('span')?.textContent === 'Çıkış Yap') {
                hasLogout = true;
            }
        });

        if (!hasLogout) {
            const profileSection = Array.from(document.querySelectorAll('.nav-section')).find(
                section => section.querySelector('h3')?.textContent === 'PROFİL'
            );

            if (profileSection) {
                const logoutLink = document.createElement('a');
                logoutLink.href = '#';
                logoutLink.className = 'nav-item';
                logoutLink.id = 'logout-btn';
                logoutLink.innerHTML = `
                    <i class="fas fa-sign-out-alt"></i>
                    <span>Çıkış Yap</span>
                `;
                profileSection.appendChild(logoutLink);
            }
        }
    }

    logout() {
        localStorage.removeItem('friendzone_token');
        localStorage.removeItem('friendzone_user');
        window.location.href = 'index.html';
    }

    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <i class="fas fa-${this.getNotificationIcon(type)}"></i>
                <span>${message}</span>
            </div>
            <button class="notification-close"><i class="fas fa-times"></i></button>
        `;

        document.body.appendChild(notification);

        setTimeout(() => notification.classList.add('show'), 100);

        notification.querySelector('.notification-close').addEventListener('click', () => {
            notification.classList.remove('show');
            setTimeout(() => notification.remove(), 300);
        });

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

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    window.app = new FriendZoneApp();
});

// Global styles for notifications
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

    .notification-success { border-left: 4px solid var(--accent-success); }
    .notification-error { border-left: 4px solid var(--accent-danger); }
    .notification-warning { border-left: 4px solid var(--accent-warning); }
    .notification-info { border-left: 4px solid var(--accent-primary); }

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

    .sidebar.collapsed { width: 72px; }
    .sidebar.collapsed .logo span,
    .sidebar.collapsed .user-info,
    .sidebar.collapsed .nav-item span,
    .sidebar.collapsed .nav-section h3,
    .sidebar.collapsed .connection-status span {
        display: none;
    }
    .sidebar.collapsed .nav-item { justify-content: center; padding: 12px; }
`;
document.head.appendChild(style);