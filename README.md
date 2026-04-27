# PROJEK DENGKIS

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-Proprietary-red.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-green.svg)](docs/PRODUCTION_READY.md)

**PROJEK DENGKIS** is a professional-grade web exploitation engine designed for authorized security assessments, red team operations, and penetration testing. Unlike passive scanners, Dengkis focuses on active exploitation and evidence-based vulnerability verification.

> [!CAUTION]
> **RESTRICTED USE - AUTHORIZED SECURITY TESTING ONLY**
> This tool is designed for use by security professionals on systems they own or have explicit permission to test. Unauthorized use is illegal.

---

## 🎯 Key Capabilities

- **Active Exploitation Engine**: Goes beyond detection by attempting to exploit vulnerabilities (SQLi, SSTI, RCE, LFI, etc.) and extract proof-of-concept data.
- **Deep Surface Discovery**: Automatically identifies 200+ endpoints through HTML parsing, JavaScript analysis, and brute-force path discovery.
- **Advanced Evasion**: Features the "Ghost Operator" module for automatic WAF/EDR evasion using encoding, fragmentation, and behavioral jitter.
- **Business Logic Testing**: Specialized probes for race conditions, IDOR, integer overflows, and price manipulation.
- **Post-Exploitation**: Integrated modules for network discovery, credential scavenging, and lateral movement analysis.

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/your-org/Projek_Dengkis.git
cd Projek_Dengkis

# Install dependencies and package
pip install -r requirements.txt
pip install -e .
```

### Basic Usage

```bash
# Run an aggressive scan on a target (requires authorization)
dengkis scan http://target.app --authorized --mode aggressive

# Generate a detailed attack report
dengkis report --format html
```

## 🏗️ Architecture & Modules

The engine is built on a modular architecture designed for high performance and extensibility:

- **Core Engine**: Orchestrates the attack lifecycle and session management.
- **Aggressive Crawler**: Deep discovery of endpoints and API routes.
- **Payload Injector**: Context-aware injection with multi-vector support.
- **WAF Evasion (Ghost Operator)**: Advanced bypass techniques.
- **Flag Hunter**: Automated CTF and environment discovery.
- **Reporting**: Comprehensive results in HTML, JSON, and Markdown.

See the [Documentation](#documentation) section for in-depth details.

## 📚 Documentation

Detailed documentation is available in the `docs/` directory:

- [System Architecture](docs/ARCHITECTURE.md)
- [API Reference](docs/API_REFERENCE.md)
- [Usage Guide](docs/USAGE_GUIDE.md)
- [Kali Linux Step-by-Step Guide](docs/KALI_LINUX_GUIDE.md)
- [Attack Engine Internals](docs/ATTACK_ENGINE.md)
- [Performance Optimization](docs/PERFORMANCE_TUI.md)

## ⚖️ Security & Legal

Dengkis is powerful and potentially destructive. Its use is governed by the following principles:

1. **Authorization First**: The `--authorized` flag is required for all active operations.
2. **Attacker Mindset**: Designed to simulate realistic attack patterns to improve defensive posture.
3. **Evidence-Based**: Prioritizes actual exploitation evidence over simple pattern matching.

**By using this software, you agree to the terms in the [LICENSE](LICENSE).**

---

© 2026 PROJEK DENGKIS Team. All rights reserved.
