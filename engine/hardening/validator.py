"""
Hardening and production readiness validation for PROJEK DENGKIS.
Validates environment, dependencies, and configuration for Kali Linux deployment.
"""
import sys
import platform
from typing import Dict, List, Optional
from pathlib import Path

from engine.logging.logger import get_logger


class EnvironmentValidator:
    """Validator for production environment readiness."""
    
    def __init__(self):
        self.logger = get_logger()
        self.checks: List[Dict] = []
    
    def validate_dependencies(self) -> Dict:
        """
        Validate all required dependencies are installed.
        
        Returns:
            Dictionary with validation results
        """
        results = {
            "all_installed": True,
            "missing": [],
            "installed": [],
            "warnings": []
        }
        
        required_deps = {
            "httpx": "httpx",
            "dnspython": "dns",
            "plotly": "plotly",
            "networkx": "networkx",
            "pandas": "pandas",
            "numpy": "numpy",
            "jinja2": "jinja2",
            "yaml": "yaml"
        }
        
        optional_deps = {
            "weasyprint": "weasyprint"
        }
        
        # Check required dependencies
        for dep_name, import_name in required_deps.items():
            try:
                __import__(import_name)
                results["installed"].append(dep_name)
            except ImportError:
                results["missing"].append(dep_name)
                results["all_installed"] = False
        
        # Check optional dependencies
        for dep_name, import_name in optional_deps.items():
            try:
                __import__(import_name)
                results["installed"].append(dep_name)
            except ImportError:
                results["warnings"].append(f"{dep_name} (optional) not installed")
        
        return results
    
    def validate_kali_compatibility(self) -> Dict:
        """
        Validate Kali Linux compatibility.
        
        Returns:
            Dictionary with compatibility check results
        """
        results = {
            "kali_detected": False,
            "linux_system": False,
            "python_version": sys.version_info[:2],
            "compatibility": "unknown",
            "recommendations": []
        }
        
        # Check if running on Linux
        results["linux_system"] = platform.system().lower() == "linux"
        
        # Check for Kali-specific indicators
        if Path("/etc/os-release").exists():
            try:
                with open("/etc/os-release", 'r') as f:
                    os_release = f.read()
                    if "kali" in os_release.lower():
                        results["kali_detected"] = True
                        results["compatibility"] = "excellent"
            except Exception:
                pass
        
        # Python version check
        if sys.version_info < (3, 8):
            results["recommendations"].append("Python 3.8+ recommended")
        else:
            results["compatibility"] = "good"
        
        # Recommendations
        if not results["linux_system"]:
            results["recommendations"].append("Production deployment recommended on Linux/Kali")
        
        return results
    
    def validate_configuration(self, config_path: Optional[str] = None) -> Dict:
        """
        Validate configuration files.
        
        Args:
            config_path: Optional path to configuration file
            
        Returns:
            Dictionary with validation results
        """
        from engine.config.manager import ConfigManager
        
        results = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        config_manager = ConfigManager(config_path or "config")
        
        try:
            config = config_manager.get_config()
            
            # Validate assessment config
            assessment = config.get("assessment", {})
            if assessment.get("timeout", 0) <= 0:
                results["errors"].append("Invalid timeout value")
                results["valid"] = False
            
            if assessment.get("max_concurrent_requests", 0) <= 0:
                results["errors"].append("Invalid max_concurrent_requests value")
                results["valid"] = False
            
            # Warnings
            if not assessment.get("ssl_verify", False):
                results["warnings"].append("SSL verification disabled - appropriate for assessment only")
            
        except Exception as e:
            results["errors"].append(f"Configuration validation failed: {e}")
            results["valid"] = False
        
        return results
    
    def run_all_checks(self) -> Dict:
        """
        Run all validation checks.
        
        Returns:
            Dictionary with all validation results
        """
        return {
            "dependencies": self.validate_dependencies(),
            "kali_compatibility": self.validate_kali_compatibility(),
            "configuration": self.validate_configuration()
        }
