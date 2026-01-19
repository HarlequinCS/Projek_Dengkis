"""
Retry and timeout utilities for network operations.
Implements exponential backoff with graceful failure handling.
"""
import asyncio
from typing import Callable, Optional, TypeVar, Any
import time
from functools import wraps


T = TypeVar('T')


class RetryConfig:
    """Configuration for retry behavior."""
    
    def __init__(
        self,
        max_attempts: int = 3,
        initial_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        timeout: float = 30.0
    ):
        self.max_attempts = max_attempts
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.timeout = timeout


async def retry_with_backoff(
    func: Callable[..., Any],
    *args,
    config: Optional[RetryConfig] = None,
    **kwargs
) -> Any:
    """
    Execute function with exponential backoff retry logic.
    
    Args:
        func: Async function to execute
        *args: Positional arguments for func
        config: Retry configuration
        **kwargs: Keyword arguments for func
        
    Returns:
        Result of function execution
        
    Raises:
        Last exception if all retries fail
    """
    if config is None:
        config = RetryConfig()
    
    last_exception = None
    delay = config.initial_delay
    
    for attempt in range(1, config.max_attempts + 1):
        try:
            # Apply timeout if specified
            if config.timeout > 0:
                return await asyncio.wait_for(
                    func(*args, **kwargs),
                    timeout=config.timeout
                )
            else:
                return await func(*args, **kwargs)
        
        except (asyncio.TimeoutError, Exception) as e:
            last_exception = e
            
            if attempt < config.max_attempts:
                # Wait before retry with exponential backoff
                await asyncio.sleep(min(delay, config.max_delay))
                delay *= config.exponential_base
            else:
                # Last attempt failed
                break
    
    # All retries exhausted
    raise last_exception


def with_retry(config: Optional[RetryConfig] = None):
    """
    Decorator for adding retry logic to async functions.
    
    Args:
        config: Retry configuration
        
    Returns:
        Decorated function
    """
    def decorator(func: Callable[..., Any]):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await retry_with_backoff(func, *args, config=config, **kwargs)
        return wrapper
    return decorator
