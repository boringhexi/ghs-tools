from io import SEEK_CUR
from math import ceil
from struct import unpack
from typing import Union, Optional, Sequence, BinaryIO

from PIL import Image

SeqIndexed = Sequence[int]
SeqRGB = Sequence[tuple[int, int, int]]
SeqRGBA = Sequence[tuple[int, int, int, int]]


PIXEL_FORMATS = ("rgba32", "rgb24", "i8", "i4")

_pixfmtval_pixfmt = {
    8: "i4",
    9: "i8",
    # ...: "rgb24",
    # ...: "rgba32",
}


class GHSTexUnknownPixFormat(ValueError):
    pass


def is_eof(file):
    """return True if file is at exactly the end of its data"""
    b = file.read(1)
    was_already_eof = len(b) == 0
    if not was_already_eof:
        file.seek(-1, SEEK_CUR)
    return was_already_eof


def read_and_check(file, size):
    """read size bytes into file, and make sure that much data actually exists"""
    return len(file.read(size)) == size


class GHSTexImageSingle:
    def __init__(
        self,
        width: int,
        height: int,
        pixels: Union[SeqRGB, SeqRGBA, SeqIndexed],
        palette: Optional[SeqRGBA] = None,
        pixfmt: Optional[str] = None,
        tex_offset: int = 0,
        alpha128: bool = True,
    ) -> None:
        self.width = width
        self.height = height
        self.palette = palette
        self.pixels = pixels

        if pixfmt is not None:
            if pixfmt not in PIXEL_FORMATS:
                raise GHSTexUnknownPixFormat(f"Unknown pixel format {pixfmt!r}")
            if pixfmt == "i4" and width % 2:
                raise ValueError(
                    f"Pixel format i4 requires an even-numbered width, width={width}"
                )
        else:
            if palette:
                pixfmt = "i4" if (len(palette) <= 16 and width % 2 == 0) else "i8"
            # else:  # no palette
            #     if pixels and max(len(pix) for pix in pixels) == 4:
            #         pixfmt = "rgba32"
            #     else:
            #         pixfmt = "rgb24"
        self.pixfmt = pixfmt

        self.tex_offset = tex_offset
        self.alpha128 = alpha128

    @classmethod
    def from_ghstexfile(cls, file: BinaryIO) -> "GHSTexImageSingle":
        pixfmt_raw = unpack("<I", file.read(4))[0]
        pixfmt = _pixfmtval_pixfmt.get(pixfmt_raw)
        if pixfmt is None:
            raise GHSTexUnknownPixFormat(f"Unknown pixel format value {pixfmt_raw!r}")

        palette_size = unpack("<I", file.read(4))[0]
        tex_index = unpack("<I", file.read(4))[0]
        unk1, unk2 = unpack("<2H", file.read(4))

        if palette_size == 0:
            palette = None
        else:
            palette_flat = unpack(f"<{palette_size}B", file.read(palette_size))
            palette = list(chunks(palette_flat, 4))

        unk3, unk4 = unpack("<2H", file.read(4))
        pixels_size = unpack("<I", file.read(4))[0]
        tex_offset = unpack("<I", file.read(4))[0]
        width, height = unpack("<2H", file.read(4))

        pixels_raw = unpack(f"<{pixels_size}B", file.read(pixels_size))
        if pixfmt == "i4":
            pixels = list(from_nibbles(pixels_raw))
        else:  # elif pixfmt == "i8":
            pixels = pixels_raw

        return cls(
            width,
            height,
            pixels,
            palette=palette,
            pixfmt=pixfmt,
            tex_offset=tex_offset,
            alpha128=True,
        )

    @property
    def size(self) -> tuple[int, int]:
        return self.width, self.height

    @property
    def alpha255(self) -> bool:
        return not self.alpha128

    def write_to_png(self, file: BinaryIO) -> None:
        if self.palette is not None:
            image = Image.new("RGBA", self.size)
            ghs_palette = self.palette255
            ghs_pixels_rgba = [ghs_palette[i] for i in self.pixels]
            image.putdata(ghs_pixels_rgba)
        else:
            image = Image.new("RGBA", self.size)
            image.putdata(self.pixels255)
        image.save(file, format="png")

    @property
    def palette255(self) -> Optional[SeqRGBA]:
        """palette with 255-based alpha"""
        if self.palette is None:
            return None
        if self.alpha255:
            return self.palette
        elif self.alpha128:
            # get alpha255 = floor(alpha128/128*255)
            return [
                (r, g, b, int(a128 / 128 * 255)) for (r, g, b, a128) in self.palette
            ]

    @property
    def pixels255(self) -> Union[SeqRGB, SeqRGBA, SeqIndexed]:
        """pixels with 255-based alpha"""
        if not self.pixels:
            return []
        if self.palette is None and len(self.pixels[0]) == 4:  # RGBA
            if self.alpha128:
                # get alpha255 = floor(alpha128/128*255)
                return [
                    (r, g, b, int(a128 / 128 * 255)) for (r, g, b, a128) in self.pixels
                ]
            elif self.alpha255:
                return self.pixels
        else:  # RGB or indexed
            return self.pixels


