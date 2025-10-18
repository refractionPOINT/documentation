---
title: AI Agent Engine [LABS]
slug: ai-agent-engine
breadcrumb: Add-Ons > Extensions > LimaCharlie Labs
source: https://docs.limacharlie.io/docs/ai-agent-engine
articleId: 0937224e-77b8-4537-96a4-f2683dc3ff57
---

* * *

AI Agent Engine [LABS]

  * __18 Aug 2025
  *  __ 4 Minutes to read 



Share this __

  * __ Print

  *  __ Share

  *  __ Dark

 __ Light




 __Contents

# AI Agent Engine [LABS]

  * __Updated on 18 Aug 2025
  *  __ 4 Minutes to read 



  * __ Print

  *  __ Share

  *  __ Dark

 __ Light




* * *

Article summary

 __

Did you find this summary helpful? __ __ __ __

__

Thank you for your feedback!

> LimaCharlie LABS

The AI Agent Engine Extension allows you to easily codify and execute AI Agents within the context of your Organization with access to the LimaCharlie APIs for investigation, remediation and automation.

The AI Agent definition themselves are managed in the `ai_agent` [Hive](/v2/docs/config-hive) Configurations and can be managed across tenants using the Infrastructure as Code extension. This hive requires the `ai_agent.*` permissions.

The execution of an AI Agent can be triggered through the following means:

  1. Interactively in the web app by going to the Extensions section for the AI Agent Engine extension.

  2. By issuing an `extension request` action through a [D&R rule](/v2/docs/detection-and-response-examples).

  3. By issuing an extension request on the API directly: <https://api.limacharlie.io/static/swagger/#/Extensions/createExtensionRequest>

  4. By issuing an extension request through the Python CLI/SDK or Golang SDK, which means they’re also available to [Playbooks](/v2/docs/playbook).




This means agents can be invoked in a fully automated fashion based on events, detections, audit messages or any other [target](/v2/docs/detection-on-alternate-targets) of  rules. But it can also be used in an ad-hoc fashion triggered manually.

## Usage

When invoking an AI Agent, all you need is the playbook name as defined in Hive and an initial message. Optionally, an AI Agent can also receive a JSON dictionary object as parameters, this is useful when passing the AI Agent additional context like a detection or event from a D&R rule.

Interactions with the agent are associated with a given (Interactive) Session ID (ISID). A Session ID is like a ChatGPT session where all the context is available to the agent. Starting a new session returns an `isid` and the `get_session` action requires an `isid`.

Common tips:

  * Specify only the subset of tools you want your AI to use, otherwise it may do things you didn’t expect or take initiative in ways you don’t intend.

  * Make the AI as specialized as possible, tell it exactly what you want it to do, processes and how you want to get the response (markdown, JSON etc).

  * Give the AI examples, adding more details and examples to the `instructions` help greatly.




The credentials provided to the engine are simply a LimaCharlie API key, we recommend storing it in a [secret](/v2/docs/config-hive-secrets) and referencing as `hive://secret/my-lc-creds`.

### Actions

#### start_session

Start a new AI Agent session, specifying all the detailed parameters (see AI Agent Structure below that are both the Agent Definition parameters and the `start_session` parameters).

#### list_tools

List all the tools available to be called by the agent along with their categories that can be used to customize agents.

### D&R rule example

Here is an example D&R rule starting a new invocation of a playbook.
    
    
    - action: extension request
      extension name: ext-ai-agent-engine
      extension action: start_session
      extension request:
        agent_definition: '{{ "my-agent-name" }}'
        message: You're a cyber security expert, summarize this detection: {...}

### Python example
    
    
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

## AI Agent structure

#### Example AI Agent Definition

The following is a sample AI Agent definition that simply aims at summarizing detections.
    
    
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

* * *

Was this article helpful?

__Yes __No

 __

Thank you for your feedback! Our team will get back to you

How can we improve this article?

Your feedback

Need more information

Difficult to understand

Inaccurate or irrelevant content

Missing/broken link

Others

Comment

Comment (Optional)

Character limit : 500

Please enter your comment

Email (Optional)

Email

Notify me about change  


Please enter a valid email

Cancel

* * *

###### What's Next

  * [ Playbook [LABS] ](/docs/playbook) __



Table of contents

    * Usage 
    * AI Agent structure 
    * Infrastructure as Code 
    * Billing 
    * Privacy 


