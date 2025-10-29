"""
Scheduling module for determining when to open/close positions.
"""
import time
import logging
from datetime import datetime, time as dt_time
from config import Config

logger = logging.getLogger(__name__)

class Scheduler:
    """Handles trading schedule and timing."""
    
    def __init__(self):
        self.open_time = self._parse_time(Config.OPEN_TIME)
        self.close_time = self._parse_time(Config.CLOSE_TIME)
        self.last_trading_day = None
    
    def _parse_time(self, time_str: str) -> dt_time:
        """Parse time string to time object."""
        return datetime.strptime(time_str, "%H:%M:%S").time()
    
    def should_open_positions(self) -> bool:
        """Check if it's time to open positions."""
        current_time = datetime.now(Config.TIMEZONE).time()
        current_date = datetime.now(Config.TIMEZONE).date()
        
        # Only open if we haven't traded today
        if self.last_trading_day == current_date:
            return False
        
        # Check if current time is within 1 minute of open time
        time_diff = abs((datetime.combine(current_date, current_time) - 
                        datetime.combine(current_date, self.open_time)).total_seconds())
        
        return time_diff <= 60
    
    def should_close_positions(self) -> bool:
        """Check if it's time to close positions."""
        current_time = datetime.now(Config.TIMEZONE).time()
        current_date = datetime.now(Config.TIMEZONE).date()
        
        # Only close if we opened positions today
        if self.last_trading_day != current_date:
            return False
        
        # Check if current time is within 1 minute of close time
        time_diff = abs((datetime.combine(current_date, current_time) - 
                        datetime.combine(current_date, self.close_time)).total_seconds())
        
        return time_diff <= 60
    
    def get_next_check_interval(self) -> int:
        """Get seconds to wait until next check."""
        current_time = datetime.now(Config.TIMEZONE).time()
        current_date = datetime.now(Config.TIMEZONE).date()
        
        # Check every 30 seconds when near trading times
        if self.is_near_trading_time():
            return 30
        else:
            return 60
    
    def is_near_trading_time(self) -> bool:
        """Check if we're within 5 minutes of any trading time."""
        current_time = datetime.now(Config.TIMEZONE).time()
        current_date = datetime.now(Config.TIMEZONE).date()
        
        # Check open time
        open_diff = abs((datetime.combine(current_date, current_time) - 
                        datetime.combine(current_date, self.open_time)).total_seconds())
        
        # Check close time (only if we have positions)
        close_diff = abs((datetime.combine(current_date, current_time) - 
                         datetime.combine(current_date, self.close_time)).total_seconds())
        
        return open_diff <= 300 or (self.last_trading_day == current_date and close_diff <= 300)
    
    def mark_trading_day(self, date):
        """Mark that we traded on this day."""
        self.last_trading_day = date
    
    def reset_trading_day(self):
        """Reset trading day (for new day)."""
        self.last_trading_day = None