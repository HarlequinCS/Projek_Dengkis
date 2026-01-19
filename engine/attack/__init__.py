"""
ATTACK ENGINE - Aggressive, attack-driven exploitation engine.
This is NOT a passive scanner. This is an ACTIVE exploitation tool.
"""
from engine.attack.crawler import AggressiveCrawler
from engine.attack.injector import PayloadInjector
from engine.attack.payloads import PayloadLibrary
from engine.attack.app_detector import KnownAppDetector
from engine.attack.flag_hunter import FlagHunter
from engine.attack.ghost_operator import GhostOperator
from engine.attack.logic_breaker import LogicBreaker
from engine.attack.red_team_architect import RedTeamArchitect
from engine.attack.attacker_mindset import AttackerMindset

__all__ = [
    "AggressiveCrawler",
    "PayloadInjector",
    "PayloadLibrary",
    "KnownAppDetector",
    "FlagHunter",
    "GhostOperator",
    "LogicBreaker",
    "RedTeamArchitect",
    "AttackerMindset",
]

# Performance and TUI modules
try:
    from engine.performance.optimizer import PerformanceOptimizer, LeakyBucketRateLimiter
    from engine.performance.zero_copy import ZeroCopyProcessor
    from engine.tui.dashboard import create_tactical_dashboard
    from engine.kali.integration import KaliIntegration
    from engine.poc.generator import PoCGenerator
except ImportError:
    pass
