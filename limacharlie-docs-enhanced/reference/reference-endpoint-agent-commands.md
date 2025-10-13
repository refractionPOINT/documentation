Contents x

* [Getting Started](what-is-limacharlie)
* [Sensors](installation-keys)
* [Events](event-schemas)
* [Query Console](query-console-ui)
* [Detection and Response](replay)
* [Platform Management](limacharlie-sdk)
* [Outputs](output-allowlisting)
* [Add-Ons](developer-grant-program)
* [Tutorials](reporting)
* [FAQ](faq-general)
* Release Notes
* [Connecting](mcp-server)

[Powered by![Document360](https://cdn.document360.io/static/images/document360-logo.svg)](https://document360.com/powered-by-document360/?utm_source=docs&utm_medium=footer&utm_campaign=poweredbylogo)

Reference: Endpoint Agent Commands

* 07 Aug 2025

Share this

Contents

# Reference: Endpoint Agent Commands

* Updated on 07 Aug 2025

## Supported Commands by OS

For commands which emit a report/reply event type from the agent, the corresponding event type is provided.

| Command | Report/Reply Event | macOS | Windows | Linux | Chrome | Edge |
| --- | --- | --- | --- | --- | --- | --- |
| [artifact\_get](/v2/docs/reference-endpoint-agent-commands#artifactget) | N/A | ☑️ | ☑️ | ☑️ |  |  |
| [deny\_tree](/v2/docs/reference-endpoint-agent-commands#denytree) | N/A | ☑️ | ☑️ | ☑️ |  |  |
| [dir\_find\_hash](/v2/docs/reference-endpoint-agent-commands#dirfindhash) | [DIR\_FINDHASH\_REP](/v2/docs/edr-events#dirfindhashrep) | ☑️ | ☑️ | ☑️ |  |  |
| [dir\_list](/v2/docs/reference-endpoint-agent-commands#dirlist) | [DIR\_LIST\_REP](/v2/docs/edr-events#dirlistrep) | ☑️ | ☑️ | ☑️ |  |  |
| [dns\_resolve](/v2/docs/reference-endpoint-agent-commands#dnsresolve) | [DNS\_REQUEST](/v2/docs/edr-events#dnsrequest) | ☑️ | ☑️ | ☑️ | ☑️ | ☑️ |
| [doc\_cache\_get](/v2/docs/reference-endpoint-agent-commands#doccacheget) | [GET\_DOCUMENT\_REP](/v2/docs/edr-events#getdocumentrep) | ☑️ | ☑️ |  |  |  |
| [get\_debug\_data](/v2/docs/reference-endpoint-agent-commands#getdebugdata) | [DEBUG\_DATA\_REP](/v2/docs/edr-events#debugdatarep) | ☑️ | ☑️ | ☑️ |  |  |
| [exfil\_add](/v2/docs/reference-endpoint-agent-commands#exfiladd) | [CLOUD\_NOTIFICATION](/v2/docs/edr-events#cloudnotification) | ☑️ | ☑️ | ☑️ |  |  |
| [exfil\_del](/v2/docs/reference-endpoint-agent-commands#exfildel) | [CLOUD\_NOTIFICATION](/v2/docs/edr-events#cloudnotification) | ☑️ | ☑️ | ☑️ |  |  |
| [exfil\_get](/v2/docs/reference-endpoint-agent-commands#exfilget) | [GET\_EXFIL\_EVENT\_REP](/v2/docs/edr-events#getexfileventrep) | ☑️ | ☑️ | ☑️ |  |  |
| [file\_del](/v2/docs/reference-endpoint-agent-commands#filedel) | [FILE\_DEL\_REP](/v2/docs/edr-events#filedelrep) | ☑️ | ☑️ | ☑️ |  |  |
| [file\_get](/v2/docs/reference-endpoint-agent-commands#fileget) | [FILE\_GET\_REP](/v2/docs/edr-events#filegetrep) | ☑️ | ☑️ | ☑️ |  |  |
| [file\_hash](/v2/docs/reference-endpoint-agent-commands#filehash) | [FILE\_HASH\_REP](/v2/docs/edr-events#filehashrep) | ☑️ | ☑️ | ☑️ |  |  |
| [file\_info](/v2/docs/reference-endpoint-agent-commands#fileinfo) | [FILE\_INFO\_REP](/v2/docs/edr-events#fileinforep) | ☑️ | ☑️ | ☑️ |  |  |
| [file\_mov](/v2/docs/reference-endpoint-agent-commands#filemov) | [FILE\_MOV\_REP](/v2/docs/edr-events#filemovrep) | ☑️ | ☑️ | ☑️ |  |  |
| [fim\_add](/v2/docs/reference-endpoint-agent-commands#fimadd) | [FIM\_ADD](/v2/docs/edr-events#fimadd) | ☑️ | ☑️ | ☑️ |  |  |
| [fim\_del](/v2/docs/reference-endpoint-agent-commands#fimdel) | [FIM\_DEL](/v2/docs/edr-events#fimdel) | ☑️ | ☑️ | ☑️ |  |  |
| [fim\_get](/v2/docs/reference-endpoint-agent-commands#fimget) | [FIM\_LIST\_REP](/v2/docs/edr-events#fimlistrep) | ☑️ | ☑️ | ☑️ |  |  |
| [hidden\_module\_scan](/v2/docs/reference-endpoint-agent-commands#hiddenmodulescan) | [HIDDEN\_MODULE\_DETECTED](/v2/docs/edr-events#hiddenmoduledetected) |  | ☑️ | ☑️ |  |  |
| [history\_dump](/v2/docs/reference-endpoint-agent-commands#historydump) | [HISTORY\_DUMP\_REP](/v2/docs/edr-events#historydumprep) | ☑️ | ☑️ | ☑️ | ☑️ | ☑️ |
| [log\_get](/v2/docs/reference-endpoint-agent-commands#logget) | N/A |  | ☑️ |  |  |  |
| [logoff](/v2/docs/reference-endpoint-agent-commands#logoff) | N/A | ☑️ | ☑️ | ☑️ |  |  |
| [mem\_find\_handle](/v2/docs/reference-endpoint-agent-commands#memfindhandle) | [MEM\_FIND\_HANDLES\_REP](/v2/docs/edr-events#memfindhandlesrep) |  | ☑️ |  |  |  |
| [mem\_find\_string](/v2/docs/reference-endpoint-agent-commands#memfindstring) | [MEM\_FIND\_STRING\_REP](/v2/docs/edr-events#memfindstringrep) | ☑️ | ☑️ | ☑️ |  |  |
| [mem\_handles](/v2/docs/reference-endpoint-agent-commands#memhandles) | [MEM\_HANDLES\_REP](/v2/docs/edr-events#memhandlesrep) |  | ☑️ |  |  |  |
| [mem\_map](/v2/docs/reference-endpoint-agent-commands#memmap) | [MEM\_MAP\_REP](/v2/docs/edr-events#memmaprep) | ☑️ | ☑️ | ☑️ |  |  |
| [mem\_read](/v2/docs/reference-endpoint-agent-commands#memread) | [MEM\_READ\_REP](/v2/docs/edr-events#memreadrep) | ☑️ | ☑️ | ☑️ |  |  |
| [mem\_strings](/v2/docs/reference-endpoint-agent-commands#memstrings) | [MEM\_STRINGS\_REP](/v2/docs/edr-events#memstringsrep) | ☑️ | ☑️ | ☑️ |  |  |
| [netstat](/v2/docs/reference-endpoint-agent-commands#netstat) | [NETSTAT\_REP](/v2/docs/edr-events#netstatrep) | ☑️ | ☑️ | ☑️ |  |  |
| [os\_autoruns](/v2/docs/reference-endpoint-agent-commands#osautoruns) | [OS\_AUTORUNS\_REP](/v2/docs/edr-events#osautorunsrep) | ☑️ | ☑️ |  |  |  |
| [os\_drivers](/v2/docs/reference-endpoint-agent-commands#osdrivers) | N/A |  | ☑️ |  |  |  |
| [os\_kill\_process](/v2/docs/reference-endpoint-agent-commands#oskillprocess) | [OS\_KILL\_PROCESS\_REP](/v2/docs/edr-events#oskillprocessrep) | ☑️ | ☑️ | ☑️ |  |  |
| [os\_packages](/v2/docs/reference-endpoint-agent-commands#ospackages) | [OS\_PACKAGES\_REP](/v2/docs/edr-events#ospackagesrep) |  | ☑️ | ☑️ | ☑️ | ☑️ |
| [os\_processes](/v2/docs/reference-endpoint-agent-commands#osprocesses) | [OS\_PROCESSES\_REP](/v2/docs/edr-events#osprocessesrep) | ☑️ | ☑️ | ☑️ |  |  |
| [os\_resume](/v2/docs/reference-endpoint-agent-commands#osresume) | [OS\_RESUME\_REP](/v2/docs/edr-events#osresumerep) | ☑️ | ☑️ | ☑️ |  |  |
| [os\_services](/v2/docs/reference-endpoint-agent-commands#osservices) | [OS\_SERVICES\_REP](/v2/docs/edr-events#osservicesrep) | ☑️ | ☑️ | ☑️ |  |  |
| [os\_suspend](/v2/docs/reference-endpoint-agent-commands#ossuspend) | [OS\_SUSPEND\_REP](/v2/docs/edr-events#ossuspendrep) | ☑️ | ☑️ | ☑️ |  |  |
| [os\_users](/v2/docs/reference-endpoint-agent-commands#osusers) | [OS\_USERS\_REP](/v2/docs/edr-events#osusersrep) |  | ☑️ |  |  |  |
| [os\_version](/v2/docs/reference-endpoint-agent-commands#osversion) | [OS\_VERSION\_REP](/v2/docs/edr-events#osversionrep) | ☑️ | ☑️ | ☑️ |  |  |
| [put](/v2/docs/reference-endpoint-agent-commands#put) | [RECEIPT](/v2/docs/edr-events#receipt) | ☑️ | ☑️ | ☑️ |  |  |
| [rejoin\_network](/v2/docs/reference-endpoint-agent-commands#rejoinnetwork) | [REJOIN\_NETWORK](/v2/docs/edr-events#rejoinnetwork) | ☑️ | ☑️ | ☑️ | ☑️ | ☑️ |
| [restart](/v2/docs/reference-endpoint-agent-commands#restart) | N/A | ☑️ | ☑️ | ☑️ |  |  |
| [run](/v2/docs/reference-endpoint-agent-commands#run) | N/A | ☑️ | ☑️ | ☑️ |  |  |
| [seal](/v2/docs/reference-endpoint-agent-commands#seal) |  |  | ☑️ |  |  |  |
| [segregate\_network](/v2/docs/reference-endpoint-agent-commands#segregatenetwork) | [SEGREGATE\_NETWORK](/v2/docs/edr-events#segregatenetwork) | ☑️ | ☑️ | ☑️ | ☑️ | ☑️ |
| [set\_performance\_mode](/v2/docs/reference-endpoint-agent-commands#setperformancemode) | N/A | ☑️ | ☑️ | ☑️ |  |  |
| [shutdown](/v2/docs/reference-endpoint-agent-commands#shutdown) |  | ☑️ | ☑️ | ☑️ |  |  |
| [uninstall](/v2/docs/reference-endpoint-agent-commands#uninstall) | N/A | ☑️ | ☑️ | ☑️ |  |  |
| [yara\_scan](/v2/docs/reference-endpoint-agent-commands#yarascan) | [YARA\_DETECTION](/v2/docs/edr-events#yaradetection) | ☑️ | ☑️ | ☑️ |  |  |
| [yara\_update](/v2/docs/reference-endpoint-agent-commands#yaraupdate) | N/A | ☑️ | ☑️ | ☑️ |  |  |
| [epp\_status](/v2/docs/reference-endpoint-agent-commands#eppstatus) | [EPP\_STATUS\_REP] | ☑️ |  |  |  |  |
| [epp\_scan](/v2/docs/reference-endpoint-agent-commands#eppscan) | [EPP\_SCAN\_REP] | ☑️ |  |  |  |  |
| [epp\_list\_exclusions](/v2/docs/reference-endpoint-agent-commands#epplistexclusions) | [EPP\_LIST\_EXCLUSIONS\_REP] | ☑️ |  |  |  |  |
| [epp\_add\_exclusion](/v2/docs/reference-endpoint-agent-commands#eppaddexclusion) | [EPP\_ADD\_EXCLUSION\_REP] | ☑️ |  |  |  |  |
| [epp\_rem\_exclusion](/v2/docs/reference-endpoint-agent-commands#eppremexclusion) | [EPP\_REM\_EXCLUSION\_REP] | ☑️ |  |  |  |  |
| [epp\_list\_quarantine](/v2/docs/reference-endpoint-agent-commands#epplistquarantine) | [EPP\_LIST\_QUARANTINE\_REP] | ☑️ |  |  |  |  |

## Command Descriptions

### artifact\_get

Retrieve an artifact from a Sensor.

The artifact collection command allows you to retrieve files directly from an EDR Sensor. This command is useful for collecting a single or multiple files from a Sensor in response to a detection or for incident triage purposes.

Artifacts can be collected via the automated Artifact Collection in the web UI, initiated via API calls, or pulled via the `artifact_get` command. Each approach provides value, depending on your use case. Utilizing the Artifact Collection capability can automate artifact collection across a fleet, whereas sensor commands can help collect files from a single Sensor under investigation.

**Platforms:**

**Report/Reply Event:**
 N/A

**Usage:**

```
usage: artifact_get [-h] [--file FILE] [--source SOURCE] [--type TYPE]
                    [--payload-id PAYLOADID] [--days-retention RETENTION]
                    [--is-ignore-cert]

optional arguments:
  --file FILE           file path to get
  --source SOURCE       optional os specific artifact source (not currently supported)
  --type TYPE           optional artifact type
  --payload-id PAYLOADID
                        optional specifies an idempotent payload ID to use
  --days-retention RETENTION
                        number of days the data should be retained, default 30
  --is-ignore-cert      if specified, the sensor will ignore SSL cert mismatch
                        while upload the artifact
```

Note on usage scenarios for the `--is-ignore-cert` flag: If the sensor is deployed on a host where built-in root CAs are not up to date or present at all, it may be necessary to use the `--is-ignore-cert` flag to allow the logs to be pushed to the cloud.

Unlike the main sensor transport (which uses a pinned certificate), the Artifact Collection feature uses Google infrastructure and their public SSL certificates. This may sometimes come up in unexpected ways. For example fresh Windows Server installations do not have the root CAs for `google.com` enabled by default.

### deny\_tree

Tells the sensor that all activity starting at a specific process (and its children) should be denied and killed. This particular command is excellent for ransomware mitigation.

**Platforms:**

**Usage:**

```
usage: deny_tree [-h] atom [atom ...]

positional arguments:
  atom        atoms to deny from
```

### dir\_find\_hash

Find files matching hashes starting at a root directory.

**Platforms:**

**Reply/Report Event:**
[DIR\_FINDHASH\_REP](/v2/docs/reference-edr-events#dirfindhashrep)

**Usage:**

```
usage: dir_find_hash [-h] [-d DEPTH] --hash HASHES rootDir fileExp

positional arguments:
  rootDir               the root directory where to begin the search from
  fileExp               a file name expression supporting basic wildcards like
                        * and ?

optional arguments:
  -d DEPTH, --depth DEPTH
                        optional maximum depth of the listing, defaults to a
                        single level
  --hash HASHES         sha256 to search for, can be specified multiple times
```

### dir\_list

List the contents of a directory.

> Windows Directories
>
> When using dir\_list on Windows systems, ensure the rootDir value is contained within double quotes AND backslashes are escaped. To list all files in a directory, a wildcard (e.g., \*) must be used for the fileExp value.
>
> For example, this will list all files in C:\
>
> * dir\_list “c:\\” \*
>
> These examples will **NOT** work correctly and will not show any files, but will not give an error since they are properly formatted:
>
> * dir\_list c:\\ \* (Missing double quotes)
> * dir\_list “c:\\” (Missing fileExp value)

**Platforms:**

**Report/Reply Event:**
[DIR\_LIST\_REP](/v2/docs/reference-edr-events#dirlistrep)

**Usage:**

```
usage: dir_list [-h] [-d DEPTH] rootDir fileExp

positional arguments:
  rootDir               the root directory where to begin the listing from
  fileExp               a file name expression supporting basic wildcards like
                        * and ?

optional arguments:
  -d DEPTH, --depth DEPTH
                        optional maximum depth of the listing, defaults to a
                        single level
```

### dns\_resolve

Cause the sensor to do a network resolution. Mainly used for internal purposes. An error code of 0 indicates a successful command.

**Platforms:**

**Usage:**

```
dns_resolve [-h] domain

positional arguments:
  domain      domain name to resolve
```

**Sample Output:**

```
{
   "ERROR" : 0
}
```

You wll also see a corresponding `DNS_REQUEST` event in the Sensor timeline.

**Sample** `DNS_REQUEST` **Event:**

```
{
  "DNS_TYPE": 1,
  "DOMAIN_NAME": "www.google.com",
  "IP_ADDRESS": "142.251.116.105",
  "MESSAGE_ID": 30183
}
```

### doc\_cache\_get

Retrieve a document / file that was cached on the sensor.

**Platforms:**

**Report/Reply Event:**
[GET\_DOCUMENT\_REP](/v2/docs/reference-edr-events#getdocumentrep)

This command is currently listed to the following document types:

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

### exfil\_add

Add an LC event to the list of events sent back to the backend by default.

Exfil Service

Rather than using the `exfil_add` and `exfil_del` commands exclusively, it is recommended to use the [Exfil extension](/v2/docs/ext-exfil) available through the web UI and REST interface.

**Platforms:**

**Usage:**

```
usage: exfil_add [-h] -e EXPIRE event

positional arguments:
  event                 name of event to start exfiling

optional arguments:
  -e EXPIRE, --expire EXPIRE
                        number of seconds before stopping exfil of event
```

### exfil\_del

Remove an LC event from the list of events always sent back to the backend.

Exfil Service

Rather than using the `exfil_add` and `exfil_del` commands exclusively, it is recommended to use the [Exfil extension](/v2/docs/ext-exfil) available through the web UI and REST interface.

**Platforms:**

**Usage:**

```
usage: exfil_del [-h] event

positional arguments:
  event       name of event to stop exfiling
```

### exfil\_get

List all LC events sent back to the backend by default.

**Platforms:**

**Report/Reply Event:**
[GET\_EXFIL\_EVENT\_REP](/v2/docs/reference-edr-events#getexfileventrep)

**Usage:**

```
usage: exfil_get [-h]
```

### file\_del

Delete a file from the endpoint.

**Platforms:**

**Report/Reply Event:**
[FILE\_DEL\_REP](/v2/docs/reference-edr-events#filedelrep)

\*\*Usage: \*\*

```
usage: file_del [-h] file

positional arguments:
  file        file path to delete
```

### file\_get

Retrieve a file from the endpoint.

*Note: The* `file_get` *command is limited to 10MB in size. For files larger than 10MB, please utilize the* `artifact_get` *command.*

**Platforms:**

**Report/Reply Event:**
[FILE\_GET\_REP](/v2/docs/reference-edr-events#filegetrep)

**Usage:**

```
usage: file_get [-h] [-o OFFSET] [-s MAXSIZE] file

positional arguments:
  file                  file path to file to get

optional arguments:
  -o OFFSET, --offset OFFSET
                        offset bytes to begin reading the file at, in base 10
  -s MAXSIZE, --size MAXSIZE
                        maximum number of bytes to read, in base 10, max of
                        10MB
```

### file\_hash

Compute the hash of a file.

**Platforms:**

**Report/Reply Event:**
[FILE\_HASH\_REP](/v2/docs/reference-edr-events#filehashrep)

**Usage:**

```
usage: file_hash [-h] file

positional arguments:
  file        file path to hash
```

### file\_info

Get file information, timestamps, sizes, etc.

**Platforms:**

**Report/Reply Event:**
[FILE\_INFO\_REP](/v2/docs/reference-edr-events#fileinforep)

**Usage:**

```
usage: file_info [-h] file

positional arguments:
  file        file path to file to get info on
```

### file\_mov

Move / rename a file on the endpoint.

**Platforms:**

**Report/Reply Event:**
[FILE\_MOV\_REP](/v2/docs/reference-edr-events#filemovrep)

**Usage:**

```
usage: file_mov [-h] srcFile dstFile

positional arguments:
  srcFile     source file path
  dstFile     destination file path
```

### fim\_add

Add a file or registry path pattern to monitor for modifications.

FIM rules are not persistent. This means that once an asset restarts, the rules will be gone. The recommended way of managing rule application is to use [Detection & Response rules](/v2/docs/detection-and-response) in a similar way to managing events sent to the cloud.

A sample  rule is available [here](/v2/docs/detection-and-response-examples).

Note that instead of using the `fim_add` and `fim_del` commands directly it is recommended to use [the Integrity extension](/v2/docs/ext-integrity) available through the web UI and REST interface.

**Platforms:**
   (see [this](/v2/docs/linux-agent-installation) for notes on Linux support)

**Report/Reply Event:**
[FIM\_ADD](/v2/docs/reference-edr-events#fimadd)

Patterns include basic wildcards:

* for one character: `?`
* for at least one character: `+`
* for any number of characters: `*`
* escape character: `\`

Note that the pattern is not a string literal, therefore "" needs to be escaped by one more level than usual.

So for example, you could do:

* `?:\*\Programs\Startup\*`
* `\REGISTRY\*\Microsoft\Windows\CurrentVersion\Run*`

Which would result in: `fim_add --pattern "?:\*\Programs\Startup\*" --pattern "\REGISTRY\*\Microsoft\Windows\CurrentVersion\Run*"`

**Usage:**

```
usage: fim_add [-h] --pattern PATTERNS

optional arguments:
  --pattern PATTERNS  file path or registry path pattern to monitor
```

### fim\_del

Remove a pattern from monitoring.

**Platforms:**
   (see [this](/v2/docs/linux-agent-installation) for notes on Linux support)

**Report/Reply Event:**
[FIM\_DEL](/v2/docs/reference-edr-events#fimdel)

```
usage: fim_del [-h] --pattern PATTERNS

optional arguments:
  --pattern PATTERNS  file path or registry path pattern to stop monitoring
```

### fim\_get

Get the list of the current monitored pattern(s).

**Platforms:**
   (see [this](/v2/docs/linux-agent-installation) for notes on Linux support)

**Report/Reply Event:**
[FIM\_LIST\_REP](/v2/docs/reference-edr-events#fimlistrep)

```
usage: fim_get [-h]
```

### get\_debug\_data

Retrieve debug data from the EDR sensor.

**Platforms:**

**Report/Reply Event:**
[DEBUG\_DATA\_REP](/v2/docs/reference-edr-events#debugdatarep)

### hidden\_module\_scan

Look for hidden modules in a process's (or all) memory. Hidden modules are DLLs or dylibs loaded manually (not by the OS).

**Platforms:**

**Report/Reply Event:**
[HIDDEN\_MODULE\_DETECTED](/v2/docs/reference-edr-events#hiddenmoduledetected)

**Usage:**

```
usage: hidden_module_scan [-h] pid

positional arguments:
  pid         pid of the process to scan, or "-1" for ALL processes
```

### history\_dump

Send to the backend the entire contents of the sensor event cache, i.e. detailed events of everything that happened recently.

**Platforms:**

**Report/Reply Event:**
[HISTORY\_DUMP\_REP](/v2/docs/reference-edr-events#historydumprep)

**Usage:**

```
usage: history_dump [-h] [-r ROOT] [-a ATOM] [-e EVENT]

optional arguments:
  -r ROOT, --rootatom ROOT
                        dump events present in the tree rooted at this atom
  -a ATOM, --atom ATOM  dump the event with this specific atom
  -e EVENT, --event EVENT
                        dump events of this type only
```

### log\_get

`log_get` is a legacy command that has been replaced with `artifact_get`. You can still issue a `log_get` command from the Sensor, however the parameters and output are the same as `artifact_get`.

### logoff

Execute a logoff for all the users

**Platforms:**

```
usage: logoff --is-confirmed
```

### mem\_find\_handle

Find specific open handles in memory on Windows.

**Platforms:**

**Report/Reply Event:**
[MEM\_FIND\_HANDLES\_REP](/v2/docs/reference-edr-events#memfindhandlesrep)

**Usage:**

```
mem_find_handle [-h] needle

positional arguments:
  needle      substring of the handle names to get
```

### mem\_find\_string

Find specific strings in memory.

**Platforms:**

**Report/Reply Event:**
[MEM\_FIND\_STRING\_REP](/v2/docs/reference-edr-events#memfindstringrep)

**Due to recent changes in MacOS, this may be less reliable on that platform.**

**Usage:**

```
mem_find_string [-h] -s STRING [STRING ...] pid

positional arguments:
  pid                   pid of the process to search in, 0 for all processes

optional arguments:
  -s STRING [STRING ...], --strings STRING [STRING ...]
                        list of strings to look for
```

### mem\_handles

List all open handles from a process (or all) on Windows.

**Platforms:**

**Report/Reply Event:**
[MEM\_HANDLES\_REP](/v2/docs/reference-edr-events#memhandlesrep)

**Usage:**

```
mem_handles [-h] [-p PID] [-a PROCESSATOM]

optional arguments:
  -p PID, --pid PID     pid of the process to get the handles from, 0 for all
                        processes
  -a PROCESSATOM, --processatom PROCESSATOM
                        the atom of the target process
```

### mem\_map

Display the map of memory pages from a process including size, access rights, etc.

**Platforms:**

**Report/Reply Event:**
[MEM\_MAP\_REP](/v2/docs/reference-edr-events#memmaprep)

**Due to recent changes in MacOS, this may be less reliable on that platform.**

**Usage:**

```
mem_map [-h] [-p PID] [-a PROCESSATOM]

optional arguments:
  -p PID, --pid PID     pid of the process to get the map from
  -a PROCESSATOM, --processatom PROCESSATOM
                        the atom of the target proces
```

### mem\_read

Retrieve a chunk of memory from a process given a base address and size.

**Platforms:**

**Report/Reply Event:**
[MEM\_READ\_REP](/v2/docs/reference-edr-events#memreadrep)

**Due to recent changes in MacOS, this may be less reliable on that platform.**

**Usage:**

```
mem_read [-h] [-p PID] [-a PROCESSATOM] baseAddr memSize

positional arguments:
  baseAddr              base address to read from, in HEX FORMAT
  memSize               number of bytes to read, in HEX FORMAT

optional arguments:
  -p PID, --pid PID     pid of the process to get the map from
  -a PROCESSATOM, --processatom PROCESSATOM
                        the atom of the target process
```

### mem\_strings

List strings from a process's memory.

**Platforms:**

**Report/Reply Event:**
[MEM\_STRINGS\_REP](/v2/docs/reference-edr-events#memstringsrep)

**Due to recent changes in MacOS, this may be less reliable on that platform.**

**Usage:**

```
mem_strings [-h] [-p PID] [-a PROCESSATOM]

optional arguments:
  -p PID, --pid PID     pid of the process to get the strings from
  -a PROCESSATOM, --processatom PROCESSATOM
                        the atom of the target process
```

### netstat

List network connections and sockets listening.

**Platforms:**

**Usage:**

```
netstat [-h]
```

**Sample Output:**

```
{
  "FRIENDLY": 0,
  "NETWORK_ACTIVITY": [
    {
      "DESTINATION": {
        "IP_ADDRESS": "0.0.0.0",
        "PORT": 0
      },
      "PROCESS_ID": 716,
      "PROTOCOL": "tcp4",
      "SOURCE": {
        "IP_ADDRESS": "0.0.0.0",
        "PORT": 135
      },
      "STATE": 2
    },
    {
      ...
    }
  ]
}
```

Netstat `STATE` fields can be mapped via the Windows `MIB_TCP_STATE` table, found [here](https://learn.microsoft.com/en-us/windows/win32/api/tcpmib/ns-tcpmib-mib_tcprow_lh).

| State | Value |
| --- | --- |
| 1 | CLOSED |
| 2 | LISTEN |
| 3 | SYN-SENT |
| 4 | SYN-RECEIVED |
| 5 | ESTABLISHED |
| 6 | FIN-WAIT-1 |
| 7 | FIN-WAIT-2 |
| 8 | CLOSE-WAIT |
| 9 | CLOSING |
| 10 | LAST-ACK |
| 11 | TIME-WAIT |
| 12 | DELETE TCB |

### os\_autoruns

List pieces of code executing at startup, similar to SysInternals autoruns.

**Platforms:**

```
usage: os_autoruns [-h]
```

### os\_drivers

List all drivers on Windows.

**Platforms:**

```
usage: os_drivers [-h]
```

### os\_kill\_process

Kill a process running on the endpoint.

**Platforms:**

```
usage: os_kill_process [-h] [-p PID] [-a PROCESSATOM]

optional arguments:
  -p PID, --pid PID     pid of the process to kill
  -a PROCESSATOM, --processatom PROCESSATOM
                        the atom of the target process
```

### os\_packages

List installed software packages.

**Platforms:**

```
usage: os_packages [-h]
```

### os\_processes

List all running processes on the endpoint.

For a faster response time, we recommend running `os_processes --is-no-modules`.

**Platforms:**

```
usage: os_processes [-h] [-p PID] [--is-no-modules]

optional arguments:
  -p PID, --pid PID  only get information on process id
  --is-no-modules    do not report modules in processes
```

### os\_resume

Resume execution of a process on the endpoint.

**Platforms:**

```
usage: os_resume [-h] [-p PID] [-a PROCESSATOM] [-t TID]

optional arguments:
  -p PID, --pid PID     process id
  -a PROCESSATOM, --processatom PROCESSATOM
                        the atom of the target process
  -t TID, --tid TID     thread id
```

### os\_services

List all services (Windows, launchctl on MacOS and initd on Linux).

**Platforms:**

```
usage: os_services [-h]
```

### os\_suspend

Suspend a process running on the endpoint.

**Platforms:**

```
usage: os_suspend [-h] [-p PID] [-a PROCESSATOM] [-t TID]

optional arguments:
  -p PID, --pid PID     process id
  -a PROCESSATOM, --processatom PROCESSATOM
                        the atom of the target process
  -t TID, --tid TID     thread id
```

### os\_users

List system users.

**Platforms:**

```
usage: os_users [-h]
```

### os\_version

Get detailed OS information on the endpoint.

**Platforms:**

```
usage: os_version [-h]
```

### put

Upload a payload to an endpoint without executing it.

**Platforms:**

```
usage: put [-h] --payload-name NAME [--payload-path PATH] [--is-ignore-cert]

optional arguments:
  --payload-name NAME  name of the payload to run
  --payload-path PATH  full path where to put the payload (including file name)
  --is-ignore-cert     if specified, the sensor will ignore SSL cert mismatch
```

**Report/Reply Event(s):**
`RECEIPT`
`CLOUD_NOTIFICATION`

Error Codes

A 200 `ERROR` code implies a successful `put` command, and will include the resulting file path. Any other error codes can be investigated [here](/v2/docs/reference-error-codes).

**Command Notes:**

Note on usage scenarios for the `--is-ignore-cert` flag: If the sensor is deployed on a host where built-in root CAs are not up to date or present at all, it may be necessary to use the `--is-ignore-cert` flag to allow the sensor to pull the payload to execute from the cloud.

Unlike the main sensor transport (which uses a pinned certificate), the Payloads feature uses Google infrastructure and their public SSL certificates.

This may sometimes come up in unexpected ways. For example fresh Windows Server installations do not have the root CAs for `google.com` enabled by default.

**Example:**

Assume you have a payload named `sample-script.sh`, and you wanted to upload it to the `/tmp` folder on a remote system, keeping the same name:

```
put --payload-name "sample_script.sh" --payload-path "/tmp/sample_script.sh"
```

If successful, this action will yield the following `RECEIPT` event:

```
"details":{
    "event":{
        "ERROR":200
        "FILE_PATH":"/tmp/sample-script.sh"
    }
"routing" : {...}
```

### pcap\_ifaces

List the network interfaces available for capture on a host.

**Platforms:**

**Usage:**

```
pcap_ifaces [-h]
```

**Sample Output:**

```
{
  "INTERFACE": [
    {
      "IPV4": [
        "10.128.15.198"
      ],
      "IPV6": [
        "fe80::4001:aff:fe80:fc6"
      ],
      "NAME": "ens4"
    },
    {
      "IPV4": [
        "127.0.0.1"
      ],
      "IPV6": [
        "::1"
      ],
      "NAME": "lo"
    },
    {
      "IPV4": [],
      "IPV6": [],
      "NAME": "any"
    },
    {
      "IPV4": [],
      "IPV6": [],
      "NAME": "nflog"
    },
    {
      "IPV4": [],
      "IPV6": [],
      "NAME": "nfqueue"
    }
  ]
}
```

### reboot

Execute an immediate system reboot (no warnings and zero delay time)

**Platforms:**

```
usage: reboot --is-confirmed
```

### reg\_list

List the keys and values in a Windows registry key.

**Platforms:**

```
usage: reg_list [-h] reg

positional arguments:
  reg         registry path to list, must start with one of "hkcr", "hkcc", "hkcu", "hklm", "hku", e.g. "hklm\software"...
```

### rejoin\_network

Tells the sensor to allow network connectivity again (after it was segregated).

**Platforms:**

**Report/Reply Event:**
[REJOIN\_NETWORK](/v2/docs/reference-edr-events#rejoinnetwork)

**Usage:**

```
usage: rejoin_network [-h]
```

### restart

Forces the LimaCharlie agent to re-initialize. This is typically only useful when dealing with cloned sensor IDs in combination with the remote deletion of the identity file on disk.

**Platforms:**

### run

Execute a payload or a shell command on the sensor.

**Platforms:**

```
usage: run [-h] [--payload-name NAME] [--arguments ARGUMENTS]
           [--shell-command SHELLCMD] [--timeout TIMEOUT] [--is-ignore-cert][--interpreter INTERPRETER]

optional arguments:
  --payload-name NAME   name of the payload to run
  --arguments ARGUMENTS
                        arguments to run the payload with
  --shell-command SHELLCMD
                        shell command to run
  --timeout TIMEOUT     number of seconds to wait for payload termination
  --is-ignore-cert      if specified, the sensor will ignore SSL cert mismatch
                        while upload the log
  --interpreter INTERPRETER
specifies that the named payload should be executed with
a specific interpreter like "powershell"
```

Note on usage scenarios for the `--is-ignore-cert` flag: If the sensor is deployed on a host where built-in root CAs are not up to date or present at all, it may be necessary to use the `--is-ignore-cert` flag to allow the sensor to pull the payload to execute from the cloud.

Using Arguments

In some cases, using the `--arguments` parameter may result in an error. If so, insert a leading space into the provided arguments.

For example `--arguments ' -ano'`

Unlike the main sensor transport (which uses a pinned certificate), the Payloads feature uses Google infrastructure and their public SSL certificates.

This may sometimes come up in unexpected ways. For example fresh Windows Server installations do not have the root CAs for `google.com` enabled by default.

Some shell execution requires embedding quotes within the command, for example when executing powershell. Here’s an example:

```
run --shell-command "powershell.exe -command \"Get-MpComputerStatus | Select-Object AMRunningMode\""
```

The above starts `powershell.exe` and passes it the `-command` argument and the value of the `-command` is `"Get-MpComputerStatus | Select-Object AMRunningMode”`.

###

### seal

Instruct the sensor to harden itself from tampering. This capability protects against use cases such as local admin users attempting to uninstall the LimaCharlie service. Please note that sealed status is currently only reflected in `CONNECTED` and `SYNC` events.

Seal Availability

Supported on sensor version 4.29.0 or newer and currently only supported on Windows.

Important note: the `seal` direct sensor command is stateless, meaning it will not survive a reboot. For this reason, in almost all cases, you want to automate the change of status in D&R rules using the `seal` and `unseal` [response actions](/v2/docs/response-actions) instead of this task. Alternatively you can also use the REST API endpoint `{`SID`}/seal` to change the status in a way that survives reboots.

The `should_seal` Boolean parameter indicates whether a Sensor has yet to complete the `seal` command.

**Platforms:**

**Usage:**

```
usage: seal [--enable] [--disable]
```

**Sample Event:**
 On Sensors version 4.29.0 or newer, you will see the following metadata within `SYNC` or `CONNECTED` events:

```
{
 ... ,
 "SEAL_STATUS" : {
    "ERROR": 0,
    "IS_DISABLED": 1
    }
}
```

### segregate\_network

Tells the sensor to stop all network connectivity on the host except LC comms to the backend. So it's network isolation, great to stop lateral movement.

Note that you should never upgrade a sensor version while the network is isolated through this mechanism. Doing so may result in the agent not regaining connectivity to the cloud, requiring a reboot to undo.

This command primitive is NOT persistent, meaning a sensor you segregate from the network using this command alone, upon reboot will rejoin the network. To achieve isolation from the network in a persistent way, see the `isolate network` and `rejoin network` [Detection & Response rule actions](/v2/docs/response-actions).

**Platforms:**

**Report/Reply Event:**
[SEGREGATE\_NETWORK](/v2/docs/reference-edr-events#segregatenetwork)

**Usage:**

```
usage: segregate_network [-h]
```

### set\_performance\_mode

Turn on or off the high performance mode on a sensor. This mode is designed for very high performance servers requiring high IO throughout. This mode reduces the accuracy of certain events which in turn reduces impact on the system, and is not useful for the vast majority of hosts. You can read more about Performance Mode and its caveats [here](/v2/docs/ext-exfil#performance-rules).

**Platforms:**

**Usage:**

```
usage: set_performance_mode [-h] [--is-enabled]

optional arguments:
  --is-enabled  if specified, the high performance mode is enabled, otherwise
                disabled
```

### shutdown

Execute an immediate system shut down (no warnings and zero delay time)

**Platforms:**

```
usage: shutdown --is-confirmed
```

### uninstall

Uninstall the sensor from that host.

*For more information on Sensor uninstallation, including Linux systems, check* [*here*](/v2/docs/endpoint-agent-uninstallation)*.*

**Platforms:**

**Usage:**

```
usage: uninstall [-h] [--is-confirmed]

optional arguments:
  --is-confirmed  must be specified as a confirmation you want to uninstall
                  the sensor
```

### yara\_scan

Scan for a specific yara signature in memory and files on the endpoint.

**Platforms:**

**The memory component of the scan on MacOS may be less reliable due to recent limitations imposed by Apple.**

```
yara_scan [--pid PID] [--filePath FILEPATH] [--processExpr PROCESSEXPR] [--is-memory-only] [--is-no-validation] [--root-dir ROOT-DIR] [--file-exp FILE-EXP] [--depth DEPTH] RULE

Positional arguments:
  RULE                   rule to compile and run on sensor, Yara resource reference like "hive://yara/my-source,other-source", literal rule or "https://" URL or base64 encoded rule

Options:
  --pid PID, -p PID      pid of the process to scan [default: -1]
  --filePath FILEPATH, -f FILEPATH
                         path to the file scan
  --processExpr PROCESSEXPR, -e PROCESSEXPR
                         expression to match on to scan (matches on full process path)
  --is-memory-only       only scan the memory, ignore files on disk. [default: true]
  --is-no-validation     if specified, do not validate the rule before sending. [default: false]
  --root-dir ROOT-DIR, -r ROOT-DIR
                         the root directory where to begin the search for files to scan
  --file-exp FILE-EXP, -x FILE-EXP
                         a file name expression supporting basic wildcards like * and ? to match against files in the --root-dir [default: *]
  --depth DEPTH, -d DEPTH
                         optional maximum depth of the search for files to scan, defaults to a single level
```

### yara\_update

Update the compiled yara signature bundle that is being used for constant memory and file scanning on the sensor.

Note

Instead of using the `yara_update` command directly it is recommended to use [the YARA extension](/v2/docs/ext-yara) available through the web UI and REST interface.

**Platforms:**

```
usage: yara_update [-h] rule

positional arguments:
  rule        rule to compile and set on sensor for constant scanning, literal rule or "https://" URL or base64 encoded rule
```

### epp\_status

Get the current status of EPP on a sensor.

**Platforms:**

```
usage: epp_status [-h]
```

### epp\_scan

Scan a directory or file using the EPP on the sensor.

**Platforms:**

```
usage: epp_scan [-h] path

positional arguments:
  path        File or directory to scan
```

### epp\_list\_exclusions

List all the exclusions for EPP on a sensor.

**Platforms:**

```
usage: epp_list_exclusions [-h]
```

### epp\_add\_exclusion

Add a new exclusion to EPP on a sensor.

**Platforms:**

```
usage: epp_add_exclusion [-h] value [--type]

positional arguments:
  value        Value of the exclusion to add
optional arguments:
  --type  Type of exclusion. Options are: extension, path, process
```

### epp\_rem\_exclusion

Remove an exclusion for EPP on a sensor.

**Platforms:**

```
usage: epp_rem_exclusion [-h] value [--type]

positional arguments:
  value        Value of the exclusion to remove
optional arguments:
  --type  Type of exclusion. Options are: extension, path, process
```

### epp\_list\_quarantine

List quarantined EPP on a sensor.

**Platforms:**

```
usage: epp_list_quarantine [-h]
```

Similar to agents, Sensors send telemetry to the LimaCharlie platform in the form of EDR telemetry or forwarded logs. Sensors are offered as a scalable, serverless solution for securely connecting endpoints of an organization to the cloud.

Endpoint Detection & Response

In LimaCharlie, Exfil (Event Collection) is a configuration extension that determines which types of events are collected and sent from endpoint agents to the cloud. It controls the data flow, ensuring only specified events are transmitted for monitoring and analysis. To capture specific events, they must be enabled within the Exfil or Event Collection settings.

In LimaCharlie, a Sensor ID (SID) is a unique identifier assigned to each deployed endpoint agent (sensor). It distinguishes individual sensors across an organization's infrastructure, allowing LimaCharlie to track, manage, and communicate with each endpoint. The Sensor ID is critical for operations such as sending commands, collecting telemetry, and monitoring activity, ensuring that actions and data are accurately linked to specific devices or endpoints.

Yes    No

[ ]  Need more information

[ ]  Difficult to understand

[ ]  Inaccurate or irrelevant content

[ ]  Missing/broken link

[ ]  Others

Comment

Comment (Optional)

Please enter your comment

Email

[ ]   Notify me about change

Please enter a valid email

Cancel