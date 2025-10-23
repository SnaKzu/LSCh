"""
Logger Configuration - Railway Compatible
"""
import logging
import os
from datetime import datetime

def get_logger(name):
    """
    Create logger instance compatible with Railway environment
    """
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        # Configure logging level
        log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
        logger.setLevel(getattr(logging, log_level, logging.INFO))
        
        # Create console handler for Railway
        handler = logging.StreamHandler()
        handler.setLevel(logger.level)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        
        logger.addHandler(handler)
    
    return logger