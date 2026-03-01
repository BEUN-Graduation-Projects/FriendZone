# backend/socket_events.py

from flask_socketio import SocketIO, emit, join_room, leave_room
from flask import request
import logging

logger = logging.getLogger(__name__)

socketio = SocketIO(cors_allowed_origins="*")


@socketio.on('connect')
def handle_connect():
    """Client bağlandığında"""
    logger.info(f"Client connected: {request.sid}")


@socketio.on('disconnect')
def handle_disconnect():
    """Client ayrıldığında"""
    logger.info(f"Client disconnected: {request.sid}")


@socketio.on('join_chat')
def handle_join_chat(data):
    """Kullanıcı sohbet odasına katılır"""
    try:
        room_id = data['room_id']
        user_id = data['user_id']
        username = data['username']

        # Odaya katıl
        join_room(room_id)

        # Chat service'i güncelle
        from backend.services.chat_service import chat_service
        online_count = chat_service.user_joined(room_id, user_id, request.sid)

        # Diğer kullanıcılara bildir
        emit('user_joined', {
            'user_id': user_id,
            'username': username,
            'online_count': online_count
        }, room=room_id, include_self=False)

        logger.info(f"User {username} joined room {room_id}")

    except Exception as e:
        logger.error(f"Join chat error: {str(e)}")


@socketio.on('leave_chat')
def handle_leave_chat(data):
    """Kullanıcı sohbet odasından ayrılır"""
    try:
        room_id = data['room_id']
        user_id = data['user_id']
        username = data['username']

        # Odadan ayrıl
        leave_room(room_id)

        # Chat service'i güncelle
        from backend.services.chat_service import chat_service
        online_count = chat_service.user_left(room_id, user_id)

        # Diğer kullanıcılara bildir
        emit('user_left', {
            'user_id': user_id,
            'username': username,
            'online_count': online_count
        }, room=room_id, include_self=False)

        logger.info(f"User {username} left room {room_id}")

    except Exception as e:
        logger.error(f"Leave chat error: {str(e)}")


@socketio.on('send_message')
def handle_send_message(data):
    """Mesaj gönder"""
    try:
        room_id = data['room_id']
        user_id = data['user_id']
        username = data['username']
        content = data['content']
        message_type = data.get('message_type', 'text')

        # Mesajı veritabanına kaydet
        from backend.models.chat_model import ChatMessage
        from backend import db

        message = ChatMessage(
            community_id=room_id,
            user_id=user_id,
            content=content,
            message_type=message_type
        )
        db.session.add(message)
        db.session.commit()

        # Mesajı odadaki herkese gönder
        emit('new_message', {
            'id': message.id,
            'user_id': user_id,
            'username': username,
            'content': content,
            'message_type': message_type,
            'timestamp': message.timestamp.isoformat()
        }, room=room_id)

    except Exception as e:
        logger.error(f"Send message error: {str(e)}")
        emit('error', {'message': 'Mesaj gönderilemedi'})


@socketio.on('typing')
def handle_typing(data):
    """Yazıyor bildirimi"""
    room_id = data['room_id']
    user_id = data['user_id']
    username = data['username']
    is_typing = data['is_typing']

    emit('user_typing', {
        'user_id': user_id,
        'username': username,
        'is_typing': is_typing
    }, room=room_id, include_self=False)