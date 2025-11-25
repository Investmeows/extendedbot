"""
Clean, modular trading bot for delta neutral BTC/ETH strategy.
"""
import time
import logging
import asyncio
from datetime import datetime, timedelta
from src.clients.extended_sdk_client import ExtendedSDKClient
from src.managers.order_manager import OrderManager
from src.managers.position_manager import PositionManager
from src.utils.scheduler import Scheduler
from src.config import Config

logger = logging.getLogger(__name__)

class TradingBot:
    """Clean, modular trading bot."""
    
    def __init__(self):
        self.client = ExtendedSDKClient()
        self.loop = None
        self.is_running = False
        
        # Initialize managers
        self.order_manager = None
        self.position_manager = None
        self.scheduler = Scheduler()
        
        # Bot state
        self.bot_state = "WAITING"  # WAITING, OPENING, OPEN, CLOSING
        self.last_state_log = None
        self.last_hourly_log = None
    
    def initialize(self):
        """Initialize the bot."""
        try:
            logger.info("Initializing trading bot...")
            
            # Setup event loop
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            
            # Initialize managers
            self.order_manager = OrderManager(self.client)
            self.position_manager = PositionManager()
            
            # Set leverage for configured pairs
            self.loop.run_until_complete(
                self.client.client.account.update_leverage(Config.LONG_PAIR, Config.LONG_LEVERAGE)
            )
            self.loop.run_until_complete(
                self.client.client.account.update_leverage(Config.SHORT_PAIR, Config.SHORT_LEVERAGE)
            )
            
            # Initialize state
            self._initialize_state()
            
            # Initialize logging state
            self.last_state_log = self.bot_state
            self.last_hourly_log = datetime.now(Config.TIMEZONE)
            
            logger.info("Bot initialization complete")
            
        except Exception as e:
            logger.error(f"Failed to initialize bot: {e}")
            raise
    
    def _initialize_state(self):
        """Initialize bot state based on current positions."""
        positions = self.position_manager.get_current_positions()
        current_date = datetime.now(Config.TIMEZONE).date()
        
        if self.position_manager.is_delta_neutral(positions):
            self.bot_state = "OPEN"
            # Mark trading day, but use a conservative approach for stale positions
            # If close_time < open_time, conservatively assume positions were opened yesterday
            # This ensures should_close_positions() will trigger if we're past close time
            # Parse times to compare properly
            close_time = datetime.strptime(Config.CLOSE_TIME, "%H:%M:%S").time()
            open_time = datetime.strptime(Config.OPEN_TIME, "%H:%M:%S").time()
            if close_time < open_time:
                # Cross-day scenario: assume positions were opened yesterday (or earlier)
                # This way, if today is past close time, we'll close immediately
                # Use yesterday to ensure we're past expected close date calculation
                self.scheduler.mark_trading_day(current_date - timedelta(days=1))
            else:
                # Same-day scenario: assume positions were opened today
                self.scheduler.mark_trading_day(current_date)
            logger.info("Delta neutral positions found - state: OPEN")
            logger.info(f"Marked trading day as: {self.scheduler.last_trading_day} (conservative for stale positions)")
        else:
            self.bot_state = "WAITING"
            logger.info("No delta neutral positions - state: WAITING")
    
    def start(self):
        """Start the trading bot main loop."""
        try:
            # Initialize the bot first
            self.initialize()
            
            self.is_running = True
            logger.info("Starting trading bot...")
            
            while self.is_running:
                try:
                    self._process_trading_cycle()
                except Exception as e:
                    logger.error(f"Error in trading cycle: {e}")
                
                # Wait before next check
                time.sleep(self.scheduler.get_next_check_interval())
                
        except KeyboardInterrupt:
            logger.info("Bot stopped by user")
        finally:
            self.stop()
    
    def _process_trading_cycle(self):
        """Process one trading cycle."""
        current_date = datetime.now(Config.TIMEZONE).date()
        current_time = datetime.now(Config.TIMEZONE)
        
        # Log state changes or hourly status
        should_log = False
        if self.bot_state != self.last_state_log:
            # Log state changes immediately
            should_log = True
            self.last_state_log = self.bot_state
        elif (self.last_hourly_log is None or 
              (current_time - self.last_hourly_log).total_seconds() >= 3600):
            # Log hourly status
            should_log = True
            self.last_hourly_log = current_time
        
        if should_log:
            logger.info(f"State: {self.bot_state}, Date: {current_date}")
        
        if self.bot_state == "WAITING":
            if self.scheduler.should_open_positions():
                self._open_positions()
        
        elif self.bot_state == "OPEN":
            if self.scheduler.should_close_positions():
                self._close_positions()
        
        elif self.bot_state == "OPENING":
            self._verify_opening()
        
        elif self.bot_state == "CLOSING":
            self._verify_closing()
    
    def _open_positions(self):
        """Open delta neutral positions."""
        try:
            logger.info("Opening delta neutral positions...")
            self.bot_state = "OPENING"
            
            success = self.order_manager.open_delta_neutral_positions(Config.TARGET_SIZE)
            
            if success:
                # Wait longer for positions to settle on the exchange
                logger.info("Waiting for positions to settle...")
                time.sleep(30)
                self._verify_opening()
            else:
                logger.error("Failed to open positions")
                self.bot_state = "WAITING"
                
        except Exception as e:
            logger.error(f"Error opening positions: {e}")
            self.bot_state = "WAITING"
    
    def _verify_opening(self):
        """Verify positions were opened successfully."""
        positions = self.position_manager.get_current_positions()
        
        # Log positions for debugging
        if positions:
            logger.info(f"Checking positions: {positions}")
            for market, pos_data in positions.items():
                logger.info(f"  {market}: size={pos_data['size']}, side={pos_data['side']}")
        else:
            logger.warning("No positions found after opening orders")
        
        # Single validation check (all logic in is_delta_neutral)
        if self.position_manager.is_delta_neutral(positions):
            self.bot_state = "OPEN"
            self.scheduler.mark_trading_day(datetime.now(Config.TIMEZONE).date())
            logger.info("✅ Delta neutral positions verified")
        else:
            logger.error(f"❌ Failed to achieve delta neutral positions: {positions}")
            # Retry once after additional wait
            logger.info("Retrying position verification in 5 seconds...")
            time.sleep(5)
            positions = self.position_manager.get_current_positions()
            
            if self.position_manager.is_delta_neutral(positions):
                self.bot_state = "OPEN"
                self.scheduler.mark_trading_day(datetime.now(Config.TIMEZONE).date())
                logger.info("✅ Delta neutral positions verified on retry")
            else:
                logger.error(f"❌ Still no delta neutral positions after retry: {positions}")
                self.bot_state = "WAITING"
    
    def _close_positions(self):
        """Close all positions."""
        try:
            logger.info("Closing all positions...")
            self.bot_state = "CLOSING"
            
            positions = self.position_manager.get_current_positions()
            success = self.order_manager.close_all_positions(positions)
            
            if success:
                # Wait longer for positions to close on the exchange
                logger.info("Waiting for positions to close...")
                time.sleep(30)
                self._verify_closing()
            else:
                logger.error("Failed to close positions")
                self.bot_state = "OPEN"
                
        except Exception as e:
            logger.error(f"Error closing positions: {e}")
            self.bot_state = "OPEN"
    
    def _verify_closing(self):
        """Verify positions were closed successfully."""
        positions = self.position_manager.get_current_positions()
        
        # Log actual positions for debugging
        if positions:
            logger.info(f"Remaining positions: {positions}")
        
        if not self.position_manager.has_positions(positions):
            self.bot_state = "WAITING"
            self.scheduler.reset_trading_day()
            logger.info("✅ All positions closed successfully")
        else:
            logger.error(f"❌ Failed to close all positions: {positions}")
            # Retry verification once more after additional wait
            logger.info("Retrying position verification in 5 seconds...")
            time.sleep(5)
            positions = self.position_manager.get_current_positions()
            if not self.position_manager.has_positions(positions):
                self.bot_state = "WAITING"
                self.scheduler.reset_trading_day()
                logger.info("✅ All positions closed successfully on retry")
            else:
                logger.error(f"❌ Still have positions after retry: {positions}")
                self.bot_state = "OPEN"
    
    def stop(self):
        """Stop the trading bot."""
        self.is_running = False
        logger.info("Trading bot stopped")
