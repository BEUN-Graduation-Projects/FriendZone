// frontend/js/personalityTest.js

class PersonalityTest {
    constructor() {
        this.currentQuestion = 0;
        this.answers = {};
        this.questions = [
            // Dışadönüklük (E) - İçedönüklük (I)
            { id: 1, text: "Yeni insanlarla tanışmaktan keyif alırım.", category: "ei", direction: "E" },
            { id: 2, text: "Kalabalık ortamlarda enerji kazanırım.", category: "ei", direction: "E" },
            { id: 3, text: "Sosyal etkinliklerde aktif rol almayı severim.", category: "ei", direction: "E" },
            { id: 4, text: "Yalnız vakit geçirmek benim için önemlidir.", category: "ei", direction: "I" },
            { id: 5, text: "Derin sohbetleri, yüzeysel muhabbetlere tercih ederim.", category: "ei", direction: "I" },
            { id: 6, text: "Tanımadığım insanlarla konuşmak beni yorar.", category: "ei", direction: "I" },

            // Duyumsama (S) - Sezgi (N)
            { id: 7, text: "Somut gerçeklere ve detaylara önem veririm.", category: "sn", direction: "S" },
            { id: 8, text: "Pratik ve işe yarar çözümleri tercih ederim.", category: "sn", direction: "S" },
            { id: 9, text: "Geçmiş deneyimlerime güvenirim.", category: "sn", direction: "S" },
            { id: 10, text: "Gelecekteki olasılıklar hakkında düşünmeyi severim.", category: "sn", direction: "N" },
            { id: 11, text: "Sembolik ve metaforik anlatımlar ilgimi çeker.", category: "sn", direction: "N" },
            { id: 12, text: "Yenilikçi ve yaratıcı fikirler üretmekten hoşlanırım.", category: "sn", direction: "N" },

            // Düşünme (T) - Hissetme (F)
            { id: 13, text: "Kararlarımı mantığıma dayanarak veririm.", category: "tf", direction: "T" },
            { id: 14, text: "Adalet ve objektiflik benim için önemlidir.", category: "tf", direction: "T" },
            { id: 15, text: "Eleştirel düşünme yeteneğim gelişmiştir.", category: "tf", direction: "T" },
            { id: 16, text: "Başkalarının duygularını önemserim.", category: "tf", direction: "F" },
            { id: 17, text: "Uyumlu ve işbirlikçi biriyimdir.", category: "tf", direction: "F" },
            { id: 18, text: "Empati yeteneğimin güçlü olduğunu düşünüyorum.", category: "tf", direction: "F" },

            // Yargılama (J) - Algılama (P)
            { id: 19, text: "Planlı ve programlı çalışmayı severim.", category: "jp", direction: "J" },
            { id: 20, text: "İşlerimi son dakikaya bırakmam.", category: "jp", direction: "J" },
            { id: 21, text: "Düzenli ve organize bir insanımdır.", category: "jp", direction: "J" },
            { id: 22, text: "Esnek ve spontane olmayı tercih ederim.", category: "jp", direction: "P" },
            { id: 23, text: "Yeni deneyimlere açığım, akışına bırakırım.", category: "jp", direction: "P" },
            { id: 24, text: "Kesin kararlar vermekte zorlanırım.", category: "jp", direction: "P" },
            { id: 25, text: "Rutin işler beni sıkar, çeşitlilik ararım.", category: "jp", direction: "P" }
        ];

        this.likertLabels = {
            1: { label: "Hiç Katılmıyorum", icon: "fa-times-circle", color: "#ef4444" },
            2: { label: "Katılmıyorum", icon: "fa-minus-circle", color: "#f97316" },
            3: { label: "Kararsızım", icon: "fa-circle", color: "#eab308" },
            4: { label: "Katılıyorum", icon: "fa-check-circle", color: "#22c55e" },
            5: { label: "Kesinlikle Katılıyorum", icon: "fa-check-double", color: "#3b82f6" }
        };

        this.init();
    }

    init() {
        this.renderQuestion();
        this.updateProgress();
        this.setupEventListeners();
        this.loadUserData();
    }

    loadUserData() {
        const user = JSON.parse(localStorage.getItem('friendzone_user'));
        if (user) {
            const userName = document.getElementById('userName');
            const userAvatar = document.getElementById('userAvatar');
            if (userName) userName.textContent = user.name || 'Kullanıcı';
            if (userAvatar) userAvatar.textContent = (user.name || 'K').charAt(0).toUpperCase();
        }
    }

