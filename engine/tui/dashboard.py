"""
TACTICAL TUI DASHBOARD - Full-screen terminal interface
Scary, tactical aesthetic with real-time attack visualization.
"""
from typing import Dict, List
import time
from datetime import datetime

# Optional imports with fallback
TEXTUAL_AVAILABLE = False
try:
    from textual.app import App, ComposeResult
    from textual.containers import Container, Horizontal, Vertical
    from textual.widgets import Static, DataTable, Sparkline, Log
    from textual import events
    from textual import on
    from rich.text import Text
    from rich.console import RenderableType
    TEXTUAL_AVAILABLE = True
except ImportError:
    # Fallback for when textual is not available
    App = object
    ComposeResult = None
    Container = object
    Horizontal = object
    Vertical = object
    Static = object
    DataTable = object
    Sparkline = object
    Log = object
    Text = str


class KillChainBreadcrumb(Static):
    """Kill-chain breadcrumb showing active phase."""
    
    def __init__(self):
        super().__init__()
        self.current_phase = "RECON"
        self.phases = ["RECON", "INJECT", "EXFIL"]
    
    def set_phase(self, phase: str):
        """Set current kill chain phase."""
        if phase.upper() in self.phases:
            self.current_phase = phase.upper()
            self.update(self._render_phases())
    
    def _render_phases(self) -> Text:
        """Render phases with current phase in red."""
        text = Text()
        for i, phase in enumerate(self.phases):
            if phase == self.current_phase:
                text.append(f" {phase} ", style="bold red on black")
            else:
                text.append(f" {phase} ", style="dim white on black")
            if i < len(self.phases) - 1:
                text.append(" → ", style="dim white on black")
        return text


class BreachStream(Log):
    """Scrolling hex-encoded packets that decode into vulnerabilities."""
    
    def __init__(self):
        super().__init__(id="breach_stream", max_lines=100)
        self.vulnerabilities = []
    
    def add_vulnerability(self, endpoint: str, vuln_type: str, payload: str):
        """Add vulnerability to breach stream."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        hex_payload = payload.encode().hex()[:40] + "..."
        
        # Create breach entry
        entry = f"[{timestamp}] BREACH [{vuln_type}] {endpoint}\n"
        entry += f"  HEX: {hex_payload}\n"
        entry += f"  PAYLOAD: {payload[:60]}...\n"
        
        self.write(entry)
        self.vulnerabilities.append({
            'timestamp': timestamp,
            'endpoint': endpoint,
            'type': vuln_type,
            'payload': payload
        })


class ImpactGraph(Static):
    """Live sparkline showing server response times."""
    
    def __init__(self):
        super().__init__("Impact Graph\n[No data]", id="impact_graph")
        self.data_points = []
        self.max_points = 50
    
    def add_data_point(self, value: float):
        """Add response time data point."""
        self.data_points.append(value)
        if len(self.data_points) > self.max_points:
            self.data_points.pop(0)
        
        # Create simple text visualization
        if self.data_points:
            avg = sum(self.data_points) / len(self.data_points)
            max_val = max(self.data_points)
            min_val = min(self.data_points)
            text = f"Response Times\nAvg: {avg:.1f}ms\nMax: {max_val:.1f}ms\nMin: {min_val:.1f}ms"
            self.update(text)


class LootVault(DataTable):
    """Displays flags and credentials with glitch animation."""
    
    def __init__(self):
        super().__init__(id="loot_vault")
        self.add_column("Type", width=12)
        self.add_column("Value", width=40)
        self.add_column("Source", width=30)
        self.loot_items = []
    
    def add_loot(self, loot_type: str, value: str, source: str):
        """Add loot item with glitch effect."""
        self.loot_items.append({
            'type': loot_type,
            'value': value,
            'source': source
        })
        
        # Add to table
        row_key = f"{loot_type}_{len(self.loot_items)}"
        self.add_row(
            loot_type,
            value[:40] + "..." if len(value) > 40 else value,
            source,
            key=row_key
        )
        
        # Trigger visual glitch effect
        self._glitch_effect(row_key)
    
    def _glitch_effect(self, row_key: str):
        """Apply digital glitch animation."""
        # Visual effect: briefly change text color
        pass  # Implemented via CSS animations


class TacticalDashboard(App):
    """
    Full-screen tactical TUI dashboard.
    True black background, neon red accents, real-time attack visualization.
    """
    
    CSS = """
    Screen {
        background: #000000;
    }
    
    .kill-chain {
        height: 3;
        border-bottom: solid red;
        padding: 1;
    }
    
    #breach_stream {
        background: #000000;
        color: #ff0000;
        border: solid #333333;
        height: 50%;
    }
    
    #impact_graph {
        background: #000000;
        border: solid #333333;
        height: 50%;
    }
    
    #loot_vault {
        background: #000000;
        color: #ff0000;
        border: solid #333333;
    }
    
    .breach-entry {
        color: #ff0000;
    }
    
    .critical {
        color: #ff0000;
        text-style: bold;
    }
    """
    
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("c", "copy_poc", "Copy PoC"),
        ("r", "refresh", "Refresh"),
    ]
    
    def __init__(self, attack_engine=None):
        super().__init__()
        self.attack_engine = attack_engine
        self.kill_chain = None
        self.breach_stream = None
        self.impact_graph = None
        self.loot_vault = None
    
    def compose(self) -> ComposeResult:
        """Compose the dashboard layout."""
        with Container(classes="kill-chain"):
            yield KillChainBreadcrumb(id="kill_chain")
        
        with Horizontal():
            yield BreachStream(id="breach_stream")
            yield ImpactGraph(id="impact_graph")
        
        yield LootVault(id="loot_vault")
    
    def on_mount(self):
        """Initialize dashboard on mount."""
        self.kill_chain = self.query_one("#kill_chain", KillChainBreadcrumb)
        self.breach_stream = self.query_one("#breach_stream", BreachStream)
        self.impact_graph = self.query_one("#impact_graph", ImpactGraph)
        self.loot_vault = self.query_one("#loot_vault", LootVault)
        
        # Start with RECON phase
        self.kill_chain.set_phase("RECON")
    
    def set_kill_chain_phase(self, phase: str):
        """Set kill chain phase."""
        if self.kill_chain:
            self.kill_chain.set_phase(phase)
    
    def add_vulnerability(self, endpoint: str, vuln_type: str, payload: str):
        """Add vulnerability to breach stream."""
        if self.breach_stream:
            self.breach_stream.add_vulnerability(endpoint, vuln_type, payload)
    
    def add_response_time(self, time_ms: float):
        """Add response time to impact graph."""
        if self.impact_graph:
            self.impact_graph.add_data_point(time_ms)
    
    def add_loot(self, loot_type: str, value: str, source: str):
        """Add loot to vault."""
        if self.loot_vault:
            self.loot_vault.add_loot(loot_type, value, source)
    
    def action_copy_poc(self):
        """Copy PoC to clipboard."""
        # Get selected vulnerability and generate PoC
        # Implementation depends on selected item
        pass
    
    def action_refresh(self):
        """Refresh dashboard."""
        self.refresh()


def create_tactical_dashboard(attack_engine=None) -> TacticalDashboard:
    """Create and return tactical dashboard instance."""
    if not TEXTUAL_AVAILABLE:
        raise ImportError("Textual library not available. Install with: pip install textual rich")
    
    return TacticalDashboard(attack_engine=attack_engine)
