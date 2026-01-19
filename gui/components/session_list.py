"""
Session list component for GUI.
Displays list of saved sessions with dark theme.
"""
import tkinter as tk
from tkinter import ttk
from typing import Dict, List, Optional, Callable
from datetime import datetime

from gui.theme import COLORS, FONTS


class SessionList(ttk.Frame):
    """Session list component with selection and dark theme."""
    
    def __init__(self, parent, on_select: Optional[Callable] = None):
        super().__init__(parent, style='Dark.TFrame')
        
        self.on_select = on_select
        self.sessions: List[Dict] = []
        
        # Treeview for session list with dark theme
        columns = ('Session ID', 'Target', 'Status', 'Started At', 'Findings')
        self.tree = ttk.Treeview(self, columns=columns, show='headings', height=10, style='Dark.Treeview')
        
        # Configure columns
        self.tree.heading('Session ID', text='SESSION ID')
        self.tree.heading('Target', text='TARGET')
        self.tree.heading('Status', text='STATUS')
        self.tree.heading('Started At', text='STARTED')
        self.tree.heading('Findings', text='FINDINGS')
        
        self.tree.column('Session ID', width=200)
        self.tree.column('Target', width=200)
        self.tree.column('Status', width=100)
        self.tree.column('Started At', width=150)
        self.tree.column('Findings', width=80)
        
        # Scrollbar with dark theme
        scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.tree.yview, style='Dark.Vertical.TScrollbar')
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind selection
        self.tree.bind('<<TreeviewSelect>>', self._on_selection)
    
    def _on_selection(self, event):
        """Handle selection event."""
        selection = self.tree.selection()
        if selection and self.on_select:
            item = self.tree.item(selection[0])
            session_id = item['values'][0]
            self.on_select(session_id)
    
    def load_sessions(self, sessions: List[Dict]):
        """Load sessions into list."""
        self.sessions = sessions
        self.tree.delete(*self.tree.get_children())
        
        for session in sessions:
            findings = session.get('findings', [])
            findings_count = len(findings)
            self.tree.insert('', tk.END, values=(
                session.get('session_id', ''),
                session.get('target', ''),
                session.get('status', ''),
                session.get('started_at', ''),
                str(findings_count)
            ))
    
    def get_selected_session_id(self) -> Optional[str]:
        """Get selected session ID."""
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            return item['values'][0]
        return None
    
    def refresh(self):
        """Refresh session list."""
        if self.sessions:
            self.load_sessions(self.sessions)
