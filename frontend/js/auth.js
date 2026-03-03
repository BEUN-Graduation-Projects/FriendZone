// frontend/js/auth.js

class AuthManager {
    constructor() {
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.checkExistingAuth();
    }

    setupEventListeners() {
        // Password toggle
        const passwordToggle = document.getElementById('passwordToggle');
        if (passwordToggle) {
            passwordToggle.addEventListener('click', this.togglePasswordVisibility.bind(this));
        }

        // Form submission
        const loginForm = document.getElementById('loginForm');
        const signupForm = document.getElementById('signupForm');

        if (loginForm) {
            loginForm.addEventListener('submit', this.handleLogin.bind(this));
        }

        if (signupForm) {
            signupForm.addEventListener('submit', this.handleSignup.bind(this));
        }

        // Real-time validation
        this.setupRealTimeValidation();
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

    async handleLogin(e) {
        e.preventDefault();

        const formData = new FormData(e.target);
        const data = {
            email: formData.get('email'),
            password: formData.get('password'),
            remember: formData.get('remember') === 'on'
        };

        if (!this.validateLoginData(data)) {
            return;
        }

        const submitBtn = e.target.querySelector('button[type="submit"]');
        this.setLoadingState(submitBtn, true);

        try {
            const response = await fetch('/api/auth/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });

            const result = await response.json();

            if (response.ok && result.success) {
                localStorage.setItem('friendzone_token', result.data.token);
                localStorage.setItem('friendzone_user', JSON.stringify(result.data.user));

                this.showSuccess('Başarıyla giriş yapıldı! Yönlendiriliyorsunuz...');

                setTimeout(() => {
                    window.location.href = 'communities.html';
                }, 1500);
            } else {
                throw new Error(result.message || 'Giriş başarısız');
            }
        } catch (error) {
            this.showError(error.message);
        } finally {
            this.setLoadingState(submitBtn, false);
        }
    }

    async handleSignup(e) {
        e.preventDefault();

        const formData = new FormData(e.target);
        const data = {
            name: formData.get('name'),
            email: formData.get('email'),
            password: formData.get('password'),
            university: formData.get('university'),
            department: formData.get('department'),
            year: parseInt(formData.get('year'))
        };

        if (!this.validateSignupData(data)) {
            return;
        }

        const submitBtn = e.target.querySelector('button[type="submit"]');
        this.setLoadingState(submitBtn, true);

        try {
            const response = await fetch('/api/auth/register', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });

            const result = await response.json();

            if (response.ok && result.success) {
                localStorage.setItem('friendzone_token', result.data.token);
                localStorage.setItem('friendzone_user', JSON.stringify(result.data.user));

                this.showSuccess('Hesabınız başarıyla oluşturuldu! Yönlendiriliyorsunuz...');

                setTimeout(() => {
                    window.location.href = 'personality_test.html';
                }, 1500);
            } else {
                throw new Error(result.message || 'Kayıt başarısız');
            }
        } catch (error) {
            this.showError(error.message);
        } finally {
            this.setLoadingState(submitBtn, false);
        }
    }

    validateLoginData(data) {
        let isValid = true;

        if (!data.email || !this.isValidEmail(data.email)) {
            this.showFieldError('email', 'Geçerli bir e-posta adresi girin');
            isValid = false;
        } else {
            this.clearFieldError('email');
        }

        if (!data.password || data.password.length < 6) {
            this.showFieldError('password', 'Şifre en az 6 karakter olmalıdır');
            isValid = false;
        } else {
            this.clearFieldError('password');
        }

        return isValid;
    }

    validateSignupData(data) {
        let isValid = true;

        if (!data.name || data.name.length < 2) {
            this.showFieldError('name', 'İsim en az 2 karakter olmalıdır');
            isValid = false;
        } else {
            this.clearFieldError('name');
        }

        if (!data.email || !this.isValidEmail(data.email)) {
            this.showFieldError('email', 'Geçerli bir e-posta adresi girin');
            isValid = false;
        } else {
            this.clearFieldError('email');
        }

        if (!data.password || data.password.length < 6) {
            this.showFieldError('password', 'Şifre en az 6 karakter olmalıdır');
            isValid = false;
        } else {
            this.clearFieldError('password');
        }

        if (!data.university) {
            this.showFieldError('university', 'Üniversite seçiniz');
            isValid = false;
        } else {
            this.clearFieldError('university');
        }

        return isValid;
    }

    isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    showFieldError(fieldName, message) {
        const field = document.getElementById(fieldName);
        if (!field) return;

        const formGroup = field.closest('.form-group');
        if (!formGroup) return;

        formGroup.classList.add('error');

        let messageElement = formGroup.querySelector('.form-message');
        if (!messageElement) {
            messageElement = document.createElement('div');
            messageElement.className = 'form-message error';
            formGroup.appendChild(messageElement);
        }

        messageElement.textContent = message;
    }

    clearFieldError(fieldName) {
        const field = document.getElementById(fieldName);
        if (!field) return;

        const formGroup = field.closest('.form-group');
        if (!formGroup) return;

        formGroup.classList.remove('error');

        const messageElement = formGroup.querySelector('.form-message');
        if (messageElement) {
            messageElement.remove();
        }
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

    showError(message) {
        this.removeMessages();

        const form = document.querySelector('.auth-form');
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.innerHTML = `<i class="fas fa-exclamation-circle"></i> ${message}`;

        form.insertBefore(errorDiv, form.firstChild);

        setTimeout(() => errorDiv.remove(), 5000);
    }

    showSuccess(message) {
        this.removeMessages();

        const form = document.querySelector('.auth-form');
        const successDiv = document.createElement('div');
        successDiv.className = 'success-message';
        successDiv.innerHTML = `<i class="fas fa-check-circle"></i> ${message}`;

        form.insertBefore(successDiv, form.firstChild);
    }

    removeMessages() {
        document.querySelectorAll('.error-message, .success-message').forEach(msg => msg.remove());
    }

    checkExistingAuth() {
        const token = localStorage.getItem('friendzone_token');
        const user = JSON.parse(localStorage.getItem('friendzone_user'));

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

    setupRealTimeValidation() {
        const emailInput = document.getElementById('email');
        if (emailInput) {
            emailInput.addEventListener('blur', () => {
                const value = emailInput.value.trim();
                if (value && !this.isValidEmail(value)) {
                    this.showFieldError('email', 'Geçerli bir e-posta adresi girin');
                } else if (value) {
                    this.clearFieldError('email');
                }
            });
        }

        const passwordInput = document.getElementById('password');
        if (passwordInput) {
            passwordInput.addEventListener('input', () => {
                this.updatePasswordStrength(passwordInput.value);
            });
        }
    }

    updatePasswordStrength(password) {
        const strengthBar = document.querySelector('.strength-fill');
        const strengthText = document.querySelector('.strength-text');
        const strengthContainer = document.querySelector('.password-strength');

        if (!strengthBar || !strengthText || !strengthContainer) return;

        let strength = 0;
        if (password.length >= 6) strength++;
        if (password.length >= 8) strength++;
        if (/[A-Z]/.test(password)) strength++;
        if (/[0-9]/.test(password)) strength++;
        if (/[^A-Za-z0-9]/.test(password)) strength++;

        strengthContainer.setAttribute('data-strength', strength);

        const strengthLabels = ['', 'Çok Zayıf', 'Zayıf', 'Orta', 'İyi', 'Güçlü'];
        strengthText.textContent = `Şifre gücü: ${strengthLabels[strength]}`;
    }
}

// Initialize auth manager
document.addEventListener('DOMContentLoaded', () => {
    window.authManager = new AuthManager();
});