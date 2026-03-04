// frontend/js/auth.js - TAM DOSYA

class AuthManager {
    constructor() {
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.checkExistingAuth();
    }

    setupEventListeners() {
        const passwordToggle = document.getElementById('passwordToggle');
        if (passwordToggle) {
            passwordToggle.addEventListener('click', this.togglePasswordVisibility.bind(this));
        }

        const loginForm = document.getElementById('loginForm');
        const signupForm = document.getElementById('signupForm');

        if (loginForm) {
            loginForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleLogin(e);
            });
        }

        if (signupForm) {
            signupForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleSignup(e);
            });
        }
    }

    togglePasswordVisibility() {
        const passwordInput = document.getElementById('password');
        const toggleIcon = document.querySelector('#passwordToggle i');

        if (passwordInput.type === 'password') {
            passwordInput.type = 'text';
            toggleIcon.className = 'fas fa-eye-slash';
        } else {
            passwordInput.type = 'password';
            toggleIcon.className = 'fas fa-eye';
        }
    }

    async handleSignup(e) {
        const formData = new FormData(e.target);
        const data = {
            name: formData.get('name')?.trim(),
            email: formData.get('email')?.trim().toLowerCase(),
            password: formData.get('password'),
            university: formData.get('university'),
            department: formData.get('department'),
            year: parseInt(formData.get('year'))
        };

        console.log('📤 Gönderilen veri:', data);

        // Validasyon
        const errors = [];

        if (!data.name || data.name.length < 2) {
            errors.push('İsim en az 2 karakter olmalıdır');
        }

        if (!data.email) {
            errors.push('Email adresi gereklidir');
        } else {
            const eduEmailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.edu\.tr$/;
            if (!eduEmailRegex.test(data.email)) {
                errors.push('Lütfen geçerli bir .edu.tr uzantılı email adresi girin');
            }
        }

        if (!data.password || data.password.length < 6) {
            errors.push('Şifre en az 6 karakter olmalıdır');
        }

        if (!data.university) {
            errors.push('Üniversite seçiniz');
        }

        if (!data.department) {
            errors.push('Bölüm gereklidir');
        }

        if (!data.year || isNaN(data.year)) {
            errors.push('Sınıf seçiniz');
        }

        if (errors.length > 0) {
            this.showError(errors.join('<br>'));
            return;
        }

        const submitBtn = e.target.querySelector('button[type="submit"]');
        this.setLoadingState(submitBtn, true);

        try {
            // ÖNEMLİ: Tam URL kullan
            const response = await fetch('http://localhost:5001/api/auth/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: JSON.stringify(data)
            });

            console.log('📥 Response status:', response.status);

            const result = await response.json();
            console.log('📥 API Yanıtı:', result);

            if (response.ok && result.success) {
                localStorage.setItem('friendzone_token', result.data.token);
                localStorage.setItem('friendzone_user', JSON.stringify(result.data.user));

                this.showSuccess('Hesabınız başarıyla oluşturuldu!');

                setTimeout(() => {
                    window.location.href = 'http://localhost:63342/FriendZone/frontend/personality_test.html';
                }, 1500);
            } else {
                throw new Error(result.message || 'Kayıt başarısız');
            }
        } catch (error) {
            console.error('❌ Hata:', error);
            this.showError('Sunucuya bağlanılamadı: ' + error.message);
        } finally {
            this.setLoadingState(submitBtn, false);
        }
    }

    async handleLogin(e) {
        const formData = new FormData(e.target);
        const data = {
            email: formData.get('email')?.trim().toLowerCase(),
            password: formData.get('password')
        };

        const errors = [];

        if (!data.email) {
            errors.push('Email adresi gereklidir');
        }

        if (!data.password || data.password.length < 6) {
            errors.push('Şifre en az 6 karakter olmalıdır');
        }

        if (errors.length > 0) {
            this.showError(errors.join('<br>'));
            return;
        }

        const submitBtn = e.target.querySelector('button[type="submit"]');
        this.setLoadingState(submitBtn, true);

        try {
            const response = await fetch('http://localhost:5001/api/auth/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });

            const result = await response.json();

            if (response.ok && result.success) {
                localStorage.setItem('friendzone_token', result.data.token);
                localStorage.setItem('friendzone_user', JSON.stringify(result.data.user));

                this.showSuccess('Başarıyla giriş yapıldı!');

                setTimeout(() => {
                    window.location.href = 'http://localhost:63342/FriendZone/frontend/communities.html';
                }, 1500);
            } else {
                throw new Error(result.message || 'Giriş başarısız');
            }
        } catch (error) {
            console.error('❌ Hata:', error);
            this.showError('Sunucuya bağlanılamadı: ' + error.message);
        } finally {
            this.setLoadingState(submitBtn, false);
        }
    }

    showError(message) {
        this.removeMessages();
        const form = document.querySelector('.auth-form');
        if (!form) return;

        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.innerHTML = `<i class="fas fa-exclamation-circle"></i> ${message}`;
        form.insertBefore(errorDiv, form.firstChild);

        setTimeout(() => {
            if (errorDiv.parentNode) errorDiv.remove();
        }, 5000);
    }

    showSuccess(message) {
        this.removeMessages();
        const form = document.querySelector('.auth-form');
        if (!form) return;

        const successDiv = document.createElement('div');
        successDiv.className = 'success-message';
        successDiv.innerHTML = `<i class="fas fa-check-circle"></i> ${message}`;
        form.insertBefore(successDiv, form.firstChild);
    }

    removeMessages() {
        document.querySelectorAll('.error-message, .success-message').forEach(msg => msg.remove());
    }

    setLoadingState(button, isLoading) {
        if (isLoading) {
            button.classList.add('btn-loading');
            button.disabled = true;
            button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> İşleniyor...';
        } else {
            button.classList.remove('btn-loading');
            button.disabled = false;
            button.innerHTML = '<i class="fas fa-user-plus"></i> Hesap Oluştur';
        }
    }

    checkExistingAuth() {
        const token = localStorage.getItem('friendzone_token');
        const user = JSON.parse(localStorage.getItem('friendzone_user') || 'null');

        if (token && user) {
            const currentPage = window.location.pathname.split('/').pop();
            if (currentPage === 'login.html' || currentPage === 'signup.html') {
                if (user.is_test_completed) {
                    window.location.href = 'communities.html';
                } else {
                    window.location.href = 'personality_test.html';
                }
            }
        }
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    window.authManager = new AuthManager();
});