# Playbook (Python SDK v5): alert when sensors stop sending data.
#
# Run it on a schedule from a D&R rule. Each run checks every sensor matching
# SELECTOR and looks for data received from it during the last
# THRESHOLD_MINUTES. Sensors with no data are tagged with SILENT_TAG and
# reported in a single detection. A tagged sensor is not reported again until
# the tag expires (REALERT_HOURS) or the sensor sends data again, which
# removes the tag.
#
# Every setting can be overridden per D&R rule through the `data` of the
# extension request, which the playbook receives as data["data"].
import time
from concurrent.futures import ThreadPoolExecutor

from limacharlie.sdk.sensor import Sensor

# Sensors to watch, as a sensor selector. For example:
#   "`firewall` in tags"   sensors tagged "firewall"
#   "plat == fortigate"    all FortiGate sensors
SELECTOR = "`firewall` in tags"
# Report a sensor once it has sent no data for this many minutes.
THRESHOLD_MINUTES = 60
# Tag applied to sensors that are currently silent.
SILENT_TAG = "data-silent"
# Report a sensor again if it is still silent after this many hours.
# 0 reports it only once per outage.
REALERT_HOURS = 24
# Also report sensors that start sending data again. A run returns a single
# detection, so when the same run also finds newly silent sensors, the
# recovered ones are listed in that sensor-data-silent detection instead.
REPORT_RECOVERY = False
# Number of sensors checked in parallel.
WORKERS = 8


def _setting(data, key, default):
    value = data.get(key)
    if value is None or value == "":
        return default
    if isinstance(default, bool):
        return str(value).lower() in ("1", "true", "yes")
    return type(default)(value)


def playbook(sdk, data):
    if sdk is None:
        return {"error": "this playbook requires credentials"}
    data = (data or {}).get("data") or {}
    selector = _setting(data, "selector", SELECTOR)
    threshold_minutes = _setting(data, "threshold_minutes", THRESHOLD_MINUTES)
    silent_tag = _setting(data, "silent_tag", SILENT_TAG)
    realert_hours = _setting(data, "realert_hours", REALERT_HOURS)
    report_recovery = _setting(data, "report_recovery", REPORT_RECOVERY)

    sensors = list(sdk.list_sensors(selector=selector))
    already_silent = {
        s["sid"]
        for s in sdk.list_sensors(selector=f"({selector}) and `{silent_tag}` in tags")
    }

    end = int(time.time())
    start = end - threshold_minutes * 60

    def has_data(info):
        # The overview lists the times at which data from this sensor was
        # stored. An empty list means nothing arrived during the window.
        # An error (for example a sensor deleted since it was listed) skips
        # that sensor for this run instead of failing the whole run.
        try:
            return len(Sensor(sdk, info["sid"]).get_overview(start, end)) > 0
        except Exception as e:
            return e

    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        results = list(pool.map(has_data, sensors))

    newly_silent = []
    recovered = []
    errors = []
    for info, sent_data in zip(sensors, results):
        sensor = Sensor(sdk, info["sid"])
        entry = {"sid": info["sid"], "hostname": info.get("hostname", "")}
        try:
            if isinstance(sent_data, Exception):
                raise sent_data
            if not sent_data and info["sid"] not in already_silent:
                # The tag expiring after REALERT_HOURS is what re-arms the alert.
                sensor.add_tag(silent_tag, ttl=realert_hours * 3600 if realert_hours else None)
                newly_silent.append(entry)
            elif sent_data and info["sid"] in already_silent:
                sensor.remove_tag(silent_tag)
                recovered.append(entry)
        except Exception as e:
            errors.append({**entry, "error": str(e)})

    summary = {
        "checked": len(sensors),
        "silent": results.count(False),
        "newly_silent": newly_silent,
        "recovered": recovered,
        "errors": errors,
    }

    if newly_silent:
        return {
            "detection": {
                "summary": f"{len(newly_silent)} sensor(s) sent no data in the last {threshold_minutes} minutes",
                "selector": selector,
                "threshold_minutes": threshold_minutes,
                "sensors": newly_silent,
                "recovered": recovered,
            },
            "cat": "sensor-data-silent",
            "data": summary,
        }
    if recovered and report_recovery:
        return {
            "detection": {
                "summary": f"{len(recovered)} sensor(s) started sending data again",
                "selector": selector,
                "sensors": recovered,
            },
            "cat": "sensor-data-resumed",
            "data": summary,
        }
    return {"data": summary}
