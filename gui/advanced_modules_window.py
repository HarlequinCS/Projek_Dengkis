"""
Advanced Modules Window - Configure and monitor advanced attack modules.
"""
import tkinter as tk
from tkinter import ttk

from gui.theme import COLORS, FONTS
from gui.utils import show_info


class AdvancedModulesWindow(tk.Toplevel):
    """Window for advanced modules configuration."""
    
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        
        self.configure(bg=COLORS['bg_primary'])
        self.title("DENGKIS // ADVANCED MODULES")
        self.geometry("700x600")
        self.transient(parent)
        
        self._create_layout()
    
    def _create_layout(self):
        """Create advanced modules layout."""
        header = tk.Label(self, text="[ADVANCED ATTACK MODULES]", 
                         bg=COLORS['bg_primary'], fg=COLORS['accent_red'],
                         font=FONTS['monospace_large'])
        header.pack(pady=10)
        
        main_frame = ttk.Frame(self, style='Dark.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Module descriptions
        modules = [
            ("FLAG HUNTER", "CTF Automation - Regex search, environment dumps, config crawls"),
            ("GHOST OPERATOR", "WAF/EDR Evasion - Encoding, fragmentation, user-agent rotation"),
            ("LOGIC BREAKER", "Business Logic Testing - Integer overflow, race conditions, IDOR"),
            ("RED TEAM ARCHITECT", "Post-Exploitation - Network discovery, credential scavenging"),
            ("ATTACKER MINDSET", "Intelligence Reports - Kill chain mapping, PoC generation")
        ]
        
        for i, (title, desc) in enumerate(modules):
            frame = ttk.LabelFrame(main_frame, text=title, style='Dark.TLabelframe', padding=10)
            frame.pack(fill=tk.X, pady=5)
            
            tk.Label(frame, text=desc, bg=COLORS['bg_secondary'], fg=COLORS['fg_primary'],
                    font=FONTS['monospace'], justify=tk.LEFT, anchor='w').pack(fill=tk.X)
        
        ttk.Button(main_frame, text="[CLOSE]", command=self.destroy,
                  style='Dark.TButton').pack(pady=20)
