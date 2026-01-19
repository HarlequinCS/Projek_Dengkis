# PROJEK DENGKIS - Plugin Development Guide

## Overview

PROJEK DENGKIS supports plugin-based extensions for custom functionality.

## Plugin Architecture

All plugins inherit from `BasePlugin` and implement required methods.

## Creating a Plugin

### Basic Plugin Template

```python
from engine.plugins.base import BasePlugin
from typing import Dict, Optional

class MyCustomPlugin(BasePlugin):
    def __init__(self):
        super().__init__()
        self.name = "My Custom Plugin"
        self.version = "1.0.0"
    
    def initialize(self, config: Optional[Dict] = None) -> bool:
        """Initialize plugin."""
        self.config = config or {}
        return True
    
    def execute(self, data: Dict) -> Dict:
        """Execute plugin logic."""
        # Your plugin logic here
        return {
            'plugin': self.name,
            'result': 'custom_data'
        }
    
    def cleanup(self):
        """Cleanup resources if needed."""
        pass
```

## Example Plugins

See `engine/plugins/examples/` for reference implementations:
- `custom_scanner.py` - Custom scanning plugin
- `compliance_iso27001.py` - ISO 27001 compliance checker
- `risk_scorer.py` - Enhanced risk scoring

## Using Plugins

```python
from engine.plugins.base import PluginManager
from engine.plugins.examples.custom_scanner import CustomScannerPlugin

# Create plugin manager
manager = PluginManager()

# Register plugin
plugin = CustomScannerPlugin()
manager.register_plugin(plugin)

# Execute plugins
data = {'target': 'example.com'}
result = manager.execute_plugins(data)
```

## Plugin Configuration

Plugins can be configured via YAML:

```yaml
plugins:
  custom_scanner:
    enabled: true
    config:
      custom_setting: value
```

## Integration

Plugins are automatically executed during assessment if registered with the plugin manager.
