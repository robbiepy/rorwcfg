#!/usr/bin/env python
# -*- coding: utf-8 -*-


import logging
from datetime import datetime
from typing import IO
from rorwcfg import rorwfile


header_start = "### this file was created by"
header_end = "###\n"
header_line = "%s %s at:[%s] %s" % (header_start, "%s", "%s", header_end)
default_warning = '''\
# This file allows programs and plugins to write dynamic values.
# This file is not intended to be edited. Hence the file can be kept read-only.
# If the file is readonly, to create, write or append it executes these
# instructions: chmod 644, write and then chmod 444 back.
'''
warning_name = "[WARNING]"
warning_section = "%s\n%s"
timestamp_line_start = "# timestamp: "
timestamp_line_offset = len(timestamp_line_start)


class CfgSection:
    def __init__(self, **kwargs):
        self.section_name = kwargs.get('section_name')
        self.timestamp: str = ""
        self.dict: dict[str, str] = {}

    def __getitem__(self, key: str) -> str:
        return self.dict[key]

    def get(self, key: str, default: str = "") -> str:
        return self.dict.get(key, default)

    def __setitem__(self, key: str, value: str) -> None:
        self.dict[key] = value

    def set(self, key: str, value: str) -> None:
        self.dict[key] = value

    def get_bool(self, key: str) -> bool:
        return self.dict[key].lower in ['yes', 'true']

    def get_int(self, key: str) -> int:
        return int(self.dict[key])

    def get_float(self, key: str) -> float:
        return float(self.dict[key])

    def set_bool(self, key: str, value: bool) -> None:
        self.dict[key] = "true" if value else "false"

    def set_int(self, key: str, value: int) -> None:
        self.dict[key] = str(value)

    def set_float(self, key: str, value: float) -> None:
        self.dict[key] = str(value)

    def get_timestamp(self) -> datetime:
        return datetime.fromisoformat(self.timestamp)


class CfgFileHandler(rorwfile._FileHandler):
    def __init__(self, config_section: CfgSection, *args, **kwargs):
        super().__init__()
        self.section = config_section
        self.set_creator(kwargs.get("creator", "rorwcfg"))
        self.set_warning(kwargs.get("warning_msg", default_warning))
        self.delimeter: str = kwargs.get("delimeter", "=")
        self.write_timestamp: bool = kwargs.get("write_timestamp", True)
        self.spaced_delimeter = " %s " % self.delimeter
        self.lines: list[str] = []
        self.numlines: int = 0
        self.is_parsed: bool = False

    def set_creator(self, creator: str) -> None:
        self.creator = creator

    def set_warning(self, msg: str) -> None:
        self.warning = warning_section % (warning_name, msg)

    def _timestamp_now(self) -> str:
        return datetime.now().isoformat(sep=' ', timespec='seconds')

    def _find_section(self) -> None:
        section_line = "[%s]\n" % self.section.section_name
        for linenum, line in enumerate(self.lines[:-1], start=1):
            if line == section_line:
                self.section_linenum = linenum
                self.firstkey_linenum = linenum + 1
                return
        self.section_linenum = -1

    def _find_timestamp(self) -> None:
        line = self.lines[self.section_linenum]
        if line.startswith(timestamp_line_start):
            self.section.timestamp = line[len(timestamp_line_start):-1]
            self.firstkey_linenum += 1
        else:
            self.timestamp_linenum = -1

    def _parse_key_values(self) -> None:
        lines = self.lines[self.firstkey_linenum - 1:]
        for linenum, line in enumerate(lines, self.firstkey_linenum):
            if line[0] == "[":
                self.lastkey_linenum = linenum - 1
                return
            key_value = line.split(self.spaced_delimeter)
            if len(key_value) == 2:
                self.section.dict[key_value[0]] = key_value[1][:-1]
        self.lastkey_linenum = linenum

    def _write_section_lines(self, fd: IO) -> None:
        fd.write("[%s]\n" % self.section.section_name)
        if self.write_timestamp:
            fd.write("%s%s\n" % (timestamp_line_start, self._timestamp_now()))
        for key, value in self.section.dict.items():
            fd.write("%s%s%s\n" % (key, self.spaced_delimeter, value))

    def create_handler(self, fd: IO) -> None:
        header = header_line % (self.creator, self._timestamp_now())
        fd.write(header)
        fd.write(self.warning)

    def read_handler(self, fd: IO) -> None:
        self.lines = fd.readlines()
        self.numlines = len(self.lines)

    def parse_handler(self) -> None:
        if self.numlines > 0:
            self._find_section()
            if self.section_linenum > -1:
                self._find_timestamp()
                self._parse_key_values()
            self.is_parsed = True

    def write_handler(self, fd: IO) -> None:
        if self.is_parsed:
            if self.section_linenum > -1:
                fd.writelines(self.lines[:self.section_linenum - 1])
                self._write_section_lines(fd)
                fd.writelines(self.lines[self.lastkey_linenum:])
            else:
                fd.writelines(self.lines)
                self._write_section_lines(fd)
        else:
            logging.warning("didn't write section, config hasn't been parsed")


class ReadWriteCfgFile(rorwfile.ReadWriteFile):
    def __init__(self, fpath: str, **kwargs):
        self.config_section = CfgSection(**kwargs)
        handler = CfgFileHandler(self.config_section, **kwargs)
        super().__init__(fpath, handler, **kwargs)


class ReadOnlyCfgFile(rorwfile.ReadOnlyFile):
    def __init__(self, fpath: str, **kwargs):
        self.config_section = CfgSection(**kwargs)
        handler = CfgFileHandler(self.config_section, **kwargs)
        super().__init__(fpath, handler, **kwargs)


def cfg_file(fpath: str, cmd: str, **kwargs) -> (
             ReadOnlyCfgFile | ReadWriteCfgFile):
    rorwfile.check_file_exists(fpath, cmd)
    if rorwfile.is_readonly(fpath):
        return ReadOnlyCfgFile(fpath, **kwargs)
    else:
        return ReadWriteCfgFile(fpath, **kwargs)
