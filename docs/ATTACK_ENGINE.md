# DENGKIS ATTACK ENGINE


## CURRENT POWER & CAPABILITIES

Dengkis is a **FULLY OPERATIONAL AGGRESSIVE ATTACK-DRIVEN EXPLOITATION ENGINE** designed for red team operations and penetration testing. This is NOT a passive scanner - it actively exploits vulnerabilities with maximum coverage and provocation.

## CORE PRINCIPLES

1. **Assume vulnerable until proven otherwise**
2. **Active payload injection on EVERY parameter**
3. **False positives acceptable; false negatives are NOT**
4. **Coverage and provocation over politeness**
5. **Never suppress findings due to low confidence**

## ARCHITECTURE

### Attack Engine Components

1. **AggressiveCrawler** (`engine/attack/crawler.py`)
   - Extracts links from HTML, JS, inline scripts, forms, JSON
   - Discovers hidden endpoints (REST, GraphQL, admin, debug)
   - Identifies parameters from query strings, POST bodies, JSON, headers
   - Crawls beyond "/" and treats SPA hash routes as real endpoints
   - Brute forces common paths

2. **PayloadInjector** (`engine/attack/injector.py`)
   - Injects payloads into EVERY discovered parameter
   - Uses mutation-based payload testing
   - Performs response differential analysis
   - Detects vulnerabilities through:
     - Response length deviation
     - Status code changes
     - Keyword leaks (SQL errors, command output)
     - Payload reflection
     - Execution indicators (e.g., SSTI: {{7*7}} = 49)
     - Time-based delays

3. **PayloadLibrary** (`engine/attack/payloads.py`)
   - SQL Injection (error-based, boolean-based, time-based, union-based)
   - XSS (reflected, stored, DOM-based, encoded)
   - SSTI (Jinja2, Twig, Handlebars, ERB, Freemarker)
   - Command Injection (basic, time-based, blind)
   - LFI / Path Traversal (basic, encoded, PHP wrappers)
   - Auth Bypass (null tokens, boolean injection)
   - Open Redirect
   - Prototype Pollution
   - Mass Assignment

4. **KnownAppDetector** (`engine/attack/app_detector.py`)
   - Detects Juice Shop, DVWA, WebGoat, bWAPP
   - Loads tailored payloads for known endpoints
   - NEVER returns "0 findings" silently on known vulnerable targets

5. **AttackEngine** (`engine/attack/engine.py`)
   - Orchestrates crawling, injection, and analysis
   - Coordinates all attack components
   - Generates comprehensive attack results

## ATTACK MODES

### Passive
- No payload injection
- Information gathering only

### Active (Default)
- Standard payload set
- Moderate coverage

### Aggressive (Recommended)
- ALL payloads
- Maximum coverage
- Time-based attacks enabled
- WAF bypass attempts (encoding, case mutation)

## USAGE

### Basic Attack

```bash
# Aggressive attack (default)
dengkis scan http://target.com --authorized --mode aggressive

# Active attack
dengkis scan http://target.com --authorized --mode active

# Passive (information gathering only)
dengkis scan http://target.com --authorized --mode passive
```

### Generate Attack Report

```bash
# Generate attacker-style report
dengkis report --session-id <session_id> --format html

# Report automatically uses attack format if session has attack_mode
```

## ATTACK FLOW

1. **App Detection**: Detect known vulnerable apps (Juice Shop, DVWA, etc.)
2. **Crawling**: Aggressively crawl and discover endpoints/parameters
3. **Baseline**: Establish baseline responses for differential analysis
4. **Injection**: Inject payloads into all discovered parameters
5. **Analysis**: Analyze responses for vulnerability indicators
6. **Reporting**: Generate attacker-style report with evidence

## FINDING STRUCTURE

Each finding includes:
- **Endpoint**: Vulnerable URL
- **Parameter**: Injected parameter name
- **Payload**: Exact payload used
- **Category**: Vulnerability type (SQLi, XSS, etc.)
- **Confidence**: low / medium / high
- **Evidence**: List of evidence items
- **Response Snippet**: Relevant response portion
- **Baseline Comparison**: Diff against baseline

## REPORTING & DASHBOARDS

### Attack Reports
Reports are **attacker-style**, not compliance-style:
- Shows exact payloads used
- Includes evidence and response snippets
- Highlights vulnerable endpoints
- Groups by attack category
- Never hides findings due to low confidence

### Threat-Centric Operator Dashboard
**NEW**: Professional threat-centric dashboard designed for security operations:
- **Dark Mode**: Terminal-style dark theme optimized for low-light environments
- **Immediate Context**: Target, session ID, attack mode, authorization status at a glance
- **Threat Summary**: Exposure score, findings breakdown, risk statements
- **Operator Insights**: Kill chain mapping, attacker value analysis, defensive implications
- **Signal Types**: Behavioral, Execution, Exposure, Trust Boundary classification
- **Never Misleading**: Even with 0 findings, explains why that doesn't mean "secure"
- **Tactical Decision Support**: Designed for operators making decisions under pressure
- **High Information Density**: Monospace typography, high contrast, maximum data per screen
- **Collapsible Technical Details**: Raw data hidden by default, expandable for deep analysis

**Dashboard Features**:
- Exposure Score (attack surface metric, not exploit-based)
- Findings grouped by category with severity badges
- Kill chain stage mapping (Initial Access, Execution, Collection, etc.)
- Attacker value analysis (what kind of attacker would exploit this)
- Defensive implications (what defenders should do immediately)
- Known vulnerable app warnings
- Risk statements (never says "safe" or "secure")

## KNOWN VULNERABLE APPS

