"""
Advanced behavioral analysis engine for PROJEK DENGKIS.
Extracts maximum information from target systems through response pattern analysis.
"""
import re
import asyncio
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import statistics
from collections import defaultdict, Counter
import difflib
import hashlib


class BehavioralAnalyzer:
    """
    Advanced behavioral analysis engine designed to extract maximum
    information from target systems through response pattern analysis.
    """
    
    def __init__(self):
        self.response_patterns: Dict[str, List[Dict]] = {}
        self.behavioral_signatures: Dict[str, Dict] = {}
        self.anomaly_thresholds = {
            'response_time': 2.0,  # Standard deviations
            'header_count': 1.5,
            'error_rate': 0.1,
            'redirect_rate': 0.2
        }
    
    async def analyze_target_behavior(self, target: str, responses: List[Dict]) -> Dict:
        """
        Analyze target behavior across multiple response dimensions to
        identify patterns, anomalies, and potential vulnerabilities.
        
        Args:
            target: Target URL or IP
            responses: List of response dictionaries
            
        Returns:
            Dict containing comprehensive behavioral analysis
        """
        behavioral_analysis = {
            "target": target,
            "analysis_timestamp": datetime.utcnow().isoformat(),
            "response_count": len(responses),
            "behavioral_patterns": {},
            "system_characteristics": {},
            "anomalies_detected": [],
            "risk_indicators": []
        }
        
        if not responses:
            return behavioral_analysis
        
        # Analyze response patterns
        behavioral_analysis["behavioral_patterns"] = await self.recognize_response_patterns(responses)
        
        # Identify system characteristics
        behavioral_analysis["system_characteristics"] = await self._identify_characteristics(responses)
        
        # Detect anomalies
        behavioral_analysis["anomalies_detected"] = await self._detect_anomalies(responses)
        
        # Identify risk indicators
        behavioral_analysis["risk_indicators"] = await self._identify_risk_indicators(responses)
        
        # Store behavioral profile
        self.behavioral_signatures[target] = behavioral_analysis
        
        return behavioral_analysis
    
    async def recognize_response_patterns(self, responses: List[Dict]) -> Dict:
        """
        Recognize response patterns that may indicate underlying
        technologies, configurations, or potential vulnerabilities.
        
        Args:
            responses: List of response dictionaries
            
        Returns:
            Dict containing pattern recognition results
        """
        patterns = {
            "error_message_patterns": [],
            "timing_patterns": {},
            "header_patterns": [],
            "status_code_patterns": {},
            "content_patterns": [],
            "redirect_patterns": []
        }
        
        response_times = []
        status_codes = []
        headers_all = []
        
        for response in responses:
            # Extract error message patterns
            if response.get("error_message"):
                error_type = self._classify_error_message(response["error_message"])
                patterns["error_message_patterns"].append({
                    "message": response["error_message"],
                    "type": error_type,
                    "severity": self._assess_error_severity(error_type)
                })
            
            # Extract timing patterns
            if response.get("response_time"):
                response_times.append(response["response_time"])
            
            # Extract status codes
            if response.get("status_code"):
                status_codes.append(response["status_code"])
            
            # Extract header patterns
            if response.get("headers"):
                headers_all.extend(response["headers"].keys())
            
            # Extract redirect patterns
            if response.get("redirect_location"):
                patterns["redirect_patterns"].append({
                    "source": response.get("url"),
                    "destination": response["redirect_location"],
                    "type": "redirect"
                })
        
        # Analyze timing patterns
        if response_times:
            patterns["timing_patterns"] = {
                "average": statistics.mean(response_times),
                "median": statistics.median(response_times),
                "min": min(response_times),
                "max": max(response_times),
                "std_dev": statistics.stdev(response_times) if len(response_times) > 1 else 0,
                "inconsistent": statistics.stdev(response_times) > statistics.mean(response_times) * 0.5 if response_times else False
            }
        
        # Analyze status code patterns
        if status_codes:
            status_counter = Counter(status_codes)
            patterns["status_code_patterns"] = {
                "distribution": dict(status_counter),
                "success_rate": len([s for s in status_codes if 200 <= s < 300]) / len(status_codes),
                "error_rate": len([s for s in status_codes if s >= 400]) / len(status_codes)
            }
        
        # Analyze header patterns
        if headers_all:
            header_counter = Counter(headers_all)
            patterns["header_patterns"] = [
                {"header": header, "frequency": count}
                for header, count in header_counter.most_common(10)
            ]
        
        return patterns
    
    async def detect_configuration_anomalies(self, target: str, configurations: Dict) -> List[Dict]:
        """
        Detect configuration anomalies by comparing against known
        standards and identifying deviations.
        
        Args:
            target: Target URL or IP
            configurations: Configuration information
            
        Returns:
            List of detected anomalies
        """
        anomalies = []
        
        # Check for missing security headers
        standard_headers = [
            "X-Frame-Options", "X-Content-Type-Options",
            "Strict-Transport-Security", "Content-Security-Policy"
        ]
        
        observed_headers = configurations.get("headers", [])
        if isinstance(observed_headers, dict):
            observed_headers = list(observed_headers.keys())
        
        missing_headers = [h for h in standard_headers if h not in observed_headers]
        for header in missing_headers:
            anomalies.append({
                "type": "missing_security_header",
                "header": header,
                "severity": "medium",
                "description": f"Missing standard security header: {header}",
                "recommendation": f"Implement {header} header"
            })
        
        # Check for weak TLS configuration
        if configurations.get("tls_version"):
            tls_version = configurations["tls_version"]
            if tls_version not in ["1.2", "1.3"]:
                anomalies.append({
                    "type": "weak_tls_configuration",
                    "tls_version": tls_version,
                    "severity": "high",
                    "description": f"Outdated TLS version: {tls_version}",
                    "recommendation": "Upgrade to TLS 1.2 or higher"
                })
        
        # Check for debug mode
        if configurations.get("debug_mode_enabled"):
            anomalies.append({
                "type": "debug_mode_enabled",
                "severity": "high",
                "description": "Debug mode enabled in production",
                "recommendation": "Disable debug mode in production"
            })
        
        # Check for information disclosure
        server_header = configurations.get("server", "")
        if server_header and len(server_header.split("/")) == 2:
            # Server version disclosure
            anomalies.append({
                "type": "version_disclosure",
                "server": server_header,
                "severity": "low",
                "description": "Server version disclosed in headers",
                "recommendation": "Suppress server version information"
            })
        
        return anomalies
    
    async def assess_compliance_deviations(self, target: str, compliance_checks: Dict) -> Dict:
        """
        Assess compliance deviations by comparing against security
        standards and identifying gaps.
        
        Args:
            target: Target URL or IP
            compliance_checks: Compliance check specifications
            
        Returns:
            Dict containing compliance assessment
        """
        deviation_assessment = {
            "target": target,
            "assessment_timestamp": datetime.utcnow().isoformat(),
            "standards_checked": compliance_checks.get("standards", []),
            "deviations_found": [],
            "compliance_score": 1.0,
            "recommendations": []
        }
        
        checks = compliance_checks.get("checks", {})
        
        # Check each standard for deviations
        for standard, check_results in checks.items():
            for check_name, check_result in check_results.items():
                if not check_result.get("compliant", False):
                    deviation = {
                        "standard": standard,
                        "check": check_name,
                        "deviation": check_result.get("deviation_description"),
                        "severity": check_result.get("severity", "unknown"),
                        "impact": check_result.get("impact", "unknown")
                    }
                    deviation_assessment["deviations_found"].append(deviation)
                    deviation_assessment["compliance_score"] -= 0.1
        
        deviation_assessment["compliance_score"] = max(0.0, deviation_assessment["compliance_score"])
        
        # Generate recommendations
        for deviation in deviation_assessment["deviations_found"]:
            deviation_assessment["recommendations"].append({
                "deviation": deviation["check"],
                "recommendation": f"Address {deviation['standard']} compliance gap: {deviation['deviation']}"
            })
        
        return deviation_assessment
    
    async def evaluate_security_posture(self, target: str, findings: Dict) -> Dict:
        """
        Evaluate security posture based on behavioral analysis,
        configuration assessment, and compliance checks.
        
        Args:
            target: Target URL or IP
            findings: Assessment findings
            
        Returns:
            Dict containing security posture evaluation
        """
        posture_evaluation = {
            "target": target,
            "evaluation_timestamp": datetime.utcnow().isoformat(),
            "overall_posture": "unknown",
            "strength_indicators": [],
            "weakness_indicators": [],
            "posture_score": 0.0,
            "comparison_to_baseline": {}
        }
        
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
            severity = anomaly.get("severity", "medium").lower()
            if severity in ["critical", "high"]:
                posture_evaluation["weakness_indicators"].append(anomaly)
            else:
                posture_evaluation["strength_indicators"].append({
                    "type": "low_severity_issue",
                    "finding": anomaly
                })
        
        return posture_evaluation
    
    async def generate_behavioral_fingerprint(self, target: str, responses: List[Dict]) -> Dict:
        """
        Generate comprehensive behavioral fingerprint by analyzing
        multiple response dimensions and characteristics.
        
        Args:
            target: Target URL or IP
            responses: List of response dictionaries
            
        Returns:
            Dict containing behavioral fingerprint
        """
        fingerprint = {
            "target": target,
            "fingerprint_timestamp": datetime.utcnow().isoformat(),
            "response_characteristics": {},
            "technologies": [],
            "security_controls": [],
            "behavioral_signatures": {},
            "consistency_score": 0.0
        }
        
        if not responses:
            return fingerprint
        
        # Analyze response characteristics
        response_times = [r.get("response_time", 0) for r in responses if r.get("response_time")]
        if response_times:
            fingerprint["response_characteristics"] = {
                "average_response_time": statistics.mean(response_times),
                "median_response_time": statistics.median(response_times),
                "min_response_time": min(response_times),
                "max_response_time": max(response_times),
                "response_time_consistency": statistics.stdev(response_times) < statistics.mean(response_times) * 0.3 if response_times else False
            }
        
        # Extract technologies
        servers = [r.get("server", "") for r in responses if r.get("server")]
        fingerprint["technologies"] = list(set([s for s in servers if s]))
        
        # Extract security controls
        all_headers = []
        for response in responses:
            if response.get("headers"):
                if isinstance(response["headers"], dict):
                    all_headers.extend(response["headers"].keys())
                elif isinstance(response["headers"], list):
                    all_headers.extend(response["headers"])
        
        security_headers = [
            "X-Frame-Options", "X-Content-Type-Options",
            "Strict-Transport-Security", "Content-Security-Policy",
            "X-XSS-Protection", "Referrer-Policy"
        ]
        fingerprint["security_controls"] = [h for h in security_headers if h in all_headers]
        
        # Calculate consistency score
        status_codes = [r.get("status_code") for r in responses if r.get("status_code")]
        if status_codes:
            unique_statuses = set(status_codes)
            fingerprint["consistency_score"] = 1.0 - (len(unique_statuses) / len(status_codes)) if status_codes else 0.0
        
        # Generate behavioral signatures
        fingerprint["behavioral_signatures"] = {
            "error_pattern": self._generate_error_signature(responses),
            "redirect_pattern": self._generate_redirect_signature(responses),
            "timing_pattern": self._generate_timing_signature(responses)
        }
        
        return fingerprint
    
    async def _identify_characteristics(self, responses: List[Dict]) -> Dict:
        """Identify system characteristics from responses."""
        characteristics = {
            "technologies": [],
            "security_controls": [],
            "configuration_indicators": []
        }
        
        # Extract technologies
        servers = [r.get("server", "") for r in responses if r.get("server")]
        characteristics["technologies"] = list(set([s for s in servers if s]))
        
        # Extract security controls
        all_headers = []
        for response in responses:
            if response.get("headers"):
                if isinstance(response["headers"], dict):
                    all_headers.extend(response["headers"].keys())
        
        security_headers = [
            "X-Frame-Options", "X-Content-Type-Options",
            "Strict-Transport-Security", "Content-Security-Policy"
        ]
        characteristics["security_controls"] = [h for h in security_headers if h in all_headers]
        
        return characteristics
    
    async def _detect_anomalies(self, responses: List[Dict]) -> List[Dict]:
        """Detect anomalies in response patterns."""
        anomalies = []
        
        # Check for unusual response times
        response_times = [r.get("response_time") for r in responses if r.get("response_time")]
        if response_times and len(response_times) > 1:
            avg_time = statistics.mean(response_times)
            std_dev = statistics.stdev(response_times)
            
            for i, time in enumerate(response_times):
                if time > avg_time + (self.anomaly_thresholds['response_time'] * std_dev):
                    anomalies.append({
                        "type": "unusual_response_time",
                        "index": i,
                        "response_time": time,
                        "average": avg_time,
                        "deviation": time - avg_time,
                        "severity": "low"
                    })
        
        # Check for high error rate
        status_codes = [r.get("status_code") for r in responses if r.get("status_code")]
        if status_codes:
            error_count = len([s for s in status_codes if s >= 400])
            error_rate = error_count / len(status_codes)
            
            if error_rate > self.anomaly_thresholds['error_rate']:
                anomalies.append({
                    "type": "high_error_rate",
                    "error_rate": error_rate,
                    "total_errors": error_count,
                    "severity": "medium"
                })
        
        return anomalies
    
    async def _identify_risk_indicators(self, responses: List[Dict]) -> List[Dict]:
        """Identify risk indicators from responses."""
        risk_indicators = []
        
        # Check for information disclosure
        for response in responses:
            if response.get("status_code", 0) >= 400:
                if response.get("error_message"):
                    if any(keyword in response["error_message"].lower() for keyword in ["path", "file", "trace"]):
                        risk_indicators.append({
                            "type": "information_disclosure",
                            "severity": "medium",
                            "description": "Potential information disclosure in error message"
                        })
        
        # Check for missing security headers
        for response in responses:
            if response.get("headers"):
                headers = response["headers"] if isinstance(response["headers"], dict) else {}
                if "X-Frame-Options" not in headers and "Strict-Transport-Security" not in headers:
                    risk_indicators.append({
                        "type": "missing_security_headers",
                        "severity": "low",
                        "description": "Missing security headers"
                    })
                    break
        
        return risk_indicators
    
    def _classify_error_message(self, error_message: str) -> str:
        """Classify error message type."""
        error_lower = error_message.lower()
        
        if any(keyword in error_lower for keyword in ["sql", "database", "mysql", "postgres"]):
            return "database_error"
        elif any(keyword in error_lower for keyword in ["permission", "access", "unauthorized"]):
            return "authorization_error"
        elif any(keyword in error_lower for keyword in ["not found", "404"]):
            return "resource_not_found"
        elif any(keyword in error_lower for keyword in ["timeout", "timed out"]):
            return "timeout_error"
        elif any(keyword in error_lower for keyword in ["internal server", "500"]):
            return "server_error"
        else:
            return "generic_error"
    
    def _assess_error_severity(self, error_type: str) -> str:
        """Assess severity of error type."""
        severity_map = {
            "database_error": "high",
            "authorization_error": "medium",
            "server_error": "medium",
            "timeout_error": "low",
            "resource_not_found": "low",
            "generic_error": "low"
        }
        return severity_map.get(error_type, "low")
    
    def _generate_error_signature(self, responses: List[Dict]) -> str:
        """Generate error pattern signature."""
        error_messages = [r.get("error_message", "") for r in responses if r.get("error_message")]
        if error_messages:
            signature = hashlib.md5("|".join(error_messages).encode()).hexdigest()[:8]
            return f"error_{signature}"
        return "no_errors"
    
    def _generate_redirect_signature(self, responses: List[Dict]) -> str:
        """Generate redirect pattern signature."""
        redirects = [r.get("redirect_location", "") for r in responses if r.get("redirect_location")]
        if redirects:
            signature = hashlib.md5("|".join(redirects).encode()).hexdigest()[:8]
            return f"redirect_{signature}"
        return "no_redirects"
    
    def _generate_timing_signature(self, responses: List[Dict]) -> str:
        """Generate timing pattern signature."""
        response_times = [r.get("response_time", 0) for r in responses if r.get("response_time")]
        if response_times:
            avg = statistics.mean(response_times)
            std_dev = statistics.stdev(response_times) if len(response_times) > 1 else 0
            signature = hashlib.md5(f"{avg}_{std_dev}".encode()).hexdigest()[:8]
            return f"timing_{signature}"
        return "no_timing"
