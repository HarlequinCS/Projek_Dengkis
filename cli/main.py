"""
Command-line interface for PROJEK DENGKIS.
Provides user-friendly CLI for running assessments and managing sessions.
"""
import argparse
import asyncio
import sys
from pathlib import Path
from typing import Optional

# Add engine to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from engine.runner import run_assessment, execute_attack
from engine.core.session import TestSession
from engine.network.request_handler import AggressiveRequestHandler
from engine.utils.retry import RetryConfig
from engine.utils.throttle import ThrottleConfig
from engine.storage.session_store import SessionStore
from engine.reporting.generator import ReportGenerator
from engine.visualization.visualizer import SecurityVisualizer
from engine.logging.logger import get_logger
from engine.config.manager import ConfigManager


async def cmd_scan(args):
    """
    Executes the 'scan' command.

    Initializes and runs an exploitation session against the target.
    Requires the --authorized flag.

    Args:
        args: Parsed command-line arguments.

    Returns:
        int: Exit code (0 for success, 1 for failure).
    """
    target = args.target
    authorized = args.authorized or False
    attack_mode = getattr(args, 'mode', 'aggressive') or 'aggressive'

    logger = get_logger()
    logger.info(f"[ATTACK] Starting attack on target: {target} (mode: {attack_mode})")

    if not authorized:
        logger.warning("[ATTACK] Attack requires authorization. Use --authorized flag.")
        print("=" * 70)
        print("⚠️  ERROR: Attack requires explicit authorization.")
        print("=" * 70)
        print("⚠️  WARNING: This is dangerous software that exploits vulnerabilities.")
        print("⚠️  Use ONLY on systems you own or have written permission to test.")
        print("⚠️  Unauthorized use is ILLEGAL and may result in criminal prosecution.")
        print("=" * 70)
        print("Use: dengkis scan <target> --authorized --mode aggressive")
        print("See LICENSE for complete terms and restrictions.")
        return 1

    # Initialize assessment
    assessment_result = run_assessment(target, authorized=authorized, attack_mode=attack_mode)

    if assessment_result.get('status') == 'error':
        logger.error(assessment_result.get('message', 'Unknown error'))
        print(f"ERROR: {assessment_result.get('message')}")
        return 1

    session_id = assessment_result.get('session_id')

    logger.info(f"[ATTACK] Attack initialized. Session ID: {session_id}")
    print(f"\n[ATTACK] Executing {attack_mode.upper()} attack on {target}...")
    print("=" * 60)

    # Execute attack
    from engine.runner import execute_attack
    attack_results = await execute_attack(
        target=target,
        authorized=authorized,
        attack_mode=attack_mode,
        session_id=session_id
    )

    if attack_results.get('status') == 'error':
        logger.error(attack_results.get('message', 'Unknown error'))
        print(f"ERROR: {attack_results.get('message')}")
        return 1

    # Store session
    store = SessionStore()
    session_data = {
        'session_id': session_id,
        'target': target,
        'started_at': assessment_result.get('started_at'),
        'status': 'completed',
        'attack_mode': attack_mode,
        'findings': attack_results.get('findings', []),
        'crawl_results': attack_results.get('crawl_results', {}),
        'detected_apps': attack_results.get('detected_apps', [])
    }
    store.save_session(session_data, session_id)
    logger.info(f"[ATTACK] Session saved: {session_id}")

    # Print attack results
    print("\n" + "=" * 60)
    print(f"[ATTACK] ATTACK COMPLETE")
    print("=" * 60)
    print(f"Session ID: {session_id}")
    print(f"Target: {target}")
    print(f"Attack Mode: {attack_mode.upper()}")
    print(f"\nFINDINGS: {attack_results.get('total_findings', 0)}")
    print(f"  - High Confidence: {attack_results.get('high_confidence', 0)}")
    print(f"  - Medium Confidence: {attack_results.get('medium_confidence', 0)}")
    print(f"  - Low Confidence: {attack_results.get('low_confidence', 0)}")

    if attack_results.get('detected_apps'):
        print(f"\nDETECTED VULNERABLE APPS: {len(attack_results['detected_apps'])}")
        for app in attack_results['detected_apps']:
            print(f"  - {app['name']} (confidence: {app['confidence']})")

    if attack_results.get('total_findings', 0) == 0:
        print("\n[WARNING] No findings detected.")
        if attack_results.get('detected_apps'):
            print("[WARNING] Known vulnerable app detected but 0 findings!")
            print("[WARNING] Manual testing recommended.")
        else:
            print("[INFO] Consider manual testing or different attack vectors.")

    print("\n" + "=" * 60)

    return 0


