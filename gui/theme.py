"""
Dark terminal theme for PROJEK DENGKIS GUI.
Tactical, cyber warfare aesthetic.
"""
import tkinter as tk
from tkinter import ttk

# Color palette - Terminal meets cyber warfare
COLORS = {
    'bg_primary': '#0b0f14',      # Near-black background
    'bg_secondary': '#1a1f2e',    # Dark gray panels
    'bg_tertiary': '#252b3d',     # Lighter dark gray
    'fg_primary': '#e0e0e0',      # Off-white text
    'fg_secondary': '#b0b0b0',    # Muted gray text
    'accent_red': '#ff0000',      # Blood red (critical)
    'accent_orange': '#ffaa00',   # Amber/orange (high)
    'accent_yellow': '#ffff00',   # Toxic yellow (medium)
    'accent_green': '#00ff00',    # Muted green (low)
    'accent_blue': '#0088ff',     # Steel blue (info)
    'border': '#333333',          # Dark border
    'border_bright': '#555555',   # Brighter border
    'selection': '#2a3f5f',       # Selection highlight
}

# Font configuration
FONTS = {
    'monospace': ('Courier New', 10),
    'monospace_bold': ('Courier New', 10, 'bold'),
    'monospace_large': ('Courier New', 12, 'bold'),
    'monospace_small': ('Courier New', 8),
}


