"""
Centralized logging utility for the Horilla project.
This module provides a consistent logging setup across all components.
"""

import os
import logging
from functools import wraps
import traceback
from django.conf import settings

class HorillaLogger:
    """
    A centralized logging utility class for the Horilla project.
    Provides consistent logging across all components with proper formatting and error handling.
    """
    
    def __init__(self, name="horilla"):
        """
        Initialize the logger with the given name.
        
        Args:
            name (str): The name of the logger. Defaults to "horilla".
        """
        self.logger = logging.getLogger(name)
        self._setup_logger()
    
    def _setup_logger(self):
        """Set up the logger with proper configuration."""
        if not self.logger.handlers:
            # Get log level from environment or settings
            log_level = os.environ.get('DJANGO_LOG_LEVEL', 'INFO')
            numeric_level = getattr(logging, log_level.upper(), logging.INFO)
            
            # Set the log level
            self.logger.setLevel(numeric_level)
            
            # Create formatter
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            
            # Get logging mode from environment variable
            logging_mode = os.environ.get('DJANGO_LOGGING_MODE', 'development')
            
            # Add console handler for non-development mode
            if logging_mode != 'development':
                console_handler = logging.StreamHandler()
                console_handler.setFormatter(formatter)
                self.logger.addHandler(console_handler)
                self.logger.info("Console logging enabled")
            
            # Add Graylog handler for development mode
            if logging_mode == 'development':
                try:
                    from pygelf import GelfTcpHandler
                    graylog_handler = GelfTcpHandler(
                        host='graylog',
                        port=12201,
                        include_extra_fields=True,
                        debug=True,
                        hostname='horilla',
                        source='horilla'
                    )
                    self.logger.addHandler(graylog_handler)
                    self.logger.info("Graylog logging enabled")
                except ImportError:
                    # Fallback to console if pygelf is not available
                    console_handler = logging.StreamHandler()
                    console_handler.setFormatter(formatter)
                    self.logger.addHandler(console_handler)
                    self.logger.warning("Graylog handler not available, falling back to console logging")
    
    def info(self, message, *args, **kwargs):
        """Log an info message."""
        self.logger.info(message, *args, **kwargs)
    
    def error(self, message, *args, **kwargs):
        """Log an error message."""
        self.logger.error(message, *args, **kwargs)
    
    def warning(self, message, *args, **kwargs):
        """Log a warning message."""
        self.logger.warning(message, *args, **kwargs)
    
    def debug(self, message, *args, **kwargs):
        """Log a debug message."""
        self.logger.debug(message, *args, **kwargs)
    
    def critical(self, message, *args, **kwargs):
        """Log a critical message."""
        self.logger.critical(message, *args, **kwargs)
    
    def exception(self, message, *args, **kwargs):
        """Log an exception message with traceback."""
        self.logger.exception(message, *args, **kwargs)
    
    def log_error(self, error, context=None):
        """
        Log an error with context information.
        
        Args:
            error: The error object or message
            context (dict): Additional context information
        """
        error_message = str(error)
        if context:
            error_message = f"{error_message} - Context: {context}"
        self.exception(error_message)
    
    def log_api_error(self, error, endpoint=None, request_data=None, response=None):
        """
        Log an API error with request and response information.
        
        Args:
            error: The error object or message
            endpoint (str): The API endpoint that caused the error
            request_data (dict): The request data
            response: The response object or data
        """
        error_message = f"API Error: {str(error)}"
        if endpoint:
            error_message = f"{error_message} - Endpoint: {endpoint}"
        if request_data:
            error_message = f"{error_message} - Request: {request_data}"
        if response:
            error_message = f"{error_message} - Response: {response}"
        self.exception(error_message)

def log_execution(logger_name="horilla"):
    """
    Decorator to log function execution with timing and error handling.
    
    Args:
        logger_name (str): The name of the logger to use
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger = HorillaLogger(logger_name)
            func_name = func.__name__
            
            try:
                logger.info(f"Starting execution of {func_name}")
                result = func(*args, **kwargs)
                logger.info(f"Successfully completed {func_name}")
                return result
            except Exception as e:
                logger.log_error(e, {
                    'function': func_name,
                    'args': args,
                    'kwargs': kwargs
                })
                raise
        return wrapper
    return decorator

# Create default logger instance lazily
def get_default_logger():
    return HorillaLogger()

# Don't create the logger instance at module level
default_logger = None 