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
        
        # Display configured pairs
        long_pairs = Config.get_all_long_pairs()
        short_pairs = Config.get_all_short_pairs()
        
        if long_pairs:
            logger.info("Long pairs:")
            for pair_config in long_pairs:
                logger.info(f"  {pair_config['pair']}: ${pair_config['target_size']:.2f} (leverage: {Config.LONG_LEVERAGE}x)")
        else:
            logger.warning("No long pairs configured. Set LONG_PAIR1, LONG_PAIR2, etc. with corresponding *_TARGET_SIZE values.")
        
        if short_pairs:
            logger.info("Short pairs:")
            for pair_config in short_pairs:
                logger.info(f"  {pair_config['pair']}: ${pair_config['target_size']:.2f} (leverage: {Config.SHORT_LEVERAGE}x)")
        else:
            logger.warning("No short pairs configured. Set SHORT_PAIR1, SHORT_PAIR2, etc. with corresponding *_TARGET_SIZE values.")
        
        logger.info(f"Timezone: {Config.TIMEZONE}")
        logger.info(f"OPEN_TIME: {Config.OPEN_TIME}")
        logger.info(f"CLOSE_TIME: {Config.CLOSE_TIME}")
        
        bot.start()
        
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
