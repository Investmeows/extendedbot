#!/bin/bash

# Deployment script for Extended Exchange trading bot
# This script helps deploy the bot to AWS EC2

set -e

echo "Extended Exchange Trading Bot - Deployment Script"
echo "================================================="

# Check if we're on AWS EC2
if [ -f /sys/hypervisor/uuid ] && [ `head -c 3 /sys/hypervisor/uuid` == ec2 ]; then
    echo "✓ Running on AWS EC2"
else
    echo "⚠️  Not running on AWS EC2 - some features may not work"
fi

# Check Python version
python_version=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
required_version="3.10"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" = "$required_version" ]; then
    echo "✓ Python $python_version is compatible"
else
    echo "✗ Python $python_version is not compatible. Need 3.10+"
    exit 1
fi

# Install dependencies
echo "Installing Python dependencies..."
pip3 install -r requirements.txt

# Set up environment
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.template .env
    echo "⚠️  Please edit .env file with your API credentials before running the bot"
fi

# Test the bot
echo "Running bot tests..."
python3 test_bot.py

if [ $? -eq 0 ]; then
    echo "✓ Bot tests passed"
else
    echo "✗ Bot tests failed - please check configuration"
    exit 1
fi

# Set up systemd service (if on Linux)
if command -v systemctl &> /dev/null; then
    echo "Setting up systemd service..."
    
    # Create service file
    sudo tee /etc/systemd/system/extended-bot.service > /dev/null <<EOF
[Unit]
Description=Extended Exchange Trading Bot
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)
Environment=PATH=$(pwd)/venv/bin
ExecStart=$(which python3) $(pwd)/scheduler.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

    # Reload systemd
    sudo systemctl daemon-reload
    
    echo "✓ Systemd service created"
    echo "To start the bot: sudo systemctl start extended-bot.service"
    echo "To enable auto-start: sudo systemctl enable extended-bot.service"
else
    echo "⚠️  Systemd not available - bot will need to be started manually"
fi

echo ""
echo "Deployment complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your API credentials"
echo "2. Test the bot: python3 test_bot.py"
echo "3. Run the bot: python3 main.py"
echo "4. Or start the service: sudo systemctl start extended-bot.service"
