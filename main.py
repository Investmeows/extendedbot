"""
Main entry point for the Extended Exchange trading bot.
"""
import sys
import signal
import time
from src.trading_bot import TradingBot
from src.logger import setup_logging
from src.config import Config
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
        logger.info(f"Strategy: Long {Config.LONG_PAIR} / Short {Config.SHORT_PAIR}")
        logger.info(f"Timezone: {Config.TIMEZONE}")
        logger.info(f"OPEN_TIME: {Config.OPEN_TIME}")
        logger.info(f"CLOSE_TIME: {Config.CLOSE_TIME}")
        logger.info(f"TARGET_SIZE: ${Config.TARGET_SIZE}")
        logger.info(f"LONG_LEVERAGE: {Config.LONG_LEVERAGE}x")
        logger.info(f"SHORT_LEVERAGE: {Config.SHORT_LEVERAGE}x")
        
        bot.start()
        
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
