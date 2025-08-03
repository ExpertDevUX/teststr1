import os
import json
import logging
from datetime import datetime, timezone
from flask import session
from flask_socketio import emit, join_room, leave_room, disconnect
from app import db, socketio
from models import User, Stream, ChatMessage, AdminSettings

# Gemini AI functionality - disabled for VPS compatibility
GEMINI_AVAILABLE = False
gemini_client = None

if os.environ.get("GEMINI_API_KEY"):
    print("Warning: GEMINI_API_KEY found but google-genai package not installed.")
    print("To enable AI bot features, install: pip install google-genai")
else:
    print("Info: AI bot features disabled. Set GEMINI_API_KEY to enable (requires google-genai package).")

# Chat room management
active_users = {}  # {room_id: {user_id: {username, joined_at}}}
chat_stats = {}    # {room_id: {total_messages, active_users}}

class ChatManager:
    def __init__(self):
        self.banned_words = [
            "spam", "scam", "fake", "bot", "hack", "cheat", 
            # Add more moderation words as needed
        ]
        self.ai_bot_enabled = True
        self.auto_moderation = True
    
    def is_message_appropriate(self, message):
        """Check if message contains banned words or inappropriate content"""
        message_lower = message.lower()
        return not any(word in message_lower for word in self.banned_words)
    
    def moderate_with_ai(self, message, username):
        """Use Gemini AI to moderate chat messages (currently disabled)"""
        # AI moderation disabled for VPS compatibility
        # To enable: install google-genai package and set GEMINI_API_KEY
        return True, ""
    
    def generate_ai_response(self, message, stream_title=""):
        """Generate AI bot response for user questions (currently disabled)"""
        # AI responses disabled for VPS compatibility
        # To enable: install google-genai package and set GEMINI_API_KEY
        return None

# Initialize chat manager
chat_manager = ChatManager()

# SocketIO Events
@socketio.on('connect')
def handle_connect():
    """Handle user connection to chat"""
    user_id = session.get('user_id')
    username = session.get('username', 'Anonymous')
    
    if user_id:
        emit('connection_status', {
            'status': 'connected',
            'user_id': user_id,
            'username': username,
            'timestamp': datetime.now(timezone.utc).isoformat()
        })
        logging.info(f"User {username} connected to chat")

@socketio.on('disconnect')
def handle_disconnect():
    """Handle user disconnection from chat"""
    user_id = session.get('user_id')
    username = session.get('username', 'Anonymous')
    
    # Remove user from all active chat rooms
    for room_id in list(active_users.keys()):
        if user_id in active_users[room_id]:
            del active_users[room_id][user_id]
            if not active_users[room_id]:  # Remove empty rooms
                del active_users[room_id]
    
    logging.info(f"User {username} disconnected from chat")

@socketio.on('join_stream_chat')
def handle_join_stream_chat(data):
    """Handle user joining a stream's chat room"""
    try:
        stream_id = data.get('stream_id')
        user_id = session.get('user_id')
        username = session.get('username', 'Anonymous')
        
        if not stream_id:
            emit('error', {'message': 'Stream ID required'})
            return
        
        # Verify stream exists
        stream = Stream.query.get(stream_id)
        if not stream:
            emit('error', {'message': 'Stream not found'})
            return
        
        room_name = f"stream_{stream_id}"
        join_room(room_name)
        
        # Track active user
        if room_name not in active_users:
            active_users[room_name] = {}
        
        active_users[room_name][user_id] = {
            'username': username,
            'joined_at': datetime.now(timezone.utc).isoformat()
        }
        
        # Update chat stats
        if room_name not in chat_stats:
            chat_stats[room_name] = {'total_messages': 0, 'active_users': 0}
        
        chat_stats[room_name]['active_users'] = len(active_users[room_name])
        
        # Notify room about new user
        emit('user_joined', {
            'username': username,
            'user_count': len(active_users[room_name]),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }, room=room_name)
        
        # Send recent chat messages to new user
        recent_messages = ChatMessage.query.filter_by(stream_id=stream_id)\
                                         .order_by(ChatMessage.timestamp.desc())\
                                         .limit(50).all()
        
        messages_data = []
        for msg in reversed(recent_messages):
            messages_data.append({
                'id': msg.id,
                'username': msg.username,
                'message': msg.message,
                'timestamp': msg.timestamp.isoformat(),
                'is_moderator': msg.is_moderator,
                'is_broadcaster': msg.is_broadcaster
            })
        
        emit('chat_history', {'messages': messages_data})
        
        logging.info(f"User {username} joined stream {stream_id} chat")
        
    except Exception as e:
        logging.error(f"Error joining stream chat: {e}")
        emit('error', {'message': 'Failed to join chat'})

@socketio.on('leave_stream_chat')
def handle_leave_stream_chat(data):
    """Handle user leaving a stream's chat room"""
    try:
        stream_id = data.get('stream_id')
        user_id = session.get('user_id')
        username = session.get('username', 'Anonymous')
        
        if not stream_id:
            return
        
        room_name = f"stream_{stream_id}"
        leave_room(room_name)
        
        # Remove user from active users
        if room_name in active_users and user_id in active_users[room_name]:
            del active_users[room_name][user_id]
            
            # Update user count
            if room_name in chat_stats:
                chat_stats[room_name]['active_users'] = len(active_users[room_name])
            
            # Notify room about user leaving
            emit('user_left', {
                'username': username,
                'user_count': len(active_users[room_name]),
                'timestamp': datetime.now(timezone.utc).isoformat()
            }, room=room_name)
        
        logging.info(f"User {username} left stream {stream_id} chat")
        
    except Exception as e:
        logging.error(f"Error leaving stream chat: {e}")

