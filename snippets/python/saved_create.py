from limacharlie.client import Client
from limacharlie.sdk.organization import Organization
from limacharlie.sdk.hive import Hive, HiveRecord

client = Client(oid="YOUR_OID", api_key="YOUR_API_KEY")
org = Organization(client)
Hive(org, "query").set(HiveRecord(
    name="my-saved-query",
    data={
        "query": "event/FILE_PATH ends with .exe",
        "stream": "event",
    },
    enabled=True,
))
