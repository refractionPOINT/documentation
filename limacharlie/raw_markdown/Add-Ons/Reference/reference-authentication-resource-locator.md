---
title: Reference: Authenticated Resource Locator
slug: reference-authentication-resource-locator
breadcrumb: Add-Ons > Reference
source: https://docs.limacharlie.io/docs/reference-authentication-resource-locator
articleId: 2048ccb2-d7a4-47d3-b7c9-25745bd18f92
---

* * *

Reference: Authenticated Resource Locator

  *  __06 Jan 2025
  *  __ 1 Minute to read 



Share this __

  * __ Print

  *  __ Share

  *  __ Dark

 __ Light




 __Contents

# Reference: Authenticated Resource Locator

  *  __Updated on 06 Jan 2025
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

## Overview

Many features in LimaCharlie require access to external resources, sometimes authenticated, provided by users.

Authenticated Resource Locators (ARLs) describe a way to specify access to a remote resource, supporting many methods, including authentication data, and all that within a single string.

## Format

### With authentication
    
    
    [methodName,methodDest,authType,authData]
    

### Without authentication
    
    
    [methodName,methodDest]
    

  * `methodName`: the transport to use, one of `http`, `https`, `gcs` and `github`.

  * `methodDest`: the actual destination of the transport. A domain and path for HTTP(S) and a bucket name and path for GCS.

  * `authType`: how to authenticate, one of `basic`, `bearer`, `token`, `gaia` or `otx`.

  * `authData`: the auth data, like `username:password` for `basic`, or access token values. If the value is a complex structure, like a `gaia` JSON service key, it must be base64-encoded.




## Examples

### HTTP GET with no auth

`[https,my.corpwebsite.com/resourdata]`

### HTTP GET with basic auth

`[https,my.corpwebsite.com/resourdata,basic,myusername:mypassword]`

### HTTP GET with bearer auth

`[https,my.corpwebsite.com/resourdata,bearer,bfuihferhf8erh7ubhfey7g3y4bfurbfhrb]`

### HTTP GET with token auth

`[https,my.corpwebsite.com/resourdata,token,bfuihferhf8erh7ubhfey7g3y4bfurbfhrb]`

### Retrieve from Google Cloud Storage

`[gcs,my-bucket-name/some-blob-prefix,gaia,base64(GCP_SERVICE_KEY)]`

### Retrieve OTX Pulse via REST API

`[https,otx.alienvault.com/api/v1/pulses/5dc56c60a9edbde72dd5d013,otx,9uhr438uhf4h4u9fj7f6the8h383v8jv4ccc1e263d37f29d034d]`

### Retrieve from public GitHub repo main branch

`[github,myGithubUserOrOrg/repoName/path/to/file]`

**Note:** The path to the repo is NOT the same as the URL. Utilize the UI breadcrumbs for the correct path.  
For example, in the following screenshot:

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/image-1734104784118.png)

The GitHub user is: _romainmarcoux_  
The repo name is: _malicious-domains_  
The path is: _sources/alienvault-phishing-scam_  
So the ARL would be: `[github,romainmarcoux/malicious-domains/sources/alienvault-phishing-scam]`

### Retrieve from GitHub repo with Github Personal Access Token

`[github,myGithubUserOrOrg/repoName/optional/subpath/to,token,f1eb898f20a0db07e88878aadfsdfdfsffdsdfadwq8f767a72218f2]`

### Retrieve from public GitHub repo at a specific branch

`[github,refractionPOINT/sigma/some-sub-dir?ref=my-branch]`

This is here for testing [purposes](/v2/docs/i-dont-exist). 

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

  * [ VirusTotal Integration ](/docs/tutorials-integratons-virustotal-integration) __



Table of contents

    * Overview 
    * Format 
    * Examples 



Tags

  * [ add-ons ](/docs/en/tags/add-ons)
  * [ reference ](/docs/en/tags/reference)


