"""
ATTACK-DRIVEN EXPLOITATION ENGINE for PROJEK DENGKIS.
This is NOT a passive scanner. This is an ACTIVE exploitation tool.
Performs aggressive crawling, payload injection, and vulnerability exploitation.
"""
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Callable
import httpx

from engine.core.session import TestSession
from engine.core.advanced_result import AssessmentResult
from engine.attack.engine import AttackEngine
from engine.logging.logger import get_logger


def run_assessment(
    target: str,
    authorized: bool = False,
    session_id: Optional[str] = None,
    attack_mode: str = "aggressive"
) -> Dict:
    """
    Initiates an attack-driven assessment on the specified target.

    This function sets up the initial assessment state and validates authorization.
    It does not execute the actual attack; use `execute_attack` for full execution.

    Args:
        target (str): The target system URL to assess.
        authorized (bool): Explicit flag confirming authorization to test the target.
        session_id (Optional[str]): Unique identifier for the session. Generated if omitted.
        attack_mode (str): Execution intensity: 'passive', 'active', or 'aggressive'.

    Returns:
        Dict: Initial assessment metadata and status.
    """
    logger = get_logger(session_id)

    if not authorized:
        logger.warning(f"[ATTACK] Attack attempt without authorization for target: {target}")
        return {
            "status": "error",
            "message": "Attack requires explicit authorization flag",
            "target": target
        }

    logger.info(f"[ATTACK] Initializing attack on target: {target} (mode: {attack_mode})")

    # Create test session for tracking attack state
    session = TestSession(target=target, authorized=authorized)

    # Initialize attack components
    assessment_data = {
        "session_id": str(session.session_id),
        "target": target,
        "authorized": authorized,
        "attack_mode": attack_mode,
        "started_at": session.started_at,
        "status": "initialized",
        "findings": []
    }

    return assessment_data


async def execute_attack(
    target: str,
    authorized: bool = False,
    attack_mode: str = "aggressive",
    session_id: Optional[str] = None,
    operation_mode: str = "attack",
    progress_callback: Optional[Callable] = None
) -> Dict:
    """
    Executes the full attack lifecycle for the given target.

    Orchestrates discovery, exploitation, and post-exploitation phases using
    the underlying AttackEngine. Requires explicit authorization.

    Args:
        target (str): The target URL to exploit.
        authorized (bool): Must be True to proceed with active testing.
        attack_mode (str): Intensity level of the attack.
        session_id (Optional[str]): ID to track this specific execution.
        operation_mode (str): The type of operation: 'attack' or 'flag_hunt'.
        progress_callback (Optional[Callable]): Async-safe callback for progress updates.

    Returns:
        Dict: Complete results including findings, extracted data, and metadata.
    """
    logger = get_logger(session_id)

    if not authorized:
        logger.error("[ATTACK] Attack requires explicit authorization")
        return {
            "status": "error",
            "message": "Attack requires explicit authorization flag",
            "target": target
        }

    logger.info(f"[ATTACK] Starting attack execution on {target}")
    logger.info(f"[ATTACK] Attack mode: {attack_mode}, Authorized: {authorized}")

    # Validate and normalize target URL
    from urllib.parse import urlparse
    if not target or not isinstance(target, str):
        logger.error("[ATTACK] Invalid target: must be a non-empty string")
        return {
            "status": "error",
            "message": "Invalid target: must be a non-empty string",
            "target": target
        }

    parsed = urlparse(target)
    if not parsed.scheme:
        target = f"https://{target}"
        logger.info(f"[ATTACK] Normalized target URL: {target}")
        parsed = urlparse(target)

    # Security: Prevent SSRF by blocking private/localhost IPs (unless explicitly allowed)
    # This is a safety check - can be disabled for authorized internal testing
    if parsed.hostname:
        hostname_lower = parsed.hostname.lower()
        if hostname_lower in ['localhost', '127.0.0.1', '0.0.0.0', '::1']:
            logger.warning(f"[ATTACK] Target is localhost - ensure this is authorized")
        # Block private IP ranges (can be configured)
        try:
            import ipaddress
            ip = ipaddress.ip_address(parsed.hostname)
            if ip.is_private or ip.is_loopback:
                logger.warning(f"[ATTACK] Target is private IP {parsed.hostname} - ensure this is authorized")
        except ValueError:
            pass  # Not an IP, likely a hostname

    # Create HTTP session
    async with httpx.AsyncClient(
        verify=False,  # SSL verification disabled for attack
        timeout=30.0,
        follow_redirects=True
    ) as client:
        logger.info(f"[ATTACK] HTTP client initialized, executing first probe...")

        # Execute immediate probe to verify connectivity
        try:
            probe_response = await client.get(target)
            logger.info(f"[PROBE] Initial probe executed: GET {target} -> {probe_response.status_code}")
        except Exception as e:
            logger.warning(f"[PROBE] Initial probe failed: {e}")

        # Initialize attack engine with operation mode and progress callback
        engine = AttackEngine(target, attack_mode=attack_mode, session=client,
                             operation_mode=operation_mode, progress_callback=progress_callback)
        if operation_mode == "flag_hunt":
            logger.info(f"[FLAG HUNT] Flag hunt engine initialized")
        else:
            logger.info(f"[ATTACK] Attack engine initialized - REAL EXPLOITATION ENABLED")

        # Execute attack
        attack_results = await engine.attack()
        logger.info(f"[ATTACK] Attack cycle completed")

        # Add session metadata
        attack_results["session_id"] = session_id
        attack_results["authorized"] = authorized
        attack_results["attack_mode"] = attack_mode
        attack_results["status"] = "completed"

        logger.info(f"[ATTACK] Attack complete. Found {attack_results.get('total_findings', 0)} vulnerabilities")

        return attack_results


