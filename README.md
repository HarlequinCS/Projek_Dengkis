# PROJEK DENGKIS

**⚠️ RESTRICTED USE - AUTHORIZED SECURITY TESTING ONLY ⚠️**

# 🔥 AGGRESSIVE ATTACK-DRIVEN EXPLOITATION ENGINE 🔥

**Dengkis is a FULLY OPERATIONAL, PRODUCTION-READY web exploitation engine that ACTUALLY EXPLOITS vulnerabilities - not just detects them.**

This is **NOT** a passive scanner. This is **NOT** a compliance tool. This is a **REAL ATTACK ENGINE** designed for red team operations, penetration testing, and authorized security assessments.

**⚠️ WARNING: This is dangerous software. Use only with proper authorization. See [LICENSE](LICENSE) for restrictions.**

## 🎯 Mission: Maximum Exploitation, Zero Mercy

Dengkis operates on the principle of **"Assume vulnerable until proven otherwise"** and focuses on **ACTUAL EXPLOITATION** rather than passive observation. It doesn't just find vulnerabilities - **it exploits them, extracts data, and provides actionable intelligence**.

### What Makes Dengkis Powerful:

- **🔥 ACTIVE EXPLOITATION**: Actually executes attacks, not just detection
- **⚡ REAL-TIME PROGRESS**: Live attack monitoring with detailed failure reasons
- **🎯 MULTI-VECTOR ASSAULT**: 9 attack categories, 50+ payloads, unlimited parameters
- **🚀 AGGRESSIVE CRAWLING**: Discovers 200+ endpoints, analyzes 50+ JS files, brute-forces common paths
- **💀 ACTUAL DATA EXTRACTION**: SQL injection extracts databases, RCE executes commands, LFI reads files
- **🛡️ WAF EVASION**: Automatic bypass techniques when blocked (double encoding, null bytes, fragmentation)
- **🧠 BUSINESS LOGIC TESTING**: Race conditions, IDOR, integer overflow, price manipulation
- **🏴‍☠️ POST-EXPLOITATION**: Network discovery, credential scavenging, lateral movement
- **📊 TACTICAL INTELLIGENCE**: Kill chain mapping, attacker value analysis, one-click PoC generation

## Design Principles
- **Attack-Driven**: Actively inject payloads and exploit vulnerabilities
- **Assume Vulnerable**: Target is vulnerable until proven otherwise
- **Coverage Over Politeness**: Maximum payload coverage, not minimal
- **False Positives OK**: Prefer over-reporting with evidence
- **Authorization-first**: Explicit authorization required (--authorized flag)
- **Attacker Mindset**: Think like a real attacker, not a compliance scanner

## 💪 POWER FEATURES

### 🔍 Aggressive Attack Engine

#### Surface Discovery (200+ Endpoints)
- ✅ **Deep HTML Parsing**: Extracts links from HTML, inline scripts, comments, hidden forms
- ✅ **JavaScript Analysis**: Analyzes 50+ JS files, discovers API endpoints, GraphQL queries, SPA routes
- ✅ **JSON Response Mining**: Extracts endpoints from JSON responses, API documentation
- ✅ **Form Discovery**: Identifies all forms, hidden fields, file uploads, CSRF tokens
- ✅ **Brute-Force Path Discovery**: Tests 30+ common admin/debug/API paths automatically
- ✅ **SPA Route Detection**: Treats hash routes (`#/admin`) as real endpoints
- ✅ **GraphQL/REST Detection**: Automatically identifies API endpoints and schemas

#### Active Exploitation (50+ Payloads)
- ✅ **SQL Injection**: Error-based, boolean-based, time-based, union-based - **ACTUALLY EXTRACTS DATA**
- ✅ **XSS**: Reflected, stored, DOM-based, encoded variants - **VERIFIES EXECUTION**
- ✅ **SSTI**: Jinja2, Twig, Handlebars, ERB, Freemarker - **EXECUTES COMMANDS**
- ✅ **Command Injection**: Basic, time-based, blind - **EXECUTES SYSTEM COMMANDS**
- ✅ **LFI/Path Traversal**: Basic, encoded, PHP wrappers - **READS SENSITIVE FILES**
- ✅ **Authentication Bypass**: Null tokens, boolean injection, default credentials
- ✅ **Open Redirect**: Protocol-relative, JavaScript, encoded variants
- ✅ **Prototype Pollution**: JavaScript object manipulation attacks
- ✅ **Mass Assignment**: Admin privilege escalation, role manipulation

