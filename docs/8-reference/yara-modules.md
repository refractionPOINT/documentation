# YARA Modules & External Variables

LimaCharlie includes [YARA 4.2.3](https://yara.readthedocs.io/en/v4.2.3/) in the endpoint sensor. The sensor gives every rule the core YARA language, several standard YARA modules, and a set of custom external string variables.

## Modules

The sensor build includes these standard YARA modules on **all platforms** (Windows, macOS, Linux):

| Module | Description | Documentation |
|--------|-------------|---------------|
| `pe` | Parse and inspect Windows PE (Portable Executable) files — headers, imports, exports, resources, signatures, imphash, and more. | [pe module](https://yara.readthedocs.io/en/v4.2.3/modules/pe.html) |
| `elf` | Parse and inspect ELF (Executable and Linkable Format) binaries — headers, sections, segments, and symbol tables. | [elf module](https://yara.readthedocs.io/en/v4.2.3/modules/elf.html) |
| `hash` | Compute cryptographic hashes (MD5, SHA-1, SHA-256), CRC32 checksums, and 32-bit checksums over data ranges within a scanned file. | [hash module](https://yara.readthedocs.io/en/v4.2.3/modules/hash.html) |
| `math` | Mathematical and statistical functions — entropy, deviation, mean, serial correlation, Monte Carlo Pi estimation, and more. | [math module](https://yara.readthedocs.io/en/v4.2.3/modules/math.html) |
| `time` | Access the current time. `time.now()` returns the current Unix timestamp. | [time module](https://yara.readthedocs.io/en/v4.2.3/modules/time.html) |
| `console` | Print debug messages with `console.log()` while a rule runs. This is useful when you develop and test rules. | [console module](https://yara.readthedocs.io/en/v4.2.3/modules/console.html) |

> **Note:** Modules such as `dotnet`, `cuckoo`, `macho`, and `dex` are **not** enabled in the sensor build.

## External Variables

The sensor defines these **string** external variables and fills them at scan time. You can use them in your rule conditions with no more configuration.

| Variable | Type | Description | Platform Notes |
|----------|------|-------------|----------------|
| `filename` | string | Base name of the scanned file (e.g. `suspicious.exe`). | All platforms |
| `filepath` | string | Full path of the scanned file (e.g. `/home/user/suspicious.exe`). | All platforms |
| `extension` | string | File extension from the file name (e.g. `exe`). | All platforms |
| `filetype` | string | Reserved for future use. Always empty now. | — |
| `owner` | string | OS user name that owns the file. `getpwuid` resolves it from the UID of the file. | Linux, macOS only. Empty on Windows. |
| `md5` | string | Reserved for future use. Always empty now. | — |

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

- The sensor fills external variables only during **file scans**. When the sensor scans process memory, `filename`, `filepath`, `extension`, and `owner` are empty strings.
- The `filetype` and `md5` variables exist for forward compatibility. A rule that refers to them compiles, but it matches only empty strings until a future sensor release fills them.
- All external variables are strings. Use string comparison operators (`==`, `!=`, `matches`, `contains`, `startswith`, `endswith`) in your conditions.
