<!--
SPDX-FileCopyrightText: 2021 Andreas Ziegler <andreas.ziegler@fau.de>

SPDX-License-Identifier: MIT
-->

# libdebuginfod-python
Python bindings for [libdebuginfod](https://sourceware.org/elfutils/Debuginfod.html).

This library provides a Python interface for the functions in the `libdebuginfod.so` library from [elfutils](https://sourceware.org/elfutils/). The `debuginfod` cilent/server infrastructure allows automatic distribution of debugging information (ELF symbol tables, DWARF and even source code) for binaries installed on the current system.

The debuginfod server is queried using a SHA-1 hash (the build ID) which is contained in a section `.note.gnu.build-id` in the stripped binary file.

# Usage

This example was run under Debian Buster with the `libdebuginfod1`, `libelf1` and `libdw1` packages from `buster-backports`.

In order to make `libdebuginfod.so` aware of the servers to query, you can set the `DEBUGINFOD_URLS` environment variable. For example, to query the Debian server, you can run:

```bash
export DEBUGINFOD_URLS="https://debuginfod.debian.net"
```

If the `DEBUGINFOD_URLS` environment variable is not set, it is temporarily set to the `elfutils` server (`https://debuginfod.elfutils.org/`) which federates to all trusted servers (listed on the [elfutils](https://sourceware.org/elfutils/Debuginfod.html) website).

The other environment variables listed in the [manual page](https://manpages.debian.org/experimental/libdebuginfod-dev/debuginfod_find_debuginfo.3.en.html#ENVIRONMENT_VARIABLES) are also respected as they are handled by `libdebuginfod.so` itself.

With the prerequisites in place, you can use the `DebugInfoD` class as follows:

```python
  >>> from debuginfod.debuginfod import DebugInfoD
  >>> session = DebugInfoD()
  >>> session.begin() # optional, is also called from __init__ at the moment.
  >>> fd, path = session.find_debuginfo('18b9a9a8c523e5cfe5b5d946d605d09242f09798')
  >>> print((fd, path))
  (3, b'/home/user/.cache/debuginfod_client/18b9a9a8c523e5cfe5b5d946d605d09242f09798/debuginfo')
  >>> session.end()
```

In a more pythonic way, `DebugInfoD` can also be used as a context manager where
`begin()` and `end()` are called automatically.

```python
  >>> from debuginfod.debuginfod import DebugInfoD
  >>> with DebugInfoD() as d:
  ...     fd, path = d.find_debuginfo('18b9a9a8c523e5cfe5b5d946d605d09242f09798')
  ...     print((fd, path))
  ...
  (3, b'/home/user/.cache/debuginfod_client/18b9a9a8c523e5cfe5b5d946d605d09242f09798/debuginfo')
```

# License(s)
The bindings themselves are released under the [MIT](https://opensource.org/licenses/MIT) license. As the script at `scripts/debuginfod-find.py` is a reimplementation of the `debuginfod-find` application from [elfutils](https://sourceware.org/elfutils/Debuginfod.html) (which is licensed under the GPLv3+ license), the script is also released under the [GPLv3+](https://www.gnu.org/licenses/gpl-3.0.en.html) license.
