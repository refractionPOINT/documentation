"""List the searches an organization currently has open.

``slotsHeld`` is what the concurrent-query limit applies to. ``count`` is
everything the organization has open, including paginated searches parked
between pages, which are resumable but consume no slot.
"""

from limacharlie.client import Client
from limacharlie.sdk.organization import Organization
from limacharlie.sdk.search import Search

client = Client(oid="YOUR_OID", api_key="YOUR_API_KEY")
org = Organization(client)
search = Search(org)

# state defaults to "all"; "executing" and "idle" are the other choices.
listing = search.list_open_queries(state="all")
print(
    f"{listing['slotsHeld']} of {listing['limit']} slots in use, "
    f"{listing['count']} search(es) open"
)

# Only what is consuming the limit, biggest scanner first - usually the one
# worth cancelling.
executing = search.list_open_queries(state="executing")
for entry in sorted(executing["queries"], key=lambda q: q["eventsScanned"], reverse=True):
    print(entry["queryId"], entry["submittedBy"], entry["eventsScanned"], entry["query"])

# iter_open_queries walks every page, so it is not capped at one server page.
for entry in search.iter_open_queries(state="all"):
    # progressPercent is absent when the scope estimate was unavailable, which
    # means progress cannot be computed rather than that nothing has been done.
    progress = entry.get("progressPercent")
    print(entry["queryId"], entry["state"], "unknown" if progress is None else f"{progress:.0f}%")
