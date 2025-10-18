# Reference: Endpoint Agent Commands

## Supported Commands by OS

For commands which emit a report/reply event type from the agent, the corresponding event type is provided.

Command| Report/Reply Event| macOS| Windows| Linux| Chrome| Edge  
---|---|---|---|---|---|---  
[artifact_get](/v2/docs/reference-endpoint-agent-commands#artifactget)| N/A| ☑️| ☑️| ☑️| |   
[deny_tree](/v2/docs/reference-endpoint-agent-commands#denytree)| N/A| ☑️| ☑️| ☑️| |   
[dir_find_hash](/v2/docs/reference-endpoint-agent-commands#dirfindhash)| [DIR_FINDHASH_REP](/v2/docs/edr-events#dirfindhashrep)| ☑️| ☑️| ☑️| |   
[dir_list](/v2/docs/reference-endpoint-agent-commands#dirlist)| [DIR_LIST_REP](/v2/docs/edr-events#dirlistrep)| ☑️| ☑️| ☑️| |   
[dns_resolve](/v2/docs/reference-endpoint-agent-commands#dnsresolve)| [DNS_REQUEST](/v2/docs/edr-events#dnsrequest)| ☑️| ☑️| ☑️| ☑️| ☑️  
[doc_cache_get](/v2/docs/reference-endpoint-agent-commands#doccacheget)| [GET_DOCUMENT_REP](/v2/docs/edr-events#getdocumentrep)| ☑️| ☑️| | |   
[get_debug_data](/v2/docs/reference-endpoint-agent-commands#getdebugdata)| [DEBUG_DATA_REP](/v2/docs/edr-events#debugdatarep)| ☑️| ☑️| ☑️| |   
[exfil_add](/v2/docs/reference-endpoint-agent-commands#exfiladd)| [CLOUD_NOTIFICATION](/v2/docs/edr-events#cloudnotification)| ☑️| ☑️| ☑️| |   
[exfil_del](/v2/docs/reference-endpoint-agent-commands#exfildel)| [CLOUD_NOTIFICATION](/v2/docs/edr-events#cloudnotification)| ☑️| ☑️| ☑️| |   
[exfil_get](/v2/docs/reference-endpoint-agent-commands#exfilget)| [GET_EXFIL_EVENT_REP](/v2/docs/edr-events#getexfileventrep)| ☑️| ☑️| ☑️| |   
[file_del](/v2/docs/reference-endpoint-agent-commands#filedel)| [FILE_DEL_REP](/v2/docs/edr-events#filedelrep)| ☑️| ☑️| ☑️| |   
[file_get](/v2/docs/reference-endpoint-agent-commands#fileget)| [FILE_GET_REP](/v2/docs/edr-events#filegetrep)| ☑️| ☑️| ☑️| |   
[file_hash](/v2/docs/reference-endpoint-agent-commands#filehash)| [FILE_HASH_REP](/v2/docs/edr-events#filehashrep)| ☑️| ☑️| ☑️| |   
[file_info](/v2/docs/reference-endpoint-agent-commands#fileinfo)| [FILE_INFO_REP](/v2/docs/edr-events#fileinforep)| ☑️| ☑️| ☑️| |   
[file_mov](/v2/docs/reference-endpoint-agent-commands#filemov)| [FILE_MOV_REP](/v2/docs/edr-events#filemovrep)| ☑️| ☑️| ☑️| |   
[fim_add](/v2/docs/reference-endpoint-agent-commands#fimadd)| [FIM_ADD](/v2/docs/edr-events#fimadd)| ☑️| ☑️| ☑️| |   
[fim_del](/v2/docs/reference-endpoint-agent-commands#fimdel)| [FIM_DEL](/v2/docs/edr-events#fimdel)| ☑️| ☑️| ☑️| |   
[fim_get](/v2/docs/reference-endpoint-agent-commands#fimget)| [FIM_LIST_REP](/v2/docs/edr-events#fimlistrep)| ☑️| ☑️| ☑️| |   
[hidden_module_scan](/v2/docs/reference-endpoint-agent-commands#hiddenmodulescan)| [HIDDEN_MODULE_DETECTED](/v2/docs/edr-events#hiddenmoduledetected)| | ☑️| ☑️| |   
[history_dump](/v2/docs/reference-endpoint-agent-commands#historydump)| [HISTORY_DUMP_REP](/v2/docs/edr-events#historydumprep)| ☑️| ☑️| ☑️| ☑️| ☑️  
[log_get](/v2/docs/reference-endpoint-agent-commands#logget)| N/A| | ☑️| | |   
[logoff](/v2/docs/reference-endpoint-agent-commands#logoff)| N/A| ☑️| ☑️| ☑️| |   
[mem_find_handle](/v2/docs/reference-endpoint-agent-commands#memfindhandle)| [MEM_FIND_HANDLES_REP](/v2/docs/edr-events#memfindhandlesrep)| | ☑️| | |   
[mem_find_string](/v2/docs/reference-endpoint-agent-commands#memfindstring)| [MEM_FIND_STRING_REP](/v2/docs/edr-events#memfindstringrep)| ☑️| ☑️| ☑️| |   
[mem_handles](/v2/docs/reference-endpoint-agent-commands#memhandles)| [MEM_HANDLES_REP](/v2/docs/edr-events#memhandlesrep)| | ☑️| | |   
[mem_map](/v2/docs/reference-endpoint-agent-commands#memmap)| [MEM_MAP_REP](/v2/docs/edr-events#memmaprep)| ☑️| ☑️| ☑️| |   
[mem_read](/v2/docs/reference-endpoint-agent-commands#memread)| [MEM_READ_REP](/v2/docs/edr-events#memreadrep)| ☑️| ☑️| ☑️| |   
[mem_strings](/v2/docs/reference-endpoint-agent-commands#memstrings)| [MEM_STRINGS_REP](/v2/docs/edr-events#memstringsrep)| ☑️| ☑️| ☑️| |   
[netstat](/v2/docs/reference-endpoint-agent-commands#netstat)| [NETSTAT_REP](/v2/docs/edr-events#netstatrep)| ☑️| ☑️| ☑️| |   
[os_autoruns](/v2/docs/reference-endpoint-agent-commands#osautoruns)| [OS_AUTORUNS_REP](/v2/docs/edr-events#osautorunsrep)| ☑️| ☑️| | |   
[os_drivers](/v2/docs/reference-endpoint-agent-commands#osdrivers)| N/A| | ☑️| | |   
[os_kill_process](/v2/docs/reference-endpoint-agent-commands#oskillprocess)| [OS_KILL_PROCESS_REP](/v2/docs/edr-events#oskillprocessrep)| ☑️| ☑️| ☑️| |   
[os_packages](/v2/docs/reference-endpoint-agent-commands#ospackages)| [OS_PACKAGES_REP](/v2/docs/edr-events#ospackagesrep)| | ☑️| ☑️| ☑️| ☑️  
[os_processes](/v2/docs/reference-endpoint-agent-commands#osprocesses)| [OS_PROCESSES_REP](/v2/docs/edr-events#osprocessesrep)| ☑️| ☑️| ☑️| |   
[os_resume](/v2/docs/reference-endpoint-agent-commands#osresume)| [OS_RESUME_REP](/v2/docs/edr-events#osresumerep)| ☑️| ☑️| ☑️| |   
[os_services](/v2/docs/reference-endpoint-agent-commands#osservices)| [OS_SERVICES_REP](/v2/docs/edr-events#osservicesrep)| ☑️| ☑️| ☑️| |   
[os_suspend](/v2/docs/reference-endpoint-agent-commands#ossuspend)| [OS_SUSPEND_REP](/v2/docs/edr-events#ossuspendrep)| ☑️| ☑️| ☑️| |   
[os_users](/v2/docs/reference-endpoint-agent-commands#osusers)| [OS_USERS_REP](/v2/docs/edr-events#osusersrep)| | ☑️| | |   
[os_version](/v2/docs/reference-endpoint-agent-commands#osversion)| [OS_VERSION_REP](/v2/docs/edr-events#osversionrep)| ☑️| ☑️| ☑️| |   
[put](/v2/docs/reference-endpoint-agent-commands#put)| [RECEIPT](/v2/docs/edr-events#receipt)| ☑️| ☑️| ☑️| |   
[rejoin_network](/v2/docs/reference-endpoint-agent-commands#rejoinnetwork)| [REJOIN_NETWORK](/v2/docs/edr-events#rejoinnetwork)| ☑️| ☑️| ☑️| ☑️| ☑️  
[restart](/v2/docs/reference-endpoint-agent-commands#restart)| N/A| ☑️| ☑️| ☑️| |   
[run](/v2/docs/reference-endpoint-agent-commands#run)| N/A| ☑️| ☑️| ☑️| |   
[seal](/v2/docs/reference-endpoint-agent-commands#seal)| | | ☑️| | |   
[segregate_network](/v2/docs/reference-endpoint-agent-commands#segregatenetwork)| [SEGREGATE_NETWORK](/v2/docs/edr-events#segregatenetwork)| ☑️| ☑️| ☑️| ☑️| ☑️  
[set_performance_mode](/v2/docs/reference-endpoint-agent-commands#setperformancemode)| N/A| ☑️| ☑️| ☑️| |   
[shutdown](/v2/docs/reference-endpoint-agent-commands#shutdown)| | ☑️| ☑️| ☑️| |   
[uninstall](/v2/docs/reference-endpoint-agent-commands#uninstall)| N/A| ☑️| ☑️| ☑️| |   
[yara_scan](/v2/docs/reference-endpoint-agent-commands#yarascan)| [YARA_DETECTION](/v2/docs/edr-events#yaradetection)| ☑️| ☑️| ☑️| |   
[yara_update](/v2/docs/reference-endpoint-agent-commands#yaraupdate)| N/A| ☑️| ☑️| ☑️| |   
[epp_status](/v2/docs/reference-endpoint-agent-commands#eppstatus)| [EPP_STATUS_REP]| ☑️| | | |   
[epp_scan](/v2/docs/reference-endpoint-agent-commands#eppscan)| [EPP_SCAN_REP]| ☑️| | | |   
[epp_list_exclusions](/v2/docs/reference-endpoint-agent-commands#epplistexclusions)| [EPP_LIST_EXCLUSIONS_REP]| ☑️| | | |   
[epp_add_exclusion](/v2/docs/reference-endpoint-agent-commands#eppaddexclusion)| [EPP_ADD_EXCLUSION_REP]| ☑️| | | |   
[epp_rem_exclusion](/v2/docs/reference-endpoint-agent-commands#eppremexclusion)| [EPP_REM_EXCLUSION_REP]| ☑️| | | |
[epp_list_quarantine](/v2/docs/reference-endpoint-agent-commands#epplistquarantine)| [EPP_LIST_QUARANTINE_REP]| ☑️| | | |

## Command Descriptions

### artifact_get

Retrieve an artifact from a Sensor.

The artifact collection command allows you to retrieve files directly from an EDR Sensor. This command is useful for collecting a single or multiple files from a Sensor in response to a detection or for incident triage purposes.

Artifacts can be collected via the automated Artifact Collection in the web UI, initiated via API calls, or pulled via the `artifact_get` command. Each approach provides value, depending on your use case. Utilizing the Artifact Collection capability can automate artifact collection across a fleet, whereas sensor commands can help collect files from a single Sensor under investigation.

**Platforms:**  
______

**Report/Reply Event:**  
N/A

**Usage:**
    
    
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
    

Note on usage scenarios for the `--is-ignore-cert` flag: If the sensor is deployed on a host where built-in root CAs are not up to date or present at all, it may be necessary to use the `--is-ignore-cert` flag to allow the logs to be pushed to the cloud.

Unlike the main sensor transport (which uses a pinned certificate), the Artifact Collection feature uses Google infrastructure and their public SSL certificates. This may sometimes come up in unexpected ways. For example fresh Windows Server installations do not have the root CAs for `google.com` enabled by default.

### deny_tree

Tells the sensor that all activity starting at a specific process (and its children) should be denied and killed. This particular command is excellent for ransomware mitigation.

**Platforms:**  
______

**Usage:**
    
    
    usage: deny_tree [-h] atom [atom ...]
    
    positional arguments:
      atom        atoms to deny from
    

### dir_find_hash

Find files matching hashes starting at a root directory.

**Platforms:**  
______

**Reply/Report Event:**  
[DIR_FINDHASH_REP](/v2/docs/reference-edr-events#dirfindhashrep)

**Usage:**
    
    
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
    

### dir_list

List the contents of a directory.

> Windows Directories
> 
> When using dir_list on Windows systems, ensure the rootDir value is contained within double quotes AND backslashes are escaped. To list all files in a directory, a wildcard (e.g., *) must be used for the fileExp value.
> 
> For example, this will list all files in C:\
> 
>   * dir_list “c:\\\” *
> 
> 

> 
> These examples will **NOT** work correctly and will not show any files, but will not give an error since they are properly formatted:
> 
>   * dir_list c:\\\ * (Missing double quotes)
> 
>   * dir_list “c:\\\” (Missing fileExp value)
> 
> 


**Platforms:**  
______

**Report/Reply Event:**  
[DIR_LIST_REP](/v2/docs/reference-edr-events#dirlistrep)

**Usage:**
    
    
    usage: dir_list [-h] [-d DEPTH] rootDir fileExp
    
    positional arguments:
      rootDir               the root directory where to begin the listing from
      fileExp               a file name expression supporting basic wildcards like
                            * and ?
    
    optional arguments:
      -d DEPTH, --depth DEPTH
                            optional maximum depth of the listing, defaults to a
                            single level
    

### dns_resolve

Cause the sensor to do a network resolution. Mainly used for internal purposes. An error code of 0 indicates a successful command.

**Platforms:**  
______

**Usage:**
    
    
    dns_resolve [-h] domain
    
    positional arguments:
      domain      domain name to resolve
    

**Sample Output:**
    
    
    {
       "ERROR" : 0
    }
    

You wll also see a corresponding `DNS_REQUEST` event in the Sensor timeline.

**Sample**`DNS_REQUEST`**Event:**
    
    
    {
      "DNS_TYPE": 1,
      "DOMAIN_NAME": "www.google.com",
      "IP_ADDRESS": "142.251.116.105",
      "MESSAGE_ID": 30183
    }
    

### doc_cache_get

Retrieve a document / file that was cached on the sensor.

**Platforms:**  
____

**Report/Reply Event:**  
[GET_DOCUMENT_REP](/v2/docs/reference-edr-events#getdocumentrep)

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
    
    
    usage: doc_cache_get [-h] [-f FILE_PATTERN] [-s HASHSTR]
    
    optional arguments:
      -f FILE_PATTERN, --file_pattern FILE_PATTERN
                            a pattern to match on the file path and name of the
                            document, simple wildcards ? and * are supported
      -s HASHSTR, --hash HASHSTR
                            hash of the document to get
    

### exfil_add

Add an LC event to the list of events sent back to the backend by default.

Exfil Service

Rather than using the `exfil_add` and `exfil_del` commands exclusively, it is recommended to use the [Exfil extension](/v2/docs/ext-exfil) available through the web UI and REST interface.

**Platforms:**  
______

**Usage:**
    
    
    usage: exfil_add [-h] -e EXPIRE event
    
    positional arguments:
      event                 name of event to start exfiling
    
    optional arguments:
      -e EXPIRE, --expire EXPIRE
                            number of seconds before stopping exfil of event
    

### exfil_del

Remove an LC event from the list of events always sent back to the backend.

Exfil Service

Rather than using the `exfil_add` and `exfil_del` commands exclusively, it is recommended to use the [Exfil extension](/v2/docs/ext-exfil) available through the web UI and REST interface.

**Platforms:**  
______

**Usage:**
    
    
    usage: exfil_del [-h] event
    
    positional arguments:
      event       name of event to stop exfiling
    
    

### exfil_get

List all LC events sent back to the backend by default.

**Platforms:**  
______

**Report/Reply Event:**  
[GET_EXFIL_EVENT_REP](/v2/docs/reference-edr-events#getexfileventrep)

**Usage:**
    
    
    usage: exfil_get [-h]
    

### file_del

Delete a file from the endpoint.

**Platforms:**  
______

**Report/Reply Event:**  
[FILE_DEL_REP](/v2/docs/reference-edr-events#filedelrep)

**Usage: **
    
    
    usage: file_del [-h] file
    
    positional arguments:
      file        file path to delete
    
    

### file_get

Retrieve a file from the endpoint.

_Note: The_`file_get` _command is limited to 10MB in size. For files larger than 10MB, please utilize the_`artifact_get` _command._

**Platforms:**  
______

**Report/Reply Event:**  
[FILE_GET_REP](/v2/docs/reference-edr-events#filegetrep)

**Usage:**
    
    
    usage: file_get [-h] [-o OFFSET] [-s MAXSIZE] file
    
    positional arguments:
      file                  file path to file to get
    
    optional arguments:
      -o OFFSET, --offset OFFSET
                            offset bytes to begin reading the file at, in base 10
      -s MAXSIZE, --size MAXSIZE
                            maximum number of bytes to read, in base 10, max of
                            10MB
    

### file_hash

Compute the hash of a file.

**Platforms:**  
______

**Report/Reply Event:**  
[FILE_HASH_REP](/v2/docs/reference-edr-events#filehashrep)

**Usage:**
    
    
    usage: file_hash [-h] file
    
    positional arguments:
      file        file path to hash
    
    

### file_info

Get file information, timestamps, sizes, etc.

**Platforms:**  
______

**Report/Reply Event:**  
[FILE_INFO_REP](/v2/docs/reference-edr-events#fileinforep)

**Usage:**
    
    
    usage: file_info [-h] file
    
    positional arguments:
      file        file path to file to get info on
    
    

### file_mov

Move / rename a file on the endpoint.

**Platforms:**  
______

**Report/Reply Event:**  
[FILE_MOV_REP](/v2/docs/reference-edr-events#filemovrep)

**Usage:**
    
    
    usage: file_mov [-h] srcFile dstFile
    
    positional arguments:
      srcFile     source file path
      dstFile     destination file path
    
    

### fim_add

Add a file or registry path pattern to monitor for modifications.

FIM rules are not persistent. This means that once an asset restarts, the rules will be gone. The recommended way of managing rule application is to use [Detection & Response rules](/v2/docs/detection-and-response) in a similar way to managing events sent to the cloud.

A sample  rule is available [here](/v2/docs/detection-and-response-examples).

Note that instead of using the `fim_add` and `fim_del` commands directly it is recommended to use [the Integrity extension](/v2/docs/ext-integrity) available through the web UI and REST interface.

**Platforms:**  
______(see[this](/v2/docs/linux-agent-installation) for notes on Linux support)

**Report/Reply Event:**  
[FIM_ADD](/v2/docs/reference-edr-events#fimadd)

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
    
    
    usage: fim_add [-h] --pattern PATTERNS
    
    optional arguments:
      --pattern PATTERNS  file path or registry path pattern to monitor
    

### fim_del

Remove a pattern from monitoring.

**Platforms:**  
______(see[this](/v2/docs/linux-agent-installation) for notes on Linux support)

**Report/Reply Event:**  
[FIM_DEL](/v2/docs/reference-edr-events#fimdel)
    
    
    usage: fim_del [-h] --pattern PATTERNS
    
    optional arguments:
      --pattern PATTERNS  file path or registry path pattern to stop monitoring
    

### fim_get

Get the list of the current monitored pattern(s).

**Platforms:**  
______(see[this](/v2/docs/linux-agent-installation) for notes on Linux support)

**Report/Reply Event:**  
[FIM_LIST_REP](/v2/docs/reference-edr-events#fimlistrep)
    
    
    usage: fim_get [-h]
    

### get_debug_data

Retrieve debug data from the EDR sensor.

**Platforms:**  
______

**Report/Reply Event:**  
[DEBUG_DATA_REP](/v2/docs/reference-edr-events#debugdatarep)

### hidden_module_scan

Look for hidden modules in a process's (or all) memory. Hidden modules are DLLs or dylibs loaded manually (not by the OS).

**Platforms:**  
__

**Report/Reply Event:**  
[HIDDEN_MODULE_DETECTED](/v2/docs/reference-edr-events#hiddenmoduledetected)

**Usage:**
    
    
    usage: hidden_module_scan [-h] pid
    
    positional arguments:
      pid         pid of the process to scan, or "-1" for ALL processes
    

### history_dump

Send to the backend the entire contents of the sensor event cache, i.e. detailed events of everything that happened recently.

**Platforms:**  
______

**Report/Reply Event:**  
[HISTORY_DUMP_REP](/v2/docs/reference-edr-events#historydumprep)

**Usage:**
    
    
    usage: history_dump [-h] [-r ROOT] [-a ATOM] [-e EVENT]
    
    optional arguments:
      -r ROOT, --rootatom ROOT
                            dump events present in the tree rooted at this atom
      -a ATOM, --atom ATOM  dump the event with this specific atom
      -e EVENT, --event EVENT
                            dump events of this type only
    

### log_get

`log_get` is a legacy command that has been replaced with `artifact_get`. You can still issue a `log_get` command from the Sensor, however the parameters and output are the same as `artifact_get`.

### logoff

Execute a logoff for all the users

**Platforms:**  
______
    
    
    usage: logoff --is-confirmed

### mem_find_handle

Find specific open handles in memory on Windows.

**Platforms:**  
__

**Report/Reply Event:**  
[MEM_FIND_HANDLES_REP](/v2/docs/reference-edr-events#memfindhandlesrep)

**Usage:**
    
    
    mem_find_handle [-h] needle
    
    positional arguments:
      needle      substring of the handle names to get
    

### mem_find_string

Find specific strings in memory.

**Platforms:**  
______

**Report/Reply Event:**  
[MEM_FIND_STRING_REP](/v2/docs/reference-edr-events#memfindstringrep)

**Due to recent changes in MacOS, this may be less reliable on that platform.**

**Usage:**
    
    
    mem_find_string [-h] -s STRING [STRING ...] pid
    
    positional arguments:
      pid                   pid of the process to search in, 0 for all processes
    
    optional arguments:
      -s STRING [STRING ...], --strings STRING [STRING ...]
                            list of strings to look for
    

### mem_handles

List all open handles from a process (or all) on Windows.

**Platforms:**  
__

**Report/Reply Event:**  
[MEM_HANDLES_REP](/v2/docs/reference-edr-events#memhandlesrep)

**Usage:**
    
    
    mem_handles [-h] [-p PID] [-a PROCESSATOM]
    
    optional arguments:
      -p PID, --pid PID     pid of the process to get the handles from, 0 for all
                            processes
      -a PROCESSATOM, --processatom PROCESSATOM
                            the atom of the target process
    

### mem_map

Display the map of memory pages from a process including size, access rights, etc.

**Platforms:**  
______

**Report/Reply Event:**  
[MEM_MAP_REP](/v2/docs/reference-edr-events#memmaprep)

**Due to recent changes in MacOS, this may be less reliable on that platform.**

**Usage:**
    
    
    mem_map [-h] [-p PID] [-a PROCESSATOM]
    
    optional arguments:
      -p PID, --pid PID     pid of the process to get the map from
      -a PROCESSATOM, --processatom PROCESSATOM
                            the atom of the target proces
    

### mem_read

Retrieve a chunk of memory from a process given a base address and size.

**Platforms:**  
______

**Report/Reply Event:**  
[MEM_READ_REP](/v2/docs/reference-edr-events#memreadrep)

**Due to recent changes in MacOS, this may be less reliable on that platform.**

**Usage:**
    
    
    mem_read [-h] [-p PID] [-a PROCESSATOM] baseAddr memSize
    
    positional arguments:
      baseAddr              base address to read from, in HEX FORMAT
      memSize               number of bytes to read, in HEX FORMAT
    
    optional arguments:
      -p PID, --pid PID     pid of the process to get the map from
      -a PROCESSATOM, --processatom PROCESSATOM
                            the atom of the target process
    

### mem_strings

List strings from a process's memory.

**Platforms:**  
______

**Report/Reply Event:**  
[MEM_STRINGS_REP](/v2/docs/reference-edr-events#memstringsrep)

**Due to recent changes in MacOS, this may be less reliable on that platform.**

**Usage:**
    
    
    mem_strings [-h] [-p PID] [-a PROCESSATOM]
    
    optional arguments:
      -p PID, --pid PID     pid of the process to get the strings from
      -a PROCESSATOM, --processatom PROCESSATOM
                            the atom of the target process
    

### netstat

List network connections and sockets listening.

**Platforms:**  
______

**Usage:**
    
    
    netstat [-h]
    

**Sample Output:**
    
    
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
    

Netstat `STATE` fields can be mapped via the Windows `MIB_TCP_STATE` table, found [here](https://learn.microsoft.com/en-us/windows/win32/api/tcpmib/ns-tcpmib-mib_tcprow_lh).

State| Value  
---|---  
1| CLOSED  
2| LISTEN  
3| SYN-SENT  
4| SYN-RECEIVED  
5| ESTABLISHED  
6| FIN-WAIT-1  
7| FIN-WAIT-2  
8| CLOSE-WAIT  
9| CLOSING  
10| LAST-ACK  
11| TIME-WAIT  
12| DELETE TCB  
  
### os_autoruns

List pieces of code executing at startup, similar to SysInternals autoruns.

**Platforms:**  
______
    
    
    usage: os_autoruns [-h]

### os_drivers

List all drivers on Windows.

**Platforms:**  
__
    
    
    usage: os_drivers [-h]

### os_kill_process

Kill a process running on the endpoint.

**Platforms:**  
______
    
    
    usage: os_kill_process [-h] [-p PID] [-a PROCESSATOM]
    
    optional arguments:
      -p PID, --pid PID     pid of the process to kill
      -a PROCESSATOM, --processatom PROCESSATOM
                            the atom of the target process

### os_packages

List installed software packages.

**Platforms:**  
____
    
    
    usage: os_packages [-h]

### os_processes

List all running processes on the endpoint.

For a faster response time, we recommend running `os_processes --is-no-modules`.

**Platforms:**  
______
    
    
    usage: os_processes [-h] [-p PID] [--is-no-modules]
    
    optional arguments:
      -p PID, --pid PID  only get information on process id
      --is-no-modules    do not report modules in processes

### os_resume

Resume execution of a process on the endpoint.

**Platforms:**  
______
    
    
    usage: os_resume [-h] [-p PID] [-a PROCESSATOM] [-t TID]
    
    optional arguments:
      -p PID, --pid PID     process id
      -a PROCESSATOM, --processatom PROCESSATOM
                            the atom of the target process
      -t TID, --tid TID     thread id

### os_services

List all services (Windows, launchctl on MacOS and initd on Linux).

**Platforms:**  
______
    
    
    usage: os_services [-h]

### os_suspend

Suspend a process running on the endpoint.

**Platforms:**  
______
    
    
    usage: os_suspend [-h] [-p PID] [-a PROCESSATOM] [-t TID]
    
    optional arguments:
      -p PID, --pid PID     process id
      -a PROCESSATOM, --processatom PROCESSATOM
                            the atom of the target process
      -t TID, --tid TID     thread id

### os_users

List system users.

**Platforms:**  
__
    
    
    usage: os_users [-h]

### os_version

Get detailed OS information on the endpoint.

**Platforms:**  
______
    
    
    usage: os_version [-h]

### put

Upload a payload to an endpoint without executing it.

**Platforms:**  
______
    
    
    usage: put [-h] --payload-name NAME [--payload-path PATH] [--is-ignore-cert]
    
    optional arguments:
      --payload-name NAME  name of the payload to run
      --payload-path PATH  full path where to put the payload (including file name)
      --is-ignore-cert     if specified, the sensor will ignore SSL cert mismatch

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
    
    
    put --payload-name "sample_script.sh" --payload-path "/tmp/sample_script.sh"
    

If successful, this action will yield the following `RECEIPT` event:
    
    
    "details":{
        "event":{
            "ERROR":200
            "FILE_PATH":"/tmp/sample-script.sh"
        }
    "routing" : {...}
    

### pcap_ifaces

List the network interfaces available for capture on a host.

**Platforms:**  
__

**Usage:**
    
    
    pcap_ifaces [-h]
    

**Sample Output:**
    
    
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
    

### reboot

Execute an immediate system reboot (no warnings and zero delay time)

**Platforms:**  
______
    
    
    usage: reboot --is-confirmed

### reg_list

List the keys and values in a Windows registry key.

**Platforms:**  
__
    
    
    usage: reg_list [-h] reg
    
    positional arguments:
      reg         registry path to list, must start with one of "hkcr", "hkcc", "hkcu", "hklm", "hku", e.g. "hklm\software"...

### rejoin_network

Tells the sensor to allow network connectivity again (after it was segregated).

**Platforms:**  
______

**Report/Reply Event:**  
[REJOIN_NETWORK](/v2/docs/reference-edr-events#rejoinnetwork)

**Usage:**
    
    
    usage: rejoin_network [-h]
    

### restart

Forces the LimaCharlie agent to re-initialize. This is typically only useful when dealing with cloned sensor IDs in combination with the remote deletion of the identity file on disk.

**Platforms:**  
______

### run

Execute a payload or a shell command on the sensor.

**Platforms:**  
______
    
    
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

Note on usage scenarios for the `--is-ignore-cert` flag: If the sensor is deployed on a host where built-in root CAs are not up to date or present at all, it may be necessary to use the `--is-ignore-cert` flag to allow the sensor to pull the payload to execute from the cloud.

Using Arguments

In some cases, using the `--arguments` parameter may result in an error. If so, insert a leading space into the provided arguments.

For example `--arguments ' -ano'`

Unlike the main sensor transport (which uses a pinned certificate), the Payloads feature uses Google infrastructure and their public SSL certificates.

This may sometimes come up in unexpected ways. For example fresh Windows Server installations do not have the root CAs for `google.com` enabled by default.

Some shell execution requires embedding quotes within the command, for example when executing powershell. Here’s an example:
    
    
    run --shell-command "powershell.exe -command \"Get-MpComputerStatus | Select-Object AMRunningMode\""

The above starts `powershell.exe` and passes it the `-command` argument and the value of the `-command` is `"Get-MpComputerStatus | Select-Object AMRunningMode”`.

### 

### seal

Instruct the sensor to harden itself from tampering. This capability protects against use cases such as local admin users attempting to uninstall the LimaCharlie service. Please note that sealed status is currently only reflected in `CONNECTED` and `SYNC` events.

Seal Availability

Supported on sensor version 4.29.0 or newer and currently only supported on Windows.

Important note: the `seal` direct sensor command is stateless, meaning it will not survive a reboot. For this reason, in almost all cases, you want to automate the change of status in D&R rules using the `seal` and `unseal` [response actions](/v2/docs/response-actions) instead of this task. Alternatively you can also use the REST API endpoint `{`SID`}/seal` to change the status in a way that survives reboots.

The `should_seal` Boolean parameter indicates whether a Sensor has yet to complete the `seal` command.

**Platforms:**  
__

**Usage:**
    
    
    usage: seal [--enable] [--disable]
    

**Sample Event:**  
On Sensors version 4.29.0 or newer, you will see the following metadata within `SYNC` or `CONNECTED` events:
    
    
    {
     ... ,
     "SEAL_STATUS" : {
        "ERROR": 0,
        "IS_DISABLED": 1
        }
    }
    

### segregate_network

Tells the sensor to stop all network connectivity on the host except LC comms to the backend. So it's network isolation, great to stop lateral movement.

Note that you should never upgrade a sensor version while the network is isolated through this mechanism. Doing so may result in the agent not regaining connectivity to the cloud, requiring a reboot to undo.

This command primitive is NOT persistent, meaning a sensor you segregate from the network using this command alone, upon reboot will rejoin the network. To achieve isolation from the network in a persistent way, see the `isolate network` and `rejoin network` [Detection & Response rule actions](/v2/docs/response-actions).

**Platforms:**  
______

**Report/Reply Event:**  
[SEGREGATE_NETWORK](/v2/docs/reference-edr-events#segregatenetwork)

**Usage:**
    
    
    usage: segregate_network [-h]
    

### set_performance_mode

Turn on or off the high performance mode on a sensor. This mode is designed for very high performance servers requiring high IO throughout. This mode reduces the accuracy of certain events which in turn reduces impact on the system, and is not useful for the vast majority of hosts. You can read more about Performance Mode and its caveats [here](/v2/docs/ext-exfil#performance-rules).

**Platforms:**  
__

**Usage:**
    
    
    usage: set_performance_mode [-h] [--is-enabled]
    
    optional arguments:
      --is-enabled  if specified, the high performance mode is enabled, otherwise
                    disabled
    

### shutdown

Execute an immediate system shut down (no warnings and zero delay time)

**Platforms:**  
______
    
    
    usage: shutdown --is-confirmed

### uninstall

Uninstall the sensor from that host.

_For more information on Sensor uninstallation, including Linux systems, check_[ _here_](/v2/docs/endpoint-agent-uninstallation) _._

**Platforms:**  
____

**Usage:**
    
    
    usage: uninstall [-h] [--is-confirmed]
    
    optional arguments:
      --is-confirmed  must be specified as a confirmation you want to uninstall
                      the sensor
    

### yara_scan

Scan for a specific yara signature in memory and files on the endpoint.

**Platforms:**  
______

**The memory component of the scan on MacOS may be less reliable due to recent limitations imposed by Apple.**
    
    
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
    

### yara_update

Update the compiled yara signature bundle that is being used for constant memory and file scanning on the sensor.

Note

Instead of using the `yara_update` command directly it is recommended to use [the YARA extension](/v2/docs/ext-yara) available through the web UI and REST interface.

**Platforms:**  
______
    
    
    usage: yara_update [-h] rule
    
    positional arguments:
      rule        rule to compile and set on sensor for constant scanning, literal rule or "https://" URL or base64 encoded rule

### epp_status

Get the current status of EPP on a sensor.

**Platforms:**  
__
    
    
    usage: epp_status [-h]

### epp_scan

Scan a directory or file using the EPP on the sensor.

**Platforms:**  
__
    
    
    usage: epp_scan [-h] path
    
    positional arguments:
      path        File or directory to scan

### epp_list_exclusions

List all the exclusions for EPP on a sensor.

**Platforms:**  
__
    
    
    usage: epp_list_exclusions [-h]

### epp_add_exclusion

Add a new exclusion to EPP on a sensor.

**Platforms:**  
__
    
    
    usage: epp_add_exclusion [-h] value [--type]
    
    positional arguments:
      value        Value of the exclusion to add
    optional arguments:
      --type  Type of exclusion. Options are: extension, path, process

### epp_rem_exclusion

Remove an exclusion for EPP on a sensor.

**Platforms:**  
__
    
    
    usage: epp_rem_exclusion [-h] value [--type]
    
    positional arguments:
      value        Value of the exclusion to remove
    optional arguments:
      --type  Type of exclusion. Options are: extension, path, process

### epp_list_quarantine

List quarantined EPP on a sensor.

**Platforms:**
__


    usage: epp_list_quarantine [-h]


