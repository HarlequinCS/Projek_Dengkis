"""
Kali Integration Window - Kali Linux-specific features.
"""
import tkinter as tk
from tkinter import ttk

from gui.theme import COLORS, FONTS
from gui.utils import show_info


class KaliIntegrationWindow(tk.Toplevel):
    """Window for Kali Linux integration features."""
    
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        
        self.configure(bg=COLORS['bg_primary'])
        self.title("DENGKIS // KALI INTEGRATION")
        self.geometry("600x400")
        self.transient(parent)
        
        self._create_layout()
    
    def _create_layout(self):
        """Create Kali integration layout."""
        header = tk.Label(self, text="[KALI LINUX INTEGRATION]", 
                         bg=COLORS['bg_primary'], fg=COLORS['accent_red'],
                         font=FONTS['monospace_large'])
        header.pack(pady=10)
        
        main_frame = ttk.Frame(self, style='Dark.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Features
        features = [
            ("NERD FONT ICONS", "Tactical icons for vulnerability types"),
            ("NOTIFY-SEND ALERTS", "Desktop notifications for critical findings"),
            ("SESSION PERSISTENCE", "SQLite storage in /opt/dengkis/db/"),
            ("NATIVE INTEGRATION", "Optimized for Kali Linux environment")
        ]
        
        for title, desc in features:
            frame = ttk.LabelFrame(main_frame, text=title, style='Dark.TLabelframe', padding=10)
            frame.pack(fill=tk.X, pady=5)
            
            tk.Label(frame, text=desc, bg=COLORS['bg_secondary'], fg=COLORS['fg_primary'],
                    font=FONTS['monospace']).pack(anchor=tk.W)
        
        ttk.Button(main_frame, text="[CLOSE]", command=self.destroy,
                  style='Dark.TButton').pack(pady=20)
