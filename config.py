"""
Configuration settings for the Extended Exchange trading bot.
"""
import os
from dotenv import load_dotenv
import pytz

# Load environment variables
load_dotenv()

class Config:
    # Extended Exchange API Configuration
    API_KEY = os.getenv('EXT_API_KEY')
    L2_KEY = os.getenv('EXT_L2_KEY')
    L2_VAULT = os.getenv('EXT_L2_VAULT')
    L2_PUBLIC_KEY = os.getenv('EXT_L2_PUBLIC_KEY') or os.getenv('L2_PUBLIC_KEY')
    USER_AGENT = os.getenv('EXT_USER_AGENT', 'extended-bot/0.1')
    BASE_URL = os.getenv('EXT_BASE_URL', 'https://api.starknet.extended.exchange/api/v1')
    
    # DigitalOcean Configuration (metadata only, doesn't affect bot functionality)
    DO_REGION = os.getenv('DO_REGION', 'syd1')
    DO_DROPLET_SIZE = os.getenv('DO_DROPLET_SIZE', 's-1vcpu-1gb')
    
    # Logging Configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', '/app/logs/trading-bot.log')
    
    # Trading Configuration - Delta Neutral Strategy
    TARGET_SIZE = float(os.getenv('TARGET_SIZE'))
    
    # Trading Pairs Configuration
    LONG_PAIR = os.getenv('LONG_PAIR', 'BTC-USD')
    SHORT_PAIR = os.getenv('SHORT_PAIR', 'ETH-USD')
    LONG_LEVERAGE = int(os.getenv('LONG_LEVERAGE', '10'))
    SHORT_LEVERAGE = int(os.getenv('SHORT_LEVERAGE', '10'))
    
    # Backward compatibility
    BTC_LEVERAGE = LONG_LEVERAGE
    ETH_LEVERAGE = SHORT_LEVERAGE
    
    TIMEZONE = pytz.timezone(os.getenv('TIMEZONE', 'UTC'))
    
    # Safety Configuration
    DEAD_MAN_SWITCH_ENABLED = os.getenv('DEAD_MAN_SWITCH_ENABLED', 'true').lower() == 'true'
    MAX_RETRY_ATTEMPTS = int(os.getenv('MAX_RETRY_ATTEMPTS', '3'))
    
    # Trading Schedule
    OPEN_TIME = os.getenv('OPEN_TIME')
    CLOSE_TIME = os.getenv('CLOSE_TIME')
    
    # Order Configuration
    PRICE_BUFFER = 0.0075  # 0.75% buffer for market-like orders
    ORDER_EXPIRY_DAYS = 1  # Order expiry in days
    
    @classmethod
    def validate_config(cls):
        """Validate that all required configuration is present."""
        required_vars = ['API_KEY', 'L2_KEY', 'L2_VAULT', 'L2_PUBLIC_KEY']
        missing = [var for var in required_vars if not getattr(cls, var)]
        
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
        
        return True