async def cmd_report(args):
    """Generate report command."""
    logger = get_logger()

    store = SessionStore()

    if args.session_id:
        session_data = store.load_session(args.session_id)
        if not session_data:
            logger.error(f"Session not found: {args.session_id}")
            print(f"ERROR: Session not found: {args.session_id}")
            return 1
    else:
        # Use most recent session
        sessions = store.list_sessions()
        if not sessions:
            logger.error("No sessions found")
            print("ERROR: No sessions found. Run a scan first.")
            return 1
        session_data = store.load_session(sessions[0]['session_id'])

    logger.info(f"Generating {args.format} report for session: {session_data.get('session_id')}")

    generator = ReportGenerator()

    # Check if this is an attack session (has attack_mode)
    if session_data.get('attack_mode'):
        # Generate attacker-style report
        report_path = generator.generate_attack_report(session_data, format=args.format)
    elif args.type == 'executive':
        report_path = generator.generate_executive_report(session_data, format=args.format)
    elif args.type == 'technical':
        report_path = generator.generate_technical_report(session_data, format=args.format)
    else:
        report_path = generator.create_interactive_dashboard(session_data)

    print(f"Report generated: {report_path}")

    if args.open and args.format == 'html':
        import webbrowser
        webbrowser.open(f"file://{Path(report_path).absolute()}")

    return 0


async def cmd_tui(args):
    """Launch tactical TUI dashboard."""
    from cli.tui_runner import run_tui_attack

    target = args.target
    authorized = args.authorized or False
    attack_mode = args.mode or 'aggressive'

    if not authorized:
        print("=" * 70)
        print("⚠️  ERROR: TUI attack requires explicit authorization.")
        print("=" * 70)
        print("⚠️  WARNING: This is dangerous software that exploits vulnerabilities.")
        print("⚠️  Use ONLY on systems you own or have written permission to test.")
        print("⚠️  Unauthorized use is ILLEGAL and may result in criminal prosecution.")
        print("=" * 70)
        print("Use: dengkis tui <target> --authorized")
        print("See LICENSE for complete terms and restrictions.")
        return 1

    try:
        await run_tui_attack(target, attack_mode, authorized)
        return 0
    except Exception as e:
        logger = get_logger()
        logger.error(f"TUI failed: {e}", exc_info=True)
        print(f"ERROR: {e}")
        return 1


async def cmd_visualize(args):
    """Generate visualizations command."""
    logger = get_logger()

    store = SessionStore()

    if args.session_id:
        session_data = store.load_session(args.session_id)
        if not session_data:
            logger.error(f"Session not found: {args.session_id}")
            print(f"ERROR: Session not found: {args.session_id}")
            return 1
    else:
        sessions = store.list_sessions()
        if not sessions:
            logger.error("No sessions found")
            print("ERROR: No sessions found. Run a scan first.")
            return 1
        session_data = store.load_session(sessions[0]['session_id'])

    logger.info("Generating visualizations...")

    visualizer = SecurityVisualizer()
    findings = session_data.get('findings', [])

    # Generate attack graph
    graph_result = visualizer.generate_attack_graph(findings, session_data)
    graph_path = Path('storage') / f"graph_{session_data.get('session_id')}.html"
    graph_path.parent.mkdir(exist_ok=True)
    graph_path.write_text(graph_result['html'])

    print(f"Visualization generated: {graph_path}")

    if args.open:
        import webbrowser
        webbrowser.open(f"file://{graph_path.absolute()}")

    return 0


