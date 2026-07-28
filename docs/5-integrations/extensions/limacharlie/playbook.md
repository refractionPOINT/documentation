# Playbook [LABS]

> LimaCharlie LABS

!!! warning "Python SDK v4 only"
    The Playbook execution environment runs on the LimaCharlie **Python SDK v4**.
    The new [Python SDK v5](../../../6-developer-guide/sdks/python-sdk.md)
    is **not yet supported** in playbooks. Write playbook code against the v4 APIs.
    For the supported `Manager` interface and module layout, see the
    [Python SDK v4 documentation](../../../6-developer-guide/sdks/python-sdk-v4.md).

The Playbook Extension lets you run Python playbooks in the context of your Organization. Use playbooks to automate tasks and to customize more complex detections.

You manage the playbooks in the playbook Hive Configurations. You can also manage them across tenants with the Infrastructure as Code extension.

You can trigger the execution of a playbook in these ways:

1. Interactively in the web app. Go to the Extensions section for the Playbook extension.
2. With an `extension request` action in a [D&R rule](../../../3-detection-response/examples.md).
3. With an extension request on the API directly: <https://api.limacharlie.io/static/swagger/#/Extensions/createExtensionRequest>
4. With an extension request through the Python CLI/SDK or Golang SDK.

You can therefore start a playbook automatically from events, detections, audit messages, or any other [target](../../../3-detection-response/alternate-targets.md) of D&R rules. You can also start a playbook manually for ad-hoc work.

## Enabling Extension

To enable the Playbook extension, subscribe your organization to the ext-playbook add-on.

![Enabling Extension The Playbook extension can be enabled by subscribing your organization to the ext-playbook add-on](../../../assets/images/image(317).png)

## Accessing Playbooks

You create, change, and delete playbooks with the Playbooks option in the Automation menu.

> Note: If you cannot see the Playbooks option, make sure that your user account has the necessary permissions enabled.
>
> ![Playbooks are created, modified, and deleted via the Playbooks option located within the Automation menu](../../../assets/images/image(319).png)

![Playbooks option in the Automation menu](../../../assets/images/image(321).png)

## Usage

To invoke a playbook, you need only the playbook name as defined in Hive. A playbook can also receive a JSON dictionary object as parameters. Use these parameters when you trigger a playbook from a D&R rule and you want to pass some context, or when you pass context interactively.

### D&R rule example

This example D&R rule starts a new invocation of a playbook.

```yaml
- action: extension request
  extension name: ext-playbook
  extension action: run_playbook
  extension request:
    name: '{{ "my-playbook" }}'
    credentials: '{{ "hive://secret/my-api-key" }}'
    data:
      some: event.FILE_PATH
      for_the: '{{ "running of the playbook" }}'
```

### Python example

```python
import limacharlie

# Manager picks up credentials from the environment or ~/.limacharlie.
man = limacharlie.Manager()
ext = limacharlie.Extension(man)

# Issue a request to the "ext-playbook" extension.
response = ext.request("ext-playbook", "run_playbook", {
    "name": "my-playbook",
    "credentials": "hive://secret/my-playbook-api-key",
    "data": {
        "some": "data"
    }
})

# The returned data from the playbook.
print(response)
```

## Playbook structure

A playbook is a normal python script. The only necessary component is a top level function called `playbook`. This function takes 2 arguments:

- `sdk`: an instance of the LC Python SDK v4 `limacharlie.Manager`. If you supply credentials, this instance is pre-authenticated to the relevant Organization. If you do not supply credentials, the value is `None`.
- `data`: the optional JSON dictionary that you supply as context to your playbook.

The function must return a dictionary with the following optional keys:

1. `data`: a dictionary of data to return to the caller
2. `error`: an error message (string) to return to the caller
3. `detection`: a dictionary to use as detection
4. `cat`: a string to use as the category of the detection, if `detection` is specified.

Your playbook can therefore return information about its execution, return data or errors, or generate a detection. The python `print()` statement does not go back to the caller, and you cannot access it. Use the `data` key to return information about the execution of your playbook.

### Example playbook

This sample playbook sends a webhook to an external product with a secret that LimaCharlie stores. It returns the data as the response from the playbook.

