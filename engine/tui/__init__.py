"""Tactical TUI dashboard modules."""
try:
    from engine.tui.dashboard import create_tactical_dashboard, TacticalDashboard
    __all__ = ["create_tactical_dashboard", "TacticalDashboard"]
except ImportError:
    __all__ = []