def cmd_config(args):
    """Configuration management command."""
    logger = get_logger()

    config_manager = ConfigManager()

    if args.init:
        # Initialize default config
        default_config = {
            'assessment': {
                'stealth_mode': False,
                'max_concurrent_requests': 10,
                'timeout': 30.0,
                'retry_attempts': 3
            },
            'reporting': {
                'template_dir': 'templates',
                'output_dir': 'reports',
                'export_formats': ['html', 'json', 'markdown']
            }
        }
        config_manager.save_config(default_config, 'config.yaml')
        logger.info("Default configuration initialized")
        print("Configuration initialized: config/config.yaml")
        return 0

    elif args.show:
        config = config_manager.get_config()
        import json
        print(json.dumps(config, indent=2, default=str))
        return 0

    return 0


def cmd_list(args):
    """List sessions command."""
    store = SessionStore()
    sessions = store.list_sessions(target=args.target)

    if not sessions:
        print("No sessions found.")
        return 0

    print(f"\nFound {len(sessions)} session(s):\n")
    print(f"{'Session ID':<40} {'Target':<30} {'Status':<15} {'Started At'}")
    print("-" * 100)

    for session in sessions:
        print(f"{session['session_id']:<40} {session['target']:<30} {session['status']:<15} {session['started_at']}")

    return 0


def cmd_batch(args):
    """Batch scan command."""
    import asyncio
    from engine.batch.scanner import BatchScanner
    from engine.utils.retry import RetryConfig
    from engine.utils.throttle import ThrottleConfig

    logger = get_logger()

    # Read targets from file or use provided list
    targets = []
    if args.file:
        with open(args.file, 'r') as f:
            targets = [line.strip() for line in f if line.strip()]
    elif args.targets:
        targets = args.targets.split(',')
    else:
        logger.error("No targets specified. Use --file or --targets")
        print("ERROR: No targets specified")
        return 1

    logger.info(f"Starting batch scan of {len(targets)} targets")

    retry_config = RetryConfig(
        max_attempts=args.max_retries,
        timeout=args.timeout
    )
    throttle_config = ThrottleConfig(
        requests_per_second=args.rate_limit
    )

    scanner = BatchScanner(
        max_concurrent=args.max_concurrent,
        retry_config=retry_config,
        throttle_config=throttle_config
    )

    async def run_batch():
        def progress_callback(completed, total):
            print(f"Progress: {completed}/{total} targets completed", end='\r')

        result = await scanner.scan_targets(
            targets,
            authorized=args.authorized,
            progress_callback=progress_callback
        )
        return result

    try:
        result = run_coro_safe(run_batch())
        print(f"\nBatch scan completed!")
        print(f"Total: {result['total_targets']}")
        print(f"Completed: {result['completed']}")
        print(f"Failed: {result['failed']}")
        return 0
    except Exception as e:
        logger.error(f"Batch scan failed: {e}")
        print(f"ERROR: {e}")
        return 1


def cmd_search(args):
    """Search sessions command."""
    from engine.storage.session_store import SessionStore
    from engine.filters.search import FilterManager

    store = SessionStore()
    filter_manager = FilterManager()

    # Build filters
    filters = {}
    if args.target:
        filters['target'] = args.target
    if args.status:
        filters['status'] = args.status
    if args.query:
        filters['fuzzy_search'] = args.query

    sessions = store.list_sessions()
    filtered = filter_manager.filter_sessions(sessions, filters)

    if not filtered:
        print("No sessions found matching criteria.")
        return 0

    print(f"\nFound {len(filtered)} session(s):\n")
    print(f"{'Session ID':<40} {'Target':<30} {'Status':<15} {'Started At'}")
    print("-" * 100)

    for session in filtered:
        print(f"{session['session_id']:<40} {session['target']:<30} {session['status']:<15} {session['started_at']}")

    return 0


