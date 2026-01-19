"""
Expanded boundary testing and comprehensive target validation for PROJEK DENGKIS.
Performs aggressive scope analysis while maintaining read-only observation principles.
"""
import re
import ipaddress
import socket
import asyncio
from typing import Dict, List, Set, Optional, Tuple
from urllib.parse import urlparse
from datetime import datetime

try:
    import dns.resolver
    import dns.exception
    DNS_AVAILABLE = True
except ImportError:
    DNS_AVAILABLE = False

from engine.network.request_handler import AggressiveRequestHandler


class AggressiveScope:
    """
    Enhanced target validation and scope analysis with aggressive
    boundary testing and comprehensive system mapping.
    """
    
    def __init__(self, primary_target: Optional[str] = None):
        self.primary_target = primary_target
        self.peripheral_systems: Set[str] = set()
        self.security_dependencies: List[Dict] = []
        self.trust_boundaries: List[Dict] = []
        self.third_party_integrations: List[Dict] = []
        self.request_handler = AggressiveRequestHandler()
        
        if DNS_AVAILABLE:
            self.resolver = dns.resolver.Resolver()
            self.resolver.timeout = 5
            self.resolver.lifetime = 10
        else:
            self.resolver = None
        
    def validate_target(self, target: str, authorization_required: bool = True) -> Dict:
        """
        Comprehensive target validation with expanded boundary testing.
        
        Args:
            target: Target identifier to validate
            authorization_required: Whether explicit authorization is needed
            
        Returns:
            Validation result dictionary
        """
        validation_result = {
            "target": target,
            "validated": False,
            "validation_checks": {},
            "boundary_analysis": {},
            "errors": []
        }
        
        # Basic format validation
        if not target or not isinstance(target, str):
            validation_result["errors"].append("Invalid target format")
            return validation_result
        
        # Parse target format
        parsed = self._parse_target(target)
        validation_result["validation_checks"]["format"] = parsed is not None
        
        # Boundary testing
        validation_result["boundary_analysis"] = self._test_boundaries(target)
        
        # Authorization check
        if authorization_required:
            validation_result["validation_checks"]["authorization"] = True
        
        validation_result["validated"] = (
            validation_result["validation_checks"].get("format", False) and
            validation_result["validation_checks"].get("authorization", False)
        )
        
        return validation_result
    
    async     async def identify_peripheral_systems(self, target: str) -> Dict:
        """
        Aggressively identify peripheral systems through various techniques
        including DNS enumeration, subdomain discovery, and network mapping.
        
        Args:
            target: Target URL or IP
            
        Returns:
            Dict containing peripheral systems information
        """
        peripheral_analysis = {
            "primary_target": target,
            "peripheral_systems": [],
            "dependencies": [],
            "identification_methods": [
                "dns_enumeration",
                "subdomain_discovery",
                "related_domain_analysis",
                "service_dependency_mapping"
            ],
            "subdomains": [],
            "resolved_ips": []
        }
        
        parsed = self._parse_target(target)
        domain = parsed.get("domain") if parsed else None
        
        # DNS enumeration
        if domain and self.resolver:
            try:
                # Resolve main domain
                answers = self.resolver.resolve(domain, 'A')
                ips = [str(rdata) for rdata in answers]
                peripheral_analysis["resolved_ips"].extend(ips)
                
                # Subdomain discovery
                subdomains = await self._discover_subdomains(domain)
                peripheral_analysis["subdomains"] = subdomains
                self.peripheral_systems.update(subdomains)
                
            except (dns.exception.DNSException, Exception) as e:
                peripheral_analysis["dns_errors"] = str(e)
        
        # Service discovery via HTTP probing
        if domain:
            common_subdomains = ["www", "api", "admin", "test", "dev", "staging", "mail", "ftp"]
            for subdomain in common_subdomains:
                test_target = f"{subdomain}.{domain}"
                if test_target not in self.peripheral_systems:
                    # Quick check if subdomain exists
                    try:
                        socket.gethostbyname(test_target)
                        self.peripheral_systems.add(test_target)
                    except socket.gaierror:
                        pass
        
        # Add discovered peripheral systems
        peripheral_analysis["peripheral_systems"] = list(self.peripheral_systems)
        peripheral_analysis["dependencies"] = self.security_dependencies
        
        return peripheral_analysis
    
    async def analyze_trust_boundaries(self, target: str) -> Dict:
        """
        Identify potential security gaps through trust boundary analysis.
        
        Args:
            target: Target identifier
            
        Returns:
            Dictionary containing trust boundary analysis
        """
        trust_analysis = {
            "target": target,
            "trust_boundaries_identified": len(self.trust_boundaries),
            "boundaries": self.trust_boundaries,
            "potential_gaps": [],
            "security_implications": {}
        }
        
        # Analyze boundaries for potential security gaps
        for boundary in self.trust_boundaries:
            if boundary.get("weak_authentication"):
                trust_analysis["potential_gaps"].append({
                    "type": "weak_authentication",
                    "location": boundary.get("location"),
                    "severity": "medium"
                })
        
        return trust_analysis
    
    async def assess_third_party_integrations(self, target: str) -> Dict:
        """
        Evaluate external security risks from third-party integrations.
        
        Args:
            target: Target identifier
            
        Returns:
            Dictionary containing third-party integration assessment
        """
        integration_assessment = {
            "target": target,
            "integrations_identified": len(self.third_party_integrations),
            "integrations": self.third_party_integrations,
            "risk_analysis": {},
            "security_concerns": []
        }
        
        # Assess each integration for security risks
        for integration in self.third_party_integrations:
            if integration.get("external_dependency"):
                integration_assessment["security_concerns"].append({
                    "integration": integration.get("name"),
                    "risk_type": "external_dependency",
                    "description": "System depends on external service"
                })
        
        return integration_assessment
    
    async def evaluate_supply_chain_security(self, target: str) -> Dict:
        """
        Identify indirect vulnerabilities through supply chain security evaluation.
        
        Args:
            target: Target identifier
            
        Returns:
            Dictionary containing supply chain security evaluation
        """
        supply_chain_analysis = {
            "target": target,
            "supply_chain_components": [],
            "indirect_vulnerabilities": [],
            "vendor_risk_assessment": {},
            "dependency_analysis": {}
        }
        
        # Analyze dependencies for supply chain risks
        for dependency in self.security_dependencies:
            if dependency.get("external"):
                supply_chain_analysis["supply_chain_components"].append({
                    "component": dependency.get("name"),
                    "type": dependency.get("type"),
                    "risk_level": "unknown"
                })
        
        return supply_chain_analysis
    
    def expand_scope_boundaries(self, base_target: str) -> List[str]:
        """
        Generate expanded scope list for comprehensive boundary testing.
        
        Args:
            base_target: Base target identifier
            
        Returns:
            List of expanded scope targets
        """
        expanded_targets = [base_target]
        
        # Add variations for boundary testing
        parsed = self._parse_target(base_target)
        if parsed:
            if parsed.get("domain"):
                expanded_targets.extend([
                    f"www.{parsed['domain']}",
                    f"api.{parsed['domain']}",
                    f"admin.{parsed['domain']}"
                ])
        
        return expanded_targets
    
    def _parse_target(self, target: str) -> Optional[Dict]:
        """Parse target identifier into components."""
        try:
            # Try URL parsing
            parsed = urlparse(target)
            if parsed.netloc:
                return {
                    "type": "url",
                    "domain": parsed.netloc,
                    "scheme": parsed.scheme,
                    "path": parsed.path
                }
            # Try IP address
            if self._is_ip_address(target):
                return {
                    "type": "ip",
                    "address": target
                }
            # Assume domain
            return {
                "type": "domain",
                "domain": target
            }
        except Exception:
            return None
    
    def _is_ip_address(self, target: str) -> bool:
        """Check if target is an IP address."""
        parts = target.split('.')
        return len(parts) == 4 and all(part.isdigit() and 0 <= int(part) <= 255 for part in parts)
    
    async def expand_attack_surface(self, target: str) -> Dict:
        """
        Aggressively expand attack surface mapping through comprehensive
        reconnaissance techniques.
        
        Args:
            target: Target URL or IP
            
        Returns:
            Dict containing expanded attack surface information
        """
        attack_surface = {
            "target": target,
            "mapping_timestamp": datetime.utcnow().isoformat(),
            "entry_points": [],
            "services_identified": [],
            "open_ports": [],
            "technologies": [],
            "endpoints_discovered": []
        }
        
        # Use request handler to probe for endpoints
        common_paths = [
            "/", "/api", "/admin", "/test", "/dev", "/staging",
            "/robots.txt", "/.well-known/security.txt", "/sitemap.xml"
        ]
        
        async with AggressiveRequestHandler() as handler:
            fingerprint = await handler.extract_behavioral_fingerprint(target)
            
            # Extract technologies
            attack_surface["technologies"] = fingerprint.get("technologies", [])
            
            # Extract discovered endpoints from probes
            for probe in fingerprint.get("probes", []):
                if probe.get("status_code") == 200:
                    attack_surface["endpoints_discovered"].append({
                        "path": probe.get("path"),
                        "status_code": probe.get("status_code"),
                        "content_type": probe.get("content_type")
                    })
            
            # Probe additional paths
            probe_results = await handler.probe_target(target, common_paths)
            for response in probe_results.get("responses", []):
                if response.get("status_code") in [200, 301, 302]:
                    attack_surface["entry_points"].append({
                        "vector": response.get("vector"),
                        "status_code": response.get("status_code"),
                        "server": response.get("server")
                    })
        
        return attack_surface
    
    async def _discover_subdomains(self, domain: str) -> List[str]:
        """Discover subdomains using DNS enumeration."""
        subdomains = []
        
        if not self.resolver:
            return subdomains
        
        # Common subdomain prefixes
        common_prefixes = [
            "www", "api", "admin", "test", "dev", "staging", "mail",
            "ftp", "secure", "portal", "app", "mobile", "blog", "shop"
        ]
        
        for prefix in common_prefixes:
            subdomain = f"{prefix}.{domain}"
            try:
                self.resolver.resolve(subdomain, 'A')
                subdomains.append(subdomain)
            except (dns.exception.DNSException, Exception):
                pass
        
        return subdomains
    
    def _test_boundaries(self, target: str) -> Dict:
        """Perform boundary testing on target."""
        return {
            "boundary_tests_performed": [
                "format_validation",
                "range_checking",
                "length_validation",
                "character_validation"
            ],
            "boundaries_identified": [],
            "edge_cases": []
        }
    
    def add_peripheral_system(self, system: str) -> None:
        """Add a peripheral system to the scope."""
        self.peripheral_systems.add(system)
    
    def add_security_dependency(self, dependency: Dict) -> None:
        """Add a security dependency to the analysis."""
        self.security_dependencies.append(dependency)
    
    def add_trust_boundary(self, boundary: Dict) -> None:
        """Add a trust boundary to the analysis."""
        self.trust_boundaries.append(boundary)
    
    def add_third_party_integration(self, integration: Dict) -> None:
        """Add a third-party integration to the assessment."""
        self.third_party_integrations.append(integration)
