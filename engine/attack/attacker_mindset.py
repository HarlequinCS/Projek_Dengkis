"""
ATTACKER MINDSET - Enhanced Reporting with Attacker Insights
Converts technical data into actionable red team intelligence.
"""
from typing import Dict, List, List
from datetime import datetime


class AttackerMindset:
    """
    Intelligence officer that generates attacker-focused insights.
    System Prompt: "You are the Dengkis Intelligence Officer."
    """
    
    def __init__(self):
        self.insights: List[Dict] = []
    
    def generate_attacker_insight(self, finding: Dict) -> Dict:
        """
        Generate attacker insight block for a finding.
        System Prompt: "For every finding, generate an 'Attacker Insight' block"
        
        Args:
            finding: Vulnerability finding dictionary
            
        Returns:
            Attacker insight dictionary
        """
        category = finding.get('category', 'unknown')
        confidence = finding.get('confidence', 'low')
        endpoint = finding.get('endpoint', '')
        parameter = finding.get('parameter', '')
        payload = finding.get('payload', '')
        method = finding.get('method', 'GET')
        
        # Determine kill chain stage
        kill_chain_stage = self._determine_kill_chain_stage(category, finding)
        
        # Determine complexity vs impact
        complexity, impact = self._assess_complexity_impact(category, confidence, finding)
        
        # Generate curl command
        curl_command = self._generate_curl_command(endpoint, parameter, payload, method)
        
        insight = {
            'finding_id': finding.get('id', ''),
            'kill_chain_stage': kill_chain_stage,
            'complexity': complexity,
            'impact': impact,
            'complexity_vs_impact': f"{complexity} Effort / {impact} Impact",
            'curl_command': curl_command,
            'attacker_value': self._assess_attacker_value(category, confidence),
            'exploitation_tips': self._generate_exploitation_tips(category, finding),
            'defensive_implication': self._get_defensive_implication(category),
            'generated_at': datetime.utcnow().isoformat()
        }
        
        self.insights.append(insight)
        return insight
    
    def _determine_kill_chain_stage(self, category: str, finding: Dict) -> str:
        """
        Identify kill chain stage.
        System Prompt: "Identify if this bug is for Initial Access, Persistence, or Privilege Escalation"
        """
        category_lower = category.lower()
        
        if 'auth' in category_lower or 'bypass' in category_lower:
            return 'Initial Access'
        elif 'sql' in category_lower:
            return 'Collection'
        elif 'command' in category_lower or 'ssti' in category_lower or 'rce' in category_lower:
            return 'Execution'
        elif 'lfi' in category_lower:
            return 'Collection'
        elif 'xss' in category_lower:
            return 'Execution'
        elif 'redirect' in category_lower:
            return 'Initial Access'
        elif 'mass' in category_lower or 'assignment' in category_lower:
            return 'Privilege Escalation'
        else:
            return 'Reconnaissance'
    
    def _assess_complexity_impact(self, category: str, confidence: str, finding: Dict) -> tuple:
        """
        Rate complexity vs impact.
        System Prompt: "Rate how easy the exploit is to trigger versus how much damage it does"
        """
        category_lower = category.lower()
        
        # Determine complexity
        if confidence == 'high' and finding.get('vulnerable', False):
            complexity = 'Low'
        elif confidence == 'medium':
            complexity = 'Medium'
        else:
            complexity = 'High'
        
        # Determine impact
        if 'rce' in category_lower or 'command' in category_lower:
            impact = 'Critical'
        elif 'sql' in category_lower:
            impact = 'High'
        elif 'ssti' in category_lower:
            impact = 'High'
        elif 'lfi' in category_lower:
            impact = 'High'
        elif 'auth' in category_lower or 'bypass' in category_lower:
            impact = 'Critical'
        elif 'xss' in category_lower:
            impact = 'Medium'
        elif 'redirect' in category_lower:
            impact = 'Medium'
        else:
            impact = 'Low'
        
        return complexity, impact
    
    def _generate_curl_command(self, endpoint: str, parameter: str, payload: str, method: str) -> str:
        """
        Generate exact curl command to reproduce exploit.
        System Prompt: "Provide the exact curl command needed to reproduce the exploit instantly"
        """
        if method.upper() == 'GET':
            # URL encode payload
            import urllib.parse
            encoded_payload = urllib.parse.quote(payload)
            if '?' in endpoint:
                url = f"{endpoint}&{parameter}={encoded_payload}"
            else:
                url = f"{endpoint}?{parameter}={encoded_payload}"
            return f"curl -X GET '{url}'"
        else:
            # POST request
            import urllib.parse
            encoded_payload = urllib.parse.quote(payload)
            return f"curl -X POST '{endpoint}' -d '{parameter}={encoded_payload}'"
    
    def _assess_attacker_value(self, category: str, confidence: str) -> str:
        """Assess value to attackers."""
        category_lower = category.lower()
        
        if 'rce' in category_lower or 'command' in category_lower:
            return 'Critical - Direct system compromise'
        elif 'sql' in category_lower:
            return 'High - Data exfiltration, potential RCE'
        elif 'auth' in category_lower:
            return 'Critical - Bypass authentication'
        elif 'ssti' in category_lower:
            return 'High - Server-side code execution'
        elif 'lfi' in category_lower:
            return 'High - File system access'
        elif confidence == 'high':
            return 'High - Exploitable vulnerability'
        else:
            return 'Medium - Requires further testing'
    
    def _generate_exploitation_tips(self, category: str, finding: Dict) -> List[str]:
        """Generate exploitation tips."""
        tips = []
        category_lower = category.lower()
        
        if 'sql' in category_lower:
            tips.append("Try UNION SELECT to extract data")
            tips.append("Use time-based payloads for blind SQLi")
            tips.append("Attempt to read /etc/passwd via LOAD_FILE()")
        elif 'xss' in category_lower:
            tips.append("Test for stored XSS by submitting to forms")
            tips.append("Check if payload is reflected in different contexts")
            tips.append("Try DOM-based XSS if reflected XSS fails")
        elif 'command' in category_lower or 'rce' in category_lower:
            tips.append("Execute 'whoami' to confirm user context")
            tips.append("Try 'id' to check privileges")
            tips.append("Attempt to read /etc/passwd for user enumeration")
        elif 'lfi' in category_lower:
            tips.append("Try PHP wrappers: php://filter/convert.base64-encode/resource=index.php")
            tips.append("Attempt to read .env files for credentials")
            tips.append("Check for log poisoning opportunities")
        elif 'ssti' in category_lower:
            tips.append("Confirm template engine with {{7*7}}")
            tips.append("Try {{config}} to dump configuration")
            tips.append("Attempt RCE with template-specific payloads")
        
        return tips
    
    def _get_defensive_implication(self, category: str) -> str:
        """Get defensive implication."""
        category_lower = category.lower()
        
        implications = {
            'sql': 'Implement parameterized queries. Use prepared statements. Input validation required.',
            'xss': 'Implement output encoding. Use Content Security Policy. Input sanitization required.',
            'command': 'Input validation critical. Use whitelist approach. Avoid shell execution.',
            'ssti': 'Sanitize template inputs. Use sandboxed templates. Avoid user-controlled templates.',
            'lfi': 'Path validation required. Use whitelist for file access. Avoid user-controlled paths.',
            'auth': 'Review authentication logic. Implement rate limiting. Use strong session management.',
        }
        
        for key, value in implications.items():
            if key in category_lower:
                return value
        
        return 'Security control review required. Implement input validation and output encoding.'
    
    def get_insights(self) -> List[Dict]:
        """Get all attacker insights."""
        return self.insights
    
    def generate_intelligence_report(self, findings: List[Dict]) -> Dict:
        """Generate comprehensive intelligence report."""
        insights = []
        for finding in findings:
            insight = self.generate_attacker_insight(finding)
            insights.append(insight)
        
        return {
            'report_type': 'attacker_intelligence',
            'generated_at': datetime.utcnow().isoformat(),
            'total_findings': len(findings),
            'insights': insights,
            'kill_chain_distribution': self._analyze_kill_chain_distribution(insights),
            'complexity_impact_matrix': self._analyze_complexity_impact(insights)
        }
    
    def _analyze_kill_chain_distribution(self, insights: List[Dict]) -> Dict:
        """Analyze kill chain stage distribution."""
        distribution = {}
        for insight in insights:
            stage = insight.get('kill_chain_stage', 'Unknown')
            distribution[stage] = distribution.get(stage, 0) + 1
        return distribution
    
    def _analyze_complexity_impact(self, insights: List[Dict]) -> Dict:
        """Analyze complexity vs impact matrix."""
        matrix = {}
        for insight in insights:
            key = f"{insight.get('complexity')} / {insight.get('impact')}"
            matrix[key] = matrix.get(key, 0) + 1
        return matrix
