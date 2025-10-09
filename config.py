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
    API_KEY = os.getenv('EXTENDED_API_KEY')
    STARK_KEY = os.getenv('EXTENDED_STARK_KEY')
    STARK_PUBLIC_KEY = os.getenv('EXTENDED_STARK_PUBLIC_KEY')
    VAULT_NUMBER = os.getenv('EXTENDED_VAULT_NUMBER')
    CLIENT_ID = os.getenv('EXTENDED_CLIENT_ID')
    BASE_URL = os.getenv('EXTENDED_BASE_URL', 'https://api.extended.exchange/api/v1')
    
    # AWS Configuration
    AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
    AWS_LOG_GROUP = os.getenv('AWS_LOG_GROUP', 'extended-bot-logs')
    
    # Trading Configuration - Delta Neutral Strategy
    TARGET_SIZE = float(os.getenv('TARGET_SIZE'))
    BTC_LEVERAGE = int(os.getenv('BTC_LEVERAGE'))
    ETH_LEVERAGE = int(os.getenv('ETH_LEVERAGE'))
    TIMEZONE = pytz.timezone(os.getenv('TIMEZONE', 'Asia/Bangkok'))
    
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
        required_vars = ['API_KEY', 'STARK_KEY', 'STARK_PUBLIC_KEY', 'VAULT_NUMBER', 'CLIENT_ID']
        missing = [var for var in required_vars if not getattr(cls, var)]
        
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
        
        return True
