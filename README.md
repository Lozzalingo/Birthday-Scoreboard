# 🎉 Birthday Scoreboard

A real-time, interactive leaderboard web application perfect for birthday parties, games, and competitions. Players can join via QR code, update their scores in real-time, and see live updates without page refreshes.

## ✨ Features

- **Real-time Updates**: Live score updates using WebSockets
- **QR Code Join**: Players scan QR code to join instantly
- **Half Point Support**: Score in increments of 0.5 (1, 1.5, 2, 2.5, etc.)
- **Responsive Design**: Works perfectly on mobile and desktop
- **Admin Panel**: Full control over teams and scores
- **Session Management**: No sign-ups required, uses browser sessions
- **SQLite Database**: Persistent data storage
- **Docker Ready**: Easy deployment with Docker
- **Beautiful UI**: Modern, gradient-based design with emojis

## 🚀 Quick Start

### Using Docker (Recommended)

1. **Clone/Download** the project
2. **Start the application**:
   ```bash
   ./run.sh start
   ```

3. **Access the application**:
   - Main Leaderboard: http://localhost:8080
   - Join Game: http://localhost:8080/join
   - Scan Page: http://localhost:8080/scan
   - Admin Panel: http://localhost:8080/admin

### Manual Installation

1. **Install Python 3.11+** and dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the application**:
   ```bash
   python app.py
   ```

## 📱 How to Use

### For Players:
1. **Scan QR Code** on the scan page or visit the join URL
2. **Enter Team Name** and click "Join Game"
3. **Update Score** using the input field or quick buttons (+0.5, +1, +5, +10, -0.5, -1)
4. **Change Team Name** if needed
5. **Watch Live Updates** on the leaderboard

### For Admins:
1. **Visit Admin Panel** at `/admin` (keep URL secret)
2. **Edit Teams** - Click edit button to modify name and score
3. **Delete Teams** - Remove individual teams
4. **Clear All** - Reset the entire leaderboard
5. **Export Data** - Download CSV of current standings

## 🎮 Game Workflow

1. **Setup**: Admin visits scan page and displays QR code
2. **Join**: Players scan QR code and enter team names
3. **Play**: Teams appear on leaderboard instantly
4. **Score**: Players update their own scores in real-time
5. **Manage**: Admin can override any scores if needed
6. **Export**: Save final results as CSV

## 🔧 Configuration

### Ports
- Default: **8080** (to avoid conflicts)
- Change in `app.py` and `docker-compose.yml` if needed

### Database
- SQLite database stored in `data/leaderboard.db`
- Automatic initialization on first run
- Backup with: `./run.sh backup`

### Security
- No authentication (by design for ease of use)
- Admin panel URL should be kept secret
- Suitable for private/internal networks

## 🐳 Docker Commands

```bash
# Start application
./run.sh start

# View logs
./run.sh logs

# Stop application
./run.sh stop

# Restart application
./run.sh restart

# Check status
./run.sh status

# Backup database
./run.sh backup

# Complete cleanup
./run.sh cleanup
```

## 🌐 Deployment on Digital Ocean

1. **Copy files** to your VM
2. **Install Docker** and Docker Compose
3. **Run the application**:
   ```bash
   ./run.sh start
   ```
4. **Configure firewall** to allow port 8080
5. **Access via server IP**: `http://YOUR_SERVER_IP:8080`

### Nginx Reverse Proxy (Optional)

If you want to use port 80/443:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8080;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
}
```

## 📊 API Endpoints

- `GET /` - Main leaderboard
- `GET /join` - Join game page
- `GET /scan` - QR code scan page
- `GET /admin` - Admin panel
- `GET /qr` - QR code image
- `GET /api/stats` - Database statistics
- `GET /api/teams` - All teams data

## 🔌 WebSocket Events

### Client → Server:
- `join_game` - Join with team name
- `update_score` - Update team score
- `update_team_name` - Change team name
- `request_leaderboard` - Get current standings

### Server → Client:
- `leaderboard_update` - Live leaderboard data
- `team_joined` - Successful join confirmation
- `team_data` - Individual team data
- `error` - Error messages

## 🛠️ Tech Stack

- **Backend**: Python Flask + Flask-SocketIO
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Database**: SQLite
- **Real-time**: WebSockets (Socket.IO)
- **QR Codes**: qrcode library
- **Containerization**: Docker + Docker Compose

## 🎨 Customization

### Colors/Theme
Edit `static/css/style.css` to change:
- Gradient colors
- Button styles
- Layout spacing

### Functionality
- Modify `app.py` for new features
- Add validation in `database.py`
- Extend WebSocket events

## 🐛 Troubleshooting

### Application won't start:
```bash
# Check logs
./run.sh logs

# Restart
./run.sh restart
```

### Port conflicts:
- Change port in `app.py` (line: `PORT = 8080`)
- Update `docker-compose.yml` ports mapping
- Update firewall rules

### Database issues:
```bash
# Backup current data
./run.sh backup

# Check database file
ls -la data/

# Restart application
./run.sh restart
```

### WebSocket connection failed:
- Check firewall allows port 8080
- Verify server IP/hostname is correct
- Try different browser/device

## 📝 License

This project is open source and available under the MIT License.

## 🎯 Perfect For

- Birthday parties
- Office competitions
- Game nights
- Sports tournaments
- Trivia contests
- Team building events

## 🤝 Contributing

Feel free to submit issues, feature requests, or pull requests!

---

**Enjoy your Birthday Scoreboard! 🎉🏆**