@socketio.on('send_chat_message')
def handle_send_chat_message(data):
    """Handle sending a chat message"""
    try:
        stream_id = data.get('stream_id')
        message = data.get('message', '').strip()
        user_id = session.get('user_id')
        username = session.get('username', 'Anonymous')
        
        if not stream_id or not message:
            emit('error', {'message': 'Stream ID and message required'})
            return
        
        if len(message) > 500:
            emit('error', {'message': 'Message too long (max 500 characters)'})
            return
        
        # Check if message is appropriate
        if not chat_manager.is_message_appropriate(message):
            emit('error', {'message': 'Message contains inappropriate content'})
            return
        
        # Get user info
        user = User.query.get(user_id) if user_id else None
        is_broadcaster = user and user.is_broadcaster if user else False
        is_moderator = user and getattr(user, 'is_moderator', False) if user else False
        
        # AI moderation (currently disabled)
        is_appropriate, ai_reason = chat_manager.moderate_with_ai(message, username)
        if not is_appropriate:
            emit('error', {'message': f'Message blocked: {ai_reason}'})
            return
        
        # Save message to database
        chat_message = ChatMessage(
            stream_id=stream_id,
            user_id=user_id,
            username=username,
            message=message,
            is_broadcaster=is_broadcaster,
            is_moderator=is_moderator,
            timestamp=datetime.now(timezone.utc)
        )
        
        db.session.add(chat_message)
        db.session.commit()
        
        # Update chat stats
        room_name = f"stream_{stream_id}"
        if room_name in chat_stats:
            chat_stats[room_name]['total_messages'] += 1
        
        # Broadcast message to room
        message_data = {
            'id': chat_message.id,
            'username': username,
            'message': message,
            'timestamp': chat_message.timestamp.isoformat(),
            'is_broadcaster': is_broadcaster,
            'is_moderator': is_moderator
        }
        
        emit('new_chat_message', message_data, room=room_name)
        
        # Generate AI response if needed (currently disabled)
        ai_response = chat_manager.generate_ai_response(message, "")
        if ai_response:
            # Send AI bot response
            bot_message = ChatMessage(
                stream_id=stream_id,
                user_id=None,
                username="StrophenBot",
                message=ai_response,
                is_broadcaster=False,
                is_moderator=True,
                timestamp=datetime.now(timezone.utc)
            )
            
            db.session.add(bot_message)
            db.session.commit()
            
            bot_message_data = {
                'id': bot_message.id,
                'username': "StrophenBot",
                'message': ai_response,
                'timestamp': bot_message.timestamp.isoformat(),
                'is_broadcaster': False,
                'is_moderator': True,
                'is_bot': True
            }
            
            emit('new_chat_message', bot_message_data, room=room_name)
        
        logging.info(f"Chat message sent by {username} in stream {stream_id}")
        
    except Exception as e:
        logging.error(f"Error sending chat message: {e}")
        emit('error', {'message': 'Failed to send message'})

@socketio.on('delete_chat_message')
def handle_delete_chat_message(data):
    """Handle deleting a chat message (moderators only)"""
    try:
        message_id = data.get('message_id')
        user_id = session.get('user_id')
        
        if not message_id or not user_id:
            emit('error', {'message': 'Message ID required'})
            return
        
        # Check if user is moderator or broadcaster
        user = User.query.get(user_id)
        if not user or (not user.is_broadcaster and not getattr(user, 'is_moderator', False)):
            emit('error', {'message': 'Insufficient permissions'})
            return
        
        # Find and delete message
        message = ChatMessage.query.get(message_id)
        if message:
            stream_id = message.stream_id
            db.session.delete(message)
            db.session.commit()
            
            # Notify room about deleted message
            room_name = f"stream_{stream_id}"
            emit('message_deleted', {
                'message_id': message_id,
                'deleted_by': user.username,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }, room=room_name)
            
            logging.info(f"Message {message_id} deleted by {user.username}")
        else:
            emit('error', {'message': 'Message not found'})
            
    except Exception as e:
        logging.error(f"Error deleting chat message: {e}")
        emit('error', {'message': 'Failed to delete message'})

@socketio.on('get_chat_stats')
def handle_get_chat_stats(data):
    """Get chat statistics for a stream"""
    try:
        stream_id = data.get('stream_id')
        if not stream_id:
            emit('error', {'message': 'Stream ID required'})
            return
        
        room_name = f"stream_{stream_id}"
        stats = chat_stats.get(room_name, {'total_messages': 0, 'active_users': 0})
        
        # Get total message count from database
        total_messages = ChatMessage.query.filter_by(stream_id=stream_id).count()
        stats['total_messages'] = total_messages
        
        emit('chat_stats', stats)
        
    except Exception as e:
        logging.error(f"Error getting chat stats: {e}")
        emit('error', {'message': 'Failed to get chat statistics'})