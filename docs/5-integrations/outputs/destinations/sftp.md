# SFTP

Output events and detections over SFTP.

- `dest_host`: the ip:port to send the data to, like `1.2.3.4:22`.
- `dir`: the directory for the files on the remote host.
- `username`: the username to log in with.
- `password`: the optional password to log in with.
- `secret_key`: the optional SSH private key to authenticate with.

Example:

```text
dest_host: storage.corp.com
dir: /uploads/
username: storage_user
password: XXXXXXXXXXXX
```

## What's Next

- [Slack](slack.md)
