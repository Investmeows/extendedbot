"""
Scheduler for running the trading bot on a daily schedule.
"""
import schedule
import time
import logging
from trading_bot import TradingBot
from config import Config

logger = logging.getLogger(__name__)

class BotScheduler:
    """Scheduler for the trading bot."""
    
    def __init__(self):
        self.bot = TradingBot()
        self.bot.initialize()
    
    def open_positions_job(self):
        """Job to open positions at market open."""
        logger.info("Executing open positions job")
        try:
            success = self.bot.open_positions()
            if success:
                logger.info("Open positions job completed successfully")
            else:
                logger.error("Open positions job failed")
        except Exception as e:
            logger.error(f"Open positions job error: {e}")
    
    def close_positions_job(self):
        """Job to close positions at market close."""
        logger.info("Executing close positions job")
        try:
            success = self.bot.close_positions()
            if success:
                logger.info("Close positions job completed successfully")
            else:
                logger.error("Close positions job failed")
        except Exception as e:
            logger.error(f"Close positions job error: {e}")
    
    def status_check_job(self):
        """Job to check and log current status."""
        logger.info("Executing status check job")
        try:
            positions = self.bot.get_current_positions()
            if positions:
                logger.info(f"Current positions: {positions}")
            else:
                logger.info("No open positions")
        except Exception as e:
            logger.error(f"Status check job error: {e}")
    
    def setup_schedule(self):
        """Set up the daily trading schedule."""
        # Schedule position opening at market open
        schedule.every().day.at(Config.OPEN_TIME).do(self.open_positions_job)
        
        # Schedule position closing at market close
        schedule.every().day.at(Config.CLOSE_TIME).do(self.close_positions_job)
        
        # Schedule status checks every hour
        schedule.every().hour.do(self.status_check_job)
        
        logger.info(f"Scheduled open positions at {Config.OPEN_TIME}")
        logger.info(f"Scheduled close positions at {Config.CLOSE_TIME}")
        logger.info("Scheduled status checks every hour")
    
    def run(self):
        """Run the scheduler."""
        logger.info("Starting bot scheduler...")
        self.setup_schedule()
        
        while True:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
            except KeyboardInterrupt:
                logger.info("Scheduler stopped by user")
                break
            except Exception as e:
                logger.error(f"Scheduler error: {e}")
                time.sleep(60)

def main():
    """Main function for the scheduler."""
    from logger import setup_logging
    
    # Set up logging
    setup_logging()
    
    # Create and run scheduler
    scheduler = BotScheduler()
    scheduler.run()

if __name__ == "__main__":
    main()
