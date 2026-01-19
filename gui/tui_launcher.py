"""
TUI Launcher Window - Launch tactical TUI dashboard.
"""
import tkinter as tk
from tkinter import ttk
import subprocess
import sys
from pathlib import Path

from gui.theme import COLORS, FONTS
from gui.utils import show_error, show_info


class TuiLauncherWindow(tk.Toplevel):
    """Window to launch TUI dashboard."""
    
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        
        self.configure(bg=COLORS['bg_primary'])
        self.title("DENGKIS // TUI LAUNCHER")
        self.geometry("500x300")
        self.transient(parent)
        self.grab_set()
        
        # Center window
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.winfo_screenheight() // 2) - (300 // 2)
        self.geometry(f"500x300+{x}+{y}")
        
        self._create_layout()
    
    def _create_layout(self):
        """Create TUI launcher layout."""
        main_frame = ttk.LabelFrame(self, text="TACTICAL TUI DASHBOARD", 
                                   style='Dark.TLabelframe', padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tk.Label(main_frame, text="Launch the tactical terminal-based dashboard", 
                bg=COLORS['bg_secondary'], fg=COLORS['fg_primary'],
                font=FONTS['monospace']).pack(pady=10)
        
        # Target input
        target_frame = ttk.Frame(main_frame, style='Dark.TFrame')
        target_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(target_frame, text="[TARGET]", bg=COLORS['bg_secondary'], 
                fg=COLORS['accent_red'], font=FONTS['monospace_bold']).pack(side=tk.LEFT, padx=5)
        self.target_var = tk.StringVar()
        target_entry = ttk.Entry(target_frame, textvariable=self.target_var, style='Dark.TEntry')
        target_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Attack mode
        mode_frame = ttk.Frame(main_frame, style='Dark.TFrame')
        mode_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(mode_frame, text="[MODE]", bg=COLORS['bg_secondary'], 
                fg=COLORS['accent_red'], font=FONTS['monospace_bold']).pack(side=tk.LEFT, padx=5)
        self.mode_var = tk.StringVar(value="aggressive")
        mode_combo = ttk.Combobox(mode_frame, textvariable=self.mode_var, 
                                 values=["passive", "active", "aggressive"],
                                 style='Dark.TCombobox', state='readonly')
        mode_combo.pack(side=tk.LEFT, padx=5)
        
        # Authorization
        self.auth_var = tk.BooleanVar()
        ttk.Checkbutton(main_frame, text="[AUTHORIZED] I have permission to test this target",
                       variable=self.auth_var, style='Dark.TCheckbutton').pack(pady=10)
        
        # Launch button
        button_frame = tk.Frame(main_frame, bg=COLORS['bg_secondary'])
        button_frame.pack(fill=tk.X, pady=20)
        
        ttk.Button(button_frame, text="[LAUNCH TUI]", command=self._launch_tui,
                  style='Danger.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="[CANCEL]", command=self.destroy,
                  style='Dark.TButton').pack(side=tk.LEFT, padx=5)
    
    def _launch_tui(self):
        """Launch TUI dashboard."""
        target = self.target_var.get().strip()
        authorized = self.auth_var.get()
        mode = self.mode_var.get()
        
        if not target:
            show_error("Please enter a target URL", self)
            return
        
        if not authorized:
            show_error("Authorization is REQUIRED", self)
            return
        
        self.destroy()
        
        # Launch TUI in subprocess
        try:
            cmd = [sys.executable, "-m", "cli.main", "tui", target, "--authorized", "--mode", mode]
            subprocess.Popen(cmd, cwd=Path(__file__).parent.parent)
            show_info("TUI dashboard launched in new terminal", self.app.root)
        except Exception as e:
            show_error(f"Failed to launch TUI: {e}", self.app.root)
