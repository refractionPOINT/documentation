---
name: init-lc-live-dashboard
description: Initialize the live AI activity dashboard infrastructure in LimaCharlie. Creates installation key and webhook cloud sensor for receiving AI session activity summaries.
allowed-tools: Task, Bash
---

# Initialize Live AI Activity Dashboard

You are setting up the live AI activity dashboard infrastructure in LimaCharlie. This enables Claude Code sessions to post activity summaries to a webhook cloud sensor.

## Prerequisites

The `lc-essentials:limacharlie-call` skill must be loaded.

## Instructions

### Step 1: List Organizations

Use the `limacharlie-call` skill to list the user's organizations:

```
Function: list_user_orgs
Parameters: {}
```

If multiple organizations exist, ask the user which ones to configure using AskUserQuestion.

### Step 2: For Each Selected Organization

Process each organization in parallel using the `lc-essentials:limacharlie-api-executor` agent.

#### 2a: Check/Create Installation Key

First, check if the `live-ai-activity` installation key exists:

```
Function: list_installation_keys
Parameters: {"oid": "<org-uuid>"}
```

If an installation key named `live-ai-activity` does NOT exist, create it:

```
Function: create_installation_key
Parameters: {
  "oid": "<org-uuid>",
  "description": "Live AI Activity Dashboard",
  "tags": ["live-ai-dashboard"]
}
```

Save the installation key ID (iid) for the next step.

#### 2b: Check/Create Webhook Cloud Sensor

Check if the `live-ai-activity` cloud sensor exists:

```
Function: get_cloud_sensor
Parameters: {
  "oid": "<org-uuid>",
  "sensor_name": "live-ai-activity"
}
```

If the sensor does NOT exist (returns error), create it:

```
Function: set_cloud_sensor
Parameters: {
  "oid": "<org-uuid>",
  "sensor_name": "live-ai-activity",
  "sensor_config": {
    "sensor_type": "webhook",
    "webhook": {
      "secret": "<generate-random-string>",
      "signature_secret": "",
      "signature_header": "",
      "signature_scheme": "",
      "client_options": {
        "hostname": "live-ai-activity",
        "identity": {
          "oid": "<org-uuid>",
          "installation_key": "<installation-key-id>"
        },
        "platform": "json",
        "sensor_seed_key": "live-ai-activity"
      }
    }
  }
}
```

**Generate the secret**: Use bash to generate a random string:
```bash
openssl rand -hex 16
```

#### 2c: Get Webhook URL

Get the organization URLs to construct the webhook URL:

```
Function: get_org_urls
Parameters: {"oid": "<org-uuid>"}
```

The webhook URL format is:
```
https://{hooks}/{oid}/live-ai-activity/{secret}
```

Where:
- `{hooks}` is from the `hooks` field in get_org_urls response
- `{oid}` is the organization UUID
- `{secret}` is the secret configured in the cloud sensor

### Step 3: Report Results

Display the results for each organization:

```
Live AI Activity Dashboard initialized!

Organization: {org-name}
- Installation Key: live-ai-activity (created/exists)
- Cloud Sensor: live-ai-activity (created/exists)
- Webhook URL: https://xxxx.hook.limacharlie.io/{oid}/live-ai-activity/{secret}

[Repeat for each organization]

The dashboard is now ready to receive AI activity summaries.
Events will appear in the 'live-ai-activity' sensor timeline.
```

### Step 4: Save Configuration (Optional)

If the user wants to use the dashboard in this project, suggest running `/init-lc` to add the LimaCharlie guidelines to their CLAUDE.md, which includes instructions for activity posting.

## Error Handling

- **Permission denied**: Report that the user lacks permission to create installation keys or cloud sensors
- **Org not found**: Report that the organization was not found
- **Cloud sensor exists with different config**: Report that the sensor already exists and show its current configuration

## Example Output

```
Live AI Activity Dashboard initialized!

Organization: production-fleet
- Installation Key: live-ai-activity (created)
- Cloud Sensor: live-ai-activity (created)
- Webhook URL: https://9157798c50af372c.hook.limacharlie.io/c7e8f940-1234/live-ai-activity/a1b2c3d4e5f6

Organization: dev-environment
- Installation Key: live-ai-activity (already exists)
- Cloud Sensor: live-ai-activity (created)
- Webhook URL: https://9157798c50af372c.hook.limacharlie.io/d4e5f6a7-5678/live-ai-activity/f6e5d4c3b2a1

The dashboard is now ready to receive AI activity summaries.
Events will appear in the 'live-ai-activity' sensor timeline.

To enable activity posting in this project, run: /init-lc
```
