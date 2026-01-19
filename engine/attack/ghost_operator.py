"""
GHOST OPERATOR - WAF/EDR Evasion Module
Modifies traffic when firewalls or blocks are detected.
"""
import random
import time
import urllib.parse
from typing import Dict, List, Optional
import httpx

from engine.logging.logger import get_logger


class GhostOperator:
    """
    Stealth controller that evades WAF/EDR when blocks are detected.
    System Prompt: "You are the Dengkis Stealth Controller."
    """
    
    def __init__(self, session: Optional[httpx.AsyncClient] = None):
        self.session = session
        self.logger = get_logger()
        self.evasion_active = False
        self.blocked_count = 0
        
        # Legitimate user agents (50+)
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0",
            "Mozilla/5.0 (X11; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
            "Mozilla/5.0 (iPad; CPU OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
            "Mozilla/5.0 (Linux; Android 13; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
            "Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
        ]
        # Add more variations
        for i in range(40):
            self.user_agents.append(f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/{120+i}.0.0.0 Safari/537.36")
    
    def detect_block(self, response: httpx.Response) -> bool:
        """
        Monitor response codes for blocks.
        System Prompt: "Monitor response codes for 403 Forbidden or 406 Not Acceptable"
        
        Args:
            response: HTTP response to check
            
        Returns:
            True if block detected
        """
        block_codes = [403, 406, 429, 503]
        if response.status_code in block_codes:
            self.blocked_count += 1
            if self.blocked_count >= 2:
                self.evasion_active = True
                self.logger.warning(f"[GHOST OPERATOR] Block detected ({response.status_code}). Activating evasion.")
            return True
        return False
    
    def encode_payload(self, payload: str, method: str = "double_url") -> str:
        """
        Encode payload for evasion.
        System Prompt: "If blocked, switch from standard payloads to Double URL Encoding or Null Byte Injection"
        
        Args:
            payload: Original payload
            method: Encoding method (double_url, null_byte, unicode)
            
        Returns:
            Encoded payload
        """
        if method == "double_url":
            # Double URL encoding
            return urllib.parse.quote(urllib.parse.quote(payload, safe=''), safe='')
        elif method == "null_byte":
            # Null byte injection
            return payload.replace("'", "%00'").replace('"', '%00"')
        elif method == "unicode":
            # Unicode encoding
            return ''.join([f'%u{ord(c):04x}' for c in payload])
        else:
            return payload
    
    def fragment_payload(self, payload: str, num_fragments: int = 3) -> Dict[str, str]:
        """
        Split payload into multiple HTTP headers.
        System Prompt: "Split payloads into multiple smaller HTTP headers if the WAF is inspecting the body"
        
        Args:
            payload: Original payload
            num_fragments: Number of fragments to create
            
        Returns:
            Dictionary of header fragments
        """
        fragment_size = len(payload) // num_fragments
        fragments = {}
        
        for i in range(num_fragments):
            start = i * fragment_size
            end = start + fragment_size if i < num_fragments - 1 else len(payload)
            fragment = payload[start:end]
            fragments[f'X-Fragment-{i}'] = fragment
        
        return fragments
    
    def get_random_user_agent(self) -> str:
        """
        Rotate through legitimate user agents.
        System Prompt: "Rotate through a list of 50+ legitimate mobile and desktop browser strings"
        
        Returns:
            Random user agent
        """
        return random.choice(self.user_agents)
    
    async def jitter_delay(self):
        """
        Introduce random delay to break pattern recognition.
        System Prompt: "Introduce a random 'jitter' delay between 200ms and 1500ms"
        
        Returns:
            None
        """
        delay = random.uniform(0.2, 1.5)
        await asyncio.sleep(delay)
    
    async def send_evasive_request(
        self,
        method: str,
        url: str,
        payload: Optional[str] = None,
        params: Optional[Dict] = None,
        data: Optional[Dict] = None,
        headers: Optional[Dict] = None
    ) -> httpx.Response:
        """
        Send request with evasion techniques applied.
        
        Args:
            method: HTTP method
            url: Target URL
            payload: Optional payload string
            params: Query parameters
            data: POST data
            headers: Custom headers
            
        Returns:
            HTTP response
        """
        # Apply jitter delay
        await self.jitter_delay()
        
        # Prepare headers
        request_headers = headers or {}
        request_headers['User-Agent'] = self.get_random_user_agent()
        
        # Apply evasion if active
        if self.evasion_active:
            if payload:
                # Try double URL encoding first
                payload = self.encode_payload(payload, "double_url")
            
            # Fragment payload into headers if needed
            if payload and len(payload) > 50:
                fragments = self.fragment_payload(payload)
                request_headers.update(fragments)
        
        # Send request
        if not self.session:
            async with httpx.AsyncClient(verify=False, timeout=15.0) as client:
                if method.upper() == 'GET':
                    response = await client.get(url, params=params, headers=request_headers)
                else:
                    response = await client.post(url, data=data, headers=request_headers)
        else:
            if method.upper() == 'GET':
                response = await self.session.get(url, params=params, headers=request_headers)
            else:
                response = await self.session.post(url, data=data, headers=request_headers)
        
        # Check for blocks
        self.detect_block(response)
        
        return response
