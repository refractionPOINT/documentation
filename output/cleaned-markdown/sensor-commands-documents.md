# Documents

## doc_cache_get

Retrieve a document / file that was cached on the sensor.

**Platforms:** (All platforms)

**Response Event:** [GET_DOCUMENT_REP](/v1/docs/reference-events-responses-documents)

This command is currently limited to the following document types:

* .bat
* .js
* .ps1
* .sh
* .py
* .exe
* .scr
* .pdf
* .doc
* .docm
* .docx
* .ppt
* .pptm
* .pptx
* .xlt
* .xlsm
* .xlsx
* .vbs
* .rtf
* .hta
* .lnk
* Any files created in `system32` on Windows.

**Usage:**

```
usage: doc_cache_get [-h] [-f FILE_PATTERN] [-s HASHSTR]

optional arguments:
  -f FILE_PATTERN, --file_pattern FILE_PATTERN
                        a pattern to match on the file path and name of the
                        document, simple wildcards ? and * are supported
  -s HASHSTR, --hash HASHSTR
                        hash of the document to get
```