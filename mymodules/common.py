from io import SEEK_CUR


def keep_file_seek_position(func):
    """after func runs, seek the file back to its original read position"""

    def wrapper(file, *args, **kwargs):
        tell = file.tell()
        ret = func(file, *args, **kwargs)
        file.seek(tell)
        return ret

    return wrapper


def is_eof(file):
    """return True if file is at exactly the end of its data"""
    b = file.read(1)
    was_already_eof = len(b) == 0
    if not was_already_eof:
        file.seek(-1, SEEK_CUR)
    return was_already_eof
