# Extended Exchange Trading Bot

Automated delta-neutral trading bot for Extended Exchange that executes daily BTC long / ETH short positions.

## If you need help can DM Toshi (if you found this repo you know how to DM him..)

## Quick Start

### 1. Get API Credentials

1. Go to [https://app.extended.exchange/api-management](https://app.extended.exchange/api-management)
2. Create a new API Key
3. Copy your API Key, Starknet Private Key, Starknet Public Key, and Vault ID

### 2. Create DigitalOcean Droplet

1. Go to [https://cloud.digitalocean.com/droplets](https://cloud.digitalocean.com/droplets)
2. Click **"Create Droplet"**
3. Configure:
   - **Image**: Ubuntu 24.04
   - **Droplet type**: Regular
   - **Plan**: $6/month
   - **Authentication**: SSH key
   - **Name**: lowercase, no spaces (e.g., `extended-bot`)
4. Note your droplet's **IPv4 address**

### 3. Connect and Deploy

**Note**: Replace `your-username` in the URLs below with your actual GitHub username.

```bash
# Connect to your droplet
ssh root@[droplet_ipv4_address]

# Download and run setup script
curl -O https://raw.githubusercontent.com/your-username/extendedbot/main/do_setup.sh
chmod +x do_setup.sh
./do_setup.sh

# Log out and reconnect
exit
ssh root@[droplet_ipv4_address]

# Clone repository
git clone https://github.com/your-username/extendedbot.git
cd extendedbot

# Configure environment
# Copy the example file to create your .env file
cp .env.example .env
# Edit .env and add your API credentials from step 1
# You need to fill in: EXT_API_KEY, L2_PUBLIC_KEY, EXT_L2_KEY, and EXT_L2_VAULT
sudo nano .env

# Tip: If you're not familiar with editing in nano, ask AI (ChatGPT, Claude, etc.) 
# "I am editing a .env file in nano and need to add my API credentials. How do I navigate, edit text, save, and exit in nano?"


# Deploy
./do_deploy.sh
```

**Important**: In `.env`, use format `KEY=value` (no spaces, no quotes, no parentheses)

### 4. Verify

```bash
# Check status
docker compose ps

# View logs
docker compose logs -f
```

## Management Commands

```bash
# Start/Stop
./start_bot.sh
./stop_bot.sh

# Status
./status.sh

# Update
cd extendedbot
git pull origin main
docker compose build --no-cache
docker compose down && docker compose up -d
```

## Disclaimer

This software is for educational purposes only. Trading cryptocurrencies involves substantial risk of loss. Use at your own risk.
