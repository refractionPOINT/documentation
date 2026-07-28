# Secure Annex

[Secure Annex](https://secureannex.com/) is a security platform for browser extensions. It analyzes the Chrome extensions that are installed on the endpoints in your organization.

The Secure Annex LimaCharlie Extension queries the Secure Annex API with the IDs of the Chrome extensions on the endpoints in your organization. The query returns detailed information about the extensions. You can then do more analysis, or write rules that use the results.

API endpoints available for querying are:

- /manifest
- /extensions
- /vulnerabilities
- /signatures
- /urls
- /analysis

At this time, only Windows, macOS, and Chrome sensors support this.

## Setup

1. Sign up and get an API key at <https://app.secureannex.com/settings/api>
2. Subscribe to the Secure Annex extension in LimaCharlie - <https://app.limacharlie.io/add-ons/extension-detail/ext-secureannex>
3. Add the API key to the configuration of the Secure Annex extension in LimaCharlie

## Usage

### Manually in the GUI

To trigger an extension request manually, click the `Get extensions from endpoint` button in the web app. Then choose the sensor, or the sensors, to get extensions from. To choose many sensors, use a Sensor Selector. See [sensor selector expression examples](../../../8-reference/sensor-selector-expressions.md).

The reliable tasking extension collects the extensions from the endpoints. It adds `secureannex_extensions` to the investigation ID of the `RECEIPT` or `OS_PACKAGES_REP` event. This triggers an extension request that queries Secure Annex. The results are in the timeline of the `ext-secureannex` sensor.

### Automatically via D&R Rules

When you subscribe to the Secure Annex extension, LimaCharlie adds several D&R rules to your organization in a **disabled state**. These rules help you use the extension and automate your detections. The rules are:

- `ext-secureannex-detect-vulnerabilities`
  - This rule looks at the vulnerabilities and their severities in the `vulnerability` results. It creates detections for the high and critical vulnerabilities that it finds
- `ext-secureannex-detect-risk-rating`
  - This rule looks at the risks and their severities in the `manifest` results. It creates detections for the high and critical severities that it finds
- `ext-secureannex-get-extensions-windows`
  - This rule schedules a base64 encoded PowerShell script every 24 hours. The script queries Windows sensors for installed Chrome extensions and returns a list of the extension IDs and versions
  - The results have a `secureannex_extensions` investigation ID. LimaCharlie uses this ID to create Secure Annex extension requests that include the IDs and versions. The requests do a full analysis and return the results to the `ext-secureannex` sensor
- `ext-secureannex-get-extensions-mac`
  - This rule schedules a base64 encoded bash script every 24 hours. The script queries macOS sensors for installed Chrome extensions and returns a list of the extension IDs and versions
  - The results have a `secureannex_extensions` investigation ID. LimaCharlie uses this ID to create Secure Annex extension requests that include the IDs and versions. The requests do a full analysis and return the results to the `ext-secureannex` sensor
- `ext-secureannex-get-extensions-chrome`
  - This rule schedules the `OS_PACKAGES` command every 24 hours. The command queries Chrome sensors for installed Chrome extensions and returns a list of the extension IDs and versions
  - The results have an investigation ID. LimaCharlie uses this ID to create Secure Annex extension requests that include the IDs and versions. The requests do a full analysis and return the results to the `ext-secureannex` sensor

To use these rules, first enable them. To change a rule, copy its contents and create your own rule. The Secure Annex extension does not manage your own rules.

### Results

Results show in the live feed and the timeline of the `ext-secureannex` Sensor.
