# PROJEK DENGKIS - Architecture Documentation

## Overview

PROJEK DENGKIS is an advanced security assessment framework designed for comprehensive read-only security evaluation through behavioral observation and configuration analysis. The framework operates on the principle of "Detect ≠ Exploit" and focuses on identifying security weaknesses through indirect methods rather than exploitation.

## Design Principles

- **Detect ≠ Exploit**: Identify vulnerabilities without exploitation
- **Observe ≠ Attack**: Behavioral analysis through passive observation
- **Authorization-first**: Explicit authorization required for all assessments
- **Kali-native deployment**: Designed for Kali Linux environments
- **OS-agnostic engine**: Core engine works across platforms

## Project Structure

```
Projek_Dengkis/
├── engine/                    # Core assessment engine
│   ├── runner.py             # Main assessment orchestrator
│   ├── core/                 # Core engine components
│   │   ├── session.py        # TestSession management
│   │   ├── aggressive_scope.py  # Expanded boundary testing
│   │   └── advanced_result.py   # Assessment result generation
│   ├── network/              # Network request handling
│   │   └── request_handler.py  # AggressiveRequestHandler
│   └── modules/              # Assessment modules
│       ├── advanced_reconnaissance.py  # Behavioral analysis (legacy)
│       ├── behavioral_analysis.py      # Advanced behavioral analysis
│       └── vulnerability_indicators.py # Vulnerability mapping
├── gui/                      # Desktop GUI (Tkinter) - Future
├── docs/                     # Documentation
└── scripts/                  # Utility scripts
```

## Core Components

### engine/runner.py

Main assessment orchestrator that coordinates all assessment activities.

**Key Functions:**

- `run_assessment(target: str, authorized: bool) -> Dict`
  - Initiates comprehensive security evaluation
  - Requires explicit authorization flag
  - Returns assessment initialization status

- `perform_aggressive_reconnaissance(target: str, session: TestSession) -> Dict`
  - Non-exploitative reconnaissance techniques
  - Tests system responses to unusual queries
  - Analyzes response timing, error messages, headers

- `analyze_response_patterns(responses: List[Dict]) -> Dict`
  - Behavioral pattern analysis
  - Identifies anomalies through response observation
  - Detects potential weaknesses without exploitation

- `configuration_stress_test(target: str, edge_cases: List[str]) -> Dict`
  - Edge case and boundary condition testing
  - Examines system reactions to edge cases
  - Identifies configuration resilience

- `detect_compliance_deviations(target: str, standards: List[str]) -> Dict`
  - Compliance gap identification
  - Compares configurations against security standards
  - Generates compliance score and recommendations

### engine/core/session.py

**TestSession Class:**

Manages assessment session state and behavioral analysis.

**Key Attributes:**
- `session_id`: UUID4 unique identifier
- `target`: Target system identifier
- `authorized`: Authorization status
- `started_at`: ISO timestamp
- `test_vectors`: List of test vectors executed
- `response_patterns`: Recorded response patterns
- `anomaly_indicators`: Detected anomalies

**Key Methods:**

- `behavioral_fingerprint() -> Dict`
  - Generates behavioral fingerprint of target system
  - Analyzes response characteristics, error patterns, headers
  - Identifies technologies and security controls

- `analyze_response_patterns() -> Dict`
  - Performs response pattern analysis
  - Identifies potential weaknesses through observation
  - Provides consistency analysis

- `comparative_security_metrics(baseline: Optional[Dict]) -> Dict`
  - Generates security metrics against standards
  - Compares with baseline measurements
  - Identifies risk factors

- `technical_debt_assessment() -> Dict`
  - Assesses technical debt based on configuration
  - Analyzes maintenance and update patterns
  - Calculates debt score

### engine/core/aggressive_scope.py

**AggressiveScope Class:**

Handles expanded boundary testing and comprehensive target validation.

**Key Methods:**

- `validate_target(target: str, authorization_required: bool) -> Dict`
  - Comprehensive target validation
  - Expanded boundary testing
  - Format and authorization checks

- `identify_peripheral_systems(target: str) -> Dict`
  - Maps security dependencies
  - Identifies peripheral systems
  - Uses DNS enumeration, subdomain discovery

