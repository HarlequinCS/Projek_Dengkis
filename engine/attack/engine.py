"""
ATTACK ENGINE - Main attack orchestration engine.
Coordinates crawling, payload injection, and vulnerability detection.

⚠️ WARNING: This is dangerous software for AUTHORIZED security testing only.
Unauthorized use is illegal. See LICENSE for restrictions.
"""
import asyncio
from typing import Dict, List, Optional, Callable
import httpx

from engine.attack.crawler import AggressiveCrawler
from engine.attack.injector import PayloadInjector
from engine.attack.app_detector import KnownAppDetector
from engine.attack.logic_breaker import LogicBreaker
from engine.attack.red_team_architect import RedTeamArchitect
from engine.attack.attacker_mindset import AttackerMindset
from engine.logging.logger import get_logger


class AttackEngine:
    """
    Main attack engine that orchestrates:
    1. Aggressive crawling
    2. Payload injection
    3. Response analysis
    4. Finding generation
    """
    
    def __init__(self, target: str, attack_mode: str = "aggressive", session: Optional[httpx.AsyncClient] = None, operation_mode: str = "attack", progress_callback: Optional[Callable] = None):
        """
        Initialize attack engine.
        
        Args:
            target: Target URL
            attack_mode: passive, active, or aggressive
            session: HTTP session
            operation_mode: "attack" for vulnerability hunting, "flag_hunt" for CTF flag hunting
            progress_callback: Optional callback for real-time progress updates
        """
        # Validate inputs
        if not target or not isinstance(target, str):
            raise ValueError("Target must be a non-empty string")
        if attack_mode not in ["passive", "active", "aggressive"]:
            raise ValueError(f"Invalid attack_mode: {attack_mode}. Must be 'passive', 'active', or 'aggressive'")
        if operation_mode not in ["attack", "flag_hunt"]:
            raise ValueError(f"Invalid operation_mode: {operation_mode}. Must be 'attack' or 'flag_hunt'")
        self.target = target
        self.attack_mode = attack_mode
        self.operation_mode = operation_mode  # "attack" or "flag_hunt"
        self.session = session
        self.progress_callback = progress_callback
        self.logger = get_logger()
        
        self.crawler = AggressiveCrawler(target, session)
        self.injector = PayloadInjector(session, attack_mode)
        self.app_detector = KnownAppDetector()
        self.logic_breaker = LogicBreaker(session)
        self.red_team_architect = RedTeamArchitect(session)
        self.attacker_mindset = AttackerMindset()
        
        # Set progress callback for real-time updates
        if progress_callback:
            self.injector.set_progress_callback(progress_callback)
        
        # Flag hunt engine for CTF mode
        if operation_mode == "flag_hunt":
            from engine.attack.flag_hunt_engine import FlagHuntEngine
            self.flag_hunt_engine = FlagHuntEngine(target, session)
        
        self.findings: List[Dict] = []
        self.crawl_results: Optional[Dict] = None
    
    async def attack(self) -> Dict:
        """
        Execute full attack cycle or flag hunt based on operation_mode.
        
        Returns:
            Dictionary containing attack results and findings
        """
        if self.operation_mode == "flag_hunt":
            return await self._flag_hunt()
        
        return await self._vulnerability_attack()
    
    async def _flag_hunt(self) -> Dict:
        """Execute aggressive flag hunting."""
        self.logger.info(f"[FLAG HUNT] Starting flag hunt on {self.target}")
        flag_results = await self.flag_hunt_engine.hunt_flags()
        
        return {
            "target": self.target,
            "operation_mode": "flag_hunt",
            "attack_mode": self.attack_mode,
            "flags_found": flag_results.get("flags", []),
            "total_flags": flag_results.get("total_flags", 0),
            "web_flags": flag_results.get("web_flags", {}),
            "network_flags": flag_results.get("network_flags", {}),
            "crawl_flags": flag_results.get("crawl_flags", {}),
            "header_flags": flag_results.get("header_flags", {}),
            "source_flags": flag_results.get("source_flags", {}),
            "all_flags": flag_results.get("all_flags", {}),
            "status": "completed"
        }
    
    async def _vulnerability_attack(self) -> Dict:
        """
        Execute full vulnerability attack cycle:
        1. Detect known vulnerable apps
        2. Aggressively crawl attack surface
        3. Inject payloads into all parameters
        4. Analyze responses for vulnerabilities
        
        Returns:
            Dictionary containing attack results and findings
        """
        self.logger.info(f"[ATTACK] Starting attack on {self.target} (mode: {self.attack_mode})")
        
        # Step 1: Detect known vulnerable apps
        detected_apps = await self.app_detector.detect(self.target)
        if detected_apps:
            self.logger.warning(f"[ATTACK] Detected {len(detected_apps)} known vulnerable app(s)")
            # Add tailored endpoints to crawler
            for app in detected_apps:
                tailored_endpoints = self.app_detector.get_tailored_endpoints(app["app_id"])
                for endpoint in tailored_endpoints:
                    full_url = f"{self.target.rstrip('/')}{endpoint}"
                    self.crawler.endpoints.add(full_url)
        
        # Step 2: Aggressive crawling
        self.logger.info("[ATTACK] Phase 1: Aggressive crawling...")
        self.crawl_results = await self.crawler.crawl(max_depth=3)
        
        endpoints = self.crawl_results.get("endpoints_discovered", [])
        parameters = self.crawl_results.get("parameters", {})
        
        self.logger.info(f"[ATTACK] Discovered {len(endpoints)} endpoints and {sum(len(p) for p in parameters.values())} parameters")
        
        # Step 3: Payload injection
        self.logger.info("[ATTACK] Phase 2: Payload injection...")
        injection_findings = await self.injector.inject_all(endpoints, parameters)
        self.findings.extend(injection_findings)
        
        # Step 4: Test tailored payloads for detected apps
        if detected_apps:
            self.logger.info("[ATTACK] Phase 3: Testing tailored payloads for detected apps...")
            for app in detected_apps:
                tailored_payloads = self.app_detector.get_tailored_payloads(app["app_id"])
                await self._test_tailored_payloads(tailored_payloads)
        
        # Step 5: Test business logic vulnerabilities
        self.logger.info("[ATTACK] Phase 4: Business logic testing...")
        logic_findings = await self._test_business_logic(endpoints)
        self.findings.extend(logic_findings)
        
        # Step 6: Generate attacker insights
        self.logger.info("[ATTACK] Phase 5: Generating attacker insights...")
        intelligence_report = self.attacker_mindset.generate_intelligence_report(self.findings)
        
        # Step 7: Generate attack report with exploitation results
        results = {
            "target": self.target,
            "attack_mode": self.attack_mode,
            "operation_mode": self.operation_mode,
            "detected_apps": detected_apps,
            "crawl_results": self.crawl_results,
            "findings": self.findings,
            "total_findings": len(self.findings),
            "high_confidence": len([f for f in self.findings if f.get("confidence") == "high"]),
            "medium_confidence": len([f for f in self.findings if f.get("confidence") == "medium"]),
            "low_confidence": len([f for f in self.findings if f.get("confidence") == "low"]),
            "exfiltrated_data": self.injector.flag_hunter.get_exfiltrated_data(),
            "flags_found": self.injector.flag_hunter.get_flags_found(),
            "logic_findings": logic_findings,
            "attacker_intelligence": intelligence_report,
            "network_map": self.red_team_architect.get_network_map(),
            "credentials_found": self.red_team_architect.get_credentials(),
            # Exploitation results
            "exploitation_results": self.injector.exploiter.get_exploitation_results(),
            "failed_exploits": self.injector.exploiter.get_failed_exploits(),
            "successful_exploits": len([r for r in self.injector.exploiter.get_exploitation_results() if r.get("success")]),
            "total_exploitation_attempts": len(self.injector.exploiter.get_exploitation_results()) + len(self.injector.exploiter.get_failed_exploits()),
        }
        
        # NEVER return 0 findings silently for known vulnerable apps
        if detected_apps and len(self.findings) == 0:
            self.logger.warning("[ATTACK] WARNING: Known vulnerable app detected but 0 findings!")
            self.logger.warning("[ATTACK] This should NOT happen. Manual testing recommended.")
            results["warning"] = "Known vulnerable app detected but no automated findings. Manual testing required."
        
        self.logger.info(f"[ATTACK] Attack complete. Found {len(self.findings)} potential vulnerabilities")
        return results
    
    async def _test_tailored_payloads(self, tailored_payloads: Dict[str, List[Dict]]):
        """Test tailored payloads for detected apps."""
        for category, payloads in tailored_payloads.items():
            for payload_data in payloads:
                endpoint = payload_data.get("endpoint", "")
                parameter = payload_data.get("parameter", "")
                payload = payload_data.get("payload", "")
                
                if not endpoint or not parameter:
                    continue
                
                full_url = f"{self.target.rstrip('/')}{endpoint}"
                
                try:
                    # Test GET
                    finding = await self.injector._inject_get_parameter(
                        full_url, parameter, payload, {"category": category, "type": "tailored", "confidence": "high"}
                    )
                    if finding and finding.get("vulnerable"):
                        self.findings.append(finding)
                    
                    # Test POST
                    finding = await self.injector._inject_post_parameter(
                        full_url, parameter, payload, {"category": category, "type": "tailored", "confidence": "high"}
                    )
                    if finding and finding.get("vulnerable"):
                        self.findings.append(finding)
                except Exception as e:
                    self.logger.debug(f"Tailored payload test failed: {e}")
    
    async def _test_business_logic(self, endpoints: List[str]) -> List[Dict]:
        """Test business logic vulnerabilities."""
        logic_findings = []
        
        # Test IDOR on API endpoints
        api_endpoints = [e for e in endpoints if '/api/' in e or '/user/' in e or '/id/' in e]
        for endpoint in api_endpoints[:10]:  # Limit to first 10
            # Try to discover IDOR
            # Convert endpoint to format string if it contains numeric IDs
            import re
            # Check if endpoint has numeric ID pattern
            idor_pattern = re.search(r'/(\d+)(?:/|$|\?|$)', endpoint)
            if idor_pattern:
                # Replace numeric ID with {id} placeholder
                base_url = endpoint.replace(idor_pattern.group(0), '/{id}' + endpoint[idor_pattern.end():])
                idor_findings = await self.logic_breaker.discover_idor(base_url)
                logic_findings.extend(idor_findings)
            elif '{id}' in endpoint:
                # Already has placeholder
                idor_findings = await self.logic_breaker.discover_idor(endpoint)
                logic_findings.extend(idor_findings)
        
        # Test integer overflow on endpoints with numeric parameters
        for endpoint in endpoints[:20]:  # Limit testing
            # Look for price/quantity parameters
            if any(keyword in endpoint.lower() for keyword in ['price', 'quantity', 'amount', 'count']):
                # Test integer overflow
                overflow_findings = await self.logic_breaker.test_integer_overflow(
                    endpoint, 'price' if 'price' in endpoint.lower() else 'quantity'
                )
                logic_findings.extend(overflow_findings)
        
        return logic_findings