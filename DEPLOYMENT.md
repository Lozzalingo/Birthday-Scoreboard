# 🚀 Birthday Scoreboard - Deployment Guide

## Quick Deploy on Digital Ocean

### 1. Upload Files
```bash
# Copy all files to your Digital Ocean VM
scp -r . user@your-server-ip:/home/user/birthday-scoreboard/
```

### 2. Install Docker (if not installed)
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo apt install docker-compose-plugin -y

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker
```

### 3. Deploy Application
```bash
cd birthday-scoreboard

# Start the application
./run.sh start

# Or manually with docker-compose
docker-compose up -d --build
```

### 4. Configure Firewall
```bash
# Allow port 8080
sudo ufw allow 8080

# Check status
sudo ufw status
```

### 5. Access Application
- **Main Leaderboard**: `http://YOUR_SERVER_IP:8080`
- **Join Game**: `http://YOUR_SERVER_IP:8080/join`
- **QR Code**: `http://YOUR_SERVER_IP:8080/scan`
- **Admin Panel**: `http://YOUR_SERVER_IP:8080/admin`

## Alternative Port Setup

If you need to use port 80 (requires root):

### Option 1: Change Docker ports
Edit `docker-compose.yml`:
```yaml
ports:
  - "80:8080"  # Map port 80 to container port 8080
```

### Option 2: Use Nginx Reverse Proxy
```bash
# Install Nginx
sudo apt install nginx -y

# Create config file
sudo nano /etc/nginx/sites-available/scoreboard
```

Add this configuration:
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

Enable the site:
```bash
sudo ln -s /etc/nginx/sites-available/scoreboard /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## Management Commands

```bash
# Start application
./run.sh start

# Stop application
./run.sh stop

# Restart application
./run.sh restart

# View logs
./run.sh logs

# Check status
./run.sh status

# Backup database
./run.sh backup

# Complete cleanup
./run.sh cleanup
```

## Troubleshooting

### Port Already in Use
```bash
# Find what's using port 8080
sudo lsof -i :8080

# Kill the process if needed
sudo kill -9 <PID>
```

### Application Won't Start
```bash
# Check logs
./run.sh logs

# Rebuild containers
docker-compose down
docker-compose up -d --build --force-recreate
```

### Database Issues
```bash
# Backup current database
./run.sh backup

# Reset database (removes all data!)
docker-compose down
sudo rm -f data/leaderboard.db
docker-compose up -d
```

### Performance Optimization

For production use:

1. **Enable Docker logging limits**:
```yaml
# Add to docker-compose.yml under the service
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
```

2. **Set up automatic backups**:
```bash
# Add to crontab (crontab -e)
0 2 * * * cd /path/to/birthday-scoreboard && ./run.sh backup
```

3. **Monitor disk usage**:
```bash
# Check Docker disk usage
docker system df

# Clean up unused containers/images
docker system prune -a
```

## Security Notes

- Keep the admin URL (`/admin`) secret
- Consider using HTTPS in production
- Regularly backup your database
- Monitor server logs for unusual activity
- Update Docker images periodically

## Auto-Start on Boot

To start the application automatically when server boots:

```bash
# Create systemd service
sudo nano /etc/systemd/system/birthday-scoreboard.service
```

Add this content:
```ini
[Unit]
Description=Birthday Scoreboard
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/home/user/birthday-scoreboard
ExecStart=/home/user/birthday-scoreboard/run.sh start
ExecStop=/home/user/birthday-scoreboard/run.sh stop
TimeoutStartSec=0
User=user

[Install]
WantedBy=multi-user.target
```

Enable the service:
```bash
sudo systemctl enable birthday-scoreboard.service
sudo systemctl start birthday-scoreboard.service
```

## Success Checklist

✅ Application builds successfully
✅ Container starts without errors
✅ Web interface loads at `http://SERVER_IP:8080`
✅ QR code generates properly
✅ Teams can join and update scores
✅ Admin panel functions correctly
✅ Database persists data between restarts
✅ Firewall allows traffic on port 8080

## Support

If you encounter issues:
1. Check the logs: `./run.sh logs`
2. Verify Docker is running: `docker ps`
3. Test port accessibility: `curl http://localhost:8080/api/stats`
4. Check firewall settings: `sudo ufw status`

**Your Birthday Scoreboard is ready to party! 🎉**