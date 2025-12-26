#!/bin/bash

# DigitalOcean Droplet setup script for Extended Exchange trading bot
# Run this script on a fresh Ubuntu 24.04 LTS Droplet (or 22.04 LTS)
#
# This script sets up the system (Docker, tools, directories) and creates
# management scripts in /opt/extended-bot. After running this script, you should:
# 1. Clone the repository into /opt/extended-bot (or update the paths in the
#    management scripts if cloning elsewhere)
# 2. Create your .env file manually with your API credentials
# 3. Run do_deploy.sh from the cloned repository location

set -e

echo "Setting up Extended Exchange trading bot on DigitalOcean..."
echo "=========================================================="

# Update system
echo "Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install Docker
echo "Installing Docker..."
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
rm get-docker.sh

# Install Docker Compose
echo "Installing Docker Compose..."
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install additional tools
echo "Installing additional tools..."
sudo apt install -y git curl wget htop tree jq

# Create application directory
echo "Creating application directory..."
sudo mkdir -p /opt/extended-bot
sudo chown $USER:$USER /opt/extended-bot
cd /opt/extended-bot

# Set timezone to UTC
echo "Setting timezone to UTC..."
sudo timedatectl set-timezone UTC

# Create logs directory
mkdir -p logs

# Create management scripts
echo "Creating management scripts..."

# Start script
cat > start_bot.sh <<'EOF'
#!/bin/bash
cd /opt/extended-bot

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ .env file not found! Please create .env file with your API credentials."
    exit 1
fi

# Determine compose command (prefer v2)
COMPOSE_CMD="docker compose"
if ! docker compose version &> /dev/null; then
    COMPOSE_CMD="docker-compose"
fi

# Start the bot
echo "Starting Extended Exchange trading bot..."
$COMPOSE_CMD up -d

echo "✅ Bot started successfully!"
echo "View logs: $COMPOSE_CMD logs -f"
echo "Stop bot: $COMPOSE_CMD down"
EOF

# Stop script
cat > stop_bot.sh <<'EOF'
#!/bin/bash
cd /opt/extended-bot

# Determine compose command (prefer v2)
COMPOSE_CMD="docker compose"
if ! docker compose version &> /dev/null; then
    COMPOSE_CMD="docker-compose"
fi

echo "Stopping Extended Exchange trading bot..."
$COMPOSE_CMD down
echo "✅ Bot stopped successfully!"
EOF

# Status script
cat > status.sh <<'EOF'
#!/bin/bash
cd /opt/extended-bot

# Determine compose command (prefer v2)
COMPOSE_CMD="docker compose"
if ! docker compose version &> /dev/null; then
    COMPOSE_CMD="docker-compose"
fi

echo "=== Extended Bot Status ==="
echo "Current time: $(date)"
echo "Timezone: $(timedatectl show --property=Timezone --value)"
echo ""

echo "Docker containers:"
$COMPOSE_CMD ps
echo ""

echo "Recent logs:"
$COMPOSE_CMD logs --tail=20
echo ""

echo "System resources:"
docker stats --no-stream
EOF

# Update script
cat > update_bot.sh <<'EOF'
#!/bin/bash
cd /opt/extended-bot

# Determine compose command (prefer v2)
COMPOSE_CMD="docker compose"
if ! docker compose version &> /dev/null; then
    COMPOSE_CMD="docker-compose"
fi

echo "Updating Extended Exchange trading bot..."

# Pull latest changes (if using git)
if [ -d .git ]; then
    git pull origin main
fi

# Rebuild and restart
$COMPOSE_CMD down
$COMPOSE_CMD build --no-cache
$COMPOSE_CMD up -d

echo "✅ Bot updated successfully!"
EOF

# Backup script
cat > backup.sh <<'EOF'
#!/bin/bash
cd /opt/extended-bot

BACKUP_DIR="/opt/backups"
BACKUP_FILE="extended-bot-backup-$(date +%Y%m%d-%H%M%S).tar.gz"

echo "Creating backup..."

# Create backup directory
mkdir -p $BACKUP_DIR

# Create backup
tar -czf $BACKUP_DIR/$BACKUP_FILE \
    --exclude='venv' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='logs/*.log' \
    .

echo "✅ Backup created: $BACKUP_DIR/$BACKUP_FILE"
EOF

# Make scripts executable
chmod +x *.sh

# Create systemd service for auto-start
echo "Creating systemd service..."
sudo tee /etc/systemd/system/extended-bot.service > /dev/null <<EOF
[Unit]
Description=Extended Exchange Trading Bot
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/extended-bot
ExecStart=/opt/extended-bot/start_bot.sh
ExecStop=/opt/extended-bot/stop_bot.sh
User=$USER
Group=$USER

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd
sudo systemctl daemon-reload

# Create logrotate configuration
echo "Setting up log rotation..."
sudo tee /etc/logrotate.d/extended-bot > /dev/null <<EOF
/opt/extended-bot/logs/*.log {
    daily
    missingok
    rotate 7
    compress
    delaycompress
    notifempty
    create 644 $USER $USER
}
EOF

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Create your .env file with your API credentials: nano .env"
echo "2. Test the bot: ./start_bot.sh"
echo "3. Check status: ./status.sh"
echo "4. Enable auto-start: sudo systemctl enable extended-bot.service"
echo "5. View logs: docker-compose logs -f"
echo ""
echo "Management commands:"
echo "  Start:  ./start_bot.sh"
echo "  Stop:   ./stop_bot.sh"
echo "  Status: ./status.sh"
echo "  Update: ./update_bot.sh"
echo "  Backup: ./backup.sh"
echo ""
echo "⚠️  Remember to log out and back in for Docker group permissions to take effect!"
