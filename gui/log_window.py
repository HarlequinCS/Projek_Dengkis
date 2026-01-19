"""
Log viewer window for PROJEK DENGKIS GUI.
Displays application logs.
"""
import tkinter as tk
from tkinter import ttk
from pathlib import Path
from datetime import datetime

from gui.components.log_viewer import LogViewer
from engine.logging.logger import get_logger
from gui.utils import open_file


class LogWindow(tk.Toplevel):
    """Log viewer window."""
    
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.logger = get_logger()
        
        self.title("Application Logs")
        self.geometry("800x600")
        self.transient(parent)
        
        # Center window
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (800 // 2)
        y = (self.winfo_screenheight() // 2) - (600 // 2)
        self.geometry(f"800x600+{x}+{y}")
        
        self._create_layout()
        self._load_logs()
    
    def _create_layout(self):
        """Create log window layout."""
        # Main frame
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(header_frame, text="Application Logs", font=('Arial', 12, 'bold')).pack(side=tk.LEFT)
        
        ttk.Button(header_frame, text="Refresh", command=self._load_logs).pack(side=tk.RIGHT, padx=5)
        ttk.Button(header_frame, text="Open Log File", command=self._open_log_file).pack(side=tk.RIGHT, padx=5)
        
        # Log viewer
        self.log_viewer = LogViewer(main_frame, height=500)
        self.log_viewer.pack(fill=tk.BOTH, expand=True)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(button_frame, text="Clear", command=self.log_viewer.clear).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Close", command=self.destroy).pack(side=tk.RIGHT, padx=5)
    
    def _load_logs(self):
        """Load logs from file."""
        log_dir = Path('logs')
        if log_dir.exists():
            # Find today's log file
            today = datetime.now().strftime('%Y%m%d')
            log_file = log_dir / f'dengkis_{today}.log'
            
            if log_file.exists():
                self.log_viewer.load_from_file(str(log_file))
            else:
                self.log_viewer.add_log("No log file found for today", "INFO")
        else:
            self.log_viewer.add_log("Log directory not found", "WARNING")
    
    def _open_log_file(self):
        """Open log file in default application."""
        log_dir = Path('logs')
        if log_dir.exists():
            today = datetime.now().strftime('%Y%m%d')
            log_file = log_dir / f'dengkis_{today}.log'
            
            if log_file.exists():
                open_file(str(log_file))
            else:
                self.log_viewer.add_log("No log file found for today", "WARNING")
