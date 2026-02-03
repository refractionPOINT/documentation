# AI Agent Engine [LABS]

The AI Agent Engine Extension allows you to easily codify and execute AI Agents within the context of your Organization with access to the LimaCharlie APIs for investigation, remediation and automation.

The AI Agent definition themselves are managed in the `ai_agent` Hive Configurations and can be managed across tenants using the Infrastructure as Code extension. This hive requires the `ai_agent.*` permissions.

The execution of an AI Agent can be triggered through the following means:

1. Interactively in the web app by going to the Extensions section for the AI Agent Engine extension.
2. By issuing an `extension request` action through a [D&R rule](../../../3-detection-response/examples.md).
3. By issuing an extension request on the API directly: https://api.limacharlie.io/static/swagger/#/Extensions/createExtensionRequest
4. By issuing an extension request through the Python CLI/SDK or Golang SDK, which means they're also available to [Playbooks](playbook.md).

This means agents can be invoked in a fully automated fashion based on events, detections, audit messages or any other [target](../../../3-detection-response/alternate-targets.md) of  rules. But it can also be used in an ad-hoc fashion triggered manually.

## Usage

When invoking an AI Agent, all you need is the playbook name as defined in Hive and an initial message. Optionally, an AI Agent can also receive a JSON dictionary object as parameters, this is useful when passing the AI Agent additional context like a detection or event from a D&R rule.

Interactions with the agent are associated with a given (Interactive) Session ID (ISID). A Session ID is like a ChatGPT session where all the context is available to the agent. Starting a new session returns an `isid` and the `get_session` action requires an `isid`.

Common tips:

* Specify only the subset of tools you want your AI to use, otherwise it may do things you didn't expect or take initiative in ways you don't intend.
* Make the AI as specialized as possible, tell it exactly what you want it to do, processes and how you want to get the response (markdown, JSON etc).
* Give the AI examples, adding more details and examples to the `instructions` help greatly.

The credentials provided to the engine are simply a LimaCharlie API key, we recommend storing it in a [secret](../../../7-administration/config-hive/secrets.md) and referencing as `hive://secret/my-lc-creds`.

### Actions

#### start_session

Start a new AI Agent session, specifying all the detailed parameters (see AI Agent Structure below that are both the Agent Definition parameters and the `start_session` parameters).

#### list_tools

List all the tools available to be called by the agent along with their categories that can be used to customize agents.

### D&R rule example

Here is an example D&R rule starting a new invocation of a playbook.

```
- action: extension request
  extension name: ext-ai-agent-engine
  extension action: start_session
  extension request:
    agent_definition: '{{ "my-agent-name" }}'
    message: You're a cyber security expert, summarize this detection: {...}
```

### Python example

```
# Import LC SDK
import limacharlie
import json
# Instantiate the SDK with default creds.
lc = limacharlie.Manager()
# Instantiate the Extension manager object.
ext = limacharlie.Extension(lc)

# Issue a request to the "ext-ai-agent-engine" extension for the "my-agent-name" agent.
response = ext.request("ext-ai-agent-engine", "start_session", {
    "agent_definition": "my-agent-name",
    "message": "You're a cyber security expert, summarize this detection: {...}"
})

for msg in response['data']['responses']:
  print(f"AI says: {json.dumps(msg, indent=2)}")
```

## AI Agent structure

#### Example AI Agent Definition

The following is a sample AI Agent definition that simply aims at summarizing detections.

```
{
  "name": "my-agent",
  "description": "Some agent that does something...",
  "credentials": "hive://secret/ai-creds", // These credentials will be used when accessing LimaCharlie APIs.
  // Instructions are the core system behavior for the AI
  "instructions": "You are a cybersecurity expert system who's job it is to summarize detections/alerts for SOC analysts. Output as markdown. Include detailed technical context about the alert and if MITRE techniques are mentioned, summarize them. Also include what next steps of the investigation should be. The audience of the report is a cyber security team at a medium sized enterprise.",
  "max_iterations": 10, // If the AI makes tool calls to the LC API or LC Sensors, this limits the number of iterations the AI is called.
  "allowed_tools": [
    "get_sensor_info" // List of tool categories (see list_tools or the Available Tools section below).
  ]
}
```

### Available Tools

The tools available to the AI Agents are the same ones available from the official [LimaCharlie MCP Server](../../../6-developer-guide/mcp-server.md).

## Infrastructure as Code

Not currently available, coming up.

## Billing

The AI Agent Engine is billed per token processed, including initial messages, prompt and response.

## Privacy

Currently, the model in use is the commercial Gemini models.

Although the models may change (and eventually Bring-Your-Own-Model), these models will never use your data to train more models and LimaCharlie never uses the data to train models.
