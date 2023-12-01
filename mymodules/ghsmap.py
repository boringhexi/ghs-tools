"""Gregory Horror Show .MAP container format"""
from io import SEEK_CUR, SEEK_END
from struct import unpack
from typing import BinaryIO

from mymodules.common import keep_file_seek_position


class GHSMap(list):
    @classmethod
    def from_mapfile(cls, file: BinaryIO) -> "GHSMap":
        magic = file.read(3)
        if magic != b"MAP":
            raise ValueError(f"Not a valid MAP file (magic='{magic})'")
        file.seek(5, SEEK_CUR)
        num1, num2 = unpack("<2H", file.read(4))
        file.seek(4, SEEK_CUR)
        num_offsets = num1 * num2
        offsets_raw = unpack(f"<{num_offsets}I", file.read(num_offsets * 4))
        offsets = [o for o in offsets_raw if o > 0]
        offsets.sort()
        filesizes = [o2 - o1 for o1, o2 in zip(offsets, offsets[1:])]
        filesizes.append(-1)  # last content file extends to the end of the MAP file
        contentfiles = []
        for offset, size in zip(offsets, filesizes):
            file.seek(offset)
            data = file.read(size)
            contentfiles.append(ContentFile(data))
        return cls(contentfiles)


class ContentFile:
    def __init__(self, data: bytes):
        self.data = data

    @property
    def ext(self) -> str:
        if self.data.startswith(b"PM2"):
            return "pm2"
        elif self.data.startswith(b"ATR"):
            return "atr"
        else:
            return "dat"


@keep_file_seek_position
def quickcheck_mapx_file(file, mapxfilesize: int = None) -> bool:
    if mapxfilesize is None:
        file.seek(0, SEEK_END)
        mapxfilesize = file.tell()
        file.seek(0)
    filesize_data = file.read(4)
    if len(filesize_data) < 4:
        return False
    filesize = unpack("<I", filesize_data)[0]
    if filesize != mapxfilesize:
        return False
    nums_data = file.read(4)
    if len(nums_data) < 4:
        return False
    num1, num2 = unpack("<2H", nums_data)
    num_offsets = num1 * num2
    offsets_data = file.read(num_offsets * 4)
    if len(offsets_data) < num_offsets * 4:
        return False
    offsets_raw = unpack(f"<{num_offsets}I", offsets_data)
    offsets = [o for o in offsets_raw if o > 0]
    if not offsets:
        return False
    for offset in offsets:
        file.seek(offset)
        magic = file.read(3)
        if magic != b"PM2":
            return False
    return True
