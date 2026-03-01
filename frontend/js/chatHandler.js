// frontend/js/chatHandler.js

class ChatHandler {
    constructor() {
        this.socket = null;
        this.currentUser = null;
        currentRoom = null;
        this.onlineUsers = new Map();
        this.messageHistory = [];
        this.isConnected = false;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
    }

    /**
     * Socket.IO bağlantısını başlat
     */
    init(userData) {
        this.currentUser = userData;
        
        // Socket.IO sunucusuna bağlan
        this.socket = io({
            path: '/socket.io',
            transports: ['websocket', 'polling'],
            reconnection: true,
            reconnectionAttempts: this.maxReconnectAttempts,
            reconnectionDelay: 1000,
            reconnectionDelayMax: 5000,
            timeout: 20000
        });

        this.setupEventListeners();
    }

    /**
     * Socket.IO event listener'larını kur
     */
    setupEventListeners() {
        // Bağlantı olayları
        this.socket.on('connect', () => {
            console.log('✅ Socket.IO bağlantısı kuruldu');
            this.isConnected = true;
            this.reconnectAttempts = 0;
            this.showNotification('Sohbet sunucusuna bağlanıldı', 'success');
        });

        this.socket.on('disconnect', (reason) => {
            console.log('❌ Socket.IO bağlantısı koptu:', reason);
            this.isConnected = false;
            
            if (reason === 'io server disconnect') {
                // Sunucu tarafından koparıldı, yeniden bağlanma
                setTimeout(() => {
                    this.socket.connect();
                }, 1000);
            }
            
            this.showNotification('Sohbet sunucusuyla bağlantı kesildi', 'error');
        });

        this.socket.on('connect_error', (error) => {
            console.error('Socket.IO bağlantı hatası:', error);
            this.reconnectAttempts++;
            
            if (this.reconnectAttempts >= this.maxReconnectAttempts) {
                this.showNotification('Sunucuya bağlanılamıyor. Lütfen sayfayı yenileyin.', 'error');
            }
        });

        this.socket.on('reconnect', (attemptNumber) => {
            console.log(`🔄 Yeniden bağlanıldı (${attemptNumber}. deneme)`);
            this.showNotification('Sohbet sunucusuna yeniden bağlanıldı', 'success');
            
            // Yeniden bağlanınca tekrar odaya katıl
            if (this.currentRoom) {
                this.joinRoom(this.currentRoom);
            }
        });

        // Sohbet odası olayları
        this.socket.on('user_joined', (data) => {
            console.log('👤 Kullanıcı katıldı:', data);
            this.addSystemMessage(`${data.username} sohbete katıldı 🎉`);
            this.updateOnlineUsers(data);
        });

        this.socket.on('user_left', (data) => {
            console.log('👋 Kullanıcı ayrıldı:', data);
            this.addSystemMessage(`${data.username} sohbetten ayrıldı 👋`);
            this.updateOnlineUsers(data);
        });

        this.socket.on('new_message', (data) => {
            console.log('💬 Yeni mesaj:', data);
            this.displayMessage(data);
            this.messageHistory.push(data);
            
            // Kendi mesajım değilse bildirim göster
            if (data.user_id !== this.currentUser.id) {
                this.playNotificationSound();
                this.updateUnreadCount();
            }
        });

        this.socket.on('user_typing', (data) => {
            this.handleTypingIndicator(data);
        });

        this.socket.on('error', (data) => {
            console.error('Socket.IO hata:', data);
            this.showNotification(data.message || 'Bir hata oluştu', 'error');
        });

        // Mesaj silme/düzenleme olayları
        this.socket.on('message_edited', (data) => {
            this.updateMessage(data);
        });

        this.socket.on('message_deleted', (data) => {
            this.removeMessage(data.message_id);
        });

        this.socket.on('reaction_updated', (data) => {
            this.updateReaction(data);
        });
    }

    /**
     * Sohbet odasına katıl
     */
    joinRoom(roomId) {
        if (!this.socket || !this.isConnected) {
            console.warn('Socket bağlantısı yok');
            return;
        }

        this.currentRoom = roomId;
        
        this.socket.emit('join_chat', {
            room_id: roomId,
            user_id: this.currentUser.id,
            username: this.currentUser.name
        });

        console.log(`🚪 Odaya katılınıyor: ${roomId}`);
    }

