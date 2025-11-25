"""
Scheduling module for determining when to open/close positions.
"""
import logging
from datetime import datetime, timedelta, time as dt_time
from src.config import Config

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
        # Make timezone-aware datetimes
        current_datetime = Config.TIMEZONE.localize(datetime.combine(current_date, current_time))
        open_datetime = Config.TIMEZONE.localize(datetime.combine(current_date, self.open_time))
        time_diff = abs((current_datetime - open_datetime).total_seconds())
        
        return time_diff <= 60
    
    def should_close_positions(self) -> bool:
        """Check if it's time to close positions."""
        current_datetime = datetime.now(Config.TIMEZONE)
        current_time = current_datetime.time()
        current_date = current_datetime.date()
        
        # Must have opened positions (last_trading_day is set)
        if self.last_trading_day is None:
            return False
        
        # Handle cross-day scenario (close time is earlier than open time)
        # If close_time < open_time, close happens on the day after open
        if self.close_time < self.open_time:
            # Close time is next day - check if we're on or past the close time
            # on the day after last_trading_day
            expected_close_date = self.last_trading_day + timedelta(days=1)
            
            # If we're past the expected close date, always close
            if current_date > expected_close_date:
                return True
            
            # If we're on the expected close date, check if time has passed
            if current_date == expected_close_date:
                # Check if current time is at or past close time (with 1 minute window before)
                # Make timezone-aware datetime
                close_datetime = Config.TIMEZONE.localize(datetime.combine(current_date, self.close_time))
                time_diff = (current_datetime - close_datetime).total_seconds()
                # Close if we're within 1 minute before or any time after
                return time_diff >= -60
            
            # If we're before the expected close date, don't close yet
            # (this handles the case where we opened today and close is tomorrow)
            return False
        else:
            # Close time is same day as open - check if we're on the same day
            if self.last_trading_day != current_date:
                # If we're past the trading day, we should have closed - trigger close
                # This handles cases where close was missed or bot was restarted
                if current_date > self.last_trading_day:
                    return True
                # If current_date < last_trading_day (shouldn't happen, but defensive)
                return False
            
            # On the same day - check if we're at or past close time
            # Make timezone-aware datetime
            close_datetime = Config.TIMEZONE.localize(datetime.combine(current_date, self.close_time))
            time_diff = (current_datetime - close_datetime).total_seconds()
            # Close if we're within 1 minute before or any time after
            return time_diff >= -60
    
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
        current_datetime = datetime.now(Config.TIMEZONE)
        current_time = current_datetime.time()
        current_date = current_datetime.date()
        
        # Check open time - make timezone-aware
        open_datetime = Config.TIMEZONE.localize(datetime.combine(current_date, self.open_time))
        open_diff = abs((current_datetime - open_datetime).total_seconds())
        
        # Check close time (only if we have positions)
        if self.last_trading_day is not None:
            # Handle cross-day scenario
            if self.close_time < self.open_time:
                # Close time is next day
                expected_close_date = self.last_trading_day + timedelta(days=1)
                close_datetime = Config.TIMEZONE.localize(datetime.combine(expected_close_date, self.close_time))
            else:
                # Close time is same day
                close_datetime = Config.TIMEZONE.localize(datetime.combine(self.last_trading_day, self.close_time))
            
            close_diff = abs((current_datetime - close_datetime).total_seconds())
            return open_diff <= 300 or close_diff <= 300
        
        return open_diff <= 300
    
    def mark_trading_day(self, date):
        """Mark that we traded on this day."""
        self.last_trading_day = date
    
    def reset_trading_day(self):
        """Reset trading day (for new day)."""
        self.last_trading_day = None