def apply_dark_theme(root: tk.Tk):
    """Apply dark terminal theme to root window."""
    style = ttk.Style()
    
    # Configure root window
    root.configure(bg=COLORS['bg_primary'])
    
    # Configure ttk styles
    style.theme_use('clam')
    
    # Frame styles
    style.configure('Dark.TFrame', background=COLORS['bg_primary'], borderwidth=0)
    style.configure('Panel.TFrame', background=COLORS['bg_secondary'], borderwidth=1, relief='flat')
    style.configure('Border.TFrame', background=COLORS['bg_secondary'], borderwidth=1, relief='solid', bordercolor=COLORS['border'])
    
    # LabelFrame styles
    style.configure('Dark.TLabelframe', background=COLORS['bg_secondary'], foreground=COLORS['accent_red'], 
                    borderwidth=2, relief='solid', bordercolor=COLORS['accent_red'])
    style.configure('Dark.TLabelframe.Label', background=COLORS['bg_secondary'], foreground=COLORS['accent_red'],
                    font=FONTS['monospace_bold'])
    
    # Label styles
    style.configure('Dark.TLabel', background=COLORS['bg_secondary'], foreground=COLORS['fg_primary'],
                    font=FONTS['monospace'])
    style.configure('Title.TLabel', background=COLORS['bg_primary'], foreground=COLORS['accent_red'],
                    font=FONTS['monospace_large'])
    style.configure('Header.TLabel', background=COLORS['bg_primary'], foreground=COLORS['accent_red'],
                    font=FONTS['monospace_bold'])
    style.configure('Info.TLabel', background=COLORS['bg_secondary'], foreground=COLORS['accent_blue'],
                    font=FONTS['monospace'])
    style.configure('Warning.TLabel', background=COLORS['bg_secondary'], foreground=COLORS['accent_yellow'],
                    font=FONTS['monospace'])
    style.configure('Error.TLabel', background=COLORS['bg_secondary'], foreground=COLORS['accent_red'],
                    font=FONTS['monospace'])
    style.configure('Success.TLabel', background=COLORS['bg_secondary'], foreground=COLORS['accent_green'],
                    font=FONTS['monospace'])
    
    # Button styles
    style.configure('Dark.TButton', background=COLORS['bg_tertiary'], foreground=COLORS['fg_primary'],
                    borderwidth=1, relief='solid', bordercolor=COLORS['border'],
                    font=FONTS['monospace'], padding=5)
    style.map('Dark.TButton',
              background=[('active', COLORS['selection']), ('pressed', COLORS['bg_tertiary'])],
              bordercolor=[('active', COLORS['accent_red']), ('pressed', COLORS['border'])])
    
    style.configure('Danger.TButton', background=COLORS['bg_tertiary'], foreground=COLORS['accent_red'],
                    borderwidth=2, relief='solid', bordercolor=COLORS['accent_red'],
                    font=FONTS['monospace_bold'], padding=5)
    style.map('Danger.TButton',
              background=[('active', COLORS['accent_red']), ('pressed', COLORS['bg_tertiary'])],
              foreground=[('active', COLORS['bg_primary']), ('pressed', COLORS['accent_red'])],
              bordercolor=[('active', COLORS['accent_red']), ('pressed', COLORS['accent_red'])])
    
    style.configure('Primary.TButton', background=COLORS['bg_tertiary'], foreground=COLORS['accent_blue'],
                    borderwidth=2, relief='solid', bordercolor=COLORS['accent_blue'],
                    font=FONTS['monospace_bold'], padding=5)
    style.map('Primary.TButton',
              background=[('active', COLORS['accent_blue']), ('pressed', COLORS['bg_tertiary'])],
              foreground=[('active', COLORS['bg_primary']), ('pressed', COLORS['accent_blue'])],
              bordercolor=[('active', COLORS['accent_blue']), ('pressed', COLORS['accent_blue'])])
    
    # Entry styles
    style.configure('Dark.TEntry', fieldbackground=COLORS['bg_tertiary'], foreground=COLORS['fg_primary'],
                   borderwidth=1, relief='solid', bordercolor=COLORS['border'],
                   font=FONTS['monospace'], padding=3)
    style.map('Dark.TEntry',
              bordercolor=[('focus', COLORS['accent_red']), ('!focus', COLORS['border'])],
              fieldbackground=[('focus', COLORS['bg_tertiary']), ('!focus', COLORS['bg_tertiary'])])
    
    # Checkbutton styles
    style.configure('Dark.TCheckbutton', background=COLORS['bg_secondary'], foreground=COLORS['fg_primary'],
                    font=FONTS['monospace'], focuscolor=COLORS['bg_secondary'])
    style.map('Dark.TCheckbutton',
              background=[('active', COLORS['bg_secondary']), ('selected', COLORS['bg_secondary'])],
              foreground=[('active', COLORS['accent_red']), ('selected', COLORS['accent_red'])])
    
    # Radiobutton styles
    style.configure('Dark.TRadiobutton', background=COLORS['bg_secondary'], foreground=COLORS['fg_primary'],
                   font=FONTS['monospace'], focuscolor=COLORS['bg_secondary'])
    style.map('Dark.TRadiobutton',
              background=[('active', COLORS['bg_secondary']), ('selected', COLORS['bg_secondary'])],
              foreground=[('active', COLORS['accent_red']), ('selected', COLORS['accent_red'])])
    
    # Combobox styles
    style.configure('Dark.TCombobox', fieldbackground=COLORS['bg_tertiary'], foreground=COLORS['fg_primary'],
                   borderwidth=1, relief='solid', bordercolor=COLORS['border'],
                   font=FONTS['monospace'])
    style.map('Dark.TCombobox',
              bordercolor=[('focus', COLORS['accent_red']), ('!focus', COLORS['border'])],
              fieldbackground=[('focus', COLORS['bg_tertiary']), ('!focus', COLORS['bg_tertiary'])])
    
    # Notebook (tab) styles
    style.configure('Dark.TNotebook', background=COLORS['bg_primary'], borderwidth=0)
    style.configure('Dark.TNotebook.Tab', background=COLORS['bg_tertiary'], foreground=COLORS['fg_secondary'],
                    borderwidth=1, relief='flat', padding=[10, 5], font=FONTS['monospace'])
    style.map('Dark.TNotebook.Tab',
              background=[('selected', COLORS['bg_secondary']), ('active', COLORS['selection'])],
              foreground=[('selected', COLORS['accent_red']), ('active', COLORS['fg_primary'])],
              expand=[('selected', [1, 1, 1, 0])])
    
    # Treeview (list) styles
    style.configure('Dark.Treeview', background=COLORS['bg_tertiary'], foreground=COLORS['fg_primary'],
                   fieldbackground=COLORS['bg_tertiary'], borderwidth=1, relief='solid',
                   bordercolor=COLORS['border'], font=FONTS['monospace_small'])
    style.configure('Dark.Treeview.Heading', background=COLORS['bg_secondary'], foreground=COLORS['accent_red'],
                   font=FONTS['monospace_bold'], borderwidth=1, relief='solid', bordercolor=COLORS['border'])
    style.map('Dark.Treeview',
              background=[('selected', COLORS['selection'])],
              foreground=[('selected', COLORS['accent_red'])])
    
    # Scrollbar styles
    style.configure('Dark.Vertical.TScrollbar', background=COLORS['bg_tertiary'], 
                   troughcolor=COLORS['bg_secondary'], borderwidth=0, arrowcolor=COLORS['accent_red'],
                   darkcolor=COLORS['bg_tertiary'], lightcolor=COLORS['bg_tertiary'])
    style.map('Dark.Vertical.TScrollbar',
              background=[('active', COLORS['selection'])],
              arrowcolor=[('active', COLORS['accent_red'])])
    
    style.configure('Dark.Horizontal.TScrollbar', background=COLORS['bg_tertiary'],
                   troughcolor=COLORS['bg_secondary'], borderwidth=0, arrowcolor=COLORS['accent_red'],
                   darkcolor=COLORS['bg_tertiary'], lightcolor=COLORS['bg_tertiary'])
    style.map('Dark.Horizontal.TScrollbar',
              background=[('active', COLORS['selection'])],
              arrowcolor=[('active', COLORS['accent_red'])])
    
    # Progressbar styles
    style.configure('Dark.Horizontal.TProgressbar', background=COLORS['accent_red'],
                   troughcolor=COLORS['bg_secondary'], borderwidth=0, lightcolor=COLORS['accent_red'],
                   darkcolor=COLORS['accent_red'])


def create_severity_label(parent, severity: str, text: str = None) -> ttk.Label:
    """Create a label with severity-based styling."""
    if text is None:
        text = severity.upper()
    
    color_map = {
        'critical': COLORS['accent_red'],
        'high': COLORS['accent_orange'],
        'medium': COLORS['accent_yellow'],
        'low': COLORS['accent_green'],
        'info': COLORS['accent_blue']
    }
    
    color = color_map.get(severity.lower(), COLORS['fg_primary'])
    
    label = tk.Label(parent, text=text, bg=COLORS['bg_secondary'], fg=color,
                    font=FONTS['monospace_bold'], padx=5, pady=2, relief='solid', borderwidth=1)
    return label
