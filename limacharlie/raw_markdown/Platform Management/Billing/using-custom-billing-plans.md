---
title: Using Custom Billing Plans
slug: using-custom-billing-plans
breadcrumb: Platform Management > Billing
source: https://docs.limacharlie.io/docs/using-custom-billing-plans
articleId: 14803f07-917a-4de2-8374-f879d09a36a8
---

* * *

Using Custom Billing Plans

  *  __10 Feb 2025
  *  __ 1 Minute to read 



Share this __

  * __ Print

  *  __ Share

  *  __ Dark

 __ Light




 __Contents

# Using Custom Billing Plans

  *  __Updated on 10 Feb 2025
  *  __ 1 Minute to read 



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

> Applicability
> 
> This page only applies to Organizations with a contracted custom billing plan.

If your organization has a custom pricing plan, follow these steps to ensure it’s correctly applied when creating your organization. You will need to know the exact plan ID that’s been allocated for your organization. If you’re unsure about your plan details or need assistance, please reach out.

How to apply your custom billing plan to newly created organizations:

  * Web UI: When creating your organization, select your assigned plan from the drop-down menu.

  * API Users: If using the API, specify your plan using the appropriate `loc` parameter.

  * REST API: Use the `loc` parameter (general location). If you need to specify a custom plan, provide the exact plan ID. [API Documentation](https://api.limacharlie.io/static/swagger/#/Organizations/requestCreateOrg)

  * Python SDK: Use the `location` parameter for the same purpose. [Python SDK Reference](https://github.com/refractionPOINT/python-limacharlie/blob/master/limacharlie/Manager.py#L1197)




Note: If you do not specify your custom plan at the time your organization is created, you will be put on standard pricing and will not receive discounted pricing.

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

  * [ Billing Options ](/docs/billing-options) __


