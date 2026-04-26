# Scripts

This directory contains utility scripts for PROJEK DENGKIS.

## optimize_kali.sh

Kernel-level optimization script for Kali Linux environments.

### Usage

```bash
# Run with user privileges (limited optimization)
./scripts/optimize_kali.sh

# Run with root privileges (full optimization)
sudo ./scripts/optimize_kali.sh
```

### What it does

- Sets `ulimit -n` to 65535 for maximum file descriptors
- Tunes TCP kernel parameters for aggressive scanning:
  - `net.ipv4.tcp_max_syn_backlog=8192`
  - `net.netfilter.nf_conntrack_max=262144`
  - `net.ipv4.tcp_fastopen=3`

### Requirements

- Kali Linux (or compatible Linux distribution)
- Root privileges for full TCP tuning (optional)

### Notes

- These optimizations are temporary and reset on reboot
- For permanent changes, add the sysctl settings to `/etc/sysctl.conf`
- Use only in authorized testing environments
