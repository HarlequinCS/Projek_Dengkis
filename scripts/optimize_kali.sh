#!/bin/bash
# Auto-optimization script for Kali Linux
# Sets kernel-level parameters for aggressive scanning

echo "[DENGKIS] Applying kernel-level optimizations..."

# Set ulimit for max file descriptors
ulimit -n 65535
echo "[DENGKIS] Set ulimit -n 65535"

# TCP tuning (requires root)
if [ "$EUID" -eq 0 ]; then
    sysctl -w net.ipv4.tcp_max_syn_backlog=8192 > /dev/null 2>&1
    sysctl -w net.netfilter.nf_conntrack_max=262144 > /dev/null 2>&1
    sysctl -w net.ipv4.tcp_fastopen=3 > /dev/null 2>&1
    echo "[DENGKIS] Applied TCP kernel tuning"
else
    echo "[DENGKIS] Warning: TCP tuning requires root. Run with sudo for full optimization."
fi

echo "[DENGKIS] Optimization complete."
