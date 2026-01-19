"""
Dashboard window for PROJEK DENGKIS GUI.
Main interface showing session list and quick stats.
"""
import tkinter as tk
from tkinter import ttk
from typing import Optional, List, Dict
import threading

from gui.components.session_list import SessionList
from gui.components.log_viewer import LogViewer
from gui.scan_window import ScanWindow
from gui.visualization_window import VisualizationWindow
from gui.report_window import ReportWindow
from engine.storage.session_store import SessionStore
from engine.logging.logger import get_logger
from engine.filters.search import FilterManager
from gui.utils import run_async, show_info


class DashboardWindow(ttk.Frame):
    """Main dashboard window."""
    
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.logger = get_logger()
        self.store = SessionStore()
        self.filter_manager = FilterManager()
        self.all_sessions: List[Dict] = []
        
        # Create layout
        self._create_layout()
        
        # Load sessions
        self.refresh_sessions()
    
    def _create_layout(self):
        """Create dashboard layout."""
        # Header frame
        header_frame = ttk.Frame(self)
        header_frame.pack(fill=tk.X, padx=10, pady=10)
        
        title_label = ttk.Label(header_frame, text="PROJEK DENGKIS Dashboard", font=('Arial', 16, 'bold'))
        title_label.pack(side=tk.LEFT)
        
        refresh_btn = ttk.Button(header_frame, text="Refresh", command=self.refresh_sessions)
        refresh_btn.pack(side=tk.RIGHT, padx=5)
        
        new_scan_btn = ttk.Button(header_frame, text="New Scan", command=self._new_scan)
        new_scan_btn.pack(side=tk.RIGHT, padx=5)
        
        # Main content area
        content_frame = ttk.Frame(self)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel - Sessions
        left_panel = ttk.LabelFrame(content_frame, text="Sessions", padding=10)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Filter frame
        filter_frame = ttk.Frame(left_panel)
        filter_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(filter_frame, text="Search:").pack(side=tk.LEFT, padx=5)
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(filter_frame, textvariable=self.search_var, width=20)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        search_entry.bind('<KeyRelease>', lambda e: self._apply_filters())
        
        ttk.Button(filter_frame, text="Filter", command=self._apply_filters).pack(side=tk.RIGHT, padx=5)
        
        self.session_list = SessionList(left_panel, on_select=self._on_session_select)
        self.session_list.pack(fill=tk.BOTH, expand=True)
        
        # Session buttons
        session_buttons = ttk.Frame(left_panel)
        session_buttons.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(session_buttons, text="View Report", command=self._view_report).pack(side=tk.LEFT, padx=2)
        ttk.Button(session_buttons, text="Visualize", command=self._visualize).pack(side=tk.LEFT, padx=2)
        ttk.Button(session_buttons, text="Delete", command=self._delete_session).pack(side=tk.LEFT, padx=2)
        
        # Right panel - Stats and Logs
        right_panel = ttk.Frame(content_frame)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # Stats frame
        stats_frame = ttk.LabelFrame(right_panel, text="Quick Statistics", padding=10)
        stats_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.stats_label = ttk.Label(stats_frame, text="Loading statistics...")
        self.stats_label.pack()
        
        # Logs frame
        logs_frame = ttk.LabelFrame(right_panel, text="Recent Activity", padding=10)
        logs_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_viewer = LogViewer(logs_frame, height=200)
        self.log_viewer.pack(fill=tk.BOTH, expand=True)
        
        # Initialize logs
        self.log_viewer.add_log("Dashboard initialized", "INFO")
        self.log_viewer.add_log("Ready for assessments", "INFO")
    
    def refresh_sessions(self):
        """Refresh session list."""
        def load():
            return self.store.list_sessions()
        
        def callback(result, error=None):
            if error:
                self.log_viewer.add_log(f"Error loading sessions: {error}", "ERROR")
                return
            
            if result:
                self.all_sessions = result
                self._apply_filters()
            else:
                self.log_viewer.add_log("No sessions found", "WARNING")
                self.all_sessions = []
                self.session_list.load_sessions([])
        
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
        
        if search_query:
            self.log_viewer.add_log(f"Filtered to {len(filtered)} session(s)", "INFO")
    
    def _update_stats(self, sessions):
        """Update statistics display."""
        total = len(sessions)
        active = len([s for s in sessions if s.get('status') == 'active'])
        completed = len([s for s in sessions if s.get('status') == 'completed'])
        
        stats_text = f"Total Sessions: {total}\nActive: {active}\nCompleted: {completed}"
        self.stats_label.config(text=stats_text)
    
    def _on_session_select(self, session_id: str):
        """Handle session selection."""
        self.log_viewer.add_log(f"Selected session: {session_id}", "INFO")
    
    def _new_scan(self):
        """Open new scan window."""
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
                self.log_viewer.add_log(f"Deleted session: {session_id}", "INFO")
                self.refresh_sessions()
            else:
                self.log_viewer.add_log(f"Failed to delete session: {session_id}", "ERROR")
