// frontend/js/gptAssistant.js

class GPTAssistant {
    constructor() {
        this.isInitialized = false;
        this.init();
    }

    async init() {
        this.setupEventListeners();
        this.isInitialized = true;
        console.log('GPT Assistant initialized');
    }

    setupEventListeners() {
        const closeBtn = document.getElementById('closeAssistantModalBtn');
        if (closeBtn) closeBtn.addEventListener('click', () => this.closeAssistantModal());

        const sendBtn = document.getElementById('sendAssistantMessageBtn');
        if (sendBtn) sendBtn.addEventListener('click', () => this.sendUserMessage());

        const assistantInput = document.getElementById('assistantInput');
        if (assistantInput) {
            assistantInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') this.sendUserMessage();
            });
        }

        document.querySelectorAll('.quick-action-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const prompt = btn.dataset.prompt;
                this.sendAssistantMessage(prompt);
            });
        });
    }

    async getSuggestion(type) {
        if (!this.isInitialized) return this.showFallbackSuggestion(type);

        const communityId = window.communityManager?.currentCommunity?.id;
        if (!communityId) return this.showError('Topluluk bilgisi bulunamadı');

        this.showLoading(type);

        try {
            const token = localStorage.getItem('friendzone_token');
            const response = await fetch('/api/assistant/suggestions', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({ community_id: communityId, type: type })
            });

            const data = await response.json();

            if (response.ok) {
                this.showSuggestion(data.suggestion, type);
            } else {
                throw new Error(data.message || 'Öneri alınamadı');
            }
        } catch (error) {
            console.error('GPT öneri hatası:', error);
            this.showFallbackSuggestion(type);
        }
    }

    sendUserMessage() {
        const input = document.getElementById('assistantInput');
        if (!input) return;

        const message = input.value.trim();
        if (!message) return;

        this.addMessageToChat(message, 'user');
        input.value = '';

        this.addMessageToChat('Düşünüyorum...', 'assistant', true);

        setTimeout(() => {
            this.removeLoadingMessage();
            this.addMessageToChat('Üzgünüm, şu anda demo moddayım. Gerçek API entegrasyonu ile cevap vereceğim.', 'assistant');
        }, 1500);
    }

    sendAssistantMessage(prompt) {
        this.addMessageToChat(prompt, 'user');
        this.addMessageToChat('Düşünüyorum...', 'assistant', true);

        setTimeout(() => {
            this.removeLoadingMessage();
            this.addMessageToChat('Bu bir demo yanıtıdır. Gerçek GPT entegrasyonu için OpenAI API anahtarı gereklidir.', 'assistant');
        }, 1500);
    }

    addMessageToChat(message, sender, isTemp = false) {
        const chatContainer = document.getElementById('assistantChat');
        if (!chatContainer) return;

        const messageId = isTemp ? 'temp-message' : `message-${Date.now()}`;

        const messageHTML = `
            <div class="assistant-message ${isTemp ? 'temp' : ''}" id="${messageId}">
                <div class="message-avatar"><i class="fas ${sender === 'user' ? 'fa-user' : 'fa-robot'}"></i></div>
                <div class="message-content"><div class="message-text">${message}</div></div>
            </div>
        `;

        if (isTemp) {
            const existingTemp = document.getElementById('temp-message');
            if (existingTemp) existingTemp.remove();
        }

        chatContainer.insertAdjacentHTML('beforeend', messageHTML);
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    removeLoadingMessage() {
        const tempMessage = document.getElementById('temp-message');
        if (tempMessage) tempMessage.remove();
    }

    showLoading(type) {
        const responseContainer = document.getElementById('assistantResponse');
        if (!responseContainer) return;

        responseContainer.innerHTML = `
            <div class="response-loading">
                <div class="loading-spinner"></div>
                <p>Öneriler hazırlanıyor...</p>
            </div>
        `;
    }

    showSuggestion(suggestion, type) {
        const responseContainer = document.getElementById('assistantResponse');
        if (!responseContainer) return;

        responseContainer.innerHTML = `
            <div class="response-suggestion">
                <div class="suggestion-header">
                    <i class="fas fa-lightbulb"></i>
                    <h4>AI Önerisi</h4>
                </div>
                <div class="suggestion-content">${suggestion.replace(/\n/g, '<br>')}</div>
            </div>
        `;
    }

    showFallbackSuggestion(type) {
        const responseContainer = document.getElementById('assistantResponse');
        if (!responseContainer) return;

        const fallbacks = {
            topic: '1. Gelecekteki teknoloji trendleri<br>2. Uzaktan çalışma kültürü<br>3. Sürdürülebilir yaşam',
            icebreaker: '1. En sevdiğin kitap?<br>2. Hangi dili öğrenmek istersin?<br>3. Hayalindeki meslek?',
            activity: '1. Haftalık kodlama buluşması<br>2. Proje fikirleri yarışması<br>3. Teknoloji söyleşileri'
        };

        responseContainer.innerHTML = `
            <div class="response-suggestion">
                <div class="suggestion-header">
                    <i class="fas fa-exclamation-triangle"></i>
                    <h4>Demo Önerisi</h4>
                </div>
                <div class="suggestion-content">${fallbacks[type] || fallbacks.topic}</div>
            </div>
        `;
    }

    showError(message) {
        if (window.app?.showNotification) window.app.showNotification(message, 'error');
        else alert('Hata: ' + message);
    }

    closeAssistantModal() {
        const modal = document.getElementById('assistantModal');
        if (modal) modal.classList.remove('show');
    }
}

// Initialize GPT Assistant
document.addEventListener('DOMContentLoaded', () => {
    window.gptAssistant = new GPTAssistant();
});