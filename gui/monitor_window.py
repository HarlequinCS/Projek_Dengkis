"""
Real-time monitoring window for PROJEK DENGKIS GUI.
Shows progress and live logs during assessment execution.
"""
import tkinter as tk
from tkinter import ttk

from gui.components.log_viewer import LogViewer
from engine.logging.logger import get_logger
from engine.storage.session_store import SessionStore


class MonitorWindow(tk.Toplevel):
    """Real-time monitoring window for active scans."""
    
    def __init__(self, parent, app, session_id: str):
        super().__init__(parent)
        self.app = app
        self.session_id = session_id
        self.logger = get_logger(session_id)
        self.store = SessionStore()
        
        self.title(f"Monitor - Session {session_id[:8]}")
        self.geometry("800x600")
        self.transient(parent)
        
        # Center window
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (800 // 2)
        y = (self.winfo_screenheight() // 2) - (600 // 2)
        self.geometry(f"800x600+{x}+{y}")
        
        self._create_layout()
        self._load_session_data()
    
    def _create_layout(self):
        """Create monitor window layout."""
        # Main frame
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(header_frame, text=f"Session ID: {self.session_id}", font=('Arial', 12, 'bold')).pack(side=tk.LEFT)
        
        refresh_btn = ttk.Button(header_frame, text="Refresh", command=self._refresh)
        refresh_btn.pack(side=tk.RIGHT)
        
        # Progress frame
        progress_frame = ttk.LabelFrame(main_frame, text="Progress", padding=10)
        progress_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.status_label = ttk.Label(progress_frame, text="Status: Active")
        self.status_label.pack(anchor=tk.W)
        
        self.progress_bar = ttk.Progressbar(progress_frame, mode='indeterminate')
        self.progress_bar.pack(fill=tk.X, pady=5)
        self.progress_bar.start()
        
        # Session info frame
        info_frame = ttk.LabelFrame(main_frame, text="Session Information", padding=10)
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.info_text = tk.Text(info_frame, height=5, wrap=tk.WORD)
        self.info_text.pack(fill=tk.X)
        self.info_text.config(state=tk.DISABLED)
        
        # Log viewer
        logs_frame = ttk.LabelFrame(main_frame, text="Activity Logs", padding=10)
        logs_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_viewer = LogViewer(logs_frame, height=200)
        self.log_viewer.pack(fill=tk.BOTH, expand=True)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(button_frame, text="View Report", command=self._view_report).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Visualize", command=self._visualize).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Close", command=self.destroy).pack(side=tk.RIGHT, padx=5)
    
    def _load_session_data(self):
        """Load and display session data."""
        session_data = self.store.load_session(self.session_id)
        
        if session_data:
            # Update status
            status = session_data.get('status', 'unknown')
            self.status_label.config(text=f"Status: {status.title()}")
            
            if status == 'completed':
                self.progress_bar.stop()
                self.progress_bar.config(mode='determinate', value=100)
            
            # Update info
            self.info_text.config(state=tk.NORMAL)
            self.info_text.delete(1.0, tk.END)
            info_content = f"Target: {session_data.get('target', 'Unknown')}\n"
            info_content += f"Started: {session_data.get('started_at', 'Unknown')}\n"
            info_content += f"Completed: {session_data.get('completed_at', 'In Progress')}\n"
            fingerprint = session_data.get('fingerprint', {})
            probes = fingerprint.get('probes', [])
            info_content += f"Probes Executed: {len(probes)}"
            self.info_text.insert(1.0, info_content)
            self.info_text.config(state=tk.DISABLED)
            
            # Add log entries
            self.log_viewer.add_log(f"Session loaded: {self.session_id}", "INFO")
            self.log_viewer.add_log(f"Target: {session_data.get('target')}", "INFO")
        else:
            self.log_viewer.add_log("Session not found", "ERROR")
    
    def _refresh(self):
        """Refresh session data."""
        self._load_session_data()
    
    def _view_report(self):
        """Open report window."""
        from gui.report_window import ReportWindow
        report_window = ReportWindow(self.app.root, self.app, self.session_id)
    
    def _visualize(self):
        """Open visualization window."""
        from gui.visualization_window import VisualizationWindow
        viz_window = VisualizationWindow(self.app.root, self.app, self.session_id)
