# PROJEK DENGKIS - API Reference

## Core Engine API

### engine.runner

#### `run_assessment(target: str, authorized: bool = False) -> Dict`

Initiates comprehensive security evaluation through aggressive reconnaissance and behavioral analysis.

**Parameters:**
- `target` (str): Target system or network identifier
- `authorized` (bool): Authorization flag (required for execution)

**Returns:**
```python
{
    "session_id": str,
    "target": str,
    "authorized": bool,
    "started_at": str,  # ISO timestamp
    "status": str,
    "test_vectors": List[Dict],
    "response_patterns": Dict,
    "anomaly_indicators": List[Dict]
}
```

**Raises:**
- Returns error dict if `authorized=False`

---

#### `perform_aggressive_reconnaissance(target: str, session: TestSession) -> Dict`

Performs aggressive but non-exploitative reconnaissance techniques.

**Parameters:**
- `target` (str): Target identifier
- `session` (TestSession): Active test session

**Returns:**
```python
{
    "target": str,
    "techniques_applied": List[str],
    "findings": List[Dict]
}
```

---

#### `analyze_response_patterns(responses: List[Dict]) -> Dict`

Analyzes system response patterns to identify potential vulnerabilities through behavioral observation.

**Parameters:**
- `responses` (List[Dict]): List of response dictionaries from target system

**Returns:**
```python
{
    "total_responses": int,
    "identified_patterns": List[Dict],
    "anomalies": List[Dict],
    "potential_weaknesses": List[Dict]
}
```

---

#### `configuration_stress_test(target: str, edge_cases: List[str]) -> Dict`

Examines how systems react to edge cases and boundary conditions.

**Parameters:**
- `target` (str): Target identifier
- `edge_cases` (List[str]): List of edge case scenarios

**Returns:**
```python
{
    "target": str,
    "edge_cases_tested": List[str],
    "responses": Dict,
    "boundary_conditions_identified": List[Dict],
    "configuration_resilience": str
}
```

---

#### `detect_compliance_deviations(target: str, standards: List[str]) -> Dict`

Identifies where systems deviate from standard security practices.

**Parameters:**
- `target` (str): Target identifier
- `standards` (List[str]): List of security standards to check

**Returns:**
```python
{
    "target": str,
    "standards_checked": List[str],
    "deviations": List[Dict],
    "compliance_score": float,
    "recommendations": List[str]
}
```

---

### engine.core.session

#### `TestSession(target: str, authorized: bool = False)`

Test session management class for tracking security assessment state.

**Attributes:**
- `session_id` (uuid.UUID): Unique session identifier
- `target` (str): Target system identifier
- `authorized` (bool): Authorization status
- `started_at` (str): ISO timestamp of session start
- `test_vectors` (List[Dict]): List of executed test vectors
- `response_patterns` (Dict): Recorded response patterns
- `anomaly_indicators` (List[Dict]): Detected anomalies

**Methods:**

##### `behavioral_fingerprint() -> Dict`

Generates behavioral fingerprint of target system.

**Returns:**
```python
{
    "target": str,
    "session_id": str,
    "response_characteristics": {
        "average_response_time": float,
        "error_message_patterns": List[str],
        "header_patterns": Dict,
        "protocol_behavior": Dict
    },
    "identified_technologies": List[str],
    "security_controls_detected": List[str]
}
```

##### `analyze_response_patterns() -> Dict`

Performs response pattern analysis.

**Returns:**
```python
{
    "patterns_identified": int,
    "pattern_types": List[str],
    "anomalies_detected": int,
    "potential_weaknesses": List[Dict],
    "consistency_analysis": Dict
}
```

##### `comparative_security_metrics(baseline: Optional[Dict] = None) -> Dict`

Generates comparative security metrics against industry standards.

**Parameters:**
- `baseline` (Optional[Dict]): Optional baseline measurements

**Returns:**
```python
{
    "target": str,
    "session_id": str,
    "security_score": float,
    "compliance_indicators": Dict,
    "deviation_from_standards": Dict,
    "risk_factors": List[Dict]
}
```

##### `technical_debt_assessment() -> Dict`

Assesses technical debt based on configuration analysis.

