# User functions (Functional style - no OOP)
from db import execute_query, execute_insert
import random
import string

# ============ HELPER FUNCTIONS ============

def generate_codename():
    """Generate a random 8-character codename"""
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choices(chars, k=8))

# ============ USER FUNCTIONS ============

def create_user(username):
    """Create a new user"""
    query = "INSERT INTO users (username) VALUES (%s)"
    return execute_insert(query, (username,))

def get_user_by_id(user_id):
    """Get user by ID"""
    query = "SELECT * FROM users WHERE id = %s"
    return execute_query(query, (user_id,), fetch_one=True)

def get_user_by_username(username):
    """Get user by username"""
    query = "SELECT * FROM users WHERE username = %s"
    return execute_query(query, (username,), fetch_one=True)

def username_exists(username):
    """Check if username already exists"""
    user = get_user_by_username(username)
    return user is not None

def delete_user(user_id):
    """Delete a user"""
    query = "DELETE FROM users WHERE id = %s"
    execute_query(query, (user_id,))

# ============ ROOM FUNCTIONS ============

def create_room(room_type, creator_id):
    """Create a new room and add creator as member"""
    # Generate unique codename
    codename = generate_codename()
    while get_room_by_codename(codename):  # Ensure unique
        codename = generate_codename()
    
    # Create room with codename
    query = "INSERT INTO rooms (codename, type) VALUES (%s, %s)"
    room_id = execute_insert(query, (codename, room_type))
    
    # Add creator as member
    add_room_member(room_id, creator_id)
    
    return room_id, codename

def get_room_by_id(room_id):
    """Get room by ID"""
    query = "SELECT * FROM rooms WHERE id = %s"
    return execute_query(query, (room_id,), fetch_one=True)

def get_room_by_codename(codename):
    """Get room by codename"""
    query = "SELECT * FROM rooms WHERE codename = %s"
    return execute_query(query, (codename.upper(),), fetch_one=True)

def get_rooms_by_user(user_id):
    """Get all rooms for a user"""
    query = """
        SELECT r.* FROM rooms r
        JOIN room_members rm ON r.id = rm.room_id
        WHERE rm.user_id = %s
        ORDER BY r.created_at DESC
    """
    return execute_query(query, (user_id,), fetch_all=True)

def room_exists(room_id):
    """Check if room exists"""
    room = get_room_by_id(room_id)
    return room is not None

# ============ ROOM MEMBER FUNCTIONS ============

def add_room_member(room_id, user_id):
    """Add user to room"""
    query = "INSERT INTO room_members (room_id, user_id) VALUES (%s, %s) ON CONFLICT DO NOTHING"
    execute_query(query, (room_id, user_id))

def remove_room_member(room_id, user_id):
    """Remove user from room"""
    query = "DELETE FROM room_members WHERE room_id = %s AND user_id = %s"
    execute_query(query, (room_id, user_id))

def is_room_member(room_id, user_id):
    """Check if user is member of room"""
    query = "SELECT 1 FROM room_members WHERE room_id = %s AND user_id = %s"
    result = execute_query(query, (room_id, user_id), fetch_one=True)
    return result is not None

def get_room_members(room_id):
    """Get all members of a room"""
    query = """
        SELECT u.* FROM users u
        JOIN room_members rm ON u.id = rm.user_id
        WHERE rm.room_id = %s
    """
    return execute_query(query, (room_id,), fetch_all=True)

def get_room_member_count(room_id):
    """Get member count of a room"""
    query = "SELECT COUNT(*) as count FROM room_members WHERE room_id = %s"
    result = execute_query(query, (room_id,), fetch_one=True)
    return result['count'] if result else 0

# ============ MESSAGE FUNCTIONS ============

def create_message(room_id, sender_id, content):
    """Create a new message"""
    query = "INSERT INTO messages (room_id, sender_id, content) VALUES (%s, %s, %s)"
    return execute_insert(query, (room_id, sender_id, content))

def get_messages_by_room(room_id, limit=50):
    """Get messages in a room"""
    query = """
        SELECT m.*, u.username as sender_name
        FROM messages m
        JOIN users u ON m.sender_id = u.id
        WHERE m.room_id = %s
        ORDER BY m.created_at ASC
        LIMIT %s
    """
    return execute_query(query, (room_id, limit), fetch_all=True)

def get_message_by_id(message_id):
    """Get message by ID"""
    query = """
        SELECT m.*, u.username as sender_name
        FROM messages m
        JOIN users u ON m.sender_id = u.id
        WHERE m.id = %s
    """
    return execute_query(query, (message_id,), fetch_one=True)
