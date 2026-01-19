"""
OPERATOR DASHBOARD - Tactical interface for PROJEK DENGKIS.
Dark terminal aesthetic with cyber warfare vibe.
"""
import tkinter as tk
from tkinter import ttk
from typing import Optional, List, Dict
import threading
from datetime import datetime

from gui.components.session_list import SessionList
from gui.components.log_viewer import LogViewer
from gui.scan_window import ScanWindow
from gui.visualization_window import VisualizationWindow
from gui.report_window import ReportWindow
from gui.theme import COLORS, FONTS, create_severity_label
from engine.storage.session_store import SessionStore
from engine.logging.logger import get_logger
from engine.filters.search import FilterManager
from gui.utils import run_async, show_info


class DashboardWindow(ttk.Frame):
    """Tactical operator dashboard window."""
    
    def __init__(self, parent, app):
        super().__init__(parent, style='Dark.TFrame')
        self.app = app
        self.logger = get_logger()
        self.store = SessionStore()
        self.filter_manager = FilterManager()
        self.all_sessions: List[Dict] = []
        self.selected_session_id: Optional[str] = None
        
        # Create layout
        self._create_layout()
        
        # Load sessions
        self.refresh_sessions()
    
    def _create_layout(self):
        """Create tactical dashboard layout."""
        # Header - Terminal-style banner
        header_frame = tk.Frame(self, bg=COLORS['bg_primary'], height=80)
        header_frame.pack(fill=tk.X, padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        # Title with ASCII art style
        title_frame = tk.Frame(header_frame, bg=COLORS['bg_primary'])
        title_frame.pack(side=tk.LEFT, padx=20, pady=10)
        
        title_label = tk.Label(title_frame, text="DENGKIS // OPERATOR DASHBOARD", 
                              bg=COLORS['bg_primary'], fg=COLORS['accent_red'],
                              font=FONTS['monospace_large'])
        title_label.pack()
        
        timestamp_label = tk.Label(title_frame, text=f"TIMESTAMP: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                                  bg=COLORS['bg_primary'], fg=COLORS['fg_secondary'],
                                  font=FONTS['monospace_small'])
        timestamp_label.pack()
        
        # Action buttons
        action_frame = tk.Frame(header_frame, bg=COLORS['bg_primary'])
        action_frame.pack(side=tk.RIGHT, padx=20, pady=10)
        
        ttk.Button(action_frame, text="[ATTACK]", command=self._new_scan, 
                  style='Danger.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="[REFRESH]", command=self.refresh_sessions,
                  style='Dark.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="[TUI]", command=self._launch_tui,
                  style='Primary.TButton').pack(side=tk.LEFT, padx=5)
        
        # Main content area
        content_frame = ttk.Frame(self, style='Dark.TFrame')
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel - Attack Sessions
        left_panel = ttk.LabelFrame(content_frame, text="ATTACK SESSIONS", style='Dark.TLabelframe', padding=10)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Filter/search
        filter_frame = ttk.Frame(left_panel, style='Dark.TFrame')
        filter_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(filter_frame, text="[SEARCH]", bg=COLORS['bg_secondary'], fg=COLORS['accent_red'],
                font=FONTS['monospace_bold']).pack(side=tk.LEFT, padx=5)
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(filter_frame, textvariable=self.search_var, width=25, style='Dark.TEntry')
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        search_entry.bind('<KeyRelease>', lambda e: self._apply_filters())
        
        # Session list with dark theme
        list_frame = ttk.Frame(left_panel, style='Dark.TFrame')
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        self.session_list = SessionList(list_frame, on_select=self._on_session_select)
        self.session_list.pack(fill=tk.BOTH, expand=True)
        
        # Session action buttons
        session_buttons = ttk.Frame(left_panel, style='Dark.TFrame')
        session_buttons.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(session_buttons, text="[REPORT]", command=self._view_report,
                  style='Primary.TButton').pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
        ttk.Button(session_buttons, text="[VIZ]", command=self._visualize,
                  style='Primary.TButton').pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
        ttk.Button(session_buttons, text="[DELETE]", command=self._delete_session,
                  style='Danger.TButton').pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
        
        # Right panel - Threat Intelligence
        right_panel = ttk.Frame(content_frame, style='Dark.TFrame')
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # Threat Summary
        threat_frame = ttk.LabelFrame(right_panel, text="THREAT SUMMARY", style='Dark.TLabelframe', padding=10)
        threat_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.threat_label = tk.Label(threat_frame, text="Loading threat data...",
                                     bg=COLORS['bg_secondary'], fg=COLORS['fg_primary'],
                                     font=FONTS['monospace'], justify=tk.LEFT, anchor='w')
        self.threat_label.pack(fill=tk.X)
        
        # Quick Stats
        stats_frame = ttk.LabelFrame(right_panel, text="QUICK STATS", style='Dark.TLabelframe', padding=10)
        stats_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.stats_label = tk.Label(stats_frame, text="Loading statistics...",
                                    bg=COLORS['bg_secondary'], fg=COLORS['fg_primary'],
                                    font=FONTS['monospace'], justify=tk.LEFT, anchor='w')
        self.stats_label.pack(fill=tk.X)
        
        # Breach Stream (Activity Log)
        breach_frame = ttk.LabelFrame(right_panel, text="BREACH STREAM", style='Dark.TLabelframe', padding=10)
        breach_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_viewer = LogViewer(breach_frame, height=200)
        self.log_viewer.pack(fill=tk.BOTH, expand=True)
        
        # Initialize logs
        self.log_viewer.add_log("[SYSTEM] Dashboard initialized", "INFO")
        self.log_viewer.add_log("[SYSTEM] Ready for attack operations", "INFO")
        self.log_viewer.add_log("[WARNING] Authorized use only", "WARNING")
    
    def _launch_tui(self):
        """Launch tactical TUI dashboard."""
        if hasattr(self.app, '_launch_tui'):
            self.app._launch_tui()
    
    def refresh_sessions(self):
        """Refresh session list."""
        self.log_viewer.add_log("[SYSTEM] Refreshing session list...", "INFO")
        
        def load():
            return self.store.list_sessions()
        
        def callback(result, error=None):
            if error:
                self.log_viewer.add_log(f"[ERROR] Failed to load sessions: {error}", "ERROR")
                return
            
            if result:
                self.all_sessions = result
                self._apply_filters()
                self.log_viewer.add_log(f"[SUCCESS] Loaded {len(result)} session(s)", "INFO")
            else:
                self.log_viewer.add_log("[WARNING] No sessions found", "WARNING")
                self.all_sessions = []
                self.session_list.load_sessions([])
                self._update_stats([])
                self._update_threat_summary([])
        
        run_async(load, callback)
    
    def _apply_filters(self):
        """Apply filters to session list."""
        search_query = self.search_var.get().strip()
        
        # Build filters
        filters = {}
        if search_query:
            filters['fuzzy_search'] = search_query
        
        # Apply filters
        filtered = self.filter_manager.filter_sessions(self.all_sessions, filters)
        
        # Update session list
        self.session_list.load_sessions(filtered)
        self._update_stats(filtered)
        self._update_threat_summary(filtered)
        
        if search_query:
            self.log_viewer.add_log(f"[FILTER] Filtered to {len(filtered)} session(s)", "INFO")
    
    def _update_stats(self, sessions):
        """Update statistics display."""
        total = len(sessions)
        active = len([s for s in sessions if s.get('status') == 'active'])
        completed = len([s for s in sessions if s.get('status') == 'completed'])
        
        # Count findings
        total_findings = 0
        critical_findings = 0
        for session in sessions:
            findings = session.get('findings', [])
            total_findings += len(findings)
            critical_findings += len([f for f in findings if f.get('confidence') == 'high' or f.get('severity') == 'critical'])
        
        stats_text = f"TOTAL SESSIONS: {total}\n"
        stats_text += f"ACTIVE: {active} | COMPLETED: {completed}\n"
        stats_text += f"TOTAL FINDINGS: {total_findings}\n"
        stats_text += f"CRITICAL: {critical_findings}"
        
        self.stats_label.config(text=stats_text)
    
    def _update_threat_summary(self, sessions):
        """Update threat summary display."""
        if not sessions:
            threat_text = "NO ACTIVE SESSIONS\n"
            threat_text += "Risk assessment unavailable"
            self.threat_label.config(text=threat_text, fg=COLORS['fg_secondary'])
            return
        
        # Calculate threat metrics
        total_endpoints = 0
        total_findings = 0
        high_confidence = 0
        
        for session in sessions:
            crawl_data = session.get('crawl_results', {})
            total_endpoints += len(crawl_data.get('endpoints_discovered', []))
            findings = session.get('findings', [])
            total_findings += len(findings)
            high_confidence += len([f for f in findings if f.get('confidence') == 'high'])
        
        threat_text = f"ATTACK SURFACE: {total_endpoints} endpoints\n"
        threat_text += f"VULNERABILITIES: {total_findings} detected\n"
        threat_text += f"HIGH CONFIDENCE: {high_confidence} findings\n"
        
        if high_confidence > 0:
            threat_text += "\n[!] CRITICAL THREATS DETECTED"
            self.threat_label.config(text=threat_text, fg=COLORS['accent_red'])
        else:
            threat_text += "\n[?] No high-confidence threats"
            self.threat_label.config(text=threat_text, fg=COLORS['accent_yellow'])
    
    def _on_session_select(self, session_id: str):
        """Handle session selection."""
        self.selected_session_id = session_id
        self.log_viewer.add_log(f"[SELECT] Session selected: {session_id}", "INFO")
        
        # Update threat summary for selected session
        session_data = self.store.load_session(session_id)
        if session_data:
            self._update_threat_summary([session_data])
    
    def _new_scan(self):
        """Open new attack scan window."""
        scan_window = ScanWindow(self.app.root, self.app)
    
    def _view_report(self):
        """View report for selected session."""
        session_id = self.session_list.get_selected_session_id()
        if not session_id:
            show_info("Please select a session first", self.app.root)
            return
        
        report_window = ReportWindow(self.app.root, self.app, session_id)
    
    def _visualize(self):
        """Open visualization for selected session."""
        session_id = self.session_list.get_selected_session_id()
        if not session_id:
            show_info("Please select a session first", self.app.root)
            return
        
        viz_window = VisualizationWindow(self.app.root, self.app, session_id)
    
    def _delete_session(self):
        """Delete selected session."""
        session_id = self.session_list.get_selected_session_id()
        if not session_id:
            show_info("Please select a session first", self.app.root)
            return
        
        from gui.utils import ask_confirmation
        if ask_confirmation(f"Delete session {session_id}?", self.app.root):
            if self.store.delete_session(session_id):
                self.log_viewer.add_log(f"[DELETE] Session deleted: {session_id}", "INFO")
                self.refresh_sessions()
            else:
                self.log_viewer.add_log(f"[ERROR] Failed to delete session: {session_id}", "ERROR")
