# MPK Tool

一个用于打包和解包 Mages. 引擎游戏（如 命运石之门|Steins;Gate、混沌之子|CHAOS;CHILD 等）中的 MPK 文件的工具。支持 MPK V1 和 V2 格式。

[English](README.md)

## 使用方法

```
usage: mpk_tools.py [-h] {pack,packbycsv,unpack} ...

MPK Tool By SpaceSkyNet

位置参数:
  {pack,packbycsv,unpack}
                        可用命令
    pack                将文件打包成 MPK
    packbycsv           通过 CSV 将文件打包成 MPK
    unpack              从 MPK 解包文件

选项:
  -h, --help            显示此帮助信息并退出
```

## 解包

将 MPK 文件解包到目标目录。您可以使用可选选项 `--csv_path` 导出 MPK 文件中的文件信息。

```
usage: mpk_tools.py unpack [-h] [-c CSV_PATH] mpk_path output

位置参数:
  mpk_path              MPK 文件路径
  output                输出目录

选项:
  -h, --help            显示此帮助信息并退出
  -c CSV_PATH, --csv_path CSV_PATH
                        文件列表的 CSV 文件路径（可选）
```

## 打包

将目标目录中的文件打包成 MPK 文件。默认情况下，目标目录中的所有文件都会被打包。您可以使用可选选项 `--old_format` 使用 MPK V1 格式，或者使用可选选项 `--no_compress` 在不压缩文件的情况下打包。

您还可以使用可选选项 `--origin_mpk_path` 从原始 MPK 文件复制文件头，这在制作补丁时非常有用。使用此选项时，忽略可选选项 `--no_compress`。

```
usage: mpk_tools.py pack [-h] [-m ORIGIN_MPK_PATH] [-o] [-n] output pack_dir

位置参数:
  output                输出 MPK 文件路径
  pack_dir              包含要打包文件的目录

选项:
  -h, --help            显示此帮助信息并退出
  -m ORIGIN_MPK_PATH, --origin_mpk_path ORIGIN_MPK_PATH
                        原始 MPK 文件路径（可选）
  -o, --old_format      使用 MPK V1 格式
  -n, --no_compress     不压缩文件（使用 origin_mpk_path 复制文件头信息时将忽略此选项）
```

## 通过 CSV 打包

将 CSV 中的文件打包成 MPK 文件。您可以使用可选选项 `--old_format` 使用 MPK V1 格式。

```
usage: mpk_tools.py packbycsv [-h] [-o] output csv_path

位置参数:
  output            输出 MPK 文件路径
  csv_path          包含要打包文件的目录

选项:
  -h, --help        显示此帮助信息并退出
  -o, --old_format  使用 MPK V1 格式
```

### CSV 结构

```csv
id,is_compressed,filename_on_disk,filename_in_archive
0,1,album.gxt,album.gxt
1,1,backlog.gxt,backlog.gxt
...
```

## MPK 文件结构
### MPK 头部（总共 64 字节）

| 名称 | 大小 | 值 |
| --- | --- | --- |
| **标识** | 4 字节 | "MPK"\0 |
| 次版本号 | 2 字节 | \0\0 |
| 主版本号 | 2 字节 | MPK V1 为 0x1，MPK V2 为 0x2 |
| 文件数量 | 4 字节/8 字节 | MPK V1 为 4 字节，MPK V2 为 8 字节 |
| 空字节 | 剩余字节 | |

次版本号似乎总是 0。

### 文件头部（每个文件 256 字节）

根据 `文件数量` 重复此部分。

#### MPK V1 格式
| 名称 | 大小 |
| --- | --- |
| 索引 | 4 字节 |
| 位置 | 4 字节 |
| 大小 | 4 字节 |
| 未压缩大小（如果没有压缩，则与之前相同） | 4 字节 |
| 空字节 | 16 字节 |
| 以空字符结尾的文件名 | 224 字节 |

#### MPK V2 格式

| 名称 | 大小 |
| --- | --- |
| 是否压缩 | 4 字节 |
| 索引 | 4 字节 |
| 位置 | 8 字节 |
| 大小 | 8 字节 |
| 未压缩大小（如果没有压缩，则与之前相同） | 8 字节 |
| 以空字符结尾的文件名 | 224 字节 |

### 原始文件数据（每个文件 n 字节，n 等于 `大小`）

根据 `文件数量` 重复此部分。

| 名称 | 大小 |
| --- | --- |
| 原始数据 | 等于 `大小` |

## 致谢

这个程序主要由 [@SpaceSkyNet](https://github.com/spaceskynet) 编写，许可为 [MIT License](https://github.com/spaceskynet/danser-gui/blob/master/LICENSE)。如果您支持这个项目，您可以通过单击[此页面](https://github.com/spaceskynet/mpk-tools/)右上角的星号给个star！

**感谢以下项目：**

1. [MagesPack](https://github.com/DanOl98/MagesPack): Mages 引擎 MPK 解包和重新打包工具（Steins;Gate Steam、Steins;Gate 0、Steins;Gate Elite、Chaos;Child 等）
2. [mpktools](https://github.com/ModzabazeR/mpktools): 用于打包/解包 Mages 包文件（.mpk）的工具
3. [ChaosChildPCTools](https://github.com/ningshanwutuobang/ChaosChildPCTools): ChaosChild 文件工具
4. [GARbro](https://github.com/crskycode/GARbro): 视觉小说资源浏览器