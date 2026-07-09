from limacharlie.client import Client
from limacharlie.sdk.organization import Organization
from limacharlie.sdk.hive import Hive

client = Client(oid="YOUR_OID", api_key="YOUR_API_KEY")
org = Organization(client)
Hive(org, "query").delete("my-saved-query")
