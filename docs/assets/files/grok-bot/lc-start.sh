#!/usr/bin/env bash
# Keep LimaCharlie running on a Grok Bot computer.
#
# Grok Bot computers have no start-on-boot: nothing restarts the sensor after
# the computer sleeps, restarts or moves. A Grok Bot routine runs this script
# every 15 minutes:
#
#   sudo -n /workspace/.limacharlie/lc-start.sh
#
# It starts the LimaCharlie sensor if it is not running and rewrites the Chrome
# policy that loads the LimaCharlie browser extension if a move wiped it. The
# sensor keeps its identity in /workspace/.limacharlie/sensor, which survives
# moves, so it always comes back as the same sensor.
#
# It prints one JSON line and saves it to /workspace/.limacharlie/status.json:
#   "ok"       everything was already running
#   "restored" something was missing and is now back
#   "problem"  something is still missing; "detail" says what
set -u

LC_HOME=/workspace/.limacharlie
SENSOR_DIR="$LC_HOME/sensor"
STATUS_FILE="$LC_HOME/status.json"

report() {
  local line policy detail
  # Keep the line valid JSON whatever the messages contain.
  policy=$(printf '%s' "$3" | tr -d '"\\\n')
  detail=$(printf '%s' "$4" | tr -d '"\\\n')
  line=$(printf '{"status":"%s","sensor":"%s","browser_policy":"%s","detail":"%s","checked_at":"%s"}' \
    "$1" "$2" "$policy" "$detail" "$(date -u +%Y-%m-%dT%H:%M:%SZ)")
  # A umask instead of chmod: the sensor-tamper rule reports any chmod of a
  # file in the sensor folder.
  (umask 022; printf '%s\n' "$line" >"$STATUS_FILE")
  printf '%s\n' "$line"
}

if [ "$(id -u)" != 0 ]; then
  echo '{"status":"problem","detail":"run it with sudo: sudo -n /workspace/.limacharlie/lc-start.sh"}'
  exit 1
fi

if [ ! -x "$LC_HOME/rphcp" ] || [ ! -s "$SENSOR_DIR/lc_installation_key.txt" ]; then
  report problem missing unknown "LimaCharlie is not set up on this computer: the sensor or its key is missing from $LC_HOME"
  exit 1
fi

# Sensor: start it if it is not running.
restored=false
sensor=running
if ! pgrep -x rphcp >/dev/null; then
  # -d - runs the sensor from its working directory without installing a
  # service. It reads its key from lc_installation_key.txt there and its
  # identity from LC_DATA_DIRECTORY, so it reconnects as the same sensor.
  (cd "$SENSOR_DIR" && LC_DATA_DIRECTORY="$SENSOR_DIR" setsid "$LC_HOME/rphcp" -d - </dev/null >/dev/null 2>&1 &)
  restored=true
  sensor=started
fi

# Wait up to 60 seconds for the sensor's connection to the LimaCharlie cloud.
connected=false
for i in $(seq 1 12); do
  if ss -tnpH state established 2>/dev/null | grep '"rphcp"' | grep -q ':443 '; then
    connected=true
    break
  fi
  # A sensor that was already running only gets a short grace period.
  if [ "$sensor" = running ] && [ "$i" -ge 2 ]; then
    break
  fi
  sleep 5
done

# Browser extension: make sure the Chrome policy files are in place.
policy=$(python3 "$LC_HOME/chrome_policy.py" 2>&1)
policy_rc=$?
case "$policy" in
  changed) restored=true ;;
esac

if ! pgrep -x rphcp >/dev/null; then
  report problem stopped "$policy" "the sensor did not start; see $SENSOR_DIR/hcp.log"
  exit 1
fi
if [ "$policy_rc" -ne 0 ]; then
  report problem "$sensor" error "could not write the Chrome policy: $policy"
  exit 1
fi
if [ "$connected" != true ]; then
  if [ "$sensor" = started ]; then
    report problem "$sensor" "$policy" "the sensor started but has not connected yet; it will be checked again on the next run"
  else
    report problem "$sensor" "$policy" "the sensor is running but is not connected to LimaCharlie"
  fi
  exit 1
fi

if [ "$restored" = true ]; then
  report restored "$sensor" "$policy" "the computer had restarted or moved; LimaCharlie is running again"
else
  report ok "$sensor" "$policy" ""
fi
exit 0
