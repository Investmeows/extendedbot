# Extended Exchange Trading Bot

A robust trading bot for Extended Exchange that executes daily long BTC-USD / short ETH-USD trades on AWS.

## 🚀 Production Status: READY FOR DEPLOYMENT

### **Core Files (Production Ready):**
- `main.py` - Main entry point
- `trading_bot.py` - Trading logic with position verification & retry
- `extended_sdk_client.py` - Official Extended Exchange SDK client
- `config.py` - Configuration management
- `logger.py` - Logging setup
- `scheduler.py` - Daily trading schedule
- `requirements.txt` - Dependencies

### **Deployment Files:**
- `aws_setup.sh` - AWS EC2 setup
- `deploy.sh` - Deployment script

## Features

- **Daily Trading Strategy**: Opens long BTC and short ETH positions at market open, closes at market close
- **AWS Deployment**: Runs on EC2 with CloudWatch logging
- **Risk Management**: Dead man's switch, position sizing, leverage control
- **Error Handling**: Comprehensive error handling and retry logic
- **Monitoring**: Real-time position tracking and logging

## 🎯 Production Features Verified

### **✅ Position Management:**
- **Opening**: BTC LONG + ETH SHORT ✅
- **Closing**: BTC SELL (close long) + ETH BUY (close short) ✅
- **Position Verification**: 5-second wait + verification ✅
- **Duplicate Prevention**: Checks existing positions ✅

### **✅ Error Handling:**
- **3-Retry Logic**: Automatic retry for failed orders ✅
- **Kill Switch**: Emergency close all positions ✅
- **Dead Man's Switch**: Cancel all orders on startup ✅
- **Robust Error Handling**: Comprehensive exception handling ✅

### **✅ Production Features:**
- **Official SDK**: Extended Exchange Python SDK ✅
- **Market Orders**: IOC orders with price buffers ✅
- **Timezone Support**: Asia/Bangkok timezone ✅
- **AWS Integration**: CloudWatch logging ✅
- **Clean Shutdown**: Graceful shutdown ✅

## Quick Start

### 1. Prerequisites

- Extended Exchange account with API access
- AWS account with EC2 and CloudWatch permissions
- Python 3.10+

### 2. Setup API Credentials

1. Create a sub-account in Extended Exchange UI
2. Generate API key, Stark key, and note vault number
3. Copy `.env.template` to `.env` and fill in your credentials:

```bash
cp .env.template .env
# Edit .env with your API credentials
```

### 3. AWS Deployment

1. Launch an Ubuntu EC2 instance (t3.micro or larger)
2. Run the setup script:

```bash
# On your EC2 instance
curl -O https://raw.githubusercontent.com/your-repo/extendedbot/main/aws_setup.sh
chmod +x aws_setup.sh
./aws_setup.sh
```

3. Configure your environment:

```bash
# Copy your .env file to the server
scp .env user@your-ec2-ip:/opt/extended-bot/

# Configure AWS credentials
aws configure
```

4. Start the bot:

```bash
# Test first
python main.py

# Enable and start the service
sudo systemctl enable extended-bot.service
sudo systemctl start extended-bot.service
```

### 4. Monitoring

```bash
# Check service status
sudo systemctl status extended-bot.service

# View logs
journalctl -u extended-bot.service -f

# Use the monitoring script
./monitor.sh
```

## 🚀 Deployment Commands

