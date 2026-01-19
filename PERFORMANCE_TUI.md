# PERFORMANCE OPTIMIZATION & TACTICAL TUI

## Performance Optimization

### Kernel-Level Tuning

The `PerformanceOptimizer` automatically applies kernel-level optimizations on Kali Linux:

- **File Descriptors**: Sets `ulimit -n 65535` for maximum concurrent connections
- **TCP Tuning**: 
  - `net.ipv4.tcp_max_syn_backlog=8192` - Increased SYN backlog
  - `net.netfilter.nf_conntrack_max=262144` - More connection tracking
  - `net.ipv4.tcp_fastopen=3` - TCP Fast Open enabled

**Usage**:
```python
from engine.performance.optimizer import PerformanceOptimizer

optimizer = PerformanceOptimizer()
results = optimizer.optimize_environment()
```

### Leaky Bucket Rate Limiting

Implements leaky bucket algorithm for maximum throughput:

```python
from engine.performance.optimizer import LeakyBucketRateLimiter

limiter = LeakyBucketRateLimiter(rate=100.0, capacity=200.0)
await limiter.acquire()  # Non-blocking token acquisition
```

### Zero-Copy Processing

- **Memory-Mapped Wordlists**: Uses `mmap` for zero-copy wordlist access
- **Fast JSON Parsing**: Uses `ujson` for 2-3x faster JSON parsing

```python
from engine.performance.zero_copy import ZeroCopyProcessor

processor = ZeroCopyProcessor()
wordlist = processor.load_wordlist_mmap("/path/to/wordlist.txt")
data = processor.parse_json_fast(json_string)
```

### GPU Acceleration

Automatically detects and uses GPU if available:
- **PyOpenCL**: For OpenCL-compatible GPUs
- **CuPy**: For NVIDIA CUDA GPUs

## Tactical TUI Dashboard

### Visual Theme

- **Background**: True Black (#000000)
- **Accents**: Neon Red (#ff0000) for breaches
- **Dim Grey**: (#333333) for background noise

### Layout Components

1. **Kill-Chain Breadcrumb** (Top)
   - Shows active phase: RECON → INJECT → EXFIL
   - Current phase pulses in red
   - Updates in real-time

2. **Breach Stream** (Center Left)
   - Scrolling hex-encoded raw packets
   - Decodes into human-readable vulnerabilities
   - Real-time vulnerability feed

3. **Impact Graph** (Center Right)
   - Live sparklines showing server response times
   - CPU flatlining visualization
   - Real-time performance metrics

4. **Loot Vault** (Bottom)
   - Displays flags and credentials
   - Digital glitch animation on new items
   - Organized by type (Flag, Credential, Token)

### Usage

```python
from engine.tui.dashboard import create_tactical_dashboard

dashboard = create_tactical_dashboard(attack_engine)
dashboard.set_kill_chain_phase("INJECT")
dashboard.add_vulnerability("http://target.com/api", "SQLi", "' OR 1=1--")
dashboard.add_response_time(125.5)
dashboard.add_loot("Flag", "FLAG{abc123}", "http://target.com")
dashboard.run()
```

### Keyboard Shortcuts

- `q` - Quit
- `c` - Copy PoC to clipboard
- `r` - Refresh dashboard

## Kali Linux Integration

### Nerd Font Icons

Vulnerability types mapped to tactical icons:
- SQL Injection: 💀 (Skull)
- XSS: ☢ (Biohazard)
- Command Injection/RCE: 💻 (Terminal)
- SSTI: ⚡
- LFI: 📁
- Auth Bypass: 🔓

### Desktop Notifications

Uses `notify-send` for critical findings:

```python
from engine.kali.integration import KaliIntegration

kali = KaliIntegration()
kali.notify_critical_finding(finding)
```

### Session Persistence

All sessions saved to `/opt/dengkis/db/sessions.db`:

```python
kali = KaliIntegration()
kali.save_session(session_id, target, attack_mode, findings, state)
session = kali.load_session(session_id)
```

**Features**:
- Instant resume after crash
- SQLite database for reliability
- Automatic session tracking
- Finding persistence

## One-Click PoC Generation

### PoC Formats

Generates PoC in multiple formats:

1. **curl** - Command-line reproduction
2. **Python** - Script-based exploitation
3. **Burp Suite** - HTTP request format

```python
from engine.poc.generator import PoCGenerator

poc = PoCGenerator()
curl_command = poc.generate_curl_poc(finding)
python_script = poc.generate_python_poc(finding)
burp_request = poc.generate_burp_poc(finding)

# Or get all formats
all_pocs = poc.generate_all_pocs(finding)
```

### TUI Integration

Press `c` in the TUI to copy PoC to clipboard for instant use.

## Auto-Trigger Logic

### Ghost Operator on 403

Automatically activates Ghost Operator evasion when 403 Forbidden is detected:

```python
# In PayloadInjector._analyze_response()
if response.status_code == 403:
    self.ghost_operator.evasion_active = True
    # Subsequent requests use evasion techniques
```

### Evasion Techniques Applied

- Double URL encoding
- Null byte injection
- Payload fragmentation
- User-agent rotation
- Jitter delays

## Performance Metrics

### Optimization Results

- **File Descriptors**: 65535 (from default 1024)
- **TCP Backlog**: 8192 (from default 128)
- **Connection Tracking**: 262144 (from default 65536)
- **JSON Parsing**: 2-3x faster with ujson
- **Wordlist Access**: Zero-copy with mmap

### Throughput

With optimizations:
- **Concurrent Requests**: 20+ simultaneous
- **Request Rate**: 100+ requests/second (with rate limiting)
- **Memory Usage**: Reduced with zero-copy processing

## Installation

```bash
# Install performance dependencies
pip install ujson

# Install TUI dependencies
pip install textual rich

# Optional: GPU acceleration
pip install pyopencl  # For OpenCL
pip install cupy-cuda12x  # For NVIDIA CUDA
```

## Usage Example

```python
from engine.performance.optimizer import PerformanceOptimizer, LeakyBucketRateLimiter
from engine.attack.engine import AttackEngine
from engine.tui.dashboard import create_tactical_dashboard
from engine.kali.integration import KaliIntegration
import httpx
import asyncio

async def main():
    # Optimize environment
    optimizer = PerformanceOptimizer()
    optimizer.optimize_environment()
    
    # Create rate limiter
    limiter = LeakyBucketRateLimiter(rate=100.0, capacity=200.0)
    
    # Initialize Kali integration
    kali = KaliIntegration()
    
    # Create attack engine
    async with httpx.AsyncClient(verify=False) as client:
        engine = AttackEngine("http://target.com", attack_mode="aggressive", session=client)
        
        # Create TUI dashboard
        dashboard = create_tactical_dashboard(engine)
        
        # Run attack with dashboard
        results = await engine.attack()
        
        # Save session
        kali.save_session(
            results['session_id'],
            results['target'],
            results['attack_mode'],
            results['findings'],
            results
        )
        
        # Notify critical findings
        for finding in results['findings']:
            if finding.get('confidence') == 'high':
                kali.notify_critical_finding(finding)

asyncio.run(main())
```

## Result

Dengkis is now a **high-performance, tactical offensive security engine** optimized for Kali Linux with:

- ✅ Kernel-level performance tuning
- ✅ Zero-copy processing
- ✅ GPU acceleration support
- ✅ Tactical TUI dashboard
- ✅ Kali native integration
- ✅ One-click PoC generation
- ✅ Auto-trigger evasion

**Maximum speed. Maximum impact. Tactical aesthetic.**
