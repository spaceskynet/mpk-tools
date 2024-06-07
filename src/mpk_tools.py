# A tool to pack and unpack MPK files for games in Mages. engine
import struct, os, zlib, csv
from os.path import join, dirname, isdir, isfile
import argparse

UInt32_MAX, UInt64_MAX = (1 << 32) - 1,  (1 << 64) - 1

class MPKHeader(object):
    MPK_SIGNATURE = b'MPK\x00'
    HEADER_SIZE = 0x40
    V1, V2 = 0x0001, 0x0002

    def __init__(self, data):
        if isinstance(data, bytes):
            self.read_header(data)
        else:
            self.new_header(*data)

    @property
    def is_v1(self):
        return self.version_major == MPKHeader.V1

    @property
    def is_v2(self):
        return self.version_major == MPKHeader.V2

    @property
    def files_count(self):
        return self._files_count

    @files_count.setter
    def files_count(self, value):
        if self.is_v1:
            if isinstance(value, int) and 0 <= value <= UInt32_MAX:
                self._files_count = value
            else:
                raise ValueError("files_count must be UInt32")
        else:
            if isinstance(value, int) and 0 <= value <= UInt64_MAX:
                self._files_count = value
            else:
                raise ValueError("files_count must be UInt64")

    def read_header(self, data):
        assert len(data) == MPKHeader.HEADER_SIZE, "Wrong size of mpk header"
        header, self.version_minor, self.version_major = struct.unpack('<4s2H', data[:0x8])
        if header != MPKHeader.MPK_SIGNATURE:
            raise ValueError('Invalid MPK file')
        if self.is_v1:
            self.files_count = struct.unpack('<I', data[0x8: 0x8 + 0x4])[0]
        else:
            self.files_count = struct.unpack('<Q', data[0x8: 0x8 + 0x8])[0]
    
    def new_header(self, version_minor, version_major, files_count):
        self.version_minor, self.version_major, self.files_count = version_minor, version_major, files_count

    def write_header(self):
        if self.is_v1:
            data = struct.pack('<4s2HI', MPKHeader.MPK_SIGNATURE, self.version_minor, self.version_major, self.files_count)
        else:
            data = struct.pack('<4s2HQ', MPKHeader.MPK_SIGNATURE, self.version_minor, self.version_major, self.files_count)
        data = data.ljust(MPKHeader.HEADER_SIZE, b'\x00')
        return data

