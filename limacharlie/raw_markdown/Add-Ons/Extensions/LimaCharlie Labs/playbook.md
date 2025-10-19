# Playbook [LABS]

> LimaCharlie LABS

The Playbook Extension allows you to execute Python playbooks within the context of your Organization in order to automate tasks and customize more complex detections.

The playbooks themselves are managed in the playbook [Hive](../../../Platform%20Management/Config%20Hive/config-hive-dr-rules.md) Configurations and can be managed across tenants using the Infrastructure as Code extension.

The execution of a playbook can be triggered through the following means:

  1. Interactively in the web app by going to the Extensions section for the Playbook extension.

  2. By issuing an `extension request` action through a [D&R rule](../../../Detection%20and%20Response/detection-and-response-examples.md).

  3. By issuing an extension request on the API directly: <https://api.limacharlie.io/static/swagger/#/Extensions/createExtensionRequest>

  4. By issuing an extension request through the Python CLI/SDK or Golang SDK.

This means playbooks can be issued in a fully automated fashion based on events, detections, audit messages or any other [target](../../../Detection%20and%20Response/detection-on-alternate-targets.md) of D&R rules. But it can also be used in an ad-hoc fashion triggered manually.

## Enabling Extension

The Playbook extension can be enabled by subscribing your organization to the ext-playbook add-on.

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/image(317).png)

## Accessing Playbooks

Playbooks are created, modified, and deleted via the Playbooks option located within the Automation menu.

> Note: If you are unable to see the Playbooks option, ensure your user account has the appropriate permissions enabled.
>
> ![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/image(319).png)

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/image(321).png)

## Usage

When invoking a playbook, all you need is the playbook name as defined in Hive. Optionally, a playbook can also receive a JSON dictionary object as parameters, this is useful when triggering a playbook from a D&R rule and you want to pass some context, or when passing context interactively.

### D&R rule example

Here is an example D&R rule starting a new invocation of a playbook.
    
    
    - action: extension request
      extension name: ext-playbook
      extension action: run_playbook
      extension request:
        name: '{{ "my-playbook" }}'
        credentials: '{{ "hive://secret/my-api-key" }}'
        data:
          some: event.FILE_PATH
          for_the: '{{ "running of the playbook" }}'

### Python example
    
    
    # Import LC SDK
    import limacharlie
    # Instantiate the SDK with default creds.
    lc = limacharlie.Manager()
    # Instantiate the Extension manager object.
    ext = limacharlie.Extension(lc)
    
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

## Playbook structure

A playbook is a normal python script. The only required component is a top level function called `playbook` which takes 2 arguments:

  * `sdk`: an instance of the LC Python SDK ( `limacharlie.Manager()` ) pre-authenticated to the relevant Organization based on the credentials provided, if any, `None` otherwise.

  * `data`: the optional JSON dictionary provided as context to your playbook.

The function must return a dictionary with the following optional keys:

  1. `data`: a dictionary of data to return to the caller

  2. `error`: an error message (string) to return to the caller

  3. `detection`: a dictionary to use as detection

  4. `cat`: a string to use as the category of the detection, if `detection` is specified.

This allows your playbook to return information about its execution, return data, errors or generate a detection. The python `print()` statement is not currently being returned to the caller or otherwise accessible, so you will want to use the `data` in order to return information about the execution of your playbook.

#### Example playbook

The following is a sample playbook that sends a webhook to an external product with a secret stored in LimaCharlie, and it returns the data as the response from the playbook.
    
    
    import limacharlie
    import json
    import urllib.request
    
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

### Execution environment

Playbooks contents are cached for short periods of time ( on the order of 10 seconds ) in the cloud.

Playbooks are instantiated on demand and the instance is reused for an undefined amount of time.

Playbook code only executes during the main call to the `playbook` function, background on-going running is not supported.

The execution environment is provisioned on a per-Organization basis, meaning all your playbooks may execute within the same container, but NEVER on a container used by another Organization.

Although you have access to the local environment, this environment is ephemeral and can be wiped at any moment in between executions so you should take care that your playbook is self contained and doesn’t assume pre-existing conditions.

A single execution of a playbook is limited to 10 minutes.

The current execution environment is based on the default libraries provided by the `python:slim` Dockerhub official container plus the following packages:

  * Python
    * `weasyprint`
    * `flask`
    * `gunicorn`
    * `flask`
    * `limacharlie` (LimaCharlie SDK/CLI)
    * `lcextension` (LimaCharlie Extension SDK)
    * `scikit-learn` (Python Machine Learning kit)
    * `jinja2`
    * `markdown`
    * `pillow`

  * NodeJS

  * AI
    * Claude Code (`claude`) CLI tool
    * Codex (`codex`) CLI tool
    * Gemini CLI (`gemini`) CLI tool

Custom packages and execution environment tweaks are not available in self-serve mode, but they _may_ be available on demand, get in touch with us at support@limacharlie.io.

## Infrastructure as Code

Example:
    
    
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
    

## Billing

Playbooks are billed per seconds of total execution time.