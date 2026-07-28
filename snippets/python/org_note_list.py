from limacharlie.client import Client
from limacharlie.sdk.organization import Organization
from limacharlie.sdk.hive import Hive

client = Client(oid="YOUR_OID", api_key="YOUR_API_KEY")
org = Organization(client)
notes = Hive(org, "org_notes")

# The index: name and description of every note, cheap to scan.
for name, record in notes.list().items():
    print(name, (record.data or {}).get("description"))

# The body of the one that matters.
print(notes.get("prod-network").data["text"])
