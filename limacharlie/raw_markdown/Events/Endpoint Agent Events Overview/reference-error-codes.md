# Reference: Error Codes

The follow error codes are found within various Report (`*_REP`) events found within the [EDR Events](reference-edr-events.md), often in response to an [endpoint agent command](../../Sensors/Endpoint%20Agent/Endpoint%20Agent%20Commands/reference-endpoint-agent-commands.md).

Error Code| Value  
---|---  
ERROR_SUCCESS| 0, 200  
ERROR_INVALID_FUNCTION| 1  
ERROR_FILE_NOT_FOUND| 2  
ERROR_PATH_NOT_FOUND| 3  
ERROR_ACCESS_DENIED| 5  
ERROR_INVALID_HANDLE| 6  
ERROR_NOT_ENOUGH_MEMORY| 8  
ERROR_INVALID_DRIVE| 15  
ERROR_CURRENT_DIRECTORY| 16  
ERROR_WRITE_PROTECT| 19  
ERROR_CRC| 23  
ERROR_SEEK| 25  
ERROR_WRITE_FAULT| 29  
ERROR_READ_FAULT| 30  
ERROR_SHARING_VIOLATION| 32  
ERROR_LOCK_VIOLATION| 33  
ERROR_HANDLE_EOF| 38  
ERROR_HANDLE_DISK_FULL| 39  
ERROR_NOT_SUPPORTED| 50  
ERROR_BAD_NETPATH| 53  
ERROR_NETWORK_BUSY| 54  
ERROR_NETWORK_ACCESS_DENIED| 65  
ERROR_BAD_NET_NAME| 67  
ERROR_FILE_EXISTS| 80  
ERROR_INVALID_PASSWORD| 86  
ERROR_INVALID_PARAMETER| 87  
ERROR_BROKEN_PIPE| 109  
ERROR_OPEN_FAILED| 110  
ERROR_BUFFER_OVERFLOW| 111  
ERROR_DISK_FULL| 112  
ERROR_INVALID_NAME| 123  
ERROR_NEGATIVE_SEEK| 131  
ERROR_DIR_NOT_EMPTY| 145  
ERROR_BUSY| 170  
ERROR_BAD_EXE_FORMAT| 193  
ERROR_FILENAME_EXCED_RANGE| 206  
ERROR_FILE_TOO_LARGE| 223  
ERROR_DIRECTORY| 267  
ERROR_INVALID_ADDRESS| 487  
ERROR_TIMEOUT| 1460  
  
## Payload Specific

When dealing with Payloads or Artifact collection, you may receive HTTP specific error codes:  
<https://developer.mozilla.org/en-US/docs/Web/HTTP/Status>

## Yara Specific

When doing Yara scanning operations, you may receive Yara specific error codes.

These are documented here:  
<https://github.com/VirusTotal/yara/blob/master/libyara/include/yara/error.h>

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

  * [ Endpoint Agent Commands ](/docs/endpoint-agent-commands)
  * [ Endpoint Agent Events Overview ](/docs/endpoint-agent-events-overview)
  * [ Reference: Endpoint Agent Commands ](/docs/reference-endpoint-agent-commands)
  * [ Reference: EDR Events ](/docs/reference-edr-events)



* * *

###### What's Next

  * [ Template Strings and Transforms ](/docs/template-strings-and-transforms) __
