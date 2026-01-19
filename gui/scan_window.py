"""
Scan input window for PROJEK DENGKIS GUI.
Allows users to configure and start security assessments.
"""
import tkinter as tk
from tkinter import ttk
import asyncio
import threading

from engine.runner import run_assessment
from engine.network.request_handler import AggressiveRequestHandler
from engine.utils.retry import RetryConfig
from engine.utils.throttle import ThrottleConfig
from engine.storage.session_store import SessionStore
from engine.logging.logger import get_logger
from gui.utils import run_async, ProgressDialog, show_error, show_info
from gui.monitor_window import MonitorWindow


class ScanWindow(tk.Toplevel):
    """Scan configuration and execution window."""
    
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.logger = get_logger()
        self.store = SessionStore()
        
        self.title("New Security Assessment")
        self.geometry("600x500")
        self.transient(parent)
        self.grab_set()
        
        # Center window
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.winfo_screenheight() // 2) - (500 // 2)
        self.geometry(f"600x500+{x}+{y}")
        
        self._create_layout()
    
    def _create_layout(self):
        """Create scan window layout."""
        # Main frame
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Target input
        ttk.Label(main_frame, text="Target:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.target_var = tk.StringVar()
        target_entry = ttk.Entry(main_frame, textvariable=self.target_var, width=40)
        target_entry.grid(row=0, column=1, columnspan=2, sticky=tk.EW, pady=5)
        
        # Authorization checkbox
        self.auth_var = tk.BooleanVar()
        auth_check = ttk.Checkbutton(
            main_frame,
            text="I have authorization to test this target",
            variable=self.auth_var
        )
        auth_check.grid(row=1, column=0, columnspan=3, sticky=tk.W, pady=10)
        
        # Options frame
        options_frame = ttk.LabelFrame(main_frame, text="Scan Options", padding=10)
        options_frame.grid(row=2, column=0, columnspan=3, sticky=tk.EW, pady=10)
        
        # Stealth mode
        self.stealth_var = tk.BooleanVar()
        ttk.Checkbutton(options_frame, text="Stealth Mode", variable=self.stealth_var).pack(anchor=tk.W)
        
        # Timeout
        ttk.Label(options_frame, text="Timeout (seconds):").pack(anchor=tk.W, pady=2)
        self.timeout_var = tk.StringVar(value="30.0")
        ttk.Entry(options_frame, textvariable=self.timeout_var, width=10).pack(anchor=tk.W)
        
        # Max retries
        ttk.Label(options_frame, text="Max Retries:").pack(anchor=tk.W, pady=2)
        self.retries_var = tk.StringVar(value="3")
        ttk.Entry(options_frame, textvariable=self.retries_var, width=10).pack(anchor=tk.W)
        
        # Rate limit
        ttk.Label(options_frame, text="Rate Limit (req/sec):").pack(anchor=tk.W, pady=2)
        self.rate_limit_var = tk.StringVar(value="10.0")
        ttk.Entry(options_frame, textvariable=self.rate_limit_var, width=10).pack(anchor=tk.W)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=3, pady=20)
        
        ttk.Button(button_frame, text="Start Scan", command=self._start_scan).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.destroy).pack(side=tk.LEFT, padx=5)
        
        main_frame.columnconfigure(1, weight=1)
    
    def _start_scan(self):
        """Start security assessment."""
        target = self.target_var.get().strip()
        authorized = self.auth_var.get()
        
        if not target:
            show_error("Please enter a target", self)
            return
        
        if not authorized:
            show_error("Authorization is required to run assessments", self)
            return
        
        # Validate numeric inputs
        try:
            timeout = float(self.timeout_var.get())
            max_retries = int(self.retries_var.get())
            rate_limit = float(self.rate_limit_var.get())
        except ValueError:
            show_error("Invalid numeric values in options", self)
            return
        
        # Close this window
        self.destroy()
        
        # Show progress
        progress = ProgressDialog(self.app.root, "Starting Assessment")
        
        def run_scan():
            """Run scan in async context."""
            try:
                # Initialize assessment
                assessment_result = run_assessment(target, authorized=authorized)
                
                if assessment_result.get('status') == 'error':
                    return None, assessment_result.get('message')
                
                session_id = assessment_result.get('session_id')
                
                # Configure retry and throttle
                retry_config = RetryConfig(
                    max_attempts=max_retries,
                    timeout=timeout
                )
                throttle_config = ThrottleConfig(
                    requests_per_second=rate_limit
                )
                
                # Run async scan
                async def scan_task():
                    async with AggressiveRequestHandler(
                        stealth_mode=self.stealth_var.get(),
                        timeout=timeout,
                        retry_config=retry_config,
                        throttle_config=throttle_config,
                        session_id=session_id
                    ) as handler:
                        # Extract behavioral fingerprint
                        fingerprint = await handler.extract_behavioral_fingerprint(target)
                        
                        # Store session
                        session_data = {
                            'session_id': session_id,
                            'target': target,
                            'started_at': assessment_result.get('started_at'),
                            'status': 'completed',
                            'fingerprint': fingerprint,
                            'findings': []
                        }
                        
                        self.store.save_session(session_data, session_id)
                        return session_id, None
                
                # Run async task
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    return loop.run_until_complete(scan_task())
                finally:
                    loop.close()
            
            except Exception as e:
                return None, str(e)
        
        def callback(result, error=None):
            """Handle scan completion."""
            progress.close()
            
            if error:
                show_error(f"Scan failed: {error}", self.app.root)
                return
            
            if result:
                session_id, scan_error = result
                if scan_error:
                    show_error(f"Scan failed: {scan_error}", self.app.root)
                else:
                    show_info(f"Scan completed!\nSession ID: {session_id}", self.app.root)
                    # Open monitor window
                    monitor = MonitorWindow(self.app.root, self.app, session_id)
                    # Refresh dashboard
                    if hasattr(self.app, 'dashboard'):
                        self.app.dashboard.refresh_sessions()
        
        # Run scan in thread
        run_async(run_scan, callback)
