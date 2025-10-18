---
title: Testing Outputs
slug: testing-outputs
breadcrumb: Outputs
source: https://docs.limacharlie.io/docs/testing-outputs
articleId: d7d3b269-137a-4d11-a3ee-0201c7a2da1c
---

* * *

Testing Outputs

  *  __05 Oct 2024
  *  __ 1 Minute to read 



Share this __

  * __ Print

  *  __ Share

  *  __ Dark

 __ Light




 __Contents

# Testing Outputs

  *  __Updated on 05 Oct 2024
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

The easiest way to test if the outputs are configured correctly is to set the stream to `Audit` which will send auditing events about activity around the management of the platform in the cloud. You can then edit the same output or make any other change on the platform, which will trigger an audit event to be sent.

After you have confirmed that the output configurations works, you can switch the data stream from `Audit` to the one you are looking to use.

If you are running into an error configuring an output, the error details will be listed in the Platform Logs section under Errors, with the key that looks like `outputs/OUTPUT_NAME`.

If an output fails, it gets disabled temporarily to avoid spam. It will be re-enabled automatically after a while, or you can force it to be re-enabled by updating the configuration.

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

###### Related articles

  * [ Template Strings and Transforms ](/docs/template-strings-and-transforms)



* * *

###### What's Next

  * [ Template Strings and Transforms ](/docs/template-strings-and-transforms-3) __



Tags

  * [ outputs ](/docs/en/tags/outputs)


