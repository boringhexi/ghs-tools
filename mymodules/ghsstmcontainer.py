"""Gregory Horror Show .STM container format"""
from io import SEEK_END
from struct import unpack
from typing import BinaryIO

from mymodules.common import keep_file_seek_position


class GHSStmContainer(list[bytes]):
    @classmethod
    def from_stmfile(cls, file: BinaryIO) -> "GHSStmContainer":
        offsets = []
        sizes = []
        datas = []
        while True:
            offset, size_raw = unpack("<2I", file.read(8))
            is_final = size_raw & 0x80000000
            size = size_raw & 0x7FFFFFFF
            offsets.append(offset)
            sizes.append(size)
            if is_final:
                break
        for offset, size in zip(offsets, sizes):
            file.seek(offset)
            data = file.read(size)
            datas.append(data)
        return cls(datas)


@keep_file_seek_position
def quickget_num_contentfiles_from_stm(file: BinaryIO):
    num_contentfiles = 0
    while True:
        size_raw = unpack("<4x1I", file.read(8))[0]
        is_final = size_raw & 0x80000000
        num_contentfiles += 1
        if is_final:
            return num_contentfiles


@keep_file_seek_position
def quickcheck_stm_file(stmfile: BinaryIO, stmfilesize: int = None) -> bool:
    """quickly check whether stmfile is (very likely) a GHSStmContainer

    Checks for the following conditions:

    - all offsets are a multiple of 0x10
    - no offsets or sizes are 0
    - no file extends past the end of the stm container
    - each offset is after the previous file, with a gap of no more than 15 bytes
    - the size of the final file reaches the end of the STM file

    :param stmfile: an open file with its current read position at 0
    :param stmfilesize: optional size of stmfile, helps determine things a little faster
    :return: True if we think stmfile is a GHSStmContainer, False otherwise.
        After return, file's current read position is back to what it was originally
    """
    ...
    if stmfilesize is None:
        stmfile.seek(0, SEEK_END)
        stmfilesize = stmfile.tell()
        stmfile.seek(0)
    prev_size_end = None

    while True:
        offset_data = stmfile.read(4)
        if len(offset_data) < 4:
            return False
        offset = unpack("<I", offset_data)[0]

        # ensure all offsets are a multiple of 0x10
        if offset & 0xF:
            return False

        size_data = stmfile.read(4)
        if len(size_data) < 4:
            return False
        size_raw = unpack("<I", size_data)[0]
        is_final = size_raw & 0x80000000
        size = size_raw & 0x7FFFFFFF

        # ensure no offsets or sizes are 0
        if (offset == 0) or (size == 0):
            return False

        # ensure no file extends past the end of the stm container
        if (offset + size) > stmfilesize:
            return False

        # ensure each offset is after the previous file, with a gap <= 15 bytes
        if prev_size_end is not None:
            gap = offset - prev_size_end
            if not 0 <= gap <= 15:
                return False
        prev_size_end = offset + size

        if is_final:
            final_offset = offset
            final_size = size
            break

    # ensure final file reaches the end of the STM container
    final_padding = stmfilesize - (final_offset + final_size)
    if final_padding > 2:
        # EU 4d.stm ends in 2 padding bytes
        return False

    return True
