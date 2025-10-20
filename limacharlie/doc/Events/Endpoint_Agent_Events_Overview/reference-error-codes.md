# Reference: Error Codes

The follow error codes are found within various Report (`*_REP`) events found within the [EDR Events](./reference-edr-events.md), often in response to an [endpoint agent command](../../Sensors/Endpoint_Agent/Endpoint_Agent_Commands/reference-endpoint-agent-commands.md).

| Error Code | Value |
| --- | --- |
| ERROR\_SUCCESS | 0, 200 |
| ERROR\_INVALID\_FUNCTION | 1 |
| ERROR\_FILE\_NOT\_FOUND | 2 |
| ERROR\_PATH\_NOT\_FOUND | 3 |
| ERROR\_ACCESS\_DENIED | 5 |
| ERROR\_INVALID\_HANDLE | 6 |
| ERROR\_NOT\_ENOUGH\_MEMORY | 8 |
| ERROR\_INVALID\_DRIVE | 15 |
| ERROR\_CURRENT\_DIRECTORY | 16 |
| ERROR\_WRITE\_PROTECT | 19 |
| ERROR\_CRC | 23 |
| ERROR\_SEEK | 25 |
| ERROR\_WRITE\_FAULT | 29 |
| ERROR\_READ\_FAULT | 30 |
| ERROR\_SHARING\_VIOLATION | 32 |
| ERROR\_LOCK\_VIOLATION | 33 |
| ERROR\_HANDLE\_EOF | 38 |
| ERROR\_HANDLE\_DISK\_FULL | 39 |
| ERROR\_NOT\_SUPPORTED | 50 |
| ERROR\_BAD\_NETPATH | 53 |
| ERROR\_NETWORK\_BUSY | 54 |
| ERROR\_NETWORK\_ACCESS\_DENIED | 65 |
| ERROR\_BAD\_NET\_NAME | 67 |
| ERROR\_FILE\_EXISTS | 80 |
| ERROR\_INVALID\_PASSWORD | 86 |
| ERROR\_INVALID\_PARAMETER | 87 |
| ERROR\_BROKEN\_PIPE | 109 |
| ERROR\_OPEN\_FAILED | 110 |
| ERROR\_BUFFER\_OVERFLOW | 111 |
| ERROR\_DISK\_FULL | 112 |
| ERROR\_INVALID\_NAME | 123 |
| ERROR\_NEGATIVE\_SEEK | 131 |
| ERROR\_DIR\_NOT\_EMPTY | 145 |
| ERROR\_BUSY | 170 |
| ERROR\_BAD\_EXE\_FORMAT | 193 |
| ERROR\_FILENAME\_EXCED\_RANGE | 206 |
| ERROR\_FILE\_TOO\_LARGE | 223 |
| ERROR\_DIRECTORY | 267 |
| ERROR\_INVALID\_ADDRESS | 487 |
| ERROR\_TIMEOUT | 1460 |

## Payload Specific

When dealing with Payloads or Artifact collection, you may receive HTTP specific error codes:
<https://developer.mozilla.org/en-US/docs/Web/HTTP/Status>

## Yara Specific

When doing Yara scanning operations, you may receive Yara specific error codes.

These are documented here:
<https://github.com/VirusTotal/yara/blob/master/libyara/include/yara/error.h>
