"""
Example plugin: Enhanced risk scoring.
"""
from typing import Dict, Optional
from engine.plugins.base import BasePlugin


class RiskScorerPlugin(BasePlugin):
    """Enhanced risk scoring plugin."""
    
    def __init__(self):
        super().__init__()
        self.name = "Enhanced Risk Scorer"
        self.version = "1.0.0"
    
    def initialize(self, config: Optional[Dict] = None) -> bool:
        """Initialize plugin."""
        self.config = config or {}
        self.severity_weights = {
            'critical': 1.0,
            'high': 0.7,
            'medium': 0.4,
            'low': 0.2
        }
        return True
    
    def execute(self, data: Dict) -> Dict:
        """
        Calculate enhanced risk score.
        
        Args:
            data: Assessment data dictionary
            
        Returns:
            Dictionary with enhanced risk scoring
        """
        findings = data.get('findings', [])
        
        # Calculate weighted risk score
        total_risk = 0.0
        for finding in findings:
            severity = finding.get('severity', 'low').lower()
            weight = self.severity_weights.get(severity, 0.2)
            total_risk += weight
        
        # Normalize to 0-1 range
        max_possible_risk = len(findings) * 1.0 if findings else 1.0
        enhanced_score = min(1.0, total_risk / max_possible_risk) if max_possible_risk > 0 else 0.0
        
        return {
            'enhanced_risk_score': enhanced_score,
            'risk_breakdown': {
                severity: len([f for f in findings if f.get('severity', '').lower() == severity])
                for severity in self.severity_weights.keys()
            }
        }
