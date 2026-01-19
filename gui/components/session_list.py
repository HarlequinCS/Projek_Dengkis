"""
Session list component for GUI.
Displays list of saved sessions.
"""
import tkinter as tk
from tkinter import ttk
from typing import List, Dict, Optional, Callable
from datetime import datetime


class SessionList(ttk.Frame):
    """Session list component with selection."""
    
    def __init__(self, parent, on_select: Optional[Callable] = None):
        super().__init__(parent)
        
        self.on_select = on_select
        self.sessions: List[Dict] = []
        
        # Treeview for session list
        columns = ('Session ID', 'Target', 'Status', 'Started At')
        self.tree = ttk.Treeview(self, columns=columns, show='headings', height=10)
        
        # Configure columns
        self.tree.heading('Session ID', text='Session ID')
        self.tree.heading('Target', text='Target')
        self.tree.heading('Status', text='Status')
        self.tree.heading('Started At', text='Started At')
        
        self.tree.column('Session ID', width=250)
        self.tree.column('Target', width=200)
        self.tree.column('Status', width=100)
        self.tree.column('Started At', width=200)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.tree.yview)
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
            self.tree.insert('', tk.END, values=(
                session.get('session_id', ''),
                session.get('target', ''),
                session.get('status', ''),
                session.get('started_at', '')
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
