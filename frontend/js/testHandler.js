// frontend/js/testHandler.js

class TestHandler {
    constructor() {
        this.currentQuestion = 0;
        this.answers = {};
        this.questions = [
            {
                id: 1,
                question: "Yeni insanlarla tanışmak size ne ifade eder?",
                type: "ei",
                options: [
                    { value: "E", text: "Heyecan verici, enerji doldurur", score: 3 },
                    { value: "I", text: "Yorucu, yalnız kalmayı tercih ederim", score: 1 }
                ]
            },
            {
                id: 2,
                question: "Bir proje üzerinde çalışırken nasıl bir yaklaşım izlersiniz?",
                type: "jp",
                options: [
                    { value: "J", text: "Plan yapar, adım adım ilerlerim", score: 3 },
                    { value: "P", text: "Akışına bırakır, esnek olurum", score: 1 }
                ]
            },
            {
                id: 3,
                question: "Karar verirken daha çok neye güvenirsiniz?",
                type: "tf",
                options: [
                    { value: "T", text: "Mantığa ve analize", score: 3 },
                    { value: "F", text: "Duygulara ve insan faktörüne", score: 1 }
                ]
            },
            {
                id: 4,
                question: "Bir grup tartışmasında genellikle nasıl davranırsınız?",
                type: "ei",
                options: [
                    { value: "E", text: "Konuşur, fikirlerimi paylaşırım", score: 3 },
                    { value: "I", text: "Dinler, sonra düşünürüm", score: 1 }
                ]
            },
            {
                id: 5,
                question: "Detaylarla uğraşmak size göre nasıldır?",
                type: "sn",
                options: [
                    { value: "S", text: "Önemlidir, dikkat ederim", score: 3 },
                    { value: "N", text: "Sıkıcıdır, büyük resmi görmek isterim", score: 1 }
                ]
            },
            {
                id: 6,
                question: "Hafta sonu planlarınızı genellikle nasıl yaparsınız?",
                type: "jp",
                options: [
                    { value: "J", text: "Önceden yapar, programlı olurum", score: 3 },
                    { value: "P", text: "Anlık kararlarla şekillendiririm", score: 1 }
                ]
            },
            {
                id: 7,
                question: "Bir arkadaşınız sıkıntılıyken nasıl davranırsınız?",
                type: "tf",
                options: [
                    { value: "T", text: "Çözüm önerileri sunarım", score: 3 },
                    { value: "F", text: "Duygusal destek olur, dinlerim", score: 1 }
                ]
            },
            {
                id: 8,
                question: "Yeni bir şey öğrenirken nasıl bir yol izlersiniz?",
                type: "sn",
                options: [
                    { value: "S", text: "Adım adım, pratik yaparak öğrenirim", score: 3 },
                    { value: "N", text: "Teoriyi anlar, sonra uygularım", score: 1 }
                ]
            },
            {
                id: 9,
                question: "Enerjinizi nereden alırsınız?",
                type: "ei",
                options: [
                    { value: "E", text: "Sosyal ortamlardan, insanlardan", score: 3 },
                    { value: "I", text: "Yalnız geçirdiğim zamanlardan", score: 1 }
                ]
            },
            {
                id: 10,
                question: "Kararlarınızda hangisi daha baskındır?",
                type: "tf",
                options: [
                    { value: "T", text: "Mantık ön plandadır", score: 3 },
                    { value: "F", text: "Duygular ön plandadır", score: 1 }
                ]
            }
        ];
        this.init();
    }

    init() {
        this.loadUserData();
        this.renderQuestion();
        this.updateProgress();
        this.setupEventListeners();
    }

    loadUserData() {
        const user = JSON.parse(localStorage.getItem('friendzone_user'));
        if (user) {
            document.getElementById('userName').textContent = user.name || 'Kullanıcı';
            document.getElementById('userAvatar').textContent = (user.name || 'K').charAt(0).toUpperCase();
        }
    }

