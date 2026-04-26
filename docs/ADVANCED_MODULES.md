# ADVANCED ATTACK MODULES

## Overview

Dengkis includes 5 advanced modules that extend beyond standard vulnerability scanning into CTF automation, WAF evasion, business logic testing, post-exploitation, and intelligence reporting.

## 1. Flag Hunter (CTF Automation)

**System Prompt**: "You are the Dengkis Exfiltration Module. Your goal is to maximize data retrieval."

### Capabilities

- **Regex Search**: Automatically scans all response bodies for CTF flag patterns:
  - `FLAG{.*}`
  - `CTF{.*}`
  - MD5/SHA1-like patterns
  - User-defined flag formats

- **Environment Dump**: If RCE is achieved, immediately executes:
  - `env` - Environment variables
  - `cat /proc/self/environ` - Process environment
  - `ls -la /home` - Home directory listing
  - `cat /etc/passwd` - User accounts
  - `cat ~/.bash_history` - Command history
  - `cat ~/.ssh/id_rsa` - SSH keys

- **Config Crawl**: If LFI is confirmed, systematically attempts to read:
  - `../../../../etc/passwd`
  - `../../../../var/www/html/.env`
  - `../../../../.git/config`
  - `~/.bash_history`
  - And 15+ other sensitive paths

### Integration

Automatically triggered when:
- RCE/Command Injection is confirmed
- LFI is confirmed
- Any response contains flag patterns

## 2. Ghost Operator (WAF/EDR Evasion)

**System Prompt**: "You are the Dengkis Stealth Controller."

### Capabilities

- **Block Detection**: Monitors for:
  - 403 Forbidden
  - 406 Not Acceptable
  - 429 Too Many Requests
  - 503 Service Unavailable

- **Evasion Techniques**:
  - **Double URL Encoding**: `'` → `%27` → `%2527`
  - **Null Byte Injection**: `%00` injection
  - **Unicode Encoding**: Full unicode encoding
  - **Payload Fragmentation**: Split payloads across multiple HTTP headers
  - **User-Agent Rotation**: 50+ legitimate browser strings
  - **Jitter Delay**: Random 200ms-1500ms delays to break pattern recognition

### Activation

Automatically activates when 2+ blocks are detected. All subsequent requests use evasion techniques.

## 3. Logic Breaker (Business Logic & Race Conditions)

**System Prompt**: "You are the Dengkis Logic Engine."

### Capabilities

- **Integer Overflow Testing**:
  - Negative numbers: `-1`, `-999999`
  - Extreme values: `INT_MIN`, `INT_MAX`
  - Tests price/quantity fields for underflow vulnerabilities

- **Race Condition Probe**:
  - Sends 20 identical requests within 50ms window
  - Tests if single-use tokens can be processed multiple times
  - Detects duplicate processing

- **IDOR Discovery**:
  - Iterates through integer IDs in URLs
  - Compares response sizes: `/api/user/101` vs `/api/user/102`
  - Flags identical structures as high-probability IDOR

### Testing Focus

Focuses on numeric and boolean parameters in state-changing requests (POST/PUT/PATCH).

## 4. Red Team Architect (Post-Exploitation)

**System Prompt**: "You are the Dengkis Post-Exploitation Lead."

### Capabilities

- **Network Discovery**:
  - `arp -a` - ARP table mapping
  - `ip route` - Routing table
  - `ifconfig` - Network interfaces
  - Maps internal subnets

- **Credential Scavenging**:
  - Searches for `DB_PASSWORD`, `AWS_SECRET`, `SECRET_KEY`
  - Finds SSH keys (`id_rsa`)
  - Locates `.env` files
  - Scans for password strings in code

- **Lateral Movement Probe**:
  - Identifies internal IPs from network discovery
  - Probes SSH (22), SMB (445), RDP (3389) ports
  - Maps accessible services for pivoting

### Integration

Triggered after RCE confirmation to map the internal network and find credentials.

## 5. Attacker Mindset (Intelligence Reporting)

**System Prompt**: "You are the Dengkis Intelligence Officer."

### Capabilities

For every finding, generates an **Attacker Insight** block:

- **Kill Chain Stage**:
  - Initial Access
  - Execution
  - Persistence
  - Privilege Escalation
  - Collection
  - Reconnaissance

- **Complexity vs Impact**:
  - Rates exploit difficulty vs damage potential
  - Examples: "Low Effort / Critical Impact"
  - Matrix analysis across all findings

- **Evidence**:
  - Provides exact `curl` command to reproduce exploit
  - Ready-to-use for immediate testing

- **Attacker Value**:
  - Explains what kind of attacker would exploit this
  - Prioritizes findings by exploitation value

- **Exploitation Tips**:
  - Actionable guidance for each vulnerability type
  - Next steps for exploitation

- **Defensive Implications**:
  - What defenders should do immediately
  - Remediation guidance

### Intelligence Report

Generates comprehensive report with:
- Kill chain distribution analysis
- Complexity/Impact matrix
- All attacker insights
- Prioritized exploitation paths

## Integration Flow

```
1. Standard Attack (Payload Injection)
   ↓
2. Vulnerability Confirmed
   ↓
3. Flag Hunter Activated (if RCE/LFI)
   ↓
4. Ghost Operator Activated (if WAF blocks)
   ↓
5. Logic Breaker Tests (business logic)
   ↓
6. Red Team Architect (post-exploitation)
   ↓
7. Attacker Mindset (intelligence report)
```

## Usage

All modules are automatically integrated. No additional configuration needed.

### Manual Activation

```python
from engine.attack.flag_hunter import FlagHunter
from engine.attack.ghost_operator import GhostOperator
from engine.attack.logic_breaker import LogicBreaker
from engine.attack.red_team_architect import RedTeamArchitect
from engine.attack.attacker_mindset import AttackerMindset

# Flag Hunter
flag_hunter = FlagHunter(session)
flags = await flag_hunter.hunt_flags(response_text, endpoint)

# Ghost Operator
ghost = GhostOperator(session)
response = await ghost.send_evasive_request('POST', url, payload=payload)

# Logic Breaker
logic = LogicBreaker(session)
idor_findings = await logic.discover_idor("http://target.com/api/user/{id}")

# Red Team Architect
architect = RedTeamArchitect(session)
network_map = await architect.network_discovery(rce_endpoint, param, payload)

# Attacker Mindset
mindset = AttackerMindset()
insight = mindset.generate_attacker_insight(finding)
```

## Output

Attack results now include:
- `exfiltrated_data`: Data retrieved by Flag Hunter
- `flags_found`: CTF flags discovered
- `logic_findings`: Business logic vulnerabilities
- `attacker_intelligence`: Complete intelligence report
- `network_map`: Internal network topology
- `credentials_found`: Discovered credentials

## Power Enhancement

These modules transform Dengkis from a vulnerability scanner into a **complete red team automation platform**:

- ✅ CTF automation
- ✅ WAF evasion
- ✅ Business logic testing
- ✅ Post-exploitation
- ✅ Intelligence reporting

**Dengkis is now a full-spectrum attack platform.**
