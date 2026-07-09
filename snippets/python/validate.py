from limacharlie.client import Client
from limacharlie.sdk.organization import Organization
from limacharlie.sdk.search import Search

client = Client(oid="YOUR_OID", api_key="YOUR_API_KEY")
org = Organization(client)
result = Search(org).validate("event/FILE_PATH ends with .exe")
print(result)