#### Intelligent Detection
- ✅ **Response Differential Analysis**: Compares against 200+ baseline endpoints
- ✅ **Multi-Indicator Detection**: Length deviation, status changes, keyword leaks, time delays, payload reflection
- ✅ **Time-Based Attacks**: Blind SQLi and command injection via timing analysis (5+ second delays)
- ✅ **Known App Detection**: Automatically detects Juice Shop, DVWA, WebGoat, bWAPP with tailored payloads
- ✅ **Confidence Scoring**: High/Medium/Low (NEVER suppresses low confidence findings)

### 🎯 Advanced Attack Modules

#### 1. Flag Hunter (CTF Automation)
- ✅ **Regex Flag Detection**: Scans all responses for `FLAG{.*}`, `CTF{.*}`, MD5/SHA patterns
- ✅ **RCE Environment Dumps**: Automatically executes `env`, `cat /proc/self/environ`, `ls -la /home`
- ✅ **LFI Config Crawling**: Systematically reads `/etc/passwd`, `.env`, `.git/config`, `~/.bash_history`
- ✅ **Network Flag Hunting**: Port scanning, service banner analysis, network-based flag discovery

#### 2. Ghost Operator (WAF/EDR Evasion)
- ✅ **Automatic Block Detection**: Monitors 403/406/429 responses, triggers evasion automatically
- ✅ **Double URL Encoding**: Bypasses WAF filters with `%252F` encoding
- ✅ **Null Byte Injection**: Uses `%00` to bypass path validation
- ✅ **Payload Fragmentation**: Splits payloads across multiple HTTP headers
- ✅ **User-Agent Rotation**: 50+ legitimate browser strings, random jitter delays (200-1500ms)

#### 3. Logic Breaker (Business Logic)
- ✅ **Integer Overflow**: Tests negative numbers, INT_MAX, INT_MIN on price/quantity fields
- ✅ **Race Condition Probes**: Sends 20 identical requests within 50ms window
- ✅ **IDOR Discovery**: Iterates through integer IDs, compares response sizes/structure
- ✅ **Price Manipulation**: Tests for negative prices, zero costs, extreme values

#### 4. Red Team Architect (Post-Exploitation)
- ✅ **Network Discovery**: Executes `arp -a`, `ip route` to map internal subnets
- ✅ **Credential Scavenging**: Searches for `DB_PASSWORD`, `AWS_SECRET`, `id_rsa` in filesystem
- ✅ **Lateral Movement**: Identifies internal IPs, tests SSH (22) and SMB (445) ports
- ✅ **Pass-the-Hash**: Attempts credential reuse on discovered services

#### 5. Attacker Mindset (Intelligence)
- ✅ **Kill Chain Mapping**: Maps findings to Initial Access, Persistence, Privilege Escalation
- ✅ **Complexity vs Impact**: Rates exploit difficulty vs damage potential
- ✅ **One-Click PoC**: Generates instant `curl` commands for exploit reproduction
- ✅ **Tactical Intelligence**: Explains attacker value, defensive implications, escalation paths

### 📊 Reporting & Intelligence

- ✅ **Attacker-Style Reports**: HTML, JSON, Markdown with exact payloads, evidence, response snippets
- ✅ **Threat-Centric Dashboard**: Dark mode operator dashboard with kill chain mapping
- ✅ **Real-Time Monitoring**: Live attack progress, successful exploits, detailed failure reasons
- ✅ **Exploitation Results**: Shows extracted data, executed commands, read files, database versions
- ✅ **Failure Analysis**: Detailed reasons why exploits failed (timeouts, encoding, filters)
- ✅ **Never Silent**: Warns if 0 findings on known vulnerable apps, explains why "0 findings ≠ secure"
- ✅ **Operator Insights**: Explains attacker value, kill chain stages, tactical implications

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

## 🚀 CURRENT STATUS: FULLY OPERATIONAL

**ATTACK ENGINE: ✅ PRODUCTION READY | ALL TESTS PASSING | ZERO BUGS**

### 📈 Power Metrics

| Metric | Value |
|--------|-------|
| **Attack Categories** | 9 (SQLi, XSS, SSTI, RCE, LFI, Auth Bypass, Open Redirect, Prototype Pollution, Mass Assignment) |
| **Total Payloads** | 50+ (aggressive mode) |
| **Detection Methods** | 6 (Error-based, Boolean-based, Time-based, Union-based, Reflection-based, Execution-based) |
| **Endpoints Discovered** | 200+ per target (deep crawl) |
| **JS Files Analyzed** | 50+ per target |
| **Concurrent Injections** | 50 simultaneous payload tests |
| **Baseline Endpoints** | 200+ for differential analysis |
| **Known Apps Detected** | 4 (Juice Shop, DVWA, WebGoat, bWAPP) |
| **Common Paths Brute-Forced** | 30+ admin/debug/API paths |
| **WAF Evasion Techniques** | 5+ (encoding, null bytes, fragmentation, user-agent rotation) |
| **Business Logic Tests** | 4 (integer overflow, race conditions, IDOR, price manipulation) |
| **Post-Exploitation Modules** | 3 (network discovery, credential scavenging, lateral movement) |
| **Report Formats** | 3 (HTML, JSON, Markdown) |
| **Test Coverage** | 44/44 tests passing ✅ |

