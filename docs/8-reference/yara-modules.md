# YARA Modules & External Variables

LimaCharlie bundles [YARA 4.2.3](https://yara.readthedocs.io/en/v4.2.3/) in the endpoint sensor. In addition to the core YARA language, the sensor makes several standard YARA modules and a set of custom external string variables available to every rule.

## Modules

The following standard YARA modules are compiled into the sensor on **all platforms** (Windows, macOS, Linux):

| Module | Description | Documentation |
|--------|-------------|---------------|
| `pe` | Parse and inspect Windows PE (Portable Executable) files — headers, imports, exports, resources, signatures, imphash, and more. | [pe module](https://yara.readthedocs.io/en/v4.2.3/modules/pe.html) |
| `elf` | Parse and inspect ELF (Executable and Linkable Format) binaries — headers, sections, segments, and symbol tables. | [elf module](https://yara.readthedocs.io/en/v4.2.3/modules/elf.html) |
| `hash` | Compute cryptographic hashes (MD5, SHA-1, SHA-256), CRC32 checksums, and 32-bit checksums over data ranges within a scanned file. | [hash module](https://yara.readthedocs.io/en/v4.2.3/modules/hash.html) |
| `math` | Mathematical and statistical functions — entropy, deviation, mean, serial correlation, Monte Carlo Pi estimation, and more. | [math module](https://yara.readthedocs.io/en/v4.2.3/modules/math.html) |
| `time` | Access the current time. Provides `time.now()` which returns the current Unix timestamp. | [time module](https://yara.readthedocs.io/en/v4.2.3/modules/time.html) |
| `console` | Print debug messages during rule evaluation via `console.log()`. Useful when developing and testing rules. | [console module](https://yara.readthedocs.io/en/v4.2.3/modules/console.html) |

> **Note:** Modules such as `dotnet`, `cuckoo`, `macho`, and `dex` are **not** enabled in the sensor build.

## External Variables

The sensor defines the following **string** external variables that are automatically populated at scan time. You can reference them in your rule conditions without any additional configuration.

| Variable | Type | Description | Platform Notes |
|----------|------|-------------|----------------|
| `filename` | string | Base name of the file being scanned (e.g. `suspicious.exe`). | All platforms |
| `filepath` | string | Full path of the file being scanned (e.g. `/home/user/suspicious.exe`). | All platforms |
| `extension` | string | File extension extracted from the file name (e.g. `exe`). | All platforms |
| `filetype` | string | Reserved for future use. Currently always empty. | — |
| `owner` | string | OS user name that owns the file. Resolved from the file's UID via `getpwuid`. | Linux, macOS only. Empty on Windows. |
| `md5` | string | Reserved for future use. Currently always empty. | — |

### Example

```yara
rule SuspiciousScript
{
    condition:
        extension == "ps1" and
        owner != "root"
}

rule MalwareInTemp
{
    strings:
        $mz = { 4D 5A }
    condition:
        $mz at 0 and
        filepath matches /\/tmp\// and
        math.entropy(0, filesize) > 7.0
}

import "pe"
import "hash"

rule SignedButSuspicious
{
    condition:
        pe.number_of_signatures > 0 and
        hash.sha256(0, filesize) == "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
}
```

### Usage Notes

- External variables are only populated during **file scans**. When scanning process memory, `filename`, `filepath`, `extension`, and `owner` will be empty strings.
- The `filetype` and `md5` variables are defined for forward compatibility. Rules referencing them will compile, but they will match only against empty strings until a future sensor release populates them.
- All external variables are strings. Use string comparison operators (`==`, `!=`, `matches`, `contains`, `startswith`, `endswith`) in your conditions.
