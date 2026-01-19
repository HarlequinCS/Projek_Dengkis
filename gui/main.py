"""
Main GUI application for PROJEK DENGKIS.
Tkinter-based desktop interface.
"""
import tkinter as tk
from tkinter import ttk
import sys
from pathlib import Path

# Add engine to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from gui.dashboard import DashboardWindow
from gui.theme import apply_dark_theme, COLORS, FONTS
from engine.logging.logger import get_logger


class DengkisGUI:
    """Main GUI application class."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("DENGKIS // OPERATOR DASHBOARD // AUTHORIZED USE ONLY")
        self.root.geometry("1400x900")
        
        # Apply dark terminal theme
        apply_dark_theme(self.root)
        
        # Set window icon if available
        try:
            # self.root.iconbitmap('icon.ico')  # Uncomment if icon available
            pass
        except Exception:
            pass
        
        self.logger = get_logger()
        self.logger.info("GUI application started")
        
        # Create menu bar
        self._create_menu()
        
        # Start with dashboard
        self.dashboard = DashboardWindow(self.root, self)
        self.dashboard.pack(fill=tk.BOTH, expand=True)
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
    
    def _create_menu(self):
        """Create application menu bar with dark theme."""
        menubar = tk.Menu(self.root, bg=COLORS['bg_secondary'], fg=COLORS['fg_primary'],
                         activebackground=COLORS['selection'], activeforeground=COLORS['accent_red'],
                         font=FONTS['monospace'])
        self.root.config(menu=menubar)
        
        # Attack menu
        attack_menu = tk.Menu(menubar, tearoff=0, bg=COLORS['bg_secondary'], fg=COLORS['fg_primary'],
                             activebackground=COLORS['selection'], activeforeground=COLORS['accent_red'],
                             font=FONTS['monospace'])
        menubar.add_cascade(label="ATTACK", menu=attack_menu)
        attack_menu.add_command(label="New Attack Scan", command=self._new_scan)
        attack_menu.add_command(label="Launch TUI Dashboard", command=self._launch_tui)
        attack_menu.add_separator()
        attack_menu.add_command(label="Advanced Modules", command=self._open_advanced_modules)
        attack_menu.add_command(label="Performance Optimizer", command=self._open_performance)
        
        # Sessions menu
        session_menu = tk.Menu(menubar, tearoff=0, bg=COLORS['bg_secondary'], fg=COLORS['fg_primary'],
                              activebackground=COLORS['selection'], activeforeground=COLORS['accent_red'],
                              font=FONTS['monospace'])
        menubar.add_cascade(label="SESSIONS", menu=session_menu)
        session_menu.add_command(label="Refresh Sessions", command=self._open_session)
        session_menu.add_command(label="View Reports", command=self._view_reports)
        session_menu.add_command(label="Visualizations", command=self._view_visualizations)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0, bg=COLORS['bg_secondary'], fg=COLORS['fg_primary'],
                            activebackground=COLORS['selection'], activeforeground=COLORS['accent_red'],
                            font=FONTS['monospace'])
        menubar.add_cascade(label="TOOLS", menu=tools_menu)
        tools_menu.add_command(label="Configuration", command=self._open_config)
        tools_menu.add_command(label="View Logs", command=self._view_logs)
        tools_menu.add_command(label="Kali Integration", command=self._open_kali)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0, bg=COLORS['bg_secondary'], fg=COLORS['fg_primary'],
                           activebackground=COLORS['selection'], activeforeground=COLORS['accent_red'],
                           font=FONTS['monospace'])
        menubar.add_cascade(label="HELP", menu=help_menu)
        help_menu.add_command(label="About", command=self._show_about)
        help_menu.add_command(label="Documentation", command=self._show_docs)
    
    def _new_scan(self):
        """Open new scan window."""
        from gui.scan_window import ScanWindow
        scan_window = ScanWindow(self.root, self)
    
    def _open_session(self):
        """Open session selection dialog."""
        self.dashboard.refresh_sessions()
    
    def _open_config(self):
        """Open configuration window."""
        from gui.config_window import ConfigWindow
        config_window = ConfigWindow(self.root, self)
    
    def _view_logs(self):
        """Open log viewer window."""
        from gui.log_window import LogWindow
        log_window = LogWindow(self.root, self)
    
    def _launch_tui(self):
        """Launch tactical TUI dashboard."""
        from gui.tui_launcher import TuiLauncherWindow
        launcher = TuiLauncherWindow(self.root, self)
    
    def _open_advanced_modules(self):
        """Open advanced modules window."""
        from gui.advanced_modules_window import AdvancedModulesWindow
        modules_window = AdvancedModulesWindow(self.root, self)
    
    def _open_performance(self):
        """Open performance optimizer window."""
        from gui.performance_window import PerformanceWindow
        perf_window = PerformanceWindow(self.root, self)
    
    def _open_kali(self):
        """Open Kali integration window."""
        from gui.kali_window import KaliIntegrationWindow
        kali_window = KaliIntegrationWindow(self.root, self)
    
    def _view_reports(self):
        """View reports for selected session."""
        if hasattr(self, 'dashboard'):
            self.dashboard._view_report()
    
    def _view_visualizations(self):
        """View visualizations for selected session."""
        if hasattr(self, 'dashboard'):
            self.dashboard._visualize()
    
    def _show_about(self):
        """Show about dialog."""
        from tkinter import messagebox
        messagebox.showinfo(
            "DENGKIS // ABOUT",
            "PROJEK DENGKIS v0.4.0\n\n"
            "AGGRESSIVE ATTACK-DRIVEN EXPLOITATION ENGINE\n\n"
            "⚠️ AUTHORIZED USE ONLY\n"
            "⚠️ Unauthorized use is ILLEGAL\n\n"
            "See LICENSE for restrictions."
        )
    
    def _show_docs(self):
        """Show documentation links."""
        from tkinter import messagebox
        messagebox.showinfo(
            "DENGKIS // DOCUMENTATION",
            "Documentation Files:\n\n"
            "- ATTACK_ENGINE.md\n"
            "- ADVANCED_MODULES.md\n"
            "- PERFORMANCE_TUI.md\n"
            "- README.md\n\n"
            "See docs/ directory for more."
        )
    
    def _on_closing(self):
        """Handle window close event."""
        self.logger.info("GUI application closing")
        self.root.quit()
        self.root.destroy()
    
    def run(self):
        """Start GUI application."""
        self.logger.info("Starting GUI event loop")
        self.root.mainloop()


def main():
    """Main entry point for GUI."""
    # Display warning banner
    print("=" * 70)
    print("⚠️  PROJEK DENGKIS - RESTRICTED USE SOFTWARE")
    print("=" * 70)
    print("⚠️  WARNING: This is dangerous software for AUTHORIZED use only.")
    print("⚠️  Unauthorized use is ILLEGAL and may result in criminal prosecution.")
    print("⚠️  Use ONLY on systems you own or have written permission to test.")
    print("⚠️  See LICENSE for complete terms and restrictions.")
    print("=" * 70)
    print()
    
    app = DengkisGUI()
    app.run()


if __name__ == '__main__':
    main()
