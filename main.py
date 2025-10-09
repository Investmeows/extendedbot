"""
Main entry point for the Extended Exchange trading bot.
"""
import sys
import signal
import time
from trading_bot import TradingBot
from logger import setup_logging
from config import Config
import logging

# Set up logging
logger = setup_logging()

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    logger.info(f"Received signal {signum}, shutting down...")
    sys.exit(0)

def main():
    """Main function to run the trading bot."""
    try:
        # Validate configuration
        Config.validate_config()
        logger.info("Configuration validated successfully")
        
        # Set up signal handlers
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Create and start the trading bot
        bot = TradingBot()
        logger.info("Starting Extended Exchange trading bot...")
        logger.info(f"Strategy: Long BTC-USD / Short ETH-USD")
        logger.info(f"Timezone: {Config.TIMEZONE}")
        logger.info(f"Open time: {Config.OPEN_TIME}")
        logger.info(f"Close time: {Config.CLOSE_TIME}")
        
        bot.start()
        
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
