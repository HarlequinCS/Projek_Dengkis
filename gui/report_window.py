"""
Report viewer and export window for PROJEK DENGKIS GUI.
Allows viewing and exporting assessment reports.
"""
import tkinter as tk
from tkinter import ttk
from pathlib import Path
import webbrowser

from engine.storage.session_store import SessionStore
from engine.reporting.generator import ReportGenerator
from engine.logging.logger import get_logger
from gui.utils import run_async, show_error, show_info, choose_file, open_file


class ReportWindow(tk.Toplevel):
    """Report viewer and export window."""
    
    def __init__(self, parent, app, session_id: str):
        super().__init__(parent)
        self.app = app
        self.session_id = session_id
        self.logger = get_logger(session_id)
        self.store = SessionStore()
        self.generator = ReportGenerator()
        
        self.title(f"Reports - Session {session_id[:8]}")
        self.geometry("800x600")
        self.transient(parent)
        
        # Center window
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (800 // 2)
        y = (self.winfo_screenheight() // 2) - (600 // 2)
        self.geometry(f"800x600+{x}+{y}")
        
        self._create_layout()
        self._load_report()
    
    def _create_layout(self):
        """Create report window layout."""
        # Main frame
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(header_frame, text="Assessment Reports", font=('Arial', 12, 'bold')).pack(side=tk.LEFT)
        
        refresh_btn = ttk.Button(header_frame, text="Refresh", command=self._load_report)
        refresh_btn.pack(side=tk.RIGHT)
        
        # Report type selection
        type_frame = ttk.LabelFrame(main_frame, text="Report Type", padding=10)
        type_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.report_type = tk.StringVar(value="executive")
        ttk.Radiobutton(type_frame, text="Executive", variable=self.report_type, value="executive").pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(type_frame, text="Technical", variable=self.report_type, value="technical").pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(type_frame, text="Dashboard", variable=self.report_type, value="dashboard").pack(side=tk.LEFT, padx=10)
        
        # Export format selection
        format_frame = ttk.LabelFrame(main_frame, text="Export Format", padding=10)
        format_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.export_format = tk.StringVar(value="html")
        ttk.Radiobutton(format_frame, text="HTML", variable=self.export_format, value="html").pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(format_frame, text="JSON", variable=self.export_format, value="json").pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(format_frame, text="Markdown", variable=self.export_format, value="markdown").pack(side=tk.LEFT, padx=10)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(button_frame, text="Generate Report", command=self._generate_report).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Export as PDF", command=self._export_pdf).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Export As...", command=self._export_as).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Open in Browser", command=self._open_in_browser).pack(side=tk.LEFT, padx=5)
        
        # Report preview area
        preview_frame = ttk.LabelFrame(main_frame, text="Report Preview", padding=10)
        preview_frame.pack(fill=tk.BOTH, expand=True)
        
        # Note label
        note_label = ttk.Label(
            preview_frame,
            text="Generate a report to preview it here. HTML reports can be opened in your browser.",
            font=('Arial', 9)
        )
        note_label.pack(pady=10)
        
        # Report file path
        self.report_path_var = tk.StringVar()
        path_frame = ttk.Frame(preview_frame)
        path_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(path_frame, text="Report File:").pack(side=tk.LEFT, padx=5)
        path_entry = ttk.Entry(path_frame, textvariable=self.report_path_var, state='readonly')
        path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Buttons
        close_btn = ttk.Button(main_frame, text="Close", command=self.destroy)
        close_btn.pack(pady=(10, 0))
        
        self.current_report_path = None
    
    def _load_report(self):
        """Load session and prepare for report generation."""
        session_data = self.store.load_session(self.session_id)
        if not session_data:
            show_error("Session not found", self)
            self.destroy()
    
    def _generate_report(self):
        """Generate report."""
        session_data = self.store.load_session(self.session_id)
        if not session_data:
            show_error("Session not found", self)
            return
        
        report_type = self.report_type.get()
        export_format = self.export_format.get()
        
        def generate():
            try:
                if report_type == "executive":
                    report_path = self.generator.generate_executive_report(session_data, format=export_format)
                elif report_type == "technical":
                    report_path = self.generator.generate_technical_report(session_data, format=export_format)
                else:
                    report_path = self.generator.create_interactive_dashboard(session_data)
                
                return report_path, None
            except Exception as e:
                return None, str(e)
        
        def callback(result, error=None):
            if error:
                show_error(f"Failed to generate report: {error}", self)
                return
            
            if result:
                report_path, gen_error = result
                if gen_error:
                    show_error(f"Generation failed: {gen_error}", self)
                else:
                    self.current_report_path = report_path
                    self.report_path_var.set(report_path)
                    show_info(f"Report generated: {report_path}", self)
                    
                    # Auto-open HTML reports
                    if export_format == 'html':
                        self._open_in_browser()
        
        run_async(generate, callback)
    
    def _export_pdf(self):
        """Export report as PDF (optional feature)."""
        if not self.current_report_path:
            show_error("Please generate a report first", self)
            return
        
        try:
            # Try to import weasyprint
            try:
                from weasyprint import HTML
                html_path = Path(self.current_report_path)
                if html_path.suffix != '.html':
                    show_error("PDF export requires HTML report format", self)
                    return
                
                pdf_path = html_path.with_suffix('.pdf')
                HTML(filename=str(html_path)).write_pdf(str(pdf_path))
                show_info(f"PDF exported: {pdf_path}", self)
            except ImportError:
                show_error(
                    "PDF export requires 'weasyprint' library.\n"
                    "Install it with: pip install weasyprint",
                    self
                )
        except Exception as e:
            show_error(f"PDF export failed: {e}", self)
    
    def _export_as(self):
        """Export report to custom location."""
        if not self.current_report_path:
            show_error("Please generate a report first", self)
            return
        
        from shutil import copy2
        source_path = Path(self.current_report_path)
        
        dest_path = choose_file(
            save=True,
            filetypes=[("All files", "*.*")]
        )
        
        if dest_path:
            try:
                copy2(source_path, dest_path)
                show_info(f"Report exported to: {dest_path}", self)
            except Exception as e:
                show_error(f"Export failed: {e}", self)
    
    def _open_in_browser(self):
        """Open report in browser."""
        if not self.current_report_path:
            show_error("Please generate a report first", self)
            return
        
        report_path = Path(self.current_report_path)
        if report_path.suffix == '.html' and report_path.exists():
            open_file(str(report_path))
        else:
            show_error("HTML report not found. Please generate an HTML report first.", self)
