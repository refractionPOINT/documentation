# YARA Syntax Reference

Complete reference for YARA rule syntax in LimaCharlie.

**See also:**
- [SKILL.md](./SKILL.md): Overview and quick start
- [EXAMPLES.md](./EXAMPLES.md): Complete rule examples
- [TROUBLESHOOTING.md](./TROUBLESHOOTING.md): Performance and debugging

---

## Rule Declaration

### Basic Structure

```yara
rule RuleName
{
    meta:
        // Metadata section

    strings:
        // Strings section

    condition:
        // Condition section
}
```

### Rule Identifier Rules

- Must start with a letter (a-z, A-Z)
- Can contain letters, numbers, and underscores
- Cannot exceed 128 characters
- Case-sensitive
- Cannot use YARA reserved keywords

### Multiple Rules in One File

```yara
rule FirstRule
{
    strings:
        $s1 = "first"
    condition:
        $s1
}

rule SecondRule
{
    strings:
        $s2 = "second"
    condition:
        $s2
}
```

---

## Metadata Section

The metadata section provides context about the rule but does not affect matching logic.

### Syntax

```yara
meta:
    key1 = "string value"
    key2 = 123
    key3 = true
```

### Supported Types

**Strings:**
```yara
meta:
    description = "Detects Emotet malware"
    author = "Security Team"
    reference = "https://example.com/threat-intel"
```

**Integers:**
```yara
meta:
    version = 1
    confidence = 90
```

**Booleans:**
```yara
meta:
    in_the_wild = true
    active = false
```

### Common Metadata Fields

```yara
meta:
    description = "What this rule detects"
    author = "Your Name or Team"
    date = "2025-01-15"
    version = "1.0"
    reference = "URL to threat intelligence"
    hash = "SHA256 hash of sample"
    severity = "critical|high|medium|low"
    mitre_attack = "T1059.001"
    tlp = "white|green|amber|red"
    confidence = 90
    in_the_wild = true
    malware_family = "Emotet"
```

---

## Strings Section

### Text Strings

**Basic syntax:**
```yara
strings:
    $string_name = "text to match"
```

**String modifiers:**

**nocase** - Case-insensitive matching:
```yara
strings:
    $text = "malicious" nocase
    // Matches: malicious, MALICIOUS, MaLiCiOuS, etc.
```

**wide** - Match wide-character (UTF-16) strings:
```yara
strings:
    $wide_text = "malware" wide
    // Matches: m\x00a\x00l\x00w\x00a\x00r\x00e\x00
```

**ascii** - Match ASCII strings (default):
```yara
strings:
    $ascii_text = "malware" ascii
```

**Both ASCII and wide:**
```yara
strings:
    $both = "malware" wide ascii
    // Matches both ASCII and UTF-16 versions
```

**fullword** - Match only if not preceded/followed by alphanumeric characters:
```yara
strings:
    $word = "cmd" fullword
    // Matches: "cmd", " cmd ", "cmd.exe"
    // Does NOT match: "command", "scmd"
```

**xor** - Match strings encrypted with single-byte XOR:
```yara
strings:
    $xor_string = "malicious" xor
    // Matches string XORed with any single-byte key
```

**XOR with specific key range:**
```yara
strings:
    $xor_range = "malicious" xor(0x01-0xff)
    // XOR keys from 0x01 to 0xff
```

**Combining modifiers:**
```yara
strings:
    $combo = "malware" nocase wide ascii fullword
```

### Hexadecimal Strings

**Basic hex string:**
```yara
strings:
    $hex = { 6A 40 68 00 30 00 00 }
```

**Wildcards:**

**Single nibble wildcard (?)**:
```yara
strings:
    $hex_wild = { E? 00 00 00 00 }
    // E0, E1, E2, ... EF all match
```

**Byte wildcard (??):**
```yara
strings:
    $hex_byte = { 6A ?? 68 }
    // Any byte in the middle position
```

**Variable-length gaps:**

**Fixed range [min-max]:**
```yara
strings:
    $gap1 = { F4 23 [4-6] 62 B4 }
    // 4 to 6 bytes between F4 23 and 62 B4
```

**Minimum bytes [min-]:**
```yara
strings:
    $gap2 = { F4 23 [10-] 62 B4 }
    // 10 or more bytes between
```

**Unlimited bytes [-]:**
```yara
strings:
    $gap3 = { F4 23 [-] 62 B4 }
    // Any number of bytes between
```

