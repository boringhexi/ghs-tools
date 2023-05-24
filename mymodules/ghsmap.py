"""Gregory Horror Show .MAP container format"""
from io import SEEK_CUR
from struct import unpack
from typing import BinaryIO


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