class MPKFile(object):
    V1, V2 = MPKHeader.V1, MPKHeader.V2
    FILE_HEADER_SIZE = 0x100
    V1_PARAMS, V2_PARAMS = 5, 6
    NAME_MAX_LENGTH = 0xE0

    def __init__(self, version_major, data = None):
        if isinstance(data, bytes):
            assert len(data) == MPKFile.FILE_HEADER_SIZE, "Wrong size of mpk file header"
        
        self.ver = version_major
        if data is None: data = b'\x00' * MPKFile.FILE_HEADER_SIZE
        self.read_header(data)
        self.path = ""
    
    @property
    def is_v1(self):
        return self.ver == MPKFile.V1
    
    @property
    def is_v2(self):
        return self.ver == MPKFile.V2

    @property
    def is_compressed(self):
        if not hasattr(self, "_compressed"): # simple check
            return 0 if self.size == self.actual_size else 1
        else:
            return self.compressed
    
    @property
    def compressed(self):
        return self._compressed
    
    @compressed.setter
    def compressed(self, value):
        self._compressed = 1 if value else 0

    @property
    def id(self):
        return self._id
    
    @id.setter
    def id(self, value):
        if isinstance(value, int) and 0 <= value <= UInt32_MAX:
            self._id = value
        else:
            raise ValueError("id must be UInt32")
    
    @property
    def offset(self):
        return self._offset

    @offset.setter
    def offset(self, value):
        if self.is_v1:
            if isinstance(value, int) and 0 <= value <= UInt32_MAX:
                self._offset = value
            else:
                raise ValueError("offset must be UInt32")
        else:
            if isinstance(value, int) and 0 <= value <= UInt64_MAX:
                self._offset = value
            else:
                raise ValueError("offset must be UInt64")

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, value):
        if self.is_v1:
            if isinstance(value, int) and 0 <= value <= UInt32_MAX:
                self._size = value
            else:
                raise ValueError("size must be UInt32")
        else:
            if isinstance(value, int) and 0 <= value <= UInt64_MAX:
                self._size = value
            else:
                raise ValueError("size must be UInt64")

    @property
    def actual_size(self):
        return self._actual_size

    @actual_size.setter
    def actual_size(self, value):
        if self.is_v1:
            if isinstance(value, int) and 0 <= value <= UInt32_MAX:
                self._actual_size = value
            else:
                raise ValueError("actual_size must be UInt32")
        else:
            if isinstance(value, int) and 0 <= value <= UInt64_MAX:
                self._actual_size = value
            else:
                raise ValueError("actual_size must be UInt64")

    @property
    def name(self):
        return self._name
    
    @name.setter
    def name(self, value):
        if not isinstance(value, bytes):
            raise ValueError("name must be bytes")
        if len(value) > MPKFile.NAME_MAX_LENGTH:
            raise ValueError("name is too long")
        self._name = value.rstrip(b'\x00')

    def read_header(self, data):
        if self.is_v1:
            if isinstance(data, bytes):
                params = struct.unpack("<4I16x224s", data)
            else:
                params = data
            assert len(params) == MPKFile.V1_PARAMS, "Wrong counts of mpk v1 file params"
            
            self.read_V1_header(params)
        elif self.is_v2:
            if isinstance(data, bytes):
                params = struct.unpack("<2I3Q224s", data)
            else:
                params = data
            assert len(params) == MPKFile.V2_PARAMS, "Wrong counts of mpk v2 file params"

            self.read_V2_header(params)
        else:
            raise NotImplementedError("Not valid MPK archive format.")

    def read_V1_header(self, params):
        (
            self.id,            # UInt32
            self.offset,        # UInt32
            self.size,          # UInt32
            self.actual_size,   # UInt32
            self.name           # 0xE0 string
        ) = params

    def read_V2_header(self, params):
        (
            self.compressed,    # UInt32
            self.id,            # UInt32
            self.offset,        # UInt64
            self.size,          # UInt64
            self.actual_size,   # UInt64
            self.name           # 0xE0 string
        ) = params

    def write_V1_header(self):
        data = struct.pack("<4I16x224s", self.id, self.offset, self.size, self.actual_size, self.name.ljust(MPKFile.NAME_MAX_LENGTH, b'\x00'))
        return data

    def write_V2_header(self):
        data = struct.pack("<2I3Q224s", self.is_compressed, self.id, self.offset, self.size, self.actual_size, self.name.ljust(MPKFile.NAME_MAX_LENGTH, b'\x00'))
        return data
    
    def write_header(self):
        if self.is_v1:
            return self.write_V1_header()
        elif self.is_v2:
            return self.write_V2_header()
        else:
            raise NotImplementedError("Not valid MPK archive format.")

    @property
    def is_null(self):
        return self.write_header() == b'\x00' * MPKFile.FILE_HEADER_SIZE

    def list_info(self):
        print("Id:", self.id)
        print("File Name:", self.name.decode())
        print("Compressed:", self.is_compressed > 0)
        print("Offset:", hex(self.offset).upper())
        print("File Size:", self.size)
        
        if self.is_compressed:
            print("Actual Size:", self.actual_size)
        print()

