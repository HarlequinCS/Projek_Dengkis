"""
LOGIC BREAKER - Business Logic & Race Condition Testing
Finds flaws that standard scanners miss (price manipulation, race conditions, IDOR).
"""
import asyncio
from typing import Dict, List, Optional, Set
import httpx

from engine.logging.logger import get_logger


class LogicBreaker:
    """
    Logic engine focused on business logic vulnerabilities.
    System Prompt: "You are the Dengkis Logic Engine."
    """
    
    def __init__(self, session: Optional[httpx.AsyncClient] = None):
        self.session = session
        self.logger = get_logger()
        self.findings: List[Dict] = []
    
    async def test_integer_overflow(self, endpoint: str, parameter: str, method: str = "POST") -> List[Dict]:
        """
        Test numeric parameters for integer overflow/underflow.
        System Prompt: "Test price or quantity fields with negative numbers and extremely large integers"
        
        Args:
            endpoint: Target endpoint
            parameter: Numeric parameter name
            method: HTTP method
            
        Returns:
            List of findings
        """
        findings = []
        
        # Test values
        test_values = [
            -1,
            -999999,
            -2147483648,  # INT_MIN
            2147483647,   # INT_MAX
            999999999999,
            0,
        ]
        
        for value in test_values:
            try:
                if not self.session:
                    async with httpx.AsyncClient(verify=False, timeout=10.0) as client:
                        if method.upper() == 'GET':
                            response = await client.get(endpoint, params={parameter: value})
                        else:
                            response = await client.post(endpoint, data={parameter: value})
                else:
                    if method.upper() == 'GET':
                        response = await self.session.get(endpoint, params={parameter: value})
                    else:
                        response = await self.session.post(endpoint, data={parameter: value})
                
                # Check for unusual responses
                if response.status_code == 200:
                    # Check if negative value was accepted (potential underflow)
                    if value < 0 and 'price' in parameter.lower():
                        findings.append({
                            'type': 'integer_underflow',
                            'endpoint': endpoint,
                            'parameter': parameter,
                            'value': value,
                            'status_code': response.status_code,
                            'response_snippet': response.text[:200]
                        })
                        self.logger.warning(f"[LOGIC BREAKER] Potential integer underflow: {parameter}={value}")
                
            except Exception as e:
                self.logger.debug(f"[LOGIC BREAKER] Test failed for {parameter}={value}: {e}")
        
        self.findings.extend(findings)
        return findings
    
    async def test_race_condition(
        self,
        endpoint: str,
        data: Dict,
        method: str = "POST",
        num_requests: int = 20,
        window_ms: int = 50
    ) -> Dict:
        """
        Test for race conditions by sending multiple identical requests rapidly.
        System Prompt: "Send 20 identical requests within a 50ms window to test if the server processes a single-use token multiple times"
        
        Args:
            endpoint: Target endpoint
            data: Request data (should include token/ID)
            method: HTTP method
            num_requests: Number of concurrent requests
            window_ms: Time window in milliseconds
            
        Returns:
            Race condition test results
        """
        self.logger.info(f"[LOGIC BREAKER] Testing race condition on {endpoint} with {num_requests} requests")
        
        async def send_request():
            try:
                if not self.session:
                    async with httpx.AsyncClient(verify=False, timeout=10.0) as client:
                        if method.upper() == 'GET':
                            response = await client.get(endpoint, params=data)
                        else:
                            response = await client.post(endpoint, data=data)
                else:
                    if method.upper() == 'GET':
                        response = await self.session.get(endpoint, params=data)
                    else:
                        response = await self.session.post(endpoint, data=data)
                return response
            except Exception as e:
                self.logger.debug(f"[LOGIC BREAKER] Race condition request failed: {e}")
                return None
        
        # Send all requests concurrently within time window
        tasks = [send_request() for _ in range(num_requests)]
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Analyze results
        success_count = sum(1 for r in responses if r and hasattr(r, 'status_code') and r.status_code == 200)
        unique_responses = len(set(r.text[:100] if r and hasattr(r, 'text') else '' for r in responses if r))
        
        result = {
            'endpoint': endpoint,
            'type': 'race_condition_test',
            'requests_sent': num_requests,
            'successful_responses': success_count,
            'unique_responses': unique_responses,
            'potential_race_condition': success_count > 1 and unique_responses == 1
        }
        
        if result['potential_race_condition']:
            self.logger.warning(f"[LOGIC BREAKER] Potential race condition detected on {endpoint}")
            self.findings.append(result)
        
        return result
    
    async def discover_idor(self, base_url: str, id_range: range = range(100, 110)) -> List[Dict]:
        """
        Discover IDOR vulnerabilities by iterating through integer IDs.
        System Prompt: "Iterate through integer IDs in URLs. Compare response size of /api/user/101 vs /api/user/102"
        
        Args:
            base_url: Base URL pattern (e.g., "http://target.com/api/user/{id}")
            id_range: Range of IDs to test
            
        Returns:
            List of IDOR findings
        """
        findings = []
        baseline_response = None
        baseline_id = None
        
        for test_id in id_range:
            try:
                # Handle URL format safely
                try:
                    url = base_url.format(id=test_id)
                except (KeyError, ValueError):
                    # If format fails, try replacing {id} manually
                    if '{id}' in base_url:
                        url = base_url.replace('{id}', str(test_id))
                    else:
                        # If no placeholder, append ID to URL
                        url = f"{base_url.rstrip('/')}/{test_id}"
                
                if not self.session:
                    async with httpx.AsyncClient(verify=False, timeout=10.0) as client:
                        response = await client.get(url)
                else:
                    response = await self.session.get(url)
                
                if response.status_code == 200:
                    response_size = len(response.content)
                    
                    if baseline_response is None:
                        baseline_response = response_size
                        baseline_id = test_id
                    else:
                        # Compare with baseline
                        if response_size == baseline_response:
                            # Same structure - potential IDOR
                            findings.append({
                                'type': 'idor',
                                'endpoint': url,
                                'baseline_id': baseline_id,
                                'test_id': test_id,
                                'response_size': response_size,
                                'status_code': 200,
                                'confidence': 'high' if response_size > 100 else 'medium'
                            })
                            self.logger.warning(f"[LOGIC BREAKER] Potential IDOR: {url} (same structure as {baseline_id})")
                
            except Exception as e:
                self.logger.debug(f"[LOGIC BREAKER] IDOR test failed for ID {test_id}: {e}")
        
        self.findings.extend(findings)
        return findings
    
    def get_findings(self) -> List[Dict]:
        """Get all logic vulnerability findings."""
        return self.findings
