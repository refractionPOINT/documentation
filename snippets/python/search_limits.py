"""Read an organization's resolved search limits.

Every value here is otherwise discoverable only by hitting it, so read it once
and size the client to it. A limit that is not enforced comes back as ``None``,
never ``0`` - in a document of limits a zero would read as "nothing allowed".
"""

from limacharlie.client import Client
from limacharlie.sdk.organization import Organization
from limacharlie.sdk.search import Search

client = Client(oid="YOUR_OID", api_key="YOUR_API_KEY")
org = Organization(client)

limits = Search(org).get_limits()

print(f"concurrent queries: {limits['concurrency']['maxConcurrentQueries']}")
print(f"results per page:   {limits['pagination']['resultsPerPage']}")
print(f"max page duration:  {limits['pagination']['maxPageDurationSeconds']}s")
print(f"resumable for:      {limits['retention']['resumableForSeconds']}s")
print(f"page results kept:  {limits['retention']['pageResultsForSeconds']}s")
print(f"open-query listing: {limits['capabilities']['openQueryListing']}")

# None means the limit is not enforced, so check for it rather than treating a
# falsy value as "no time allowed".
max_query_seconds = limits["execution"]["maxQueryDurationSeconds"]
if max_query_seconds is None:
    print("query duration:     not enforced")
else:
    print(f"query duration:     cut off after {max_query_seconds}s")
