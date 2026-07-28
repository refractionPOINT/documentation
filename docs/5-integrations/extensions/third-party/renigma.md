# REnigma

## About REnigma

[REnigma](https://dtrsec.com/) is a malware analysis platform that uses Record and Replay technology. REnigma records each state change in a virtual machine during live execution. Analysts can then replay and analyze the behavior of the malware offline, down to the instruction level. This method removes the risk of evasion and captures all malicious activity. For SOC teams that triage alerts, and for incident responders, REnigma gives fast detonation, precise analysis, and extraction of artifacts. Its API integrations also automate investigation workflows.

## About the Extension

The LimaCharlie Extension for REnigma connects to the REnigma API. It analyzes suspicious URLs or files that the LimaCharlie BinLib or Artifact Extensions collect. When a file or URL triggers an alert in LimaCharlie, preconfigured Detection & Response () rules can queue the item for investigation in REnigma.

These D&R rules send the artifact or URL directly to REnigma. REnigma records and analyzes the item in a controlled virtual machine. Analysts can then see the execution data, the artifacts, and the network patterns that the Record and Replay technology captured. This workflow shortens the triage process. It also gives deep information about possible threats without manual work at each step.

## Configuration

To use the REnigma extension, you need your REnigma URL and API key. [Contact the REnigma team for access](https://dtrsec.com/contact.html).

![Configuration To use the REnigma extension, you will need your REnigma URL and API key](../../../assets/images/image(284).png)

## Using the Extension

You can submit a file or URL to the REnigma extension for processing in one of 2 ways:

1. With the LimaCharlie web app:

   1. Submit the ID of the artifact that you want REnigma to process. A series of D&R rules uploads and processes the artifact. The output shows in the `ext-renigma` sensor timeline.![You can submit a file or URL to the REnigma extension for processing in one of 2 ways: 1](../../../assets/images/image(297).png)
   2. Submit the URL that you want REnigma to analyze. A series of D&R rules sends and processes the URL. The output shows in the `ext-renigma` sensor timeline.![You can submit a file or URL to the REnigma extension for processing in one of 2 ways: 1](../../../assets/images/image(296).png)
2. With D&R rules:

   1. Detect:

      ```yaml
      event: ingest
      op: exists
      path: /
      target: artifact_event
      artifact type: ext-binlib-bin
      ```

   2. Respond

      ```yaml
      - action: "extension request"
        extension name: "ext-renigma"
        extension action: "upload_file"
        extension request:
            file_id: '{{ .routing.log_id }}'
            disable_internet: false
      ```

LimaCharlie Extensions let users expand and customize their security environments. Extensions integrate third-party tools, automate workflows, and add new capabilities. Organizations subscribe to Extensions and give them specific permissions to interact with their infrastructure. An Extension can be private or public, for one organization or for the community. This framework supports scale, flexibility, and secure, repeatable deployments.

## Related Articles

- [BinLib](../limacharlie/binlib.md)
- [Artifacts](../limacharlie/artifact.md)
- [Using Extensions](../using-extensions.md)
- [Secure Annex](secureannex.md)
