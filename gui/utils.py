"""
GUI utilities for PROJEK DENGKIS.
Helper functions for GUI components.
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Optional, Callable, Any
import threading
import webbrowser
from pathlib import Path


def show_error(message: str, parent: Optional[tk.Tk] = None):
    """Show error message dialog."""
    messagebox.showerror("Error", message, parent=parent)


def show_warning(message: str, parent: Optional[tk.Tk] = None):
    """Show warning message dialog."""
    messagebox.showwarning("Warning", message, parent=parent)


def show_info(message: str, parent: Optional[tk.Tk] = None):
    """Show info message dialog."""
    messagebox.showinfo("Information", message, parent=parent)


def ask_confirmation(message: str, parent: Optional[tk.Tk] = None) -> bool:
    """Ask for user confirmation."""
    return messagebox.askyesno("Confirmation", message, parent=parent)


def run_async(task: Callable, callback: Optional[Callable] = None):
    """
    Run async task in thread to avoid freezing GUI.
    
    Args:
        task: Function to run in thread
        callback: Optional callback function to call after task completes
    """
    def wrapper():
        try:
            result = task()
            if callback:
                callback(result)
        except Exception as e:
            if callback:
                callback(None, error=str(e))
    
    thread = threading.Thread(target=wrapper, daemon=True)
    thread.start()


def open_file(path: str):
    """Open file in default application."""
    path_obj = Path(path)
    if path_obj.exists():
        if path_obj.suffix == '.html':
            webbrowser.open(f"file://{path_obj.absolute()}")
        else:
            webbrowser.open(str(path_obj.absolute()))


def choose_file(save: bool = False, filetypes: Optional[list] = None) -> Optional[str]:
    """
    Show file dialog.
    
    Args:
        save: If True, show save dialog; otherwise open dialog
        filetypes: List of file type tuples [(description, pattern), ...]
        
    Returns:
        Selected file path or None
    """
    if save:
        return filedialog.asksaveasfilename(filetypes=filetypes)
    else:
        return filedialog.askopenfilename(filetypes=filetypes)


class ProgressDialog:
    """Simple progress dialog."""
    
    def __init__(self, parent: tk.Tk, title: str = "Processing"):
        self.parent = parent
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("400x120")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center window
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (400 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (120 // 2)
        self.dialog.geometry(f"400x120+{x}+{y}")
        
        self.label = ttk.Label(self.dialog, text="Please wait...")
        self.label.pack(pady=10)
        
        self.progress = ttk.Progressbar(self.dialog, mode='indeterminate')
        self.progress.pack(pady=10, padx=20, fill='x')
        self.progress.start()
        
        self.dialog.protocol("WM_DELETE_WINDOW", lambda: None)  # Disable close
    
    def update_text(self, text: str):
        """Update progress text."""
        self.label.config(text=text)
        self.dialog.update()
    
    def close(self):
        """Close progress dialog."""
        self.progress.stop()
        self.dialog.destroy()
