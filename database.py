import sqlite3
import uuid
from datetime import datetime
import os

DATABASE_FILE = 'leaderboard.db'

def get_db_connection():
    """Get a database connection with row factory for easier access."""
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    """Initialize the database with required tables."""
    conn = get_db_connection()

    # Create teams table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS teams (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            score REAL DEFAULT 0,
            is_locked BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Add is_locked column if it doesn't exist
    try:
        conn.execute('ALTER TABLE teams ADD COLUMN is_locked BOOLEAN DEFAULT 0')
    except sqlite3.OperationalError:
        pass  # Column already exists

    # Migrate existing tables to support decimal scores
    try:
        # Check if score column is INTEGER and migrate if needed
        cursor = conn.execute("PRAGMA table_info(teams)")
        columns = cursor.fetchall()
        score_column = next((col for col in columns if col[1] == 'score'), None)

        if score_column and score_column[2] == 'INTEGER':
            # Create backup and migrate
            conn.execute('''
                CREATE TABLE teams_backup AS SELECT * FROM teams
            ''')
            conn.execute('DROP TABLE teams')
            conn.execute('''
                CREATE TABLE teams (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    score REAL DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.execute('''
                INSERT INTO teams (id, name, score, created_at, updated_at)
                SELECT id, name, CAST(score AS REAL), created_at, updated_at
                FROM teams_backup
            ''')
            conn.execute('DROP TABLE teams_backup')
            print("✅ Database migrated to support decimal scores")
    except Exception as e:
        print(f"Migration info: {e}")

    # Create games table (for future multi-game support)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS games (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            is_active BOOLEAN DEFAULT 0,
            players_locked BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Add players_locked column if it doesn't exist
    try:
        conn.execute('ALTER TABLE games ADD COLUMN players_locked BOOLEAN DEFAULT 0')
    except sqlite3.OperationalError:
        pass  # Column already exists

    # Create a default game if none exists
    existing_game = conn.execute('SELECT COUNT(*) as count FROM games').fetchone()
    if existing_game['count'] == 0:
        game_id = str(uuid.uuid4())
        conn.execute(
            'INSERT INTO games (id, name, is_active, players_locked) VALUES (?, ?, ?, ?)',
            (game_id, 'Birthday Game', 1, 0)
        )

    conn.commit()
    conn.close()

def get_active_game():
    """Get the currently active game."""
    conn = get_db_connection()
    game = conn.execute('SELECT * FROM games WHERE is_active = 1 LIMIT 1').fetchone()
    conn.close()
    return dict(game) if game else None

def get_all_teams():
    """Get all teams ordered by score descending."""
    conn = get_db_connection()
    teams = conn.execute(
        'SELECT * FROM teams ORDER BY score DESC, created_at ASC'
    ).fetchall()
    conn.close()
    return [dict(team) for team in teams]

def get_team_by_id(team_id):
    """Get a specific team by ID."""
    conn = get_db_connection()
    team = conn.execute('SELECT * FROM teams WHERE id = ?', (team_id,)).fetchone()
    conn.close()
    return dict(team) if team else None

def create_team(name):
    """Create a new team and return its data."""
    team_id = str(uuid.uuid4())
    conn = get_db_connection()

    try:
        conn.execute(
            'INSERT INTO teams (id, name, score) VALUES (?, ?, ?)',
            (team_id, name, 0)
        )
        conn.commit()

        # Get the created team
        team = conn.execute('SELECT * FROM teams WHERE id = ?', (team_id,)).fetchone()
        result = dict(team) if team else None
        conn.close()
        return result
    except sqlite3.IntegrityError as e:
        conn.close()
        raise ValueError("Team ID conflict")
    except Exception as e:
        conn.close()
        raise e

def update_team_name(team_id, new_name):
    """Update a team's name."""
    conn = get_db_connection()

    cursor = conn.execute(
        'UPDATE teams SET name = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
        (new_name, team_id)
    )

    updated = cursor.rowcount > 0
    conn.commit()
    conn.close()

    if updated:
        return get_team_by_id(team_id)
    return None

def update_team_score(team_id, new_score):
    """Update a team's score."""
    conn = get_db_connection()

    cursor = conn.execute(
        'UPDATE teams SET score = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
        (new_score, team_id)
    )

    updated = cursor.rowcount > 0
    conn.commit()
    conn.close()

    if updated:
        return get_team_by_id(team_id)
    return None

def update_team(team_id, name=None, score=None):
    """Update both team name and score."""
    if name is None and score is None:
        return get_team_by_id(team_id)

    conn = get_db_connection()

    if name is not None and score is not None:
        cursor = conn.execute(
            'UPDATE teams SET name = ?, score = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
            (name, score, team_id)
        )
    elif name is not None:
        cursor = conn.execute(
            'UPDATE teams SET name = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
            (name, team_id)
        )
    else:
        cursor = conn.execute(
            'UPDATE teams SET score = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
            (score, team_id)
        )

    updated = cursor.rowcount > 0
    conn.commit()
    conn.close()

    if updated:
        return get_team_by_id(team_id)
    return None

def delete_team(team_id):
    """Delete a team."""
    conn = get_db_connection()
    cursor = conn.execute('DELETE FROM teams WHERE id = ?', (team_id,))
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return deleted

def clear_all_teams():
    """Delete all teams."""
    conn = get_db_connection()
    cursor = conn.execute('DELETE FROM teams')
    deleted_count = cursor.rowcount
    conn.commit()
    conn.close()
    return deleted_count

def get_team_count():
    """Get the total number of teams."""
    conn = get_db_connection()
    count = conn.execute('SELECT COUNT(*) as count FROM teams').fetchone()
    conn.close()
    return count['count']

def team_name_exists(name, exclude_id=None):
    """Check if a team name already exists (case-insensitive)."""
    conn = get_db_connection()

    if exclude_id:
        result = conn.execute(
            'SELECT COUNT(*) as count FROM teams WHERE LOWER(name) = LOWER(?) AND id != ?',
            (name, exclude_id)
        ).fetchone()
    else:
        result = conn.execute(
            'SELECT COUNT(*) as count FROM teams WHERE LOWER(name) = LOWER(?)',
            (name,)
        ).fetchone()

    conn.close()
    return result['count'] > 0

def backup_database(backup_path=None):
    """Create a backup of the database."""
    if backup_path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"backup_leaderboard_{timestamp}.db"

    if os.path.exists(DATABASE_FILE):
        import shutil
        shutil.copy2(DATABASE_FILE, backup_path)
        return backup_path
    return None

def are_players_locked():
    """Check if players are locked from updating scores."""
    conn = get_db_connection()
    game = conn.execute('SELECT players_locked FROM games WHERE is_active = 1 LIMIT 1').fetchone()
    conn.close()
    return bool(game['players_locked']) if game else False

def set_players_locked(locked):
    """Set the players locked state."""
    conn = get_db_connection()
    cursor = conn.execute(
        'UPDATE games SET players_locked = ? WHERE is_active = 1',
        (1 if locked else 0,)
    )
    updated = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return updated

def is_team_locked(team_id):
    """Check if a specific team is locked."""
    conn = get_db_connection()
    team = conn.execute('SELECT is_locked FROM teams WHERE id = ?', (team_id,)).fetchone()
    conn.close()
    return bool(team['is_locked']) if team else False

def set_team_locked(team_id, locked):
    """Set the locked state for a specific team."""
    conn = get_db_connection()
    cursor = conn.execute(
        'UPDATE teams SET is_locked = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
        (1 if locked else 0, team_id)
    )
    updated = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return updated

def get_database_stats():
    """Get database statistics."""
    conn = get_db_connection()

    team_count = conn.execute('SELECT COUNT(*) as count FROM teams').fetchone()['count']
    total_score = conn.execute('SELECT SUM(score) as total FROM teams').fetchone()['total'] or 0
    avg_score = conn.execute('SELECT AVG(score) as avg FROM teams').fetchone()['avg'] or 0

    top_team = conn.execute('SELECT name, score FROM teams ORDER BY score DESC LIMIT 1').fetchone()
    players_locked = conn.execute('SELECT players_locked FROM games WHERE is_active = 1 LIMIT 1').fetchone()

    conn.close()

    return {
        'team_count': team_count,
        'total_score': total_score,
        'average_score': round(avg_score, 2),
        'top_team': dict(top_team) if top_team else None,
        'players_locked': bool(players_locked['players_locked']) if players_locked else False
    }

# Initialize database when module is imported
if __name__ == "__main__":
    init_database()
    print("Database initialized successfully!")
else:
    init_database()