    renderQuestion() {
        const container = document.getElementById('testQuestions');
        const question = this.questions[this.currentQuestion];
        const selectedValue = this.answers[this.currentQuestion] || 0;

        const options = [1, 2, 3, 4, 5].map(value => {
            const isSelected = selectedValue === value;
            const label = this.likertLabels[value];

            return `
                <div class="likert-option">
                    <input type="radio" 
                           name="q${this.currentQuestion}" 
                           id="q${this.currentQuestion}_${value}" 
                           value="${value}" 
                           ${isSelected ? 'checked' : ''}>
                    <label for="q${this.currentQuestion}_${value}" class="option-content">
                        <span class="option-value">${value}</span>
                        <span class="option-label">${label.label}</span>
                        <i class="fas ${label.icon}" style="color: ${label.color}; font-size: 24px; margin-top: 8px;"></i>
                    </label>
                    <div class="option-tooltip">${label.label}</div>
                </div>
            `;
        }).join('');

        container.innerHTML = `
            <div class="question-card">
                <div class="question-number">Soru ${this.currentQuestion + 1} / ${this.questions.length}</div>
                <h2 class="question-text">${question.text}</h2>
                <div class="likert-scale">
                    ${options}
                </div>
            </div>
        `;

        // Radio button değişimlerini dinle
        document.querySelectorAll(`input[name="q${this.currentQuestion}"]`).forEach(radio => {
            radio.addEventListener('change', (e) => {
                this.answers[this.currentQuestion] = parseInt(e.target.value);
                this.updateNavigation();
            });
        });
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
        const nextBtn = document.getElementById('nextBtn');
        const submitBtn = document.getElementById('submitBtn');

        prevBtn.disabled = this.currentQuestion === 0;

        if (this.currentQuestion === this.questions.length - 1) {
            nextBtn.style.display = 'none';
            submitBtn.style.display = 'flex';
        } else {
            nextBtn.style.display = 'flex';
            submitBtn.style.display = 'none';
        }

        this.updateNavigation();
    }

    updateNavigation() {
        const nextBtn = document.getElementById('nextBtn');
        const submitBtn = document.getElementById('submitBtn');

        if (nextBtn.style.display !== 'none') {
            nextBtn.disabled = !this.answers[this.currentQuestion];
        }

        if (submitBtn.style.display !== 'none') {
            submitBtn.disabled = Object.keys(this.answers).length !== this.questions.length;
        }
    }