```bash
# Deploy to AWS
./deploy.sh

# Run main bot
python main.py

# Run with scheduler
python scheduler.py
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `EXTENDED_API_KEY` | Extended Exchange API key | Required |
| `EXTENDED_STARK_KEY` | Extended Exchange Stark key | Required |
| `EXTENDED_STARK_PUBLIC_KEY` | Extended Exchange Stark public key | Required |
| `EXTENDED_VAULT_NUMBER` | Extended Exchange vault number | Required |
| `EXTENDED_CLIENT_ID` | Extended Exchange client ID | Required |
| `BTC_QUANTITY` | BTC position size | 0.0001 |
| `ETH_QUANTITY` | ETH position size | 0.001 |
| `BTC_LEVERAGE` | BTC leverage multiplier | 10 |
| `ETH_LEVERAGE` | ETH leverage multiplier | 10 |
| `TIMEZONE` | Trading timezone | Asia/Bangkok |
| `DEAD_MAN_SWITCH_ENABLED` | Enable safety cancel-all | true |

### Trading Schedule

- **Open Time**: 00:00 (Asia/Bangkok timezone)
- **Close Time**: 23:59:30 (Asia/Bangkok timezone)
- **Strategy**: Long BTC-USD / Short ETH-USD

## 📊 Strategy
- **Daily BTC LONG / ETH SHORT**
- **Market open/close times configurable**
- **Leverage: 10x for both assets**
- **Minimum order sizes for cost efficiency**

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   AWS EC2       │    │  Extended API    │    │  CloudWatch     │
│                 │    │                  │    │                 │
│ ┌─────────────┐ │    │ ┌──────────────┐ │    │ ┌─────────────┐ │
│ │ Scheduler   │◄┼────┼►│ Authentication│ │    │ │ Logs        │ │
│ │             │ │    │ │              │ │    │ │             │ │
│ └─────────────┘ │    │ └──────────────┘ │    │ └─────────────┘ │
│ ┌─────────────┐ │    │ ┌──────────────┐ │    │                 │
│ │ Trading Bot │◄┼────┼►│ Order API    │ │    │                 │
│ │             │ │    │ │              │ │    │                 │
│ └─────────────┘ │    │ └──────────────┘ │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## Safety Features

### Dead Man's Switch
- Cancels all orders at startup
- Prevents stranded orders if bot crashes
- Configurable via `DEAD_MAN_SWITCH_ENABLED`

### Error Handling
- Retry logic for failed orders
- Position validation before closing
- Comprehensive logging

### Risk Management
- Configurable leverage per symbol
- Position sizing controls
- Market order emulation with price bounds

## API Endpoints Used

- `GET /api/v1/user/fees` - Get trading fees
- `GET /api/v1/user/positions` - Get current positions
- `PATCH /api/v1/user/leverage` - Set leverage
- `POST /api/v1/user/order` - Place orders
- `POST /api/v1/user/order/cancel-all` - Cancel all orders
- `GET /api/v1/market/orderbook` - Get market data

## Troubleshooting

### Common Issues

1. **Authentication Errors**
   - Verify API key, Stark key, and vault number
   - Check Extended Exchange account status

2. **Order Failures**
   - Insufficient margin
   - Position limits exceeded
   - Market data unavailable

3. **Service Issues**
   - Check systemd service status
   - Review CloudWatch logs
   - Verify timezone settings

### Logs

```bash
# Service logs
journalctl -u extended-bot.service -f

# CloudWatch logs
aws logs tail /aws/lambda/extended-bot-logs --follow
```

## Development

### Local Testing

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.template .env
# Edit .env with test credentials

# Run bot
python main.py
```

### Code Structure

```
extendedbot/
├── main.py              # Entry point
├── trading_bot.py       # Core trading logic
├── extended_sdk_client.py # Official SDK client
├── scheduler.py         # Daily scheduler
├── config.py           # Configuration
├── logger.py           # Logging setup
├── aws_setup.sh        # AWS deployment script
└── requirements.txt     # Dependencies
```

## ✅ Final Test Results
- ✅ Configuration validated
- ✅ Bot initialized successfully
- ✅ Position opening: BTC LONG + ETH SHORT correctly placed
- ✅ Position verification: Both positions correctly identified
- ✅ Position closing: Both positions correctly closed
- ✅ Final verification: All positions closed
- ✅ Kill switch: Working perfectly

**Status: PRODUCTION READY** 🚀

## License

MIT License - see LICENSE file for details.

## Disclaimer

This software is for educational purposes only. Trading cryptocurrencies involves substantial risk of loss. Use at your own risk.