- `analyze_trust_boundaries(target: str) -> Dict`
  - Trust boundary analysis
  - Identifies potential security gaps
  - Maps trust relationships

- `assess_third_party_integrations(target: str) -> Dict`
  - Evaluates external security risks
  - Analyzes third-party dependencies
  - Identifies integration concerns

- `evaluate_supply_chain_security(target: str) -> Dict`
  - Supply chain security evaluation
  - Identifies indirect vulnerabilities
  - Vendor risk assessment

### engine/core/advanced_result.py

**AssessmentResult Class:**

Comprehensive assessment result management and reporting.

**Key Methods:**

- `calculate_risk_amplification_factors() -> Dict`
  - Identifies risk amplification factors
  - Analyzes compound risk scenarios
  - Maps escalation paths

- `assess_security_maturity() -> Dict`
  - Security maturity assessment
  - Based on configuration and response patterns
  - Provides maturity level scoring

- `integrate_threat_modeling(threat_model: Optional[Dict]) -> Dict`
  - Integrates threat modeling context
  - Maps anomalies to threat scenarios
  - Provides threat prioritization

- `prioritize_remediation() -> List[Dict]`
  - Prioritizes remediation based on exploitability and impact
  - Generates prioritized recommendations
  - Estimates remediation effort

- `analyze_attack_surface() -> Dict`
  - Attack surface analysis
  - Identifies entry points and exposure vectors
  - Maps security controls

### engine/modules/advanced_reconnaissance.py

**BehavioralAnalyzer Class:**

Performs behavioral analysis of target systems.

**Key Methods:**

- `analyze_target_behavior(target: str, responses: List[Dict]) -> Dict`
  - Behavioral analysis of target system
  - Extracts patterns and characteristics
  - Detects anomalies

- `recognize_response_patterns(responses: List[Dict]) -> Dict`
  - Response pattern recognition
  - Analyzes error messages, timing, headers
  - Identifies patterns indicating vulnerabilities

- `detect_configuration_anomalies(target: str, configurations: Dict) -> List[Dict]`
  - Configuration anomaly detection
  - Compares against standard practices
  - Identifies non-standard configurations

- `assess_compliance_deviations(target: str, compliance_checks: Dict) -> Dict`
  - Compliance deviation assessment
  - Compares against security standards
  - Generates compliance score

- `evaluate_security_posture(target: str, findings: Dict) -> Dict`
  - Security posture evaluation
  - Based on observable characteristics
  - Provides posture scoring

### engine/network/request_handler.py

**AggressiveRequestHandler Class:**

Advanced HTTP request handler for aggressive security assessment through read-only observation.

**Key Features:**
- Async/await pattern with httpx
- SSL verification bypass for assessment (authorized testing only)
- Stealth mode with user agent rotation
- Request history tracking

**Key Methods:**

- `probe_target(target: str, probe_vectors: List[str]) -> Dict`
  - Aggressively probe target with various request vectors
  - Extract behavioral information without exploitation
  - Returns behavioral analysis results

- `analyze_response_timing(target: str, endpoints: List[str]) -> Dict`
  - Analyze response timing patterns across endpoints
  - Identify timing-based anomalies
  - Statistical analysis of response times

- `extract_behavioral_fingerprint(target: str) -> Dict`
  - Extract comprehensive behavioral fingerprint
  - Test various paths and analyze responses
  - Identify technologies, security headers, error patterns

- `test_boundary_conditions(target: str, boundary_vectors: List[str]) -> Dict`
  - Test boundary conditions with crafted requests
  - Push systems to limits without exploitation
  - Identify configuration resilience

- `analyze_error_messages(target: str, error_vectors: List[str]) -> Dict`
  - Analyze error messages for information disclosure
  - Extract technology indicators
  - Identify potential vulnerabilities through errors

### engine/modules/behavioral_analysis.py

**BehavioralAnalyzer Class:**

Advanced behavioral analysis engine for extracting maximum information through response pattern analysis.

**Key Methods:**

- `analyze_target_behavior(target: str, responses: List[Dict]) -> Dict`
  - Multi-dimensional behavior analysis
  - Pattern recognition and anomaly detection
  - Risk indicator identification

