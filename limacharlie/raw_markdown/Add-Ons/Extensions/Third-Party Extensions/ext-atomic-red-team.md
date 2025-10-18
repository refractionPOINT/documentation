---
title: Atomic Red Team
slug: ext-atomic-red-team
breadcrumb: Add-Ons > Extensions > Third-Party Extensions
source: https://docs.limacharlie.io/docs/ext-atomic-red-team
articleId: 03a32aa9-365d-4f75-afc9-563a16c8e2f2
---

* * *

Atomic Red Team

  *  __10 Oct 2025
  *  __ 3 Minutes to read 



Share this __

  * __ Print

  *  __ Share

  *  __ Dark

 __ Light




 __Contents

# Atomic Red Team

  *  __Updated on 10 Oct 2025
  *  __ 3 Minutes to read 



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

**Atomic Red Team** is a library of tests mapped to the MITRE ATT&CK framework, provided by Red Canary. With this Extension, LimaCharlie users can use Atomic Red Team to quickly, portably, and reproducibly test their environments.

Find more information about it [here](https://atomicredteam.io/).

New Atomic Red Team Extension

Please note that the Atomic Red Team **Extension** has replaced the Atomic Red Team **Service**. Ensure that your Organization disabled/removes the Service and subscribes to the Extension. This documentation applies to the Atomic Red Team extension.

## Enabling the Atomic Red Team Extension

Enabling Atomic Red Team can be done within the LimaCharlie **Marketplace** , or at [this link](https://beta.app.limacharlie.io/add-ons/extension-detail/ext-atomic-red-team).

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/atomic-1.png)

Under the Organization dropdown, select a tenant (organization) you want to subscribe to Atomic Red Team and click subscribe.

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/atomic-2.png)

Please note that Extensions are applied on the per-tenant basis. If you have multiple organizations you want to subscribe to Atomic Red Team, you will need to subscribe each organization to the extension separately.

You can also manage add-ons from the **Subscriptions** menu under **Billing**.

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/atomic-3.png)

Tenants that have been subscribed to the extension, will be marked with a green check mark in the **Organization** dropdown.

## Running Atomic Red Team test(s)

After Atomic Red Team has been enabled for your organization, the **Atomic Red Team** option will be available under the **Extensions** menu in the web UI. Selecting this Extension will render the Atomic Red Team test selection menu.

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/atomic-4.png)

Sensor Eligibility for Atomic Red Team tests

Currently, LimaCharlie supports Atomic Red Team tests on Sensors installed on Windows operating systems. Furthermore, sensors must be online in order for tests to run.

Within the Atomic Red Team menu, you can select a **Sensor** to run test(s) against. Furthermore, you can also pre-select a set of tests from the full Atomic Red Team suite.

System Changes

Running Atomic Red Team tests will likely modify some system configurations. LimaCharlie attempts to revert any configuration changes performed, but the core logic is handled by the Atomic Red Team project. The following actions may occur:

  * Modify PowerShell scripting permissions

  * Modify PowerShell script execution policies

  * Check/Modify Microsoft Defender status

  * Install dependencies like Nuget

  * Install Atomic Red Team technique-specific dependencies

  * Technique-specific configuration changes




The list of available tests is updated every time the window is open, ensuring that you are getting all available options from the Atomic Red Team repository.

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/atomic-5.png)

Select your test(s) of choice, and click 'Run Tests'. You will receive a dialog box with a job id that is associated with this particular run of test(s).

## Checking Atomic Red Team Results

When the Atomic Red Team extension is enabled, you will see an Adapter named `ext-atomic-red-team`.

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/atomic-6.png)

This Adapter corresponds to all Atomic Red Team activity, including jobs run and results returned. As a separate adapter, this also means that Atomic Red Team tests are actionable events. For example, you could construct a  rule based on Atomic Red Team test results or feedback from system telemetry.

Viewing the **Timeline** within the `ext-atomic-red-team` adapter will display the test(s) run and associated results, if available.

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/atomic-7.png)

Note that results are easily distinguished via a `result <MITRE ATT&CK ID>` event name, allowing for easy filtering and analysis.

Within the **Timeline** of the _system on which you ran a test_ , you will also find `RECEIPT` event(s) that contain more details about executed tests. For example, the following output shows data related to a test for ATT&CK ID T1053.

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/atomic-8.png)

Between `RECEIPT` events and output in the `ext-atomic-red-team` adapter, you can correlate and identify successful and failed Atomic Red Team tests.

LimaCharlie Extensions allow users to expand and customize their security environments by integrating third-party tools, automating workflows, and adding new capabilities. Organizations subscribe to Extensions, which are granted specific permissions to interact with their infrastructure. Extensions can be private or public, enabling tailored use or broader community sharing. This framework supports scalability, flexibility, and secure, repeatable deployments.

In LimaCharlie, an Organization represents a tenant within the SecOps Cloud Platform, providing a self-contained environment to manage security data, configurations, and assets independently. Each Organization has its own sensors, detection rules, data sources, and outputs, offering complete control over security operations. This structure enables flexible, multi-tenant setups, ideal for managed security providers or enterprises managing multiple departments or clients.

LimaCharlie Extensions allow users to expand and customize their security environments by integrating third-party tools, automating workflows, and adding new capabilities. Organizations subscribe to Extensions, which are granted specific permissions to interact with their infrastructure. Extensions can be private or public, enabling tailored use or broader community sharing. This framework supports scalability, flexibility, and secure, repeatable deployments.

Similar to agents, Sensors send telemetry to the LimaCharlie platform in the form of EDR telemetry or forwarded logs. Sensors are offered as a scalable, serverless solution for securely connecting endpoints of an organization to the cloud.

Adapters serve as flexible data ingestion mechanisms for both on-premise and cloud environments. 

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

  * [ Govee ](/docs/ext-govee) __



Table of contents

    * Enabling the Atomic Red Team Extension 
    * Running Atomic Red Team test(s) 
    * Checking Atomic Red Team Results 



Tags

  * [ add-ons ](/docs/en/tags/add-ons)
  * [ extensions ](/docs/en/tags/extensions)


