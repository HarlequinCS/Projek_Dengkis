"""
Advanced configuration management system for PROJEK DENGKIS.
Handles loading, validation, and merging of configuration files.
"""
import yaml
import json
import os
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
import logging
from dataclasses import dataclass, asdict, field
from enum import Enum


class ConfigFormat(Enum):
    YAML = 'yaml'
    JSON = 'json'
    ENV = 'env'


@dataclass
class AssessmentConfig:
    """Configuration data class for assessment parameters"""
    stealth_mode: bool = False
    max_concurrent_requests: int = 10
    timeout: float = 30.0
    retry_attempts: int = 3
    user_agent_rotation: bool = True
    ssl_verify: bool = False
    rate_limit: Optional[float] = None


@dataclass
class ReportingConfig:
    """Configuration data class for reporting parameters"""
    template_dir: str = 'templates'
    output_dir: str = 'reports'
    include_raw_data: bool = False
    generate_charts: bool = True
    export_formats: List[str] = field(default_factory=lambda: ['html', 'pdf', 'json'])


@dataclass
class VisualizationConfig:
    """Configuration data class for visualization parameters"""
    color_scheme: str = 'default'
    chart_theme: str = 'plotly_white'
    max_graph_nodes: int = 500
    timeline_aggregation: str = 'hour'
    include_3d_visualizations: bool = True


