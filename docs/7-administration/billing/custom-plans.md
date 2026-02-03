# Using Custom Billing Plans

> Applicability
>
> This page only applies to Organizations with a contracted custom billing plan.

If your organization has a custom pricing plan, follow these steps to ensure it's correctly applied when creating your organization. You will need to know the exact plan ID that's been allocated for your organization. If you're unsure about your plan details or need assistance, please reach out.

How to apply your custom billing plan to newly created organizations:

* Web UI: When creating your organization, select your assigned plan from the drop-down menu.
* API Users: If using the API, specify your plan using the appropriate `loc` parameter.
* REST API: Use the `loc` parameter (general location). If you need to specify a custom plan, provide the exact plan ID. [API Documentation](https://api.limacharlie.io/static/swagger/#/Organizations/requestCreateOrg)
* Python SDK: Use the `location` parameter for the same purpose. [Python SDK Reference](https://github.com/refractionPOINT/python-limacharlie/blob/master/limacharlie/Manager.py#L1197)

Note: If you do not specify your custom plan at the time your organization is created, you will be put on standard pricing and will not receive discounted pricing.