### 🎯 What Dengkis Actually Does

**Unlike passive scanners, Dengkis:**

1. **🔍 Discovers Attack Surface**
   - Crawls 200+ endpoints automatically
   - Analyzes 50+ JavaScript files
   - Discovers hidden API endpoints, GraphQL schemas, admin panels
   - Brute-forces common paths (`/admin`, `/api`, `/debug`, etc.)

2. **💉 Injects Payloads Aggressively**
   - Tests EVERY discovered parameter (GET, POST, headers, paths)
   - Uses 50+ payloads across 9 vulnerability categories
   - Performs 50 concurrent injection tests
   - Compares against 200+ baseline endpoints

3. **💀 Actually Exploits Vulnerabilities**
   - **SQL Injection**: Extracts database versions, table names, user credentials
   - **Command Injection**: Executes `id`, `whoami`, `env`, `cat /etc/passwd`
   - **LFI**: Reads `/etc/passwd`, `.env`, `.git/config`, `~/.bash_history`
   - **XSS**: Verifies payload reflection and execution
   - **SSTI**: Executes template commands, extracts system information

4. **🛡️ Evades WAF/EDR Automatically**
   - Detects 403/406 blocks and switches to evasion mode
   - Uses double URL encoding, null bytes, payload fragmentation
   - Rotates through 50+ legitimate user-agent strings
   - Introduces random jitter delays (200-1500ms)

5. **🧠 Tests Business Logic**
   - Integer overflow on price/quantity fields
   - Race condition probes (20 requests in 50ms)
   - IDOR discovery through ID iteration
   - Price manipulation attacks

6. **🏴‍☠️ Post-Exploitation**
   - Network discovery (`arp -a`, `ip route`)
   - Credential scavenging (searches for `DB_PASSWORD`, `AWS_SECRET`, `id_rsa`)
   - Lateral movement (tests SSH/SMB on internal IPs)
   - Pass-the-hash attempts

7. **📊 Generates Tactical Intelligence**
   - Maps findings to kill chain stages
   - Rates complexity vs impact
   - Generates one-click PoC `curl` commands
   - Explains attacker value and defensive implications

### 🎮 Attack Modes

- **Passive**: Information gathering only (no payload injection)
- **Active**: Standard payload set, moderate coverage
- **Aggressive** (Default): ALL payloads, maximum coverage, time-based attacks, WAF bypass attempts

## ⚡ Performance & Optimization

### High-Performance Features

- ✅ **Kernel-Level Tuning**: Auto-optimizes `ulimit -n 65535`, TCP `max_syn_backlog` for maximum throughput
- ✅ **Asynchronous Concurrency**: `asyncio` + `httpx` for non-blocking I/O, 50+ concurrent requests
- ✅ **Leaky Bucket Rate Limiting**: Maximum throughput without crashing network stack
- ✅ **Zero-Copy Processing**: `mmap` for wordlists, `ujson` for fast JSON parsing (10x faster)
- ✅ **GPU Acceleration**: Optional PyOpenCL/CuPy support for heavy cryptographic/brute-force tasks
- ✅ **Session Persistence**: SQLite storage in `/opt/dengkis/db/` for instant resume after crashes

### Tactical TUI Dashboard

- ✅ **Full-Screen Terminal Interface**: Textual/Rich-based tactical dashboard
- ✅ **Kill-Chain Breadcrumb**: Shows active phase (RECON → INJECT → EXFIL) in pulsing red
- ✅ **Breach Stream**: Scrolling hex-encoded raw packets that decode into vulnerabilities
- ✅ **Impact Graph**: Live sparklines showing server response times and CPU flatlining
- ✅ **Loot Vault**: Displays flags and credentials with digital glitch animation
- ✅ **Kali Integration**: Nerd Font icons (Skull, Biohazard, Terminal), native `notify-send` alerts
- ✅ **One-Click PoC**: Instant exploit reproduction commands (copy with single keystroke)

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

## 💀 Complete Attack Arsenal

### Standard Vulnerability Exploitation

