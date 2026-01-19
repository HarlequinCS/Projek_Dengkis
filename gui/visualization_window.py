"""
Visualization window for PROJEK DENGKIS GUI.
Displays interactive security visualizations.
"""
import tkinter as tk
from tkinter import ttk
from pathlib import Path
import webbrowser

from engine.storage.session_store import SessionStore
from engine.visualization.visualizer import SecurityVisualizer
from engine.logging.logger import get_logger
from gui.utils import run_async, show_error, open_file


class VisualizationWindow(tk.Toplevel):
    """Visualization viewer window."""
    
    def __init__(self, parent, app, session_id: str):
        super().__init__(parent)
        self.app = app
        self.session_id = session_id
        self.logger = get_logger(session_id)
        self.store = SessionStore()
        self.visualizer = SecurityVisualizer()
        
        self.title(f"Visualizations - Session {session_id[:8]}")
        self.geometry("1000x700")
        self.transient(parent)
        
        # Center window
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (1000 // 2)
        y = (self.winfo_screenheight() // 2) - (700 // 2)
        self.geometry(f"1000x700+{x}+{y}")
        
        self._create_layout()
        self._load_visualizations()
    
    def _create_layout(self):
        """Create visualization window layout."""
        # Main frame
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(header_frame, text="Security Visualizations", font=('Arial', 12, 'bold')).pack(side=tk.LEFT)
        
        refresh_btn = ttk.Button(header_frame, text="Refresh", command=self._load_visualizations)
        refresh_btn.pack(side=tk.RIGHT)
        
        # Visualization selection
        selection_frame = ttk.LabelFrame(main_frame, text="Visualization Type", padding=10)
        selection_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.viz_type = tk.StringVar(value="attack_graph")
        ttk.Radiobutton(selection_frame, text="Attack Graph", variable=self.viz_type, value="attack_graph").pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(selection_frame, text="Timeline", variable=self.viz_type, value="timeline").pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(selection_frame, text="Risk Heatmap", variable=self.viz_type, value="heatmap").pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(selection_frame, text="Sunburst", variable=self.viz_type, value="sunburst").pack(side=tk.LEFT, padx=10)
        
        ttk.Button(selection_frame, text="Generate", command=self._generate_viz).pack(side=tk.LEFT, padx=10)
        
        # Web view frame (for HTML visualizations)
        view_frame = ttk.LabelFrame(main_frame, text="Visualization", padding=10)
        view_frame.pack(fill=tk.BOTH, expand=True)
        
        # Note label
        note_label = ttk.Label(
            view_frame,
            text="Visualizations will be generated and opened in your default browser.",
            font=('Arial', 9)
        )
        note_label.pack(pady=10)
        
        # File list
        file_frame = ttk.LabelFrame(view_frame, text="Generated Files", padding=10)
        file_frame.pack(fill=tk.BOTH, expand=True)
        
        self.file_listbox = tk.Listbox(file_frame, height=10)
        self.file_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        file_scrollbar = ttk.Scrollbar(file_frame, orient=tk.VERTICAL, command=self.file_listbox.yview)
        file_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.file_listbox.config(yscrollcommand=file_scrollbar.set)
        
        self.file_listbox.bind('<Double-Button-1>', lambda e: self._open_selected_file())
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(button_frame, text="Open Selected", command=self._open_selected_file).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Close", command=self.destroy).pack(side=tk.RIGHT, padx=5)
        
        # Store generated file paths
        self.generated_files = []
    
    def _load_visualizations(self):
        """Load existing visualizations."""
        # Check for existing visualization files
        storage_dir = Path('storage')
        viz_files = list(storage_dir.glob(f"*{self.session_id[:8]}*.html"))
        
        self.file_listbox.delete(0, tk.END)
        self.generated_files = []
        
        for file_path in viz_files:
            self.file_listbox.insert(tk.END, file_path.name)
            self.generated_files.append(str(file_path))
    
    def _generate_viz(self):
        """Generate selected visualization."""
        session_data = self.store.load_session(self.session_id)
        
        if not session_data:
            show_error("Session not found", self)
            return
        
        viz_type = self.viz_type.get()
        findings = session_data.get('findings', [])
        
        def generate():
            try:
                if viz_type == "attack_graph":
                    result = self.visualizer.generate_attack_graph(findings, session_data)
                elif viz_type == "timeline":
                    events = [
                        {'timestamp': session_data.get('started_at'), 'severity': 'info', 'description': 'Assessment started'}
                    ]
                    result = self.visualizer.create_timeline_visualization(events)
                elif viz_type == "heatmap":
                    result = self.visualizer.generate_risk_heatmap(findings, ['severity', 'category'])
                elif viz_type == "sunburst":
                    result = self.visualizer.create_vulnerability_sunburst(findings)
                else:
                    return None, "Unknown visualization type"
                
                # Save HTML file
                output_dir = Path('storage')
                output_dir.mkdir(exist_ok=True)
                output_file = output_dir / f"{viz_type}_{self.session_id[:8]}.html"
                output_file.write_text(result['html'])
                
                return str(output_file), None
            except Exception as e:
                return None, str(e)
        
        def callback(result, error=None):
            if error:
                show_error(f"Failed to generate visualization: {error}", self)
                return
            
            if result:
                file_path, gen_error = result
                if gen_error:
                    show_error(f"Generation failed: {gen_error}", self)
                else:
                    # Open in browser
                    open_file(file_path)
                    # Refresh file list
                    self._load_visualizations()
        
        run_async(generate, callback)
    
    def _open_selected_file(self):
        """Open selected file."""
        selection = self.file_listbox.curselection()
        if selection:
            index = selection[0]
            if index < len(self.generated_files):
                open_file(self.generated_files[index])
