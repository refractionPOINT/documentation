# Using Custom Billing Plans

> Applicability
>
> This page applies only to Organizations with a contracted custom billing plan.

If your organization has a custom pricing plan, obey these steps. The steps make sure that the plan applies when you create your organization. You must know the exact plan ID for your organization. If you do not know the details of your plan, or if you need help, contact LimaCharlie.

To apply your custom billing plan to a new organization:

- Web UI: When you create your organization, select your assigned plan in the drop-down menu.
- API Users: With the API, give your plan in the correct `loc` parameter.
- REST API: Use the `loc` parameter (general location). For a custom plan, give the exact plan ID. [API Documentation](https://api.limacharlie.io/static/swagger/#/Organizations/requestCreateOrg)
- Python SDK: Use the `location` parameter for the same purpose. [Python SDK Reference](https://github.com/refractionPOINT/python-limacharlie/blob/master/limacharlie/Manager.py#L1197)

Note: If you do not give your custom plan when you create the organization, you get standard pricing. You do not get the discounted pricing.
