#!/usr/bin/env python3
"""
VoidLink Admin Web Interface - Web-based administration panel
"""

import os
import sys
import json
import time
import datetime
import threading
import socket
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import VoidLink modules
from authentication import authenticate_user, get_user_role, list_users, create_user, delete_user
from file_transfer import get_file_list, get_file_metadata, delete_file
from file_transfer_resumable import get_active_transfers, cancel_transfer
from storage import get_chat_history
from rooms import get_rooms, create_room, delete_room
from error_handling import logger, log_info, log_warning, log_error

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(hours=2)

# Initialize login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# User class for Flask-Login
class User(UserMixin):
    def __init__(self, username, role):
        self.id = username
        self.username = username
        self.role = role

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    # Check if user exists
    users = list_users()
    for user in users:
        if user['username'] == user_id:
            return User(user['username'], user['role'])
    return None

# Routes
@app.route('/')
def index():
    """Home page"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Authenticate user
        try:
            if authenticate_user(username, password):
                # Get user role
                role = get_user_role(username)
                
                # Only allow admin users
                if role == 'admin':
                    user = User(username, role)
                    login_user(user)
                    log_info(f"Admin login: {username}")
                    flash('Login successful', 'success')
                    return redirect(url_for('dashboard'))
                else:
                    error = 'Admin access required'
                    log_warning(f"Non-admin login attempt: {username}")
            else:
                error = 'Invalid username or password'
                log_warning(f"Failed login attempt: {username}")
        except Exception as e:
            error = str(e)
            log_error(f"Login error: {str(e)}")
    
    return render_template('login.html', error=error)

@app.route('/logout')
@login_required
def logout():
    """Logout"""
    log_info(f"Admin logout: {current_user.username}")
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    """Dashboard page"""
    # Get system stats
    stats = {
        'users': len(list_users()),
        'files': len(get_file_list()),
        'rooms': len(get_rooms()),
        'active_transfers': len(get_active_transfers())
    }
    
    # Get recent activity
    recent_messages = get_chat_history(limit=10)
    
    return render_template('dashboard.html', stats=stats, recent_messages=recent_messages)

@app.route('/users')
@login_required
def users():
    """Users management page"""
    users_list = list_users()
    return render_template('users.html', users=users_list)

@app.route('/users/add', methods=['POST'])
@login_required
def add_user():
    """Add a new user"""
    username = request.form['username']
    password = request.form['password']
    role = request.form['role']
    
    if not username or not password:
        flash('Username and password are required', 'error')
        return redirect(url_for('users'))
    
    try:
        success = create_user(username, password, role)
        if success:
            flash(f'User {username} created successfully', 'success')
            log_info(f"User created by admin {current_user.username}: {username}")
        else:
            flash(f'Failed to create user {username}', 'error')
    except Exception as e:
        flash(f'Error creating user: {str(e)}', 'error')
        log_error(f"Error creating user: {str(e)}")
    
    return redirect(url_for('users'))

@app.route('/users/delete/<username>', methods=['POST'])
@login_required
def delete_user_route(username):
    """Delete a user"""
    if username == current_user.username:
        flash('You cannot delete your own account', 'error')
        return redirect(url_for('users'))
    
    try:
        success = delete_user(username)
        if success:
            flash(f'User {username} deleted successfully', 'success')
            log_info(f"User deleted by admin {current_user.username}: {username}")
        else:
            flash(f'Failed to delete user {username}', 'error')
    except Exception as e:
        flash(f'Error deleting user: {str(e)}', 'error')
        log_error(f"Error deleting user: {str(e)}")
    
    return redirect(url_for('users'))

@app.route('/files')
@login_required
def files():
    """Files management page"""
    files_list = get_file_list()
    return render_template('files.html', files=files_list)

@app.route('/files/view/<filename>')
@login_required
def view_file(filename):
    """View file details"""
    file_info = get_file_metadata(filename)
    if not file_info:
        flash(f'File {filename} not found', 'error')
        return redirect(url_for('files'))
    
    return render_template('file_details.html', file=file_info)

@app.route('/files/delete/<filename>', methods=['POST'])
@login_required
def delete_file_route(filename):
    """Delete a file"""
    try:
        success = delete_file(filename)
        if success:
            flash(f'File {filename} deleted successfully', 'success')
            log_info(f"File deleted by admin {current_user.username}: {filename}")
        else:
            flash(f'Failed to delete file {filename}', 'error')
    except Exception as e:
        flash(f'Error deleting file: {str(e)}', 'error')
        log_error(f"Error deleting file: {str(e)}")
    
    return redirect(url_for('files'))

@app.route('/rooms')
@login_required
def rooms():
    """Rooms management page"""
    rooms_list = get_rooms()
    return render_template('rooms.html', rooms=rooms_list)

@app.route('/rooms/add', methods=['POST'])
@login_required
def add_room():
    """Add a new room"""
    room_id = request.form['room_id']
    name = request.form['name']
    description = request.form['description']
    
    if not room_id or not name:
        flash('Room ID and name are required', 'error')
        return redirect(url_for('rooms'))
    
    try:
        success = create_room(room_id, name, description, current_user.username)
        if success:
            flash(f'Room {name} created successfully', 'success')
            log_info(f"Room created by admin {current_user.username}: {room_id}")
        else:
            flash(f'Failed to create room {name}', 'error')
    except Exception as e:
        flash(f'Error creating room: {str(e)}', 'error')
        log_error(f"Error creating room: {str(e)}")
    
    return redirect(url_for('rooms'))

@app.route('/rooms/delete/<room_id>', methods=['POST'])
@login_required
def delete_room_route(room_id):
    """Delete a room"""
    try:
        success = delete_room(room_id, current_user.username)
        if success:
            flash(f'Room {room_id} deleted successfully', 'success')
            log_info(f"Room deleted by admin {current_user.username}: {room_id}")
        else:
            flash(f'Failed to delete room {room_id}', 'error')
    except Exception as e:
        flash(f'Error deleting room: {str(e)}', 'error')
        log_error(f"Error deleting room: {str(e)}")
    
    return redirect(url_for('rooms'))

@app.route('/transfers')
@login_required
def transfers():
    """Active transfers page"""
    transfers_list = get_active_transfers()
    return render_template('transfers.html', transfers=transfers_list)

@app.route('/transfers/cancel/<transfer_id>', methods=['POST'])
@login_required
def cancel_transfer_route(transfer_id):
    """Cancel a transfer"""
    try:
        success = cancel_transfer(transfer_id)
        if success:
            flash(f'Transfer {transfer_id} cancelled successfully', 'success')
            log_info(f"Transfer cancelled by admin {current_user.username}: {transfer_id}")
        else:
            flash(f'Failed to cancel transfer {transfer_id}', 'error')
    except Exception as e:
        flash(f'Error cancelling transfer: {str(e)}', 'error')
        log_error(f"Error cancelling transfer: {str(e)}")
    
    return redirect(url_for('transfers'))

@app.route('/logs')
@login_required
def logs():
    """Logs page"""
    log_dir = 'logs'
    log_files = []
    
    if os.path.exists(log_dir):
        for file in os.listdir(log_dir):
            if file.endswith('.log'):
                log_files.append(file)
    
    return render_template('logs.html', log_files=log_files)

@app.route('/logs/view/<filename>')
@login_required
def view_log(filename):
    """View log file"""
    log_path = os.path.join('logs', filename)
    
    if not os.path.exists(log_path):
        flash(f'Log file {filename} not found', 'error')
        return redirect(url_for('logs'))
    
    with open(log_path, 'r') as f:
        log_content = f.readlines()
    
    return render_template('log_details.html', filename=filename, log_content=log_content)

@app.route('/settings')
@login_required
def settings():
    """Settings page"""
    return render_template('settings.html')

@app.route('/api/stats')
@login_required
def api_stats():
    """API endpoint for system stats"""
    stats = {
        'users': len(list_users()),
        'files': len(get_file_list()),
        'rooms': len(get_rooms()),
        'active_transfers': len(get_active_transfers()),
        'timestamp': time.time()
    }
    return jsonify(stats)

@app.route('/api/transfers')
@login_required
def api_transfers():
    """API endpoint for active transfers"""
    transfers = get_active_transfers()
    return jsonify(transfers)

if __name__ == '__main__':
    # Create logs directory if it doesn't exist
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # Start the Flask app
    app.run(host='0.0.0.0', port=5000, debug=True)