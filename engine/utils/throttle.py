"""
Rate limiting and throttling utilities for network requests.
Provides async-compatible per-target throttling.
"""
import asyncio
import time
from typing import Dict, Optional
from collections import defaultdict
from dataclasses import dataclass


@dataclass
class ThrottleConfig:
    """Configuration for request throttling."""
    requests_per_second: float = 10.0
    burst_size: int = 5


class Throttler:
    """
    Async-compatible request throttler with per-target rate limiting.
    """
    
    def __init__(self, config: Optional[ThrottleConfig] = None):
        """
        Initialize throttler.
        
        Args:
            config: Throttle configuration
        """
        self.config = config or ThrottleConfig()
        self._locks: Dict[str, asyncio.Lock] = defaultdict(asyncio.Lock)
        self._request_times: Dict[str, list] = defaultdict(list)
        self._min_interval = 1.0 / self.config.requests_per_second
    
    async def acquire(self, target: str) -> None:
        """
        Acquire permission to make a request for a target.
        Blocks if rate limit would be exceeded.
        
        Args:
            target: Target identifier for rate limiting
        """
        async with self._locks[target]:
            now = time.time()
            request_times = self._request_times[target]
            
            # Remove old request times (older than 1 second)
            request_times[:] = [t for t in request_times if now - t < 1.0]
            
            # Check if we're at the limit
            if len(request_times) >= self.config.requests_per_second:
                # Calculate wait time
                oldest_request = min(request_times)
                wait_time = 1.0 - (now - oldest_request) + 0.01  # Small buffer
                if wait_time > 0:
                    await asyncio.sleep(wait_time)
                    now = time.time()
                    # Clean up again after waiting
                    request_times[:] = [t for t in request_times if now - t < 1.0]
            
            # Record this request
            request_times.append(time.time())
            
            # Ensure minimum interval between requests
            if request_times:
                time_since_last = now - request_times[-2] if len(request_times) > 1 else 0
                if time_since_last < self._min_interval:
                    await asyncio.sleep(self._min_interval - time_since_last)
    
    def reset(self, target: Optional[str] = None):
        """
        Reset throttle state for a target or all targets.
        
        Args:
            target: Target to reset (None for all targets)
        """
        if target:
            self._request_times[target].clear()
        else:
            self._request_times.clear()


# Global throttler instance
_global_throttler: Optional[Throttler] = None


def get_throttler(config: Optional[ThrottleConfig] = None) -> Throttler:
    """
    Get global throttler instance.
    
    Args:
        config: Throttle configuration (used only on first call)
        
    Returns:
        Global throttler instance
    """
    global _global_throttler
    if _global_throttler is None:
        _global_throttler = Throttler(config)
    return _global_throttler
