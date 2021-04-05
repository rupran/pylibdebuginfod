#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2021 Andreas Ziegler <andreas.ziegler@fau.de>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import argparse
import os
import sys

from libdebuginfod import DebugInfoD, get_buildid_from_path
from elftools.elf.elffile import ELFFile
from elftools.common.exceptions import ELFError

def run(command, arg, sourcefile=None, verbose=False):
    d = DebugInfoD()
    if verbose:
        d.set_verbose_fd(sys.stderr)
    buildid = None
    if all(c in '0123456789abcdef' for c in arg):
        buildid = arg
    else:
        try:
            buildid = get_buildid_from_path(arg)
        except OSError as e:
            print('Cannot open {}: {}'.format(arg, os.strerror(e.errno)), file=sys.stderr)
        except ELFError as e:
            print('Error while reading ELF file {}: {}'.format(arg, e), file=sys.stderr)
    if buildid is None:
        sys.exit(1)
    if command == 'debuginfo':
        fd, path = d.find_debuginfo(buildid)
    elif command == 'executable':
        fd, path = d.find_executable(buildid)
    elif command == 'source':
        fd, path = d.find_source(buildid, sourcefile)
    if fd < 0:
        print('Query failed: {}'.format(os.strerror(-fd)), file=sys.stderr)
        sys.exit(1)
    print(path.decode('utf-8'))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', help='Be more verbose',
                        action='store_true')
    parser.add_argument('command', choices=['debuginfo', 'executable', 'source'],
                        help='The command what to retrieve from debuginfod.')
    parser.add_argument('input', nargs='+', help='A SHA-1 build ID or the path to a binary file'\
                        ' containing a build ID section. If the command is \'source\', you need'\
                        ' to provide a build ID or file as the first input parameter and the'\
                        ' absolute path to the target file (as present in the DWARF information)'\
                        ' as the second.')
    args = parser.parse_args()
    if args.command == 'source' and \
            (len(args.input) != 2 or not os.path.isabs(args.input[1])):
        parser.error('Please provide a PATH/BUILDID and an absolute path for \'source\'')
    elif args.command in ('debuginfo', 'executable') and len(args.input) != 1:
        parser.error('Please provide exactly one PATH or BUILDID as a parameter')
    sourcefile = None
    if args.command == 'source':
        sourcefile = args.input[1]

    run(args.command, args.input[0], sourcefile=sourcefile, verbose=args.verbose)
