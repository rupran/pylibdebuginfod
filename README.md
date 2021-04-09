<!--
SPDX-FileCopyrightText: 2021 Andreas Ziegler <andreas.ziegler@fau.de>

SPDX-License-Identifier: MIT
-->
[![PyPI version](https://badge.fury.io/py/pylibdebuginfod.svg)](https://badge.fury.io/py/pylibdebuginfod)

# pylibdebuginfod
Python bindings for [libdebuginfod](https://sourceware.org/elfutils/Debuginfod.html).

This library provides a Python interface for the functions in the `libdebuginfod.so` library from [elfutils](https://sourceware.org/elfutils/). The `debuginfod` client/server infrastructure allows automatic distribution of debugging information (ELF symbol tables, DWARF and even source code) for binaries installed on the current system.

The debuginfod server is queried using a SHA-1 hash (the build ID) which is contained in a section `.note.gnu.build-id` in the stripped binary file.

# Prerequisites
The minimum Python version required is 3.5.

The bindings require an installation of `libdebuginfod.so` and the [pyelftools](https://github.com/eliben/pyelftools) library.

`libdebuginfod.so` is shipped in the major distributions in the following packages:
 * Debian (`buster-backports`, `bullseye`, `sid`): `libdebuginfod1`
 * Fedora/CentOS: `elfutils-debuginfod-client`
 * openSUSE Tumbleweed: `elfutils`
 * Ubuntu (20.10 and later): `libdebuginfod1`

Alternatively, you can get and compile the source code from the official [elfutils Git repository](https://sourceware.org/git/?p=elfutils.git;a=summary).

# Usage
The following examples were run under Debian Buster with the `libdebuginfod1`, `libelf1` and `libdw1` packages from `buster-backports`.

In order to make `libdebuginfod.so` aware of the servers to query, you can set the `DEBUGINFOD_URLS` environment variable. For example, to query the Debian server, you can run:

```bash
$ export DEBUGINFOD_URLS="https://debuginfod.debian.net"
```

If the `DEBUGINFOD_URLS` environment variable is not set, it is temporarily set to the `elfutils` server (`https://debuginfod.elfutils.org/`) which federates to all trusted servers (listed on the [elfutils](https://sourceware.org/elfutils/Debuginfod.html) website).

The other environment variables listed in the [manual page](https://manpages.debian.org/experimental/libdebuginfod-dev/debuginfod_find_debuginfo.3.en.html#ENVIRONMENT_VARIABLES) are also respected as they are handled by `libdebuginfod.so` itself.

You can extract the build ID information using the `readelf` tool like this:

```bash
$ readelf -n /lib/x86_64-linux-gnu/libc-2.28.so

Displaying notes found in: .note.gnu.build-id
  Owner                 Data size	Description
  GNU                  0x00000014	NT_GNU_BUILD_ID (unique build ID bitstring)
    Build ID: 18b9a9a8c523e5cfe5b5d946d605d09242f09798
```

With the prerequisites in place, you can use the `DebugInfoD` class as follows:

```python
  >>> from libdebuginfod import DebugInfoD
  >>> session = DebugInfoD()
  >>> session.begin() # optional, is also called from __init__ at the moment.
  >>> fd, path = session.find_debuginfo('18b9a9a8c523e5cfe5b5d946d605d09242f09798')
  >>> print((fd, path))
  (3, b'/home/user/.cache/debuginfod_client/18b9a9a8c523e5cfe5b5d946d605d09242f09798/debuginfo')
  >>> session.end()
```

In a more pythonic way, `DebugInfoD` can also be used as a context manager where `begin()` and `end()` are called automatically.

```python
  >>> from libdebuginfod import DebugInfoD
  >>> with DebugInfoD() as d:
  ...     fd, path = d.find_debuginfo('18b9a9a8c523e5cfe5b5d946d605d09242f09798')
  ...     print((fd, path))
  ...
  (3, b'/home/user/.cache/debuginfod_client/18b9a9a8c523e5cfe5b5d946d605d09242f09798/debuginfo')
```

The [scripts/debuginfod-find.py](https://github.com/rupran/pylibdebuginfod/blob/main/scripts/debuginfod-find.py) script supports three commands (`debuginfo`, `executable` and `source`) and accepts either a build ID or a path to a target file. If the filename matches the pattern `[0-9a-f]+`, please provide the path (e.g., `./e3`) to avoid misinterpretation of the input as a build ID. If the command is `source`, you need to provide the path or build ID as the first input parameter and an absolute path to the target source file (as present in the DWARF information) as the second input parameter.

Example usage:

```bash
$ ./scripts/debuginfod-find.py debuginfo /lib/x86_64-linux-gnu/libc-2.28.so
/home/user/.cache/debuginfod_client/18b9a9a8c523e5cfe5b5d946d605d09242f09798/debuginfo
```

# License(s)
The bindings themselves are released under the [MIT](https://opensource.org/licenses/MIT) license. As the script at [scripts/debuginfod-find.py](https://github.com/rupran/pylibdebuginfod/blob/main/scripts/debuginfod-find.py) is a reimplementation of the `debuginfod-find` application from [elfutils](https://sourceware.org/elfutils/Debuginfod.html) (which is licensed under the GPLv3+ license), the script is also released under the [GPLv3+](https://www.gnu.org/licenses/gpl-3.0.en.html) license and not included in the packaged release of the bindings.
