# NIMS

Notion Incident Management System (NIMS) helps SOC and IR teams collaborate on incidents. It is not a replacement for an advanced SIEM or a SOAR case management system. It is an alternative for teams that do not have these tools.

The Notion template uses connected relational databases to track incidents and manage cases.

The LimaCharlie NIMS extension lets you send detections from LimaCharlie to NIMS through the Notion API.

After you subscribe an org to the extension, it creates a D&R rule. The rule sends all detections from your org to your NIMS alert database.

A Notion database has a limit on the number of records. The extension can therefore purge old alerts. It purges an alert that has no link to an incident and is older than the number of days that you specify. The extension also creates a D&R rule for this cleanup. Your configuration controls if the cleanup runs automatically.

The [NIMS project page on Notion](https://nims-template.notion.site/) gives more information, including the template and its documentation.

## Configuration

To use this extension, you need 3 pieces of data:

- Notion authentication token
- NIMS Alert database ID
- NIMS Asset database ID

### Find your database IDs

1. Go to the Alert database in NIMS under `Databases`
2. Right click on the database and click `Copy link`[![NIMS database link button screenshot](https://github.com/shortstack/nims-webhook/raw/main/screenshots/link.png)](https://github.com/shortstack/nims-webhook/blob/main/screenshots/link.png)
3. Find the database ID in the URL

    - The database ID is the long string of letters and numbers in the URL. It comes after the last `/`, and before the `?` or the `#` if one is present
    - Example:

        - Link: `https://www.notion.so/184cdc5a1ef3710badc2d2b1271aeb81?v=174cdc3a1ef181719981000cab12bf54&pvs=4`
        - ID: `184cdc5a1ef3710badc2d2b1271aeb81`
4. Copy the ID
5. Repeat the steps above for the Asset database

### Generate an auth token

These steps create a Notion integration, get the auth token, and add the integration to the correct NIMS databases.

In the steps below, add the connection to all 3 databases: Alert, Asset, and Incident. The Incident database is necessary only for the cleanup of alerts, which checks if an alert has a link to an incident.

1. Go to `Manage connections` in Notion [![connection](https://github.com/shortstack/nims-webhook/raw/main/screenshots/connection.png)](https://github.com/shortstack/nims-webhook/blob/main/screenshots/connection.png)
2. Click `Develop or manage integrations`[![connection](https://github.com/shortstack/nims-webhook/raw/main/screenshots/manage.png)](https://github.com/shortstack/nims-webhook/blob/main/screenshots/manage.png)
3. Click `New integration`[![connection](https://github.com/shortstack/nims-webhook/raw/main/screenshots/new.png)](https://github.com/shortstack/nims-webhook/blob/main/screenshots/new.png)
4. Configure the new integration

    - Give it a name, for example `nims_template`
    - Choose the workspace
    - Type: `Internal`
    - Click `Save` [![connection](https://github.com/shortstack/nims-webhook/raw/main/screenshots/integration.png)](https://github.com/shortstack/nims-webhook/blob/main/screenshots/integration.png)
5. Click `Configure integration settings` [![connection](https://github.com/shortstack/nims-webhook/raw/main/screenshots/configure.png)](https://github.com/shortstack/nims-webhook/blob/main/screenshots/configure.png)
6. Copy the `Internal Integration Secret`. This is your auth token

    - Click `Save` [![connection](https://github.com/shortstack/nims-webhook/raw/main/screenshots/token.png)](https://github.com/shortstack/nims-webhook/blob/main/screenshots/token.png)
7. Go to your `Alert Database`

    - Click the 3-dot menu and find `Connections`
    - Click the integration that you created [![connection](https://github.com/shortstack/nims-webhook/raw/main/screenshots/alerts.png)](https://github.com/shortstack/nims-webhook/blob/main/screenshots/alerts.png)
8. Click `Confirm`
    [![connection](https://github.com/shortstack/nims-webhook/raw/main/screenshots/confirm.png)](https://github.com/shortstack/nims-webhook/blob/main/screenshots/confirm.png)
9. Repeat steps 7 and 8 for the `Asset Database` and the `Incident Database`

## Example D&R rule

**Detect:**

```yaml
op: exists
path: cat
target: detection
```

**Respond:**

```yaml
- action: extension request
  extension action: push_detections
  extension name: ext-nims
  extension request:
    cat: '{{ .cat }}'
    detection: '{{json .detect }}'
    event_time: '{{ .routing.event_time }}'
    hostname: '{{ .routing.hostname }}'
    int_ip: '{{ .routing.int_ip }}'
    link: '{{ .link }}'
    metadata: '{{json .detect_mtd }}'
```

## Related

- [OTX](otx.md)
