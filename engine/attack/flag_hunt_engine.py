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
        Execute aggressive flag hunting on web and network.
        
        Returns:
            Dictionary with all found flags
        """
        self.logger.info(f"[FLAG HUNT] Starting aggressive flag hunt on {self.target}")
        
        # Phase 1: Web application flag hunting
        self.logger.info("[FLAG HUNT] Phase 1: Web application scanning...")
        web_results = await self._hunt_web_flags()
        
        # Phase 2: Network service flag hunting
        self.logger.info("[FLAG HUNT] Phase 2: Network service scanning...")
        network_results = await self._hunt_network_flags()
        
        # Phase 3: Deep crawl for hidden flags
        self.logger.info("[FLAG HUNT] Phase 3: Deep crawling for hidden flags...")
        crawl_results = await self._deep_crawl_flags()
        
        # Phase 4: Response header analysis
        self.logger.info("[FLAG HUNT] Phase 4: Response header analysis...")
        header_flags = await self._scan_headers()
        
        # Phase 5: Source code analysis
        self.logger.info("[FLAG HUNT] Phase 5: Source code analysis...")
        source_flags = await self._scan_source_code()
        
        return {
            "target": self.target,
            "total_flags": len(self.flags_found),
            "flags": list(self.flags_found),
            "web_flags": web_results,
            "network_flags": network_results,
            "crawl_flags": crawl_results,
            "header_flags": header_flags,
            "source_flags": source_flags,
            "all_flags": {
                "web": self.web_flags,
                "network": self.network_flags
            }
        }
    
    async def _hunt_web_flags(self) -> Dict:
        """Aggressively hunt flags in web application."""
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
                    flags = await self.flag_hunter.hunt_flags(response.text, url)
                    if flags:
                        flags_found.extend(flags)
                        self.web_flags.append({
                            "url": url,
                            "flags": flags,
                            "method": "direct_access"
                        })
                        self.logger.warning(f"[FLAG HUNT] Found flags at {url}: {flags}")
            except Exception as e:
                self.logger.debug(f"[FLAG HUNT] Failed to check {location}: {e}")
        
        # 2. Aggressive crawling with flag focus
        self.logger.info("[FLAG HUNT] Aggressive crawling for flags...")
        crawl_results = await self.crawler.crawl(max_depth=5)  # Deeper crawl for flags
        
        # Scan all discovered endpoints for flags
        endpoints = crawl_results.get("endpoints_discovered", [])
        for endpoint in endpoints[:100]:  # Limit to prevent timeout
            try:
                if self.session:
                    response = await self.session.get(endpoint, timeout=5.0)
                else:
                    async with httpx.AsyncClient(verify=False, timeout=5.0) as client:
                        response = await client.get(endpoint)
                
                if response.status_code == 200:
                    flags = await self.flag_hunter.hunt_flags(response.text, endpoint)
                    if flags:
                        flags_found.extend(flags)
                        self.web_flags.append({
                            "url": endpoint,
                            "flags": flags,
                            "method": "crawl_discovery"
                        })
            except Exception as e:
                self.logger.debug(f"[FLAG HUNT] Failed to scan {endpoint}: {e}")
        
        # 3. Check robots.txt, sitemap.xml, etc.
        self.logger.info("[FLAG HUNT] Checking common files...")
        common_files = ['/robots.txt', '/sitemap.xml', '/.well-known/security.txt', '/.git/config', '/.env']
        for file_path in common_files:
            try:
                url = urljoin(self.target, file_path)
                if self.session:
                    response = await self.session.get(url, timeout=5.0)
                else:
                    async with httpx.AsyncClient(verify=False, timeout=5.0) as client:
                        response = await client.get(url)
                
                if response.status_code == 200:
                    flags = await self.flag_hunter.hunt_flags(response.text, url)
                    if flags:
                        flags_found.extend(flags)
                        self.web_flags.append({
                            "url": url,
                            "flags": flags,
                            "method": "common_file"
                        })
            except Exception as e:
                self.logger.debug(f"[FLAG HUNT] Failed to check {file_path}: {e}")
        
        return {
            "flags_found": flags_found,
            "locations_checked": len(self.flag_locations) + len(endpoints) + len(common_files),
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
                        flags = await self.flag_hunter.hunt_flags(response.text, url)
                        if flags:
                            result['flags'] = flags
                            result['service'] = 'http'
                            self.logger.warning(f"[FLAG HUNT] Found flags on {host}:{port}: {flags}")
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
                        flags = await self.flag_hunter.hunt_flags(response.text, url)
                        if flags:
                            result['flags'] = flags
                            result['service'] = 'https'
                            self.logger.warning(f"[FLAG HUNT] Found flags on {host}:{port}: {flags}")
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
                    flags = await self.flag_hunter.hunt_flags(response.text, url)
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
        """Scan HTTP headers for flags."""
        flags_found = []
        
        try:
            if self.session:
                response = await self.session.get(self.target)
            else:
                async with httpx.AsyncClient(verify=False, timeout=5.0) as client:
                    response = await client.get(self.target)
            
            # Check all headers for flag patterns
            for header_name, header_value in response.headers.items():
                for pattern in self.flag_patterns:
                    matches = re.findall(pattern, header_value, re.IGNORECASE)
                    if matches:
                        flags_found.extend(matches)
                        self.logger.warning(f"[FLAG HUNT] Found flag in header {header_name}: {matches}")
        
        except Exception as e:
            self.logger.debug(f"[FLAG HUNT] Header scan failed: {e}")
        
        return {
            "flags_found": flags_found,
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
                    flags = await self.flag_hunter.hunt_flags(response.text, js_url)
                    if flags:
                        flags_found.extend(flags)
                        self.logger.warning(f"[FLAG HUNT] Found flags in JS {js_url}: {flags}")
            except Exception as e:
                self.logger.debug(f"[FLAG HUNT] Failed to scan JS {js_url}: {e}")
        
        return {
            "flags_found": flags_found,
            "files_scanned": len(js_files),
            "flags_count": len(flags_found)
        }
