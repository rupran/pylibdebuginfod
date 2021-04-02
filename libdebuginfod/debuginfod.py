# SPDX-FileCopyrightText: 2021 Andreas Ziegler <andreas.ziegler@fau.de>
#
# SPDX-License-Identifier: MIT
'''A Python interface for functionality provided by libdebuginfod.so.

With the DebugInfoD class in this module, you can query a debuginfod server
for debugging information, the original executable or the source code for a
given build id. An overview of existing servers, applications with integrated
debuginfod support can be found at [0].

Note that for a working connection the DEBUGINFOD_URLS environment variable must
be set to a space-separated list of servers which will be queried for the
requested file. Otherwise, all find_* methods will fail and only return the
error code -38 (Function not implemented).

Example:
    >>> from libdebuginfod import DebugInfoD
    >>> d = DebugInfoD()
    >>> d.begin()
    >>> d.find_debuginfo('18b9a9a8c523e5cfe5b5d946d605d09242f09798')
    (3, b'/tmp/cache/18b9a9a8c523e5cfe5b5d946d605d09242f09798/debuginfo')
    >>> d.end()

[0]: https://sourceware.org/elfutils/Debuginfod.html
'''
import os

from ctypes import util
from ctypes import CDLL, c_char_p, c_void_p, c_int, c_long, CFUNCTYPE
from ctypes import get_errno, create_string_buffer, byref, cast

def _convert_to_string_buffer(buildid):
    '''Convert a given buffer (bytes or str) to a ctypes string buffer.

    Similar to the interface of libdebuginfod itself, all find_* functions can
    be called with either a sequence of bytes or a string. In the latter case,
    0 should be provided in the build_id_len parameter, while the actual number
    of bytes should be reported for a byte string.

    Args:
        buildid (bytes or str): the input buildid to be converted

    Returns:
        A tuple containing the ctypes string buffer as the first element and
        an integer with the correct value to pass in the build_id_len parameter
        to libdebuginfo.so.
    '''
    if isinstance(buildid, str):
        return create_string_buffer(buildid.encode('utf-8')), 0
    buf = create_string_buffer(buildid)
    return buf, len(buf)-1

# typedef int (*debuginfod_progressfn_t)(debuginfod_client *client,
#                                        long a, long b);
ProgressFunction = CFUNCTYPE(c_int, c_void_p, c_long, c_long)
'''A callback function type which is called during file download.

In order to allow a callback function to be implemented, it must be derived from
ctypes.CFUNCTYPE. The ProgressFunction type already includes the correct
description of parameter types and the return value. The callback function must
take three parameters - client (which will be of type ctypes.c_void_p), a, and
b -, where a and b are ctypes.c_long values and a/b describes the progress of
the current file download. b may be zero until the actual download size can be
determined.
'''

