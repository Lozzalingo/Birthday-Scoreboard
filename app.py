from flask import Flask, render_template, request, session, jsonify, url_for, send_file
from flask_socketio import SocketIO, emit, disconnect
import qrcode
import io
import os
from datetime import datetime
import secrets
import database as db

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(16)

# Initialize SocketIO with CORS enabled
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# Configuration
HOST = '0.0.0.0'
PORT = 8080  # Using port 8080 to avoid conflicts
DEBUG = True

def get_join_url():
    """Get the join URL for QR code generation."""
    return f"http://{request.host}/join"

def emit_leaderboard_update():
    """Emit leaderboard update to all connected clients."""
    teams = db.get_all_teams()
    socketio.emit('leaderboard_update', {'teams': teams})

@app.route('/')
def index():
    """Main leaderboard page."""
    return render_template('leaderboard.html')

@app.route('/scan')
def scan():
    """Scan page with QR code and mini leaderboard."""
    join_url = get_join_url()
    return render_template('scan.html', join_url=join_url)

@app.route('/join')
def join():
    """Join game page for players."""
    return render_template('join.html')

@app.route('/admin')
def admin():
    """Admin panel for managing teams and scores."""
    return render_template('admin.html')

@app.route('/qr')
def qr_code():
    """Generate QR code for joining the game."""
    join_url = get_join_url()

    # Create QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(join_url)
    qr.make(fit=True)

    # Create QR code image
    img = qr.make_image(fill_color="black", back_color="white")

    # Save to BytesIO
    img_io = io.BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)

    return send_file(img_io, mimetype='image/png')

@app.route('/api/stats')
def api_stats():
    """API endpoint for database statistics."""
    stats = db.get_database_stats()
    return jsonify(stats)

@app.route('/api/teams')
def api_teams():
    """API endpoint for getting all teams."""
    teams = db.get_all_teams()
    return jsonify({'teams': teams})

