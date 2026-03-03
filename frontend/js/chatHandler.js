// frontend/js/chatHandler.js

class ChatHandler {
    constructor() {
        this.socket = null;
        this.currentUser = null;
        this.currentRoom = null;
        this.onlineUsers = new Map();
        this.messageHistory = [];
        this.isConnected = false;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
    }

    init(userData) {
        this.currentUser = userData;

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

    setupEventListeners() {
        this.socket.on('connect', () => {
            console.log('✅ Socket.IO bağlantısı kuruldu');
            this.isConnected = true;
            this.reconnectAttempts = 0;
            this.showNotification('Sohbet sunucusuna bağlanıldı', 'success');
        });

        this.socket.on('disconnect', (reason) => {
            console.log('❌ Socket.IO bağlantısı koptu:', reason);
            this.isConnected = false;
            this.showNotification('Sohbet sunucusuyla bağlantı kesildi', 'error');
        });

        this.socket.on('user_joined', (data) => {
            this.addSystemMessage(`${data.username} sohbete katıldı 🎉`);
        });

        this.socket.on('user_left', (data) => {
            this.addSystemMessage(`${data.username} sohbetten ayrıldı 👋`);
        });

        this.socket.on('new_message', (data) => {
            this.displayMessage(data);
            this.messageHistory.push(data);

            if (data.user_id !== this.currentUser.id) {
                this.playNotificationSound();
            }
        });

        this.socket.on('user_typing', (data) => {
            this.handleTypingIndicator(data);
        });

        this.socket.on('error', (data) => {
            this.showNotification(data.message || 'Bir hata oluştu', 'error');
        });
    }

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

    leaveRoom(roomId) {
        if (!this.socket) return;

        this.socket.emit('leave_chat', {
            room_id: roomId,
            user_id: this.currentUser.id,
            username: this.currentUser.name
        });

        if (this.currentRoom === roomId) this.currentRoom = null;
    }

    sendMessage(content, messageType = 'text') {
        if (!this.socket || !this.currentRoom) {
            this.showNotification('Sohbet odasına bağlı değilsiniz', 'warning');
            return;
        }

        if (!content.trim()) return;

        const messageData = {
            room_id: this.currentRoom,
            user_id: this.currentUser.id,
            username: this.currentUser.name,
            content: content.trim(),
            message_type: messageType,
            timestamp: new Date().toISOString()
        };

        this.socket.emit('send_message', messageData);

        this.displayMessage({ ...messageData, id: 'temp-' + Date.now(), sending: true });

        const input = document.getElementById('message-input');
        if (input) input.value = '';
    }

    sendTyping(isTyping) {
        if (!this.socket || !this.currentRoom) return;

        this.socket.emit('typing', {
            room_id: this.currentRoom,
            user_id: this.currentUser.id,
            username: this.currentUser.name,
            is_typing: isTyping
        });
    }

    displayMessage(message) {
        const messagesContainer = document.getElementById('chat-messages');
        if (!messagesContainer) return;

        if (message.id?.startsWith('temp-')) {
            const tempMessage = document.getElementById(`msg-${message.id}`);
            if (tempMessage) tempMessage.remove();
        }

        const messageElement = this.createMessageElement(message);
        messagesContainer.appendChild(messageElement);
        messageElement.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }

    createMessageElement(message) {
        const isOwnMessage = message.user_id === this.currentUser.id;
        const div = document.createElement('div');
        div.id = `msg-${message.id}`;
        div.className = `message ${isOwnMessage ? 'own-message' : ''} ${message.sending ? 'sending' : ''}`;

        const time = new Date(message.timestamp).toLocaleTimeString('tr-TR', {
            hour: '2-digit', minute: '2-digit'
        });

        div.innerHTML = `
            <div class="message-avatar">
                <div class="avatar-small">${(message.username || '?').charAt(0).toUpperCase()}</div>
            </div>
            <div class="message-content">
                <div class="message-header">
                    <span class="message-username">${message.username}</span>
                    <span class="message-time">${time}</span>
                </div>
                <div class="message-body">${message.content}</div>
            </div>
        `;

        return div;
    }

    addSystemMessage(content) {
        this.displayMessage({
            id: 'system-' + Date.now(),
            user_id: 0,
            username: 'Sistem',
            content: content,
            message_type: 'system',
            timestamp: new Date().toISOString()
        });
    }

    handleTypingIndicator(data) {
        const indicator = document.getElementById('typing-indicator');
        if (!indicator) return;

        if (data.is_typing && data.user_id !== this.currentUser.id) {
            indicator.innerHTML = `${data.username} yazıyor...`;
            indicator.style.display = 'block';

            clearTimeout(this.typingTimeout);
            this.typingTimeout = setTimeout(() => {
                indicator.style.display = 'none';
            }, 3000);
        } else {
            indicator.style.display = 'none';
        }
    }

    playNotificationSound() {
        if (document.hidden) {
            const audio = new Audio('/assets/sounds/notification.mp3');
            audio.volume = 0.5;
            audio.play().catch(e => console.log('Ses çalınamadı:', e));
        }
    }

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

    disconnect() {
        if (this.socket) {
            this.socket.disconnect();
            this.socket = null;
        }
        this.isConnected = false;
        this.currentRoom = null;
    }
}

// Global chat handler instance
const chatHandler = new ChatHandler();