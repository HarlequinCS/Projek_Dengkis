"""
TUI Runner - Launch tactical dashboard with attack engine
"""
import asyncio
import sys
from pathlib import Path

# Add engine to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from engine.attack.engine import AttackEngine
from engine.performance.optimizer import PerformanceOptimizer
from engine.kali.integration import KaliIntegration
from engine.tui.dashboard import create_tactical_dashboard
from engine.logging.logger import get_logger
import httpx


async def run_tui_attack(target: str, attack_mode: str = "aggressive", authorized: bool = False):
    """
    Run attack with tactical TUI dashboard.
    
    Args:
        target: Target URL
        attack_mode: passive, active, or aggressive
        authorized: Authorization flag
    """
    logger = get_logger()
    
    if not authorized:
        logger.error("[TUI] Attack requires explicit authorization")
        print("ERROR: Use --authorized flag")
        return
    
    # Optimize environment
    logger.info("[TUI] Optimizing environment...")
    optimizer = PerformanceOptimizer()
    optimizer.optimize_environment()
    
    # Initialize Kali integration
    kali = KaliIntegration()
    
    # Create dashboard
    try:
        dashboard = create_tactical_dashboard()
    except ImportError:
        logger.error("[TUI] Textual library not available. Install with: pip install textual rich")
        print("ERROR: TUI requires textual library")
        return
    
    # Update kill chain to RECON
    dashboard.set_kill_chain_phase("RECON")
    
    # Run attack in background
    async def run_attack():
        async with httpx.AsyncClient(verify=False, timeout=30.0) as client:
            engine = AttackEngine(target, attack_mode=attack_mode, session=client)
            
            # Update kill chain to INJECT
            dashboard.set_kill_chain_phase("INJECT")
            
            # Run attack
            results = await engine.attack()
            
            # Update kill chain to EXFIL
            dashboard.set_kill_chain_phase("EXFIL")
            
            # Add findings to dashboard
            for finding in results.get('findings', []):
                dashboard.add_vulnerability(
                    finding.get('endpoint', ''),
                    finding.get('category', ''),
                    finding.get('payload', '')
                )
            
            # Add flags to loot vault
            for flag in results.get('flags_found', []):
                dashboard.add_loot("Flag", flag, results.get('target', ''))
            
            # Add credentials to loot vault
            for cred in results.get('credentials_found', []):
                dashboard.add_loot("Credential", cred.get('content', '')[:40], cred.get('endpoint', ''))
            
            # Save session
            kali.save_session(
                results.get('session_id', 'unknown'),
                results.get('target', ''),
                results.get('attack_mode', ''),
                results.get('findings', []),
                results
            )
            
            # Notify critical findings
            for finding in results.get('findings', []):
                if finding.get('confidence') == 'high':
                    kali.notify_critical_finding(finding)
            
            return results
    
    # Run dashboard with attack in background
    attack_task = None
    dashboard_thread = None
    try:
        # Start attack task in background
        attack_task = asyncio.create_task(run_attack())
        
        # Run the blocking Textual dashboard in a separate thread so the
        # async event loop can continue executing attack tasks.
        import threading
        def _run_dashboard():
            try:
                dashboard.run()
            except Exception as de:
                logger.error(f"[TUI] Dashboard thread error: {de}")
        dashboard_thread = threading.Thread(target=_run_dashboard, daemon=True)
        dashboard_thread.start()

        # Await attack completion
        results = await attack_task

        # After attack completes, try to close the dashboard gracefully
        try:
            if hasattr(dashboard, 'exit'):
                dashboard.exit()
        except Exception:
            pass

        # Give dashboard thread a moment to finish
        if dashboard_thread and dashboard_thread.is_alive():
            dashboard_thread.join(timeout=2)

    except KeyboardInterrupt:
        logger.info("[TUI] Dashboard interrupted")
        if attack_task and not attack_task.done():
            attack_task.cancel()
        try:
            if hasattr(dashboard, 'exit'):
                dashboard.exit()
        except Exception:
            pass
    except Exception as e:
        logger.error(f"[TUI] Dashboard error: {e}")
        if attack_task and not attack_task.done():
            attack_task.cancel()


if __name__ == "__main__":
    import argparse
    import threading
    
    parser = argparse.ArgumentParser(description="Dengkis Tactical TUI")
    parser.add_argument('target', help='Target URL')
    parser.add_argument('--authorized', action='store_true', help='Authorization flag (required)')
    parser.add_argument('--mode', choices=['passive', 'active', 'aggressive'], default='aggressive', help='Attack mode')
    
    args = parser.parse_args()
    
    # Run the async TUI runner in a dedicated thread to avoid calling
    # asyncio.run() from an already-running event loop (common in some
    # interactive or embedded environments). Running in a thread creates
    # an isolated event loop and prevents "asyncio.run() cannot be called
    # from a running event loop" errors.
    def _run_coro_in_thread(coro, *coro_args):
        def _target():
            try:
                asyncio.run(coro(*coro_args))
            except Exception as e:
                # Log errors from the thread
                get_logger().error(f"[TUI] Runner thread error: {e}")
        t = threading.Thread(target=_target, daemon=False)
        t.start()
        t.join()

    _run_coro_in_thread(run_tui_attack, args.target, args.mode, args.authorized)
