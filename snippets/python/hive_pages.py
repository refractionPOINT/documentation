from limacharlie.client import Client
from limacharlie.sdk.organization import Organization
from limacharlie.sdk.hive import Hive

client = Client(oid="YOUR_OID", api_key="YOUR_API_KEY")
org = Organization(client)
hive = Hive(org, "lookup")

# Walk the hive one page at a time, so only one page is in memory.
for page in hive.iter_pages(limit=100):
    for name, record in page.items():
        print(name, record.enabled)

# Or fetch a single page yourself and keep the cursor.
records, cursor = hive.list_page(limit=100)
while cursor:
    more, cursor = hive.list_page(limit=100, cursor=cursor)
    records.update(more)
