"""
ATTACK SCAN WINDOW - Configure and launch aggressive attacks.
Tactical interface with access to all attack modules.
"""
import tkinter as tk
from tkinter import ttk
import asyncio
import threading
from typing import Dict

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
        
        # Tab 1: Operation Mode
        mode_frame = ttk.Frame(notebook, style='Dark.TFrame')
        notebook.add(mode_frame, text="[MODE]")
        self._create_mode_tab(mode_frame)
        
        # Tab 2: Basic Configuration
        basic_frame = ttk.Frame(notebook, style='Dark.TFrame')
        notebook.add(basic_frame, text="[BASIC]")
        self._create_basic_tab(basic_frame)
        
        # Tab 3: Attack Modes
        attack_frame = ttk.Frame(notebook, style='Dark.TFrame')
        notebook.add(attack_frame, text="[ATTACK MODES]")
        self._create_attack_tab(attack_frame)
        
        # Tab 4: Advanced Modules
        advanced_frame = ttk.Frame(notebook, style='Dark.TFrame')
        notebook.add(advanced_frame, text="[ADVANCED MODULES]")
        self._create_advanced_tab(advanced_frame)
        
        # Tab 5: Performance
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
    
    def _create_mode_tab(self, parent):
        """Create operation mode selection tab."""
        main_frame = ttk.LabelFrame(parent, text="OPERATION MODE", 
                                    style='Dark.TLabelframe', padding=15)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Mode selection
        mode_frame = ttk.LabelFrame(main_frame, text="SELECT MODE", style='Dark.TLabelframe', padding=10)
        mode_frame.pack(fill=tk.X, pady=10)
        
        self.operation_mode_var = tk.StringVar(value="attack")
        
        # Attack mode
        attack_frame = ttk.Frame(mode_frame, style='Dark.TFrame')
        attack_frame.pack(fill=tk.X, pady=5)
        
        ttk.Radiobutton(attack_frame, text="[ATTACK MODE]", variable=self.operation_mode_var, 
                       value="attack", style='Dark.TRadiobutton').pack(side=tk.LEFT, padx=5)
        tk.Label(attack_frame, text="Find vulnerabilities and exploit them", 
                bg=COLORS['bg_secondary'], fg=COLORS['fg_primary'],
                font=FONTS['monospace']).pack(side=tk.LEFT, padx=10)
        
        # Flag Hunt mode
        flag_frame = ttk.Frame(mode_frame, style='Dark.TFrame')
        flag_frame.pack(fill=tk.X, pady=5)
        
        ttk.Radiobutton(flag_frame, text="[FLAG HUNT MODE]", variable=self.operation_mode_var, 
                       value="flag_hunt", style='Dark.TRadiobutton').pack(side=tk.LEFT, padx=5)
        tk.Label(flag_frame, text="Focus on finding CTF flags (network & web)", 
                bg=COLORS['bg_secondary'], fg=COLORS['accent_yellow'],
                font=FONTS['monospace']).pack(side=tk.LEFT, padx=10)
        
        # Mode descriptions
        desc_frame = ttk.LabelFrame(main_frame, text="MODE DESCRIPTIONS", style='Dark.TLabelframe', padding=10)
        desc_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        attack_desc = """
[ATTACK MODE]
- Aggressive vulnerability discovery
- Payload injection and exploitation
- Business logic testing
- Post-exploitation capabilities
- Full attack surface mapping
        """
        
        flag_desc = """
[FLAG HUNT MODE]
- Network port scanning for flags
- Deep web crawling for hidden flags
- Response header/body analysis
- Source code flag scanning
- Common flag location checking
- Optimized for CTF competitions
        """
        
        tk.Label(desc_frame, text=attack_desc, bg=COLORS['bg_secondary'], fg=COLORS['fg_primary'],
                font=FONTS['monospace_small'], justify=tk.LEFT, anchor='w').pack(anchor=tk.W, pady=5)
        tk.Label(desc_frame, text=flag_desc, bg=COLORS['bg_secondary'], fg=COLORS['accent_yellow'],
                font=FONTS['monospace_small'], justify=tk.LEFT, anchor='w').pack(anchor=tk.W, pady=5)
    
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
    
    def _normalize_target_url(self, target: str) -> str:
        """Normalize target URL - ensure proper scheme and format."""
        target = target.strip()
        
        # If no scheme, assume HTTPS for CTF/live targets
        if not target.startswith(('http://', 'https://')):
            target = f"https://{target}"
        
        # Parse and reconstruct to normalize
        from urllib.parse import urlparse, urlunparse
        parsed = urlparse(target)
        
        # Ensure scheme is http or https
        if not parsed.scheme:
            scheme = 'https'  # Default to HTTPS for security
        else:
            scheme = parsed.scheme
        
        # Ensure netloc (domain) exists
        if not parsed.netloc:
            # If path looks like domain, use it as netloc
            if '/' not in target.replace('://', ''):
                netloc = target.replace('http://', '').replace('https://', '')
                path = '/'
            else:
                return target  # Can't normalize, return as-is
        else:
            netloc = parsed.netloc
            path = parsed.path or '/'
        
        # Normalize port (443 for HTTPS, 80 for HTTP)
        if ':' in netloc:
            host, port = netloc.rsplit(':', 1)
            if scheme == 'https' and port == '443':
                netloc = host  # Remove default port
            elif scheme == 'http' and port == '80':
                netloc = host
        elif scheme == 'https' and ':' not in netloc:
            # HTTPS default port 443 (implicit)
            pass
        elif scheme == 'http' and ':' not in netloc:
            # HTTP default port 80 (implicit)
            pass
        
        # Reconstruct URL
        normalized = urlunparse((scheme, netloc, path, parsed.params, parsed.query, parsed.fragment))
        
        return normalized
    
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
        """Start attack scan or flag hunt."""
        target = self.target_var.get().strip()
        authorized = self.auth_var.get()
        attack_mode = self.attack_mode_var.get()
        operation_mode = self.operation_mode_var.get()
        
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
        
        # Initialize assessment first to get session_id
        normalized_target = self._normalize_target_url(target)
        assessment_result = run_assessment(normalized_target, authorized=authorized, attack_mode=attack_mode)
        
        if assessment_result.get('status') == 'error':
            show_error(f"Failed to initialize attack: {assessment_result.get('message')}", self.app.root)
            return
        
        session_id = assessment_result.get('session_id')
        
        # Open monitor window immediately for live progress
        from gui.monitor_window import MonitorWindow
        monitor = MonitorWindow(self.app.root, self.app, session_id)
        
        # Store monitor reference for callback
        self.monitor_ref = monitor
        
        # Create progress callback that updates monitor in real-time (thread-safe)
        # Dict is already imported at module level, but ensure it's in closure
        def progress_callback(update: Dict):
            """Callback for real-time attack progress - updates monitor window."""
            try:
                # Schedule GUI update on main thread
                def update_gui():
                    try:
                        if hasattr(monitor, 'attack_monitor') and monitor.attack_monitor:
                            monitor.attack_monitor.add_progress(
                                update.get('message', ''),
                                update.get('status', 'info'),
                                update.get('data')
                            )
                            
                            # Also update log viewer
                            if hasattr(monitor, 'log_viewer'):
                                monitor.log_viewer.add_log(update.get('message', ''), update.get('status', 'INFO').upper())
                    except Exception as e:
                        pass  # Silently fail to avoid breaking attack
                
                # Schedule on main thread
                self.app.root.after(0, update_gui)
            except Exception as e:
                self.logger.debug(f"Progress callback error: {e}")
        
        # Show progress dialog
        progress = ProgressDialog(self.app.root, "Launching Attack")
        
        def run_attack():
            """Run attack in async context."""
            # Initialize all variables with safe defaults to prevent NameError
            attack_results = {}
            progress_updates = []
            findings = []
            stats = {}
            
            try:
                import asyncio
                
                self.logger.info(f"[ATTACK] Normalized target: {normalized_target}")
                self.logger.info(f"[ATTACK] Session initialized: {session_id}")
                
                # Execute actual attack or flag hunt (this runs probes)
                async def execute():
                    from engine.runner import execute_attack
                    return await execute_attack(
                        target=normalized_target,
                        authorized=authorized,
                        attack_mode=attack_mode,
                        session_id=session_id,
                        operation_mode=operation_mode,
                        progress_callback=progress_callback
                    )
                
                # Run async attack
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    attack_results = loop.run_until_complete(execute())
                    # Ensure attack_results is a dict
                    if not isinstance(attack_results, dict):
                        self.logger.warning(f"[ATTACK] Attack results is not a dict: {type(attack_results)}")
                        attack_results = {}
                    self.logger.info(f"[ATTACK] Attack completed. Probes executed: {attack_results.get('total_findings', 0)}")
                except Exception as e:
                    self.logger.error(f"[ATTACK] Error during attack execution: {e}", exc_info=True)
                    attack_results = {}
                finally:
                    loop.close()
                
                # Extract all result data from attack_results with safe defaults
                # Ensure these are always defined even if attack_results is empty/None
                if isinstance(attack_results, dict):
                    progress_updates = attack_results.get("progress_updates", [])
                    findings = attack_results.get("findings", [])
                    stats = attack_results.get("stats", {})
                
                # Store session with results including exploitation data
                session_data = {
                    'session_id': session_id,
                    'target': normalized_target,
                    'started_at': assessment_result.get('started_at'),
                    'status': 'completed',
                    'operation_mode': operation_mode,
                    'attack_mode': attack_mode,
                    'crawl_results': attack_results.get('crawl_results', {}),
                    'findings': findings,
                    'total_findings': attack_results.get('total_findings', 0),
                    'flags_found': attack_results.get('flags_found', []) if operation_mode == 'flag_hunt' else [],
                    'total_flags': attack_results.get('total_flags', 0) if operation_mode == 'flag_hunt' else 0,
                    'exploitation_results': attack_results.get('exploitation_results', []),
                    'failed_exploits': attack_results.get('failed_exploits', []),
                    'progress_updates': progress_updates,
                    'advanced_modules': {
                        'flag_hunter': self.flag_hunter_var.get(),
                        'ghost_operator': self.ghost_operator_var.get(),
                        'logic_breaker': self.logic_breaker_var.get(),
                        'red_team_architect': self.redteam_var.get(),
                        'attacker_mindset': self.mindset_var.get()
                    }
                }
                
                self.store.save_session(session_data, session_id)
                return session_id, None
            
            except Exception as e:
                self.logger.error(f"[ATTACK] Attack failed: {e}", exc_info=True)
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
                    # Update existing monitor with completion
                    if hasattr(self, 'monitor_ref') and hasattr(self.monitor_ref, 'attack_monitor'):
                        self.monitor_ref.attack_monitor.add_progress("ATTACK COMPLETED SUCCESSFULLY", "success")
                    
                    show_info(f"Attack completed!\nSession ID: {session_id}", self.app.root)
                    # Refresh dashboard
                    if hasattr(self.app, 'dashboard'):
                        self.app.dashboard.refresh_sessions()
        
        # Run attack in thread
        run_async(run_attack, callback)
