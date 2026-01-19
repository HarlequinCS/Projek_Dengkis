"""
Batch scanning functionality for PROJEK DENGKIS.
Allows scanning multiple targets in sequence or parallel.
"""
import asyncio
from typing import Dict, List, Optional, Callable
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import uuid

from engine.runner import run_assessment
from engine.network.request_handler import AggressiveRequestHandler
from engine.utils.retry import RetryConfig
from engine.utils.throttle import ThrottleConfig
from engine.storage.session_store import SessionStore
from engine.logging.logger import get_logger


class BatchScanner:
    """
    Batch scanner for processing multiple targets.
    """
    
    def __init__(
        self,
        max_concurrent: int = 5,
        retry_config: Optional[RetryConfig] = None,
        throttle_config: Optional[ThrottleConfig] = None
    ):
        """
        Initialize batch scanner.
        
        Args:
            max_concurrent: Maximum concurrent scans
            retry_config: Retry configuration
            throttle_config: Throttle configuration
        """
        self.max_concurrent = max_concurrent
        self.retry_config = retry_config or RetryConfig()
        self.throttle_config = throttle_config or ThrottleConfig(requests_per_second=5.0)
        self.store = SessionStore()
        self.logger = get_logger()
        self.results: List[Dict] = []
    
    async def scan_targets(
        self,
        targets: List[str],
        authorized: bool = True,
        progress_callback: Optional[Callable] = None
    ) -> Dict:
        """
        Scan multiple targets.
        
        Args:
            targets: List of target URLs/IPs
            authorized: Authorization flag
            progress_callback: Optional callback for progress updates
            
        Returns:
            Dictionary containing batch scan results
        """
        if not authorized:
            return {
                "status": "error",
                "message": "Batch scanning requires authorization"
            }
        
        self.results = []
        semaphore = asyncio.Semaphore(self.max_concurrent)
        
        async def scan_single_target(target: str) -> Dict:
            """Scan a single target."""
            async with semaphore:
                try:
                    result = await self._scan_target(target, authorized)
                    self.results.append(result)
                    
                    if progress_callback:
                        progress_callback(len(self.results), len(targets))
                    
                    return result
                except Exception as e:
                    error_result = {
                        "target": target,
                        "status": "error",
                        "error": str(e)
                    }
                    self.results.append(error_result)
                    return error_result
        
        # Run scans concurrently
        tasks = [scan_single_target(target) for target in targets]
        await asyncio.gather(*tasks)
        
        return {
            "status": "completed",
            "total_targets": len(targets),
            "completed": len([r for r in self.results if r.get("status") == "completed"]),
            "failed": len([r for r in self.results if r.get("status") == "error"]),
            "results": self.results
        }
    
    async def _scan_target(self, target: str, authorized: bool) -> Dict:
        """Scan a single target."""
        # Initialize assessment
        assessment_result = run_assessment(target, authorized=authorized)
        
        if assessment_result.get('status') == 'error':
            return {
                "target": target,
                "status": "error",
                "error": assessment_result.get("message")
            }
        
        session_id = assessment_result.get('session_id')
        
        # Perform network reconnaissance
        async with AggressiveRequestHandler(
            timeout=self.retry_config.timeout,
            retry_config=self.retry_config,
            throttle_config=self.throttle_config,
            session_id=session_id
        ) as handler:
            # Extract behavioral fingerprint
            fingerprint = await handler.extract_behavioral_fingerprint(target)
            
            # Store session
            session_data = {
                'session_id': session_id,
                'target': target,
                'started_at': assessment_result.get('started_at'),
                'status': 'completed',
                'fingerprint': fingerprint,
                'findings': []
            }
            
            self.store.save_session(session_data, session_id)
            
            return {
                "target": target,
                "status": "completed",
                "session_id": session_id,
                "probes": len(fingerprint.get('probes', []))
            }
