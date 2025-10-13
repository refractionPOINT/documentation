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
```

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

```
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
```

### Execution environment

Playbooks contents are cached for short periods of time ( on the order of 10 seconds ) in the cloud.

Playbooks are instantiated on demand and the instance is reused for an undefined amount of time.

Playbook code only executes during the main call to the `playbook` function, background on-going running is not supported.

The execution environment is provisioned on a per-Organization basis, meaning all your playbooks may execute within the same container, but NEVER on a container used by another Organization.

Although you have access to the local environment, this environment is ephemeral and can be wiped at any moment in between executions so you should take care that your playbook is self contained and doesn’t assume pre-existing conditions.

A single execution of a playbook is limited to 10 minutes.

The current execution environment is based on the default libraries provided by the `python:slim` Dockerhub official container plus the following packages:

* Python

  + `weasyprint`
  + `flask`
  + `gunicorn`
  + `flask`
  + `limacharlie` (LimaCharlie SDK/CLI)
  + `lcextension` (LimaCharlie Extension SDK)
  + `scikit-learn` (Python Machine Learning kit)
  + `jinja2`
  + `markdown`
  + `pillow`
* NodeJS
* AI

  + Claude Code (`claude`) CLI tool
  + Codex (`codex`) CLI tool
  + Gemini CLI (`gemini`) CLI tool

Custom packages and execution environment tweaks are not available in self-serve mode, but they *may* be available on demand, get in touch with us at support@limacharlie.io.

## Infrastructure as Code

Example:

```
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

Playbooks are billed per seconds of total execution time.

LimaCharlie Extensions allow users to expand and customize their security environments by integrating third-party tools, automating workflows, and adding new capabilities. Organizations subscribe to Extensions, which are granted specific permissions to interact with their infrastructure. Extensions can be private or public, enabling tailored use or broader community sharing. This framework supports scalability, flexibility, and secure, repeatable deployments.

In LimaCharlie, an Organization represents a tenant within the SecOps Cloud Platform, providing a self-contained environment to manage security data, configurations, and assets independently. Each Organization has its own sensors, detection rules, data sources, and outputs, offering complete control over security operations. This structure enables flexible, multi-tenant setups, ideal for managed security providers or enterprises managing multiple departments or clients.

Infrastructure as Code (IaC) automates the management and provisioning of IT infrastructure using code, making it easier to scale, maintain, and deploy resources consistently. In LimaCharlie, IaC allows security teams to deploy and manage sensors, rules, and other security infrastructure programmatically, ensuring streamlined, repeatable configurations and faster response times, while maintaining infrastructure-as-code best practices in cybersecurity operations.