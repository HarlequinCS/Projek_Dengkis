"""
Sophisticated HTTP request handler for aggressive security assessment.
Performs comprehensive read-only reconnaissance through behavioral observation.
"""
import httpx
import asyncio
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import random
import string
from urllib.parse import urljoin, urlparse
import ssl
import time
import statistics

from engine.utils.retry import RetryConfig, retry_with_backoff
from engine.utils.throttle import ThrottleConfig, get_throttler
from engine.logging.logger import get_logger


class AggressiveRequestHandler:
    """
    Advanced HTTP request handler designed for aggressive security assessment.
    Implements sophisticated request techniques to extract maximum information
    from target systems while remaining within read-only assessment boundaries.
    """

    def __init__(
        self,
        stealth_mode: bool = False,
        timeout: float = 30.0,
        retry_config: Optional[RetryConfig] = None,
        throttle_config: Optional[ThrottleConfig] = None,
        session_id: Optional[str] = None
    ):
        """
        Initialize request handler.

        Args:
            stealth_mode: Enable stealth mode for reduced detection
            timeout: Request timeout in seconds
            retry_config: Retry configuration
            throttle_config: Throttle configuration
            session_id: Session ID for logging
        """
        self.stealth_mode = stealth_mode
        self.timeout = timeout
        self.session: Optional[httpx.AsyncClient] = None
        self.request_history: List[Dict] = []
        self.response_patterns: Dict[str, List[Dict]] = {}
        self.session_id = session_id
        self.logger = get_logger(session_id)

        # Retry and throttle configuration
        self.retry_config = retry_config or RetryConfig(timeout=timeout)
        self.throttler = get_throttler(throttle_config)

        # SSL context for certificate verification bypass (assessment only)
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

        self.client_config = {
            "timeout": httpx.Timeout(timeout, connect=10.0),
            "verify": False,  # SSL verification disabled for assessment
            "follow_redirects": True,
            "http2": True,    # Enable HTTP/2 for multiplexing
            "limits": httpx.Limits(
                max_keepalive_connections=50,
                max_connections=100,
                keepalive_expiry=30.0
            )
        }

    async def __aenter__(self):
        """Async context manager entry."""
        self.session = httpx.AsyncClient(**self.client_config)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.aclose()

    async def _get_session(self) -> httpx.AsyncClient:
        """Get or create HTTP session."""
        if self.session is None:
            self.session = httpx.AsyncClient(**self.client_config)
        return self.session

    def _generate_user_agent(self) -> str:
        """Generate user agent string."""
        if self.stealth_mode:
            # Use common user agent in stealth mode
            agents = [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
            ]
            return random.choice(agents)
        else:
            return "PROJEK-DENGKIS/1.0 Security Assessment Tool"

    async def probe_target(self, target: str, probe_vectors: List[str]) -> Dict:
        """
        Aggressively probe target with various request vectors to extract
        behavioral information without exploitation.

        Args:
            target: Target URL or IP
            probe_vectors: List of probe vectors/paths to test

        Returns:
            Dict containing behavioral analysis results
        """
        if not target.startswith(('http://', 'https://')):
            target = f"https://{target}"

        results = {
            "target": target,
            "probe_timestamp": datetime.utcnow().isoformat(),
            "vectors_tested": len(probe_vectors),
            "responses": [],
            "behavioral_indicators": {},
            "patterns_detected": []
        }

        session = await self._get_session()

        for vector in probe_vectors:
            try:
                url = urljoin(target, vector)
                start_time = time.time()

                # Apply throttling before request
                await self.throttler.acquire(target)

                # Make request with retry logic
                response = await retry_with_backoff(
                    session.get,
                    url,
                    headers={"User-Agent": self._generate_user_agent()},
                    config=self.retry_config
                )

                response_time = time.time() - start_time

                response_data = {
                    "vector": vector,
                    "url": url,
                    "status_code": response.status_code,
                    "response_time": response_time,
                    "headers": dict(response.headers),
                    "content_length": len(response.content),
                    "redirect_location": response.headers.get("Location"),
                    "server": response.headers.get("Server", ""),
                    "content_type": response.headers.get("Content-Type", "")
                }

                results["responses"].append(response_data)

                # Record request in history
                self.request_history.append({
                    "timestamp": datetime.utcnow().isoformat(),
                    "method": "GET",
                    "url": url,
                    "status_code": response.status_code,
                    "response_time": response_time
                })

                self.logger.debug(f"Probed {url}: {response.status_code}")

            except (httpx.TimeoutException, asyncio.TimeoutError) as e:
                self.logger.warning(f"Request timeout for {url}: {e}")
                results["responses"].append({
                    "vector": vector,
                    "url": urljoin(target, vector),
                    "status_code": None,
                    "error": "timeout",
                    "response_time": None
                })
            except Exception as e:
                self.logger.error(f"Request failed for {urljoin(target, vector)}: {e}")
                results["responses"].append({
                    "vector": vector,
                    "url": urljoin(target, vector),
                    "status_code": None,
                    "error": str(e),
                    "response_time": None
                })

        # Analyze behavioral indicators
        results["behavioral_indicators"] = self._analyze_behavioral_indicators(results["responses"])
        results["patterns_detected"] = self._detect_patterns(results["responses"])

        return results

    async def analyze_response_timing(self, target: str, endpoints: List[str]) -> Dict:
        """
        Analyze response timing patterns across multiple endpoints to identify
        potential vulnerabilities through timing differences.

        Args:
            target: Target URL
            endpoints: List of endpoints to test

        Returns:
            Dict containing timing analysis results
        """
        if not target.startswith(('http://', 'https://')):
            target = f"https://{target}"

        timing_results = {
            "target": target,
            "analysis_timestamp": datetime.utcnow().isoformat(),
            "endpoints_tested": len(endpoints),
            "timing_data": [],
            "statistical_analysis": {},
            "anomalies": []
        }

        session = await self._get_session()
        response_times = []

        for endpoint in endpoints:
            url = urljoin(target, endpoint)
            times = []

            # Make multiple requests to measure timing consistency
            for _ in range(3):
                try:
                    await self.throttler.acquire(target)
                    start_time = time.time()
                    response = await retry_with_backoff(
                        session.get,
                        url,
                        headers={"User-Agent": self._generate_user_agent()},
                        config=self.retry_config
                    )
                    elapsed = time.time() - start_time
                    times.append(elapsed)
                    response_times.append(elapsed)
                except Exception as e:
                    self.logger.debug(f"Timing request failed for {url}: {e}")
                    pass

            if times:
                timing_results["timing_data"].append({
                    "endpoint": endpoint,
                    "times": times,
                    "average": statistics.mean(times),
                    "min": min(times),
                    "max": max(times),
                    "std_dev": statistics.stdev(times) if len(times) > 1 else 0
                })

        # Statistical analysis
        if response_times:
            timing_results["statistical_analysis"] = {
                "overall_average": statistics.mean(response_times),
                "overall_median": statistics.median(response_times),
                "overall_std_dev": statistics.stdev(response_times) if len(response_times) > 1 else 0,
                "min_response_time": min(response_times),
                "max_response_time": max(response_times)
            }

            # Detect timing anomalies
            mean = timing_results["statistical_analysis"]["overall_average"]
            std_dev = timing_results["statistical_analysis"]["overall_std_dev"]

            for endpoint_data in timing_results["timing_data"]:
                if endpoint_data["average"] > mean + (2 * std_dev):
                    timing_results["anomalies"].append({
                        "endpoint": endpoint_data["endpoint"],
                        "type": "slow_response",
                        "average_time": endpoint_data["average"],
                        "deviation": endpoint_data["average"] - mean
                    })
                elif endpoint_data["average"] < mean - (2 * std_dev):
                    timing_results["anomalies"].append({
                        "endpoint": endpoint_data["endpoint"],
                        "type": "fast_response",
                        "average_time": endpoint_data["average"],
                        "deviation": mean - endpoint_data["average"]
                    })

        return timing_results

    async def extract_behavioral_fingerprint(self, target: str) -> Dict:
        """
        Extract comprehensive behavioral fingerprint by analyzing responses
        to various crafted requests designed to elicit revealing responses.

        Args:
            target: Target URL

        Returns:
            Dict containing behavioral fingerprint
        """
        if not target.startswith(('http://', 'https://')):
            target = f"https://{target}"

        fingerprint = {
            "target": target,
            "fingerprint_timestamp": datetime.utcnow().isoformat(),
            "probes": [],
            "technologies": [],
            "security_headers": [],
            "response_characteristics": {},
            "error_patterns": []
        }

        session = await self._get_session()

        # Test various paths to extract information
        test_paths = [
            "/",
            "/robots.txt",
            "/.well-known/security.txt",
            "/favicon.ico",
            "/admin",
            "/api",
            "/test",
            "/.git/config",
            "/.env"
        ]

        for path in test_paths:
            try:
                url = urljoin(target, path)

                # Apply throttling
                await self.throttler.acquire(target)

                start_time = time.time()
                response = await retry_with_backoff(
                    session.get,
                    url,
                    headers={"User-Agent": self._generate_user_agent()},
                    config=self.retry_config
                )

                response_time = time.time() - start_time

                probe_result = {
                    "path": path,
                    "status_code": response.status_code,
                    "response_time": response_time,
                    "headers": dict(response.headers),
                    "server": response.headers.get("Server", ""),
                    "content_type": response.headers.get("Content-Type", ""),
                    "content_length": len(response.content)
                }

                fingerprint["probes"].append(probe_result)

                # Extract technologies
                server = response.headers.get("Server", "").lower()
                if server:
                    fingerprint["technologies"].append(server)

                # Extract security headers
                security_headers = [
                    "X-Frame-Optional, ns", "X-Content-Type-Optional, ns",
                    "Strict-Transport-Security", "Content-Security-Policy",
                    "X-XSS-Protection", "Referrer-Policy"
                ]
                for header in security_headers:
                    if header in response.headers:
                        fingerprint["security_headers"].append({
                            "header": header,
                            "value": response.headers[header]
                        })

                # Analyze error patterns
                if response.status_code >= 400:
                    fingerprint["error_patterns"].append({
                        "path": path,
                        "status_code": response.status_code,
                        "error_type": self._classify_error(response.status_code)
                    })

            except Exception as e:
                fingerprint["probes"].append({
                    "path": path,
                    "error": str(e)
                })

        # Extract unique technologies and headers
        fingerprint["technologies"] = list(set(fingerprint["technologies"]))

        # Calculate response characteristics
        response_times = [p.get("response_time", 0) for p in fingerprint["probes"] if p.get("response_time")]
        if response_times:
            fingerprint["response_characteristics"] = {
                "average_response_time": statistics.mean(response_times),
                "min_response_time": min(response_times),
                "max_response_time": max(response_times)
            }

        return fingerprint

    async def test_boundary_conditions(self, target: str, boundary_vectors: List[str]) -> Dict:
        """
        Test boundary conditions with carefully crafted requests that push
        systems to their limits without crossing exploitation boundaries.

        Args:
            target: Target URL
            boundary_vectors: List of boundary condition vectors

        Returns:
            Dict containing boundary condition test results
        """
        if not target.startswith(('http://', 'https://')):
            target = f"https://{target}"

        boundary_results = {
            "target": target,
            "test_timestamp": datetime.utcnow().isoformat(),
            "vectors_tested": len(boundary_vectors),
            "results": [],
            "anomalies": []
        }

        session = await self._get_session()

        for vector in boundary_vectors:
            try:
                url = urljoin(target, vector)

                # Test with various request methods
                methods = ["GET", "POST", "PUT", "DELETE", "Optional, NS", "HEAD"]
                for method in methods:
                    try:
                        response = await session.request(
                            method,
                            url,
                            headers={"User-Agent": self._generate_user_agent()},
                            timeout=self.timeout
                        )

                        result = {
                            "vector": vector,
                            "method": method,
                            "status_code": response.status_code,
                            "headers": dict(response.headers),
                            "allows_method": response.status_code not in [405, 501]
                        }

                        boundary_results["results"].append(result)

                        # Detect anomalies
                        if method == "Optional, NS" and "Allow" in response.headers:
                            allowed_methods = response.headers["Allow"].split(", ")
                            if len(allowed_methods) > 5:
                                boundary_results["anomalies"].append({
                                    "type": "excessive_methods_allowed",
                                    "vector": vector,
                                    "methods": allowed_methods
                                })

                    except Exception:
                        pass

            except Exception as e:
                boundary_results["results"].append({
                    "vector": vector,
                    "error": str(e)
                })

        return boundary_results

    async def analyze_error_messages(self, target: str, error_vectors: List[str]) -> Dict:
        """
        Analyze error messages to extract information about underlying
        technologies, configurations, and potential vulnerabilities.

        Args:
            target: Target URL
            error_vectors: List of vectors designed to trigger errors

        Returns:
            Dict containing error message analysis
        """
        if not target.startswith(('http://', 'https://')):
            target = f"https://{target}"

        error_analysis = {
            "target": target,
            "analysis_timestamp": datetime.utcnow().isoformat(),
            "vectors_tested": len(error_vectors),
            "errors": [],
            "technology_indicators": [],
            "information_disclosure": []
        }

        session = await self._get_session()

        for vector in error_vectors:
            try:
                url = urljoin(target, vector)

                # Apply throttling
                await self.throttler.acquire(target)

                response = await retry_with_backoff(
                    session.get,
                    url,
                    headers={"User-Agent": self._generate_user_agent()},
                    config=self.retry_config
                )

                if response.status_code >= 400:
                    error_info = {
                        "vector": vector,
                        "status_code": response.status_code,
                        "error_type": self._classify_error(response.status_code),
                        "response_headers": dict(response.headers),
                        "response_body_snippet": response.text[:500] if response.text else ""
                    }

                    error_analysis["errors"].append(error_info)

                    # Extract technology indicators
                    tech_indicators = self._extract_technology_indicators(response)
                    error_analysis["technology_indicators"].extend(tech_indicators)

                    # Check for information disclosure
                    disclosures = self._check_information_disclosure(response)
                    error_analysis["information_disclosure"].extend(disclosures)

            except Exception as e:
                error_analysis["errors"].append({
                    "vector": vector,
                    "error": str(e)
                })

        return error_analysis

    def _analyze_behavioral_indicators(self, responses: List[Dict]) -> Dict:
        """Analyze behavioral indicators from responses."""
        indicators = {
            "response_variability": 0,
            "redirect_patterns": [],
            "server_consistency": False,
            "header_consistency": {}
        }

        status_codes = [r.get("status_code") for r in responses if r.get("status_code")]
        if status_codes:
            unique_statuses = set(status_codes)
            indicators["response_variability"] = len(unique_statuses) / len(status_codes) if status_codes else 0

        redirects = [r for r in responses if r.get("redirect_location")]
        indicators["redirect_patterns"] = [r.get("redirect_location") for r in redirects]

        servers = [r.get("server", "") for r in responses if r.get("server")]
        if servers:
            indicators["server_consistency"] = len(set(servers)) == 1

        return indicators

    def _detect_patterns(self, responses: List[Dict]) -> List[Dict]:
        """Detect patterns in responses."""
        patterns = []

        # Check for consistent error patterns
        error_responses = [r for r in responses if r.get("status_code", 0) >= 400]
        if len(error_responses) > len(responses) * 0.5:
            patterns.append({
                "type": "high_error_rate",
                "description": "High proportion of error responses",
                "error_rate": len(error_responses) / len(responses)
            })

        # Check for timing patterns
        response_times = [r.get("response_time") for r in responses if r.get("response_time")]
        if response_times and len(response_times) > 1:
            avg_time = statistics.mean(response_times)
            std_dev = statistics.stdev(response_times)
            if std_dev > avg_time * 0.5:
                patterns.append({
                    "type": "inconsistent_response_times",
                    "description": "Highly variable response times",
                    "std_dev": std_dev,
                    "average": avg_time
                })

        return patterns

    def _classify_error(self, status_code: int) -> str:
        """Classify HTTP error type."""
        if 400 <= status_code < 500:
            return "client_error"
        elif 500 <= status_code < 600:
            return "server_error"
        else:
            return "unknown_error"

    def _extract_technology_indicators(self, response: httpx.Response) -> List[Dict]:
        """Extract technology indicators from response."""
        indicators = []

        # Check Server header
        server = response.headers.get("Server", "")
        if server:
            indicators.append({"type": "server", "value": server})

        # Check X-Powered-By header
        powered_by = response.headers.get("X-Powered-By", "")
        if powered_by:
            indicators.append({"type": "framework", "value": powered_by})

        # Analyze response body for technology indicators
        if response.text:
            body_lower = response.text.lower()
            tech_keywords = {
                "apache": "webserver",
                "nginx": "webserver",
                "iis": "webserver",
                "php": "language",
                "python": "language",
                "django": "framework",
                "flask": "framework",
                "rails": "framework",
                "node": "runtime"
            }

            for keyword, tech_type in tech_keywords.items():
                if keyword in body_lower:
                    indicators.append({"type": tech_type, "value": keyword})

        return indicators

    def _check_information_disclosure(self, response: httpx.Response) -> List[Dict]:
        """Check for information disclosure in error responses."""
        disclosures = []

        if response.text:
            body_lower = response.text.lower()

            # Check for file paths
            if "c:\\" in body_lower or "/var/" in body_lower or "/home/" in body_lower:
                disclosures.append({
                    "type": "file_path_disclosure",
                    "severity": "medium",
                    "description": "File paths visible in error message"
                })

            # Check for stack traces
            if "stack trace" in body_lower or "traceback" in body_lower:
                disclosures.append({
                    "type": "stack_trace_disclosure",
                    "severity": "high",
                    "description": "Stack trace visible in error message"
                })

            # Check for SQL errors
            if "sql" in body_lower and "error" in body_lower:
                disclosures.append({
                    "type": "database_error_disclosure",
                    "severity": "medium",
                    "description": "Database error information visible"
                })

        return disclosures

    async def close(self):
        """Close HTTP session."""
        if self.session:
            await self.session.aclose()
            self.session = None
