# Hybrid Analysis

Hybrid Analysis, aka Falcon Sandbox, is a powerful, free malware analysis service for the community that detects and analyzes unknown threats. Hybrid Analysis has its own unique approach, and offers both public-facing and private team-based sandboxing capabilities.

LimaCharlie integrates with the following Hybrid Analysis API calls:

* [Overview](https://www.hybrid-analysis.com/docs/api/v2#/Analysis%20Overview/get_overview__sha256_)
* [Search](https://www.hybrid-analysis.com/docs/api/v2#/Search/post_search_hash)

## Detection & Response Rules

### Overview

The Search API accepts a SHA256 value, and provides an extensive overview of a hash (if previously observed by the platform).

**Rule:**

The following D&R rule

```
event: NEW_PROCESS
op: lookup
path: event/HASH
resource: hive://lookup/hybrid-analysis-overview
```

**Response Data:**

```
{
  "result": {
    "analysis_start_time": "2023-07-17T18:31:04+00:00",
    "architecture": "WINDOWS",
    "children_in_progress": 0,
    "children_in_queue": 0,
    "last_file_name": "cmd.exe",
    "last_multi_scan": "2023-07-17T18:31:09+00:00",
    "multiscan_result": 0,
    "other_file_name": [
      "Utilman.exe",
      "file",
      "kiss.exe",
      "osk.exe",
      "sethc.exe",
      "utilman.exe"
    ],
    "related_children_hashes": [],
    "related_parent_hashes": [
      "c502bd80423e10dcc4b59fe4b523acb5ce0bd07748f73c7bdc6c797883b8a417"
    ],
    "related_reports": [
      {
        "environment_id": 100,
        "error_origin": null,
        "error_type": null,
        "job_id": "627e3011d695730f2c3ad419",
        "sha256": "c502bd80423e10dcc4b59fe4b523acb5ce0bd07748f73c7bdc6c797883b8a417",
        "state": "SUCCESS",
        "verdict": "no verdict"
      }
    ],
    "reports": [
      "58593319aac2edc56d351531",
      "5a34f2a27ca3e13531789a95",
      "5f196598eac13102deff3d42",
      "64b588e7e14d64e6a60b2130",
      "5965d8027ca3e10ec737634f",
      "60251a499b1b3016bb674fb4",
      "637f3600a3d94f1ecc7c1800"
    ],
    "scanners": [
      {
        "anti_virus_results": [],
        "error_message": null,
        "name": "CrowdStrike Falcon Static Analysis (ML)",
        "percent": 0,
        "positives": null,
        "progress": 100,
        "status": "clean",
        "total": null
      },
      {
        "anti_virus_results": [],
        "error_message": null,
        "name": "Metadefender",
        "percent": 0,
        "positives": 0,
        "progress": 100,
        "status": "clean",
        "total": 27
      },
      {
        "anti_virus_results": [],
        "error_message": null,
        "name": "VirusTotal",
        "percent": 0,
        "positives": 0,
        "progress": 100,
        "status": "clean",
        "total": 75
      }
    ],
    "scanners_v2": {
      "bfore_ai": null,
      "clean_dns": null,
      "crowdstrike_ml": {
        "anti_virus_results": [],
        "error_message": null,
        "name": "CrowdStrike Falcon Static Analysis (ML)",
        "percent": 0,
        "progress": 100,
        "status": "clean"
      },
      "metadefender": {
        "anti_virus_results": [],
        "error_message": null,
        "name": "Metadefender",
        "percent": 0,
        "positives": 0,
        "progress": 100,
        "status": "clean",
        "total": 27
      },
      "scam_adviser": null,
      "urlscan_io": null,
      "virustotal": {
        "error_message": null,
        "name": "VirusTotal",
        "percent": 0,
        "positives": 0,
        "progress": 100,
        "status": "clean",
        "total": 75
      }
    },
    "sha256": "935c1861df1f4018d698e8b65abfa02d7e9037d8f68ca3c2065b6ca165d44ad2",
    "size": 232960,
    "submit_context": [],
    "tags": [],
    "threat_score": null,
    "type": "PE32+ executable (console) x86-64, for MS Windows",
    "type_short": [
      "peexe",
      "64bits",
      "executable"
    ],
    "url_analysis": false,
    "verdict": "no specific threat",
    "vx_family": null,
    "whitelisted": false
  }
}
```

### Search

The Search lookup provides a basic lookup of a hash value. This look accepts one of the following values:

* MD5
* SHA1
* SHA256

**D&R Rule:**

```
event: NEW_PROCESS
op: lookup
path: event/HASH
resource: hive://lookup/hybrid-analysis-search
```

**Response Data:**

```
[
  {
    "classification_tags": [],
    "tags": [],
    "submissions": [
      {
        "submission_id": "64b588e7e14d64e6a60b2131",
        "filename": "cmd.exe",
        "url": null,
        "created_at": "2023-07-17T18:31:03+00:00"
      }
    ],
    "machine_learning_models": [],
    "crowdstrike_ai": {
      "executable_process_memory_analysis": [],
      "analysis_related_urls": []
    },
    "job_id": "64b588e7e14d64e6a60b2130",
    "environment_id": 160,
    "environment_description": "Windows 10 64 bit",
    "size": 232960,
    "type": "PE32+ executable (console) x86-64, for MS Windows",
    "type_short": [
      "peexe",
      "64bits",
      "executable"
    ],
    "target_url": null,
    "state": "SUCCESS",
    "error_type": null,
    "error_origin": null,
    "submit_name": "cmd.exe",
    "md5": "f4f684066175b77e0c3a000549d2922c",
    "sha1": "99ae9c73e9bee6f9c76d6f4093a9882df06832cf",
    "sha256": "935c1861df1f4018d698e8b65abfa02d7e9037d8f68ca3c2065b6ca165d44ad2",
    "sha512": "fe8f0593cc335ad28eb90211bc4ff01a3d2992cffb3877d04cefede9ef94afeb1a7d7874dd0c0ae04eaf8308291d5a4d879e6ecf6fe2b8d0ff1c3ac7ef143206",
    "ssdeep": "3072:bkd4COZG6/A1tO1Y6TbkX2FtynroeJ/MEJoSsasbLLkhyjyGe:bkuC9+Af0Y6TbbFtkoeJk1KsfLXm",
    "imphash": "3062ed732d4b25d1c64f084dac97d37a",
    "entrypoint": "0x140015190",
    "entrypoint_section": ".text",
    "image_base": "0x140000000",
    "subsystem": "Windows Cui",
    "image_file_characteristics": [
      "EXECUTABLE_IMAGE",
      "LARGE_ADDRESS_AWARE"
    ],
    "dll_characteristics": [
      "GUARD_CF",
      "TERMINAL_SERVER_AWARE",
      "DYNAMIC_BASE",
      "NX_COMPAT",
      "HIGH_ENTROPY_VA"
    ],
    "major_os_version": 10,
    "minor_os_version": 0,
    "av_detect": 0,
    "vx_family": null,
    "url_analysis": false,
    "analysis_start_time": "2023-07-17T18:31:04+00:00",
    "threat_score": null,
    "interesting": false,
    "threat_level": 0,
    "verdict": "no specific threat",
    "certificates": [],
    "is_certificates_valid": false,
    "certificates_validation_message": "No signature was present in the subject. (0x800b0100)",
    "domains": [],
    "compromised_hosts": [],
    "hosts": [],
    "total_network_connections": 0,
    "total_processes": 1,
    "total_signatures": 99,
    "extracted_files": [],
    "file_metadata": null,
    "processes": [],
    "mitre_attcks": [
      ...
    ]
  }
]
```