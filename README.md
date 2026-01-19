# PROJEK DENGKIS

Kali Linux–first security assessment tool for comprehensive read-only security evaluation through behavioral observation and configuration analysis.

## Goal
Provide safe, read-only security observations with strict scope control. The framework operates on the principle of "Detect ≠ Exploit" and focuses on identifying security weaknesses through indirect methods rather than exploitation.

## Design Principles
- **Detect ≠ Exploit**: Identify vulnerabilities without exploitation
- **Observe ≠ Attack**: Behavioral analysis through passive observation
- **Authorization-first**: Explicit authorization required for all assessments
- **Kali-native deployment**: Designed for Kali Linux environments
- **OS-agnostic engine**: Core engine works across platforms

## Features

- ✅ **Advanced Reconnaissance**: Non-exploitative reconnaissance techniques
- ✅ **Behavioral Analysis**: Response pattern recognition and anomaly detection
- ✅ **Scope Analysis**: Expanded boundary testing and peripheral system identification
- ✅ **Security Assessment**: Maturity evaluation and compliance deviation detection
- ✅ **Vulnerability Mapping**: Attack surface analysis and configuration weakness identification
- ✅ **Result Generation**: Risk analysis, remediation prioritization, and comprehensive reporting

## Quick Start

```python
from engine.runner import run_assessment
from engine.core.session import TestSession

# Initialize assessment
result = run_assessment("example.com", authorized=True)

# Create test session
session = TestSession(target="example.com", authorized=True)

# Perform behavioral analysis
fingerprint = session.behavioral_fingerprint()
```

## Documentation

- **[Architecture](docs/ARCHITECTURE.md)** - System architecture and design
- **[API Reference](docs/API_REFERENCE.md)** - Complete API documentation
- **[Usage Guide](docs/USAGE_GUIDE.md)** - Usage examples and workflows
- **[Progress](docs/PROGRESS.md)** - Development progress and status

## Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

## Status

**Phase 0 - Foundation: ✅ COMPLETE**

- Core engine framework implemented
- Session management system
- Behavioral analysis modules
- Vulnerability mapping framework
- Comprehensive documentation

**Phase 1 - Integration: 🔄 PENDING**

- Network request integration
- Actual target scanning
- Response collection pipeline

## Requirements

- Python 3.8+
- Kali Linux (for deployment)
- Authorized testing environment

## Security Considerations

- All assessments require explicit authorization
- Read-only observation principles
- No exploitation capabilities
- Behavioral analysis only
- Audit trail through session tracking