**Returns:**
```python
{
    "target": str,
    "configuration_complexity": str,
    "maintenance_indicators": Dict,
    "update_frequency_indicators": Dict,
    "documentation_quality_indicators": Dict,
    "debt_score": float
}
```

---

### engine.core.aggressive_scope

#### `AggressiveScope(primary_target: str)`

Handles expanded boundary testing and comprehensive target validation.

**Methods:**

##### `validate_target(target: str, authorization_required: bool = True) -> Dict`

Comprehensive target validation with expanded boundary testing.

**Returns:**
```python
{
    "target": str,
    "validated": bool,
    "validation_checks": Dict,
    "boundary_analysis": Dict,
    "errors": List[str]
}
```

##### `identify_peripheral_systems(target: str) -> Dict`

Maps security dependencies and identifies peripheral systems.

**Returns:**
```python
{
    "primary_target": str,
    "peripheral_systems": List[str],
    "dependencies": List[Dict],
    "identification_methods": List[str]
}
```

##### `analyze_trust_boundaries(target: str) -> Dict`

Identifies potential security gaps through trust boundary analysis.

**Returns:**
```python
{
    "target": str,
    "trust_boundaries_identified": int,
    "boundaries": List[Dict],
    "potential_gaps": List[Dict],
    "security_implications": Dict
}
```

---

### engine.core.advanced_result

#### `AssessmentResult(session_id: uuid.UUID, target: str, test_vectors: List[Dict], anomaly_indicators: List[Dict])`

Comprehensive assessment result management.

**Methods:**

##### `calculate_risk_amplification_factors() -> Dict`

Identifies risk amplification factors.

**Returns:**
```python
{
    "factors_identified": List[Dict],
    "compound_risk_scenarios": List[Dict],
    "escalation_paths": List[Dict],
    "impact_analysis": Dict
}
```

##### `assess_security_maturity() -> Dict`

Assesses security maturity based on configuration and response patterns.

**Returns:**
```python
{
    "maturity_level": str,  # "advanced", "intermediate", "basic", "initial"
    "indicators": {
        "configuration_quality": float,
        "security_control_implementation": float,
        "incident_response_readiness": float,
        "compliance_adherence": float
    },
    "recommendations": List[str],
    "comparison_to_standards": Dict
}
```

##### `prioritize_remediation() -> List[Dict]`

Prioritizes remediation based on exploitability and impact factors.

**Returns:**
```python
[
    {
        "finding": Dict,
        "priority_score": float,
        "priority_level": str,  # "critical", "high", "medium", "low"
        "recommended_action": str,
        "estimated_effort": str
    },
    ...
]
```

---

### engine.modules.advanced_reconnaissance

#### `BehavioralAnalyzer()`

Performs behavioral analysis of target systems.

**Methods:**

##### `analyze_target_behavior(target: str, responses: List[Dict]) -> Dict`

Performs behavioral analysis of target system.

**Returns:**
```python
{
    "target": str,
    "analysis_timestamp": str,
    "response_count": int,
    "behavioral_patterns": Dict,
    "system_characteristics": Dict,
    "anomalies_detected": List[Dict]
}
```

##### `recognize_response_patterns(responses: List[Dict]) -> Dict`

Recognizes response patterns for vulnerability indication.

**Returns:**
```python
{
    "error_message_patterns": List[Dict],
    "timing_patterns": Dict,
    "header_patterns": List[str],
    "status_code_patterns": Dict,
    "content_patterns": List[Dict]
}
```

---

### engine.modules.vulnerability_indicators

#### `VulnerabilitySurfaceMapper()`

Maps vulnerability surfaces and analyzes attack paths.

**Methods:**

##### `map_vulnerability_surface(target: str, system_info: Dict) -> Dict`

Maps vulnerability surface without exploitation.

**Returns:**
```python
{
    "target": str,
    "mapping_timestamp": str,
    "entry_points": List[Dict],
    "exposed_services": List[Dict],
    "configuration_weaknesses": List[Dict],
    "surface_area_score": float
}
```

##### `analyze_attack_paths(target: str, architecture: Dict) -> List[Dict]`

Analyzes potential attack paths based on system architecture.

**Returns:**
```python
[
    {
        "path_id": str,
        "source": str,
        "target": str,
        "trust_level": str,
        "potential_vulnerability": str,
        "complexity": str
    },
    ...
]
```