    calculateMBTI() {
        let eScore = 0, iScore = 0, sScore = 0, nScore = 0, tScore = 0, fScore = 0, jScore = 0, pScore = 0;

        this.questions.forEach((question, index) => {
            const answer = this.answers[index];
            if (!answer) return;

            // 1-5 Likert skalasını -2 ile +2 arasına dönüştür
            const value = answer - 3;

            if (question.category === 'ei') {
                if (question.direction === 'E') {
                    eScore += value;
                } else {
                    iScore += value;
                }
            } else if (question.category === 'sn') {
                if (question.direction === 'S') {
                    sScore += value;
                } else {
                    nScore += value;
                }
            } else if (question.category === 'tf') {
                if (question.direction === 'T') {
                    tScore += value;
                } else {
                    fScore += value;
                }
            } else if (question.category === 'jp') {
                if (question.direction === 'J') {
                    jScore += value;
                } else {
                    pScore += value;
                }
            }
        });

        let mbti = '';
        mbti += (eScore > iScore) ? 'E' : 'I';
        mbti += (sScore > nScore) ? 'S' : 'N';
        mbti += (tScore > fScore) ? 'T' : 'F';
        mbti += (jScore > pScore) ? 'J' : 'P';

        return {
            type: mbti,
            scores: { eScore, iScore, sScore, nScore, tScore, fScore, jScore, pScore }
        };
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

            const result = this.calculateMBTI();

            const response = await fetch('http://localhost:5001/api/test/personality', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    user_id: user.id,
                    personality_type: result.type,
                    answers: this.answers
                })
            });

            const data = await response.json();

            if (response.ok && data.success) {
                user.personality_type = result.type;
                localStorage.setItem('friendzone_user', JSON.stringify(user));

                this.showResult(result.type, result.scores);
            } else {
                throw new Error(data.message || 'Test kaydedilemedi');
            }
        } catch (error) {
            console.error('Test hatası:', error);
            alert('Test gönderilirken bir hata oluştu: ' + error.message);
        } finally {
            this.setLoadingState(submitBtn, false);
        }
    }

    showResult(mbti, scores) {
        const descriptions = {
            'ISTJ': 'Mantıklı, düzenli ve güvenilir. Kurallara ve düzene önem verir, sorumluluk sahibidir.',
            'ISFJ': 'Koruyucu, sıcak kanlı ve fedakar. Başkalarına yardım etmekten mutlu olur, sadıktır.',
            'INFJ': 'Yaratıcı, idealist ve hassas. Derin ilişkiler kurmayı sever, başkalarına ilham verir.',
            'INTJ': 'Stratejik, mantıklı ve bağımsız. Karmaşık problemleri çözmekte iyidir, vizyon sahibidir.',
            'ISTP': 'Pratik, esnek ve gözlemci. Elleriyle çalışmayı ve sorun çözmeyi sever, maceraperesttir.',
            'ISFP': 'Sanatçı ruhlu, uyumlu ve maceraperest. Güzelliği takdir eder, duyarlıdır.',
            'INFP': 'İdealist, yaratıcı ve duygusal. Kendi değerlerine sıkı sıkıya bağlıdır, uyumludur.',
            'INTP': 'Analitik, yenilikçi ve meraklı. Teorik kavramları anlamayı sever, mantıklıdır.',
            'ESTP': 'Enerjik, mantıklı ve spontane. Anı yaşamayı sever, pratik zekaya sahiptir.',
            'ESFP': 'Canlı, eğlenceli ve arkadaş canlısı. İnsanları eğlendirmeyi sever, sosyaldir.',
            'ENFP': 'Yaratıcı, sosyal ve coşkulu. Yeni olasılıkları keşfetmeyi sever, ilham vericidir.',
            'ENTP': 'Yaratıcı, tartışmacı ve meraklı. Entelektüel zorlukları sever, yenilikçidir.',
            'ESTJ': 'Mantıklı, düzenli ve kararlı. Liderlik etmeyi ve organize etmeyi sever, güvenilirdir.',
            'ESFJ': 'Sıcak kanlı, popüler ve yardımsever. Başkalarını mutlu etmeyi sever, uyumludur.',
            'ENFJ': 'Karizmatik, idealist ve ilham verici. Başkalarına yardım etmeyi sever, lider ruhludur.',
            'ENTJ': 'Kararlı, mantıklı ve lider ruhlu. Büyük hedeflere ulaşmayı sever, stratejiktir.'
        };

        const resultHTML = `
            <div class="result-container">
                <div class="result-icon">
                    <i class="fas fa-brain"></i>
                </div>
                <h1 class="result-title">Kişilik Tipin: ${mbti}</h1>
                <p class="result-description">${descriptions[mbti] || 'Benzersiz kişilik özelliklerine sahipsin!'}</p>
                
                <div class="result-scores">
                    <h3>Kişilik Boyutları</h3>
                    <div class="scores-grid">
                        <div class="score-item">
                            <span class="score-label">Dışadönüklük</span>
                            <div class="score-bar">
                                <div class="score-fill" style="width: ${this.calculatePercentage(scores.eScore, scores.iScore, true)}%"></div>
                            </div>
                        </div>
                        <div class="score-item">
                            <span class="score-label">İçedönüklük</span>
                            <div class="score-bar">
                                <div class="score-fill" style="width: ${this.calculatePercentage(scores.iScore, scores.eScore, true)}%"></div>
                            </div>
                        </div>
                        <div class="score-item">
                            <span class="score-label">Duyumsama</span>
                            <div class="score-bar">
                                <div class="score-fill" style="width: ${this.calculatePercentage(scores.sScore, scores.nScore, true)}%"></div>
                            </div>
                        </div>
                        <div class="score-item">
                            <span class="score-label">Sezgi</span>
                            <div class="score-bar">
                                <div class="score-fill" style="width: ${this.calculatePercentage(scores.nScore, scores.sScore, true)}%"></div>
                            </div>
                        </div>
                        <div class="score-item">
                            <span class="score-label">Düşünme</span>
                            <div class="score-bar">
                                <div class="score-fill" style="width: ${this.calculatePercentage(scores.tScore, scores.fScore, true)}%"></div>
                            </div>
                        </div>
                        <div class="score-item">
                            <span class="score-label">Hissetme</span>
                            <div class="score-bar">
                                <div class="score-fill" style="width: ${this.calculatePercentage(scores.fScore, scores.tScore, true)}%"></div>
                            </div>
                        </div>
                        <div class="score-item">
                            <span class="score-label">Yargılama</span>
                            <div class="score-bar">
                                <div class="score-fill" style="width: ${this.calculatePercentage(scores.jScore, scores.pScore, true)}%"></div>
                            </div>
                        </div>
                        <div class="score-item">
                            <span class="score-label">Algılama</span>
                            <div class="score-bar">
                                <div class="score-fill" style="width: ${this.calculatePercentage(scores.pScore, scores.jScore, true)}%"></div>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="result-actions">
                    <a href="hobbies.html" class="btn btn-primary btn-large">
                        <i class="fas fa-arrow-right"></i> Hobi Testine Geç
                    </a>
                </div>
            </div>
        `;

        document.querySelector('.test-content').innerHTML = resultHTML;
    }

    calculatePercentage(score1, score2, isFirst) {
        const total = Math.abs(score1) + Math.abs(score2);
        if (total === 0) return 50;
        const percentage = (Math.abs(score1) / total) * 100;
        return Math.min(100, Math.max(0, percentage));
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

    setupEventListeners() {
        document.getElementById('prevBtn').addEventListener('click', () => this.previousQuestion());
        document.getElementById('nextBtn').addEventListener('click', () => this.nextQuestion());
        document.getElementById('submitBtn').addEventListener('click', () => this.submitTest());
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    window.personalityTest = new PersonalityTest();
});