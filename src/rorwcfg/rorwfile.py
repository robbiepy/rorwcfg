#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os
import stat
import logging
from typing import IO, Callable


class RoRWFileError(Exception):
    pass


class _Object():
    def __init__(self, *args, **kwargs):
        pass


class _FileStat(_Object):
    readonly_bit = stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH
    readwrite_bit = readonly_bit | stat.S_IWUSR

    def __init__(self, *args, **kwargs):
        self.fpath: str = args[0]
        super().__init__(*args, **kwargs)

    def _get_file_stat(self) -> int:
        return (os.stat(self.fpath).st_mode & 0o777)

    def _is_readonly(self) -> bool:
        return (self._get_file_stat() == 0o444)

    def _is_readwrite(self) -> bool:
        return (self._get_file_stat() == 0o644)

    def _chmod(self, permissions: str) -> None:
        if permissions not in ["readonly", "readwrite"]:
            msg = "can't chmod, invalid permissions: %s" % permissions
            logging.warning(msg)
            return
        try:
            if permissions == "readonly":
                os.chmod(self.fpath, self.readonly_bit)
            elif permissions == "readwrite":
                os.chmod(self.fpath, self.readwrite_bit)
            return
        except FileNotFoundError:
            sub_msg = "file not found: %s" % self.fpath
        except OSError:
            sub_msg = "os error"
        msg = "can't chmod %s, %s" % (permissions, sub_msg)
        logging.error(msg)
        raise RoRWFileError(msg)

    def _chmod_readonly(self) -> None:
        self._chmod("readonly")

    def _chmod_readwrite(self) -> None:
        self._chmod("readwrite")


class _FileHandler:
    def create_handler(self, fd: IO) -> None:
        pass

    def read_handler(self, fd: IO) -> None:
        pass

    def write_handler(self, fd: IO) -> None:
        pass

    def append_handler(self, fd: IO) -> None:
        pass

    def parse_handler(self) -> None:
        pass


class _LowLevelFileBase(_Object):
    def __init__(self, *args, **kwargs):
        self.fpath: str = args[0]
        self.handler: _FileHandler = args[1]
        self.binaryfile: bool = kwargs.get("is_binary_file", False)
        self.binary_char: str = "b" if self.binaryfile else ""
        super().__init__(*args, **kwargs)

    def _handle_file(self, action: str, fn: Callable[[IO], None]) -> None:
        if isinstance(self.handler, _FileHandler):
            io_char: str = "w" if action == "create" else action[0]
            with open(self.fpath, io_char + self.binary_char) as fd:
                fn(fd)
        else:
            msg = "can't %s, file handler is invalid" % action
            logging.error(msg)
            raise RoRWFileError(msg)

    def _get_handler(self) -> _FileHandler:
        if isinstance(self.handler, _FileHandler):
            return self.handler
        else:
            msg = "file handler is invalid"
            logging.error(msg)
            raise RoRWFileError(msg)

    def _create(self) -> None:
        self._handle_file("create", self.handler.create_handler)

    def _delete(self) -> None:
        os.remove(self.fpath)

    def _read(self) -> None:
        self._handle_file("read", self.handler.read_handler)

    def _write(self) -> None:
        self._handle_file("write", self.handler.write_handler)

    def _append(self) -> None:
        self._handle_file("append", self.handler.append_handler)

    def _parse(self) -> None:
        self._get_handler().parse_handler()

    def _check_create_path_validity(self, **kwargs) -> None:
        overwrite_if_exists: bool = kwargs.get('overwrite_if_exists', False)
        cant_create_msg = "Can't create,"
        dirname = os.path.dirname(os.path.abspath(self.fpath))
        if not os.path.isdir(dirname):
            msg = "%s directory doesn't exist: %s" % (cant_create_msg, dirname)
        elif os.path.isfile(self.fpath) and not overwrite_if_exists:
            msg = "%s file already exists: %s" % (cant_create_msg, self.fpath)
        else:
            return
        logging.error(msg)
        raise RoRWFileError(msg)

    def _check_file_exists(self, cmd) -> None:
        if not os.path.isfile(self.fpath):
            msg = "Can't %s, file doesn't exist: %s" % (cmd, self.fpath)
            logging.error(msg)
            raise RoRWFileError(msg)


class _FileBase(_LowLevelFileBase):
    def create(self, **kwargs) -> None:
        self._check_create_path_validity(**kwargs)
        self._create()

    def delete(self) -> None:
        self._check_file_exists("delete")
        self._delete()

    def read(self) -> None:
        self._check_file_exists("read")
        self._read()

    def write(self) -> None:
        self._check_file_exists("write")
        self._write()

    def append(self) -> None:
        self._check_file_exists("append")
        self._append()

    def parse(self) -> None:
        self._parse()


class ReadWriteFile(_FileBase, _FileStat):
    pass


class ReadOnlyFile(_FileBase, _FileStat):
    def create(self, **kwargs) -> None:
        self._check_create_path_validity(**kwargs)
        self._chmod_readwrite() if os.path.isfile(self.fpath) else None
        super()._create()
        self._chmod_readonly()

    def delete(self) -> None:
        self._check_file_exists("delete")
        self._chmod_readwrite()
        super()._delete()

    def write(self) -> None:
        self._check_file_exists("write")
        self._chmod_readwrite()
        super()._write()
        self._chmod_readonly()

    def append(self) -> None:
        self._check_file_exists("append")
        self._chmod_readwrite()
        super()._append()
        self._chmod_readonly()


def check_file_exists(fpath: str, cmd: str) -> None:
    _LowLevelFileBase(fpath, None)._check_file_exists(cmd)


def is_readonly(fpath: str) -> bool:
    return _FileStat(fpath)._is_readonly()
