"""
AGGRESSIVE CRAWLER - Attack-driven surface discovery.
Extracts every possible endpoint, parameter, and attack vector.
Think like an attacker: assume everything is vulnerable until proven otherwise.
"""
import re
import json
import asyncio
from typing import Dict, List, Optional, Set, Tuple
from urllib.parse import urlparse, urljoin, parse_qs, urlencode, unquote
from html.parser import HTMLParser
import httpx
from collections import defaultdict

from engine.logging.logger import get_logger


class AggressiveCrawler:
    """
    Aggressive crawler that extracts attack surface from:
    - HTML links, forms, scripts
    - JavaScript files and inline scripts
    - JSON responses and API endpoints
    - Hidden endpoints (REST, GraphQL, admin paths)
    - Parameters from query strings, POST bodies, headers
    - SPA hash routes
    """
    
    def __init__(self, target: str, session: Optional[httpx.AsyncClient] = None):
        # Normalize target URL
        self.target = self._normalize_target(target)
        self.session = session
        self.logger = get_logger()
        self.logger.info(f"[CRAWLER] Initialized with target: {self.target}")
        
        # Discovered attack surface
        self.endpoints: Set[str] = set()
        self.parameters: Dict[str, List[str]] = defaultdict(list)  # endpoint -> [params]
        self.forms: List[Dict] = []
        self.api_endpoints: List[Dict] = []
        self.graphql_endpoints: List[str] = []
        self.js_files: List[str] = []
        self.json_responses: List[Dict] = []
        
        # Common paths to brute force
        self.common_paths = [
            # Admin/Debug
            "/admin", "/administrator", "/wp-admin", "/wp-login.php",
            "/admin/login", "/admin/dashboard", "/admin/panel",
            "/debug", "/debug.php", "/test", "/testing",
            "/.env", "/.git/config", "/.git/HEAD", "/.svn/entries",
            "/config.php", "/config.json", "/config.yaml",
            "/backup", "/backups", "/backup.sql", "/dump.sql",
            
            # API endpoints
            "/api", "/api/v1", "/api/v2", "/api/v3",
            "/rest", "/rest/api", "/graphql", "/graphiql",
            "/swagger", "/swagger.json", "/swagger-ui",
            "/openapi.json", "/api-docs", "/api/docs",
            
            # Common frameworks
            "/actuator", "/actuator/health", "/actuator/env",
            "/.well-known/security.txt", "/robots.txt", "/sitemap.xml",
            "/phpinfo.php", "/info.php", "/server-status",
            
            # Auth endpoints
            "/login", "/signin", "/auth", "/authenticate",
            "/logout", "/signout", "/register", "/signup",
            "/reset-password", "/forgot-password", "/password-reset",
            
            # Files
            "/uploads", "/files", "/download", "/downloads",
            "/static", "/assets", "/media", "/images",
        ]
        
        # SPA hash route patterns
        self.spa_patterns = [
            "/#/", "/#!/", "/#/admin", "/#!/admin",
            "/#/api", "/#!/api", "/#/login", "/#!/login"
        ]
    
    def _normalize_target(self, target: str) -> str:
        """Normalize target URL to ensure proper scheme and format."""
        target = target.strip()
        
        # If no scheme, default to HTTPS
        if not target.startswith(('http://', 'https://')):
            target = f"https://{target}"
        
        # Parse and normalize
        from urllib.parse import urlparse, urlunparse
        parsed = urlparse(target)
        
        # Ensure scheme
        scheme = parsed.scheme or 'https'
        
        # Ensure netloc
        if not parsed.netloc:
            # Try to extract domain from path
            if parsed.path and '/' not in parsed.path:
                netloc = parsed.path
                path = '/'
            else:
                netloc = parsed.path.split('/')[0] if parsed.path else ''
                path = '/' + '/'.join(parsed.path.split('/')[1:]) if '/' in parsed.path else '/'
        else:
            netloc = parsed.netloc
            path = parsed.path or '/'
        
        # Normalize port (remove default ports)
        if ':' in netloc:
            host, port = netloc.rsplit(':', 1)
            if (scheme == 'https' and port == '443') or (scheme == 'http' and port == '80'):
                netloc = host
        
        # Reconstruct
        normalized = urlunparse((scheme, netloc, path, parsed.params, parsed.query, parsed.fragment))
        return normalized
    
    async def crawl(self, max_depth: int = 3) -> Dict:
        """
        Aggressively crawl the target to discover attack surface.
        
        Args:
            max_depth: Maximum crawl depth
            
        Returns:
            Dictionary containing discovered attack surface
        """
        self.logger.info(f"[CRAWLER] Starting aggressive crawl of {self.target} (max_depth={max_depth})")
        
        # Execute immediate probe (GET request to root)
        probe_count = 0
        try:
            self.logger.info(f"[PROBE] Executing initial probe: GET {self.target}")
            if self.session:
                response = await self.session.get(self.target)
                probe_count += 1
                self.logger.info(f"[PROBE] Initial probe completed: {response.status_code} ({probe_count} probe executed)")
            else:
                async with httpx.AsyncClient(verify=False, timeout=10.0) as client:
                    response = await client.get(self.target)
                    probe_count += 1
                    self.logger.info(f"[PROBE] Initial probe completed: {response.status_code} ({probe_count} probe executed)")
        except Exception as e:
            self.logger.warning(f"[PROBE] Initial probe failed: {e}")
        
        # Start with root
        await self._crawl_url(self.target, depth=0, max_depth=max_depth)
        
        # Brute force common paths
        await self._brute_force_paths()
        
        # Extract from discovered pages (more aggressive in aggressive mode)
        endpoint_limit = 200 if max_depth >= 3 else 50  # More endpoints for deeper crawls
        for endpoint in list(self.endpoints)[:endpoint_limit]:
            try:
                await self._extract_from_page(endpoint)
            except Exception as e:
                self.logger.debug(f"Failed to extract from {endpoint}: {e}")
        
        # Extract from JS files (more aggressive)
        js_limit = 50 if max_depth >= 3 else 20
        for js_url in self.js_files[:js_limit]:
            try:
                await self._extract_from_js(js_url)
            except Exception as e:
                self.logger.debug(f"Failed to extract from JS {js_url}: {e}")
        
        return {
            "target": self.target,
            "endpoints_discovered": list(self.endpoints),
            "parameters": dict(self.parameters),
            "forms": self.forms,
            "api_endpoints": self.api_endpoints,
            "graphql_endpoints": self.graphql_endpoints,
            "total_endpoints": len(self.endpoints),
            "total_parameters": sum(len(params) for params in self.parameters.values())
        }
    
    async def _crawl_url(self, url: str, depth: int = 0, max_depth: int = 3):
        """Crawl a URL and extract attack surface."""
        if depth > max_depth or url in self.endpoints:
            return
        
        if not url.startswith(('http://', 'https://')):
            url = urljoin(self.target, url)
        
        self.endpoints.add(url)
        self.logger.debug(f"[CRAWLER] Crawling URL (depth={depth}): {url}")
        
        try:
            if not self.session:
                async with httpx.AsyncClient(verify=False, timeout=10.0) as client:
                    response = await client.get(url)
                    self.logger.debug(f"[PROBE] GET {url} -> {response.status_code}")
                    await self._extract_from_response(url, response)
            else:
                response = await self.session.get(url)
                self.logger.debug(f"[PROBE] GET {url} -> {response.status_code}")
                await self._extract_from_response(url, response)
        except Exception as e:
            self.logger.warning(f"[PROBE] Failed to crawl {url}: {e}")
    
    async def _extract_from_response(self, url: str, response: httpx.Response):
        """Extract attack surface from HTTP response."""
        content_type = response.headers.get("Content-Type", "").lower()
        
        # Extract parameters from URL
        parsed = urlparse(url)
        if parsed.query:
            params = parse_qs(parsed.query)
            self.parameters[url].extend(params.keys())
        
        # Extract from HTML
        if "text/html" in content_type:
            await self._extract_from_html(url, response.text)
        
        # Extract from JSON
        elif "application/json" in content_type:
            await self._extract_from_json(url, response.text)
        
        # Check for GraphQL
        if "/graphql" in url.lower() or (response.text and "graphql" in response.text.lower()):
            self.graphql_endpoints.append(url)
    
    async def _extract_from_html(self, url: str, html: str):
        """Extract links, forms, and parameters from HTML."""
        parser = HTMLLinkFormExtractor(url, self)
        parser.feed(html)
        
        # Extract inline script content
        script_pattern = r'<script[^>]*>(.*?)</script>'
        scripts = re.findall(script_pattern, html, re.DOTALL | re.IGNORECASE)
        for script in scripts:
            await self._extract_from_js_content(url, script)
        
        # Extract from data attributes and JavaScript variables
        js_var_pattern = r'(?:var|let|const)\s+(\w+)\s*=\s*["\']([^"\']+)["\']'
        js_vars = re.findall(js_var_pattern, html)
        for var_name, var_value in js_vars:
            if any(path in var_value for path in ['/api', '/admin', '/login']):
                potential_endpoint = urljoin(url, var_value)
                self.endpoints.add(potential_endpoint)
    
    async def _extract_from_json(self, url: str, json_text: str):
        """Extract endpoints and parameters from JSON responses."""
        try:
            data = json.loads(json_text)
            self.json_responses.append({"url": url, "data": data})
            
            # Look for endpoint patterns in JSON
            json_str = json.dumps(data)
            endpoint_patterns = [
                r'["\']([^"\']*(?:api|endpoint|url|path)[^"\']*)["\']',
                r'/(?:api|v\d+|rest|graphql)[^"\s]*',
            ]
            
            for pattern in endpoint_patterns:
                matches = re.findall(pattern, json_str, re.IGNORECASE)
                for match in matches:
                    if isinstance(match, tuple):
                        match = match[0]
                    if match.startswith('/') or 'http' in match:
                        endpoint = urljoin(url, match) if match.startswith('/') else match
                        self.endpoints.add(endpoint)
        except json.JSONDecodeError:
            pass
    
    async def _extract_from_js(self, js_url: str):
        """Extract endpoints and parameters from JavaScript files."""
        try:
            if not self.session:
                async with httpx.AsyncClient(verify=False, timeout=10.0) as client:
                    response = await client.get(js_url)
                    await self._extract_from_js_content(js_url, response.text)
            else:
                response = await self.session.get(js_url)
                await self._extract_from_js_content(js_url, response.text)
        except Exception as e:
            self.logger.debug(f"Failed to fetch JS {js_url}: {e}")
    
    async def _extract_from_js_content(self, source_url: str, js_content: str):
        """Extract endpoints from JavaScript content."""
        # API endpoint patterns
        patterns = [
            r'["\']([^"\']*(?:/api|/rest|/graphql|/admin|/login)[^"\']*)["\']',
            r'fetch\s*\(\s*["\']([^"\']+)["\']',
            r'axios\.(?:get|post|put|delete)\s*\(\s*["\']([^"\']+)["\']',
            r'\.ajax\s*\(\s*\{[^}]*url\s*:\s*["\']([^"\']+)["\']',
            r'url\s*:\s*["\']([^"\']+)["\']',
            r'endpoint\s*:\s*["\']([^"\']+)["\']',
            r'path\s*:\s*["\']([^"\']+)["\']',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, js_content, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    match = match[0] if match else ""
                if match and ('/' in match or 'http' in match):
                    endpoint = urljoin(source_url, match) if match.startswith('/') else match
                    self.endpoints.add(endpoint)
                    
                    # Extract parameters from URL patterns
                    if '?' in match:
                        param_part = match.split('?')[1].split('&')[0]
                        if '=' in param_part:
                            param_name = param_part.split('=')[0]
                            self.parameters[endpoint].append(param_name)
        
        # Extract GraphQL queries
        if 'graphql' in js_content.lower() or 'query' in js_content.lower():
            graphql_pattern = r'["\']([^"\']*graphql[^"\']*)["\']'
            graphql_matches = re.findall(graphql_pattern, js_content, re.IGNORECASE)
            for match in graphql_matches:
                self.graphql_endpoints.append(urljoin(source_url, match))
    
    async def _brute_force_paths(self):
        """Brute force common paths to discover hidden endpoints."""
        self.logger.info(f"[ATTACK] Brute forcing {len(self.common_paths)} common paths")
        
        tasks = []
        for path in self.common_paths:
            url = urljoin(self.target, path)
            tasks.append(self._probe_path(url))
        
        # Limit concurrent requests
        for i in range(0, len(tasks), 10):
            batch = tasks[i:i+10]
            await asyncio.gather(*batch, return_exceptions=True)
    
    async def _probe_path(self, url: str):
        """Probe a path to see if it exists."""
        try:
            if not self.session:
                async with httpx.AsyncClient(verify=False, timeout=5.0) as client:
                    response = await client.get(url, follow_redirects=True)
            else:
                response = await self.session.get(url, follow_redirects=True)
            
            # Accept any response as potential endpoint
            if response.status_code < 500:  # Don't count server errors
                self.endpoints.add(url)
                self.logger.debug(f"[ATTACK] Discovered endpoint: {url} ({response.status_code})")
        except Exception:
            pass
    
    async def _extract_from_page(self, url: str):
        """Extract additional attack surface from a page."""
        try:
            if not self.session:
                async with httpx.AsyncClient(verify=False, timeout=10.0) as client:
                    response = await client.get(url)
                    await self._extract_from_response(url, response)
            else:
                response = await self.session.get(url)
                await self._extract_from_response(url, response)
        except Exception:
            pass


class HTMLLinkFormExtractor(HTMLParser):
    """HTML parser to extract links, forms, and parameters."""
    
    def __init__(self, base_url: str, crawler: AggressiveCrawler):
        super().__init__()
        self.base_url = base_url
        self.crawler = crawler
        self.current_form = None
    
    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        
        # Extract links
        if tag == 'a' and 'href' in attrs_dict:
            href = attrs_dict['href']
            if href and not href.startswith(('javascript:', 'mailto:', '#')):
                endpoint = urljoin(self.base_url, href)
                self.crawler.endpoints.add(endpoint)
                
                # Extract parameters from href
                if '?' in href:
                    parsed = urlparse(href)
                    if parsed.query:
                        params = parse_qs(parsed.query)
                        self.crawler.parameters[endpoint].extend(params.keys())
        
        # Extract forms
        if tag == 'form':
            self.current_form = {
                'action': attrs_dict.get('action', ''),
                'method': attrs_dict.get('method', 'GET').upper(),
                'inputs': []
            }
        
        # Extract form inputs
        if tag == 'input' and self.current_form is not None:
            input_name = attrs_dict.get('name', '')
            input_type = attrs_dict.get('type', 'text')
            if input_name:
                self.current_form['inputs'].append({
                    'name': input_name,
                    'type': input_type
                })
                # Add parameter
                form_url = urljoin(self.base_url, self.current_form['action'])
                self.crawler.parameters[form_url].append(input_name)
        
        # Extract script sources
        if tag == 'script' and 'src' in attrs_dict:
            src = attrs_dict['src']
            if src:
                js_url = urljoin(self.base_url, src)
                self.crawler.js_files.append(js_url)
    
    def handle_endtag(self, tag):
        if tag == 'form' and self.current_form:
            form_url = urljoin(self.base_url, self.current_form['action'])
            self.crawler.forms.append({
                'url': form_url,
                'method': self.current_form['method'],
                'inputs': self.current_form['inputs']
            })
            self.current_form = None