**Exact number of bytes [n]:**
```yara
strings:
    $gap4 = { F4 23 [8] 62 B4 }
    // Exactly 8 bytes between
```

**Alternatives (OR):**
```yara
strings:
    $alt = { ( 01 02 | 03 04 ) }
    // Matches either 01 02 OR 03 04
```

**Common patterns:**

**PE header:**
```yara
strings:
    $pe_header = { 4D 5A }
    // "MZ" header
```

**ELF header:**
```yara
strings:
    $elf_header = { 7F 45 4C 46 }
    // "\x7FELF"
```

**PDF header:**
```yara
strings:
    $pdf_header = { 25 50 44 46 }
    // "%PDF"
```

### Regular Expressions

**Basic syntax:**
```yara
strings:
    $regex = /pattern/
```

**Modifiers:**

**i - Case insensitive:**
```yara
strings:
    $regex_nocase = /malware/i
    // Matches: malware, MALWARE, MaLwArE
```

**s - Dot matches newline:**
```yara
strings:
    $regex_dotall = /start.*end/s
    // . can match newline characters
```

**Common patterns:**

**MD5 hash:**
```yara
strings:
    $md5 = /md5: [0-9a-fA-F]{32}/
```

**SHA256 hash:**
```yara
strings:
    $sha256 = /sha256: [0-9a-fA-F]{64}/
```

**URL pattern:**
```yara
strings:
    $url = /https?:\/\/[a-z0-9.-]+\.[a-z]{2,}/i
```

**Email address:**
```yara
strings:
    $email = /[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}/i
```

**IPv4 address:**
```yara
strings:
    $ipv4 = /\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/
```

**Windows file path:**
```yara
strings:
    $winpath = /[A-Z]:\\[^:*?"<>|]+/i
```

---

## Condition Section

The condition defines the logic that determines if a rule matches.

### String Matching

**Basic string reference:**
```yara
condition:
    $string1                    // String must appear
```

**Boolean operators:**
```yara
condition:
    $string1 and $string2      // Both must appear
    $string1 or $string2       // Either must appear
    not $string1               // String must NOT appear
```

**Grouping with parentheses:**
```yara
condition:
    ($string1 or $string2) and not $string3
```

### Counting Strings

**Count of specific string:**
```yara
condition:
    #string1 > 5               // Appears more than 5 times
    #string1 == 3              // Appears exactly 3 times
    #string1 >= 10             // Appears 10 or more times
```

**Wildcard counting:**
```yara
condition:
    #string* > 10              // All strings matching $string* appear more than 10 times total
```

### Set Operations

**All strings:**
```yara
condition:
    all of them                // All defined strings must appear
```

**Any string:**
```yara
condition:
    any of them                // At least one string must appear
```

**Specific count:**
```yara
condition:
    2 of them                  // At least 2 strings must appear
    3 of ($text*)              // At least 3 strings matching $text*
```

**Percentage:**
```yara
condition:
    50% of them                // At least 50% of strings must appear
```

**Range:**
```yara
condition:
    2 of them in (0..1024)     // At least 2 strings in first 1024 bytes
```

**Wildcard sets:**
```yara
condition:
    all of ($text*)            // All strings starting with $text
    any of ($hex*)             // Any string starting with $hex
    3 of ($malware_*)          // At least 3 strings starting with $malware_
```

**Specific sets:**
```yara
condition:
    all of ($a, $b, $c)        // All of these specific strings
    any of ($a, $b, $c)        // Any of these specific strings
    2 of ($a, $b, $c, $d)      // At least 2 of these strings
```

### Position-Based Conditions

**String at specific offset:**
```yara
condition:
    $string at 0               // String at file offset 0
    $string at 100             // String at file offset 100
```

**String in range:**
```yara
condition:
    $string in (0..1024)       // String in first 1024 bytes
    $string in (100..200)      // String between offsets 100 and 200
```

**First occurrence position:**
```yara
condition:
    @string < 100              // First occurrence at offset < 100
    @string[1] < 100           // First occurrence
    @string[2] > 1000          // Second occurrence at offset > 1000
```

**Last occurrence position:**
```yara
condition:
    @string[#string] > 5000    // Last occurrence after offset 5000
```

### File Size Conditions

**Basic file size:**
```yara
condition:
    filesize < 1MB
    filesize > 500KB
    filesize == 1024
```

**Size units:**
- `KB` or `KiB` - Kilobytes (1024 bytes)
- `MB` or `MiB` - Megabytes (1024 KB)
- `GB` or `GiB` - Gigabytes (1024 MB)