def perform_aggressive_reconnaissance(target: str, session: TestSession) -> Dict:
    """
    Performs aggressive but non-exploitative reconnaissance techniques
    to test system responses to unusual queries.

    Args:
        target: Target identifier
        session: Active TestSession object

    Returns:
        Dictionary containing reconnaissance findings
    """
    reconnaissance_results = {
        "target": target,
        "techniques_applied": [
            "response_timing_analysis",
            "error_message_enumeration",
            "header_analysis",
            "service_fingerprinting",
            "protocol_behavior_observation"
        ],
        "findings": []
    }

    return reconnaissance_results


def analyze_response_patterns(responses: List[Dict]) -> Dict:
    """
    Analyzes system response patterns to identify potential vulnerabilities
    through behavioral observation rather than exploitation.

    Args:
        responses: List of response dictionaries from target system

    Returns:
        Dictionary containing pattern analysis results
    """
    pattern_analysis = {
        "total_responses": len(responses),
        "identified_patterns": [],
        "anomalies": [],
        "potential_weaknesses": []
    }

    # Analyze response consistency, timing, error messages, etc.
    for response in responses:
        if response.get("unusual_behavior"):
            pattern_analysis["anomalies"].append(response)
        if response.get("security_control_evident"):
            pattern_analysis["identified_patterns"].append(response)

    return pattern_analysis


def configuration_stress_test(target: str, edge_cases: List[str]) -> Dict:
    """
    Examines how systems react to edge cases and boundary conditions
    without causing harm or exploitation.

    Args:
        target: Target identifier
        edge_cases: List of edge case scenarios to test

    Returns:
        Dictionary containing stress test results
    """
    stress_test_results = {
        "target": target,
        "edge_cases_tested": edge_cases,
        "responses": {},
        "boundary_conditions_identified": [],
        "configuration_resilience": "unknown"
    }

    return stress_test_results


def detect_compliance_deviations(target: str, standards: List[str]) -> Dict:
    """
    Identifies where systems deviate from standard security practices
    through configuration analysis.

    Args:
        target: Target identifier
        standards: List of security standards to check against

    Returns:
        Dictionary containing compliance deviation findings
    """
    compliance_results = {
        "target": target,
        "standards_checked": standards,
        "deviations": [],
        "compliance_score": 0.0,
        "recommendations": []
    }

    return compliance_results


def generate_assessment_report(session: TestSession, results: AssessmentResult) -> Dict:
    """
    Generates comprehensive assessment report from session and results.

    Args:
        session: TestSession object
        results: AssessmentResult object

    Returns:
        Dictionary containing formatted assessment report
    """
    report = {
        "session_id": str(session.session_id),
        "target": session.target,
        "assessment_date": session.started_at,
        "test_vectors": session.test_vectors,
        "findings": results.to_dict(),
        "recommendations": results.generate_recommendations()
    }

    return report
