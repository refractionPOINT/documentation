# Memory

The following sensor commands perform actions against memory on EDR sensors.

## get_debug_data

Retrieve debug data from the EDR sensor.

**Platforms:** Windows, Linux, macOS

**Return Event:** [DEBUG_DATA_REP](/v1/docs/reference-events-responses-memory#DEBUG_DATA_REP)

## mem_find_handle

Find specific open handles in memory on Windows.

**Platforms:** Windows

**Return Event:** [MEM_FIND_HANDLES_REP](/v1/docs/reference-events-responses-memory#MEM_FIND_HANDLES_REP)

**Usage:**

```
mem_find_handle [-h] needle

positional arguments:
  needle      substring of the handle names to get
```

## mem_find_string

Find specific strings in memory.

**Platforms:** Windows, Linux, macOS

**Return Event:** [MEM_FIND_STRING_REP](/v1/docs/reference-events-responses-memory#MEM_FIND_STRING_REP)

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

## mem_handles

List all open handles from a process (or all) on Windows.

**Platforms:** Windows

**Return Event:** [MEM_HANDLES_REP](/v1/docs/reference-events-responses-memory#MEM_HANDLES_REP)

**Usage:**

```
mem_handles [-h] [-p PID] [-a PROCESSATOM]

optional arguments:
  -p PID, --pid PID     pid of the process to get the handles from, 0 for all
                        processes
  -a PROCESSATOM, --processatom PROCESSATOM
                        the atom of the target process
```

## mem_map

Display the map of memory pages from a process including size, access rights, etc.

**Platforms:** Windows, Linux, macOS

**Return Event:** [MEM_MAP_REP](/v1/docs/reference-events-responses-memory#MEM_MAP_REP)

**Due to recent changes in MacOS, this may be less reliable on that platform.**

**Usage:**

```
mem_map [-h] [-p PID] [-a PROCESSATOM]

optional arguments:
  -p PID, --pid PID     pid of the process to get the map from
  -a PROCESSATOM, --processatom PROCESSATOM
                        the atom of the target proces
```

## mem_read

Retrieve a chunk of memory from a process given a base address and size.

**Platforms:** Windows, Linux, macOS

**Return Event:** [MEM_READ_REP](/v1/docs/reference-events-responses-memory#MEM_READ_REP)

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

## mem_strings

List strings from a process's memory.

**Platforms:** Windows, Linux, macOS

**Return Event:** [MEM_STRINGS_REP](/v1/docs/reference-events-responses-memory#MEM_STRINGS_REP)

**Due to recent changes in MacOS, this may be less reliable on that platform.**

**Usage:**

```
mem_strings [-h] [-p PID] [-a PROCESSATOM]

optional arguments:
  -p PID, --pid PID     pid of the process to get the strings from
  -a PROCESSATOM, --processatom PROCESSATOM
                        the atom of the target process
```