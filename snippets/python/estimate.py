import time

from limacharlie.client import Client
from limacharlie.sdk.organization import Organization
from limacharlie.sdk.search import Search

client = Client(oid="YOUR_OID", api_key="YOUR_API_KEY")
org = Organization(client)

end = int(time.time())
start = end - 3600

result = Search(org).estimate(
    query="event/FILE_PATH ends with .exe",
    start_time=start,
    end_time=end,
)
print(result)
