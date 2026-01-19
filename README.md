# PROJEK DENGKIS

**⚠️ RESTRICTED USE - AUTHORIZED SECURITY TESTING ONLY ⚠️**

**AGGRESSIVE ATTACK-DRIVEN EXPLOITATION ENGINE**

Dengkis is an **ACTIVE, AGGRESSIVE** web exploitation engine designed for **AUTHORIZED** penetration testing and red team operations. This is NOT a passive scanner - it actively injects payloads and exploits vulnerabilities.

**⚠️ WARNING: This is dangerous software. Use only with proper authorization. See [LICENSE](LICENSE) for restrictions.**

## Goal
Provide aggressive, attack-driven vulnerability exploitation. The framework operates on the principle of **"Assume vulnerable until proven otherwise"** and focuses on active payload injection and exploitation rather than passive observation.

## Design Principles
- **Attack-Driven**: Actively inject payloads and exploit vulnerabilities
- **Assume Vulnerable**: Target is vulnerable until proven otherwise
- **Coverage Over Politeness**: Maximum payload coverage, not minimal
- **False Positives OK**: Prefer over-reporting with evidence
- **Authorization-first**: Explicit authorization required (--authorized flag)
- **Attacker Mindset**: Think like a real attacker, not a compliance scanner

## Features

### Attack Engine
- ✅ **Aggressive Crawling**: Extracts endpoints from HTML, JS, JSON, forms, SPA routes, brute-forces common paths
- ✅ **Active Payload Injection**: SQLi, XSS, SSTI, Command Injection, LFI, Auth Bypass, Open Redirect, Prototype Pollution, Mass Assignment
- ✅ **Response Differential Analysis**: Baseline comparison detects vulnerabilities through length deviation, status changes, keyword leaks, time delays
- ✅ **Known App Detection**: Automatically detects Juice Shop, DVWA, WebGoat, bWAPP with tailored payloads and endpoints
- ✅ **Attack Modes**: Passive (info gathering), Active (standard payloads), Aggressive (all payloads, time-based attacks)
- ✅ **Multi-Vector Testing**: GET parameters, POST bodies, path injection, header manipulation

### Reporting & Analysis
- ✅ **Attacker-Style Reports**: HTML, JSON, Markdown formats showing exact payloads, evidence, response snippets
- ✅ **Threat-Centric Dashboard**: Dark mode operator dashboard with kill chain mapping, attacker value analysis, defensive implications
- ✅ **Confidence Scoring**: High/Medium/Low confidence levels (never suppresses low confidence findings)
- ✅ **Never Silent**: Warns if 0 findings on known vulnerable apps, explains why 0 findings doesn't mean "secure"
- ✅ **Operator Insights**: Explains what kind of attacker would exploit findings, kill chain stages, tactical implications

## Quick Start

```bash
# Aggressive attack (default)
dengkis scan http://target.com --authorized --mode aggressive

# Generate attack report
dengkis report --format html
```

### Python API

```python
from engine.attack.engine import AttackEngine
import httpx
import asyncio

async def attack():
    async with httpx.AsyncClient(verify=False) as client:
        engine = AttackEngine("http://target.com", attack_mode="aggressive", session=client)
        results = await engine.attack()
        print(f"Found {results['total_findings']} vulnerabilities")

asyncio.run(attack())
```

## Documentation

- **[Architecture](docs/ARCHITECTURE.md)** - System architecture and design
- **[API Reference](docs/API_REFERENCE.md)** - Complete API documentation
- **[Usage Guide](docs/USAGE_GUIDE.md)** - Usage examples and workflows
- **[Attack Engine](ATTACK_ENGINE.md)** - Core attack engine documentation
- **[Advanced Modules](ADVANCED_MODULES.md)** - Advanced attack modules
- **[Performance & TUI](PERFORMANCE_TUI.md)** - Performance optimization & TUI

## Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

## Current Status

**ATTACK ENGINE: ✅ FULLY OPERATIONAL**

