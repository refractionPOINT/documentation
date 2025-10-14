# Azure Storage Blob

Output events and detections to a Blob Container in Azure Storage Blobs.

## Configuration Parameters

* `secret_key`: the secret access key for the Blob Container.
* `blob_container`: the name of the Blob Container to upload to.
* `account_name`: the account name used to authenticate in Azure.

## Example

```
blob_container: testlcdatabucket
account_name: lctestdata
secret_key: dkndsgnlngfdlgfd
```