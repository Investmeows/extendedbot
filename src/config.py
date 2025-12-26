"""
Configuration settings for the Extended Exchange trading bot.
"""
import os
import warnings
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
    
    # Trading Pairs Configuration - Basket-based mode
    # Only numbered pairs are supported: LONG_PAIR1, LONG_PAIR2, etc. with corresponding *_TARGET_SIZE
    LONG_LEVERAGE = None
    SHORT_LEVERAGE = None
    
    # Parse leverage from env (required)
    _LONG_LEVERAGE_RAW = os.getenv('LONG_LEVERAGE')
    if _LONG_LEVERAGE_RAW:
        LONG_LEVERAGE = int(_LONG_LEVERAGE_RAW)
    
    _SHORT_LEVERAGE_RAW = os.getenv('SHORT_LEVERAGE')
    if _SHORT_LEVERAGE_RAW:
        SHORT_LEVERAGE = int(_SHORT_LEVERAGE_RAW)
    
    # Basket configuration (parsed at class level)
    _LONG_PAIRS = None
    _SHORT_PAIRS = None
    
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
    def _parse_pairs(cls):
        """Parse basket-based pair configuration from environment variables.
        
        Only numbered pairs are supported: LONG_PAIR1, LONG_PAIR2, etc.
        Each pair requires a corresponding *_TARGET_SIZE variable.
        Parsing is variable - no hardcoded limits.
        """
        if cls._LONG_PAIRS is not None:
            return  # Already parsed
        
        long_pairs = []
        short_pairs = []
        
        # Parse LONG_PAIR1, LONG_PAIR2, etc. (variable parsing, no hardcoded limit)
        # Scan through a reasonable range to allow non-sequential pair numbers
        # (e.g., LONG_PAIR1 and LONG_PAIR3 without LONG_PAIR2)
        for i in range(1, 20):  # Scan up to 20 pairs
            pair_key = f'LONG_PAIR{i}'
            size_key = f'LONG_PAIR{i}_TARGET_SIZE'
            pair_value = os.getenv(pair_key)
            if pair_value:
                size_value = os.getenv(size_key)
                if not size_value:
                    raise ValueError(f"Missing {size_key} for {pair_key}. Each pair must have a corresponding target size.")
                long_pairs.append({
                    'pair': pair_value,
                    'target_size': float(size_value)
                })
        
        # Parse SHORT_PAIR1, SHORT_PAIR2, etc. (variable parsing, no hardcoded limit)
        # Scan through a reasonable range to allow non-sequential pair numbers
        # (e.g., SHORT_PAIR1 and SHORT_PAIR3 without SHORT_PAIR2)
        for i in range(1, 20):  # Scan up to 20 pairs
            pair_key = f'SHORT_PAIR{i}'
            size_key = f'SHORT_PAIR{i}_TARGET_SIZE'
            pair_value = os.getenv(pair_key)
            if pair_value:
                size_value = os.getenv(size_key)
                if not size_value:
                    raise ValueError(f"Missing {size_key} for {pair_key}. Each pair must have a corresponding target size.")
                short_pairs.append({
                    'pair': pair_value,
                    'target_size': float(size_value)
                })
        
        cls._LONG_PAIRS = long_pairs
        cls._SHORT_PAIRS = short_pairs
    
    @classmethod
    def get_all_long_pairs(cls):
        """Get all configured long pairs with target sizes."""
        cls._parse_pairs()
        return cls._LONG_PAIRS
    
    @classmethod
    def get_all_short_pairs(cls):
        """Get all configured short pairs with target sizes."""
        cls._parse_pairs()
        return cls._SHORT_PAIRS
    
    @classmethod
    def validate_config(cls):
        """Validate that all required configuration is present."""
        # Required API configuration
        required_vars = ['API_KEY', 'L2_KEY', 'L2_VAULT', 'L2_PUBLIC_KEY']
        missing = [var for var in required_vars if not getattr(cls, var)]
        
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
        
        # Validate trading-specific configuration (no defaults allowed)
        trading_missing = []
        if cls.LONG_LEVERAGE is None:
            trading_missing.append('LONG_LEVERAGE')
        if cls.SHORT_LEVERAGE is None:
            trading_missing.append('SHORT_LEVERAGE')
        if not cls.OPEN_TIME:
            trading_missing.append('OPEN_TIME')
        if not cls.CLOSE_TIME:
            trading_missing.append('CLOSE_TIME')
        
        if trading_missing:
            warnings.warn(f"Missing required trading configuration: {', '.join(trading_missing)}", UserWarning)
            raise ValueError(f"Missing required trading configuration: {', '.join(trading_missing)}")
        
        # Validate time format (HH:MM:SS)
        from datetime import datetime
        try:
            datetime.strptime(cls.OPEN_TIME, "%H:%M:%S")
        except ValueError:
            raise ValueError(f"Invalid OPEN_TIME format: '{cls.OPEN_TIME}'. Expected format: HH:MM:SS (e.g., '21:30:30')")
        
        try:
            datetime.strptime(cls.CLOSE_TIME, "%H:%M:%S")
        except ValueError:
            raise ValueError(f"Invalid CLOSE_TIME format: '{cls.CLOSE_TIME}'. Expected format: HH:MM:SS (e.g., '18:30:30')")
        
        # Parse and validate pairs
        cls._parse_pairs()
        
        # Validate at least one pair is configured
        if not cls._LONG_PAIRS and not cls._SHORT_PAIRS:
            raise ValueError(
                "No pairs configured. Please set LONG_PAIR1/SHORT_PAIR1 with corresponding *_TARGET_SIZE values. "
                "Example: LONG_PAIR1=BTC-USD, LONG_PAIR1_TARGET_SIZE=1500.0"
            )
        
        # Validate target sizes are positive
        for pair_config in cls._LONG_PAIRS + cls._SHORT_PAIRS:
            if pair_config['target_size'] <= 0:
                warnings.warn(f"Target size for {pair_config['pair']} must be positive", UserWarning)
                raise ValueError(f"Target size for {pair_config['pair']} must be positive")
        
        return True
