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