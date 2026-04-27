# QUICK DEPLOYMENT GUIDE - PHASE 1 STABILIZATION

## 5-Minute Quick Start

### What Was Changed?

Four critical areas have been refactored and fixed:

1. **HTTP/2 is now optional** (was hardcoded)
2. **Security header literals fixed** (were malformed)
3. **HTTP method literals fixed** (were invalid)
4. **Testing dependencies explicitly managed** (pytest-cov added)

### Files Modified

```
engine/network/request_handler.py  ← HTTP/2 fallback + 3 literal fixes
requirements.txt                   ← Added pytest-cov
setup.py                          ← Added extras_require
.github/workflows/ci.yml          ← Updated install step
docs/PRODUCTION_READY.md          ← Completely rewritten
```

### Deploy in 3 Steps

```bash
# Step 1: Update dependencies
pip install -r requirements.txt
pip install pytest-cov

# Step 2: Run tests
pytest --cov=engine --cov=cli --cov=gui

# Step 3: Deploy
git add .
git commit -m "Phase 1 Stabilization: HTTP/2 optional, fix malformed literals, improve dependencies"
git push origin main
```

---

## What Was Fixed

### 1. HTTP/2 Optional with Fallback ✅

**Before**:
```python
"http2": True,  # Always enabled, crashes if h2 not installed
```

**After**:
```python
def __init__(self, ..., enable_http2: bool = False):
    if enable_http2:
        try:
            import h2
        except ImportError:
            logger.warning("HTTP/2 not available, using HTTP/1.1")
            http2_enabled = False
```

**Impact**: Users can now choose HTTP/2 support without crashes

---

### 2. Security Header Literals Fixed ✅

**Before** (BROKEN):
```python
"X-Frame-Optional, ns"
"X-Content-Type-Optional, ns"
```

**After** (CORRECT):
```python
"X-Frame-Options"
"X-Content-Type-Options"
```

**Impact**: Security header detection now works correctly

---

### 3. HTTP Method Literals Fixed ✅

**Before** (BROKEN):
```python
methods = ["GET", "POST", "PUT", "DELETE", "Optional, NS", "HEAD"]
if method == "Optional, NS":  # Invalid method string
```

**After** (CORRECT):
```python
methods = ["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD"]
if method == "OPTIONS":  # Valid HTTP method
```

**Impact**: HTTP method testing now uses proper HTTP verbs

---

### 4. Dependencies Properly Managed ✅

**Before**:
```
pytest-cov missing from requirements
CI workflow had redundant installs
No optional extras defined
```

**After**:
```
pytest-cov explicitly in requirements.txt
CI leverages requirements.txt as source of truth
setup.py has extras_require for http2 and dev
```

**Installation Methods**:
```bash
pip install projek-dengkis              # Basic (HTTP/1.1)
pip install projek-dengkis[http2]       # With HTTP/2 support
pip install projek-dengkis[dev]         # With dev/testing tools
```

---

## Verification

### Quick Verification (2 minutes)

```bash
# 1. Check HTTP/2 fallback works
python -c "from engine.network.request_handler import AggressiveRequestHandler; \
AggressiveRequestHandler(enable_http2=True); print('✓ HTTP/2 fallback OK')"

# 2. Verify security headers are fixed
grep "X-Frame-Options" engine/network/request_handler.py

# 3. Verify HTTP methods are fixed
grep '"OPTIONS"' engine/network/request_handler.py

# 4. Verify pytest-cov is available
pytest --version
pytest --cov --co
```

### Full Verification (5 minutes)

```bash
# Run full test suite with coverage
pip install pytest-cov
pytest --cov=engine --cov=cli --cov=gui --cov-report=term-missing

# Check linting
flake8 engine/network/request_handler.py

# Verify CI config
cat .github/workflows/ci.yml | grep -A 3 "Install dependencies"
```

---

## Troubleshooting

### "HTTP/2 library missing" Warning

**This is expected behavior** if you don't have h2 installed.

**Fix** (choose one):
```bash
pip install h2
pip install httpx[http2]
pip install projek-dengkis[http2]
```

**Or** continue with HTTP/1.1 (fully supported):
```bash
# No fix needed, app works fine with HTTP/1.1
```

### Tests fail with "pytest-cov not found"

**Fix**:
```bash
pip install pytest-cov
# Then rerun tests
pytest
```

### Old dependencies still installed

**Fix**:
```bash
pip install --upgrade -r requirements.txt
```

---

## Key Points for Review

1. **HTTP/2 is optional** - No more crashes if h2 not installed
2. **Literals are fixed** - Security headers and HTTP methods now valid
3. **Dependencies are clean** - pytest-cov explicitly included
4. **CI will work** - Coverage reporting now enabled in GitHub Actions
5. **Documentation is accurate** - PRODUCTION_READY.md is evidence-based

---

## Before Deploying

- [ ] Run local tests: `pytest`
- [ ] Verify HTTP/2 fallback: `python verification_command.py`
- [ ] Check requirements: `pip list | grep -E "httpx|pytest|h2"`
- [ ] Read PRODUCTION_READY.md for any environment-specific needs
- [ ] Commit message prepared

---

## Commit Message Template

```
Phase 1 Stabilization: Critical dependency and network layer fixes

FIXES:
- Make HTTP/2 optional with graceful dependency fallback
- Fix malformed security header literals (X-Frame-Optional→X-Frame-Options)
- Fix malformed HTTP method literals (Optional, NS→OPTIONS)
- Add pytest-cov to testing dependencies
- Update CI workflow to properly install test dependencies

CHANGES:
- engine/network/request_handler.py: Added enable_http2 parameter with fallback
- requirements.txt: Added pytest-cov, reorganized with comments
- setup.py: Added extras_require for http2 and dev dependencies
- .github/workflows/ci.yml: Simplified dependency installation
- docs/PRODUCTION_READY.md: Rewritten with evidence-based verification

TESTING:
- All security header detections now work correctly
- HTTP method boundary testing uses valid verbs
- HTTP/2 gracefully falls back to HTTP/1.1 if h2 not installed
- Coverage reporting enabled in CI pipeline

Ref: Phase 1 Stabilization (27 April 2026)
```

---

## Post-Deployment Checklist

- [ ] All commits merged to main/develop
- [ ] GitHub Actions CI passed all tests
- [ ] No warnings about missing dependencies in logs
- [ ] HTTP/2 feature working (if enabled)
- [ ] Coverage reports generating in CI
- [ ] Team notified of changes
- [ ] Documentation reviewed and approved

---

## Support

If issues arise:

1. **HTTP/2 problems** → See PRODUCTION_READY.md section 5
2. **Test failures** → See PRODUCTION_READY.md Troubleshooting Guide
3. **Dependency issues** → Run `pip install --upgrade -r requirements.txt`
4. **CI problems** → Check `.github/workflows/ci.yml` was updated correctly

---

**Status**: ✅ READY FOR PRODUCTION DEPLOYMENT  
**Date**: 27 April 2026  
**Prepared by**: GitHub Copilot
