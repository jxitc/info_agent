"""Logging configuration for the Info Agent application."""

import logging
import logging.config
import os
from pathlib import Path
from typing import Dict, Any


def setup_logging(
    log_level: str = "INFO",
    log_file: str = None,
    log_dir: str = None
) -> None:
    """
    Configure logging for the application.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional log file name
        log_dir: Optional log directory path
    """
    if log_dir is None:
        log_dir = os.path.expanduser("~/.info_agent/logs")
    
    # Create log directory if it doesn't exist
    Path(log_dir).mkdir(parents=True, exist_ok=True)
    
    config = get_logging_config(log_level, log_file, log_dir)
    logging.config.dictConfig(config)


def get_logging_config(
    log_level: str,
    log_file: str = None,
    log_dir: str = None
) -> Dict[str, Any]:
    """
    Get logging configuration dictionary.
    
    Args:
        log_level: Logging level
        log_file: Optional log file name
        log_dir: Optional log directory path
        
    Returns:
        Dictionary configuration for logging
    """
    if log_file is None:
        log_file = "info_agent.log"
    
    if log_dir is None:
        log_dir = os.path.expanduser("~/.info_agent/logs")
    
    log_path = os.path.join(log_dir, log_file)
    
    config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            },
            'detailed': {
                'format': '%(asctime)s [%(levelname)s] %(name)s:%(lineno)d: %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            }
        },
        'handlers': {
            'console': {
                'level': log_level,
                'class': 'logging.StreamHandler',
                'formatter': 'standard',
                'stream': 'ext://sys.stdout'
            },
            'file': {
                'level': 'DEBUG',
                'class': 'logging.handlers.RotatingFileHandler',
                'formatter': 'detailed',
                'filename': log_path,
                'maxBytes': 10485760,  # 10MB
                'backupCount': 5
            }
        },
        'loggers': {
            'info_agent': {
                'level': 'DEBUG',
                'handlers': ['console', 'file'],
                'propagate': False
            }
        },
        'root': {
            'level': 'WARNING',
            'handlers': ['console']
        }
    }
    
    return config


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for the given name.
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Logger instance
    """
    return logging.getLogger(f"info_agent.{name}")