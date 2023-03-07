# rorwcfg

A small cross-platform python module that can safely write to a protected readonly config file.


## Installation

``` pip install -i https://test.pypi.org/simple/ rorwcfg ```


## Description

This package is useful when there is a need for a config file that people may like to read but wish to prevent human editing. 

For example, imagine python packaging software has dynamic versioning and is used by a team of coders. The software may find the latest version from Git and then modify the string to create the dynamic version, which it writes to a human readable file. However the team doesn't want the junior coders to edit the file and potentially corrupt the dynamic versioning.


## Basic Tutorial

This code creates a readonly file called "bump.ini", then minor bumps the version five times:

```
import time
import rorwcfg


def bump_version(section):
    version = float(section.get("version", "0.0")) + 0.1
    section["version"] = str(version)


fpath = "bump.ini"
rorwcfg.create_ro(fpath)
# bump five times
for x in range(0, 5):
    print("bump [%d]" % x)
    time.sleep(1)
    rorwcfg.write_ro(fpath, "bumper", bump_version)
```


## Example File

This is the resultant config file from the above basic tutorial. Note that a header, warning section and timestamps are added by default.

```
### this file was created by rorwcfg at:[2023-03-07 14:35:42] ###
[WARNING]
# This file allows programs and plugins to write dynamic values.
# This file is not intended to be edited. Hence the file can be kept read-only.
# If the file is readonly, to create, write or append it executes these
# instructions: chmod 644, write and then chmod 444 back.
[bumper]
# timestamp: 2023-03-07 14:35:47
version = 0.5
```
Here are the files permissions:
```
-r--r--r-- 1 robbiepy robbiepy  407 Mar  7 14:35 bump.ini
```

## Reference

This package has the following top-level helper functions. Write functions require a callback function.

```
import rorwcfg

# create a readonly file
rorwcfg.create_ro(fpath)

# create a readwrite file
rorwcfg.create_rw(fpath)

# write to a readonly file
rorwcfg.write_ro(fpath, section, callback_function)

# write to a readwrite file
rorwcfg.write_rw(fpath, section, callback_function)

# write to a file regardless if file is RO or RW
rorwcfg.write(fpath, section, callback_function)

# delete a rorwcfg file
rorwcfg.delete(fpath)
```

These functions call the underlying classes ``` ReadOnlyCfgFile ``` and ``` ReadWriteCfgFile ```. 

If you wish to use these underlying classes instead of the helper functions, it is best to read the code itself to understand their functionality. You may wish to overwrite the classes.

There are also more parameters that can be passed to the helper ``` create_ro ``` and ``` create_rw ``` functions:

```
# create a readonly file
rorwcfg.create_ro(fpath, creator="rorwcfg", warning_msg=default_warning, 
                  delimeter="=", write_timestamp=True, is_binary_file=False)

```

[MIT Licence](https://github.com/robbiepy/rorwcfg/blob/main/LICENSE) © [Robert Smith](https://github.com/robbiepy) 2023
