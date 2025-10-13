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

The tools available to the AI Agents are the same ones available from the official [LimaCharlie MCP Server](/v2/docs/mcp-server).

## Infrastructure as Code

Not currently available, coming up.

## Billing

The AI Agent Engine is billed per token processed, including initial messages, prompt and response.

## Privacy

Currently, the model in use is the commercial Gemini models.

Although the models may change (and eventually Bring-Your-Own-Model), these models will never use your data to train more models and LimaCharlie never uses the data to train models.

LimaCharlie Extensions allow users to expand and customize their security environments by integrating third-party tools, automating workflows, and adding new capabilities. Organizations subscribe to Extensions, which are granted specific permissions to interact with their infrastructure. Extensions can be private or public, enabling tailored use or broader community sharing. This framework supports scalability, flexibility, and secure, repeatable deployments.

In LimaCharlie, an Organization represents a tenant within the SecOps Cloud Platform, providing a self-contained environment to manage security data, configurations, and assets independently. Each Organization has its own sensors, detection rules, data sources, and outputs, offering complete control over security operations. This structure enables flexible, multi-tenant setups, ideal for managed security providers or enterprises managing multiple departments or clients.

Infrastructure as Code (IaC) automates the management and provisioning of IT infrastructure using code, making it easier to scale, maintain, and deploy resources consistently. In LimaCharlie, IaC allows security teams to deploy and manage sensors, rules, and other security infrastructure programmatically, ensuring streamlined, repeatable configurations and faster response times, while maintaining infrastructure-as-code best practices in cybersecurity operations.

LimaCharlie Extensions allow users to expand and customize their security environments by integrating third-party tools, automating workflows, and adding new capabilities. Organizations subscribe to Extensions, which are granted specific permissions to interact with their infrastructure. Extensions can be private or public, enabling tailored use or broader community sharing. This framework supports scalability, flexibility, and secure, repeatable deployments.

Command-line Interface