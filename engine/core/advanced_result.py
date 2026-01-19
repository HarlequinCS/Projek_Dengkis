"""
Advanced result generation and reporting for PROJEK DENGKIS assessments.
Provides comprehensive analysis of security posture without exploitation.
"""
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any


class AssessmentResult:
    """
    Comprehensive assessment result object with detailed analysis
    of security posture, compliance gaps, and attack surface.
    """
    
    def __init__(
        self,
        session_id: uuid.UUID,
        target: str,
        test_vectors: List[Dict],
        anomaly_indicators: List[Dict]
    ):
        self.session_id = session_id
        self.target = target
        self.test_vectors = test_vectors
        self.anomaly_indicators = anomaly_indicators
        self.security_posture: Dict = {}
        self.compliance_gaps: List[Dict] = []
        self.attack_surface_analysis: Dict = {}
        self.generated_at = datetime.utcnow().isoformat()
    
    def calculate_risk_amplification_factors(self) -> Dict:
        """
        Identify risk amplification factors to understand how minor issues
        could potentially become major problems under certain conditions.
        
        Returns:
            Dictionary containing risk amplification analysis
        """
        amplification_factors = {
            "factors_identified": [],
            "compound_risk_scenarios": [],
            "escalation_paths": [],
            "impact_analysis": {}
        }
        
        # Analyze anomalies for potential amplification
        for anomaly in self.anomaly_indicators:
            if anomaly.get("severity") == "low":
                amplification_factors["factors_identified"].append({
                    "anomaly": anomaly,
                    "amplification_potential": "medium",
                    "conditions": "Multiple low-severity issues combined"
                })
        
        return amplification_factors
    
    def assess_security_maturity(self) -> Dict:
        """
        Assess security maturity based on configuration and response patterns
        observed during assessment.
        
        Returns:
            Dictionary containing security maturity assessment
        """
        maturity_assessment = {
            "maturity_level": "unknown",
            "indicators": {
                "configuration_quality": 0.0,
                "security_control_implementation": 0.0,
                "incident_response_readiness": 0.0,
                "compliance_adherence": 0.0
            },
            "recommendations": [],
            "comparison_to_standards": {}
        }
        
        # Calculate maturity scores based on findings
        if len(self.compliance_gaps) == 0:
            maturity_assessment["indicators"]["compliance_adherence"] = 1.0
        else:
            maturity_assessment["indicators"]["compliance_adherence"] = max(
                0.0, 1.0 - (len(self.compliance_gaps) * 0.1)
            )
        
        # Determine overall maturity level
        avg_score = sum(maturity_assessment["indicators"].values()) / len(maturity_assessment["indicators"])
        if avg_score >= 0.8:
            maturity_assessment["maturity_level"] = "advanced"
        elif avg_score >= 0.6:
            maturity_assessment["maturity_level"] = "intermediate"
        elif avg_score >= 0.4:
            maturity_assessment["maturity_level"] = "basic"
        else:
            maturity_assessment["maturity_level"] = "initial"
        
        return maturity_assessment
    
    def integrate_threat_modeling(self, threat_model: Optional[Dict] = None) -> Dict:
        """
        Integrate threat modeling context for better understanding of findings.
        
        Args:
            threat_model: Optional threat model dictionary
            
        Returns:
            Dictionary containing threat modeling integration
        """
        threat_integration = {
            "threat_model_provided": threat_model is not None,
            "identified_threats": [],
            "attack_scenarios": [],
            "threat_prioritization": {},
            "mitigation_mapping": {}
        }
        
        # Map anomalies to threat scenarios
        for anomaly in self.anomaly_indicators:
            threat_integration["identified_threats"].append({
                "anomaly": anomaly,
                "potential_threat": self._map_anomaly_to_threat(anomaly),
                "likelihood": "unknown",
                "impact": anomaly.get("severity", "unknown")
            })
        
        return threat_integration
    
    def prioritize_remediation(self) -> List[Dict]:
        """
        Prioritize remediation based on exploitability and impact factors
        without actually exploiting vulnerabilities.
        
        Returns:
            List of prioritized remediation recommendations
        """
        remediation_items = []
        
        # Prioritize based on anomaly indicators
        for anomaly in self.anomaly_indicators:
            priority_score = self._calculate_remediation_priority(anomaly)
            remediation_items.append({
                "finding": anomaly,
                "priority_score": priority_score,
                "priority_level": self._score_to_priority(priority_score),
                "recommended_action": self._generate_remediation_action(anomaly),
                "estimated_effort": "unknown"
            })
        
        # Sort by priority score (highest first)
        remediation_items.sort(key=lambda x: x["priority_score"], reverse=True)
        
        return remediation_items
    
    def analyze_attack_surface(self) -> Dict:
        """
        Perform attack surface analysis based on system architecture
        and configuration without exploitation.
        
        Returns:
            Dictionary containing attack surface analysis
        """
        attack_surface = {
            "surface_area_score": 0.0,
            "entry_points_identified": [],
            "exposure_vectors": [],
            "security_controls_mapping": {},
            "hardening_opportunities": []
        }
        
        # Analyze test vectors for attack surface indicators
        for vector in self.test_vectors:
            if vector.get("exposed_service"):
                attack_surface["entry_points_identified"].append({
                    "type": vector.get("service_type"),
                    "location": vector.get("location"),
                    "exposure_level": "unknown"
                })
        
        # Calculate surface area score
        attack_surface["surface_area_score"] = len(attack_surface["entry_points_identified"]) * 0.1
        
        return attack_surface
    
    def to_dict(self) -> Dict:
        """Convert assessment result to dictionary format."""
        return {
            "session_id": str(self.session_id),
            "target": self.target,
            "generated_at": self.generated_at,
            "test_vectors_count": len(self.test_vectors),
            "anomaly_indicators_count": len(self.anomaly_indicators),
            "security_posture": self.security_posture,
            "compliance_gaps": self.compliance_gaps,
            "attack_surface_analysis": self.analyze_attack_surface(),
            "security_maturity": self.assess_security_maturity(),
            "risk_amplification": self.calculate_risk_amplification_factors()
        }
    
    def generate_recommendations(self) -> List[Dict]:
        """Generate prioritized remediation recommendations."""
        recommendations = []
        
        # Add prioritized remediations
        recommendations.extend(self.prioritize_remediation())
        
        # Add compliance gap remediations
        for gap in self.compliance_gaps:
            recommendations.append({
                "type": "compliance",
                "finding": gap,
                "recommended_action": f"Address compliance gap: {gap.get('type', 'unknown')}",
                "priority_level": "high"
            })
        
        return recommendations
    
    def _map_anomaly_to_threat(self, anomaly: Dict) -> str:
        """Map an anomaly indicator to a potential threat type."""
        anomaly_type = anomaly.get("type", "").lower()
        
        threat_mapping = {
            "configuration": "Misconfiguration exploitation",
            "authentication": "Credential compromise",
            "authorization": "Privilege escalation",
            "encryption": "Data interception",
            "input": "Input validation bypass"
        }
        
        for key, threat in threat_mapping.items():
            if key in anomaly_type:
                return threat
        
        return "General security weakness"
    
    def _calculate_remediation_priority(self, anomaly: Dict) -> float:
        """Calculate remediation priority score (0.0 to 1.0)."""
        base_score = 0.5
        
        # Adjust based on severity
        severity = anomaly.get("severity", "medium").lower()
        severity_multipliers = {
            "critical": 1.0,
            "high": 0.8,
            "medium": 0.6,
            "low": 0.4
        }
        base_score *= severity_multipliers.get(severity, 0.6)
        
        # Adjust based on exploitability indicators
        if anomaly.get("easily_exploitable"):
            base_score += 0.2
        
        # Adjust based on impact
        if anomaly.get("high_impact"):
            base_score += 0.2
        
        return min(1.0, base_score)
    
    def _score_to_priority(self, score: float) -> str:
        """Convert numeric priority score to priority level."""
        if score >= 0.8:
            return "critical"
        elif score >= 0.6:
            return "high"
        elif score >= 0.4:
            return "medium"
        else:
            return "low"
    
    def _generate_remediation_action(self, anomaly: Dict) -> str:
        """Generate recommended remediation action for an anomaly."""
        anomaly_type = anomaly.get("type", "unknown")
        
        action_templates = {
            "configuration": "Review and harden configuration settings",
            "authentication": "Strengthen authentication mechanisms",
            "authorization": "Implement proper access controls",
            "encryption": "Ensure proper encryption implementation",
            "input": "Implement input validation and sanitization"
        }
        
        for key, action in action_templates.items():
            if key in anomaly_type.lower():
                return action
        
        return "Review and address identified security issue"