### Core Attack Capabilities
- ✅ **Aggressive Crawler**: Discovers endpoints from HTML, JS, JSON, forms, SPA routes
- ✅ **Active Payload Injection**: Injects into EVERY discovered parameter
- ✅ **Comprehensive Payload Library**: 9 categories, 50+ payloads (SQLi, XSS, SSTI, Command Injection, LFI, Auth Bypass, etc.)
- ✅ **Response Differential Analysis**: Baseline comparison for accurate vulnerability detection
- ✅ **Known App Detection**: Automatically detects Juice Shop, DVWA, WebGoat, bWAPP with tailored payloads
- ✅ **Attack Modes**: Passive, Active, Aggressive (configurable intensity)
- ✅ **Time-Based Detection**: Blind SQLi and command injection via timing analysis

### Reporting & Dashboards
- ✅ **Attacker-Style Reports**: HTML, JSON, Markdown with payloads and evidence
- ✅ **Threat-Centric Operator Dashboard**: Dark mode, tactical insights, kill chain mapping
- ✅ **Confidence Scoring**: High/Medium/Low (never suppresses findings)
- ✅ **Operator Insights**: Attacker value analysis, defensive implications, kill chain stages

### Operational Features
- ✅ **Session Management**: Track and manage multiple assessments
- ✅ **Batch Scanning**: Process multiple targets concurrently
- ✅ **CLI Interface**: Full command-line control with attack modes
- ✅ **Python API**: Programmatic access for automation
- ✅ **Docker Support**: Containerized deployment ready

## Performance & TUI

- ✅ **Kernel-Level Tuning**: Auto-optimizes ulimit, TCP parameters for maximum throughput
- ✅ **Leaky Bucket Rate Limiting**: Maximum throughput without crashing network stack
- ✅ **Zero-Copy Processing**: mmap for wordlists, ujson for fast JSON parsing
- ✅ **GPU Acceleration**: Optional PyOpenCL/CuPy support for heavy computations
- ✅ **Tactical TUI**: Full-screen terminal dashboard with kill-chain, breach stream, impact graph
- ✅ **Kali Integration**: Nerd Font icons, desktop notifications, session persistence
- ✅ **One-Click PoC**: Instant exploit reproduction commands

See [PERFORMANCE_TUI.md](PERFORMANCE_TUI.md) for complete documentation.


## Requirements

- Python 3.8+
- Kali Linux (for deployment)
- Authorized testing environment

## Security Considerations

⚠️ **CRITICAL WARNING**: This is DANGEROUS SOFTWARE - AUTHORIZED USE ONLY

- **⚠️ NOT FOR GENERAL PUBLIC USE** - This tool actively exploits vulnerabilities
- **⚠️ REQUIRES explicit authorization** (--authorized flag)
- **⚠️ Designed for authorized penetration testing and security research ONLY**
- **⚠️ Use ONLY on systems you own or have written permission to test**
- **⚠️ Unauthorized use is ILLEGAL and may result in criminal prosecution**
- **⚠️ May trigger IDS/IPS alerts and security monitoring**
- **⚠️ Designed for Kali Linux / authorized penetration testing environments**
- **⚠️ Users assume ALL responsibility for their use of this software**
- **⚠️ The authors are NOT responsible for misuse or illegal activities**

**BY USING THIS SOFTWARE, YOU ACKNOWLEDGE:**
- You understand this is dangerous software that can exploit vulnerabilities
- You have proper authorization to use this software
- You will use it only for authorized security testing
- You accept full responsibility for your use
- Unauthorized use is illegal and may be prosecuted

**See [LICENSE](LICENSE) for complete terms and restrictions.**

## Attack Capabilities

### Standard Vulnerabilities
- SQL Injection (error-based, boolean-based, time-based, union-based)
- XSS (reflected, stored, DOM-based)
- SSTI (Jinja2, Twig, Handlebars, ERB, Freemarker)
- Command Injection
- LFI / Path Traversal
- Authentication Bypass
- Open Redirect
- Prototype Pollution
- Mass Assignment

### Advanced Modules
- **Flag Hunter**: CTF automation, environment dumps, config crawling
- **Ghost Operator**: WAF/EDR evasion, payload encoding, user-agent rotation
- **Logic Breaker**: Business logic testing, race conditions, IDOR discovery
- **Red Team Architect**: Post-exploitation, network discovery, credential scavenging
- **Attacker Mindset**: Intelligence reporting, kill chain mapping, curl commands

See [ADVANCED_MODULES.md](ADVANCED_MODULES.md) for complete documentation.
