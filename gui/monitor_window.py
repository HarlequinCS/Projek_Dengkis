"""
Real-time monitoring window for PROJEK DENGKIS GUI.
Shows progress and live logs during assessment execution.
"""
import tkinter as tk
from tkinter import ttk

from gui.components.log_viewer import LogViewer
from gui.components.attack_monitor import AttackMonitor
from gui.theme import COLORS, FONTS
from engine.logging.logger import get_logger
from engine.storage.session_store import SessionStore


class MonitorWindow(tk.Toplevel):
    """Real-time monitoring window for active attacks with live progress."""
    
    def __init__(self, parent, app, session_id: str):
        super().__init__(parent)
        self.app = app
        self.session_id = session_id
        self.logger = get_logger(session_id)
        self.store = SessionStore()
        
        # Apply dark theme
        self.configure(bg=COLORS['bg_primary'])
        
        self.title(f"DENGKIS // LIVE ATTACK MONITOR // {session_id[:8]}")
        self.geometry("1000x700")
        self.transient(parent)
        
        # Center window
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (1000 // 2)
        y = (self.winfo_screenheight() // 2) - (700 // 2)
        self.geometry(f"1000x700+{x}+{y}")
        
        self._create_layout()
        self._load_session_data()
    
    def _create_layout(self):
        """Create monitor window layout with live attack monitor."""
        # Header
        header_frame = tk.Frame(self, bg=COLORS['bg_primary'], height=60)
        header_frame.pack(fill=tk.X, padx=10, pady=10)
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(header_frame, text=f"LIVE ATTACK MONITOR // SESSION: {self.session_id[:12]}", 
                              bg=COLORS['bg_primary'], fg=COLORS['accent_red'],
                              font=FONTS['monospace_large'])
        title_label.pack()
        
        # Main notebook
        notebook = ttk.Notebook(self, style='Dark.TNotebook')
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tab 1: Live Attack Monitor
        monitor_frame = ttk.Frame(notebook, style='Dark.TFrame')
        notebook.add(monitor_frame, text="[LIVE ATTACK]")
        
        self.attack_monitor = AttackMonitor(monitor_frame)
        self.attack_monitor.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Tab 2: Session Info
        info_frame = ttk.Frame(notebook, style='Dark.TFrame')
        notebook.add(info_frame, text="[SESSION INFO]")
        self._create_info_tab(info_frame)
        
        # Tab 3: Logs
        logs_frame = ttk.Frame(notebook, style='Dark.TFrame')
        notebook.add(logs_frame, text="[LOGS]")
        
        self.log_viewer = LogViewer(logs_frame, height=300)
        self.log_viewer.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Buttons
        button_frame = tk.Frame(self, bg=COLORS['bg_primary'])
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(button_frame, text="[REFRESH]", command=self._refresh,
                  style='Dark.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="[REPORT]", command=self._view_report,
                  style='Primary.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="[CLOSE]", command=self.destroy,
                  style='Dark.TButton').pack(side=tk.RIGHT, padx=5)
    
    def _create_info_tab(self, parent):
        """Create session info tab."""
        info_frame = ttk.LabelFrame(parent, text="SESSION INFORMATION", 
                                    style='Dark.TLabelframe', padding=10)
        info_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.info_text = tk.Text(info_frame, height=20, wrap=tk.WORD,
                                bg=COLORS['bg_tertiary'], fg=COLORS['fg_primary'],
                                font=FONTS['monospace'],
                                borderwidth=1, relief='solid')
        self.info_text.pack(fill=tk.BOTH, expand=True)
        self.info_text.config(state=tk.DISABLED)
    
    def _load_session_data(self):
        """Load and display session data."""
        session_data = self.store.load_session(self.session_id)
        
        if session_data:
            # Update attack monitor with progress updates
            progress_updates = session_data.get('progress_updates', [])
            for update in progress_updates:
                self.attack_monitor.add_progress(
                    update.get('message', ''),
                    update.get('status', 'info'),
                    update.get('data')
                )
            
            # Add successful exploits
            exploitation_results = session_data.get('exploitation_results', [])
            for result in exploitation_results:
                if result.get('success'):
                    self.attack_monitor.add_success(result)
            
            # Add failed exploits
            failed_exploits = session_data.get('failed_exploits', [])
            for failure in failed_exploits:
                self.attack_monitor.add_failure(failure)
            
            # Update info
            self.info_text.config(state=tk.NORMAL)
            self.info_text.delete(1.0, tk.END)
            info_content = f"Target: {session_data.get('target', 'Unknown')}\n"
            info_content += f"Started: {session_data.get('started_at', 'Unknown')}\n"
            info_content += f"Status: {session_data.get('status', 'In Progress')}\n"
            
            # Count probes from crawl results (endpoints discovered = probes executed)
            crawl_results = session_data.get('crawl_results', {})
            endpoints = crawl_results.get('endpoints_discovered', [])
            total_probes = len(endpoints)
            
            # Also count from findings (each finding represents a probe)
            findings = session_data.get('findings', [])
            if total_probes == 0 and len(findings) > 0:
                total_probes = len(findings)
            
            info_content += f"Probes Executed: {total_probes}\n"
            info_content += f"Endpoints Discovered: {len(endpoints)}\n"
            info_content += f"Findings: {len(findings)}\n\n"
            
            # Count successful exploits
            successful_exploits = len([f for f in findings if f.get('exploited', False)])
            failed_exploits = len([f for f in findings if f.get('exploitation_failure')])
            
            info_content += f"EXPLOITATION RESULTS:\n"
            info_content += f"Successful Exploits: {successful_exploits}\n"
            info_content += f"Failed Exploits: {failed_exploits}\n\n"
            
            # Show failed exploits with reasons
            if failed_exploits > 0:
                info_content += f"FAILED EXPLOITS (with reasons):\n"
                for finding in findings:
                    if finding.get('exploitation_failure'):
                        failure = finding['exploitation_failure']
                        info_content += f"- {finding.get('category', 'unknown')} on {finding.get('endpoint', 'unknown')}\n"
                        info_content += f"  REASON: {failure.get('reason', 'Unknown')}\n"
            
            self.info_text.config(state=tk.NORMAL)
            self.info_text.delete(1.0, tk.END)
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
