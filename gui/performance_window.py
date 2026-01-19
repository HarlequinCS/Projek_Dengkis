"""
Performance Optimization Window - Configure performance settings.
"""
import tkinter as tk
from tkinter import ttk

from gui.theme import COLORS, FONTS
from gui.utils import show_info, show_error


class PerformanceWindow(tk.Toplevel):
    """Window for performance optimization."""
    
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        
        self.configure(bg=COLORS['bg_primary'])
        self.title("DENGKIS // PERFORMANCE OPTIMIZER")
        self.geometry("600x500")
        self.transient(parent)
        
        self._create_layout()
    
    def _create_layout(self):
        """Create performance window layout."""
        header = tk.Label(self, text="[PERFORMANCE OPTIMIZATION]", 
                         bg=COLORS['bg_primary'], fg=COLORS['accent_red'],
                         font=FONTS['monospace_large'])
        header.pack(pady=10)
        
        main_frame = ttk.Frame(self, style='Dark.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Kernel optimization
        kernel_frame = ttk.LabelFrame(main_frame, text="KERNEL TUNING", 
                                      style='Dark.TLabelframe', padding=10)
        kernel_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(kernel_frame, text="Apply kernel-level optimizations:", 
                bg=COLORS['bg_secondary'], fg=COLORS['fg_primary'],
                font=FONTS['monospace']).pack(anchor=tk.W)
        tk.Label(kernel_frame, text="- ulimit -n 65535 (file descriptors)", 
                bg=COLORS['bg_secondary'], fg=COLORS['fg_secondary'],
                font=FONTS['monospace_small']).pack(anchor=tk.W, padx=20)
        tk.Label(kernel_frame, text="- TCP stack tuning (sysctl)", 
                bg=COLORS['bg_secondary'], fg=COLORS['fg_secondary'],
                font=FONTS['monospace_small']).pack(anchor=tk.W, padx=20)
        
        ttk.Button(kernel_frame, text="[APPLY KERNEL OPTIMIZATIONS]", 
                  command=self._apply_kernel, style='Primary.TButton').pack(pady=10)
        
        # Zero-copy
        zerocopy_frame = ttk.LabelFrame(main_frame, text="ZERO-COPY PROCESSING", 
                                        style='Dark.TLabelframe', padding=10)
        zerocopy_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(zerocopy_frame, text="Enabled by default:", 
                bg=COLORS['bg_secondary'], fg=COLORS['fg_primary'],
                font=FONTS['monospace']).pack(anchor=tk.W)
        tk.Label(zerocopy_frame, text="- mmap for wordlist handling", 
                bg=COLORS['bg_secondary'], fg=COLORS['fg_secondary'],
                font=FONTS['monospace_small']).pack(anchor=tk.W, padx=20)
        tk.Label(zerocopy_frame, text="- ujson for fast JSON parsing", 
                bg=COLORS['bg_secondary'], fg=COLORS['fg_secondary'],
                font=FONTS['monospace_small']).pack(anchor=tk.W, padx=20)
        
        # GPU acceleration
        gpu_frame = ttk.LabelFrame(main_frame, text="GPU ACCELERATION", 
                                   style='Dark.TLabelframe', padding=10)
        gpu_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(gpu_frame, text="Optional GPU acceleration:", 
                bg=COLORS['bg_secondary'], fg=COLORS['fg_primary'],
                font=FONTS['monospace']).pack(anchor=tk.W)
        tk.Label(gpu_frame, text="- PyOpenCL / CuPy for heavy computations", 
                bg=COLORS['bg_secondary'], fg=COLORS['fg_secondary'],
                font=FONTS['monospace_small']).pack(anchor=tk.W, padx=20)
        
        ttk.Button(main_frame, text="[CLOSE]", command=self.destroy,
                  style='Dark.TButton').pack(pady=20)
    
    def _apply_kernel(self):
        """Apply kernel optimizations."""
        try:
            from engine.performance.optimizer import PerformanceOptimizer
            optimizer = PerformanceOptimizer()
            result = optimizer.optimize_environment()
            show_info("Kernel optimizations applied successfully", self)
        except Exception as e:
            show_error(f"Failed to apply optimizations: {e}", self)
