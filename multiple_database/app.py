from flask import Flask, request, jsonify, session, redirect, url_for, render_template
from functools import wraps
from config import SECRET_KEY
import models

app = Flask(__name__)
app.secret_key = SECRET_KEY

# ============ HELPER FUNCTIONS ============

def json_response(success, message, data=None, status=200):
    """Create standardized JSON response"""
    response = {
        'success': success,
        'message': message
    }
    if data is not None:
        response['data'] = data
    return jsonify(response), status

def login_required(f):
    """Decorator to check if user is logged in"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            if request.is_json:
                return json_response(False, 'Login required', status=401)
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

def get_current_user():
    """Get current logged in user"""
    if 'user_id' in session:
        return models.get_user_by_id(session['user_id'])
    return None

# ============ PAGE ROUTES ============

@app.route('/')
def index():
    """Landing page - Login/Register"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/dashboard')
@login_required
def dashboard():
    """Dashboard page"""
    user = get_current_user()
    rooms = models.get_rooms_by_user(session['user_id'])
    return render_template('dashboard.html', user=user, rooms=rooms)

@app.route('/room/<int:room_id>')
@login_required
def chat_room(room_id):
    """Chat room page"""
    # Check if room exists
    room = models.get_room_by_id(room_id)
    if not room:
        return redirect(url_for('dashboard'))
    
    # Check if user is member
    if not models.is_room_member(room_id, session['user_id']):
        return redirect(url_for('dashboard'))
    
    user = get_current_user()
    messages = models.get_messages_by_room(room_id)
    members = models.get_room_members(room_id)
    
    return render_template('chat.html', user=user, room=room, messages=messages, members=members)

# ============ AUTH API ============

@app.route('/api/register', methods=['POST'])
def api_register():
    """Register new user"""
    data = request.get_json()
    
    if not data or 'username' not in data:
        return json_response(False, 'Username is required', status=400)
    
    username = data['username'].strip().lower()
    
    if len(username) < 3:
        return json_response(False, 'Username must be at least 3 characters', status=400)
    
    if models.username_exists(username):
        return json_response(False, 'Username already exists', status=400)
    
    try:
        user_id = models.create_user(username)
        session['user_id'] = user_id
        session['username'] = username
        
        return json_response(True, 'Registration successful', {
            'user_id': user_id,
            'username': username
        })
    except Exception as e:
        return json_response(False, str(e), status=500)

@app.route('/api/login', methods=['POST'])
def api_login():
    """Login with username"""
    data = request.get_json()
    
    if not data or 'username' not in data:
        return json_response(False, 'Username is required', status=400)
    
    username = data['username'].strip().lower()
    user = models.get_user_by_username(username)
    
    if not user:
        return json_response(False, 'Username not found', status=404)
    
    session['user_id'] = user['id']
    session['username'] = user['username']
    
    return json_response(True, 'Login successful', {
        'user_id': user['id'],
        'username': user['username']
    })

@app.route('/api/logout', methods=['POST'])
def api_logout():
    """Logout user"""
    session.clear()
    return json_response(True, 'Logout successful')

@app.route('/logout')
def logout():
    """Logout and redirect to index"""
    session.clear()
    return redirect(url_for('index'))

# ============ ROOM API ============

@app.route('/api/rooms', methods=['GET'])
@login_required
def api_get_my_rooms():
    """Get rooms for current user"""
    rooms = models.get_rooms_by_user(session['user_id'])
    rooms_list = [dict(room) for room in rooms] if rooms else []
    return json_response(True, 'Rooms fetched', rooms_list)

@app.route('/api/rooms', methods=['POST'])
@login_required
def api_create_room():
    """Create a new room"""
    data = request.get_json()
    
    room_type = data.get('type', 'group')
    if room_type not in ['dm', 'group']:
        return json_response(False, 'Room type must be dm or group', status=400)
    
    try:
        room_id, codename = models.create_room(room_type, session['user_id'])
        
        return json_response(True, 'Room created', {
            'room_id': room_id,
            'codename': codename,
            'type': room_type,
            'message': f'Share this code with others: {codename}'
        })
    except Exception as e:
        return json_response(False, str(e), status=500)

