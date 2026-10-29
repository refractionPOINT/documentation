from limacharlie.client import Client
from limacharlie.sdk.organization import Organization
from limacharlie.sdk.usp import USP

client = Client(oid="YOUR_OID", api_key="YOUR_API_KEY")
org = Organization(client)

result = USP(org).validate(
    platform="text",
    mapping={
        "parsing_re": r"^(?P<ts>\S+) (?P<host>\S+) (?P<action>\S+) (?P<msg>.*)$",
        "event_type_path": "action",
        "event_time_path": "ts",
        "sensor_hostname_path": "host",
    },
    text_input="2026-10-29T12:00:00Z fw01 DENY blocked 10.0.0.5 -> 8.8.8.8\n",
)

for event in result["results"]:
    print(event["event_type"], event["event_time"], event["json_payload"])
for error in result["errors"]:
    print("error:", error)