- `recognize_response_patterns(responses: List[Dict]) -> Dict`
  - Recognize response patterns indicating vulnerabilities
  - Error message pattern analysis
  - Timing pattern recognition
  - Header pattern analysis

- `detect_configuration_anomalies(target: str, configurations: Dict) -> List[Dict]`
  - Detect configuration anomalies against standards
  - Identify missing security headers
  - Check TLS configuration
  - Identify information disclosure

- `assess_compliance_deviations(target: str, compliance_checks: Dict) -> Dict`
  - Assess compliance deviations
  - Generate compliance scores
  - Provide remediation recommendations

- `evaluate_security_posture(target: str, findings: Dict) -> Dict`
  - Evaluate overall security posture
  - Classify strength/weakness indicators
  - Generate posture scores

- `generate_behavioral_fingerprint(target: str, responses: List[Dict]) -> Dict`
  - Generate comprehensive behavioral fingerprint
  - Analyze multiple response dimensions
  - Create behavioral signatures

### engine/modules/vulnerability_indicators.py

**VulnerabilitySurfaceMapper Class:**

Maps vulnerability surfaces and analyzes attack paths.

**Key Methods:**

- `map_vulnerability_surface(target: str, system_info: Dict) -> Dict`
  - Maps vulnerability surface without exploitation
  - Identifies entry points and exposed services
  - Calculates surface area score

- `analyze_attack_paths(target: str, architecture: Dict) -> List[Dict]`
  - Attack path analysis
  - Based on system architecture
  - Identifies potential paths through trust relationships

- `assess_security_control_effectiveness(target: str, controls: List[Dict]) -> Dict`
  - Security control effectiveness assessment
  - Through response testing
  - Identifies weaknesses

- `identify_configuration_weaknesses(target: str, configurations: Dict) -> List[Dict]`
  - Configuration weakness identification
  - Through comparative analysis
  - Checks against best practices

- `evaluate_patch_management(target: str, version_info: Dict) -> Dict`
  - Patch management evaluation
  - Through version analysis
  - Identifies outdated components

## Usage Example

```python
import asyncio
from engine.runner import run_assessment
from engine.core.session import TestSession
from engine.network.request_handler import AggressiveRequestHandler
from engine.modules.behavioral_analysis import BehavioralAnalyzer

# Initialize assessment (requires authorization)
result = run_assessment("example.com", authorized=True)

# Create test session
session = TestSession(target="example.com", authorized=True)

# Perform network reconnaissance
async def perform_assessment():
    async with AggressiveRequestHandler() as handler:
        # Extract behavioral fingerprint
        fingerprint = await handler.extract_behavioral_fingerprint("example.com")
        
        # Probe target with vectors
        probe_results = await handler.probe_target(
            "example.com",
            ["/", "/api", "/admin", "/test"]
        )
        
        # Analyze responses
        analyzer = BehavioralAnalyzer()
        behavior = await analyzer.analyze_target_behavior(
            "example.com",
            probe_results["responses"]
        )

# Run async assessment
asyncio.run(perform_assessment())
```

## Current Status

**Phase 0 - Foundation: Complete**
- ✅ Project structure established
- ✅ Core engine skeleton implemented
- ✅ Session management framework
- ✅ Assessment result generation
- ✅ Behavioral analysis modules
- ✅ Vulnerability mapping framework

**Phase 1 - Integration: Complete**
- ✅ Network reconnaissance implementation
- ✅ Actual network request integration (httpx)
- ✅ Target validation implementation
- ✅ DNS enumeration and subdomain discovery
- ✅ Async/await network operations
- ✅ Enhanced behavioral analysis engine
- ✅ Attack surface expansion capabilities

**Phase 2 - Enhancement: Pending**
- Logging framework
- Rate limiting and throttling
- Report export functionality
- Advanced error handling

## Dependencies

- `httpx`: Async HTTP client library for network requests - **INSTALLED**
- `dnspython`: DNS resolution and enumeration library - **INSTALLED**

## Security Considerations

- All assessments require explicit authorization
- Read-only observation principles
- No exploitation capabilities
- Behavioral analysis only
- Configuration comparison based
- Audit trail through session tracking
