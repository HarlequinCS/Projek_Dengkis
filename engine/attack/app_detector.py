"""
KNOWN VULNERABLE APP DETECTOR - Detects Juice Shop, DVWA, WebGoat, etc.
When detected, loads tailored payloads and endpoints for maximum exploitation.
"""
import re
from typing import Dict, List, Optional
import httpx

from engine.logging.logger import get_logger


class KnownAppDetector:
    """
    Detects known vulnerable applications and provides tailored attack vectors.
    """
    
    def __init__(self):
        self.logger = get_logger()
        self.detected_apps: List[Dict] = []
        
        # App signatures
        self.app_signatures = {
            "juice_shop": {
                "name": "OWASP Juice Shop",
                "indicators": [
                    r"juice.*shop",
                    r"OWASP.*Juice.*Shop",
                    r"application.*version.*\d+\.\d+\.\d+",
                ],
                "endpoints": [
                    "/api/products",
                    "/api/users",
                    "/rest/user/login",
                    "/api/BasketItems",
                    "/api/Feedbacks",
                    "/api/Challenges",
                ],
                "payloads": {
                    "sql_injection": [
                        {"payload": "' OR 1=1--", "endpoint": "/rest/user/login", "parameter": "email"},
                        {"payload": "admin@juice-sh.op'--", "endpoint": "/rest/user/login", "parameter": "email"},
                    ],
                    "xss": [
                        {"payload": "<script>alert('XSS')</script>", "endpoint": "/api/Feedbacks", "parameter": "comment"},
                    ]
                }
            },
            "dvwa": {
                "name": "Damn Vulnerable Web Application",
                "indicators": [
                    r"DVWA",
                    r"Damn.*Vulnerable.*Web.*Application",
                    r"login\.php",
                ],
                "endpoints": [
                    "/login.php",
                    "/vulnerabilities/sqli/",
                    "/vulnerabilities/xss_r/",
                    "/vulnerabilities/xss_s/",
                    "/vulnerabilities/exec/",
                    "/vulnerabilities/upload/",
                ],
                "payloads": {
                    "sql_injection": [
                        {"payload": "' OR '1'='1", "endpoint": "/vulnerabilities/sqli/", "parameter": "id"},
                    ],
                    "xss": [
                        {"payload": "<script>alert(1)</script>", "endpoint": "/vulnerabilities/xss_r/", "parameter": "name"},
                    ],
                    "command_injection": [
                        {"payload": "; ls -la", "endpoint": "/vulnerabilities/exec/", "parameter": "ip"},
                    ]
                }
            },
            "webgoat": {
                "name": "OWASP WebGoat",
                "indicators": [
                    r"WebGoat",
                    r"webgoat",
                    r"Welcome to WebGoat",
                ],
                "endpoints": [
                    "/WebGoat/login",
                    "/WebGoat/attack",
                ],
                "payloads": {}
            },
            "bwapp": {
                "name": "bWAPP",
                "indicators": [
                    r"bWAPP",
                    r"bee.*web.*application",
                ],
                "endpoints": [
                    "/login.php",
                    "/sqli_1.php",
                    "/xss_stored_1.php",
                ],
                "payloads": {}
            }
        }
    
    async def detect(self, target: str, response: Optional[httpx.Response] = None) -> List[Dict]:
        """
        Detect known vulnerable applications.
        
        Args:
            target: Target URL
            response: Optional response object to analyze
            
        Returns:
            List of detected applications
        """
        detected = []
        
        # If no response provided, fetch one
        if not response:
            try:
                async with httpx.AsyncClient(verify=False, timeout=10.0) as client:
                    response = await client.get(target)
            except Exception as e:
                self.logger.debug(f"Failed to fetch {target} for app detection: {e}")
                return detected
        
        # Analyze response
        body_lower = (response.text.lower() if response.text else "")
        headers_lower = str(response.headers).lower()
        combined_text = f"{body_lower} {headers_lower}"
        
        # Check each app signature
        for app_id, signature in self.app_signatures.items():
            for indicator in signature["indicators"]:
                if re.search(indicator, combined_text, re.IGNORECASE):
                    detected.append({
                        "app_id": app_id,
                        "name": signature["name"],
                        "confidence": "high",
                        "indicators_found": [indicator],
                        "endpoints": signature.get("endpoints", []),
                        "payloads": signature.get("payloads", {})
                    })
                    self.logger.warning(f"[ATTACK] DETECTED VULNERABLE APP: {signature['name']} at {target}")
                    break
        
        self.detected_apps.extend(detected)
        return detected
    
    def get_tailored_endpoints(self, app_id: str) -> List[str]:
        """Get tailored endpoints for a detected app."""
        signature = self.app_signatures.get(app_id, {})
        return signature.get("endpoints", [])
    
    def get_tailored_payloads(self, app_id: str) -> Dict[str, List[Dict]]:
        """Get tailored payloads for a detected app."""
        signature = self.app_signatures.get(app_id, {})
        return signature.get("payloads", {})
    
    def should_never_return_zero(self, target: str) -> bool:
        """
        Check if target is a known vulnerable app.
        If so, we should NEVER return 0 findings silently.
        """
        return len(self.detected_apps) > 0
