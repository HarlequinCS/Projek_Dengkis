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
from engine.logging.logger import get_logger


class DengkisGUI:
    """Main GUI application class."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("PROJEK DENGKIS - Security Assessment Framework")
        self.root.geometry("1200x800")
        
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
        """Create application menu bar."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Scan", command=self._new_scan)
        file_menu.add_command(label="Open Session", command=self._open_session)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self._on_closing)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Configuration", command=self._open_config)
        tools_menu.add_command(label="View Logs", command=self._view_logs)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self._show_about)
    
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
    
    def _show_about(self):
        """Show about dialog."""
        from tkinter import messagebox
        messagebox.showinfo(
            "About PROJEK DENGKIS",
            "PROJEK DENGKIS v0.4.0\n\n"
            "Kali Linux-first security assessment tool\n"
            "Detect ≠ Exploit | Observe ≠ Attack\n\n"
            "For authorized security testing only."
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
    app = DengkisGUI()
    app.run()


if __name__ == '__main__':
    main()
