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
        // Assistant modal events
        document.getElementById('closeAssistantModalBtn')?.addEventListener('click', () => {
            this.closeAssistantModal();
        });

        // Quick action buttons
        document.querySelectorAll('.quick-action-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const prompt = btn.dataset.prompt;
                this.sendAssistantMessage(prompt);
            });
        });

        // Send message button
        document.getElementById('sendAssistantMessageBtn')?.addEventListener('click', () => {
            this.sendUserMessage();
        });

        // Enter key in input
        document.getElementById('assistantInput')?.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.sendUserMessage();
            }
        });
    }

    async getSuggestion(type, prompt) {
        if (!this.isInitialized) {
            this.showError('Asistan henüz hazır değil');
            return;
        }

        try {
            const communityId = window.communityManager?.currentCommunity?.id;
            if (!communityId) {
                this.showError('Topluluk bilgisi bulunamadı');
                return;
            }

            this.showLoading(type);

            const response = await fetch('/api/assistant/suggestions', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('friendzone_token')}`
                },
                body: JSON.stringify({
                    community_id: communityId,
                    type: type
                })
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

    async sendUserMessage() {
        const input = document.getElementById('assistantInput');
        const message = input.value.trim();

        if (!message) return;

        this.addMessageToChat(message, 'user');
        input.value = '';

        // Show loading state
        this.addMessageToChat('Düşünüyorum...', 'assistant', true);

        try {
            const response = await fetch('/api/assistant/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('friendzone_token')}`
                },
                body: JSON.stringify({
                    message: message,
                    community_id: window.communityManager?.currentCommunity?.id
                })
            });

            const data = await response.json();

            // Remove loading message
            this.removeLoadingMessage();

            if (response.ok) {
                this.addMessageToChat(data.response, 'assistant');
            } else {
                throw new Error(data.message || 'Yanıt alınamadı');
            }

        } catch (error) {
            console.error('GPT sohbet hatası:', error);
            this.removeLoadingMessage();
            this.addMessageToChat('Üzgünüm, şu anda yardımcı olamıyorum. Lütfen daha sonra tekrar deneyin.', 'assistant');
        }
    }

    async sendAssistantMessage(prompt) {
        this.addMessageToChat(prompt, 'user');

        // Show loading state
        this.addMessageToChat('Düşünüyorum...', 'assistant', true);

        try {
            const communityId = window.communityManager?.currentCommunity?.id;
            const response = await fetch('/api/assistant/suggestions', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('friendzone_token')}`
                },
                body: JSON.stringify({
                    community_id: communityId,
                    type: 'custom',
                    prompt: prompt
                })
            });

            const data = await response.json();

            // Remove loading message
            this.removeLoadingMessage();

            if (response.ok) {
                this.addMessageToChat(data.suggestion, 'assistant');
            } else {
                throw new Error(data.message || 'Yanıt alınamadı');
            }

        } catch (error) {
            console.error('GPT mesaj hatası:', error);
            this.removeLoadingMessage();
            this.addMessageToChat('Üzgünüm, bir hata oluştu. Lütfen daha sonra tekrar deneyin.', 'assistant');
        }
    }

    addMessageToChat(message, sender, isTemp = false) {
        const chatContainer = document.getElementById('assistantChat');
        const messageId = isTemp ? 'temp-message' : `message-${Date.now()}`;

        const messageHTML = `
            <div class="assistant-message ${isTemp ? 'temp' : ''}" id="${messageId}">
                <div class="message-avatar">
                    <i class="fas ${sender === 'user' ? 'fa-user' : 'fa-robot'}"></i>
                </div>
                <div class="message-content">
                    <div class="message-text">${this.formatMessage(message)}</div>
                </div>
            </div>
        `;

        if (isTemp) {
            // Replace existing temp message
            const existingTemp = document.getElementById('temp-message');
            if (existingTemp) {
                existingTemp.remove();
            }
        }

        chatContainer.insertAdjacentHTML('beforeend', messageHTML);
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    removeLoadingMessage() {
        const tempMessage = document.getElementById('temp-message');
        if (tempMessage) {
            tempMessage.remove();
        }
    }

    formatMessage(message) {
        // Convert line breaks to HTML
        return message.replace(/\n/g, '<br>');
    }

    showLoading(type) {
        const responseContainer = document.getElementById('assistantResponse');
        const typeLabels = {
            topic: 'sohbet konuları',
            icebreaker: 'buz kırıcı sorular',
            activity: 'etkinlik önerileri'
        };

        responseContainer.innerHTML = `
            <div class="response-loading">
                <div class="loading-spinner"></div>
                <p>${typeLabels[type] || 'öneriler'} hazırlanıyor...</p>
            </div>
        `;
    }

    showSuggestion(suggestion, type) {
        const responseContainer = document.getElementById('assistantResponse');
        const typeIcons = {
            topic: 'fa-comments',
            icebreaker: 'fa-snowflake',
            activity: 'fa-calendar-alt'
        };

        responseContainer.innerHTML = `
            <div class="response-suggestion">
                <div class="suggestion-header">
                    <i class="fas ${typeIcons[type] || 'fa-lightbulb'}"></i>
                    <h4>${this.getSuggestionTitle(type)}</h4>
                </div>
                <div class="suggestion-content">
                    ${this.formatSuggestion(suggestion, type)}
                </div>
                <div class="suggestion-actions">
                    <button class="btn btn-small btn-primary" onclick="gptAssistant.useSuggestion('${type}')">
                        <i class="fas fa-check"></i>
                        Kullan
                    </button>
                    <button class="btn btn-small btn-secondary" onclick="gptAssistant.regenerateSuggestion('${type}')">
                        <i class="fas fa-sync"></i>
                        Yeniden Üret
                    </button>
                </div>
            </div>
        `;
    }

    getSuggestionTitle(type) {
        const titles = {
            topic: 'Sohbet Konusu Önerileri',
            icebreaker: 'Buz Kırıcı Sorular',
            activity: 'Etkinlik Önerileri'
        };
        return titles[type] || 'AI Önerisi';
    }

    formatSuggestion(suggestion, type) {
        if (typeof suggestion === 'string') {
            // Format numbered lists and bullet points
            let formatted = suggestion.replace(/\n/g, '<br>');
            formatted = formatted.replace(/(\d+)\.\s/g, '<strong>$1.</strong> ');
            formatted = formatted.replace(/\*\s(.+?)(?=<br>|$)/g, '• <strong>$1</strong>');
            return formatted;
        }

        return 'Öneri formatı desteklenmiyor';
    }

    showFallbackSuggestion(type) {
        const fallbackSuggestions = {
            topic: `
                1. <strong>Gelecekteki Teknoloji Trendleri</strong><br>
                Yapay zeka, blockchain ve metaverse gibi teknolojilerin üniversite hayatımıza etkileri<br><br>
                
                2. <strong>Remote Çalışma Kültürü</strong><br>
                Pandemi sonrası iş hayatındaki değişimler ve yeni nesil çalışma modelleri<br><br>
                
                3. <strong>Sürdürülebilir Teknoloji</strong><br>
                Yeşil bilişim ve çevre dostu teknoloji çözümleri
            `,
            icebreaker: `
                • <strong>En sevdiğiniz ders hangisi ve neden?</strong><br>
                • <strong>Boş zamanlarınızda ne yapmaktan hoşlanırsınız?</strong><br>
                • <strong>Üniversite hayatınızın en unutulmaz anısı nedir?</strong><br>
                • <strong>Hangi alanda kendinizi geliştirmek istiyorsunuz?</strong><br>
                • <strong>Gelecek 5 yıl içinde neler başarmak istiyorsunuz?</strong>
            `,
            activity: `
                1. <strong>Haftalık Kodlama Buluşması</strong><br>
                Her hafta farklı bir programlama konsepti üzerine workshop<br><br>
                
                2. <strong>Proje Fikirleri Yarışması</strong><br>
                Takımlar halinde yenilikçi proje fikirleri geliştirme<br><br>
                
                3. <strong>Teknoloji Sohbetleri</strong><br>
                Alanında uzman konuklarla söyleşi ve networking
            `
        };

        const responseContainer = document.getElementById('assistantResponse');
        responseContainer.innerHTML = `
            <div class="response-suggestion fallback">
                <div class="suggestion-header">
                    <i class="fas fa-exclamation-triangle"></i>
                    <h4>Demo Önerisi - ${this.getSuggestionTitle(type)}</h4>
                </div>
                <div class="suggestion-content">
                    ${fallbackSuggestions[type]}
                </div>
                <div class="suggestion-note">
                    <i class="fas fa-info-circle"></i>
                    Gerçek API entegrasyonu ile kişiselleştirilmiş öneriler alacaksınız
                </div>
            </div>
        `;
    }

    useSuggestion(type) {
        const suggestionContent = document.querySelector('.suggestion-content').innerHTML;

        // Show success message
        this.showSuccess(`${this.getSuggestionTitle(type)} sohbet kutusuna eklendi!`);

        // In a real app, this would add the suggestion to the chat
        console.log('Suggestion used:', type, suggestionContent);
    }

    regenerateSuggestion(type) {
        this.getSuggestion(type);
    }

    closeAssistantModal() {
        document.getElementById('assistantModal').classList.remove('show');
    }

    showSuccess(message) {
        if (window.app && window.app.showNotification) {
            window.app.showNotification(message, 'success');
        } else {
            alert(message);
        }
    }

    showError(message) {
        if (window.app && window.app.showNotification) {
            window.app.showNotification(message, 'error');
        } else {
            alert('Hata: ' + message);
        }
    }
}

// Initialize GPT Assistant
document.addEventListener('DOMContentLoaded', () => {
    window.gptAssistant = new GPTAssistant();
});