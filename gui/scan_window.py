"""
ATTACK SCAN WINDOW - Configure and launch aggressive attacks.
Tactical interface with access to all attack modules.
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
from gui.theme import COLORS, FONTS
from gui.utils import run_async, ProgressDialog, show_error, show_info
from gui.monitor_window import MonitorWindow


class ScanWindow(tk.Toplevel):
    """Attack configuration and execution window."""
    
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.logger = get_logger()
        self.store = SessionStore()
        
        # Apply dark theme
        self.configure(bg=COLORS['bg_primary'])
        
        self.title("DENGKIS // ATTACK CONFIGURATION")
        self.geometry("800x700")
        self.transient(parent)
        self.grab_set()
        
        # Center window
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (800 // 2)
        y = (self.winfo_screenheight() // 2) - (700 // 2)
        self.geometry(f"800x700+{x}+{y}")
        
        self._create_layout()
    
    def _create_layout(self):
        """Create attack configuration layout."""
        # Header
        header_frame = tk.Frame(self, bg=COLORS['bg_primary'], height=60)
        header_frame.pack(fill=tk.X, padx=10, pady=10)
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(header_frame, text="[ATTACK CONFIGURATION]", 
                              bg=COLORS['bg_primary'], fg=COLORS['accent_red'],
                              font=FONTS['monospace_large'])
        title_label.pack()
        
        # Main notebook for tabs
        notebook = ttk.Notebook(self, style='Dark.TNotebook')
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tab 1: Basic Configuration
        basic_frame = ttk.Frame(notebook, style='Dark.TFrame')
        notebook.add(basic_frame, text="[BASIC]")
        self._create_basic_tab(basic_frame)
        
        # Tab 2: Attack Modes
        attack_frame = ttk.Frame(notebook, style='Dark.TFrame')
        notebook.add(attack_frame, text="[ATTACK MODES]")
        self._create_attack_tab(attack_frame)
        
        # Tab 3: Advanced Modules
        advanced_frame = ttk.Frame(notebook, style='Dark.TFrame')
        notebook.add(advanced_frame, text="[ADVANCED MODULES]")
        self._create_advanced_tab(advanced_frame)
        
        # Tab 4: Performance
        perf_frame = ttk.Frame(notebook, style='Dark.TFrame')
        notebook.add(perf_frame, text="[PERFORMANCE]")
        self._create_performance_tab(perf_frame)
        
        # Action buttons
        button_frame = tk.Frame(self, bg=COLORS['bg_primary'])
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(button_frame, text="[LAUNCH ATTACK]", command=self._start_attack,
                  style='Danger.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="[CANCEL]", command=self.destroy,
                  style='Dark.TButton').pack(side=tk.LEFT, padx=5)
    
    def _create_basic_tab(self, parent):
        """Create basic configuration tab."""
        main_frame = ttk.LabelFrame(parent, text="TARGET CONFIGURATION", 
                                    style='Dark.TLabelframe', padding=15)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Target input
        target_frame = ttk.Frame(main_frame, style='Dark.TFrame')
        target_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(target_frame, text="[TARGET URL]", bg=COLORS['bg_secondary'], 
                fg=COLORS['accent_red'], font=FONTS['monospace_bold']).pack(side=tk.LEFT, padx=5)
        self.target_var = tk.StringVar()
        target_entry = ttk.Entry(target_frame, textvariable=self.target_var, width=50, style='Dark.TEntry')
        target_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Authorization
        auth_frame = ttk.Frame(main_frame, style='Dark.TFrame')
        auth_frame.pack(fill=tk.X, pady=10)
        
        self.auth_var = tk.BooleanVar()
        auth_check = ttk.Checkbutton(auth_frame, 
                                     text="[AUTHORIZED] I have explicit permission to test this target",
                                     variable=self.auth_var, style='Dark.TCheckbutton')
        auth_check.pack(anchor=tk.W, padx=5)
        
        # Network options
        network_frame = ttk.LabelFrame(main_frame, text="NETWORK OPTIONS", 
                                      style='Dark.TLabelframe', padding=10)
        network_frame.pack(fill=tk.X, pady=10)
        
        # Timeout
        timeout_frame = ttk.Frame(network_frame, style='Dark.TFrame')
        timeout_frame.pack(fill=tk.X, pady=5)
        tk.Label(timeout_frame, text="Timeout (sec):", bg=COLORS['bg_secondary'], 
                fg=COLORS['fg_primary'], font=FONTS['monospace']).pack(side=tk.LEFT, padx=5)
        self.timeout_var = tk.StringVar(value="30.0")
        ttk.Entry(timeout_frame, textvariable=self.timeout_var, width=10, style='Dark.TEntry').pack(side=tk.LEFT, padx=5)
        
        # Max retries
        retry_frame = ttk.Frame(network_frame, style='Dark.TFrame')
        retry_frame.pack(fill=tk.X, pady=5)
        tk.Label(retry_frame, text="Max Retries:", bg=COLORS['bg_secondary'], 
                fg=COLORS['fg_primary'], font=FONTS['monospace']).pack(side=tk.LEFT, padx=5)
        self.retries_var = tk.StringVar(value="3")
        ttk.Entry(retry_frame, textvariable=self.retries_var, width=10, style='Dark.TEntry').pack(side=tk.LEFT, padx=5)
        
        # Rate limit
        rate_frame = ttk.Frame(network_frame, style='Dark.TFrame')
        rate_frame.pack(fill=tk.X, pady=5)
        tk.Label(rate_frame, text="Rate Limit (req/sec):", bg=COLORS['bg_secondary'], 
                fg=COLORS['fg_primary'], font=FONTS['monospace']).pack(side=tk.LEFT, padx=5)
        self.rate_limit_var = tk.StringVar(value="10.0")
        ttk.Entry(rate_frame, textvariable=self.rate_limit_var, width=10, style='Dark.TEntry').pack(side=tk.LEFT, padx=5)
    
    def _create_attack_tab(self, parent):
        """Create attack mode configuration tab."""
        main_frame = ttk.LabelFrame(parent, text="ATTACK MODE SELECTION", 
                                    style='Dark.TLabelframe', padding=15)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Attack mode selection
        mode_frame = ttk.LabelFrame(main_frame, text="MODE", style='Dark.TLabelframe', padding=10)
        mode_frame.pack(fill=tk.X, pady=10)
        
        self.attack_mode_var = tk.StringVar(value="aggressive")
        
        modes = [
            ("PASSIVE", "passive", "Passive reconnaissance only"),
            ("ACTIVE", "active", "Active payload injection"),
            ("AGGRESSIVE", "aggressive", "Full exploitation (DEFAULT)")
        ]
        
        for label, value, desc in modes:
            frame = ttk.Frame(mode_frame, style='Dark.TFrame')
            frame.pack(fill=tk.X, pady=5)
            
            radio = ttk.Radiobutton(frame, text=label, variable=self.attack_mode_var, 
                                   value=value, style='Dark.TRadiobutton')
            radio.pack(side=tk.LEFT, padx=5)
            
            tk.Label(frame, text=desc, bg=COLORS['bg_secondary'], fg=COLORS['fg_secondary'],
                    font=FONTS['monospace_small']).pack(side=tk.LEFT, padx=10)
        
        # Payload categories
        payload_frame = ttk.LabelFrame(main_frame, text="PAYLOAD CATEGORIES", 
                                       style='Dark.TLabelframe', padding=10)
        payload_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.payload_vars = {}
        categories = [
            ("SQL Injection", "sqli"),
            ("XSS", "xss"),
            ("SSTI", "ssti"),
            ("Command Injection", "rce"),
            ("LFI/Path Traversal", "lfi"),
            ("Auth Bypass", "auth"),
            ("Open Redirect", "redirect"),
            ("Prototype Pollution", "prototype"),
            ("Mass Assignment", "mass_assignment")
        ]
        
        for i, (label, key) in enumerate(categories):
            var = tk.BooleanVar(value=True)
            self.payload_vars[key] = var
            check = ttk.Checkbutton(payload_frame, text=label, variable=var, 
                                   style='Dark.TCheckbutton')
            check.grid(row=i//3, column=i%3, sticky=tk.W, padx=10, pady=5)
    
    def _create_advanced_tab(self, parent):
        """Create advanced modules configuration tab."""
        main_frame = ttk.LabelFrame(parent, text="ADVANCED ATTACK MODULES", 
                                    style='Dark.TLabelframe', padding=15)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Flag Hunter (CTF Automation)
        flag_frame = ttk.LabelFrame(main_frame, text="FLAG HUNTER", style='Dark.TLabelframe', padding=10)
        flag_frame.pack(fill=tk.X, pady=5)
        
        self.flag_hunter_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(flag_frame, text="Enable CTF flag hunting (regex search, env dumps, config crawls)",
                       variable=self.flag_hunter_var, style='Dark.TCheckbutton').pack(anchor=tk.W)
        
        # Ghost Operator (WAF Evasion)
        ghost_frame = ttk.LabelFrame(main_frame, text="GHOST OPERATOR", style='Dark.TLabelframe', padding=10)
        ghost_frame.pack(fill=tk.X, pady=5)
        
        self.ghost_operator_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(ghost_frame, text="Enable WAF/EDR evasion (encoding, fragmentation, user-agent rotation)",
                       variable=self.ghost_operator_var, style='Dark.TCheckbutton').pack(anchor=tk.W)
        
        # Logic Breaker (Business Logic)
        logic_frame = ttk.LabelFrame(main_frame, text="LOGIC BREAKER", style='Dark.TLabelframe', padding=10)
        logic_frame.pack(fill=tk.X, pady=5)
        
        self.logic_breaker_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(logic_frame, text="Enable business logic testing (integer overflow, race conditions, IDOR)",
                       variable=self.logic_breaker_var, style='Dark.TCheckbutton').pack(anchor=tk.W)
        
        # Red Team Architect (Post-Exploitation)
        redteam_frame = ttk.LabelFrame(main_frame, text="RED TEAM ARCHITECT", style='Dark.TLabelframe', padding=10)
        redteam_frame.pack(fill=tk.X, pady=5)
        
        self.redteam_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(redteam_frame, text="Enable post-exploitation (network discovery, credential scavenging, lateral movement)",
                        variable=self.redteam_var, style='Dark.TCheckbutton').pack(anchor=tk.W)
        
        # Attacker Mindset (Reporting)
        mindset_frame = ttk.LabelFrame(main_frame, text="ATTACKER MINDSET", style='Dark.TLabelframe', padding=10)
        mindset_frame.pack(fill=tk.X, pady=5)
        
        self.mindset_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(mindset_frame, text="Enable attacker-style intelligence reports (kill chain, PoC generation)",
                       variable=self.mindset_var, style='Dark.TCheckbutton').pack(anchor=tk.W)
    
    def _create_performance_tab(self, parent):
        """Create performance optimization tab."""
        main_frame = ttk.LabelFrame(parent, text="PERFORMANCE OPTIMIZATION", 
                                    style='Dark.TLabelframe', padding=15)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Kernel optimization
        kernel_frame = ttk.LabelFrame(main_frame, text="KERNEL TUNING", style='Dark.TLabelframe', padding=10)
        kernel_frame.pack(fill=tk.X, pady=5)
        
        self.kernel_opt_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(kernel_frame, text="Apply kernel-level optimizations (ulimit, TCP tuning)",
                       variable=self.kernel_opt_var, style='Dark.TCheckbutton').pack(anchor=tk.W)
        
        # Zero-copy processing
        zerocopy_frame = ttk.LabelFrame(main_frame, text="ZERO-COPY PROCESSING", style='Dark.TLabelframe', padding=10)
        zerocopy_frame.pack(fill=tk.X, pady=5)
        
        self.zerocopy_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(zerocopy_frame, text="Enable zero-copy processing (mmap, ujson)",
                        variable=self.zerocopy_var, style='Dark.TCheckbutton').pack(anchor=tk.W)
        
        # GPU acceleration
        gpu_frame = ttk.LabelFrame(main_frame, text="GPU ACCELERATION", style='Dark.TLabelframe', padding=10)
        gpu_frame.pack(fill=tk.X, pady=5)
        
        self.gpu_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(gpu_frame, text="Enable GPU acceleration (PyOpenCL/CuPy) - if available",
                        variable=self.gpu_var, style='Dark.TCheckbutton').pack(anchor=tk.W)
    
    def _start_attack(self):
        """Start attack scan."""
        target = self.target_var.get().strip()
        authorized = self.auth_var.get()
        attack_mode = self.attack_mode_var.get()
        
        if not target:
            show_error("Please enter a target URL", self)
            return
        
        if not authorized:
            show_error("Authorization is REQUIRED to launch attacks", self)
            return
        
        # Validate numeric inputs
        try:
            timeout = float(self.timeout_var.get())
            max_retries = int(self.retries_var.get())
            rate_limit = float(self.rate_limit_var.get())
        except ValueError:
            show_error("Invalid numeric values in network options", self)
            return
        
        # Apply performance optimizations if requested
        if self.kernel_opt_var.get():
            try:
                from engine.performance.optimizer import PerformanceOptimizer
                optimizer = PerformanceOptimizer()
                optimizer.optimize_environment()
            except Exception as e:
                self.logger.warning(f"Failed to apply kernel optimizations: {e}")
        
        # Close this window
        self.destroy()
        
        # Show progress
        progress = ProgressDialog(self.app.root, "Launching Attack")
        
        def run_attack():
            """Run attack in async context."""
            try:
                # Run assessment with attack mode
                assessment_result = run_assessment(target, authorized=authorized, attack_mode=attack_mode)
                
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
                
                # Store session with advanced module flags
                session_data = {
                    'session_id': session_id,
                    'target': target,
                    'started_at': assessment_result.get('started_at'),
                    'status': 'completed',
                    'attack_mode': attack_mode,
                    'advanced_modules': {
                        'flag_hunter': self.flag_hunter_var.get(),
                        'ghost_operator': self.ghost_operator_var.get(),
                        'logic_breaker': self.logic_breaker_var.get(),
                        'red_team_architect': self.redteam_var.get(),
                        'attacker_mindset': self.mindset_var.get()
                    },
                    'findings': assessment_result.get('findings', [])
                }
                
                self.store.save_session(session_data, session_id)
                return session_id, None
            
            except Exception as e:
                return None, str(e)
        
        def callback(result, error=None):
            """Handle attack completion."""
            progress.close()
            
            if error:
                show_error(f"Attack failed: {error}", self.app.root)
                return
            
            if result:
                session_id, attack_error = result
                if attack_error:
                    show_error(f"Attack failed: {attack_error}", self.app.root)
                else:
                    show_info(f"Attack completed!\nSession ID: {session_id}", self.app.root)
                    # Open monitor window
                    monitor = MonitorWindow(self.app.root, self.app, session_id)
                    # Refresh dashboard
                    if hasattr(self.app, 'dashboard'):
                        self.app.dashboard.refresh_sessions()
        
        # Run attack in thread
        run_async(run_attack, callback)
