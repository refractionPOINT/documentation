# Elastic

Output events and detections to [Elastic](https://www.elastic.co/).

  * `addresses`: the IPs or DNS where to send the data to.

  * `index`: the index name to send data to.

  * `username`: user name if using username/password auth. (use either username/password -or- API key)

  * `password`: password if using username/password auth.

  * `cloud_id`: Cloud ID from Elastic.

  * `api_key`: API key; if using it for auth. (use either username/password -or- API key)




Example:
    
    
    addresses: 11.10.10.11,11.10.11.11
    username: some
    password: pass1234
    index: limacharlie
