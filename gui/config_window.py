"""
Configuration window for PROJEK DENGKIS GUI.
Allows viewing and editing configuration settings.
"""
import tkinter as tk
from tkinter import ttk

from engine.config.manager import ConfigManager
from engine.logging.logger import get_logger
from gui.utils import show_info, show_error


class ConfigWindow(tk.Toplevel):
    """Configuration management window."""
    
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.logger = get_logger()
        self.config_manager = ConfigManager()
        
        self.title("Configuration")
        self.geometry("600x500")
        self.transient(parent)
        self.grab_set()
        
        # Center window
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.winfo_screenheight() // 2) - (500 // 2)
        self.geometry(f"600x500+{x}+{y}")
        
        self._create_layout()
        self._load_config()
    
    def _create_layout(self):
        """Create configuration window layout."""
        # Main frame
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Notebook for tabs
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Assessment config tab
        assessment_frame = ttk.Frame(notebook, padding=10)
        notebook.add(assessment_frame, text="Assessment")
        
        self.stealth_var = tk.BooleanVar()
        ttk.Checkbutton(assessment_frame, text="Stealth Mode", variable=self.stealth_var).pack(anchor=tk.W, pady=5)
        
        ttk.Label(assessment_frame, text="Max Concurrent Requests:").pack(anchor=tk.W, pady=2)
        self.max_concurrent_var = tk.StringVar()
        ttk.Entry(assessment_frame, textvariable=self.max_concurrent_var, width=20).pack(anchor=tk.W, pady=2)
        
        ttk.Label(assessment_frame, text="Timeout (seconds):").pack(anchor=tk.W, pady=2)
        self.timeout_var = tk.StringVar()
        ttk.Entry(assessment_frame, textvariable=self.timeout_var, width=20).pack(anchor=tk.W, pady=2)
        
        ttk.Label(assessment_frame, text="Max Retries:").pack(anchor=tk.W, pady=2)
        self.retries_var = tk.StringVar()
        ttk.Entry(assessment_frame, textvariable=self.retries_var, width=20).pack(anchor=tk.W, pady=2)
        
        # Reporting config tab
        reporting_frame = ttk.Frame(notebook, padding=10)
        notebook.add(reporting_frame, text="Reporting")
        
        ttk.Label(reporting_frame, text="Output Directory:").pack(anchor=tk.W, pady=2)
        self.output_dir_var = tk.StringVar()
        ttk.Entry(reporting_frame, textvariable=self.output_dir_var, width=40).pack(anchor=tk.W, pady=2)
        
        self.include_raw_var = tk.BooleanVar()
        ttk.Checkbutton(reporting_frame, text="Include Raw Data", variable=self.include_raw_var).pack(anchor=tk.W, pady=5)
        
        self.generate_charts_var = tk.BooleanVar()
        ttk.Checkbutton(reporting_frame, text="Generate Charts", variable=self.generate_charts_var).pack(anchor=tk.W, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(button_frame, text="Save", command=self._save_config).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Reset to Defaults", command=self._reset_config).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Close", command=self.destroy).pack(side=tk.RIGHT, padx=5)
    
    def _load_config(self):
        """Load current configuration."""
        config = self.config_manager.get_config()
        
        # Assessment config
        assessment = config.get('assessment', {})
        self.stealth_var.set(assessment.get('stealth_mode', False))
        self.max_concurrent_var.set(str(assessment.get('max_concurrent_requests', 10)))
        self.timeout_var.set(str(assessment.get('timeout', 30.0)))
        self.retries_var.set(str(assessment.get('retry_attempts', 3)))
        
        # Reporting config
        reporting = config.get('reporting', {})
        self.output_dir_var.set(reporting.get('output_dir', 'reports'))
        self.include_raw_var.set(reporting.get('include_raw_data', False))
        self.generate_charts_var.set(reporting.get('generate_charts', True))
    
    def _save_config(self):
        """Save configuration."""
        try:
            # Update assessment config
            self.config_manager.update_config('assessment', {
                'stealth_mode': self.stealth_var.get(),
                'max_concurrent_requests': int(self.max_concurrent_var.get()),
                'timeout': float(self.timeout_var.get()),
                'retry_attempts': int(self.retries_var.get())
            })
            
            # Update reporting config
            self.config_manager.update_config('reporting', {
                'output_dir': self.output_dir_var.get(),
                'include_raw_data': self.include_raw_var.get(),
                'generate_charts': self.generate_charts_var.get()
            })
            
            # Save to file
            config = self.config_manager.get_config()
            self.config_manager.save_config(config, 'config.yaml')
            
            show_info("Configuration saved successfully", self)
        except ValueError as e:
            show_error(f"Invalid configuration values: {e}", self)
        except Exception as e:
            show_error(f"Failed to save configuration: {e}", self)
    
    def _reset_config(self):
        """Reset configuration to defaults."""
        self.config_manager.reset_to_defaults()
        self._load_config()
        show_info("Configuration reset to defaults", self)
