# FAQ - Detect and Respond Rules

## Is there an method for base64 decoding and inspection within Detect & Respond rules?

D&R rules do not support base64 decoding directly.

Your D&R rule can detect base64 content and send it as an action to a Python playbook. The playbook then does the decoding and the analysis.

Base64 decoding in a security context is rarely simple. It usually includes:

- The extraction of substrings, instead of the decoding of complete fields
- Special alphabets and custom encoding schemes
- Different starting offsets

It is possible to add a basic parameter to operators that decodes a full field. But base64 is used in many different and complex ways, so a generic feature is difficult to build.