class GHSTexImageMulti(list):
    @classmethod
    def from_ghstexfile(cls, file: BinaryIO) -> "GHSTexImageMulti":
        ghstexs = []
        while not is_eof(file):
            ghstexs.append(GHSTexImageSingle.from_ghstexfile(file))
        return cls(ghstexs)


def quickcheck_tex_file(file) -> bool:
    """quickly check whether file is (very likely) a Gregory Horror Show texture

    Works by checking if expected header/palette/pixel values match the file size

    :param file: an open file with its current read position at 0
    :return: True if we think file is a Gregory Horror Show texture, False otherwise.
        After return, file's current read position is undefined
    """
    while True:
        if not read_and_check(file, 4):
            return False
        palette_size_b = file.read(4)
        if len(palette_size_b) < 4:
            return False
        palette_size = unpack("<I", palette_size_b)[0]
        if not read_and_check(file, 8 + palette_size):
            return False
        if not read_and_check(file, 4):
            return False
        pixels_size_b = file.read(4)
        if len(pixels_size_b) < 4:
            return False
        pixels_size = unpack("<I", pixels_size_b)[0]
        if pixels_size == 0:
            return False
        if not read_and_check(file, 8 + pixels_size):
            return False
        # now at beginning of next texture or end of file
        if is_eof(file):
            return True


def chunks(seq, n, fillseq=None):
    """yield n-sized chunks from seq

    seq: a sequence to be chunked
    n: desired size of each chunk
    fillseq: If the last chunk would be shorter than length n, it will be extended to
    length n by concatenating it with fillseq repeating. If specified, it should
    support being multiplied and added to seq. If not specified, the last chunk can
    be shorter than n.
    yields: sequences of the same type as seq
    raises: ValueError if n==0
    """
    if n == 0:
        raise ValueError("Invalid chunk size 0")

    seq_len = len(seq)
    num_leftovers = seq_len % n
    short_len = seq_len - num_leftovers

    for i in range(0, short_len, n):
        yield seq[i : i + n]

    # handle leftovers
    if num_leftovers:
        if fillseq is None:
            # yield last chunk as-is
            yield seq[short_len:]
        else:
            # extend last chunk and yield it
            num_tofill = n - num_leftovers
            fillseq_extended = fillseq * ceil(num_tofill / len(fillseq))
            yield seq[short_len:] + fillseq_extended[:num_tofill]


def from_nibbles(bytes_, signed=False):
    """yield 4-bit nibble values in bytes_, low nibbles first

    (order example: nibbles(b'\x21\x43\x65') yields the nibbles 1,2,3,4,5,6)

    bytes_: a bytes object OR a single int representing a single byte.
    signed: if True, nibbles are yielded as signed values,
        i.e. nibbles between [0x8 to 0xf] will yield respective values [-8 to -1]
    yields: integers in the range 0,15 for signed=False, -8,7 for signed=True
    """
    if not hasattr(bytes_, "__iter__"):
        bytes_ = (bytes_,)
    for b in bytes_:
        if signed:
            yield -(b & 0b1000) + (b & 0b0111)
            yield -(b >> 4 & 0b1000) + (b >> 4 & 0b0111)
        else:
            yield b & 0b1111
            yield (b >> 4) & 0b1111
