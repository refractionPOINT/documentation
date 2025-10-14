These documents are identical - they both describe the Govee Extension with the exact same content. I'll output a single synthesized version:

# Govee Extension

The Govee Extension allows you to trigger color changes on your [supported Govee lights](https://developer.govee.com/docs/support-product-model) via a rule response action. It requires you to configure a Govee API key in the extension.

## Setup

1. Request an API key from Govee by following their instructions [here](https://developer.govee.com/reference/apply-you-govee-api-key)
2. Get the Device ID (device) and model (sku) of the device you'd like to target by requesting a list of your supported devices from the Govee API:

```bash
curl --location 'https://openapi.api.govee.com/router/api/v1/user/devices' --header 'Govee-API-Key: YOUR_GOVEE_API_KEY'
```

3. Decide what RGB color(s) you want to use. By default, the extension will alert with red (`255,0,0`), and revert back to white (`255,255,255`) when the alert `duration` has ended.
4. Add your Govee API key to the extension configuration:
    ![Govee Extension Configuration](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/govee.png)

## Usage

When enabled, you may configure the response of a D&R rule to trigger a Govee event. Consider the following example response rule:

```yaml
- action: extension request
  extension action: run
  extension name: ext-govee
  extension request:
    device_id: '{{ "YOUR_GOVEE_DEVICE" }}'
    device_model: '{{ "YOUR_GOVEE_DEVICE_SKU" }}'
    alert_color: '{{ "255,0,0" }}'
    alert_brightness: '{{ "100" }}'
    revert_color: '{{ "255,255,255" }}'
    revert_brightness: '{{ "10" }}'
    duration: '{{ "30" }}'
  suppression:
    is_global: true
    keys:
      - Govee
    max_count: 1
    period: 1m
```

Note that the only required fields here are the `device_id` and `device_model`. Values supplied in the example are the defaults.

## Parameters

### Required Parameters

* `device_id`: Device ID returned via the Govee API (see example response below)
* `device_model`: Device model/SKU returned via the Govee API (see example response below)

### Optional Parameters

* `alert_color`: Color of the light when alert fires, in [RGB format](https://htmlcolorcodes.com/color-picker/), default `255,0,0` (red)
* `revert_color`: Color of the light to return to after alert fires, in [RGB format](https://htmlcolorcodes.com/color-picker/), default `255,255,255` (white)
* `alert_brightness`: Brightness of the light during alert, default `100`
* `revert_brightness`: Brightness of the light to return to after alert fires, default `10`
* `duration`: Duration of the alert in seconds (how long the light will remain at `alert_color` before returning to `revert_color`), default `30`

## Govee API Reference

### Sample Request

```bash
curl --location 'https://openapi.api.govee.com/router/api/v1/user/devices' --header 'Govee-API-Key: YOUR_GOVEE_API_KEY'
```

### Sample Response

```json
{
    "code": 200,
    "message": "success",
    "data": [
        {
            "sku": "H6008",                           # use in `device_model` parameter
            "device": "AA:BB:00:11:22:33:44:55",      # use in `device_id` parameter
            "deviceName": "DetectionLight",
            "type": "devices.types.light",
            "capabilities": [
                ...
            ]
        }
    ]
}
```