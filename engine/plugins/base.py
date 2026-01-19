"""
Base plugin interface for PROJEK DENGKIS.
Defines the plugin architecture for extending functionality.
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any


class BasePlugin(ABC):
    """
    Base class for PROJEK DENGKIS plugins.
    All custom plugins must inherit from this class.
    """
    
    def __init__(self):
        self.name = self.__class__.__name__
        self.version = "1.0.0"
        self.enabled = True
    
    @abstractmethod
    def initialize(self, config: Optional[Dict] = None) -> bool:
        """
        Initialize the plugin.
        
        Args:
            config: Optional configuration dictionary
            
        Returns:
            True if initialization successful, False otherwise
        """
        pass
    
    @abstractmethod
    def execute(self, data: Dict) -> Dict:
        """
        Execute plugin functionality.
        
        Args:
            data: Input data dictionary
            
        Returns:
            Output data dictionary
        """
        pass
    
    def cleanup(self):
        """
        Cleanup plugin resources.
        Override if needed.
        """
        pass
    
    def get_info(self) -> Dict:
        """
        Get plugin information.
        
        Returns:
            Plugin information dictionary
        """
        return {
            'name': self.name,
            'version': self.version,
            'enabled': self.enabled
        }


class PluginManager:
    """
    Manager for loading and executing plugins.
    """
    
    def __init__(self):
        self.plugins: List[BasePlugin] = []
    
    def register_plugin(self, plugin: BasePlugin) -> bool:
        """
        Register a plugin.
        
        Args:
            plugin: Plugin instance
            
        Returns:
            True if registration successful
        """
        if plugin.initialize():
            self.plugins.append(plugin)
            return True
        return False
    
    def execute_plugins(self, data: Dict) -> Dict:
        """
        Execute all enabled plugins on data.
        
        Args:
            data: Input data dictionary
            
        Returns:
            Combined output from all plugins
        """
        result = data.copy()
        
        for plugin in self.plugins:
            if plugin.enabled:
                try:
                    plugin_result = plugin.execute(result)
                    result.update(plugin_result)
                except Exception as e:
                    # Log error but continue with other plugins
                    continue
        
        return result
    
    def get_plugins(self) -> List[Dict]:
        """
        Get list of registered plugins.
        
        Returns:
            List of plugin information dictionaries
        """
        return [plugin.get_info() for plugin in self.plugins]
    
    def cleanup_all(self):
        """Cleanup all plugins."""
        for plugin in self.plugins:
            try:
                plugin.cleanup()
            except Exception:
                pass
