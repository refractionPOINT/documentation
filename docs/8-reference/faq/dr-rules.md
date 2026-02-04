# FAQ - Detect and Respond Rules

## Is there an method for base64 decoding and inspection within Detect & Respond rules?

Base64 decoding is not currently supported directly within D&R rules.

You can have your D&R rule detect base64 content and send it as an action to a Python playbook, where you can perform the necessary decoding and analysis.

Why isn't this feature available? Base64 decoding in security contexts is rarely straightforward - it typically involves:
- Extracting substrings rather than decoding entire fields
- Handling special alphabets and custom encoding schemes
- Managing different starting offsets

While a basic full-field decoding parameter could potentially be added to operators, the complexity and variety of real-world base64 usage patterns make this a challenging feature to implement
generically.

