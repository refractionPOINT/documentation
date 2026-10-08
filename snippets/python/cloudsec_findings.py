from limacharlie.client import Client
from limacharlie.sdk.organization import Organization
from limacharlie.sdk.cloudsec import CloudSec

client = Client(oid="YOUR_OID", api_key="YOUR_API_KEY")
cs = CloudSec(Organization(client))

# Keep the filters identical when requesting each subsequent page.
cursor = None
while True:
    page = cs.list_findings(severity=["CRITICAL"], kev=True, limit=100, cursor=cursor)
    for finding in page.get("findings", []):
        print(finding["lc_risk"], finding["title"], finding["resource_urn"])
    cursor = page.get("next_cursor")
    if not cursor:
        break
