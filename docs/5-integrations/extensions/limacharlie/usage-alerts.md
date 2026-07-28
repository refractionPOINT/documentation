# Usage Alerts

The usage alerts Extension lets you create, maintain, and refresh conditions for usage alerts in an Organization automatically.

For example, you can create a usage alert rule that fires a detection when artifact downloads reach a 1GB threshold in the last 30 days (43200 minutes). LimaCharlie saves this alert as a managed rule. When the usage reaches the threshold, LimaCharlie creates a detection with this `cat`:

`Usage alert - Output data over threshold - 1024 MB in 30.00 days`

You can manage these alert rules across tenants with the Infrastructure as Code extension.

Every hour, LimaCharlie syncs all the usage alert rules in the configuration. To sync them manually, click the `Sync Usage Alert Rules` button on the extension page. When you add a usage alert rule, LimaCharlie does **not** sync it immediately, unless you click `Sync Usage Alert Rules`.

**NOTE**: The maximum timeframe is 43200 minutes (30 days).

## Usage - GUI

To define a new usage alert:

1. Click the `Add New Usage Alert` button on the extension page.
2. Give the alert a name, for example `Output data over threshold`.
3. Select a SKU, in this example `output_data`.
4. Select a timeframe and a limit.
5. Click `Save`.

    ![image(275).png "image(275).png"](../../../assets/images/image(275).png "image(275).png")

To add the rule immediately, click the `Sync Usage Alert Rules` button. If you do not, LimaCharlie pushes the rule automatically at the next hour interval.

![image(278).png "image(278).png"](../../../assets/images/image(278).png "image(278).png")

This creates a managed D&R rule in the `dr-managed` hive in the cloud. The rule syncs automatically every hour.

```yaml
hives:
    dr-managed:
        Output data over threshold:
            data:
                detect:
                    event: billing_record
                    op: and
                    rules:
                        - op: is
                          path: event/record/cat
                          value: output
                        - op: is
                          path: event/record/k
                          value: bytes_tx
                    target: billing
                respond:
                    - action: report
                      name: Usage alert - Output data over threshold - 1024 MB in 24.00 hours
                      suppression:
                        count_path: event/record/v
                        keys:
                            - output
                            - bytes_tx
                            - ext-usage-alerts
                            - Output data over threshold
                        max_count: 1.073741824e+09
                        min_count: 1.073741824e+09
                        period: 43200m
```

## Usage - Infrastructure as Code

If you manage your organizations with infrastructure as code, you can also configure these rules in the `extension_config` hive.

```yaml
hives:
    extension_config:
        ext-usage-alerts:
            data:
                usage_alert_rules:
                    - enabled: true
                      limit: 1024
                      name: Output data over threshold
                      sku: output_data
                      timeframe: 43200
            usr_mtd:
                enabled: true
                expiry: 0
                tags: []
                comment: ""
```
