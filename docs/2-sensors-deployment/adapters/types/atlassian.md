# Atlassian

[Atlassian](https://www.atlassian.com/) makes products for enterprise work management, IT service management, and Agile development. The Atlassian products include:

- Bitbucket
- Confluence
- Jira Work Management (this includes a suite of products, include Jira Software, Service Management, and Product Discovery)
- Opsgenie
- Trello

Atlassian has [full documentation](https://confluence.atlassian.com/alldoc/atlassian-documentation-32243719.html) for the Cloud and the Data Center/Server editions.

LimaCharlie supports the ingestion of Jira events. A `json` webhook adapter ingests Jira events into LimaCharlie.

## Adapter Deployment

A cloud-to-cloud webhook adapter ingests Jira events. You configure the adapter to receive JSON events, and you map the fields to the Atlassian events. To create the adapter and enable the input, do these steps:

1. Create the webhook adapter with the LimaCharlie CLI.
2. Find the URL that LimaCharlie creates for the webhook adapter.
3. Give the complete URL to Jira for webhook events.

### 1. Creating the LimaCharlie Webhook Adapter

These steps come from the [generic webhook adapter creation guide](../tutorials/webhook-adapter.md).

A webhook adapter needs a set of parameters: the organization ID, an Installation Key, a platform, and mapping details. This configuration sets up a webhook adapter that ingests Jira events:

```json
{
    "sensor_type": "webhook",
    "webhook": {
       "secret": "atlassian-jira-secret",
        "client_options": {
            "hostname": "atlassian-jira",
            "identity": {
                "oid": "<your_oid>",
                "installation_key": "<your_installation_key>"
            },
            "platform": "json",
            "sensor_seed_key": "atlassian-jira-super-secret-key",
            "mapping" : {
                "event_type_path" : "webhookEvent",
                "event_time_path" : "timestamp"
            }
        }
    }
}
```

The mapping above matches the webhook event from Jira. The mapping makes these two changes:

- `event_type_path` maps to the `webhookEvent` field
- `event_time_path` maps to the `timestamp` field

### 2. Building the Webhook URL

After you create the webhook, get the webhook URL from the [Get Org URLs](https://api.limacharlie.io/static/swagger/get-org-urls) API call. To complete the webhook URL, you need this information:

- Organization ID
- Webhook name (from the config)
- Secret (from the config)

If the returned domain is `9157798c50af372c.hook.limacharlie.io`, the URL has this format:

`https://9157798c50af372c.hook.limacharlie.io/OID/HOOKNAME/SECRET`

You can give the `secret` value in the webhook URL or in an HTTP header named `lc-secret`.

### 3. Providing the URL to Jira for Webhook Events

In the Atlassian Admin window, go to **Jira Administration** > **Jira settings** > **Advanced** > **WebHooks**. Select **+ Create a WebHook**.

![image.png](../../../assets/images/image(178).png)

- Choose a name that identifies the webhook as a LimaCharlie webhook
- Give the webhook URL (see step 2 above)
- (optional) Give a description
- (optional) Give a JQL query that selects the issues that trigger webhooks. The default selection is *All issues*.

In the WebHook creation dialog, you can also select which events the webhook sends. The main event categories are:

- Issues
  - Issue events
  - Worklog
  - Comment(s)
  - Entity Properties
  - Attachment
  - Issue Link
  - Filter
- User-related
- Jira configuration
- Project-related
- Jira Software-related

By default, Jira sends issues as JSON. LimaCharlie accepts JSON directly. Save your WebHook configuration, then do an action that triggers the event.

If the configuration is correct, your Jira events appear in LimaCharlie. This is an example event:

```json
{
  "event": {
    "issue": {
      "fields": {
        "aggregateprogress": {
          "progress": 0,
          "total": 0
        },
        "aggregatetimeestimate": null,
        "aggregatetimeoriginalestimate": null,
        "aggregatetimespent": null,
        "assignee": null,
        "attachment": [],
        "comment": {
          "comments": [],
          "maxResults": 0,
          "self": "https://###.atlassian.net...",
          "startAt": 0,
          "total": 0
        },
        "components": [],
        "created": "2023-12-02T11:16:02.927-0600",
        "creator": {
          "accountId": "...",
          "accountType": "atlassian",
          "active": true,
          "avatarUrls": {
            "16x16": "...",
            "24x24": "...",
            "32x32": "...",
            "48x48": "..."
          },
          "displayName": "Matt Bromiley",
          "self": "https://###.atlassian.net...",
          "timeZone": "America/Chicago"
        },
        "customfield_10001": null,
        "customfield_10002": null,
        "customfield_10003": null,
        "customfield_10004": null,
        "customfield_10005": null,
        "customfield_10006": null,
        "customfield_10007": null,
        "customfield_10008": null,
        "customfield_10009": null,
        "customfield_10010": null,
        "customfield_10014": null,
        "customfield_10015": null,
        "customfield_10016": null,
        "customfield_10017": null,
        "customfield_10018": {
          "hasEpicLinkFieldDependency": false,
          "nonEditableReason": {
            "message": "The Parent Link is only available to Jira Premium users.",
            "reason": "PLUGIN_LICENSE_ERROR"
          },
          "showField": false
        },
        "customfield_10019": "0|hzzzzz:",
        "customfield_10020": null,
        "customfield_10021": null,
        "customfield_10022": null,
        "customfield_10023": null,
        "customfield_10024": null,
        "customfield_10025": null,
        "customfield_10026": null,
        "customfield_10027": null,
        "customfield_10028": null,
        "customfield_10029": null,
        "customfield_10030": null,
        "description": null,
        "duedate": null,
        "environment": null,
        "fixVersions": [],
        "issuelinks": [],
        "issuerestriction": {
          "issuerestrictions": {},
          "shouldDisplay": true
        },
        "issuetype": {
          "avatarId": 10318,
          "description": "Tasks track small, distinct pieces of work.",
          "entityId": "e44d856a-3c4b-4a5e-bc67-c3c93227fe18",
          "hierarchyLevel": 0,
          "iconUrl": "https://###.atlassian.net/rest/api/...",
          "id": "10001",
          "name": "Task",
          "self": "https://###.atlassian.net/rest/api/...",
          "subtask": false
        },
        "labels": [],
        "lastViewed": "2023-12-02T17:18:42.192-0600",
        "priority": {
          "iconUrl": "https://###.atlassian.net/rest/api/...",
          "id": "3",
          "name": "Medium",
          "self": "https://###.atlassian.net/rest/api/..."
        },
        "progress": {
          "progress": 0,
          "total": 0
        },
        "project": {
          "avatarUrls": {
            "16x16": "...",
            "24x24": "...",
            "32x32": "...",
            "48x48": "..."
          },
          "id": "10000",
          "key": "KAN",
          "name": "My Kanban Project",
          "projectTypeKey": "software",
          "self": "https://###.atlassian.net/rest/api/...",
          "simplified": true
        },
        "reporter": {
          "accountId": "...",
          "accountType": "atlassian",
          "active": true,
          "avatarUrls": {
            "16x16": "...",
            "24x24": "...",
            "32x32": "...",
            "48x48": "..."
          },
          "displayName": "Matt Bromiley",
          "self": "...",
          "timeZone": "America/Chicago"
        },
        "resolution": null,
        "resolutiondate": null,
        "security": null,
        "status": {
          "description": "",
          "iconUrl": "https://###.atlassian.net/",
          "id": "10000",
          "name": "To Do",
          "self": "https://###.atlassian.net/rest/api/...",
          "statusCategory": {
            "colorName": "blue-gray",
            "id": 2,
            "key": "new",
            "name": "To Do",
            "self": "https://###.atlassian.net/rest/api/..."
          }
        },
        "statuscategorychangedate": "2023-12-02T11:16:03.211-0600",
        "subtasks": [],
        "summary": "sample issue",
        "timeestimate": null,
        "timeoriginalestimate": null,
        "timespent": null,
        "timetracking": {},
        "updated": "2023-12-02T11:16:03.129-0600",
        "versions": [],
        "votes": {
          "hasVoted": false,
          "self": "https://###.atlassian.net/rest/api/...",
          "votes": 0
        },
        "watches": {
          "isWatching": true,
          "self": "https://###.atlassian.net/rest/api/...",
          "watchCount": 1
        },
        "worklog": {
          "maxResults": 20,
          "startAt": 0,
          "total": 0,
          "worklogs": []
        },
        "workratio": -1
      },
      "id": "10012",
      "key": "KAN-13",
      "self": "https://###.atlassian.net/rest/api/..."
    },
    "timestamp": 1701559124723,
    "user": {
      "accountId": "...",
      "accountType": "atlassian",
      "active": true,
      "avatarUrls": {
        "16x16": "...",
        "24x24": "...",
        "32x32": "...",
        "48x48": "..."
      },
      "displayName": "Matt Bromiley",
      "self": "...",
      "timeZone": "America/Chicago"
    },
    "webhookEvent": "jira:issue_deleted"
  },
  "routing": {...},
  "ts": "2023-12-02 23:18:44"
}
```

The Jira "webhookEvent" becomes the event type. The LimaCharlie adapter timeline also shows this event type.
