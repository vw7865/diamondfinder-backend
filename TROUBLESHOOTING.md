# Render.com Deployment Troubleshooting

## Common Build Issues and Solutions

### 1. Python Version Issues
**Problem:** Build fails with Python version errors
**Solution:** 
- ✅ `runtime.txt` specifies Python 3.11.0
- ✅ `render.yaml` sets `PYTHON_VERSION=3.11.0`

### 2. Import Errors
**Problem:** Module import failures
**Solution:**
- ✅ `test_imports.py` verifies all imports work
- ✅ `requirements.txt` includes all dependencies
- ✅ Build command upgrades pip first

### 3. Port Configuration
**Problem:** Service won't start due to port issues
**Solution:**
- ✅ `render.yaml` sets `PORT=8000`
- ✅ `server_api.py` uses `host="0.0.0.0"`
- ✅ Disabled `reload=True` for production

### 4. File Not Found Errors
**Problem:** Missing files during build
**Solution:**
- ✅ All required files are in repository
- ✅ `enriched_servers.json` is included
- ✅ Build process is sequential

## Debugging Steps

### 1. Check Render.com Logs
1. Go to your service dashboard
2. Click "Logs" tab
3. Look for error messages in build logs

### 2. Test Locally
```bash
# Test imports
python3 test_imports.py

# Test server startup
python3 server_api.py

# Test health endpoint
curl http://localhost:8000/health
```

### 3. Verify Files
```bash
# Check all required files exist
ls -la server_api.py server_enricher_v2.py requirements.txt render.yaml runtime.txt
```

## Build Process

The build process now includes:
1. **Upgrade pip** - Ensures latest package manager
2. **Install requirements** - All Python dependencies
3. **Test imports** - Verify everything works
4. **Start server** - Production-ready configuration

## Environment Variables

- `PYTHON_VERSION=3.11.0` - Explicit Python version
- `PYTHONUNBUFFERED=1` - Real-time logging
- `PORT=8000` - Service port

## Health Check

The service includes a health check at `/health` that verifies:
- ✅ Server is responding
- ✅ Enriched data file exists
- ✅ Server count is available

## Common Error Messages

| Error | Cause | Solution |
|-------|-------|----------|
| `ModuleNotFoundError` | Missing dependency | Check `requirements.txt` |
| `Port already in use` | Port conflict | Verify `PORT=8000` |
| `File not found` | Missing file | Check repository contents |
| `Python version` | Version mismatch | Verify `runtime.txt` |

## Support

If issues persist:
1. Check Render.com documentation
2. Review build logs carefully
3. Test locally first
4. Verify all files are committed 