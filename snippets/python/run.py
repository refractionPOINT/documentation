import time

from limacharlie.client import Client
from limacharlie.sdk.organization import Organization
from limacharlie.sdk.search import Search

client = Client(oid="YOUR_OID", api_key="YOUR_API_KEY")
org = Organization(client)

end = int(time.time())
start = end - 3600  # 1 hour ago

for result in Search(org).execute(
    query="event/FILE_PATH ends with .exe",
    start_time=start,
    end_time=end,
    stream="event",
    limit=100,
):
    print(result)