class MPK(object):
    MpkSignature = b'MPK\x00'
    V1, V2 = (0, 1), (0, 2) # minor, major
    CSV_HEADER = ("id", "is_compressed", "filename_on_disk", "filename_in_archive")

    def __init__(self, file = None, file_ver = None):
        if file is None:
            # default create MPK V2
            if file_ver is None: file_ver = MPK.V2
            self.header = MPKHeader((*file_ver, 0))
            self.files = []
        else:
            if isinstance(file, str):
                self.fp = open(file, 'rb')
            else:
                self.fp = file
            self.fp.seek(0)
            self.header = MPKHeader(data = self.fp.read(MPKHeader.HEADER_SIZE))
            self.files = []
            for i in range(self.header.files_count):
                mpk_file = MPKFile(data = self.fp.read(MPKFile.FILE_HEADER_SIZE), version_major = self.header.version_major)
                self.files.append(mpk_file)
    
    def __del__(self):
        if hasattr(self, 'fp') and not self.fp.closed: 
            self.fp.close()
    
    def unpack(self, output_path: str, toc_file_path: str | None = None):
        if self.fp is None:
            print("No files to unpack")
            return

        assert len(self.files) == self.header.files_count, "File counts is not matched"
        if toc_file_path:
            with open(toc_file_path, "w", encoding="utf-8", newline="") as csv_file:
                item = csv.writer(csv_file)
                item.writerow(MPK.CSV_HEADER)

        for mpk_file in self.files:
            if mpk_file.is_null: continue
            mpk_file.list_info()
            file_name = mpk_file.name.decode()
            mpk_file.path = join(output_path, file_name)
            file_dir = dirname(mpk_file.path)
            if not isdir(file_dir):
                os.makedirs(file_dir)
            
            with open(mpk_file.path, "wb") as file_in_archive:
                self.fp.seek(mpk_file.offset)
                buf = self.fp.read(mpk_file.size)
                if mpk_file.is_compressed:
                    buf = zlib.decompress(buf)
                file_in_archive.write(buf)

            if toc_file_path:
                with open(toc_file_path, "a", encoding="utf-8", newline="") as csv_file:
                    item = csv.writer(csv_file)
                    item.writerow([mpk_file.id, mpk_file.is_compressed, mpk_file.path, file_name])

    @classmethod
    def parse_files_in_csv(self, toc_file_path: str):
        files_list = []
        with open(toc_file_path, 'r', encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                files_list.append(row)

        print("Total files found: {0}\n".format(len(files_list)))
        return files_list

    @classmethod
    def parse_files_from_dir(self, input_dir: str, compress: bool = True):
        files_list = []
        index = 0
        for root, dirs, files in os.walk(input_dir):
            for name in files:
                file_path = join(root, name)
                files_list.append({
                    "id": index,
                    "is_compressed": 1 if compress else 0,
                    "filename_in_archive": os.path.relpath(file_path, input_dir),
                    "filename_on_disk": file_path
                })
                index += 1
        
        print("Total files found: {0}\n".format(len(files_list)))
        return files_list

    def parse_files_from_dir_and_copy_headers(self, input_dir: str):
        files_list = []
        for mpk_file in self.files:
            file_path = join(input_dir, mpk_file.name.decode())
            if not isfile(file_path):
                raise FileNotFoundError(f"{mpk_file.name} is not found in {input_dir}")
            files_list.append({
                "id": mpk_file.id,
                "is_compressed": mpk_file.compressed,
                "filename_in_archive": mpk_file.name.decode(),
                "filename_on_disk": file_path
            })
        
        print("Total files found: {0}\n".format(len(files_list)))
        return files_list

    def pack(self, output_mpk_path: str, files_list: list | None = None):
        if files_list:
            self.files.clear()
            self.header.files_count = len(files_list)
            for file in files_list:
                mpk_file = MPKFile(version_major = self.header.version_major)
                mpk_file.id, mpk_file.compressed = int(file["id"]), int(file["is_compressed"])
                mpk_file.name = file["filename_in_archive"].replace('\\', '/').encode()
                mpk_file.path = file["filename_on_disk"]
                self.files.append(mpk_file)

        if not self.files:
            print("No files to pack")
            return

        # write header
        self.fp = open(output_mpk_path, "wb")
        self.fp.seek(0)
        self.fp.write(self.header.write_header())

        file_content_offset = MPKHeader.HEADER_SIZE + self.header.files_count * MPKFile.FILE_HEADER_SIZE
        file_header_offset = MPKHeader.HEADER_SIZE

        for mpk_file in self.files:
            if mpk_file.is_null: continue
            mpk_file.offset = file_content_offset
            with open(mpk_file.path, "rb") as f:
                buf = f.read()
                mpk_file.actual_size = f.tell()
            if mpk_file.is_compressed:
                buf = zlib.compress(buf)
            mpk_file.size = len(buf)

            # write file header
            self.fp.seek(file_header_offset)
            self.fp.write(mpk_file.write_header())
            file_header_offset += MPKFile.FILE_HEADER_SIZE
            # write file content
            self.fp.seek(file_content_offset)
            self.fp.write(buf)
            file_content_offset += mpk_file.size
            
            mpk_file.list_info()

def pack_mpk_by_csv(output_mpk_path: str, file_list_csv_path: str, old_format: bool = False):
    file_ver = MPK.V1 if old_format else MPK.V2
    mpk = MPK(file_ver=file_ver)

    files = MPK.parse_files_in_csv(file_list_csv_path)
    mpk.pack(output_mpk_path, files)

def pack_mpk_by_dir(output_mpk_path: str, pack_dir: str, origin_mpk_path: str | None = None, old_format: bool = False, no_compress: bool = False):
    file_ver = MPK.V1 if old_format else MPK.V2
    mpk = MPK(file_ver = file_ver)

    if origin_mpk_path and isinstance(origin_mpk_path, str):
        origin_mpk = MPK(file = origin_mpk_path)
        files = origin_mpk.parse_files_from_dir_and_copy_headers(pack_dir)
    else:
        files = mpk.parse_files_from_dir(pack_dir, compress = not no_compress)
    
    mpk.pack(output_mpk_path, files)

def unpack_mpk(mpk_path: str, output_dir: str, file_list_csv_path: str | None = None):
    mpk = MPK(mpk_path)
    mpk.unpack(output_path = output_dir, toc_file_path = file_list_csv_path)

if __name__ == "__main__": 
    parser = argparse.ArgumentParser(description='MPK Tool By SpaceSkyNet')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Pack command
    pack_parser = subparsers.add_parser('pack', help='Pack files into MPK')
    pack_parser.add_argument('output', type=str, help='Output MPK file path')
    pack_parser.add_argument('pack_dir', type=str, help='Directory containing files to pack')
    pack_parser.add_argument('-m', '--origin_mpk_path', type=str, help='Path to original MPK file (optional)')
    pack_parser.add_argument('-o', '--old_format', action='store_true', help='Use MPK V1 format')
    pack_parser.add_argument('-n', '--no_compress', action='store_true', help='Not compress files (Ignored when use origin_mpk_path to copy headers)')

    pack_parser = subparsers.add_parser('packbycsv', help='Pack files into MPK By CSV')
    pack_parser.add_argument('output', type=str, help='Output MPK file path')
    pack_parser.add_argument('csv_path', type=str, help='Directory containing files to pack')
    pack_parser.add_argument('-o', '--old_format', action='store_true', help='Use MPK V1 format')

    # Unpack command
    unpack_parser = subparsers.add_parser('unpack', help='Unpack files from MPK')
    unpack_parser.add_argument('mpk_path', type=str, help='Path to MPK file')
    unpack_parser.add_argument('output', type=str, help='Output directory')
    unpack_parser.add_argument('-c', '--csv_path', type=str, help='Path to CSV file for file list (optional)')

    args = parser.parse_args()

    if args.command == 'pack':
        pack_mpk_by_dir(
            output_mpk_path=args.output,
            pack_dir=args.pack_dir,
            origin_mpk_path=args.origin_mpk_path,
            old_format=args.old_format,
            no_compress=args.no_compress
        )
    elif args.command == 'packbycsv':
        pack_mpk_by_csv(
            output_mpk_path=args.output,
            file_list_csv_path=args.csv_path,
            old_format=args.old_format
        )
    elif args.command == 'unpack':
        unpack_mpk(
            mpk_path=args.mpk_path,
            output_dir=args.output,
            file_list_csv_path=args.csv_path
        )
    else:
        parser.print_help()