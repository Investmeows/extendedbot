# 🤖 Complete Beginner's Guide: Setting Up Your Trading Bot

**Don't worry if you've never coded before!** This guide will walk you through everything step-by-step, like you're learning to ride a bike for the first time. 🚴

---

## 📋 What This Bot Does (In Simple Terms)

This bot automatically trades cryptocurrency baskets for you, every single day. It:
- Opens long positions on your configured assets when the market opens
- Opens short positions on your configured assets at the same time
- Closes all positions when the market closes
- Does this automatically, 24/7, without you doing anything



---

## ⚠️ Important Before You Start

- **This costs about $6/month** to run (for the computer server)
- **You need money in your Extended Exchange account** to trade with
- **Trading has risks** - you could lose money. Only use money you can afford to lose
- **This takes about 30-60 minutes** to set up the first time

---

## 🎯 Step 1: Sign Up for Extended Exchange

**First, you need an account on Extended Exchange to trade.**

1. **Go to Extended Exchange** using this link: **https://app.extended.exchange/join/TOSHI**
   - This link helps support the bot developer & entitles you to reach out w/ questions! 💙

2. **Create your account**
   - Click "Sign Up" or "Create Account"
   - Enter your email and create a password
   - Follow the instructions to verify your email

3. **Add money to your account** (if you haven't already)
   - You'll need some USDT or other supported cryptocurrency
   - This is the money the bot will use to trade

---

## 🔑 Step 2: Get Your API Keys (Like a Password for the Bot)

**API keys are like special passwords that let the bot trade for you. Here's how to get them:**

1. **Log into Extended Exchange**
   - Go to: https://app.extended.exchange/api-management
   - Make sure you're logged in!

2. **Create a new API Key**
   - Look for a button that says "Create API Key" or "New API Key"
   - Click it!

3. **Copy these 4 things** (you'll need them later):
   - **API Key** - looks like a long string of letters and numbers
   - **Starknet Private Key** - also a long string
   - **Starknet Public Key** - another long string
   - **Vault ID** - usually a number like "1" or "2"

4. **Save them somewhere safe!**
   - Write them down in a text file on your computer
   - Or copy them to a notes app
   - **Don't share these with anyone!** They're like your password.

**💡 Tip:** Keep a text file open on your computer with these 4 things. You'll need to copy-paste them later.

---

## 💻 Step 3: Get a Computer Server (DigitalOcean)

**The bot needs to run on a computer that's always on. We'll rent one for $6/month.**

### 3A. Create a DigitalOcean Account

1. **Go to DigitalOcean** using this link will give you $200 in credit for your first 60 days: **https://m.do.co/c/26409a45c0ac**
-it's a ref link
2. **Click "Sign Up"** (top right corner)
3. **Create your account** with your email
4. **Add a payment method** (credit card)
   - Don't worry, you can cancel anytime
   - It's only $6/month

### 3B. Create Your Server (They Call It a "Droplet")

1. **After logging in, click "Create"** (top right) → **"Droplets"**

2. **Choose your settings:**
   - **Image/Operating System:** Click "Ubuntu" → Choose **"Ubuntu 24.04"**
   - **Plan:** Click the **$6/month** option (should say "Regular" with "1 GB RAM")
   - **Authentication:** Choose **"SSH keys"** or **"Password"**
     - If you choose password, create a strong password and save it!
   - **Name your droplet:** Type something like `my-trading-bot` (lowercase, no spaces)

3. **Click "Create Droplet"** (green button at the bottom)
   - Wait 1-2 minutes for it to finish creating

4. **Copy your server's IP address**
   - After it's created, you'll see an IPv4 address like `123.45.67.89`
   - **Copy this number!** You'll need it in the next step.

---

## 🔌 Step 4: Connect to Your Server

**Now we need to "talk" to your server using your computer. This is like calling it on the phone.**

### 💻 **On Your Computer:**

1. **Open Terminal/Command Prompt:**
   - **Windows:** Open PowerShell or Command Prompt (search for "PowerShell" or "cmd" in Start menu)
   - **Mac:** Open Terminal (search for "Terminal" in Spotlight)
   - **Linux:** Open Terminal (usually Ctrl+Alt+T)

2. **Type this command** (replace `123.45.67.89` with YOUR IP address):
   ```bash
   ssh root@123.45.67.89
   ```

3. **Press Enter**
   - If it asks "Are you sure you want to continue connecting?" type `yes` and press Enter
   - Enter your password when asked (the one you created when setting up the droplet)
   - **Note:** When you type the password, you won't see any characters appear - this is normal! Just type it and press Enter.

**✅ Success!** You should see something like `root@your-server-name:~#` - this means you're connected!

---

### 📌 **IMPORTANT: Understanding Where to Run Commands**

**From now on, pay attention to these icons:**

- **🖥️ = Run this command ON YOUR SERVER** (in the SSH terminal window you just opened)
- **💻 = Do this ON YOUR COMPUTER** (in your regular browser, file explorer, or local terminal)

**Most commands from Step 5 onwards are run 🖥️ ON YOUR SERVER!**

If you see a command in a code block without an icon, assume it's **🖥️ on your server** unless stated otherwise.

---

## 📥 Step 5: Install the Bot on Your Server

**Now we'll download and set up the bot software. Just copy and paste these commands one at a time.**

**🖥️ All commands in this step are run ON YOUR SERVER (in the SSH terminal window you just opened)**

### 5A. Install the Setup Tools

**🖥️ In your SSH terminal window**, copy and paste this command, then press Enter:
```bash
curl -O https://raw.githubusercontent.com/YOUR_GITHUB_USERNAME/extendedbot/main/scripts/do_setup.sh
```
*(Replace `YOUR_GITHUB_USERNAME` with the actual GitHub username where this code is hosted)*

**🖥️ Still in your SSH terminal window**, then run:
```bash
chmod +x do_setup.sh
./do_setup.sh
```

**This will take 5-10 minutes.** It's installing all the software the bot needs. Just wait until it says "Setup complete!"

### 5B. Disconnect and Reconnect

**🖥️ In your SSH terminal window**, type:
```bash
exit
```

**💻 Now on your computer**, reconnect using the same method from Step 4:
- Open Terminal/PowerShell/Command Prompt again
- Run: `ssh root@your-ip-address` (replace with your actual IP)

### 5C. Download the Bot Code

**🖥️ Back in your SSH terminal window**, copy and paste these commands one at a time:
```bash
git clone https://github.com/YOUR_GITHUB_USERNAME/extendedbot.git
cd extendedbot
```
*(Again, replace `YOUR_GITHUB_USERNAME` with the actual username)*

---

## ⚙️ Step 6: Configure the Bot (Add Your API Keys & Trading Pairs)

**This is where you tell the bot your API keys and which assets to trade.**

**🖥️ All commands in this step are run ON YOUR SERVER (in the SSH terminal window)**

1. **🖥️ In your SSH terminal window**, create the configuration file:
   ```bash
   cp .env.example .env
   ```

2. **🖥️ Still in your SSH terminal window**, open the file to edit it:
   ```bash
   nano .env
   ```

3. **You'll see a file with lots of lines. Fill in these required settings:**

   **API Credentials (from Step 2):**
   ```
   EXT_API_KEY=your_api_key_here
   EXT_L2_KEY=your_starknet_private_key_here
   EXT_L2_VAULT=your_vault_id_here
   EXT_L2_PUBLIC_KEY=your_starknet_public_key_here
   ```

   **Trading Configuration (basket-based):**
   ```
   LONG_PAIR1=BTC-USD
   LONG_PAIR1_TARGET_SIZE=1500.0
   
   SHORT_PAIR1=ETH-USD
   SHORT_PAIR1_TARGET_SIZE=1500.0
   
   LONG_LEVERAGE=10
   SHORT_LEVERAGE=10
   
   OPEN_TIME=21:30:30
   CLOSE_TIME=18:30:30
   TIMEZONE=UTC
   ```

   **To add more pairs, use numbered format:**
   ```
   LONG_PAIR2=SOL-USD
   LONG_PAIR2_TARGET_SIZE=1000.0
   SHORT_PAIR2=AVAX-USD
   SHORT_PAIR2_TARGET_SIZE=800.0
   ```

4. **How to edit in nano:**
   - Use your arrow keys to move around
   - Delete the text after the `=` sign
   - Type (or paste) your actual values
   - **Important:** No spaces! It should look like: `EXT_API_KEY=abc123xyz`
   - Each pair must have a corresponding `*_TARGET_SIZE` (e.g., `LONG_PAIR1` needs `LONG_PAIR1_TARGET_SIZE`)

5. **Save and exit:**
   - Press `Ctrl + X` (hold Control, press X)
   - Press `Y` (to confirm yes)
   - Press `Enter` (to confirm the filename)

**💡 Stuck?** Ask ChatGPT or Claude: "I'm editing a file in nano and need to save and exit. How do I do that?"

---

## 🚀 Step 7: Start the Bot!

**Almost done! Now let's start the bot running.**

**🖥️ In your SSH terminal window**, run this command:
```bash
./scripts/do_deploy.sh
```

**This will:**
- Test your configuration
- Build the bot
- Start it running

Wait for it to say "✅ Bot started successfully!"

---

## ✅ Step 8: Check That It's Working

**Let's make sure everything is running correctly.**

**🖥️ In your SSH terminal window**, run this command:
```bash
docker compose ps
```

**You should see something like:**
```
NAME                  STATUS
extended-trading-bot  Up 2 minutes
```

If you see "Up", **you're all set!** 🎉

**🖥️ To see what the bot is doing (still in your SSH terminal window):**
```bash
docker compose logs -f
```

This shows you live updates. Press `Ctrl + C` to stop watching.

---

## 📊 Daily Use: What Happens Now?

**The bot is now running automatically!** It will:
- ✅ Check the time every minute
- ✅ Open positions when the market opens (based on your OPEN_TIME setting)
- ✅ Close positions when the market closes (based on your CLOSE_TIME setting)
- ✅ Run 24/7 without you doing anything

**You can check on it anytime by:**
1. **💻 On your computer:** Connect to your server (Step 4)
2. **🖥️ On your server (in SSH terminal):** Run: `docker compose logs -f`

---

## 🛠️ Common Commands You Might Need

**🖥️ All these commands are run ON YOUR SERVER (in your SSH terminal window)**

**Stop the bot:**
```bash
docker compose down
```

**Start the bot again:**
```bash
docker compose up -d
```

**See what the bot is doing right now:**
```bash
docker compose logs -f
```

**Check if it's running:**
```bash
docker compose ps
```

---

## ❓ Troubleshooting

### "I'm stuck on a step"
- Ask ChatGPT or Claude for help with that specific step

### "Configuration validation failed"
- Check that all 4 API keys are in your `.env` file
- Make sure there are no spaces around the `=` sign
- Verify each pair has a corresponding `*_TARGET_SIZE` (e.g., `LONG_PAIR1` needs `LONG_PAIR1_TARGET_SIZE`)
- Ensure at least one pair is configured (LONG_PAIR1 or SHORT_PAIR1)

### "No pairs configured"
- Make sure you have at least `LONG_PAIR1` or `SHORT_PAIR1` set
- Each pair must have a corresponding target size (e.g., `LONG_PAIR1_TARGET_SIZE=1500.0`)

---

## 💰 Cost Breakdown

- **DigitalOcean server:** $6/month
- **Extended Exchange trading fees:** Small percentage per trade (check their fee schedule)
- **Total:** About $6-10/month depending on trading activity

**You can cancel anytime!** Just delete your DigitalOcean droplet.

---

## 🎓 What Each Setting Does (Optional Reading)

In your `.env` file, you'll see these settings:

**API Credentials:**
- **EXT_API_KEY:** Your Extended Exchange API key
- **EXT_L2_KEY:** Your Starknet private key
- **EXT_L2_VAULT:** Your vault ID
- **EXT_L2_PUBLIC_KEY:** Your Starknet public key

**Trading Pairs (Basket-based):**
- **LONG_PAIR1, LONG_PAIR2, etc.:** Asset symbols to go long (e.g., `BTC-USD`, `SOL-USD`)
- **LONG_PAIR1_TARGET_SIZE, LONG_PAIR2_TARGET_SIZE, etc.:** Target notional size in USD for each long position
- **SHORT_PAIR1, SHORT_PAIR2, etc.:** Asset symbols to go short (e.g., `ETH-USD`, `AVAX-USD`)
- **SHORT_PAIR1_TARGET_SIZE, SHORT_PAIR2_TARGET_SIZE, etc.:** Target notional size in USD for each short position

**Leverage:**
- **LONG_LEVERAGE:** Leverage multiplier for all long positions (e.g., `10` = 10x)
- **SHORT_LEVERAGE:** Leverage multiplier for all short positions (e.g., `10` = 10x)

**Schedule:**
- **OPEN_TIME:** When to open positions (format: `HH:MM:SS` like `21:30:30`)
- **CLOSE_TIME:** When to close positions (format: `HH:MM:SS` like `18:30:30`)
- **TIMEZONE:** Timezone for schedule (usually `UTC`)

**Don't change these unless you know what you're doing!**

---

## ⚠️ Final Reminders

1. **Keep your API keys secret!** Never share them with anyone.
2. **Check on your bot occasionally** to make sure it's running.
3. **The bot runs automatically** - you don't need to do anything after setup.
4. **If something breaks**, **🖥️ on your server (in SSH terminal)** check the logs first: `docker compose logs -f`

---

## 🎉 Congratulations!

You've set up an automated trading bot! It's now running 24/7, trading for you automatically.

**Remember:** Trading has risks. Monitor it occasionally and only use money you can afford to lose.

---

## 📞 Need Help?

- **Technical issues:** **🖥️ On your server (in SSH terminal)** check the logs with `docker compose logs -f`
- **Setup questions:** Ask ChatGPT or Claude for help with specific steps

---

**Happy Trading! 🚀**
