#!/bin/sh
# Run the LimaCharlie command-line tool on a Grok Bot computer.
#
# Installed as /workspace/.limacharlie-cli/limacharlie. The tool and its
# sign-in live in /workspace/.limacharlie-cli, which survives restarts and
# moves. If a move removed the tool itself, it is reinstalled on the next run.
#
#   /workspace/.limacharlie-cli/limacharlie sensor list --output yaml
set -u

d=/workspace/.limacharlie-cli
export LC_CONFIG_DIR="$d/config"

if [ -x "$d/venv/bin/limacharlie" ]; then
  exec "$d/venv/bin/limacharlie" "$@"
fi
if [ -d "$d/lib/limacharlie" ]; then
  PYTHONPATH="$d/lib" exec python3 -m limacharlie "$@"
fi

# Not installed yet, or a move removed it. Prefer a virtual environment, and
# fall back to a plain folder where python3-venv is missing.
echo "Installing the LimaCharlie command-line tool..." >&2
rm -rf "${d:?}/venv" "${d:?}/lib"
if python3 -m venv "$d/venv" >/dev/null 2>&1 && "$d/venv/bin/pip" install -q limacharlie >&2; then
  exec "$d/venv/bin/limacharlie" "$@"
fi
rm -rf "${d:?}/venv"
if python3 -m pip install -q --target "$d/lib" limacharlie >&2; then
  PYTHONPATH="$d/lib" exec python3 -m limacharlie "$@"
fi
echo "Could not install the LimaCharlie command-line tool (pip install limacharlie failed)." >&2
exit 1
