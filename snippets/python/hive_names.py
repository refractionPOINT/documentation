from limacharlie.client import Client
from limacharlie.sdk.organization import Organization
from limacharlie.sdk.hive import Hive

client = Client(oid="YOUR_OID", api_key="YOUR_API_KEY")
org = Organization(client)
hive = Hive(org, "lookup")

# Names and metadata only: the record data is never loaded.
for name, record in hive.list_mtd().items():
    print(name, record.tags, record.last_modified)
