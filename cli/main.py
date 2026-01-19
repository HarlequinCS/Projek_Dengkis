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

from engine.runner import run_assessment
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
    """Execute security scan command."""
    target = args.target
    authorized = args.authorized or False
    
    logger = get_logger()
    logger.info(f"Starting assessment for target: {target}")
    
    if not authorized:
        logger.warning("Assessment requires authorization. Use --authorized flag.")
        print("ERROR: Assessment requires explicit authorization.")
        print("Use: dengkis scan <target> --authorized")
        return 1
    
    # Initialize assessment
    assessment_result = run_assessment(target, authorized=authorized)
    
    if assessment_result.get('status') == 'error':
        logger.error(assessment_result.get('message', 'Unknown error'))
        print(f"ERROR: {assessment_result.get('message')}")
        return 1
    
    session_id = assessment_result.get('session_id')
    session = TestSession(target=target, authorized=authorized)
    
    logger.info(f"Assessment initialized. Session ID: {session_id}")
    
    # Configure retry and throttle
    retry_config = RetryConfig(
        max_attempts=args.max_retries,
        timeout=args.timeout
    )
    throttle_config = ThrottleConfig(
        requests_per_second=args.rate_limit
    )
    
    # Perform network reconnaissance
    async with AggressiveRequestHandler(
        stealth_mode=args.stealth,
        timeout=args.timeout,
        retry_config=retry_config,
        throttle_config=throttle_config,
        session_id=session_id
    ) as handler:
        logger.info("Performing network reconnaissance...")
        
        # Extract behavioral fingerprint
        fingerprint = await handler.extract_behavioral_fingerprint(target)
        logger.info(f"Fingerprint extracted: {len(fingerprint.get('probes', []))} probes")
        
        # Store session
        store = SessionStore()
        session_data = {
            'session_id': session_id,
            'target': target,
            'started_at': assessment_result.get('started_at'),
            'status': 'completed',
            'fingerprint': fingerprint,
            'findings': []
        }
        store.save_session(session_data, session_id)
        logger.info(f"Session saved: {session_id}")
        
        print(f"\nAssessment completed successfully!")
        print(f"Session ID: {session_id}")
        print(f"Target: {target}")
        print(f"Findings: {len(session_data.get('findings', []))}")
    
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
    
    if args.type == 'executive':
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
        result = asyncio.run(run_batch())
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
    parser = argparse.ArgumentParser(
        description='PROJEK DENGKIS - Security Assessment Framework',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Scan command
    scan_parser = subparsers.add_parser('scan', help='Run security assessment')
    scan_parser.add_argument('target', help='Target URL or IP address')
    scan_parser.add_argument('--authorized', action='store_true', help='Explicit authorization flag (required)')
    scan_parser.add_argument('--stealth', action='store_true', help='Enable stealth mode')
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
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Execute command
    try:
        if args.command == 'scan':
            return asyncio.run(cmd_scan(args))
        elif args.command == 'report':
            return asyncio.run(cmd_report(args))
        elif args.command == 'visualize':
            return asyncio.run(cmd_visualize(args))
        elif args.command == 'config':
            return cmd_config(args)
        elif args.command == 'list':
            return cmd_list(args)
        elif args.command == 'batch':
            return cmd_batch(args)
        elif args.command == 'search':
            return cmd_search(args)
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
