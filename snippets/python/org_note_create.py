from limacharlie.client import Client
from limacharlie.sdk.organization import Organization
from limacharlie.sdk.hive import Hive, HiveRecord

client = Client(oid="YOUR_OID", api_key="YOUR_API_KEY")
org = Organization(client)
Hive(org, "org_notes").set(HiveRecord(
    name="prod-network",
    data={
        "text": "# Production Network\n- 10.10.0.0/16 is production.",
        "description": "Production network layout and ownership",
    },
    enabled=True,
    tags=["network", "reference"],
))
