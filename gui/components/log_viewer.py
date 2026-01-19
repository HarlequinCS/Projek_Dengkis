"""
Log viewer component for GUI.
Displays logs in a scrollable text widget.
"""
import tkinter as tk
from tkinter import ttk, scrolledtext
from typing import Optional
from pathlib import Path


class LogViewer(ttk.Frame):
    """Scrollable log viewer component."""
    
    def __init__(self, parent, height: int = 300):
        super().__init__(parent)
        
        self.log_text = scrolledtext.ScrolledText(
            self,
            height=height,
            wrap=tk.WORD,
            state=tk.DISABLED,
            font=('Consolas', 9)
        )
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Configure text tags for different log levels
        self.log_text.tag_config('INFO', foreground='blue')
        self.log_text.tag_config('WARNING', foreground='orange')
        self.log_text.tag_config('ERROR', foreground='red')
        self.log_text.tag_config('DEBUG', foreground='gray')
        self.log_text.tag_config('CRITICAL', foreground='red', background='yellow')
    
    def add_log(self, message: str, level: str = 'INFO'):
        """Add log message to viewer."""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"[{level}] {message}\n", level)
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.update()
    
    def clear(self):
        """Clear all logs."""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
    
    def load_from_file(self, file_path: str):
        """Load logs from file."""
        try:
            path = Path(file_path)
            if path.exists():
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.log_text.config(state=tk.NORMAL)
                    self.log_text.delete(1.0, tk.END)
                    self.log_text.insert(1.0, content)
                    self.log_text.config(state=tk.DISABLED)
                    self.log_text.see(tk.END)
        except Exception:
            pass