@app.route('/api/rooms/join', methods=['POST'])
@login_required
def api_join_room():
    """Join a room by codename"""
    data = request.get_json()
    
    if not data or 'codename' not in data:
        return json_response(False, 'Codename is required', status=400)
    
    codename = data['codename'].strip().upper()
    
    # Check if room exists by codename
    room = models.get_room_by_codename(codename)
    if not room:
        return json_response(False, 'Room not found', status=404)
    
    room_id = room['id']
    
    # Check if already member
    if models.is_room_member(room_id, session['user_id']):
        return json_response(False, 'Already a member of this room', status=400)
    
    # Check DM room limit
    if room['type'] == 'dm':
        member_count = models.get_room_member_count(room_id)
        if member_count >= 2:
            return json_response(False, 'DM room is full (max 2 members)', status=400)
    
    try:
        models.add_room_member(room_id, session['user_id'])
        return json_response(True, 'Joined room successfully', {
            'room_id': room_id,
            'codename': room['codename']
        })
    except Exception as e:
        return json_response(False, str(e), status=500)

@app.route('/api/rooms/<int:room_id>/leave', methods=['POST'])
@login_required
def api_leave_room(room_id):
    """Leave a room"""
    if not models.is_room_member(room_id, session['user_id']):
        return json_response(False, 'Not a member of this room', status=400)
    
    try:
        models.remove_room_member(room_id, session['user_id'])
        return json_response(True, 'Left room successfully')
    except Exception as e:
        return json_response(False, str(e), status=500)

@app.route('/api/rooms/<int:room_id>/members', methods=['GET'])
@login_required
def api_get_room_members(room_id):
    """Get room members"""
    if not models.is_room_member(room_id, session['user_id']):
        return json_response(False, 'Not a member of this room', status=403)
    
    members = models.get_room_members(room_id)
    members_list = [dict(m) for m in members] if members else []
    return json_response(True, 'Members fetched', members_list)

# ============ MESSAGE API ============

@app.route('/api/rooms/<int:room_id>/messages', methods=['GET'])
@login_required
def api_get_messages(room_id):
    """Get messages in a room"""
    if not models.is_room_member(room_id, session['user_id']):
        return json_response(False, 'Not a member of this room', status=403)
    
    messages = models.get_messages_by_room(room_id)
    
    # Convert datetime to string for JSON
    messages_list = []
    for msg in messages:
        msg_dict = dict(msg)
        msg_dict['created_at'] = msg_dict['created_at'].isoformat() if msg_dict['created_at'] else None
        messages_list.append(msg_dict)
    
    return json_response(True, 'Messages fetched', messages_list)

@app.route('/api/rooms/<int:room_id>/messages', methods=['POST'])
@login_required
def api_send_message(room_id):
    """Send a message to a room"""
    if not models.is_room_member(room_id, session['user_id']):
        return json_response(False, 'Not a member of this room', status=403)
    
    data = request.get_json()
    
    if not data or 'content' not in data:
        return json_response(False, 'Message content is required', status=400)
    
    content = data['content'].strip()
    if not content:
        return json_response(False, 'Message cannot be empty', status=400)
    
    try:
        message_id = models.create_message(room_id, session['user_id'], content)
        message = models.get_message_by_id(message_id)
        
        msg_dict = dict(message)
        msg_dict['created_at'] = msg_dict['created_at'].isoformat() if msg_dict['created_at'] else None
        
        return json_response(True, 'Message sent', msg_dict)
    except Exception as e:
        return json_response(False, str(e), status=500)

# ============ USER API ============

@app.route('/api/user', methods=['GET'])
@login_required
def api_get_current_user():
    """Get current user info"""
    user = get_current_user()
    if user:
        user_dict = dict(user)
        user_dict['created_at'] = user_dict['created_at'].isoformat() if user_dict['created_at'] else None
        return json_response(True, 'User fetched', user_dict)
    return json_response(False, 'User not found', status=404)

@app.route('/api/user', methods=['DELETE'])
@login_required
def api_delete_account():
    """Delete current user account"""
    try:
        models.delete_user(session['user_id'])
        session.clear()
        return json_response(True, 'Account deleted successfully')
    except Exception as e:
        return json_response(False, str(e), status=500)

# ============ RUN APP ============

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