```python
import json
import urllib.request
import limacharlie

def playbook(sdk, data):
  # Get the secret we need from LimaCharlie.
  mySecret = limacharlie.Hive(sdk, "secret").get("my-secret-name").data["secret"]

  # Send the Webhook.
  request = urllib.request.Request("https://example.com/webhook", data=json.dumps(data).encode('utf-8'), headers={
    "Content-Type": "application/json",
    "Authorization": f"Bearer {mySecret}"
  }, method="POST")

  try:
    with urllib.request.urlopen(request) as response:
      response_body = response.read().decode('utf-8')
      # Parse the JSON response
      parsed_response = json.loads(response_body)
  except Exception as e:
    # Some error occured, let the caller/LC know.
    return {
      "error": str(e),
    }

  # Return the data to the caller/LC.
  return {
    "data": parsed_response,
  }
```

#### Example playbook with custom detection category

When a playbook generates a detection, you can customize the detection category name that shows in the web app. To do this, set the `cat` field at the top level of the return dictionary. Use this field to give the detections from different playbooks descriptive names, instead of the generic "playbook-detection".

This example checks if a server sensor missed a check-in. It then creates a detection with a custom category name:

```python
def playbook(sdk, data):
  if not sdk:
    return {"error": "LC API key required"}

  # Check for sensors that haven't checked in recently
  import time
  current_time = time.time()
  threshold = 3600  # 1 hour in seconds

  missing_sensors = []
  # Manager.sensors() is a v4 generator yielding Sensor objects.
  for sensor in sdk.sensors():
    info = sensor.getInfo()
    last_seen = info.get('last_seen', 0)
    if (current_time - last_seen) > threshold:
      missing_sensors.append({
        "sid": sensor.sid,
        "hostname": info.get('hostname', 'unknown')
      })

  if missing_sensors:
    # Return a detection with a custom category name
    # The 'cat' field MUST be at the top level, not inside 'detection'
    return {
      "detection": {
        "summary": f"Found {len(missing_sensors)} sensors missing check-in",
        "missing_sensors": missing_sensors
      },
      "cat": "Server-Sensor-Missing-Check-In"
    }

  # No issues found
  return {
    "data": {"status": "all sensors checked in"}
  }
```

**Important:** Put the `cat` field at the **top level** of the return dictionary, next to `detection`, not inside it. When this playbook creates a detection, the detection shows in the Detections UI with the category name "Server-Sensor-Missing-Check-In", not the default "playbook-detection".

**Without `cat`:** Detection appears as "playbook-detection → ext_playbook"

**With `cat`:** Detection appears as "Server-Sensor-Missing-Check-In → ext_playbook"

### Execution environment

The cloud caches the contents of playbooks for short periods of time (about 10 seconds).

The cloud creates a playbook instance on demand, and it reuses the instance for an undefined amount of time.

Playbook code runs only during the main call to the `playbook` function. Background execution is not supported.

The cloud provisions the execution environment for each Organization. All of your playbooks can run in the same container, but NEVER in a container that another Organization uses.

Make your playbook self contained, and do not let it assume conditions that exist before it runs. You have access to the local environment, but this environment is ephemeral. The cloud can erase it at any moment between executions.

A single execution of a playbook is limited to 10 minutes.

The current execution environment uses the default libraries of the official `python:slim` Dockerhub container, plus these packages:

- Python
  - `weasyprint`
  - `flask`
  - `gunicorn`
  - `flask`
  - `limacharlie` (LimaCharlie SDK/CLI)
  - `lcextension` (LimaCharlie Extension SDK)
  - `scikit-learn` (Python Machine Learning kit)
  - `jinja2`
  - `markdown`
  - `pillow`
- NodeJS
- AI
  - Claude Code (`claude`) CLI tool
  - Codex (`codex`) CLI tool
  - Gemini CLI (`gemini`) CLI tool

Custom packages and changes to the execution environment are not available in self-serve mode. They *can* be available on demand. For these, contact <support@limacharlie.io>.

## Infrastructure as Code

Example:

```yaml
hives:
    playbook:
        my-playbook:
            data:
                python: |-
                    def playbook(sdk, data):
                        if not sdk:
                            return {"error": "LC API key required to list sensors"}
                        return {
                            "data": {
                                "sensors": [s.getInfo() for s in sdk.sensors()]
                            }
                        }
            usr_mtd:
                enabled: true
                expiry: 0
                tags: []
                comment: ""
```

## Billing

LimaCharlie bills playbooks for each second of total execution time.
