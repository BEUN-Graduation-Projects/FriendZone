// frontend/js/sidebar.js - Sidebar yönetimi

class SidebarManager {
    constructor() {
        this.currentUser = null;
        this.init();
    }

    init() {
        this.loadUserData();
        this.setupEventListeners();
        this.highlightCurrentPage();
    }

    loadUserData() {
        const userStr = localStorage.getItem('friendzone_user');
        const token = localStorage.getItem('friendzone_token');

        if (userStr && token) {
            this.currentUser = JSON.parse(userStr);
            this.updateSidebarForLoggedInUser();
        } else {
            this.updateSidebarForGuest();
        }
    }

    updateSidebarForLoggedInUser() {
        // Kullanıcı bilgilerini güncelle
        document.getElementById('sidebarUsername').textContent = this.currentUser.name || 'Kullanıcı';
        document.getElementById('avatarText').textContent = (this.currentUser.name || 'K').charAt(0).toUpperCase();

        // Auth bölümünü gizle, test ve logout bölümünü göster
        document.getElementById('authSection').style.display = 'none';
        document.getElementById('testSection').style.display = 'block';
        document.getElementById('logoutSection').style.display = 'block';
    }

    updateSidebarForGuest() {
        document.getElementById('sidebarUsername').textContent = 'Misafir';
        document.getElementById('avatarText').textContent = 'M';
        document.getElementById('authSection').style.display = 'block';
        document.getElementById('testSection').style.display = 'none';
        document.getElementById('logoutSection').style.display = 'none';
    }

    highlightCurrentPage() {
        const currentPage = window.location.pathname.split('/').pop();
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active');
            const page = item.dataset.page;
            if (page === 'home' && currentPage === 'index.html') item.classList.add('active');
            else if (page === 'communities' && currentPage === 'communities.html') item.classList.add('active');
            else if (page === 'profile' && currentPage === 'profile.html') item.classList.add('active');
            else if (page === 'login' && currentPage === 'login.html') item.classList.add('active');
            else if (page === 'signup' && currentPage === 'signup.html') item.classList.add('active');
            else if (page === 'personality' && currentPage === 'personality_test.html') item.classList.add('active');
            else if (page === 'hobbies' && currentPage === 'hobbies.html') item.classList.add('active');
        });
    }

    setupEventListeners() {
        // Sidebar toggle
        document.getElementById('sidebarToggle')?.addEventListener('click', () => {
            document.querySelector('.sidebar').classList.toggle('collapsed');
        });

        // Logout
        document.getElementById('logoutBtn')?.addEventListener('click', (e) => {
            e.preventDefault();
            localStorage.removeItem('friendzone_token');
            localStorage.removeItem('friendzone_user');
            window.location.href = 'index.html';
        });

        // Profil sayfasına git
        document.getElementById('userProfile')?.addEventListener('click', () => {
            if (this.currentUser) {
                window.location.href = 'profile.html';
            } else {
                window.location.href = 'login.html';
            }
        });
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    window.sidebarManager = new SidebarManager();
});