# WebSocket Events
@socketio.on('connect')
def handle_connect():
    """Handle client connection."""
    print(f"Client connected: {request.sid}")
    emit('connected', {'message': 'Successfully connected to the game server'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection."""
    print(f"Client disconnected: {request.sid}")

@socketio.on('request_leaderboard')
def handle_request_leaderboard():
    """Send current leaderboard to requesting client."""
    teams = db.get_all_teams()
    emit('leaderboard_update', {'teams': teams})

@socketio.on('join_game')
def handle_join_game(data):
    """Handle player joining the game."""
    team_name = data.get('team_name', '').strip()

    if not team_name:
        emit('error', {'message': 'Team name is required'})
        return

    if len(team_name) > 50:
        emit('error', {'message': 'Team name must be 50 characters or less'})
        return

    # Check if team name already exists
    if db.team_name_exists(team_name):
        emit('error', {'message': 'Team name already exists. Please choose a different name.'})
        return

    try:
        # Create new team
        team = db.create_team(team_name)

        # Verify team was created successfully
        if not team or 'id' not in team:
            emit('error', {'message': 'Failed to create team. Please try again.'})
            return

        # Store team ID in session
        session['team_id'] = team['id']

        # Emit success to joining client
        emit('team_joined', {
            'team_id': team['id'],
            'team_name': team['name'],
            'score': team['score']
        })

        # Broadcast leaderboard update to all clients
        emit_leaderboard_update()

        print(f"Team '{team_name}' joined the game with ID: {team['id']}")

    except ValueError as e:
        print(f"ValueError creating team: {e}")
        emit('error', {'message': 'Team name conflict. Please try a different name.'})
    except Exception as e:
        print(f"Unexpected error creating team: {e}")
        emit('error', {'message': 'Failed to join game. Please try again.'})

@socketio.on('get_team_data')
def handle_get_team_data(data):
    """Get specific team data."""
    team_id = data.get('team_id')

    if not team_id:
        emit('error', {'message': 'Team ID is required'})
        return

    team = db.get_team_by_id(team_id)

    if team:
        emit('team_data', {
            'team_id': team['id'],
            'team_name': team['name'],
            'score': team['score']
        })
    else:
        emit('error', {'message': 'Team not found'})

@socketio.on('update_team_name')
def handle_update_team_name(data):
    """Handle team name update."""
    team_id = data.get('team_id')
    new_name = data.get('team_name', '').strip()

    if not team_id:
        emit('error', {'message': 'Team ID is required'})
        return

    if not new_name:
        emit('error', {'message': 'Team name is required'})
        return

    if len(new_name) > 50:
        emit('error', {'message': 'Team name must be 50 characters or less'})
        return

    # Check if team name already exists (excluding current team)
    if db.team_name_exists(new_name, exclude_id=team_id):
        emit('error', {'message': 'Team name already exists. Please choose a different name.'})
        return

    try:
        updated_team = db.update_team_name(team_id, new_name)

        if updated_team:
            # Emit success to updating client
            emit('team_data', {
                'team_id': updated_team['id'],
                'team_name': updated_team['name'],
                'score': updated_team['score']
            })

            # Broadcast leaderboard update to all clients
            emit_leaderboard_update()

            print(f"Team {team_id} updated name to: {new_name}")
        else:
            emit('error', {'message': 'Team not found'})

    except Exception as e:
        print(f"Error updating team name: {e}")
        emit('error', {'message': 'Failed to update team name. Please try again.'})

@socketio.on('update_score')
def handle_update_score(data):
    """Handle score update."""
    team_id = data.get('team_id')
    new_score = data.get('score')

    if not team_id:
        emit('error', {'message': 'Team ID is required'})
        return

    if new_score is None or new_score < 0:
        emit('error', {'message': 'Valid score is required (must be 0 or greater)'})
        return

    try:
        updated_team = db.update_team_score(team_id, new_score)

        if updated_team:
            # Emit success to updating client
            emit('team_data', {
                'team_id': updated_team['id'],
                'team_name': updated_team['name'],
                'score': updated_team['score']
            })

            # Broadcast leaderboard update to all clients
            emit_leaderboard_update()

            print(f"Team {updated_team['name']} updated score to: {new_score}")
        else:
            emit('error', {'message': 'Team not found'})

    except Exception as e:
        print(f"Error updating score: {e}")
        emit('error', {'message': 'Failed to update score. Please try again.'})

# Admin-only events
@socketio.on('admin_update_team')
def handle_admin_update_team(data):
    """Handle admin team updates (both name and score)."""
    team_id = data.get('team_id')
    team_name = data.get('team_name', '').strip()
    score = data.get('score')

    if not team_id:
        emit('error', {'message': 'Team ID is required'})
        return

    if not team_name:
        emit('error', {'message': 'Team name is required'})
        return

    if len(team_name) > 50:
        emit('error', {'message': 'Team name must be 50 characters or less'})
        return

    if score is None or score < 0:
        emit('error', {'message': 'Valid score is required (must be 0 or greater)'})
        return

    # Check if team name already exists (excluding current team)
    if db.team_name_exists(team_name, exclude_id=team_id):
        emit('error', {'message': 'Team name already exists. Please choose a different name.'})
        return

    try:
        updated_team = db.update_team(team_id, name=team_name, score=score)

        if updated_team:
            # Broadcast leaderboard update to all clients
            emit_leaderboard_update()

            print(f"Admin updated team {team_id}: {team_name} -> {score}")
        else:
            emit('error', {'message': 'Team not found'})

    except Exception as e:
        print(f"Error in admin update: {e}")
        emit('error', {'message': 'Failed to update team. Please try again.'})

@socketio.on('delete_team')
def handle_delete_team(data):
    """Handle team deletion (admin only)."""
    team_id = data.get('team_id')

    if not team_id:
        emit('error', {'message': 'Team ID is required'})
        return

    try:
        deleted = db.delete_team(team_id)

        if deleted:
            # Emit confirmation to admin
            emit('team_deleted', {'team_id': team_id})

            # Broadcast leaderboard update to all clients
            emit_leaderboard_update()

            print(f"Admin deleted team: {team_id}")
        else:
            emit('error', {'message': 'Team not found'})

    except Exception as e:
        print(f"Error deleting team: {e}")
        emit('error', {'message': 'Failed to delete team. Please try again.'})

@socketio.on('clear_all_teams')
def handle_clear_all_teams():
    """Handle clearing all teams (admin only)."""
    try:
        deleted_count = db.clear_all_teams()

        # Broadcast leaderboard update to all clients
        emit_leaderboard_update()

        print(f"Admin cleared all teams. Deleted {deleted_count} teams.")

    except Exception as e:
        print(f"Error clearing teams: {e}")
        emit('error', {'message': 'Failed to clear teams. Please try again.'})

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return render_template('leaderboard.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return "Internal server error", 500

if __name__ == '__main__':
    print("🎉 Birthday Scoreboard Server Starting...")
    print(f"🌐 Server will be available at: http://{HOST}:{PORT}")
    print(f"📱 Join URL: http://{HOST}:{PORT}/join")
    print(f"⚙️ Admin Panel: http://{HOST}:{PORT}/admin")
    print(f"📊 Scan Page: http://{HOST}:{PORT}/scan")

    # Initialize database
    db.init_database()
    print("✅ Database initialized")

    # Run the application
    socketio.run(
        app,
        host=HOST,
        port=PORT,
        debug=DEBUG,
        allow_unsafe_werkzeug=True
    )