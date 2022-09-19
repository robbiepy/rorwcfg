#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os
import logging
import unittest
from datetime import datetime
import rorwcfg


fname = "test1.cfg"


class RoRWCfgTestBase:
    def _bump_version(self, section):
        version = int(section.get("version", "0")) + 1
        section["version"] = str(version)
        self.count = version
        self.section = section

    def _get_file_stat(self, fname: str) -> int:
        return (os.stat(fname).st_mode & 0o777)

    def _delete_testfile(self, fname):
        if os.path.isfile(fname):
            os.remove(fname)


class TestRoCfg(unittest.TestCase, RoRWCfgTestBase):
    def test_01_create_in_wrong_directory(self):
        fpath = "/___NOT_A_DIRECTORY___/test.cfg"
        exc = rorwcfg.rorwfile.RoRWFileError
        self.assertRaises(exc, rorwcfg.create_ro, fpath)

    def test_02_create_ro(self):
        # fname = "test1.cfg"
        self._delete_testfile(fname)
        rorwcfg.create_ro(fname)
        self.assertTrue(os.path.isfile(fname), "testing create")
        self.assertTrue(self._get_file_stat(fname) == 0o444)
        # test create while file exists raises exception
        exc = rorwcfg.rorwfile.RoRWFileError
        self.assertRaises(exc, rorwcfg.create_ro, fname)
        self.assertLogs(None, logging.ERROR)

    def test_03_overwrite_ro(self):
        # test create, overwriting with keyword
        rorwcfg.create_ro(fname, overwrite_if_exists=True)

    def test_04_write_ro(self):
        # fname = "test1.cfg"
        rorwcfg.write_ro(fname, "test", self._bump_version)
        self.assertEqual(self.count, 1)
        rorwcfg.write(fname, "test", self._bump_version)
        self.assertEqual(self.count, 2)
        self.assertEqual(self.section.section_name, "test")
        self.assertIsInstance(self.section.get_timestamp(), datetime)

    def test_05_write_rw(self):
        # fname = "test1.cfg"
        # test readwrite write to readonly file
        exc = PermissionError
        self.assertRaises(exc, rorwcfg.write_rw,
                          fname, "test", self._bump_version)

    def test_06_delete_ro(self):
        # fname = "test1.cfg"
        rorwcfg.delete(fname)
        self.assertFalse(os.path.isfile(fname), "testing delete")
        # test delete when file doesn't exists raises exception
        exc = rorwcfg.rorwfile.RoRWFileError
        self.assertRaises(exc, rorwcfg.delete, fname)
        self.assertLogs(None, logging.ERROR)


class TestRWCfg(unittest.TestCase, RoRWCfgTestBase):
    def test_101_create_rw(self):
        # fname = "test1.cfg"
        self._delete_testfile(fname)
        rorwcfg.create_rw(fname)
        self.assertTrue(os.path.isfile(fname), "testing create")
        self.assertTrue(self._get_file_stat(fname) == 0o664)

    def test_102_write_rw(self):
        # fname = "test1.cfg"
        rorwcfg.write_rw(fname, "test", self._bump_version)
        self.assertEqual(self.count, 1)
        rorwcfg.write(fname, "test", self._bump_version)
        self.assertEqual(self.count, 2)


if __name__ == '__main__':
    logging.basicConfig(level=logging.CRITICAL)
    unittest.main()
