#!/usr/bin/env bash
set -euo pipefail

# --- Config ---
VENV_DIR=".venv"

echo "▶ Checking for Python 3..."
if ! command -v python3 >/dev/null 2>&1; then
  echo "❌ python3 not found. Please install Python 3.8+ and re-run."
  exit 1
fi

PYTHON="$(command -v python3)"

echo "▶ Ensuring venv module is available..."
"$PYTHON" -m venv --help >/dev/null 2>&1 || {
  echo "❌ The venv module is not available in this Python installation."
  echo "   Install the python3-venv package (Debian/Ubuntu) or equivalent."
  exit 1
}

if [ ! -d "$VENV_DIR" ]; then
  echo "▶ Creating virtual environment: $VENV_DIR"
  "$PYTHON" -m venv "$VENV_DIR"
else
  echo "▶ Reusing existing virtual environment: $VENV_DIR"
fi

# Determine venv bin path for POSIX shells
VENV_BIN="$VENV_DIR/bin"
if [ ! -d "$VENV_BIN" ]; then
  echo "❌ Could not find venv bin directory at $VENV_BIN"
  exit 1
fi

echo "▶ Activating virtual environment"
# shellcheck disable=SC1090
source "$VENV_BIN/activate"

echo "▶ Upgrading pip/setuptools/wheel"
python -m pip install --upgrade pip setuptools wheel

echo "▶ Installing LimaCharlie Python package (CLI/SDK)"
python -m pip install --upgrade limacharlie

echo "▶ Verifying installation"
# Print Python package version
python - <<'PY'
try:
    import limacharlie
    print(f"limacharlie Python package version: {getattr(limacharlie, '__version__', 'unknown')}")
except Exception as e:
    print("Failed to import limacharlie:", e)
    raise SystemExit(1)
PY

# Try to detect an 'lc' console script (if provided by the package)
LC_PATH="$VENV_BIN/lc"
if [ -x "$LC_PATH" ]; then
  echo "▶ Found lc CLI at: $LC_PATH"
  if "$LC_PATH" --version >/dev/null 2>&1; then
    echo "lc --version:"
    "$LC_PATH" --version || true
  else
    echo "ℹ️ lc CLI present but --version didn’t return info."
  fi
else
  echo "ℹ️ No 'lc' console script detected in $VENV_BIN."
  echo "  You can still use the SDK via Python (e.g., 'import limacharlie')."
fi

cat <<'NOTE'

✅ Done.

To use this environment in a new shell:
  source .venv/bin/activate

If 'lc' exists in .venv/bin, you can run:
  .venv/bin/lc --help

Tip: add an alias to your shell profile (~/.bashrc or ~/.zshrc):
  alias lc="$(pwd)/.venv/bin/lc"

NOTE