**Range:**
```yara
condition:
    filesize > 500KB and filesize < 2MB
```

### Magic Bytes and Headers

**uint16(offset)** - Read 2-byte unsigned integer:
```yara
condition:
    uint16(0) == 0x5A4D        // PE header "MZ"
```

**uint32(offset)** - Read 4-byte unsigned integer:
```yara
condition:
    uint32(0) == 0x464C457F    // ELF header
```

**uint8(offset)** - Read 1-byte unsigned integer:
```yara
condition:
    uint8(0) == 0x4D           // First byte is 'M'
```

**Common file headers:**
```yara
condition:
    uint16(0) == 0x5A4D        // PE (MZ)
    uint32(0) == 0x464C457F    // ELF
    uint32(0) == 0x46445025    // PDF (%PDF)
    uint16(0) == 0xCFFA        // Mach-O (32-bit)
    uint32(0) == 0xFEEDFACE    // Mach-O (64-bit)
```

### Entry Point

**at entrypoint** - Check if string is at entry point:
```yara
condition:
    $code at entrypoint
```

**Note:** Entry point detection requires PE file structure.

### Arithmetic and Comparison

**Operators:**
- `+` Addition
- `-` Subtraction
- `*` Multiplication
- `\` Division
- `%` Modulus
- `==` Equal
- `!=` Not equal
- `<` Less than
- `>` Greater than
- `<=` Less than or equal
- `>=` Greater than or equal

**Examples:**
```yara
condition:
    filesize > 1000 and filesize < 2000
    #string1 * 2 > #string2
    (@string1 + 100) < 1000
```

### Bitwise Operations

**Operators:**
- `&` Bitwise AND
- `|` Bitwise OR
- `^` Bitwise XOR
- `~` Bitwise NOT
- `<<` Left shift
- `>>` Right shift

**Examples:**
```yara
condition:
    uint8(0) & 0x80 == 0x80    // Check if bit 7 is set
    uint16(0) | 0x0001         // Bitwise OR
```

### String Length

**!string** - Length of string match:
```yara
condition:
    !string1 > 50              // First match of $string1 is longer than 50 bytes
    !string1[2] < 100          // Second match is shorter than 100 bytes
```

### Complex Conditions

**Combining multiple criteria:**
```yara
condition:
    (uint16(0) == 0x5A4D) and              // PE file
    filesize < 2MB and                      // Less than 2MB
    (2 of ($string*)) and                   // At least 2 strings
    (any of ($hex*)) and                    // Any hex pattern
    (@suspicious < 1024)                    // Suspicious string in first 1KB
```

**Nested conditions:**
```yara
condition:
    (
        (uint16(0) == 0x5A4D and filesize < 1MB) or
        (uint32(0) == 0x464C457F and filesize < 500KB)
    ) and
    any of them
```

### Rule References

**Reference other rules:**
```yara
rule Rule1
{
    strings:
        $a = "suspicious"
    condition:
        $a
}

rule Rule2
{
    strings:
        $b = "malicious"
    condition:
        Rule1 and $b          // Both Rule1 and $b must match
}
```

---

## Functions and Modules

### Built-in Functions

**defined(expression)** - Check if expression is defined:
```yara
condition:
    defined pe.entry_point
```

### Math Module

**math.entropy(offset, size)** - Calculate entropy:
```yara
import "math"

condition:
    math.entropy(0, filesize) > 7.5    // High entropy (possible encryption)
```

**math.mean(offset, size)** - Calculate mean:
```yara
import "math"

condition:
    math.mean(0, filesize) > 128
```

**math.min(offset, size)** - Minimum byte value:
```yara
import "math"

condition:
    math.min(0, 100) == 0
```

**math.max(offset, size)** - Maximum byte value:
```yara
import "math"

condition:
    math.max(0, 100) == 255
```

### PE Module

**Import PE module:**
```yara
import "pe"
```

**PE characteristics:**
```yara
condition:
    pe.is_pe                           // Is a PE file
    pe.is_32bit()                      // 32-bit PE
    pe.is_64bit()                      // 64-bit PE
    pe.is_dll()                        // Is a DLL
```

**PE sections:**
```yara
condition:
    pe.number_of_sections > 3
    pe.sections[0].name == ".text"
    pe.sections[0].characteristics & 0x20000000  // Section is executable
```

**PE imports:**
```yara
condition:
    pe.imports("kernel32.dll", "CreateRemoteThread")
    pe.number_of_imports > 10