def main():
    """Main CLI entry point."""
    # Display warning banner
    print("=" * 70)
    print("⚠️  PROJEK DENGKIS - RESTRICTED USE SOFTWARE")
    print("=" * 70)
    print("⚠️  WARNING: This is dangerous software for AUTHORIZED use only.")
    print("⚠️  Unauthorized use is ILLEGAL and may result in criminal prosecution.")
    print("⚠️  Use ONLY on systems you own or have written permission to test.")
    print("⚠️  See LICENSE for complete terms and restrictions.")
    print("=" * 70)
    print()

    parser = argparse.ArgumentParser(
        description='PROJEK DENGKIS - Security Assessment Framework (AUTHORIZED USE ONLY)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='⚠️  WARNING: This is dangerous software. Use only with proper authorization. See LICENSE for restrictions.'
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Scan command
    scan_parser = subparsers.add_parser('scan', help='Run AGGRESSIVE attack scan')
    scan_parser.add_argument('target', help='Target URL or IP address')
    scan_parser.add_argument('--authorized', action='store_true', help='Explicit authorization flag (REQUIRED)')
    scan_parser.add_argument('--mode', choices=['passive', 'active', 'aggressive'], default='aggressive', help='Attack mode (default: aggressive)')
    scan_parser.add_argument('--stealth', action='store_true', help='Enable stealth mode (reduces detection)')
    scan_parser.add_argument('--timeout', type=float, default=30.0, help='Request timeout in seconds')
    scan_parser.add_argument('--max-retries', type=int, default=3, help='Maximum retry attempts')
    scan_parser.add_argument('--rate-limit', type=float, default=10.0, help='Requests per second limit')

    # Report command
    report_parser = subparsers.add_parser('report', help='Generate assessment report')
    report_parser.add_argument('--session-id', help='Session ID (uses most recent if not specified)')
    report_parser.add_argument('--format', choices=['html', 'json', 'markdown'], default='html', help='Report format')
    report_parser.add_argument('--type', choices=['executive', 'technical', 'dashboard'], default='executive', help='Report type')
    report_parser.add_argument('--open', action='store_true', help='Open report in browser (HTML only)')

    # Visualize command
    viz_parser = subparsers.add_parser('visualize', help='Generate visualizations')
    viz_parser.add_argument('--session-id', help='Session ID (uses most recent if not specified)')
    viz_parser.add_argument('--open', action='store_true', help='Open visualization in browser')

    # Config command
    config_parser = subparsers.add_parser('config', help='Configuration management')
    config_parser.add_argument('--init', action='store_true', help='Initialize default configuration')
    config_parser.add_argument('--show', action='store_true', help='Show current configuration')

    # List command
    list_parser = subparsers.add_parser('list', help='List saved sessions')
    list_parser.add_argument('--target', help='Filter by target')

    # Batch command
    batch_parser = subparsers.add_parser('batch', help='Batch scan multiple targets')
    batch_parser.add_argument('--file', help='File containing targets (one per line)')
    batch_parser.add_argument('--targets', help='Comma-separated list of targets')
    batch_parser.add_argument('--authorized', action='store_true', help='Explicit authorization flag (required)')
    batch_parser.add_argument('--max-concurrent', type=int, default=5, help='Maximum concurrent scans')
    batch_parser.add_argument('--timeout', type=float, default=30.0, help='Request timeout')
    batch_parser.add_argument('--max-retries', type=int, default=3, help='Maximum retry attempts')
    batch_parser.add_argument('--rate-limit', type=float, default=10.0, help='Requests per second limit')

    # Search command
    search_parser = subparsers.add_parser('search', help='Search sessions with filters')
    search_parser.add_argument('--query', help='Search query (fuzzy match)')
    search_parser.add_argument('--target', help='Filter by target')
    search_parser.add_argument('--status', help='Filter by status')

    # TUI command
    tui_parser = subparsers.add_parser('tui', help='Launch tactical TUI dashboard')
    tui_parser.add_argument('target', help='Target URL')
    tui_parser.add_argument('--authorized', action='store_true', help='Explicit authorization flag (REQUIRED)')
    tui_parser.add_argument('--mode', choices=['passive', 'active', 'aggressive'], default='aggressive', help='Attack mode')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # Execute command
    try:
        if args.command == 'scan':
            return run_coro_safe(cmd_scan(args))
        elif args.command == 'report':
            return run_coro_safe(cmd_report(args))
        elif args.command == 'visualize':
            return run_coro_safe(cmd_visualize(args))
        elif args.command == 'config':
            return cmd_config(args)
        elif args.command == 'list':
            return cmd_list(args)
        elif args.command == 'batch':
            return cmd_batch(args)
        elif args.command == 'search':
            return cmd_search(args)
        elif args.command == 'tui':
            return run_coro_safe(cmd_tui(args))
        else:
            parser.print_help()
            return 1
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        return 1
    except Exception as e:
        logger = get_logger()
        logger.error(f"Command failed: {e}", exc_info=True)
        print(f"ERROR: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