class ConfigManager:
    """
    Advanced configuration management system that handles loading,
    validation, and merging of configuration files from multiple sources.
    Supports environment-specific configurations and runtime overrides.
    """
    
    def __init__(self, config_dir: str = 'config'):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.config: Dict[str, Any] = {}
        self.logger = logging.getLogger(__name__)
        
        # Default configuration
        self.default_config = {
            'assessment': asdict(AssessmentConfig()),
            'reporting': asdict(ReportingConfig()),
            'visualization': asdict(VisualizationConfig())
        }
        
        # Load default config
        self.config = self.default_config.copy()
    
    def load_config(self, config_file: str, format: ConfigFormat = ConfigFormat.YAML) -> Dict:
        """
        Load configuration from specified file with format detection.
        
        Args:
            config_file: Configuration file path
            format: Configuration file format
            
        Returns:
            Loaded configuration dictionary
        """
        config_path = Path(config_file)
        
        if not config_path.is_absolute():
            config_path = self.config_dir / config_path
        
        if not config_path.exists():
            self.logger.warning(f"Config file not found: {config_path}")
            return {}
        
        try:
            if format == ConfigFormat.YAML:
                with open(config_path, 'r') as f:
                    loaded_config = yaml.safe_load(f) or {}
            elif format == ConfigFormat.JSON:
                with open(config_path, 'r') as f:
                    loaded_config = json.load(f)
            else:
                raise ValueError(f"Unsupported format: {format}")
            
            self.logger.info(f"Loaded config from {config_path}")
            return loaded_config
        
        except Exception as e:
            self.logger.error(f"Error loading config from {config_path}: {e}")
            return {}
    
    def merge_configs(self, *config_dicts: Dict) -> Dict:
        """
        Merge multiple configuration dictionaries with deep merge.
        
        Args:
            config_dicts: Configuration dictionaries to merge
            
        Returns:
            Merged configuration dictionary
        """
        merged = {}
        
        for config_dict in config_dicts:
            merged = self._deep_merge(merged, config_dict)
        
        return merged
    
    def _deep_merge(self, base: Dict, update: Dict) -> Dict:
        """Deep merge two dictionaries."""
        result = base.copy()
        
        for key, value in update.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def validate_config(self, config: Dict, schema: Optional[Dict] = None) -> bool:
        """
        Validate configuration against specified schema.
        
        Args:
            config: Configuration to validate
            schema: Validation schema (optional, uses default if not provided)
            
        Returns:
            True if valid, False otherwise
        """
        if schema is None:
            schema = self._get_default_schema()
        
        try:
            self._validate_recursive(config, schema)
            return True
        except ValueError as e:
            self.logger.error(f"Configuration validation failed: {e}")
            return False
    
    def _validate_recursive(self, config: Dict, schema: Dict, path: str = "") -> None:
        """Recursively validate configuration against schema."""
        for key, expected_type in schema.items():
            current_path = f"{path}.{key}" if path else key
            
            if key not in config:
                continue  # Optional fields
            
            value = config[key]
            
            if isinstance(expected_type, dict):
                if not isinstance(value, dict):
                    raise ValueError(f"Expected dict at {current_path}, got {type(value).__name__}")
                self._validate_recursive(value, expected_type, current_path)
            elif isinstance(expected_type, type):
                if not isinstance(value, expected_type):
                    raise ValueError(f"Expected {expected_type.__name__} at {current_path}, got {type(value).__name__}")
    
    def _get_default_schema(self) -> Dict:
        """Get default validation schema."""
        return {
            'assessment': {
                'stealth_mode': bool,
                'max_concurrent_requests': int,
                'timeout': float,
                'retry_attempts': int,
                'user_agent_rotation': bool,
                'ssl_verify': bool
            },
            'reporting': {
                'template_dir': str,
                'output_dir': str,
                'include_raw_data': bool,
                'generate_charts': bool,
                'export_formats': list
            },
            'visualization': {
                'color_scheme': str,
                'chart_theme': str,
                'max_graph_nodes': int,
                'timeline_aggregation': str,
                'include_3d_visualizations': bool
            }
        }
    
    def save_config(self, config: Dict, config_file: str, format: ConfigFormat = ConfigFormat.YAML) -> bool:
        """
        Save configuration to file.
        
        Args:
            config: Configuration dictionary to save
            config_file: Output file path
            format: Output format
            
        Returns:
            True if successful, False otherwise
        """
        config_path = Path(config_file)
        
        if not config_path.is_absolute():
            config_path = self.config_dir / config_path
        
        try:
            if format == ConfigFormat.YAML:
                with open(config_path, 'w') as f:
                    yaml.dump(config, f, default_flow_style=False)
            elif format == ConfigFormat.JSON:
                with open(config_path, 'w') as f:
                    json.dump(config, f, indent=2)
            else:
                raise ValueError(f"Unsupported format: {format}")
            
            self.logger.info(f"Saved config to {config_path}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error saving config to {config_path}: {e}")
            return False
    
    def load_from_env(self) -> Dict:
        """
        Load configuration from environment variables.
        
        Returns:
            Configuration dictionary from environment
        """
        env_config = {}
        
        # Assessment config from env
        if os.getenv('DENGKIS_STEALTH_MODE'):
            env_config.setdefault('assessment', {})['stealth_mode'] = os.getenv('DENGKIS_STEALTH_MODE').lower() == 'true'
        
        if os.getenv('DENGKIS_MAX_CONCURRENT'):
            env_config.setdefault('assessment', {})['max_concurrent_requests'] = int(os.getenv('DENGKIS_MAX_CONCURRENT'))
        
        if os.getenv('DENGKIS_TIMEOUT'):
            env_config.setdefault('assessment', {})['timeout'] = float(os.getenv('DENGKIS_TIMEOUT'))
        
        # Reporting config from env
        if os.getenv('DENGKIS_OUTPUT_DIR'):
            env_config.setdefault('reporting', {})['output_dir'] = os.getenv('DENGKIS_OUTPUT_DIR')
        
        return env_config
    
    def get_config(self, section: Optional[str] = None) -> Any:
        """
        Get configuration value(s).
        
        Args:
            section: Configuration section name (None for all config)
            
        Returns:
            Configuration value or dictionary
        """
        if section:
            return self.config.get(section, {})
        return self.config
    
    def update_config(self, section: str, updates: Dict) -> None:
        """
        Update configuration section.
        
        Args:
            section: Configuration section name
            updates: Dictionary of updates to apply
        """
        if section not in self.config:
            self.config[section] = {}
        
        self.config[section].update(updates)
        self.logger.info(f"Updated config section: {section}")
    
    def reset_to_defaults(self) -> None:
        """Reset configuration to defaults."""
        self.config = self.default_config.copy()
        self.logger.info("Configuration reset to defaults")