    renderQuestion() {
        const container = document.getElementById('questionContainer');
        const question = this.questions[this.currentQuestion];

        const optionsHTML = question.options.map(opt => {
            const isSelected = this.answers[this.currentQuestion] === opt.value;
            return `
                <div class="option-card ${isSelected ? 'selected' : ''}" data-value="${opt.value}">
                    <div class="option-content">
                        <div class="option-title">${opt.text}</div>
                    </div>
                </div>
            `;
        }).join('');

        container.innerHTML = `
            <div class="question-card">
                <div class="question-number">Soru ${this.currentQuestion + 1} / ${this.questions.length}</div>
                <h2 class="question-text">${question.question}</h2>
                <div class="options-grid">
                    ${optionsHTML}
                </div>
            </div>
        `;

        document.querySelectorAll('.option-card').forEach(card => {
            card.addEventListener('click', () => {
                const value = card.dataset.value;
                this.selectOption(value);
            });
        });
    }

    selectOption(value) {
        this.answers[this.currentQuestion] = value;
        this.renderQuestion();

        if (this.currentQuestion < this.questions.length - 1) {
            setTimeout(() => this.nextQuestion(), 300);
        } else {
            document.getElementById('nextBtn').style.display = 'none';
            document.getElementById('submitBtn').style.display = 'flex';
        }
    }

    nextQuestion() {
        if (this.currentQuestion < this.questions.length - 1) {
            this.currentQuestion++;
            this.renderQuestion();
            this.updateProgress();
        }
    }

    previousQuestion() {
        if (this.currentQuestion > 0) {
            this.currentQuestion--;
            this.renderQuestion();
            this.updateProgress();
        }
    }

    updateProgress() {
        const progress = ((this.currentQuestion + 1) / this.questions.length) * 100;
        document.getElementById('progressFill').style.width = `${progress}%`;
        document.getElementById('currentQuestion').textContent = this.currentQuestion + 1;
        document.getElementById('totalQuestions').textContent = this.questions.length;

        const prevBtn = document.getElementById('prevBtn');
        if (prevBtn) prevBtn.disabled = this.currentQuestion === 0;
    }

    setupEventListeners() {
        document.getElementById('prevBtn')?.addEventListener('click', () => this.previousQuestion());
        document.getElementById('nextBtn')?.addEventListener('click', () => this.nextQuestion());
        document.getElementById('submitBtn')?.addEventListener('click', () => this.submitTest());
    }