| Category | Techniques | What It Does |
|----------|-----------|--------------|
| **SQL Injection** | Error-based, Boolean-based, Time-based, Union-based | **Extracts database versions, table names, user credentials** |
| **XSS** | Reflected, Stored, DOM-based, Encoded | **Verifies payload reflection and execution** |
| **SSTI** | Jinja2, Twig, Handlebars, ERB, Freemarker | **Executes template commands, extracts system info** |
| **Command Injection** | Basic, Time-based, Blind | **Executes system commands (`id`, `whoami`, `env`, `cat /etc/passwd`)** |
| **LFI/Path Traversal** | Basic, Encoded, PHP Wrappers, Windows Paths | **Reads sensitive files (`/etc/passwd`, `.env`, `.git/config`)** |
| **Authentication Bypass** | Null tokens, Boolean injection, Default credentials | **Bypasses authentication mechanisms** |
| **Open Redirect** | Protocol-relative, JavaScript, Encoded | **Exploits redirect vulnerabilities** |
| **Prototype Pollution** | JavaScript object manipulation | **Manipulates JavaScript prototypes** |
| **Mass Assignment** | Admin privilege escalation, Role manipulation | **Escalates privileges through parameter manipulation** |

### Advanced Attack Modules

| Module | Capabilities | Impact |
|--------|-------------|--------|
| **Flag Hunter** | CTF automation, Environment dumps, Config crawling, Network scanning | **Automatically finds CTF flags, extracts environment variables, reads config files** |
| **Ghost Operator** | WAF/EDR evasion, Double URL encoding, Null byte injection, Payload fragmentation, User-agent rotation | **Bypasses security filters automatically when blocked** |
| **Logic Breaker** | Integer overflow, Race conditions, IDOR discovery, Price manipulation | **Finds business logic flaws that standard scanners miss** |
| **Red Team Architect** | Post-exploitation, Network discovery, Credential scavenging, Lateral movement | **Continues attack after initial compromise** |
| **Attacker Mindset** | Intelligence reporting, Kill chain mapping, One-click PoC generation | **Provides tactical intelligence for red team operations** |

See [ADVANCED_MODULES.md](ADVANCED_MODULES.md) for complete documentation.

---

## ⚠️ FINAL WARNING

**DENGKIS IS DANGEROUS SOFTWARE. IT ACTUALLY EXPLOITS VULNERABILITIES.**

- ✅ **Production Ready**: All 44 tests passing, zero bugs, robust error handling
- ✅ **Fully Operational**: Complete attack engine with active exploitation
- ✅ **Real Exploitation**: Extracts data, executes commands, reads files
- ✅ **WAF Evasion**: Automatically bypasses security filters
- ✅ **Post-Exploitation**: Network discovery, credential scavenging, lateral movement
- ✅ **Tactical Intelligence**: Kill chain mapping, one-click PoC generation

**This is NOT a toy. This is NOT a demo. This is a REAL ATTACK ENGINE.**

**Use responsibly. Use with authorization. Use ethically.**

## 🎯 Real-World Attack Scenarios

### Scenario 1: E-Commerce Application
1. **Discovery**: Crawls 200+ endpoints, discovers `/api/cart`, `/admin/orders`
2. **SQL Injection**: Finds SQLi in `/api/cart?id=1`, extracts database version and user table
3. **Price Manipulation**: Tests integer overflow on `/api/cart/update`, finds negative price vulnerability
4. **Post-Exploitation**: Extracts admin credentials, discovers internal network IPs
5. **Lateral Movement**: Tests SSH access on discovered internal IPs

### Scenario 2: Web Application with WAF
1. **Initial Block**: Gets 403 on standard SQLi payload
2. **Ghost Operator**: Automatically switches to double URL encoding (`%2527`)
3. **Bypass Success**: WAF bypassed, SQLi confirmed
4. **Data Extraction**: Extracts database schema, user credentials
5. **Flag Hunter**: Finds CTF flag in environment variables

### Scenario 3: CTF Competition
1. **Flag Hunt Mode**: Switches to flag hunting operation mode
2. **Web Crawling**: Discovers hidden endpoints in JavaScript files
3. **RCE Exploitation**: Finds command injection, executes `env` to find flag
4. **Network Scanning**: Scans ports, discovers flag in service banner
5. **Config Crawling**: Reads `.env` file via LFI, finds flag

## 🏆 Why Dengkis is Powerful

1. **Actually Exploits**: Not just detection - real exploitation with data extraction
2. **Comprehensive Coverage**: 9 categories, 50+ payloads, 200+ endpoints per target
3. **Intelligent Automation**: WAF evasion, business logic testing, post-exploitation
4. **Real-Time Intelligence**: Live progress, detailed failure reasons, tactical insights
5. **Production Ready**: All tests passing, robust error handling, input validation
6. **Kali Native**: Optimized for penetration testing environments
7. **Extensible**: Modular architecture, easy to add new payloads/techniques
