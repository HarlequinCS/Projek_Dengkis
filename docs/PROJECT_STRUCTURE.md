# Project Structure

This document describes the organization and structure of the PROJEK DENGKIS repository.

## Directory Structure

```
Projek_Dengkis/
├── .github/                    # GitHub templates and workflows
│   ├── ISSUE_TEMPLATE/         # Issue templates
│   │   ├── bug_report.md
│   │   ├── feature_request.md
│   │   └── security_issue.md
│   ├── workflows/              # CI/CD workflows
│   │   └── ci.yml
│   └── PULL_REQUEST_TEMPLATE.md
├── cli/                        # Command-line interface
│   ├── __init__.py
│   ├── main.py                 # Main CLI entry point
│   └── tui_runner.py           # TUI interface runner
├── docs/                       # Documentation
│   ├── ADVANCED_MODULES.md     # Advanced attack modules documentation
│   ├── API_REFERENCE.md        # API documentation
│   ├── ARCHITECTURE.md         # System architecture
│   ├── ATTACK_ENGINE.md        # Attack engine documentation
│   ├── PERFORMANCE_TUI.md      # Performance and TUI docs
│   ├── PRODUCTION_READY.md     # Production status
│   ├── PROJECT_STRUCTURE.md    # This file
│   └── USAGE_GUIDE.md          # Usage guide
├── engine/                     # Core engine modules
│   ├── attack/                 # Attack engine components
│   ├── batch/                  # Batch processing
│   ├── config/                 # Configuration management
│   ├── core/                   # Core functionality
│   ├── filters/                # Filtering utilities
│   ├── hardening/              # Security hardening
│   ├── kali/                   # Kali Linux specific features
│   ├── logging/                # Logging utilities
│   ├── modules/                # Attack modules
│   ├── network/                # Network utilities
│   ├── performance/           # Performance optimization
│   ├── plugins/                # Plugin system
│   ├── poc/                    # Proof of concept generation
│   ├── reporting/              # Report generation
│   ├── storage/                # Data storage
│   ├── tui/                    # Terminal UI components
│   ├── utils/                  # Utility functions
│   └── visualization/         # Visualization components
├── gui/                        # Graphical user interface
│   ├── components/             # GUI components
│   ├── __init__.py
│   ├── main.py                 # GUI entry point
│   └── [various window modules]
├── scripts/                    # Utility scripts
│   ├── optimize_kali.sh       # Kali optimization script
│   └── README.md               # Scripts documentation
├── tests/                      # Test suite
│   ├── conftest.py             # Pytest configuration
│   └── test_*.py               # Test files
├── .editorconfig               # Editor configuration
├── .gitignore                  # Git ignore rules
├── CHANGELOG.md                # Version changelog
├── CONTRIBUTING.md             # Contribution guidelines
├── docker-compose.yml          # Docker Compose configuration
├── Dockerfile                  # Docker image definition
├── LICENSE                     # License file
├── pytest.ini                  # Pytest configuration
├── README.md                   # Main project README
├── requirements.txt            # Python dependencies
└── setup.py                    # Package setup script
```

## Key Directories

### `.github/`
Contains GitHub-specific files including issue templates, pull request templates, and CI/CD workflows.

### `cli/`
Command-line interface implementation. Entry point for the `dengkis` command.

### `docs/`
All project documentation including architecture, API reference, usage guides, and module documentation.

### `engine/`
Core engine implementation containing all attack modules, crawlers, injectors, and supporting utilities.

### `gui/`
Graphical user interface implementation using the chosen GUI framework.

### `scripts/`
Utility scripts for system optimization, deployment, and maintenance.

### `tests/`
Test suite with unit tests, integration tests, and test fixtures.

## File Naming Conventions

- **Python modules**: `snake_case.py`
- **Test files**: `test_*.py`
- **Documentation**: `UPPER_SNAKE_CASE.md` or `Title_Case.md`
- **Scripts**: `snake_case.sh` or `snake_case.py`
- **Configuration**: `lowercase.ini`, `lowercase.yml`, etc.

## Module Organization

### Attack Engine (`engine/attack/`)
Core attack functionality including:
- Crawling and discovery
- Payload injection
- Vulnerability detection
- Exploitation

### Advanced Modules (`engine/modules/`)
Specialized attack modules:
- Flag Hunter (CTF automation)
- Ghost Operator (WAF evasion)
- Logic Breaker (Business logic)
- Red Team Architect (Post-exploitation)
- Attacker Mindset (Intelligence)

### Reporting (`engine/reporting/`)
Report generation in multiple formats (HTML, JSON, Markdown).

### Performance (`engine/performance/`)
Performance optimization utilities and monitoring.

## Adding New Components

When adding new components:

1. **Place in appropriate directory** based on functionality
2. **Follow naming conventions** (snake_case for Python files)
3. **Add documentation** in `docs/` if it's a major feature
4. **Write tests** in `tests/` directory
5. **Update this document** if structure changes significantly

## Documentation Standards

- All public APIs should have docstrings
- Major features should have dedicated documentation files in `docs/`
- README files in subdirectories explain directory purpose
- Code examples should be included where helpful
