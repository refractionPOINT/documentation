---
title: GreyNoise
slug: api-integrations-greynoise
breadcrumb: Add-Ons > API Integrations
source: https://docs.limacharlie.io/docs/api-integrations-greynoise
articleId: d0992720-135c-4803-a584-099a7f5ad707
---

* * *

GreyNoise

  *  __05 Oct 2024
  *  __ 1 Minute to read 



Share this __

  * __ Print

  *  __ Share

  *  __ Dark

 __ Light




 __Contents

# GreyNoise

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

GreyNoise collects, analyzes, and labels data on IP addresses that scan the Internet and often saturate security tools with noise. By querying IP addresses against GreyNoise, teams can spend less time on irrelevant or harmless activity and focus on targeted and/or emerging threats.

LimaCharlie offers integrations with two GreyNoise API lookups:

  * [IP Context](https://docs.greynoise.io/reference/noisecontextip-1)

    * Get more information about a given IP address. Returns time ranges, IP metadata (network owner, ASN, reverse DNS pointer, country), associated actors, activity tags, and raw port scan and web request information.

  * [RIOT IP Lookups](https://docs.greynoise.io/reference/riotip)

    * RIOT identifies IPs from known benign services and organizations that commonly cause false positives in network security and threat intelligence products. The collection of IPs in RIOT is continually curated and verified to provide accurate results.




## IP Context
    
    
    {
      "api_greynoise-noise-context": {
        "ip": "35.184.178.65",
        "seen": false
      }
    }
    

## RIOT IP Lookup
    
    
    {
      "ip": "8.8.8.8",
      "noise": false,
      "riot": true,
      "classification": "benign",
      "name": "Google Public DNS",
      "link": "https://viz.greynoise.io/riot/8.8.8.8",
      "last_seen": "2023-08-02",
      "message": "Success"
    }
    

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

  * [ Hybrid Analysis ](/docs/api-integrations-hybrid-analysis) __



Table of contents

    * IP Context 
    * RIOT IP Lookup 



Tags

  * [ add-ons ](/docs/en/tags/add-ons)


