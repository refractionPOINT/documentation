## Rules Unit Tests

A D&R rule record can optionally contain unit tests. These tests describe events that should match, and events that should not match. When a D&R rule is updated or created, LimaCharlie will simulate the rules and if the tests fail, an error is produced.

### Structure

A typical D&R rule looks like:

```
{
  "detect": {...},
  "respond": [
    {},
    {}
  ],
  "tests": {
    "match": [],
    "non_match": []
  }
}
```

The `match` and `non_match` both have the same format: they contain a list of lists of events. Each top list element is a unit test, and the content of a test is a list of events as would be seen by LimaCharlie. The reason for the test to be a list is to accomodate for [Stateful Detections](/v2/docs/stateful-rules) which operate across multiple events.

Here’s an example:

```
{
  "tests": {
    "match": [
      [{"event": ...}, {"event": ...}, {"event": ...}],
      [{"event": ...}],
      [{"event": ...}]
    ],
    "non_match": [
      [{"event": ...}, {"event": ...}],
      [{"event": ...}]
    ]
  }
}
```

### Example

```
version: 3
hives:
    dr-general:
        "CobaltStrike Named Pipe Patterns":
            data:
                detect:
                    event: WEL
                    op: and
                    rules:
                      - op: and
                        rules:
                        - op: or
                          rules:
                          - case sensitive: false
                            op: is
                            path: event/EVENT/System/_event_id
                            value: '17'
                          - case sensitive: false
                            op: is
                            path: event/EVENT/System/_event_id
                            value: '18'
                        - case sensitive: false
                          op: is
                          path: event/EVENT/System/Channel
                          value: Microsoft-Windows-Sysmon/Operational
                      - op: or
                        rules:
                        - op: or
                          rules:
                          - case sensitive: false
                            op: starts with
                            path: event/EVENT/EventData/PipeName
                            value: \mojo.5688.8052.183894939787088877
                          - case sensitive: false
                            op: starts with
                            path: event/EVENT/EventData/PipeName
                            value: \mojo.5688.8052.35780273329370473
                          - case sensitive: false
                            op: starts with
                            path: event/EVENT/EventData/PipeName
                            value: \mypipe-f
                          - case sensitive: false
                            op: starts with
                            path: event/EVENT/EventData/PipeName
                            value: \mypipe-h
                          - case sensitive: false
                            op: starts with
                            path: event/EVENT/EventData/PipeName
                            value: \ntsvcs
                          - case sensitive: false
                            op: starts with
                            path: event/EVENT/EventData/PipeName
                            value: \scerpc
                          - case sensitive: false
                            op: starts with
                            path: event/EVENT/EventData/PipeName
                            value: \win_svc
                          - case sensitive: false
                            op: starts with
                            path: event/EVENT/EventData/PipeName
                            value: \spoolss
                          - case sensitive: false
                            op: starts with
                            path: event/EVENT/EventData/PipeName
                            value: \msrpc_
                          - case sensitive: false
                            op: starts with
                            path: event/EVENT/EventData/PipeName
                            value: \win\msrpc_
                          - case sensitive: false
                            op: starts with
                            path: event/EVENT/EventData/PipeName
                            value: \wkssvc
                          - case sensitive: false
                            op: starts with
                            path: event/EVENT/EventData/PipeName
                            value: \windows.update.manager
                          - case sensitive: false
                            op: starts with
                            path: event/EVENT/EventData/PipeName
                            value: \SearchTextHarvester
                          - case sensitive: false
                            op: starts with
                            path: event/EVENT/EventData/PipeName
                            value: \DserNamePipe
                          - case sensitive: false
                            op: starts with
                            path: event/EVENT/EventData/PipeName
                            value: \PGMessagePipe
                          - case sensitive: false
                            op: starts with
                            path: event/EVENT/EventData/PipeName
                            value: \MsFteWds
                          - case sensitive: false
                            op: starts with
                            path: event/EVENT/EventData/PipeName
                            value: \fullduplex_
                          - case sensitive: false
                            op: starts with
                            path: event/EVENT/EventData/PipeName
                            value: \rpc_
                        - op: or
                          rules:
                          - case sensitive: false
                            op: is
                            path: event/EVENT/EventData/PipeName
                            value: \demoagent_11
                          - case sensitive: false
                            op: is
                            path: event/EVENT/EventData/PipeName
                            value: \demoagent_22
                        - op: matches
                          path: event/EVENT/EventData/PipeName
                          re: \\f4c3[0-9a-f]{2}$
                        - op: matches
                          path: event/EVENT/EventData/PipeName
                          re: \\f53f[0-9a-f]{2}$
                        - op: and
                          rules:
                          - case sensitive: false
                            op: starts with
                            path: event/EVENT/EventData/PipeName
                            value: \Winsock2\CatalogChangeListener-
                          - case sensitive: false
                            op: ends with
                            path: event/EVENT/EventData/PipeName
                            value: -0,
                respond:
                    - action: report
                      name: CobaltStrike Named Pipe Patterns
                      metadata:
                        tags:
                        - attack.defense_evasion
                        - attack.privilege_escalation
                        - attack.t1055
                        description: Detects the creation of a named pipe with a pattern found in CobaltStrike malleable C2 profiles
                        status: stable
                        id: 29206f7e-21fd-448a-9723-5f3272f22eba
                        references:
                        - https://svch0st.medium.com/guide-to-named-pipes-and-hunting-for-cobalt-strike-pipes-dc46b2c5f575
                        - https://gist.github.com/MHaggis/6c600e524045a6d49c35291a21e10752
                        level: medium
                        author: Florian Roth, Christian Burkard
                        falsepositives:
                        - Chrome instances using the exact same pipe name "mojo.something"
                        logsource: LimaCharlie
                tests:
                    match:
                      # Test 1: CobaltStrike mojo pipe pattern
                      - - event:
                            EVENT:
                              EventData:
                                EventType: CreatePipe
                                Image: C:\Windows\system32\rundll32.exe
                                PipeName: \mojo.5688.8052.183894939787088877
                                ProcessGuid: "{a6385ccd-7fc6-6850-1702-000000001700}"
                                ProcessId: "1234"
                                RuleName: "-"
                                User: NT AUTHORITY\SYSTEM
                                UtcTime: "2025-06-17 18:00:00.000"
                              System:
                                Channel: Microsoft-Windows-Sysmon/Operational
                                Computer: testhost.domain.com
                                EventID: "17"
                                _event_id: "17"
                          routing:
                            event_type: WEL
                            hostname: testhost
                      # Test 2: CobaltStrike demoagent pipe
                      - - event:
                            EVENT:
                              EventData:
                                EventType: ConnectPipe
                                Image: C:\Windows\explorer.exe
                                PipeName: \demoagent_11
                                ProcessGuid: "{a6385ccd-7fc6-6850-1702-000000001700}"
                                ProcessId: "5678"
                                RuleName: "-"
                                User: DOMAIN\user
                                UtcTime: "2025-06-17 18:01:00.000"
                              System:
                                Channel: Microsoft-Windows-Sysmon/Operational
                                Computer: testhost.domain.com
                                EventID: "18"
                                _event_id: "18"
                          routing:
                            event_type: WEL
                            hostname: testhost
                      # Test 3: Regex pattern f4c3
                      - - event:
                            EVENT:
                              EventData:
                                EventType: CreatePipe
                                Image: C:\temp\malicious.exe
                                PipeName: \f4c3ab
                                ProcessGuid: "{a6385ccd-7fc6-6850-1702-000000001700}"
                                ProcessId: "9999"
                                RuleName: "-"
                                User: DOMAIN\user
                                UtcTime: "2025-06-17 18:02:00.000"
                              System:
                                Channel: Microsoft-Windows-Sysmon/Operational
                                Computer: testhost.domain.com
                                EventID: "17"
                                _event_id: "17"
                          routing:
                            event_type: WEL
                            hostname: testhost
                      # Test 4: Winsock2 CatalogChangeListener pattern
                      - - event:
                            EVENT:
                              EventData:
                                EventType: ConnectPipe
                                Image: C:\Windows\system32\svchost.exe
                                PipeName: \Winsock2\CatalogChangeListener-123-0,
                                ProcessGuid: "{a6385ccd-7fc6-6850-1702-000000001700}"
                                ProcessId: "1111"
                                RuleName: "-"
                                User: NT AUTHORITY\SYSTEM
                                UtcTime: "2025-06-17 18:03:00.000"
                              System:
                                Channel: Microsoft-Windows-Sysmon/Operational
                                Computer: testhost.domain.com
                                EventID: "18"
                                _event_id: "18"
                          routing:
                            event_type: WEL
                            hostname: testhost
                    non_match:
                      # Test 1: SearchIndexer.exe using legitimate pipe NOT in detection patterns
                      - - event:
                            EVENT:
                              EventData:
                                EventType: ConnectPipe
                                Image: C:\WINDOWS\system32\SearchIndexer.exe
                                PipeName: \SearchFilterHost
                                ProcessGuid: "{a6385ccd-7fc6-6850-1702-000000001700}"
                                ProcessId: "11816"
                                RuleName: "-"
                                User: NT AUTHORITY\SYSTEM
                                UtcTime: "2025-06-16 20:42:20.099"
                              System:
                                Channel: Microsoft-Windows-Sysmon/Operational
                                Computer: workstation01.example.com
                                EventID: "18"
                                _event_id: "18"
                          routing:
                            event_type: WEL
                            hostname: workstation01
                      # Test 2: Different event channel (not Sysmon)
                      - - event:
                            EVENT:
                              EventData:
                                PipeName: \mojo.5688.8052.183894939787088877
                              System:
                                Channel: Security
                                EventID: "18"
                                _event_id: "18"
                          routing:
                            event_type: WEL
                            hostname: testhost
                      # Test 3: Wrong event ID (not 17 or 18)
                      - - event:
                            EVENT:
                              EventData:
                                PipeName: \demoagent_11
                              System:
                                Channel: Microsoft-Windows-Sysmon/Operational
                                EventID: "1"
                                _event_id: "1"
                          routing:
                            event_type: WEL
                            hostname: testhost
                      # Test 4: Legitimate Windows pipe not in detection patterns
                      - - event:
                            EVENT:
                              EventData:
                                EventType: ConnectPipe
                                Image: C:\Windows\system32\lsass.exe
                                PipeName: \lsass
                                ProcessGuid: "{a6385ccd-7fc6-6850-1702-000000001700}"
                                ProcessId: "700"
                                RuleName: "-"
                                User: NT AUTHORITY\SYSTEM
                                UtcTime: "2025-06-17 18:05:00.000"
                              System:
                                Channel: Microsoft-Windows-Sysmon/Operational
                                Computer: testhost.domain.com
                                EventID: "18"
                                _event_id: "18"
                          routing:
                            event_type: WEL
                            hostname: testhost
                      # Test 5: Non-WEL event type
                      - - event:
                            PROCESS_ID: 1234
                            FILE_PATH: \Device\NamedPipe\mojo.test
                          routing:
                            event_type: NEW_NAMED_PIPE
                            hostname: testhost
            usr_mtd:
                enabled: true
                expiry: 0
                tags: []
                comment: "Detects the creation of a named pipe with a pattern found in CobaltStrike malleable C2 profiles"
```