When detected, the engine:
1. Adds tailored endpoints to crawl list
2. Tests known vulnerable endpoints
3. Uses app-specific payloads
4. Warns if 0 findings on known vulnerable app

## CONFIDENCE SCORING

- **High**: Clear evidence (SQL errors, time delays, execution)
- **Medium**: Suspicious indicators (reflection, length changes)
- **Low**: Minor anomalies (status changes, small length deviations)

**Important**: Low confidence findings are STILL REPORTED. We prefer over-reporting.

## EXAMPLE OUTPUT

```
[ATTACK] Starting attack on http://target.com (mode: aggressive)
[ATTACK] Phase 1: Aggressive crawling...
[ATTACK] Discovered 45 endpoints and 127 parameters
[ATTACK] Phase 2: Payload injection...
[ATTACK] Injection complete. Found 12 potential vulnerabilities

[ATTACK] ATTACK COMPLETE
============================================================
Session ID: abc123
Target: http://target.com
Attack Mode: AGGRESSIVE

FINDINGS: 12
  - High Confidence: 3
  - Medium Confidence: 5
  - Low Confidence: 4

DETECTED VULNERABLE APPS: 1
  - OWASP Juice Shop (confidence: high)
```

## WARNINGS

- This tool actively exploits vulnerabilities
- Use only on authorized targets
- Requires `--authorized` flag
- Designed for penetration testing environments
- Not a compliance scanner

## ENGINEERING

- **Modular**: Each component is independent
- **Extensible**: Easy to add new payloads/categories
- **Python-based**: Async/await for performance
- **Payloads stored separately**: Easy to update

## CURRENT CAPABILITIES SUMMARY

### Attack Engine
- ✅ **Aggressive Crawling**: Discovers endpoints from HTML, JS, JSON, forms, SPA routes
- ✅ **Active Payload Injection**: Injects into EVERY discovered parameter
- ✅ **Comprehensive Payload Library**: 9 attack categories, 50+ payloads
- ✅ **Response Differential Analysis**: Baseline comparison for accurate detection
- ✅ **Known App Detection**: Juice Shop, DVWA, WebGoat, bWAPP with tailored payloads
- ✅ **Attack Modes**: Passive, Active, Aggressive (configurable intensity)
- ✅ **Time-Based Detection**: Blind SQLi, command injection via timing analysis
- ✅ **Multi-Vector Testing**: GET, POST, path injection, header manipulation

### Detection Capabilities
- ✅ **SQL Injection**: Error-based, boolean-based, time-based, union-based
- ✅ **XSS**: Reflected, stored, DOM-based, encoded variants
- ✅ **SSTI**: Jinja2, Twig, Handlebars, ERB, Freemarker
- ✅ **Command Injection**: Basic, time-based, blind execution
- ✅ **LFI/Path Traversal**: Basic, encoded, PHP wrappers, Windows paths
- ✅ **Auth Bypass**: Null tokens, boolean injection, default credentials
- ✅ **Open Redirect**: Protocol-relative, JavaScript, encoded
- ✅ **Prototype Pollution**: JavaScript object manipulation
- ✅ **Mass Assignment**: Admin privilege escalation, role manipulation

### Reporting & Analysis
- ✅ **Attacker-Style Reports**: HTML, JSON, Markdown formats
- ✅ **Threat-Centric Dashboard**: Operator-focused tactical dashboard
- ✅ **Evidence Collection**: Response snippets, baseline comparisons, keyword detection
- ✅ **Confidence Scoring**: High/Medium/Low (never suppresses low confidence)
- ✅ **Kill Chain Mapping**: Maps findings to attack stages
- ✅ **Attacker Value Analysis**: Explains exploitation potential
- ✅ **Defensive Implications**: Actionable guidance for defenders

### Operational Features
- ✅ **Session Management**: Track multiple assessments
- ✅ **Batch Scanning**: Process multiple targets
- ✅ **CLI Interface**: Full command-line control
- ✅ **Python API**: Programmatic access for automation
- ✅ **Docker Support**: Containerized deployment
- ✅ **Offline Operation**: No external dependencies for dashboard
- ✅ **Kali Linux Native**: Optimized for penetration testing environments

### Engineering Excellence
- ✅ **Modular Architecture**: Independent, extensible components
- ✅ **Async/Await**: High-performance concurrent operations
- ✅ **Error Handling**: Robust error recovery and logging
- ✅ **Payload Management**: Separated payload library for easy updates
- ✅ **Template System**: Jinja2-based report generation
- ✅ **Pure Python**: No external binary dependencies

## POWER METRICS

- **Payload Categories**: 9
- **Total Payloads**: 50+ (aggressive mode)
- **Attack Vectors**: SQLi, XSS, SSTI, Command Injection, LFI, Auth Bypass, Open Redirect, Prototype Pollution, Mass Assignment
- **Detection Methods**: Error-based, Boolean-based, Time-based, Union-based, Reflection-based, Execution-based
- **Known Apps Detected**: 4 (Juice Shop, DVWA, WebGoat, bWAPP)
- **Report Formats**: HTML, JSON, Markdown
- **Dashboard Types**: Attack Report, Threat-Centric Operator Dashboard
- **Concurrent Operations**: 20+ simultaneous payload injections
- **Crawl Depth**: Configurable (default: 3 levels)
- **Common Paths Brute-Forced**: 30+ admin/debug/API paths

## TRANSFORMATION SUMMARY

**Before**: Passive, read-only, compliance-focused scanner
**After**: Aggressive, attack-driven, exploitation-focused engine

**Dengkis is now FULLY OPERATIONAL. It's DANGEROUS. It's LOUD. It's UNCOMFORTABLE.**
**This is by design.**
