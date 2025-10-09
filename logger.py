"""
Logging configuration for the trading bot.
"""
import logging
import time
import boto3
from botocore.exceptions import ClientError
from config import Config

class CloudWatchHandler(logging.Handler):
    """Custom handler for AWS CloudWatch logs."""
    
    def __init__(self, log_group_name: str, region_name: str):
        super().__init__()
        self.log_group_name = log_group_name
        self.client = boto3.client('logs', region_name=region_name)
        self._ensure_log_group_exists()
    
    def _ensure_log_group_exists(self):
        """Ensure the log group exists in CloudWatch."""
        try:
            self.client.describe_log_groups(logGroupNamePrefix=self.log_group_name)
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                # Create log group if it doesn't exist
                self.client.create_log_group(logGroupName=self.log_group_name)
                print(f"Created CloudWatch log group: {self.log_group_name}")
    
    def emit(self, record):
        """Emit a log record to CloudWatch."""
        try:
            log_stream_name = f"trading-bot-{int(time.time())}"
            
            # Create log stream if it doesn't exist
            try:
                self.client.create_log_stream(
                    logGroupName=self.log_group_name,
                    logStreamName=log_stream_name
                )
            except ClientError as e:
                if e.response['Error']['Code'] != 'ResourceAlreadyExistsException':
                    raise
            
            # Send log event
            message = self.format(record)
            self.client.put_log_events(
                logGroupName=self.log_group_name,
                logStreamName=log_stream_name,
                logEvents=[{
                    'timestamp': int(record.created * 1000),
                    'message': message
                }]
            )
        except Exception:
            # Fallback to console if CloudWatch fails
            print(f"CloudWatch logging failed: {self.format(record)}")

def setup_logging():
    """Set up logging configuration."""
    # Create logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # CloudWatch handler (if AWS is configured)
    try:
        cloudwatch_handler = CloudWatchHandler(
            Config.AWS_LOG_GROUP,
            Config.AWS_REGION
        )
        cloudwatch_handler.setLevel(logging.INFO)
        cloudwatch_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        cloudwatch_handler.setFormatter(cloudwatch_formatter)
        logger.addHandler(cloudwatch_handler)
    except Exception as e:
        print(f"Failed to set up CloudWatch logging: {e}")
    
    return logger
