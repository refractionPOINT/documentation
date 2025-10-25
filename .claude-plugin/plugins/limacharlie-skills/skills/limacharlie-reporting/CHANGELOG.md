# Changelog - LimaCharlie Reporting Skill

## Version 2.1.0 - 2025-10-25

### Major Improvements

**Simplified Server Implementation**

Replaced the complex threading-based HTTP server with a much simpler subprocess-based approach.

#### What Changed

**Before:**
- Custom HTTP server with threading
- Watchdog thread monitoring parent process
- Complex cleanup and shutdown logic
- Changed working directory during operation
- Created temporary directories with session IDs

**After:**
- Uses Python's built-in `http.server` module
- Runs as a simple background subprocess
- Serves files directly from `/tmp`
- No threading, no watchdog, no directory changes
- Clean and reliable

#### Key Benefits

1. **Reliability**: The subprocess approach is more stable and predictable
2. **Simplicity**: ~50% less code with clearer logic
3. **No Side Effects**: Doesn't change working directory or manage complex state
4. **Proven**: Uses the same approach that was manually tested and worked

#### Technical Details

The new implementation in `lib/server.py`:
- Uses `subprocess.Popen()` to spawn `python3 -m http.server`
- Serves from `tempfile.gettempdir()` (/tmp)
- Adds a 0.5s startup delay to ensure server is ready
- Subprocess runs independently and persists after script ends

#### Files Modified

- `lib/server.py` - Complete rewrite of ReportServer class
- `SKILL.md` - Updated "How It Works" section to explain subprocess approach

#### Migration

No changes needed for existing code! The API remains identical:

```python
from lib import create_and_serve_report

url = create_and_serve_report(html_content, title="My Report")
```

#### Testing

Verified with:
- Simple HTML reports
- Complete HTML documents with wrap=False
- Multiple concurrent servers on different ports
- Background persistence after script completion

All tests passed successfully.
