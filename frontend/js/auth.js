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
            password: formData.get('password')
        };

        // Validation
        if (!this.validateLoginData(data)) {
            return;
        }

        const submitBtn = e.target.querySelector('button[type="submit"]');
        this.setLoadingState(submitBtn, true);

        try {
            const response = await fetch('/api/auth/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });

            const result = await response.json();

            if (response.ok) {
                this.handleSuccessfulLogin(result.data);
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

        // Validation
        if (!this.validateSignupData(data)) {
            return;
        }

        const submitBtn = e.target.querySelector('button[type="submit"]');
        this.setLoadingState(submitBtn, true);

        try {
            const response = await fetch('/api/auth/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });

            const result = await response.json();

            if (response.ok) {
                this.handleSuccessfulSignup(result.data);
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

        // Email validation
        if (!data.email || !this.isValidEmail(data.email)) {
            this.showFieldError('email', 'Geçerli bir e-posta adresi girin');
            isValid = false;
        } else {
            this.clearFieldError('email');
        }

        // Password validation
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

        // Name validation
        if (!data.name || data.name.length < 2) {
            this.showFieldError('name', 'İsim en az 2 karakter olmalıdır');
            isValid = false;
        } else {
            this.clearFieldError('name');
        }

        // Email validation
        if (!data.email || !this.isValidEmail(data.email)) {
            this.showFieldError('email', 'Geçerli bir üniversite e-posta adresi girin');
            isValid = false;
        } else {
            this.clearFieldError('email');
        }

        // Password validation
        if (!data.password || data.password.length < 6) {
            this.showFieldError('password', 'Şifre en az 6 karakter olmalıdır');
            isValid = false;
        } else {
            this.clearFieldError('password');
        }

        // University validation
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
        const formGroup = field.closest('.form-group');

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
        const formGroup = field.closest('.form-group');

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

    handleSuccessfulLogin(data) {
        // Save token and user data
        localStorage.setItem('friendzone_token', data.token);
        localStorage.setItem('friendzone_user', JSON.stringify(data.user));

        // Show success message
        this.showSuccess('Başarıyla giriş yapıldı! Yönlendiriliyorsunuz...');

        // Redirect to appropriate page
        setTimeout(() => {
            if (data.user.is_test_completed) {
                window.location.href = 'communities.html';
            } else {
                window.location.href = 'personality_test.html';
            }
        }, 1500);
    }

    handleSuccessfulSignup(data) {
        // Save token and user data
        localStorage.setItem('friendzone_token', data.token);
        localStorage.setItem('friendzone_user', JSON.stringify(data.user));

        // Show success message
        this.showSuccess('Hesabınız başarıyla oluşturuldu! Kişilik testine yönlendiriliyorsunuz...');

        // Redirect to personality test
        setTimeout(() => {
            window.location.href = 'personality_test.html';
        }, 2000);
    }

    showError(message) {
        if (window.app && window.app.showNotification) {
            window.app.showNotification(message, 'error');
        } else {
            alert(`Hata: ${message}`);
        }
    }

    showSuccess(message) {
        if (window.app && window.app.showNotification) {
            window.app.showNotification(message, 'success');
        } else {
            alert(message);
        }
    }

    checkExistingAuth() {
        const token = localStorage.getItem('friendzone_token');
        if (token && (window.location.pathname.includes('login.html') ||
                      window.location.pathname.includes('signup.html'))) {

            // Check if user has completed tests
            this.checkTestStatusAndRedirect();
        }
    }

    async checkTestStatusAndRedirect() {
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

                if (user.is_test_completed) {
                    window.location.href = 'communities.html';
                } else {
                    window.location.href = 'personality_test.html';
                }
            }
        } catch (error) {
            console.error('Auth check failed:', error);
            // If there's an error, clear invalid token
            localStorage.removeItem('friendzone_token');
            localStorage.removeItem('friendzone_user');
        }
    }

    setupRealTimeValidation() {
        // Email validation
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

        // Password strength
        const passwordInput = document.getElementById('password');
        if (passwordInput) {
            passwordInput.addEventListener('input', this.checkPasswordStrength.bind(this));
        }
    }

    checkPasswordStrength() {
        const password = document.getElementById('password').value;
        const strengthMeter = document.getElementById('passwordStrength');

        if (!strengthMeter) return;

        let strength = 0;
        let feedback = '';

        // Length check
        if (password.length >= 8) strength += 1;

        // Complexity checks
        if (/[A-Z]/.test(password)) strength += 1;
        if (/[a-z]/.test(password)) strength += 1;
        if (/[0-9]/.test(password)) strength += 1;
        if (/[^A-Za-z0-9]/.test(password)) strength += 1;

        // Update strength meter
        strengthMeter.className = `password-strength strength-${strength}`;

        // Provide feedback
        switch(strength) {
            case 0:
            case 1:
                feedback = 'Zayıf';
                break;
            case 2:
            case 3:
                feedback = 'Orta';
                break;
            case 4:
                feedback = 'Güçlü';
                break;
            case 5:
                feedback = 'Çok Güçlü';
                break;
        }

        strengthMeter.textContent = `Şifre gücü: ${feedback}`;
    }
}

// Initialize auth manager
document.addEventListener('DOMContentLoaded', () => {
    window.authManager = new AuthManager();
});