    /**
     * Sohbet odasından ayrıl
     */
    leaveRoom(roomId) {
        if (!this.socket) return;

        this.socket.emit('leave_chat', {
            room_id: roomId,
            user_id: this.currentUser.id,
            username: this.currentUser.name
        });

        if (this.currentRoom === roomId) {
            this.currentRoom = null;
        }

        console.log(`🚪 Odadan ayrılındı: ${roomId}`);
    }

    /**
     * Mesaj gönder
     */
    sendMessage(content, messageType = 'text') {
        if (!this.socket || !this.currentRoom) {
            this.showNotification('Sohbet odasına bağlı değilsiniz', 'warning');
            return;
        }

        if (!content.trim()) {
            return;
        }

        const messageData = {
            room_id: this.currentRoom,
            user_id: this.currentUser.id,
            username: this.currentUser.name,
            content: content.trim(),
            message_type: messageType,
            timestamp: new Date().toISOString()
        };

        this.socket.emit('send_message', messageData);
        
        // Mesajı hemen kendi ekranında göster (optimistik UI)
        this.displayMessage({
            ...messageData,
            id: 'temp-' + Date.now(),
            sending: true
        });

        // Input'u temizle
        document.getElementById('message-input').value = '';
    }

    /**
     * Yazıyor bildirimi gönder
     */
    sendTyping(isTyping) {
        if (!this.socket || !this.currentRoom) return;

        this.socket.emit('typing', {
            room_id: this.currentRoom,
            user_id: this.currentUser.id,
            username: this.currentUser.name,
            is_typing: isTyping
        });
    }

    /**
     * Mesaj sil
     */
    deleteMessage(messageId) {
        if (!this.socket || !this.currentRoom) return;

        this.socket.emit('delete_message', {
            room_id: this.currentRoom,
            user_id: this.currentUser.id,
            message_id: messageId
        });
    }

    /**
     * Mesaj düzenle
     */
    editMessage(messageId, newContent) {
        if (!this.socket || !this.currentRoom) return;

        this.socket.emit('edit_message', {
            room_id: this.currentRoom,
            user_id: this.currentUser.id,
            message_id: messageId,
            content: newContent
        });
    }

    /**
     * Mesaja tepki ekle
     */
    addReaction(messageId, emoji) {
        if (!this.socket || !this.currentRoom) return;

        this.socket.emit('add_reaction', {
            room_id: this.currentRoom,
            user_id: this.currentUser.id,
            message_id: messageId,
            emoji: emoji
        });
    }

    /**
     * Mesajları göster
     */
    displayMessage(message) {
        const messagesContainer = document.getElementById('chat-messages');
        if (!messagesContainer) return;

        // Geçici mesajı bul ve kaldır
        if (message.id?.startsWith('temp-')) {
            const tempMessage = document.getElementById(`msg-${message.id}`);
            if (tempMessage) tempMessage.remove();
        }

        const messageElement = this.createMessageElement(message);
        messagesContainer.appendChild(messageElement);
        
        // Son mesaja kaydır
        messageElement.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }

    /**
     * Mesaj elementi oluştur
     */
    createMessageElement(message) {
        const isOwnMessage = message.user_id === this.currentUser.id;
        const div = document.createElement('div');
        div.id = `msg-${message.id}`;
        div.className = `message ${isOwnMessage ? 'own-message' : ''} ${message.sending ? 'sending' : ''}`;

        const time = new Date(message.timestamp).toLocaleTimeString('tr-TR', {
            hour: '2-digit',
            minute: '2-digit'
        });

        div.innerHTML = `
            <div class="message-avatar">
                <img src="${message.user_avatar || 'assets/default-avatar.png'}" alt="${message.username}">
            </div>
            <div class="message-content">
                <div class="message-header">
                    <span class="message-username">${message.username}</span>
                    <span class="message-time">${time}</span>
                </div>
                <div class="message-body">
                    ${this.formatMessageContent(message.content, message.message_type)}
                </div>
                <div class="message-footer">
                    <div class="message-reactions" id="reactions-${message.id}">
                        ${this.renderReactions(message.reactions)}
                    </div>
                    <div class="message-actions">
                        <button onclick="chatHandler.addReaction('${message.id}', '👍')" class="action-btn" title="Beğen">
                            👍
                        </button>
                        <button onclick="chatHandler.addReaction('${message.id}', '❤️')" class="action-btn" title="Kalp">
                            ❤️
                        </button>
                        <button onclick="chatHandler.addReaction('${message.id}', '😄')" class="action-btn" title="Gülücük">
                            😄
                        </button>
                        ${isOwnMessage ? `
                            <button onclick="chatHandler.editMessage('${message.id}')" class="action-btn" title="Düzenle">
                                ✏️
                            </button>
                            <button onclick="chatHandler.deleteMessage('${message.id}')" class="action-btn" title="Sil">
                                🗑️
                            </button>
                        ` : ''}
                    </div>
                </div>
            </div>
        `;

        return div;
    }

