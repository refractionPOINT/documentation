# EchoTrail

[EchoTrail](https://echotrail.io/) is an API service that allows you to perform a lookup of a file name or hash value. EchoTrail will return a summary of statistical details that describes the behavior of the submitted value, as observed from their sensors over time.

LimaCharlie has an integration available for EchoTrail's `insights` API lookup, accepting one of the following:

  * MD5 Hash

  * SHA256 Hash

  * Windows filename with extension




## Detection & Response Rule

The following detection and response rule utilizes a file name from a `NEW_PROCESS` event to query the EchoTrail `insights` API:
    
    
    event: NEW_PROCESS
    op: lookup
    path: event/FILE_PATH
    resource: hive://lookup/echotrail-insights
    

EchoTrail's response data includes the following:
    
    
    {
      "rank": 24,
      "host_prev": "94.4",
      "eps": "96.07",
      "paths": [
        [
          "C:\\Windows\\System32",
          "99.92"
        ],
        [
          "C:\\WINDOWS\\System32",
          "0.07"
        ],
        [
          "C:\\Windows\\SysWOW64",
          "0.00"
        ],
        [
          "C:\\Users\\...",
          "0.00"
        ],
        [
          "C:\\Windows\\Temp\\...",
          "0.00"
        ],
        [
          "C:\\...",
          "0.00"
        ]
      ],
      "parents": [
        [
          "services.exe",
          "99.65"
        ],
        [
          "MsMpEng.exe",
          "0.35"
        ],
        [
          "rpcnet.exe",
          "0.00"
        ],
        [
          "svchost.exe",
          "0.00"
        ],
        [
          "MRT.exe",
          "0.00"
        ],
        [
          "cmd.exe",
          "0.00"
        ],
        [
          "consent.exe",
          "0.00"
        ],
        [
          "explorer.exe",
          "0.00"
        ],
        [
          "python.exe",
          "0.00"
        ],
        [
          "MRT-KB890830.exe",
          "0.00"
        ]
      ],
      "children": [
        [
          "WmiPrvSE.exe",
          "12.44"
        ],
        [
          "wmiprvse.exe",
          "7.96"
        ],
        [
          "backgroundTaskHost.exe",
          "7.76"
        ],
        [
          "taskhostw.exe",
          "6.76"
        ],
        [
          "backgroundtaskhost.exe",
          "4.96"
        ],
        [
          "dllhost.exe",
          "4.58"
        ],
        [
          "RuntimeBroker.exe",
          "3.95"
        ],
        [
          "runtimebroker.exe",
          "3.48"
        ],
        [
          "spatialaudiolicensesrv.exe",
          "2.47"
        ],
        [
          "werfault.exe",
          "1.65"
        ],
        [
          "GoogleUpdate.exe",
          "1.62"
        ],
        [
          "wermgr.exe",
          "1.55"
        ],
        [
          "gpupdate.exe",
          "1.44"
        ],
        [
          "filecoauth.exe",
          "1.40"
        ],
        [
          "FCHelper64.exe",
          "1.26"
        ],
        [
          "HxTsr.exe",
          "1.20"
        ],
        [
          "googleupdate.exe",
          "1.15"
        ],
        [
          "TiWorker.exe",
          "1.08"
        ],
        [
          "audiodg.exe",
          "1.05"
        ],
        [
          "tiworker.exe",
          "0.96"
        ]
      ],
      "grandparents": [
        [
          "wininit.exe",
          "99.89"
        ],
        [
          "services.exe",
          "0.11"
        ],
        [
          "explorer.exe",
          "0.00"
        ],
        [
          "cmd.exe",
          "0.00"
        ],
        [
          "userinit.exe",
          "0.00"
        ],
        [
          "svchost.exe",
          "0.00"
        ],
        [
          "Windows-KB890830-x64-V5.72-delta.exe",
          "0.00"
        ],
        [
          "Windows-KB890830-x64-V5.71-delta.exe",
          "0.00"
        ],
        [
          "Windows-KB890830-x64-V5.70-delta.exe",
          "0.00"
        ],
        [
          "Windows-KB890830-x64-V5.69-delta.exe",
          "0.00"
        ],
        [
          "Windows-KB890830-x64-V5.65.exe",
          "0.00"
        ],
        [
          "Windows-KB890830-x64-V5.62-delta.exe",
          "0.00"
        ],
        [
          "Windows-KB890830-x64-V5.58-delta.exe",
          "0.00"
        ],
        [
          "Windows-KB890830-x64-V5.57-delta.exe",
          "0.00"
        ]
      ],
      "network": [
        [
          "443",
          "45.89"
        ],
        [
          "80",
          "32.37"
        ],
        [
          "5353",
          "2.71"
        ],
        [
          "53",
          "1.17"
        ],
        [
          "5355",
          "0.61"
        ],
        [
          "1900",
          "0.31"
        ],
        [
          "54188",
          "0.17"
        ],
        [
          "3702",
          "0.16"
        ],
        [
          "54189",
          "0.07"
        ],
        [
          "67",
          "0.06"
        ],
        [
          "547",
          "0.05"
        ],
        [
          "53240",
          "0.05"
        ],
        [
          "59298",
          "0.05"
        ],
        [
          "53242",
          "0.05"
        ],
        [
          "53241",
          "0.04"
        ],
        [
          "53048",
          "0.04"
        ],
        [
          "62120",
          "0.04"
        ],
        [
          "64473",
          "0.03"
        ],
        [
          "58569",
          "0.03"
        ],
        [
          "50531",
          "0.03"
        ]
      ],
      "description": "Svchost.exe is the name for services that run from dynamic-linked libraries (DLLs). The Service Host Process acts like a shell for loading services from DLL files. Those services are partitioned into groups and each group is run in a different instance of the Service Host Process. This prevents problems in one instance from affecting other instances. That is also why you will see multiple instances of svchost.exe running at the same time.",
      "intel": "It is normal to see many svchost processes running on a single machine. It usually has elevated privileges and a tremendous amount of trust from Windows and third-party applications, leading to its abuse during a variety of attacks. Automated, opportunistic malware as well as manual, targeted tools commonly abuse this process in a few ways:\n\nName masquerading - More common to commodity, non-targeted attacks, malware will disguise itself as an svchost process by changing one or more characters in the name (e.g. svch0st, svchosts, scvhost, suchost, svchost32, etc.). These tend to be simple to identify by a human, but they can be more complicated to detect by algorithms or automated detection solutions if they are more than one character off the true name “svchost.”\n\nPath masquerading - Not uncommon to commodity malware but more common to targeted attack scenarios, malware or other tools used abused malicious purposes may disguise itself with an “svchost.exe” filename but located in a directory of the attacker’s choosing. It is not a legitimate svchost process. The legitimate svchost will always run from C:\\Windows\\System32 or C:\\Windows\\SysWOW64. If “svchost.exe” is running from any other directory, it is worth investigation. With endpoint process data, each running process’ path is simple to examine and, hence, simple to detect svchost path abuse.\n\nProcess migration - This type of abuse is more common to targeted or advanced attacks. Rather than running a malicious tool with the name “svchost.exe,” process migration allows an attacker to use a legitimate, currently running svchost process to effect their objectives. This typically occurs after privileged remote access is already gained to a system through a malicious remote administration tool (RAT). This sort of svchost abuse may be identifiable by uncommon behaviors of svchost, such as its launching of unusual executables, accessing unusual websites or IP addresses, performing host or network reconnaissance, or some combination thereof.\n",
      "truncated": {
        "paths": 5,
        "parents": 10,
        "grandparents": 13,
        "children": 1328,
        "network": 32667,
        "filenames": 1
      },
      "filenames": [
        [
          "svchost.exe",
          "100.00"
        ]
      ]
    }
