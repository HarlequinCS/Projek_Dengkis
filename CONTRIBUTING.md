# Contributing to PROJEK DENGKIS

Thank you for your interest in contributing to PROJEK DENGKIS! This document provides guidelines and instructions for contributing.

## ⚠️ Important Notice

**PROJEK DENGKIS is a security testing tool designed for authorized penetration testing only.**
- All contributions must align with ethical security research principles
- Contributors must ensure their code does not enable unauthorized access
- We reserve the right to reject contributions that could be misused

## Code of Conduct

- Be respectful and professional
- Focus on constructive feedback
- Respect the security and privacy of others
- Follow responsible disclosure practices

## Getting Started

1. **Fork the repository**
2. **Clone your fork**: `git clone https://github.com/your-username/Projek_Dengkis.git`
3. **Create a branch**: `git checkout -b feature/your-feature-name`
4. **Set up development environment**:
   ```bash
   pip install -r requirements.txt
   pip install -e .
   ```

## Development Guidelines

### Code Style

- Follow PEP 8 for Python code
- Use type hints where appropriate
- Maximum line length: 120 characters
- Use 4 spaces for indentation
- Write docstrings for all functions and classes

### Testing

- Write tests for all new features
- Ensure all tests pass: `pytest`
- Maintain or improve test coverage
- Add integration tests for new attack modules

### Documentation

- Update relevant documentation files
- Add docstrings to new functions/classes
- Update README.md if adding new features
- Keep documentation in `docs/` directory organized

### Commit Messages

Use clear, descriptive commit messages:
```
feat: Add new SQL injection payload variant
fix: Resolve WAF evasion false positive
docs: Update attack engine documentation
test: Add tests for flag hunter module
```

## Pull Request Process

1. **Update documentation** if needed
2. **Add tests** for new functionality
3. **Ensure all tests pass** and code is linted
4. **Update CHANGELOG.md** with your changes
5. **Create a pull request** with a clear description

### PR Checklist

- [ ] Code follows the project's style guidelines
- [ ] Tests have been added/updated and pass
- [ ] Documentation has been updated
- [ ] CHANGELOG.md has been updated
- [ ] Code has been tested manually
- [ ] No security vulnerabilities introduced

## Security Considerations

When contributing:

- **Never commit** API keys, credentials, or sensitive data
- **Review** your code for potential security issues
- **Test** your changes in a controlled environment
- **Document** any security implications of your changes

## Questions?

If you have questions about contributing, please:
- Open an issue for discussion
- Review existing documentation in `docs/`
- Check existing issues and pull requests

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.
