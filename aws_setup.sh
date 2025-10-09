#!/bin/bash

# AWS EC2 setup script for Extended Exchange trading bot
# Run this script on a fresh Ubuntu EC2 instance

set -e

echo "Setting up Extended Exchange trading bot on AWS EC2..."

# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.10+
sudo apt install -y python3.10 python3.10-venv python3-pip

# Install system dependencies
sudo apt install -y git curl wget unzip

# Create application directory
sudo mkdir -p /opt/extended-bot
sudo chown $USER:$USER /opt/extended-bot
cd /opt/extended-bot

# Clone or copy the bot code (assuming it's already here)
# If not, you would clone from your repository:
# git clone <your-repo-url> .

# Create virtual environment
python3.10 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Install AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
rm -rf aws awscliv2.zip

# Set timezone to Asia/Bangkok
sudo timedatectl set-timezone Asia/Bangkok

# Create systemd service file
sudo tee /etc/systemd/system/extended-bot.service > /dev/null <<EOF
[Unit]
Description=Extended Exchange Trading Bot
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=/opt/extended-bot
Environment=PATH=/opt/extended-bot/venv/bin
ExecStart=/opt/extended-bot/venv/bin/python /opt/extended-bot/scheduler.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Create environment file template
cat > .env.template <<EOF
# Extended Exchange API Configuration
EXTENDED_API_KEY=your_api_key_here
EXTENDED_STARK_KEY=your_stark_key_here
EXTENDED_VAULT_NUMBER=your_vault_number_here
EXTENDED_BASE_URL=https://api.extended.exchange

# AWS Configuration
AWS_REGION=us-east-1
AWS_LOG_GROUP=extended-bot-logs

# Trading Configuration
BTC_QUANTITY=0.01
ETH_QUANTITY=0.1
BTC_LEVERAGE=10
ETH_LEVERAGE=10
TIMEZONE=Asia/Bangkok

# Safety Configuration
DEAD_MAN_SWITCH_ENABLED=true
MAX_RETRY_ATTEMPTS=3
EOF

# Create log directory
mkdir -p logs

# Set up CloudWatch logs
aws logs create-log-group --log-group-name extended-bot-logs --region us-east-1 || true

# Create startup script
cat > start_bot.sh <<EOF
#!/bin/bash
cd /opt/extended-bot
source venv/bin/activate
python scheduler.py
EOF

chmod +x start_bot.sh

# Create monitoring script
cat > monitor.sh <<EOF
#!/bin/bash
echo "=== Extended Bot Status ==="
echo "Service status:"
systemctl status extended-bot.service
echo ""
echo "Recent logs:"
journalctl -u extended-bot.service -n 20 --no-pager
echo ""
echo "Current time: \$(date)"
echo "Timezone: \$(timedatectl show --property=Timezone --value)"
EOF

chmod +x monitor.sh

echo "Setup complete!"
echo ""
echo "Next steps:"
echo "1. Copy your .env file with API credentials"
echo "2. Configure AWS credentials: aws configure"
echo "3. Test the bot: python main.py"
echo "4. Enable the service: sudo systemctl enable extended-bot.service"
echo "5. Start the service: sudo systemctl start extended-bot.service"
echo "6. Monitor with: ./monitor.sh"