```

**PE exports:**
```yara
condition:
    pe.exports("ServiceMain")
```

**PE timestamp:**
```yara
condition:
    pe.timestamp > 1640000000          // After certain date
```

### ELF Module

**Import ELF module:**
```yara
import "elf"
```

**ELF properties:**
```yara
condition:
    elf.type == elf.ET_EXEC            // Executable
    elf.machine == elf.EM_X86_64       // x86-64 architecture
    elf.number_of_sections > 5
```

---

## Advanced Patterns

### For Loops

**for any/all:**
```yara
condition:
    for any i in (0..pe.number_of_sections): (
        pe.sections[i].name == ".text"
    )
```

**For all sections:**
```yara
condition:
    for all i in (0..pe.number_of_sections): (
        pe.sections[i].characteristics & 0x20000000
    )
```

**For specific count:**
```yara
condition:
    for 2 i in (0..pe.number_of_sections): (
        pe.sections[i].name contains "data"
    )
```

### String Iteration

**Iterate over string occurrences:**
```yara
condition:
    for any i in (1..#string): (
        @string[i] > 1000
    )
```

---

## Best Practices

### Performance Optimization

1. **Check fast conditions first:**
```yara
condition:
    uint16(0) == 0x5A4D and        // Fast: header check
    filesize < 2MB and              // Fast: file size
    2 of ($string*)                 // Slower: string matching
```

2. **Use specific strings:**
```yara
strings:
    $specific = "UNIQUE_MALWARE_STRING_12345"  // Good
    $generic = "Windows"                        // Avoid
```

3. **Use fullword for common terms:**
```yara
strings:
    $cmd = "cmd" fullword          // Prevents matching "command"
```

4. **Limit file size:**
```yara
condition:
    filesize < 5MB and
    // ... other conditions
```

### Avoiding False Positives

1. **Require multiple indicators:**
```yara
condition:
    uint16(0) == 0x5A4D and        // Is PE file
    filesize < 1MB and              // Reasonable size
    3 of ($string*) and             // Multiple strings match
    any of ($hex*)                  // And hex pattern matches
```

2. **Use file type checks:**
```yara
condition:
    uint16(0) == 0x5A4D and        // Ensure it's a PE file first
    $suspicious_string
```

3. **Add exclusions:**
```yara
condition:
    (all of ($malware*)) and
    not (any of ($legitimate*))
```

### Rule Maintenance

1. **Version your rules:**
```yara
meta:
    version = "1.2"
    changelog = "Added detection for new variant"
```

2. **Document your logic:**
```yara
condition:
    // Check for PE header
    uint16(0) == 0x5A4D and
    // File size between 100KB and 2MB
    filesize > 100KB and filesize < 2MB and
    // Require at least 3 suspicious strings
    3 of ($suspicious*)
```

3. **Use descriptive names:**
```yara
strings:
    $network_beacon = "User-Agent: Mozilla/5.0"
    $persistence_registry = "Software\\Microsoft\\Windows\\CurrentVersion\\Run"
```

---

## Quick Reference

### String Modifiers
- `nocase` - Case-insensitive
- `wide` - UTF-16 encoding
- `ascii` - ASCII encoding (default)
- `fullword` - Word boundaries
- `xor` - Single-byte XOR encryption

### Hex Wildcards
- `??` - Any byte
- `?` - Any nibble (half-byte)
- `[n]` - Exactly n bytes
- `[n-m]` - Between n and m bytes
- `[n-]` - n or more bytes
- `[-]` - Unlimited bytes

### Regex Modifiers
- `i` - Case-insensitive
- `s` - Dot matches newline

### Condition Operators
- `and`, `or`, `not` - Boolean logic
- `==`, `!=`, `<`, `>`, `<=`, `>=` - Comparison
- `+`, `-`, `*`, `\`, `%` - Arithmetic
- `&`, `|`, `^`, `~`, `<<`, `>>` - Bitwise

### Set Operations
- `all of them` - All strings
- `any of them` - At least one string
- `2 of them` - At least 2 strings
- `50% of them` - At least 50% of strings
- `all of ($text*)` - All strings matching pattern

### Special Variables
- `filesize` - Size of file being scanned
- `entrypoint` - Entry point offset (PE files)
- `@string` - First occurrence offset
- `#string` - Count of occurrences
- `!string` - Length of match

---

For complete examples using this syntax, see [EXAMPLES.md](./EXAMPLES.md).
