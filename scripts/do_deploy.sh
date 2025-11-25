#!/bin/bash

# DigitalOcean deployment script for Extended Exchange trading bot
# This script helps deploy the bot to a DigitalOcean Droplet

set -e

echo "Extended Exchange Trading Bot - DigitalOcean Deployment"
echo "======================================================"

# Check if we're on a DigitalOcean Droplet
if [ -f /etc/digitalocean ]; then
    echo "✓ Running on DigitalOcean Droplet"
else
    echo "⚠️  Not running on DigitalOcean - some features may not work"
fi

# Check Docker installation
if command -v docker &> /dev/null; then
    echo "✓ Docker is installed"
    docker --version
else
    echo "❌ Docker is not installed. Please run ./do_setup.sh first"
    exit 1
fi

# Check Docker Compose installation (try v2 first, then v1)
if docker compose version &> /dev/null; then
    echo "✓ Docker Compose (v2) is installed"
    docker compose version
elif command -v docker-compose &> /dev/null; then
    echo "✓ Docker Compose (v1) is installed"
    docker-compose --version
    COMPOSE_CMD="docker-compose"
else
    echo "❌ Docker Compose is not installed. Please run ./do_setup.sh first"
    exit 1
fi

# Set compose command (use docker compose v2 if available)
if [ -z "$COMPOSE_CMD" ]; then
    COMPOSE_CMD="docker compose"
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.template .env
    echo "⚠️  Please edit .env file with your API credentials before running the bot"
    echo "   You can edit it with: nano .env"
    exit 1
fi

# Validate .env file
echo "Validating configuration..."
if ! grep -q "EXTENDED_API_KEY=your_api_key_here" .env; then
    echo "✓ .env file appears to be configured"
else
    echo "❌ .env file still contains template values. Please configure your API credentials."
    exit 1
fi

# Create necessary directories
echo "Creating directories..."
mkdir -p logs
mkdir -p monitoring

# Build Docker image
echo "Building Docker image..."
$COMPOSE_CMD build --no-cache

# Test the bot configuration
echo "Testing bot configuration..."
$COMPOSE_CMD run --rm extended-bot python -c "
from src.config import Config
try:
    Config.validate_config()
    print('✓ Configuration validation passed')
except Exception as e:
    print(f'❌ Configuration validation failed: {e}')
    exit(1)
"

if [ $? -eq 0 ]; then
    echo "✓ Bot configuration test passed"
else
    echo "❌ Bot configuration test failed - please check your .env file"
    exit 1
fi

# Start the bot
echo "Starting the trading bot..."
$COMPOSE_CMD up -d

# Wait for bot to start
echo "Waiting for bot to start..."
sleep 10

# Check if bot is running
if $COMPOSE_CMD ps | grep -q "Up"; then
    echo "✅ Bot started successfully!"
    echo ""
    echo "Management commands:"
    echo "  View logs:    $COMPOSE_CMD logs -f"
    echo "  Stop bot:     $COMPOSE_CMD down"
    echo "  Restart bot:  $COMPOSE_CMD restart"
    echo "  Bot status:   $COMPOSE_CMD ps"
    echo ""
    echo "System commands:"
    echo "  Start:        ./start_bot.sh"
    echo "  Stop:         ./stop_bot.sh"
    echo "  Status:       ./status.sh"
    echo "  Update:       ./update_bot.sh"
    echo "  Backup:       ./backup.sh"
    echo ""
    echo "Monitoring:"
    echo "  View logs:    $COMPOSE_CMD logs -f extended-bot"
    echo "  System stats: docker stats"
    echo "  Bot health:   $COMPOSE_CMD ps"
else
    echo "❌ Bot failed to start. Check logs with: $COMPOSE_CMD logs"
    exit 1
fi

# Enable auto-start service
echo "Enabling auto-start service..."
sudo systemctl enable extended-bot.service

echo ""
echo "🎉 Deployment complete!"
echo ""
echo "The bot is now running and will automatically start on system boot."
echo "Monitor the bot with: ./status.sh"