class DebugInfoD:
    '''A wrapper class providing Python bindings for libdebuginfo.so operations.
    '''

    def __init__(self):
        '''Initialize the DebugInfoD object.

        If the environment variable DEBUGINFOD_URLS is not set, it is
        initialized to point to the federating server provided by elfutils,
        located at https://debuginfod.elfutils.org/.

        Raises:
            FileNotFoundError: libdebuginfod.so was not found in the system.
            OSError: Creating the connection handle for this session failed.
        '''
        searched_library = util.find_library('debuginfod')
        if not searched_library:
            raise FileNotFoundError('libdebuginfod not found, please install it first!')
        self._handle = CDLL(searched_library, use_errno=True)
        self._handle_libc = CDLL(util.find_library('c'))
        if not os.environ.get('DEBUGINFOD_URLS', None):
            os.environ['DEBUGINFOD_URLS'] = 'https://debuginfod.elfutils.org/'
        self._client = None
        self.begin()

    def __enter__(self):
        '''Allow DebugInfoD to be used as a context manager.'''
        self.begin()
        return self

    def __exit__(self, *args):
        '''Allow DebugInfoD to be used as a context manager.'''
        self.end()

    # debuginfod_client *debuginfod_begin(void);
    def begin(self):
        '''Create a connection handle.

        Raises:
            OSError: Creating the connection handle for this session failed.
        '''
        if self._client:
            return
        self._handle.debuginfod_begin.restype = c_void_p
        self._client = self._handle.debuginfod_begin()
        if not self._client:
            errno = get_errno()
            raise OSError(errno, os.strerror(errno))

    # void debuginfod_end(debuginfod_client *client);
    def end(self):
        '''Release all state and storage for the current connection handle.'''
        if self._client:
            self._handle.debuginfod_end(self._client)
            self._client = None

    # int debuginfod_find_debuginfo(debuginfod_client *client,
    #                               const unsigned char *build_id,
    #                               int build_id_len,
    #                               char ** path);
    def find_debuginfo(self, buildid):
        '''Retrieve the debug information file for a given build ID

        Args:
            buildid (bytes or str): The build ID of the binary file

        Returns:
            A tuple with an open file descriptor (<int>) and a <bytes>
            representation of the path to the retrieved source code file.

            Example: (3, b'$HOME/.cache/debuginfod_client/{buildid}/debuginfo)
        '''
        path_p = c_char_p()
        buildid, size = _convert_to_string_buffer(buildid)
        self._handle.debuginfod_find_debuginfo.argtypes = [c_void_p, c_char_p,
                                                           c_int, c_void_p]

        res = self._handle.debuginfod_find_debuginfo(self._client, buildid,
                                                     size, byref(path_p))
        if res < 0:
            return res, None
        # From os.path documentation: Unfortunately, some file names may not be
        # representable as strings on Unix, so applications that need to
        # support arbitrary file names on Unix should use bytes objects to
        # represent path names.
        path = cast(path_p, c_char_p).value
        # If path is not NULL and the query is successful, path is set to the
        # path of the file in the cache. The caller must free() this value.
        self._handle_libc.free(path_p)
        return res, path

    # int debuginfod_find_executable(debuginfod_client *client,
    #                                const unsigned char *build_id,
    #                                int build_id_len,
    #                                char ** path);
    def find_executable(self, buildid):
        '''Retrieve the executable file for a given build ID

        Args:
            buildid (bytes or str): The build ID of the binary file

        Returns:
            A tuple with an open file descriptor (<int>) and a <bytes>
            representation of the path to the retrieved source code file.

            Example: (3, b'$HOME/.cache/debuginfod_client/{buildid}/executable)
        '''
        path_p = c_char_p()
        buildid, size = _convert_to_string_buffer(buildid)
        self._handle.debuginfod_find_executable.argtypes = [c_void_p, c_char_p,
                                                            c_int, c_void_p]

        res = self._handle.debuginfod_find_executable(self._client, buildid,
                                                      size, byref(path_p))
        if res < 0:
            return res, None
        path = cast(path_p, c_char_p).value
        self._handle_libc.free(path_p)
        return res, path

    # int debuginfod_find_source(debuginfod_client *client,
    #                            const unsigned char *build_id,
    #                            int build_id_len,
    #                            const char *filename,
    #                            char ** path);
    def find_source(self, buildid, filename):
        '''Retrieve the source code for a given build ID and filename

        Args:
            buildid (bytes or str):  The build ID of the binary file
            filename (bytes or str): The absolute path to the source file as
                given in the DWARF information.

        Returns:
            A tuple with an open file descriptor (<int>) and a <bytes>
            representation of the path to the retrieved source code file.

            Example: (3, b'$HOME/.cache/debuginfod_client/{buildid}/source/{filename})
        '''
        path_p = c_char_p()
        buildid, size = _convert_to_string_buffer(buildid)
        filename = _convert_to_string_buffer(filename)
        self._handle.debuginfod_find_source.argtypes = [c_void_p, c_char_p, c_int,
                                                        c_char_p, c_void_p]

        res = self._handle.debuginfod_find_source(self._client, buildid, size,
                                                  filename, byref(path_p))
        if res < 0:
            return res, None
        path = cast(path_p, c_char_p).value
        self._handle_libc.free(path_p)
        return res, path

    # void debuginfod_set_progressfn(debuginfod_client *client,
    #                                debuginfod_progressfn_t progressfn);
    def set_progressfn(self, progressfn: ProgressFunction):
        '''Set a callback function which is called during file download

        Args:
            progressfn (ProgressFunction): A function constructed with the
                wrapper ProgressFunction (derived of ctypes.CFUNCTYPE) which
                takes three parameters (debuginfod_client *, long a, long b).
                a and b represent the fraction a/b of the current download
                progress. b may be zero until the exact download size is known.
        '''
        # We already need a CFUNCTYPE object passed in, see the following
        # excerpt from the ctypes documentation regarding callbacks:
        # Note: Make sure you keep references to CFUNCTYPE() objects as long as
        # they are used from C code. ctypes doesn’t, and if you don’t, they may
        # be garbage collected, crashing your program when a callback is made.
        self._handle.debuginfod_set_progressfn(self._client, progressfn)

    # void debuginfod_set_verbose_fd(debuginfod_client *client, int fd);
    def set_verbose_fd(self, fd):
        '''Set the file descriptor to write verbose messages to

        Args:
            fd (file object): the file object to write verbose output to

        Raises:
            NotImplementedError: The backing libdebuginfod.so file does not
                provide the debuginfod_set_verbose_fd() function.
        '''
        try:
            self._handle.debuginfod_set_verbose_fd.argtypes = [c_void_p, c_int]
            self._handle.debuginfod_set_verbose_fd(self._client, fd.fileno())
        except AttributeError:
            raise NotImplementedError from None

    # void debuginfod_set_user_data(debuginfod_client *client, void *data);
    def set_user_data(self, data):
        '''Not implemented (yet).

        Raises:
            NotImlementedError: always
        '''
        raise NotImplementedError

    # void* debuginfod_get_user_data(debuginfod_client *client);
    def get_user_data(self):
        '''Not implemented (yet).

        Raises:
            NotImlementedError: always
        '''
        raise NotImplementedError

    # const char* debuginfod_get_url(debuginfod_client *client);
    def get_url(self):
        '''Get the URL of the most recent downloaded file

        Returns:
            The most recent download URL as a string.

        Raises:
            NotImplementedError: The backing libdebuginfod.so file does not
                provide the debuginfod_get_url() function.
        '''
        try:
            self._handle.debuginfod_get_url.restype = c_char_p
            result = self._handle.debuginfod_get_url(self._client)
            return result.decode('utf-8') if result else None
        except AttributeError:
            raise NotImplementedError from None

    # int debuginfod_add_http_header(debuginfod_client *client,
    #                                const char* header);
    def add_http_header(self, header: str):
        '''Add a custom HTTP header to all outgoing requests

        Args:
            header (str): The custom header in the form \"Header: value\".

        Returns:
            0 on success, a negative error code otherwise.

        Raises:
            NotImplementedError: The backing libdebuginfod.so file does not
                provide the debuginfod_add_http_header() function.
        '''
        header = _convert_to_string_buffer(header)
        try:
            self._handle.debuginfod_add_http_header.argtypes = [c_void_p, c_char_p]
            return self._handle.debuginfod_add_http_header(self._client, header)
        except AttributeError:
            raise NotImplementedError from None

    def __del__(self):
        '''Release all state and storage for the current connection handle.'''
        if self._client:
            self._handle.debuginfod_end(self._client)
            self._client = None
