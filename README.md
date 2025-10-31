# Extended Exchange Trading Bot

Automated delta-neutral trading bot for Extended Exchange that executes daily BTC long / ETH short positions.

## 🚀 Production Ready

**Strategy**: Daily BTC long + ETH short positions with market orders  
**Schedule**: Configurable open/close times via `.env`  
**Deployment**: DigitalOcean Droplet with Docker (UTC timezone)  
**Safety**: Dead man's switch, kill switch, retry logic  

## Quick Start

### 1. Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.template .env
# Edit .env with your API credentials

# Run locally
python main.py
```

### 2. Docker Development
```bash
# Build and run with Docker
docker-compose up --build

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f
```

### 3. Environment Variables
```bash
# Required API credentials
EXTENDED_API_KEY=your_api_key
EXTENDED_STARK_KEY=your_stark_key
EXTENDED_STARK_PUBLIC_KEY=your_stark_public_key
EXTENDED_VAULT_NUMBER=your_vault_number
EXTENDED_CLIENT_ID=your_client_id

# Trading configuration
TARGET_SIZE=200.0   #USD terms
BTC_LEVERAGE=10
ETH_LEVERAGE=10
OPEN_TIME=00:00:00
CLOSE_TIME=23:59:30
TIMEZONE=UTC

# DigitalOcean configuration
DO_REGION=nyc1
DO_DROPLET_SIZE=s-1vcpu-1gb
```

## DigitalOcean Deployment

### 1. Create Droplet
- **Image**: Ubuntu 24.04 LTS
- **Size**: 1bg 25
- **Region**: Sydney
- **Authentication**: SSH key

### 2. Initial Setup
```bash
# Connect to your droplet
ssh root@your-droplet-ip

# Download and run setup script
curl -O https://raw.githubusercontent.com/your-repo/extendedbot/main/do_setup.sh
chmod +x do_setup.sh
./do_setup.sh

# Log out and back in for Docker permissions
exit
ssh root@your-droplet-ip
```

### 3. Deploy Bot
```bash
# Clone your repository
git clone https://github.com/your-username/extendedbot.git
cd extendedbot

# Configure environment
cp .env.template .env
nano .env  # Edit with your API credentials

# Deploy
./do_deploy.sh
```

### 4. Management Commands
```bash
# Start bot
./start_bot.sh

# Stop bot
./stop_bot.sh

# Check status
./status.sh

# View logs
docker-compose logs -f

# Update bot
./update_bot.sh

# Create backup
./backup.sh
```

### 5. Monitoring
```bash
# View logs
docker-compose logs -f

# Check container status
docker-compose ps

# View system resources
docker stats
```

## Trading Logic

**Daily Cycle:**
- **21:30:30**: Open Long BTC + Short ETH (market orders)
- **18:30:30**: Close all positions (market orders)
(close during the most volatility ridden times of 2-4am UTC+7)
- **Every minute**: Check time and positions
- **Every hour**: Status logging

**Position Sizing:**
- Delta-neutral: Equal USD value for both positions
- Leverage: 10x on both assets
- Size: Configurable via `TARGET_SIZE`

## Safety Features

- **Dead Man's Switch**: Cancels all orders on startup
- **Kill Switch**: Emergency close all positions
- **Retry Logic**: 3 attempts for failed orders
- **Duplicate Prevention**: Checks existing positions
- **Position Verification**: 5-second wait + verification

## Files

```
extendedbot/
├── main.py              # Entry point
├── trading_bot.py       # Core trading logic
├── extended_sdk_client.py # Official SDK client
├── scheduler.py         # Daily scheduler
├── config.py           # Configuration
├── logger.py           # Logging setup
├── aws_setup.sh        # AWS deployment
├── deploy.sh           # Deployment script
└── requirements.txt    # Dependencies
```

## Troubleshooting

**Common Issues:**
- Authentication: Verify API credentials
- Orders: Check margin and position limits
- Service: Check systemd status and logs

**Logs:**
```bash
# Service logs
journalctl -u extended-bot.service -f

# CloudWatch logs
aws logs tail /aws/lambda/extended-bot-logs --follow
```

## License

MIT License - see LICENSE file for details.

## Disclaimer

This software is for educational purposes only. Trading cryptocurrencies involves substantial risk of loss. Use at your own risk.