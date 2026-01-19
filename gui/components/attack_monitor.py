"""
Live Attack Monitor - Real-time progress display for active attacks.
Shows exploitation progress, successes, and failures.
"""
import tkinter as tk
from tkinter import ttk
from typing import Dict, List, Optional
from datetime import datetime
import threading

from gui.theme import COLORS, FONTS


class AttackMonitor(ttk.Frame):
    """Real-time attack progress monitor."""
    
    def __init__(self, parent):
        super().__init__(parent, style='Dark.TFrame')
        self.progress_updates: List[Dict] = []
        self.exploits_successful: List[Dict] = []
        self.exploits_failed: List[Dict] = []
        
        self._create_layout()
    
    def _create_layout(self):
        """Create monitor layout."""
        # Header
        header = tk.Label(self, text="[LIVE ATTACK MONITOR]", 
                         bg=COLORS['bg_primary'], fg=COLORS['accent_red'],
                         font=FONTS['monospace_large'])
        header.pack(pady=10)
        
        # Stats frame
        stats_frame = ttk.LabelFrame(self, text="ATTACK STATISTICS", 
                                     style='Dark.TLabelframe', padding=10)
        stats_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.stats_label = tk.Label(stats_frame, text="Initializing attack...",
                                    bg=COLORS['bg_secondary'], fg=COLORS['fg_primary'],
                                    font=FONTS['monospace'])
        self.stats_label.pack()
        
        # Progress stream
        progress_frame = ttk.LabelFrame(self, text="ATTACK PROGRESS", 
                                       style='Dark.TLabelframe', padding=10)
        progress_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Progress text with scrollbar
        text_frame = tk.Frame(progress_frame, bg=COLORS['bg_secondary'])
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        self.progress_text = tk.Text(text_frame, height=15, wrap=tk.WORD,
                                     bg=COLORS['bg_tertiary'], fg=COLORS['fg_primary'],
                                     font=FONTS['monospace_small'],
                                     insertbackground=COLORS['accent_red'],
                                     selectbackground=COLORS['selection'],
                                     selectforeground=COLORS['accent_red'],
                                     borderwidth=1, relief='solid')
        
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, 
                                  command=self.progress_text.yview,
                                  style='Dark.Vertical.TScrollbar')
        self.progress_text.configure(yscrollcommand=scrollbar.set)
        
        self.progress_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Configure text tags
        self.progress_text.tag_config('info', foreground=COLORS['accent_blue'])
        self.progress_text.tag_config('attack', foreground=COLORS['accent_yellow'])
        self.progress_text.tag_config('success', foreground=COLORS['accent_green'])
        self.progress_text.tag_config('error', foreground=COLORS['accent_red'])
        self.progress_text.tag_config('warning', foreground=COLORS['accent_orange'])
        
        # Success/Failure summary
        summary_frame = ttk.LabelFrame(self, text="EXPLOITATION RESULTS", 
                                      style='Dark.TLabelframe', padding=10)
        summary_frame.pack(fill=tk.X, padx=10, pady=5)
        
        results_frame = tk.Frame(summary_frame, bg=COLORS['bg_secondary'])
        results_frame.pack(fill=tk.X)
        
        self.success_label = tk.Label(results_frame, text="SUCCESS: 0", 
                                     bg=COLORS['bg_secondary'], fg=COLORS['accent_green'],
                                     font=FONTS['monospace_bold'])
        self.success_label.pack(side=tk.LEFT, padx=10)
        
        self.failure_label = tk.Label(results_frame, text="FAILED: 0", 
                                     bg=COLORS['bg_secondary'], fg=COLORS['accent_red'],
                                     font=FONTS['monospace_bold'])
        self.failure_label.pack(side=tk.LEFT, padx=10)
        
        self.total_label = tk.Label(results_frame, text="TOTAL: 0", 
                                   bg=COLORS['bg_secondary'], fg=COLORS['fg_primary'],
                                   font=FONTS['monospace_bold'])
        self.total_label.pack(side=tk.LEFT, padx=10)
    
    def add_progress(self, message: str, status: str = "info", data: Optional[Dict] = None):
        """Add progress update."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] [{status.upper()}] {message}\n"
        
        self.progress_text.config(state=tk.NORMAL)
        self.progress_text.insert(tk.END, formatted_message, status)
        self.progress_text.see(tk.END)
        self.progress_text.config(state=tk.DISABLED)
        
        self.progress_updates.append({
            "timestamp": timestamp,
            "message": message,
            "status": status,
            "data": data
        })
        
        # Update stats
        self._update_stats()
    
    def add_success(self, exploit_result: Dict):
        """Add successful exploitation."""
        self.exploits_successful.append(exploit_result)
        exploit_type = exploit_result.get("exploit_type", "unknown")
        endpoint = exploit_result.get("endpoint", "unknown")
        self.add_progress(f"EXPLOIT SUCCESS: {exploit_type} on {endpoint}", "success", exploit_result)
        self._update_stats()
    
    def add_failure(self, failure: Dict):
        """Add failed exploitation with reason."""
        self.exploits_failed.append(failure)
        exploit_type = failure.get("exploit_type", "unknown")
        endpoint = failure.get("endpoint", "unknown")
        reason = failure.get("reason", "Unknown error")
        self.add_progress(f"EXPLOIT FAILED: {exploit_type} on {endpoint} - REASON: {reason}", "error", failure)
        self._update_stats()
    
    def _update_stats(self):
        """Update statistics display."""
        total = len(self.exploits_successful) + len(self.exploits_failed)
        successful = len(self.exploits_successful)
        failed = len(self.exploits_failed)
        
        stats_text = f"Total Exploits: {total} | Successful: {successful} | Failed: {failed} | Updates: {len(self.progress_updates)}"
        self.stats_label.config(text=stats_text)
        
        self.success_label.config(text=f"SUCCESS: {successful}")
        self.failure_label.config(text=f"FAILED: {failed}")
        self.total_label.config(text=f"TOTAL: {total}")
    
    def clear(self):
        """Clear all progress."""
        self.progress_text.config(state=tk.NORMAL)
        self.progress_text.delete(1.0, tk.END)
        self.progress_text.config(state=tk.DISABLED)
        self.progress_updates.clear()
        self.exploits_successful.clear()
        self.exploits_failed.clear()
        self._update_stats()
