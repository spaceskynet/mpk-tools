# MPK Tools

A tool to pack and unpack MPK files for games in Mages. engine, such as Steins;Gate, CHAOS;CHILD and so on. MPK v1 & v2 format are both supported.

[中文说明](README-zh.md)

## Usage

```
usage: mpk_tools.py [-h] {pack,packbycsv,unpack} ...

MPK Tool By SpaceSkyNet

positional arguments:
  {pack,packbycsv,unpack}
                        Available commands
    pack                Pack files into MPK
    packbycsv           Pack files into MPK By CSV
    unpack              Unpack files from MPK

options:
  -h, --help            show this help message and exit
```

## Unpack

Unpack the MPK file to the target directory. You can use the optional option `--csv_path` to export the file information in MPK file.

```
usage: mpk_tools.py unpack [-h] [-c CSV_PATH] mpk_path output

positional arguments:
  mpk_path              Path to MPK file
  output                Output directory

options:
  -h, --help            show this help message and exit
  -c CSV_PATH, --csv_path CSV_PATH
                        Path to CSV file for file list (optional)
```

## Pack

Pack the files in the target directory into an MPK file. By default, all files in the target directory are packed. You can use the optional option `--old_format` to use the MPK V1 format, or you can use the optional option `--no_compress` to pack without compressing the files. 

You can also use the optional option `--origin_mpk_path` to copy the file headers from the original MPK file, which is useful when you are making a patch. The optional option `--no_compress` is ignored when using this option.

```
usage: mpk_tools.py pack [-h] [-m ORIGIN_MPK_PATH] [-o] [-n] output pack_dir

positional arguments:
  output                Output MPK file path
  pack_dir              Directory containing files to pack

options:
  -h, --help            show this help message and exit
  -m ORIGIN_MPK_PATH, --origin_mpk_path ORIGIN_MPK_PATH
                        Path to original MPK file (optional)
  -o, --old_format      Use MPK V1 format
  -n, --no_compress     Not compress files (Ignored when use origin_mpk_path to copy headers)
```

## Pack By CSV

Pack the files in the CSV into an MPK file. You can use the optional option `--old_format` to use the MPK V1 format.

```
usage: mpk_tools.py packbycsv [-h] [-o] output csv_path

positional arguments:
  output            Output MPK file path
  csv_path          Directory containing files to pack

options:
  -h, --help        show this help message and exit
  -o, --old_format  Use MPK V1 format
```

### CSV Structure

```csv
id,is_compressed,filename_on_disk,filename_in_archive
0,1,album.gxt,album.gxt
1,1,backlog.gxt,backlog.gxt
...
```

## MPK File Structure
### MPK Header (64 bytes in total)

| name | size | values |
| --- | --- | --- |
| **IDENT** | 4 bytes | "MPK"\0 |
| Minor Version | 2 bytes | \0\0 |
| Major Version | 2 bytes | 0x1 in MPK v1, 0x2 in MPK v2 |
| File count | 4 bytes/8 bytes | 4 bytes in MPK v1, 8 bytes in MPK v2 |
| Null Bytes | remained bytes | |

The minor version seems to be always 0.

### File Header (256 bytes each file)

Repeat this section with the number equal to `File count`.

#### MPK V1 format

| name | size |
| --- | --- |
| Index | 4 bytes |
| Position | 4 bytes |
| Size | 4 bytes |
| Uncompressed Size (Same as before, if there is no compression) | 4 bytes |
| Null bytes | 16 bytes |
| Null terminated file name | 224 bytes |

#### MPK V2 format

| name | size |
| --- | --- |
| isCompressed | 4 bytes |
| Index | 4 bytes |
| Position | 8 bytes |
| Size | 8 bytes |
| Uncompressed Size (Same as before, if there is no compression) | 8 bytes |
| Null terminated file name | 224 bytes |

### Raw File Data (n bytes each file，n is equal to the `Size`)

Repeat this section with the number equal to `File count`.

| name | size |
| --- | --- |
| Raw data | Equal to the `Size` |

## Credits

This program is mainly created by [@SpaceSkyNet](https://github.com/spaceskynet), which is licensed under the [MIT License](./LICENSE). If you support this project, you can become a stargazer by clicking the star in the upper right corner of this [page](https://github.com/spaceskynet/mpk-tools/). It must be awesome!

**Thanks to These Projects:**

1. [MagesPack](https://github.com/DanOl98/MagesPack): Mages Engine MPK UnPack & RePack (Steins;Gate Steam, Steins;Gate 0, Steins;Gate Elite, Chaos;Child etc.)
2. [mpktools](https://github.com/ModzabazeR/mpktools): Tool for pack/unpack Mages Package files (.mpk)
3. [ChaosChildPCTools](https://github.com/ningshanwutuobang/ChaosChildPCTools): Tools for ChaosChild files
4. [GARbro](https://github.com/crskycode/GARbro): Visual Novels resource browser