"""
Example plugin: ISO 27001 compliance checker.
"""
from typing import Dict, Optional
from engine.plugins.base import BasePlugin


class ISO27001CompliancePlugin(BasePlugin):
    """ISO 27001 compliance checking plugin."""
    
    def __init__(self):
        super().__init__()
        self.name = "ISO 27001 Compliance"
        self.version = "1.0.0"
    
    def initialize(self, config: Optional[Dict] = None) -> bool:
        """Initialize plugin."""
        self.config = config or {}
        self.controls = [
            'A.9.4.2',  # Secure log-on procedures
            'A.14.2.1',  # Secure development policy
            'A.12.6.1',  # Management of technical vulnerabilities
        ]
        return True
    
    def execute(self, data: Dict) -> Dict:
        """
        Check ISO 27001 compliance.
        
        Args:
            data: Assessment data dictionary
            
        Returns:
            Dictionary with compliance check results
        """
        findings = data.get('findings', [])
        compliance_results = {
            'plugin': self.name,
            'framework': 'ISO 27001',
            'controls_checked': len(self.controls),
            'compliant_controls': [],
            'non_compliant_controls': [],
            'compliance_score': 0.0
        }
        
        # Check findings against controls
        security_issues = [f for f in findings if f.get('severity') in ['high', 'critical']]
        
        if len(security_issues) == 0:
            compliance_results['compliance_score'] = 1.0
            compliance_results['compliant_controls'] = self.controls
        else:
            compliance_results['compliance_score'] = max(0.0, 1.0 - (len(security_issues) * 0.2))
            compliance_results['non_compliant_controls'] = [
                {'control': c, 'issue': 'Security findings detected'} 
                for c in self.controls
            ]
        
        return {'iso27001_compliance': compliance_results}
