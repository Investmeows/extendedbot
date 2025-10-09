# Extended Exchange Trading Bot

Automated delta-neutral trading bot for Extended Exchange that executes daily BTC long / ETH short positions.

## 🚀 Production Ready

**Strategy**: Daily BTC long + ETH short positions with market orders  
**Schedule**: Configurable open/close times via `.env`  
**Deployment**: AWS EC2 with CloudWatch logging  
**Safety**: Dead man's switch, kill switch, retry logic  

## Quick Start

### 1. Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.template .env
# Edit .env with your API credentials
```

### 2. Environment Variables
```bash
# Required API credentials
EXTENDED_API_KEY=your_api_key
EXTENDED_STARK_KEY=your_stark_key
EXTENDED_STARK_PUBLIC_KEY=your_stark_public_key
EXTENDED_VAULT_NUMBER=your_vault_number
EXTENDED_CLIENT_ID=your_client_id

# Trading configuration
TARGET_SIZE=5.0   #USD terms
BTC_LEVERAGE=10
ETH_LEVERAGE=10
OPEN_TIME=00:00:00
CLOSE_TIME=23:59:30
TIMEZONE=Asia/Bangkok
```

### 3. Run Bot
```bash
# Direct execution
python main.py

# Scheduled execution
python scheduler.py
```

## AWS Deployment

### 1. EC2 Setup
```bash
# Launch Ubuntu EC2 instance
# Run setup script
curl -O https://raw.githubusercontent.com/your-repo/extendedbot/main/aws_setup.sh
chmod +x aws_setup.sh
./aws_setup.sh
```

### 2. Configure
```bash
# Copy .env to server
scp .env user@your-ec2-ip:/opt/extended-bot/

# Configure AWS
aws configure
```

### 3. Start Service
```bash
# Test first
python main.py

# Enable service
sudo systemctl enable extended-bot.service
sudo systemctl start extended-bot.service
```

### 4. Monitor
```bash
# Check status
sudo systemctl status extended-bot.service

# View logs
journalctl -u extended-bot.service -f

# Use monitoring script
./monitor.sh
```

## Trading Logic

**Daily Cycle:**
- **00:00:00**: Open Long BTC + Short ETH (market orders)
- **23:59:30**: Close all positions (market orders)
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