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
        self.region_name = region_name
        self.client = None
        self.log_stream_name = f"trading-bot-{int(time.time())}"
        self.sequence_token = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the CloudWatch client with error handling."""
        try:
            self.client = boto3.client('logs', region_name=self.region_name)
            self._ensure_log_group_exists()
            self._ensure_log_stream_exists()
        except Exception as e:
            # If CloudWatch setup fails, disable the handler
            self.client = None
            print(f"CloudWatch initialization failed: {e}")
    
    def _ensure_log_group_exists(self):
        """Ensure the log group exists in CloudWatch."""
        if not self.client:
            return
            
        try:
            self.client.describe_log_groups(logGroupNamePrefix=self.log_group_name)
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                try:
                    self.client.create_log_group(logGroupName=self.log_group_name)
                    print(f"Created CloudWatch log group: {self.log_group_name}")
                except Exception as create_error:
                    print(f"Failed to create log group: {create_error}")
                    self.client = None
    
    def _ensure_log_stream_exists(self):
        """Ensure the log stream exists in CloudWatch."""
        if not self.client:
            return
            
        try:
            self.client.create_log_stream(
                logGroupName=self.log_group_name,
                logStreamName=self.log_stream_name
            )
        except ClientError as e:
            if e.response['Error']['Code'] != 'ResourceAlreadyExistsException':
                print(f"Failed to create log stream: {e}")
                self.client = None
    
    def emit(self, record):
        """Emit a log record to CloudWatch."""
        if not self.client:
            return  # Silently skip if CloudWatch is not available
            
        try:
            message = self.format(record)
            log_events = [{
                'timestamp': int(record.created * 1000),
                'message': message
            }]
            
            # Prepare put_log_events parameters
            params = {
                'logGroupName': self.log_group_name,
                'logStreamName': self.log_stream_name,
                'logEvents': log_events
            }
            
            # Add sequence token if we have one
            if self.sequence_token:
                params['sequenceToken'] = self.sequence_token
            
            response = self.client.put_log_events(**params)
            self.sequence_token = response.get('nextSequenceToken')
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'InvalidSequenceTokenException':
                # Try to get the correct sequence token
                try:
                    response = self.client.describe_log_streams(
                        logGroupName=self.log_group_name,
                        logStreamNamePrefix=self.log_stream_name
                    )
                    if response['logStreams']:
                        self.sequence_token = response['logStreams'][0].get('uploadSequenceToken')
                except Exception:
                    pass
        except Exception:
            # Silently fail - don't print error messages to avoid spam
            pass

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
        # Only add handler if CloudWatch client was successfully initialized
        if cloudwatch_handler.client is not None:
            cloudwatch_handler.setLevel(logging.INFO)
            cloudwatch_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            cloudwatch_handler.setFormatter(cloudwatch_formatter)
            logger.addHandler(cloudwatch_handler)
            print("CloudWatch logging enabled")
        else:
            print("CloudWatch logging disabled - using console logging only")
    except Exception as e:
        print(f"Failed to set up CloudWatch logging: {e}")
    
    return logger