    /**
     * Mesaj içeriğini formatla
     */
    formatMessageContent(content, type) {
        if (type === 'image') {
            return `<img src="${content}" class="message-image" alt="Görsel">`;
        } else if (type === 'system') {
            return `<em>${content}</em>`;
        } else {
            // Linkleri tıklanabilir yap
            const urlRegex = /(https?:\/\/[^\s]+)/g;
            return content.replace(urlRegex, '<a href="$1" target="_blank" rel="noopener noreferrer">$1</a>');
        }
    }

    /**
     * Tepkileri render et
     */
    renderReactions(reactions) {
        if (!reactions || Object.keys(reactions).length === 0) return '';
        
        return Object.entries(reactions).map(([emoji, users]) => `
            <span class="reaction-badge" onclick="chatHandler.toggleReaction('${emoji}')">
                ${emoji} ${users.length}
            </span>
        `).join('');
    }

    /**
     * Sistem mesajı ekle
     */
    addSystemMessage(content) {
        const systemMessage = {
            id: 'system-' + Date.now(),
            user_id: 0,
            username: 'Sistem',
            content: content,
            message_type: 'system',
            timestamp: new Date().toISOString()
        };
        
        this.displayMessage(systemMessage);
    }

    /**
     * Yazıyor göstergesini yönet
     */
    handleTypingIndicator(data) {
        const indicator = document.getElementById('typing-indicator');
        if (!indicator) return;

        if (data.is_typing && data.user_id !== this.currentUser.id) {
            indicator.innerHTML = `${data.username} yazıyor...`;
            indicator.style.display = 'block';
            
            // 3 saniye sonra gizle (eğer yeni bildirim gelmezse)
            clearTimeout(this.typingTimeout);
            this.typingTimeout = setTimeout(() => {
                indicator.style.display = 'none';
            }, 3000);
        } else {
            indicator.style.display = 'none';
        }
    }

    /**
     * Online kullanıcı listesini güncelle
     */
    updateOnlineUsers(data) {
        const onlineList = document.getElementById('online-users');
        if (!onlineList) return;

        if (data.online_count !== undefined) {
            document.getElementById('online-count').textContent = data.online_count;
        }

        // Online kullanıcı listesini güncelle (opsiyonel)
        if (data.online_users) {
            // Online listeyi render et
        }
    }

    /**
     * Bildirim sesi çal
     */
    playNotificationSound() {
        // Sayfa görünür değilse ses çalma
        if (document.hidden) {
            const audio = new Audio('/assets/sounds/notification.mp3');
            audio.volume = 0.5;
            audio.play().catch(e => console.log('Ses çalınamadı:', e));
        }
    }

    /**
     * Okunmamış mesaj sayısını güncelle
     */
    updateUnreadCount() {
        if (document.hidden) {
            const count = parseInt(document.title.match(/\d+/) || 0) + 1;
            document.title = `(${count}) FriendZone`;
        }
    }

    /**
     * Bildirim göster
     */
    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.classList.add('fade-out');
            setTimeout(() => notification.remove(), 500);
        }, 3000);
    }

    /**
     * Bağlantıyı kapat
     */
    disconnect() {
        if (this.socket) {
            this.socket.disconnect();
            this.socket = null;
        }
        this.isConnected = false;
        this.currentRoom = null;
        console.log('Socket.IO bağlantısı kapatıldı');
    }
}

// Global chat handler instance'ı
const chatHandler = new ChatHandler();