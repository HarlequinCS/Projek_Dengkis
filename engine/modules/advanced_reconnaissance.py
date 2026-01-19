"""
Advanced reconnaissance modules for PROJEK DENGKIS.
Focuses on behavioral analysis and response pattern recognition without exploitation.
"""
from typing import Dict, List, Optional
from datetime import datetime


class BehavioralAnalyzer:
    """
    Analyzes behavioral characteristics of target systems through
    response observation and pattern recognition.
    """
    
    def __init__(self):
        self.behavioral_profiles: Dict[str, Dict] = {}
        self.response_history: List[Dict] = []
    
    def analyze_target_behavior(self, target: str, responses: List[Dict]) -> Dict:
        """
        Perform behavioral analysis of target system based on observed responses.
        
        Args:
            target: Target identifier
            responses: List of response dictionaries from target
            
        Returns:
            Dictionary containing behavioral analysis results
        """
        behavioral_analysis = {
            "target": target,
            "analysis_timestamp": datetime.utcnow().isoformat(),
            "response_count": len(responses),
            "behavioral_patterns": {},
            "system_characteristics": {},
            "anomalies_detected": []
        }
        
        # Analyze response patterns
        behavioral_analysis["behavioral_patterns"] = self._extract_patterns(responses)
        
        # Identify system characteristics
        behavioral_analysis["system_characteristics"] = self._identify_characteristics(responses)
        
        # Detect anomalies
        behavioral_analysis["anomalies_detected"] = self._detect_anomalies(responses)
        
        # Store behavioral profile
        self.behavioral_profiles[target] = behavioral_analysis
        
        return behavioral_analysis
    
    def recognize_response_patterns(self, responses: List[Dict]) -> Dict:
        """
        Recognize response patterns that may indicate potential vulnerabilities
        through indirect observation rather than exploitation.
        
        Args:
            responses: List of response dictionaries
            
        Returns:
            Dictionary containing recognized patterns
        """
        patterns = {
            "error_message_patterns": [],
            "timing_patterns": {},
            "header_patterns": [],
            "status_code_patterns": {},
            "content_patterns": []
        }
        
        for response in responses:
            # Extract error message patterns
            if response.get("error_message"):
                patterns["error_message_patterns"].append({
                    "message": response["error_message"],
                    "type": self._classify_error_message(response["error_message"])
                })
            
            # Extract timing patterns
            if response.get("response_time"):
                if "response_times" not in patterns["timing_patterns"]:
                    patterns["timing_patterns"]["response_times"] = []
                patterns["timing_patterns"]["response_times"].append(response["response_time"])
            
            # Extract header patterns
            if response.get("headers"):
                patterns["header_patterns"].extend(response["headers"])
        
        # Calculate timing statistics
        if patterns["timing_patterns"].get("response_times"):
            times = patterns["timing_patterns"]["response_times"]
            patterns["timing_patterns"]["average"] = sum(times) / len(times)
            patterns["timing_patterns"]["min"] = min(times)
            patterns["timing_patterns"]["max"] = max(times)
        
        return patterns
    
    def detect_configuration_anomalies(self, target: str, configurations: Dict) -> List[Dict]:
        """
        Detect configuration anomalies by comparing against standard security practices.
        
        Args:
            target: Target identifier
            configurations: Dictionary of observed configurations
            
        Returns:
            List of detected configuration anomalies
        """
        anomalies = []
        
        # Check for non-standard configurations
        standard_configs = {
            "security_headers": ["X-Frame-Options", "X-Content-Type-Options", "Strict-Transport-Security"],
            "encryption": ["TLS 1.2+", "Strong cipher suites"],
            "authentication": ["Multi-factor authentication", "Strong password policy"]
        }
        
        observed_headers = configurations.get("headers", [])
        missing_headers = [h for h in standard_configs["security_headers"] if h not in observed_headers]
        
        for missing in missing_headers:
            anomalies.append({
                "type": "missing_security_header",
                "header": missing,
                "severity": "medium",
                "description": f"Missing standard security header: {missing}"
            })
        
        return anomalies
    
    def assess_compliance_deviations(self, target: str, compliance_checks: Dict) -> Dict:
        """
        Assess compliance deviations by comparing observed characteristics
        against security standards and best practices.
        
        Args:
            target: Target identifier
            compliance_checks: Dictionary of compliance check results
            
        Returns:
            Dictionary containing compliance deviation assessment
        """
        deviation_assessment = {
            "target": target,
            "standards_checked": compliance_checks.get("standards", []),
            "deviations_found": [],
            "compliance_score": 1.0,
            "recommendations": []
        }
        
        # Check each standard for deviations
        for standard, checks in compliance_checks.get("checks", {}).items():
            for check_name, check_result in checks.items():
                if not check_result.get("compliant", False):
                    deviation_assessment["deviations_found"].append({
                        "standard": standard,
                        "check": check_name,
                        "deviation": check_result.get("deviation_description"),
                        "severity": check_result.get("severity", "unknown")
                    })
                    deviation_assessment["compliance_score"] -= 0.1
        
        deviation_assessment["compliance_score"] = max(0.0, deviation_assessment["compliance_score"])
        
        return deviation_assessment
    
    def evaluate_security_posture(self, target: str, findings: Dict) -> Dict:
        """
        Evaluate security posture based on observable characteristics
        and configuration analysis.
        
        Args:
            target: Target identifier
            findings: Dictionary of assessment findings
            
        Returns:
            Dictionary containing security posture evaluation
        """
        posture_evaluation = {
            "target": target,
            "overall_posture": "unknown",
            "strength_indicators": [],
            "weakness_indicators": [],
            "posture_score": 0.0,
            "comparison_to_baseline": {}
        }
        
        # Analyze findings for posture indicators
        anomalies = findings.get("anomalies", [])
        compliance_gaps = findings.get("compliance_gaps", [])
        
        # Calculate posture score
        total_issues = len(anomalies) + len(compliance_gaps)
        if total_issues == 0:
            posture_evaluation["posture_score"] = 1.0
            posture_evaluation["overall_posture"] = "strong"
        elif total_issues < 3:
            posture_evaluation["posture_score"] = 0.7
            posture_evaluation["overall_posture"] = "moderate"
        elif total_issues < 6:
            posture_evaluation["posture_score"] = 0.5
            posture_evaluation["overall_posture"] = "weak"
        else:
            posture_evaluation["posture_score"] = 0.3
            posture_evaluation["overall_posture"] = "very_weak"
        
        # Classify indicators
        for anomaly in anomalies:
            if anomaly.get("severity") in ["critical", "high"]:
                posture_evaluation["weakness_indicators"].append(anomaly)
            else:
                posture_evaluation["strength_indicators"].append({
                    "type": "low_severity",
                    "finding": anomaly
                })
        
        return posture_evaluation
    
    def _extract_patterns(self, responses: List[Dict]) -> Dict:
        """Extract behavioral patterns from responses."""
        return {
            "response_consistency": "unknown",
            "error_patterns": [],
            "timing_patterns": {}
        }
    
    def _identify_characteristics(self, responses: List[Dict]) -> Dict:
        """Identify system characteristics from responses."""
        return {
            "technologies": [],
            "security_controls": [],
            "configuration_indicators": []
        }
    
    def _detect_anomalies(self, responses: List[Dict]) -> List[Dict]:
        """Detect anomalies in response patterns."""
        anomalies = []
        
        # Check for unusual response times
        response_times = [r.get("response_time", 0) for r in responses if r.get("response_time")]
        if response_times:
            avg_time = sum(response_times) / len(response_times)
            for i, time in enumerate(response_times):
                if time > avg_time * 3:  # Significantly slower
                    anomalies.append({
                        "type": "unusual_response_time",
                        "index": i,
                        "response_time": time,
                        "severity": "low"
                    })
        
        return anomalies
    
    def _classify_error_message(self, error_message: str) -> str:
        """Classify error message type for pattern recognition."""
        error_lower = error_message.lower()
        
        if "sql" in error_lower or "database" in error_lower:
            return "database_error"
        elif "permission" in error_lower or "access" in error_lower:
            return "authorization_error"
        elif "not found" in error_lower or "404" in error_lower:
            return "resource_not_found"
        elif "timeout" in error_lower:
            return "timeout_error"
        else:
            return "generic_error"
