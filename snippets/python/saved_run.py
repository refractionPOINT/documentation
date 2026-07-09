import time

from limacharlie.client import Client
from limacharlie.sdk.organization import Organization
from limacharlie.sdk.hive import Hive
from limacharlie.sdk.search import Search

client = Client(oid="YOUR_OID", api_key="YOUR_API_KEY")
org = Organization(client)

saved = Hive(org, "query").get("my-saved-query")
end = int(time.time())
start = end - 3600

for result in Search(org).execute(
    query=saved.data["query"],
    start_time=start,
    end_time=end,
    stream=saved.data.get("stream", "event"),
):
    print(result)
