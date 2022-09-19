#!/usr/bin/env python
# -*- coding: utf-8 -*-


from typing import Callable
from rorwcfg.rorwcfg import (ReadWriteCfgFile, ReadOnlyCfgFile,
                             CfgSection, cfg_file)


def create_ro(fpath: str, **kwargs) -> None:
    f = ReadOnlyCfgFile(fpath, **kwargs)
    f.create(**kwargs)


def create_rw(fpath: str, **kwargs) -> None:
    f = ReadWriteCfgFile(fpath, **kwargs)
    f.create(**kwargs)


def delete(fpath: str) -> None:
    cfg_file(fpath, "delete").delete()


def _write(f: ReadOnlyCfgFile | ReadWriteCfgFile,
           callback: Callable[[CfgSection], None]) -> None:
    f.read()
    f.parse()
    callback(f.config_section)
    f.write()


def write_ro(fpath: str, section_name: str,
             callback: Callable[[CfgSection], None]) -> None:
    _write(ReadOnlyCfgFile(fpath, section_name=section_name), callback)


def write_rw(fpath: str, section_name: str,
             callback: Callable[[CfgSection], None]) -> None:
    _write(ReadWriteCfgFile(fpath, section_name=section_name), callback)


def write(fpath: str, section_name: str,
          callback: Callable[[CfgSection], None]) -> None:
    _write(cfg_file(fpath, "write", section_name=section_name), callback)
