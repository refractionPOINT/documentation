---
title: SCP
slug: outputs-destinations-scp
breadcrumb: Outputs > Output Destinations
source: https://docs.limacharlie.io/docs/outputs-destinations-scp
articleId: c62bf281-b3f2-4c02-8d8f-87de3e2c3edd
---

* * *

SCP

  *  __05 Oct 2024
  *  __ 1 Minute to read 



Share this __

  * __ Print

  *  __ Share

  *  __ Dark

 __ Light




 __Contents

# SCP

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

Output events and detections over SCP (SSH file transfer).

  * `dest_host`: the ip:port where to send the data to, like `1.2.3.4:22`.

  * `dir`: the directory where to output the files on the remote host.

  * `username`: the SSH username to log in with.

  * `password`: optional password to use to login with.

  * `secret_key`: the optional SSH private key to authenticate with.




Example:
    
    
    dest_host: storage.corp.com
    dir: /uploads/
    username: storage_user
    password: XXXXXXXXXXXX
    

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

  * [ SFTP ](/docs/outputs-destinations-sftp) __



Tags

  * [ outputs ](/docs/en/tags/outputs)