    async submitTest() {
        if (Object.keys(this.answers).length !== this.questions.length) {
            alert('Lütfen tüm soruları cevaplayın!');
            return;
        }

        const submitBtn = document.getElementById('submitBtn');
        this.setLoadingState(submitBtn, true);

        try {
            const user = JSON.parse(localStorage.getItem('friendzone_user'));
            const token = localStorage.getItem('friendzone_token');

            // MBTI tipini hesapla
            const personalityType = this.calculatePersonalityType();

            const response = await fetch('/api/test/personality', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    user_id: user.id,
                    personality_type: personalityType,
                    answers: this.answers
                })
            });

            const result = await response.json();

            if (response.ok && result.success) {
                user.personality_type = personalityType;
                localStorage.setItem('friendzone_user', JSON.stringify(user));

                this.showResult(personalityType);
            } else {
                throw new Error(result.message || 'Test gönderilemedi');
            }
        } catch (error) {
            console.error('Test hatası:', error);
            alert('Test gönderilirken bir hata oluştu: ' + error.message);
        } finally {
            this.setLoadingState(submitBtn, false);
        }
    }

    calculatePersonalityType() {
        let eCount = 0, iCount = 0, sCount = 0, nCount = 0, tCount = 0, fCount = 0, jCount = 0, pCount = 0;

        Object.values(this.answers).forEach(answer => {
            if (answer === 'E') eCount++;
            else if (answer === 'I') iCount++;
            else if (answer === 'S') sCount++;
            else if (answer === 'N') nCount++;
            else if (answer === 'T') tCount++;
            else if (answer === 'F') fCount++;
            else if (answer === 'J') jCount++;
            else if (answer === 'P') pCount++;
        });

        let type = '';
        type += (eCount >= iCount) ? 'E' : 'I';
        type += (sCount >= nCount) ? 'S' : 'N';
        type += (tCount >= fCount) ? 'T' : 'F';
        type += (jCount >= pCount) ? 'J' : 'P';

        return type;
    }

    showResult(personalityType) {
        const descriptions = {
            'ISTJ': 'Mantıklı, düzenli ve güvenilirsin. Kurallara ve düzene önem verirsin.',
            'ISFJ': 'Koruyucu, sıcak kanlı ve fedakarsın. Başkalarına yardım etmekten mutlu olursun.',
            'INFJ': 'Yaratıcı, idealist ve hassassın. Derin ilişkiler kurmayı seversin.',
            'INTJ': 'Stratejik, mantıklı ve bağımsızsın. Karmaşık problemleri çözmekte iyisin.',
            'ISTP': 'Pratik, esnek ve gözlemcisin. Ellerinle çalışmayı ve sorun çözmeyi seversin.',
            'ISFP': 'Sanatçı ruhlu, uyumlu ve maceraperestsin. Güzelliği takdir edersin.',
            'INFP': 'İdealist, yaratıcı ve duygusalsın. Kendi değerlerine sıkı sıkıya bağlısın.',
            'INTP': 'Analitik, yenilikçi ve meraklısın. Teorik kavramları anlamayı seversin.',
            'ESTP': 'Enerjik, mantıklı ve spontanesin. Anı yaşamayı seversin.',
            'ESFP': 'Canlı, eğlenceli ve arkadaş canlısısın. İnsanları eğlendirmeyi seversin.',
            'ENFP': 'Yaratıcı, sosyal ve coşkulusun. Yeni olasılıkları keşfetmeyi seversin.',
            'ENTP': 'Yaratıcı, tartışmacı ve meraklısın. Entelektüel zorlukları seversin.',
            'ESTJ': 'Mantıklı, düzenli ve kararlısın. Liderlik etmeyi ve organize etmeyi seversin.',
            'ESFJ': 'Sıcak kanlı, popüler ve yardımsever sin. Başkalarını mutlu etmeyi seversin.',
            'ENFJ': 'Karizmatik, idealist ve ilham vericisin. Başkalarına yardım etmeyi seversin.',
            'ENTJ': 'Kararlı, mantıklı ve lider ruhluy sun. Büyük hedeflere ulaşmayı seversin.'
        };

        const resultHTML = `
            <div class="results-container">
                <div class="personality-result">
                    <div class="result-icon">
                        <i class="fas fa-brain"></i>
                    </div>
                    <h1 class="result-title">Kişilik Tipin: ${personalityType}</h1>
                    <p class="result-description">${descriptions[personalityType] || 'Benzersiz kişilik özelliklerine sahipsin!'}</p>
                    <div class="test-navigation">
                        <a href="hobbies.html" class="btn btn-primary btn-large">
                            <i class="fas fa-arrow-right"></i>
                            Hobi Testine Geç
                        </a>
                    </div>
                </div>
            </div>
        `;

        document.querySelector('.test-content').innerHTML = resultHTML;
    }

    setLoadingState(button, isLoading) {
        if (isLoading) {
            button.classList.add('btn-loading');
            button.disabled = true;
            button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> İşleniyor...';
        } else {
            button.classList.remove('btn-loading');
            button.disabled = false;
            button.innerHTML = '<i class="fas fa-paper-plane"></i> Testi Tamamla';
        }
    }
}

// Initialize test handler
document.addEventListener('DOMContentLoaded', () => {
    window.testHandler = new TestHandler();
});