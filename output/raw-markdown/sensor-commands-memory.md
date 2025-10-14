[![LimaCharlie](https://cdn.document360.io/logo/84ec2311-0e05-4c58-90b9-baa9c041d22b/a8f5c28d58ea4df0b59badd4cebcc541-Logo_Blue.png)](/)

* [LimaCharlie Log In](https://app.limacharlie.io)

* v1

  + [v1 Deprecated](/v1/docs "v1")
  + [v2](/docs "v2")

Contents x

* [Getting Started](what-is-limacharlie)
* [Telemetry](telemetry-sensors)
* [Detection and Response](detecting-related-events)
* [Platform Management](platform-configuration-limacharlie-sdk)
* [Outputs](output-whitelisting)
* [Add-Ons](developer-grant-program)
* [FAQ](faq-privacy)

[Powered by![Document360](https://cdn.document360.io/static/images/document360-logo.svg)](https://document360.com/powered-by-document360/?utm_source=docs&utm_medium=footer&utm_campaign=poweredbylogo)

---

Memory

* 14 Feb 2024
* 1 Minute to read

Share this

* Print
* Share
* Dark

  Light

Contents

This documentation version is deprecated, please click here for the latest version.

# Memory

* Updated on 14 Feb 2024
* 1 Minute to read

* Print
* Share
* Dark

  Light

---

Article summary

Did you find this summary helpful?

Thank you for your feedback!

The following sensor commands perform actions against memory on EDR sensors.

## get\_debug\_data

Retrieve debug data from the EDR sensor.

**Platforms:**

**Return Event:**
 [DEBUG\_DATA\_REP](/v1/docs/reference-events-responses-memory#DEBUG_DATA_REP)

## mem\_find\_handle

Find specific open handles in memory on Windows.

**Platforms:**

**Return Event:**
 [MEM\_FIND\_HANDLES\_REP](/v1/docs/reference-events-responses-memory#MEM_FIND_HANDLES_REP)

**Usage:**

```
mem_find_handle [-h] needle

positional arguments:
  needle      substring of the handle names to get
```

## mem\_find\_string

Find specific strings in memory.

**Platforms:**

**Return Event:**
 [MEM\_FIND\_STRING\_REP](/v1/docs/reference-events-responses-memory#MEM_FIND_STRING_REP)

**Due to recent changes in MacOS, this may be less reliable on that platform.**

**Usage:**

```
mem_find_string [-h] -s STRING [STRING ...] pid

positional arguments:
  pid                   pid of the process to search in, 0 for all processes

optional arguments:
  -s STRING [STRING ...], --strings STRING [STRING ...]
                        list of strings to look for
```

## mem\_handles

List all open handles from a process (or all) on Windows.

**Platforms:**

**Return Event:**
 [MEM\_HANDLES\_REP](/v1/docs/reference-events-responses-memory#MEM_HANDLES_REP)

**Usage:**

```
mem_handles [-h] [-p PID] [-a PROCESSATOM]

optional arguments:
  -p PID, --pid PID     pid of the process to get the handles from, 0 for all
                        processes
  -a PROCESSATOM, --processatom PROCESSATOM
                        the atom of the target process
```

## mem\_map

Display the map of memory pages from a process including size, access rights, etc.

**Platforms:**

**Return Event:**
 [MEM\_MAP\_REP](/v1/docs/reference-events-responses-memory#MEM_MAP_REP)

**Due to recent changes in MacOS, this may be less reliable on that platform.**

**Usage:**

```
mem_map [-h] [-p PID] [-a PROCESSATOM]

optional arguments:
  -p PID, --pid PID     pid of the process to get the map from
  -a PROCESSATOM, --processatom PROCESSATOM
                        the atom of the target proces
```

## mem\_read

Retrieve a chunk of memory from a process given a base address and size.

**Platforms:**

**Return Event:**
 [MEM\_READ\_REP](/v1/docs/reference-events-responses-memory#MEM_READ_REP)

**Due to recent changes in MacOS, this may be less reliable on that platform.**

**Usage:**

```
mem_read [-h] [-p PID] [-a PROCESSATOM] baseAddr memSize

positional arguments:
  baseAddr              base address to read from, in HEX FORMAT
  memSize               number of bytes to read, in HEX FORMAT

optional arguments:
  -p PID, --pid PID     pid of the process to get the map from
  -a PROCESSATOM, --processatom PROCESSATOM
                        the atom of the target process
```

## mem\_strings

List strings from a process's memory.

**Platforms:**

**Return Event:**
 [MEM\_STRINGS\_REP](/v1/docs/reference-events-responses-memory#MEM_STRINGS_REP)

**Due to recent changes in MacOS, this may be less reliable on that platform.**

**Usage:**

```
mem_strings [-h] [-p PID] [-a PROCESSATOM]

optional arguments:
  -p PID, --pid PID     pid of the process to get the strings from
  -a PROCESSATOM, --processatom PROCESSATOM
                        the atom of the target process
```

---

Was this article helpful?

Yes    No

Thank you for your feedback! Our team will get back to you

How can we improve this article?

Your feedback

[ ]  Need more information

[ ]  Difficult to understand

[ ]  Inaccurate or irrelevant content

[ ]  Missing/broken link

[ ]  Others

Comment

Comment (Optional)

Character limit : 500

Please enter your comment

Email (Optional)

Email

[ ]   Notify me about change

Please enter a valid email

Cancel

---

###### What's Next

* [Mitigation](/v1/docs/sensor-commands-mitigation)

Table of contents

+ [get\_debug\_data](#get_debug_data)
+ [mem\_find\_handle](#mem_find_handle)
+ [mem\_find\_string](#mem_find_string)
+ [mem\_handles](#mem_handles)
+ [mem\_map](#mem_map)
+ [mem\_read](#mem_read)
+ [mem\_strings](#mem_strings)
