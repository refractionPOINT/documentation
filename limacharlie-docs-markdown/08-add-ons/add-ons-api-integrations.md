# API Integrations
## Mechanics

Functionally, API-based lookups operate exactly the same as using the normal `lookup` [operator](/v2/docs/detection-logic-operators#lookup), with one addition: `metadata_rules`. The rule will pass a value to the lookup, wait for a response, and then evaluate the response using `metadata_rules`.

The operators within `metadata_rules` are evaluated exactly the same as any other rule, except they additionally evaluate the lookup's response. The response actions will only run if the `metadata_rules` criteria are met.

## Configuration

When subscribed, API keys can be managed within the `Integrations` menu, available under `Organization Settings` in the web app:

![image.png](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/image%28116%29.png)

Users who wish to view and/or edit API keys will need to have the following permissions:

* `org.conf.get`
* `org.conf.set`

## Available Lookups

LimaCharlie offers multiple API lookups for telemetry and [D&R rule](/v2/docs/detection-and-response) enrichment, allowing you to make higher fidelity detections that rely on API-based metadata. The list of available API-based integrations are under this page in the left-side navigation menu. Don't see an integration that you want? [Let us know!](https://www.limacharlie.io/contact)