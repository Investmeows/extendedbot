"""
Logging configuration for the trading bot.
"""
import logging
import logging.handlers
import os
from datetime import datetime
from src.config import Config

class FileRotationHandler(logging.handlers.RotatingFileHandler):
    """Custom file handler with rotation for Docker environments."""
    
    def __init__(self, filename, max_bytes=10*1024*1024, backup_count=5):
        # Ensure log directory exists
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        super().__init__(filename, maxBytes=max_bytes, backupCount=backup_count)

def setup_logging():
    """Set up logging configuration for Docker/DO deployment."""
    # Create logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, Config.LOG_LEVEL.upper(), logging.INFO))
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Console handler (for Docker logs)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler with rotation (for persistent logs)
    try:
        # Use local path if /app is not writable
        log_file = Config.LOG_FILE
        if log_file.startswith('/app'):
            log_file = './logs/trading-bot.log'
        
        file_handler = FileRotationHandler(
            log_file,
            max_bytes=10*1024*1024,  # 10MB
            backup_count=5
        )
        file_handler.setLevel(logging.INFO)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
        print(f"File logging enabled: {Config.LOG_FILE}")
    except Exception as e:
        print(f"Failed to set up file logging: {e}")
    
    return logger
