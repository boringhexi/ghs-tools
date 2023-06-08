"""Gregory Horror Show .MPR (mesh position/rotation) animation format"""
from struct import unpack
from typing import BinaryIO

from mymodules.common import is_eof, keep_file_seek_position


@keep_file_seek_position
def quickcheck_mpr_file(mprfile: BinaryIO) -> bool:
    numbones_data = mprfile.read(4)
    if len(numbones_data) < 4:
        return False
    num_bones = unpack("<I", numbones_data)[0]
    offsets_data = mprfile.read(num_bones * 4)
    if len(offsets_data) < num_bones * 4:
        return False
    for i in range(num_bones):
        various_data = mprfile.read(4)
        if len(various_data) < 4:
            return False
        num_frames, is_float = unpack("<HxB", various_data)
        if is_float:
            frame_length = 24
        else:
            frame_length = 12
        frames_data = mprfile.read(num_frames * frame_length)
        if len(frames_data) < num_frames * frame_length:
            return False
    if not is_eof(mprfile):
        return False
    return True


@keep_file_seek_position
def quickcheck_mpr_forcedfloat_file(mprfile: BinaryIO) -> bool:
    """some .mpr files have is_float unset but use floats anyway; this detects them"""
    numbones_data = mprfile.read(4)
    if len(numbones_data) < 4:
        return False
    num_bones = unpack("<I", numbones_data)[0]
    offsets_data = mprfile.read(num_bones * 4)
    if len(offsets_data) < num_bones * 4:
        return False
    for i in range(num_bones):
        various_data = mprfile.read(4)
        if len(various_data) < 4:
            return False
        num_frames, is_float = unpack("<HxB", various_data)
        if is_float:
            return False
        frame_length = 24
        frames_data = mprfile.read(num_frames * frame_length)
        if len(frames_data) < num_frames * frame_length:
            return False
    if not is_eof(mprfile):
        return False
    return True
