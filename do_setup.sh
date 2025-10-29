#!/bin/bash

# DigitalOcean Droplet setup script for Extended Exchange trading bot
# Run this script on a fresh Ubuntu 22.04 LTS Droplet

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

# Create environment file template
echo "Creating environment file template..."
cat > .env.template <<EOF
# Extended Exchange API Configuration
EXTENDED_API_KEY=your_api_key_here
EXTENDED_STARK_KEY=your_stark_key_here
EXTENDED_STARK_PUBLIC_KEY=your_stark_public_key_here
EXTENDED_VAULT_NUMBER=your_vault_number_here
EXTENDED_CLIENT_ID=your_client_id_here
EXTENDED_BASE_URL=https://api.starknet.extended.exchange/api/v1

# Trading Configuration
TARGET_SIZE=5.0
BTC_LEVERAGE=10
ETH_LEVERAGE=10
OPEN_TIME=00:00:00
CLOSE_TIME=23:59:30
TIMEZONE=UTC

# Safety Configuration
DEAD_MAN_SWITCH_ENABLED=true
MAX_RETRY_ATTEMPTS=3

# DigitalOcean Configuration
DO_REGION=nyc1
DO_DROPLET_SIZE=s-1vcpu-1gb
EOF

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
    echo "❌ .env file not found! Please copy .env.template to .env and configure it."
    exit 1
fi

# Start the bot
echo "Starting Extended Exchange trading bot..."
docker-compose up -d

echo "✅ Bot started successfully!"
echo "View logs: docker-compose logs -f"
echo "Stop bot: docker-compose down"
EOF

# Stop script
cat > stop_bot.sh <<'EOF'
#!/bin/bash
cd /opt/extended-bot
echo "Stopping Extended Exchange trading bot..."
docker-compose down
echo "✅ Bot stopped successfully!"
EOF

# Status script
cat > status.sh <<'EOF'
#!/bin/bash
cd /opt/extended-bot

echo "=== Extended Bot Status ==="
echo "Current time: $(date)"
echo "Timezone: $(timedatectl show --property=Timezone --value)"
echo ""

echo "Docker containers:"
docker-compose ps
echo ""

echo "Recent logs:"
docker-compose logs --tail=20
echo ""

echo "System resources:"
docker stats --no-stream
EOF

# Update script
cat > update_bot.sh <<'EOF'
#!/bin/bash
cd /opt/extended-bot

echo "Updating Extended Exchange trading bot..."

# Pull latest changes (if using git)
if [ -d .git ]; then
    git pull origin main
fi

# Rebuild and restart
docker-compose down
docker-compose build --no-cache
docker-compose up -d

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
echo "1. Copy your .env file: cp .env.template .env"
echo "2. Edit .env with your API credentials: nano .env"
echo "3. Test the bot: ./start_bot.sh"
echo "4. Check status: ./status.sh"
echo "5. Enable auto-start: sudo systemctl enable extended-bot.service"
echo "6. View logs: docker-compose logs -f"
echo ""
echo "Management commands:"
echo "  Start:  ./start_bot.sh"
echo "  Stop:   ./stop_bot.sh"
echo "  Status: ./status.sh"
echo "  Update: ./update_bot.sh"
echo "  Backup: ./backup.sh"
echo ""
echo "⚠️  Remember to log out and back in for Docker group permissions to take effect!"
