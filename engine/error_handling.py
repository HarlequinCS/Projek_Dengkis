"""
Enhanced error handling and recovery for PROJEK DENGKIS.
"""
import asyncio
import logging
from typing import Dict, Optional, Callable, Any, Dict
from functools import wraps
from enum import Enum

from engine.logging.logger import get_logger


class ErrorSeverity(Enum):
    """Error severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AssessmentError(Exception):
    """Base exception for assessment errors."""
    
    def __init__(self, message: str, severity: ErrorSeverity = ErrorSeverity.MEDIUM, recoverable: bool = True):
        super().__init__(message)
        self.message = message
        self.severity = severity
        self.recoverable = recoverable


class NetworkError(AssessmentError):
    """Network-related errors."""
    pass


class ValidationError(AssessmentError):
    """Validation errors."""
    pass


class SessionError(AssessmentError):
    """Session-related errors."""
    pass


def handle_errors(recoverable: bool = True, default_return: Any = None):
    """
    Decorator for error handling.
    
    Args:
        recoverable: Whether error is recoverable
        default_return: Default return value on error
    """
    def decorator(func: Callable):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except AssessmentError as e:
                logger = get_logger()
                logger.error(f"Assessment error in {func.__name__}: {e.message}")
                if e.recoverable and recoverable:
                    return default_return
                raise
            except Exception as e:
                logger = get_logger()
                logger.error(f"Unexpected error in {func.__name__}: {e}")
                if recoverable:
                    return default_return
                raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except AssessmentError as e:
                logger = get_logger()
                logger.error(f"Assessment error in {func.__name__}: {e.message}")
                if e.recoverable and recoverable:
                    return default_return
                raise
            except Exception as e:
                logger = get_logger()
                logger.error(f"Unexpected error in {func.__name__}: {e}")
                if recoverable:
                    return default_return
                raise
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    
    return decorator


class ErrorRecovery:
    """Error recovery manager."""
    
    def __init__(self):
        self.recovery_strategies: Dict[type, Callable] = {}
        self.logger = get_logger()
    
    def register_recovery(self, error_type: type, recovery_func: Callable):
        """
        Register recovery function for error type.
        
        Args:
            error_type: Exception type
            recovery_func: Recovery function
        """
        self.recovery_strategies[error_type] = recovery_func
    
    async def attempt_recovery(self, error: Exception, context: Dict) -> Optional[Any]:
        """
        Attempt to recover from error.
        
        Args:
            error: Exception that occurred
            context: Context information
            
        Returns:
            Recovery result or None
        """
        error_type = type(error)
        
        if error_type in self.recovery_strategies:
            try:
                recovery_func = self.recovery_strategies[error_type]
                if asyncio.iscoroutinefunction(recovery_func):
                    return await recovery_func(error, context)
                else:
                    return recovery_func(error, context)
            except Exception as e:
                self.logger.error(f"Recovery failed: {e}")
        
        return None
