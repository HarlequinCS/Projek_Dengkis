# PROJEK DENGKIS - Usage Guide

## Getting Started

### Prerequisites

- Python 3.8+
- Kali Linux (for deployment)
- Authorized testing environment

### Installation

```bash
# Clone repository
git clone <repository-url> Projek_Dengkis
cd Projek_Dengkis
```

### Install dependencies (recommended)

On Debian-based systems (including Kali), avoid modifying the system Python. Use a virtual environment:

```bash
# Install venv support (one-time)
sudo apt install python3-venv -y

# Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate

# Then install requirements inside the venv
pip install -r requirements.txt
```

This prevents PEP 668 "externally managed environment" errors when Kali blocks global pip installs.


### Fast but risky (not recommended)

Force installation into the system environment (may break OS tools):

```bash
pip install -r requirements.txt --break-system-packages
```

### Alternative for standalone CLIs

For single packages, consider pipx:

```bash
pipx install package-name
```

## Basic Usage

### Initializing an Assessment

```python
from engine.runner import run_assessment

# Start assessment with explicit authorization
result = run_assessment("example.com", authorized=True)

print(f"Session ID: {result['session_id']}")
print(f"Status: {result['status']}")
```

### Creating a Test Session

```python
from engine.core.session import TestSession

# Create test session
session = TestSession(target="example.com", authorized=True)

# Check session status
status = session.get_status()
print(status)
```

### Behavioral Analysis

```python
from engine.core.session import TestSession

session = TestSession(target="example.com", authorized=True)

# Generate behavioral fingerprint
fingerprint = session.behavioral_fingerprint()
print(f"Technologies identified: {fingerprint['identified_technologies']}")
print(f"Security controls: {fingerprint['security_controls_detected']}")

# Analyze response patterns
patterns = session.analyze_response_patterns()
print(f"Anomalies detected: {patterns['anomalies_detected']}")
```

### Scope Analysis

```python
from engine.core.aggressive_scope import AggressiveScope

# Initialize scope analyzer
scope = AggressiveScope(primary_target="example.com")

# Validate target
validation = scope.validate_target("example.com", authorization_required=True)
if validation["validated"]:
    print("Target validated successfully")

# Identify peripheral systems
peripheral = scope.identify_peripheral_systems("example.com")
print(f"Peripheral systems: {peripheral['peripheral_systems']}")

# Analyze trust boundaries
trust_analysis = scope.analyze_trust_boundaries("example.com")
print(f"Trust boundaries: {trust_analysis['trust_boundaries_identified']}")
```

### Assessment Results

```python
from engine.core.advanced_result import AssessmentResult
from engine.core.session import TestSession
import uuid

# Create session
session = TestSession(target="example.com", authorized=True)

# Create assessment result
result = AssessmentResult(
    session_id=session.session_id,
    target="example.com",
    test_vectors=[],
    anomaly_indicators=[]
)

# Assess security maturity
maturity = result.assess_security_maturity()
print(f"Security maturity: {maturity['maturity_level']}")

# Prioritize remediation
remediations = result.prioritize_remediation()
for item in remediations:
    print(f"Priority: {item['priority_level']} - {item['recommended_action']}")
```

### Behavioral Reconnaissance

```python
from engine.modules.advanced_reconnaissance import BehavioralAnalyzer

analyzer = BehavioralAnalyzer()

# Analyze target behavior
responses = [
    {"response_time": 0.5, "status_code": 200},
    {"response_time": 0.3, "status_code": 200},
    {"error_message": "Internal Server Error", "status_code": 500}
]

behavior = analyzer.analyze_target_behavior("example.com", responses)
print(f"Anomalies: {behavior['anomalies_detected']}")

# Recognize response patterns
patterns = analyzer.recognize_response_patterns(responses)
print(f"Error patterns: {len(patterns['error_message_patterns'])}")
```

### Vulnerability Surface Mapping

```python
from engine.modules.vulnerability_indicators import VulnerabilitySurfaceMapper

mapper = VulnerabilitySurfaceMapper()

# Map vulnerability surface
system_info = {
    "services": [
        {"type": "HTTP", "port": 80, "version": "Apache 2.4", "publicly_accessible": True},
        {"type": "HTTPS", "port": 443, "version": "Apache 2.4", "publicly_accessible": True}
    ],
    "configuration": {}
}

surface = mapper.map_vulnerability_surface("example.com", system_info)
print(f"Entry points: {len(surface['entry_points'])}")
print(f"Surface area score: {surface['surface_area_score']}")

# Analyze attack paths
architecture = {
    "components": ["web_server", "database", "api_gateway"],
    "connections": [
        {"source": "web_server", "target": "database", "trust_level": "high"}
    ]
}

paths = mapper.analyze_attack_paths("example.com", architecture)
print(f"Attack paths identified: {len(paths)}")
```

## Workflow Example

### Complete Assessment Workflow

```python
from engine.runner import run_assessment, generate_assessment_report
from engine.core.session import TestSession
from engine.core.advanced_result import AssessmentResult
from engine.core.aggressive_scope import AggressiveScope

# Step 1: Initialize assessment
assessment = run_assessment("example.com", authorized=True)
session = TestSession(target="example.com", authorized=True)

# Step 2: Validate target and scope
scope = AggressiveScope(primary_target="example.com")
validation = scope.validate_target("example.com", authorization_required=True)

if not validation["validated"]:
    print("Target validation failed")
    exit(1)

# Step 3: Perform behavioral analysis
fingerprint = session.behavioral_fingerprint()
patterns = session.analyze_response_patterns()

# Step 4: Generate assessment result
result = AssessmentResult(
    session_id=session.session_id,
    target="example.com",
    test_vectors=session.test_vectors,
    anomaly_indicators=session.anomaly_indicators
)

# Step 5: Assess security posture
maturity = result.assess_security_maturity()
remediations = result.prioritize_remediation()

# Step 6: Generate report
report = generate_assessment_report(session, result)
print(report)
```

## Best Practices

### Authorization

- **Always** set `authorized=True` explicitly
- Verify authorization before running assessments
- Maintain audit trail through session tracking

### Session Management

- Use unique sessions for each assessment
- Track all test vectors and responses
- Record anomaly indicators as they're detected

### Scope Validation

- Always validate targets before assessment
- Identify peripheral systems and dependencies
- Analyze trust boundaries and third-party integrations

### Result Analysis

- Review security maturity assessments
- Prioritize remediation based on scores
- Consider risk amplification factors

## Security Considerations

1. **Authorization Required**: All assessments require explicit authorization
2. **Read-Only Operations**: Framework performs observation only, no exploitation
3. **Audit Trail**: All sessions are tracked with timestamps and unique IDs
4. **Scope Control**: Targets must be validated before assessment
5. **Privacy**: No data exfiltration or persistent storage by default

## Error Handling

```python
from engine.runner import run_assessment

# Check for authorization
result = run_assessment("example.com", authorized=False)
if result.get("status") == "error":
    print(f"Error: {result.get('message')}")
    exit(1)

# Validate assessment results
if "session_id" not in result:
    print("Assessment initialization failed")
    exit(1)
```

## Next Steps

- Integrate network reconnaissance (httpx)
- Implement actual network requests
- Add report export functionality
- Create GUI interface (Tkinter)
- Enhance logging and error handling
