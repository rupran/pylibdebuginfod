import os
import unittest

from ctypes import sizeof
from elftools.elf.elffile import ELFFile
from libdebuginfod import DebugInfoD, get_buildid_from_path
from libdebuginfod.debuginfod import _convert_to_string_buffer

# WARNING: These tests currently only work inside a Fedora Rawhide container
# (the .github/workflows/test.yml file pulls such a container for test case
# execution as a GitHub Action).

TEST_BINARY='/bin/gcc'
# Source path from a specific version of gcc in rawhide. This needs to be
# installed in the correct version in the test.yml file
TEST_SRCPATH='/usr/src/debug/gcc-11.0.1-0.4.fc35.x86_64/obj-x86_64-redhat-linux/gcc/../../gcc/gcc-main.c'

class TestDebugInfoD(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.buildid = get_buildid_from_path(TEST_BINARY)

    def test_0_get_buildid_from_path(self):
        self.assertIsNotNone(self.buildid)

    def test_0_string_convert_to_string_buffer(self):
        test_str = '4d7e25cb25aefa300b44f32fe1fefe7bea76cb41'
        buf, buflen = _convert_to_string_buffer(test_str)
        self.assertEqual(len(test_str) + 1, sizeof(buf))
        self.assertEqual(0, buflen)

    def test_0_binary_convert_to_string_buffer(self):
        test_hex = b'\x4d\x7e\x25\xcb\x25\xae\xfa\x30\x0b\x44\xf3\x2f\xe1\xfe\xfe\x7b\xea\x76\xcb\x41'
        buf, buflen = _convert_to_string_buffer(test_hex)
        self.assertEqual(len(test_hex) + 1, sizeof(buf))
        self.assertEqual(len(test_hex), buflen)

    def test_1_get_debuginfo(self):
        with DebugInfoD() as client:
            fdesc, path = client.find_debuginfo(self.buildid)
            # Check that we got a valid result
            self.assertIsNotNone(path)
            # Open the file and check if it has a .symtab section
            fd = os.fdopen(fdesc, 'rb')
            section = ELFFile(fd).get_section_by_name('.symtab')
            self.assertIsNotNone(section)
            if fdesc > 0:
                fd.close()
            # Remove the downloaded file to trigger a fresh download in the next
            # test case
            os.remove(path)

    def test_1_fail_get_debuginfo(self):
        with DebugInfoD() as client:
            fdesc, path = client.find_debuginfo(self.buildid + 'f')
            self.assertLess(fdesc, 0)
            self.assertIsNone(path)

    def test_2_get_executable(self):
        with DebugInfoD() as client:
            fdesc, path = client.find_executable(self.buildid)
            if fdesc > 0:
                os.close(fdesc)
            self.assertIsNotNone(path)
            os.remove(path)

    def test_2_fail_get_executable(self):
        with DebugInfoD() as client:
            fdesc, path = client.find_executable(self.buildid + 'f')
            self.assertLess(fdesc, 0)
            self.assertIsNone(path)

    def test_3_get_source(self):
        with DebugInfoD() as client:
            fdesc, path = client.find_source(self.buildid, TEST_SRCPATH)
            if fdesc > 0:
                os.close(fdesc)
            self.assertIsNotNone(path)
            os.remove(path)

    def test_3_fail_get_source(self):
        with DebugInfoD() as client:
            fdesc, path = client.find_source(self.buildid + 'f', TEST_SRCPATH)
            self.assertLess(fdesc, 0)
            self.assertIsNone(path)

    def test_4_get_url(self):
        with DebugInfoD() as client:
            fdesc, path = client.find_debuginfo(self.buildid)
            if fdesc > 0:
                os.close(fdesc)
            if path is not None:
                os.remove(path)
            url = client.get_url()
            self.assertIsNotNone(url)

    def test_5_set_user_data(self):
        with self.assertRaises(NotImplementedError):
            with DebugInfoD() as client:
                client.set_user_data(None)

    def test_6_get_user_data(self):
        with self.assertRaises(NotImplementedError):
            with DebugInfoD() as client:
                client.get_user_data()

    def test_7_add_http_header(self):
        with DebugInfoD() as client:
            retval = client.add_http_header('Cache-control: no-cache')
            self.assertEqual(retval, 0)
            retval = client.add_http_header('Invalid-header')
            self.assertNotEqual(retval, 0)

if __name__ == '__main__':
    unittest.main()
