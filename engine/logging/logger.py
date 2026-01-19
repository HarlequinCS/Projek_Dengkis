"""
Centralized logging system for PROJEK DENGKIS.
Provides session-aware logging with async-safe file and console output.
"""
import logging
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime
import os


class SessionAwareFormatter(logging.Formatter):
    """Custom formatter that includes session ID in log messages."""
    
    def format(self, record):
        if not hasattr(record, 'session_id'):
            record.session_id = 'N/A'
        return super().format(record)


class DengkisLogger:
    """
    Centralized logging system with session awareness and async-safe output.
    """
    
    _instance: Optional['DengkisLogger'] = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if DengkisLogger._initialized:
            return
        
        self.logger = logging.getLogger('dengkis')
        self.logger.setLevel(logging.DEBUG)
        self.logger.handlers.clear()
        
        # Prevent propagation to root logger
        self.logger.propagate = False
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_format = SessionAwareFormatter(
            '%(asctime)s - %(levelname)s - [%(session_id)s] - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_format)
        self.logger.addHandler(console_handler)
        
        # File handler
        log_dir = Path('logs')
        log_dir.mkdir(exist_ok=True)
        
        log_file = log_dir / f'dengkis_{datetime.now().strftime("%Y%m%d")}.log'
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_format = SessionAwareFormatter(
            '%(asctime)s - %(name)s - %(levelname)s - [%(session_id)s] - %(filename)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_format)
        self.logger.addHandler(file_handler)
        
        DengkisLogger._initialized = True
    
    def get_logger(self, session_id: Optional[str] = None):
        """
        Get logger instance with Optional session ID.
        
        Args:
            session_id: Optional session ID to attach to logs
            
        Returns:
            Logger adapter with session ID
        """
        if session_id:
            return SessionLoggerAdapter(self.logger, {'session_id': session_id})
        return SessionLoggerAdapter(self.logger, {'session_id': 'N/A'})
    
    def set_level(self, level: str):
        """
        Set logging level.
        
        Args:
            level: Log level (DEBUG, INFO, WARNING, ERROR)
        """
        level_map = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR
        }
        self.logger.setLevel(level_map.get(level.upper(), logging.INFO))
        for handler in self.logger.handlers:
            handler.setLevel(level_map.get(level.upper(), logging.INFO))


class SessionLoggerAdapter(logging.LoggerAdapter):
    """Logger adapter that adds session ID to all log records."""
    
    def process(self, msg, kwargs):
        kwargs['extra'] = kwargs.get('extra', {})
        kwargs['extra']['session_id'] = self.extra.get('session_id', 'N/A')
        return msg, kwargs


# Global logger instance
_logger_instance: Optional[DengkisLogger] = None


def get_logger(session_id: Optional[str] = None) -> logging.LoggerAdapter:
    """
    Get global logger instance with Optional session ID.
    
    Args:
        session_id: Optional session ID to attach to logs
        
    Returns:
        Logger adapter instance
    """
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = DengkisLogger()
    return _logger_instance.get_logger(session_id)
