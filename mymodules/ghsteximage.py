"""Gregory Horror Show texture formats

Encompasses two formats, which I will call GHSTexImage and GHSTexImage2. GHSTexImage2
has some unknown extra data before and after the palette and pixels. The header gives
no indication of whether a given texture file is a GHSTexImage or GHSTexImage2.

Example of GHSTexImage2 can be found in FILE.STM at 28.stm/03.dat
"""
from io import SEEK_CUR
from math import ceil
from struct import unpack
from typing import BinaryIO, Optional, Sequence, Union

from PIL import Image

from mymodules.common import is_eof, keep_file_seek_position

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

palette_deswizzler = (
    {8: 16, 9: 17, 10: 18, 11: 19, 12: 20, 13: 21, 14: 22, 15: 23}
    | {16: 8, 17: 9, 18: 10, 19: 11, 20: 12, 21: 13, 22: 14, 23: 15}
    | {40: 48, 41: 49, 42: 50, 43: 51, 44: 52, 45: 53, 46: 54, 47: 55}
    | {48: 40, 49: 41, 50: 42, 51: 43, 52: 44, 53: 45, 54: 46, 55: 47}
    | {72: 80, 73: 81, 74: 82, 75: 83, 76: 84, 77: 85, 78: 86, 79: 87}
    | {80: 72, 81: 73, 82: 74, 83: 75, 84: 76, 85: 77, 86: 78, 87: 79}
    | {104: 112, 105: 113, 106: 114, 107: 115, 108: 116, 109: 117, 110: 118, 111: 119}
    | {112: 104, 113: 105, 114: 106, 115: 107, 116: 108, 117: 109, 118: 110, 119: 111}
    | {136: 144, 137: 145, 138: 146, 139: 147, 140: 148, 141: 149, 142: 150, 143: 151}
    | {144: 136, 145: 137, 146: 138, 147: 139, 148: 140, 149: 141, 150: 142, 151: 143}
    | {168: 176, 169: 177, 170: 178, 171: 179, 172: 180, 173: 181, 174: 182, 175: 183}
    | {176: 168, 177: 169, 178: 170, 179: 171, 180: 172, 181: 173, 182: 174, 183: 175}
    | {200: 208, 201: 209, 202: 210, 203: 211, 204: 212, 205: 213, 206: 214, 207: 215}
    | {208: 200, 209: 201, 210: 202, 211: 203, 212: 204, 213: 205, 214: 206, 215: 207}
    | {232: 240, 233: 241, 234: 242, 235: 243, 236: 244, 237: 245, 238: 246, 239: 247}
    | {240: 232, 241: 233, 242: 234, 243: 235, 244: 236, 245: 237, 246: 238, 247: 239}
)


class GHSTexUnknownPixFormat(ValueError):
    pass


class GHSTexExtraDataException(Exception):
    pass


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
        # Account for that one texture file that ends in 16 extra 0xff's
        bytes16 = file.read(16)
        if is_eof(file) and bytes16 == b"\xff" * 16:
            raise GHSTexExtraDataException
        file.seek(-16, SEEK_CUR)

        pixfmt_raw = unpack("<I", file.read(4))[0]
        pixfmt = _pixfmtval_pixfmt.get(pixfmt_raw)
        if pixfmt is None:
            raise GHSTexUnknownPixFormat(
                f"Unknown pixel format value {pixfmt_raw:#010x}"
            )

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
            palette = deswizzle_palette(palette)
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

    @classmethod
    def from_ghstex2file(cls, file: BinaryIO) -> "GHSTexImageSingle":
        pixfmt_raw = unpack("<I", file.read(4))[0]
        pixfmt = _pixfmtval_pixfmt.get(pixfmt_raw)
        if pixfmt is None:
            raise GHSTexUnknownPixFormat(
                f"Unknown pixel format value {pixfmt_raw:#010x}"
            )

        palette_size = unpack("<I", file.read(4))[0]
        tex_index = unpack("<I", file.read(4))[0]
        unk1, unk2 = unpack("<2H", file.read(4))

        file.seek(128, SEEK_CUR)

        if palette_size == 0:
            palette = None
        else:
            palette_flat = unpack(f"<{palette_size}B", file.read(palette_size))
            palette = list(chunks(palette_flat, 4))

        file.seek(32, SEEK_CUR)

        last, pixels_are_swizzled, unk3 = unpack("<HBB", file.read(4))
        pixels_size = unpack("<I", file.read(4))[0]
        tex_offset = unpack("<I", file.read(4))[0]
        width, height = unpack("<2H", file.read(4))

        file.seek(128, SEEK_CUR)

        pixels_raw = unpack(f"<{pixels_size}B", file.read(pixels_size))
        if pixfmt == "i4":
            pixels = list(from_nibbles(pixels_raw))
            if pixels_are_swizzled:
                pixels = deswizzle_pixels(pixels)
        else:  # elif pixfmt == "i8":
            palette = deswizzle_palette(palette)
            pixels = pixels_raw

        file.seek(32, SEEK_CUR)

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


@keep_file_seek_position
def quickcheck_tex_file(file) -> bool:
    """quickly check whether file is (very likely) a GHSTexImage

    Works by checking if expected header/palette/pixel values match the file size

    :param file: an open file with its current read position at 0
    :return: True if we think file is a Gregory Horror Show texture, False otherwise.
        After return, file's current read position is back to what it was originally
    """
    texcount = 0
    while True:
        header1_b = file.read(4)
        if header1_b not in (b"\x08\0\0\0", b"\x09\0\0\0"):
            # Account for that one texture that ends in 4 extra 0xffffffff's
            if header1_b == b"\xff\xff\xff\xff":
                read_and_check(file, 12)
                if is_eof(file) and texcount > 1:
                    return True
                else:
                    return False
            else:
                return False

        texcount += 1
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


@keep_file_seek_position
def quickcheck_tex2_file(file) -> bool:
    """quickly check whether file is (very likely) a GHSTexImage2

    :param file: an open file with its current read position at 0
    :return: True if we think file is a Gregory Horror Show texture, False otherwise.
        After return, file's current read position is back to what it was originally
    """
    while True:
        header1_b = file.read(4)
        if header1_b not in (b"\x08\0\0\0", b"\x09\0\0\0"):
            return False
        palette_size_b = file.read(4)
        if len(palette_size_b) < 4:
            return False
        palette_size = unpack("<I", palette_size_b)[0]
        if not read_and_check(file, 8 + 128 + palette_size + 32):
            return False
        if not read_and_check(file, 4):
            return False
        pixels_size_b = file.read(4)
        if len(pixels_size_b) < 4:
            return False
        pixels_size = unpack("<I", pixels_size_b)[0]
        if pixels_size == 0:
            return False
        if not read_and_check(file, 8 + 128 + pixels_size + 32):
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


def deswizzle_pixels(pixels_swizzled: SeqIndexed) -> SeqIndexed:
    if len(pixels_swizzled) != 65536:
        raise ValueError("Can only deswizzle pixels of length 65536 (256x256)")
    pixels_deswizzled = [0] * 65536

    for i, pixel in enumerate(pixels_swizzled):
        half128 = int(i >= 32768)
        columnbase = (i // 8192) % 4
        columnadd = (i // 512) % 2 * 4
        column32 = columnbase + columnadd
        row16 = (i // 64) % 8

        linebasei = (i // 1024) % 8
        linebase = [0, 1, 4, 5, 8, 9, 0xC, 0xD][linebasei]
        lineadd = (i // 32) % 2 * 2

        xbasei = i % 64
        xbasechooser = (
            [0x00, 0x04, 0x08, 0x0C, 0x10, 0x14, 0x18, 0x1C]
            + [0x01, 0x05, 0x09, 0x0D, 0x11, 0x15, 0x19, 0x1D]
            + [0x02, 0x06, 0x0A, 0x0E, 0x12, 0x16, 0x1A, 0x1E]
            + [0x03, 0x07, 0x0B, 0x0F, 0x13, 0x17, 0x1B, 0x1F]
            + [0x04, 0x00, 0x0C, 0x08, 0x14, 0x10, 0x1C, 0x18]
            + [0x05, 0x01, 0x0D, 0x09, 0x15, 0x11, 0x1D, 0x19]
            + [0x06, 0x02, 0x0E, 0x0A, 0x16, 0x12, 0x1E, 0x1A]
            + [0x07, 0x03, 0x0F, 0x0B, 0x17, 0x13, 0x1F, 0x1B]
        )
        # kludge part 1...
        # my initial assumptions about xbase were sometimes wrong, this kind of fixes it
        if linebasei in (2, 3, 6, 7):
            xbasechooser = (
                [0x04, 0x00, 0x0C, 0x08, 0x14, 0x10, 0x1C, 0x18]
                + [0x05, 0x01, 0x0D, 0x09, 0x15, 0x11, 0x1D, 0x19]
                + [0x06, 0x02, 0x0E, 0x0A, 0x16, 0x12, 0x1E, 0x1A]
                + [0x07, 0x03, 0x0F, 0x0B, 0x17, 0x13, 0x1F, 0x1B]
                + [0x00, 0x04, 0x08, 0x0C, 0x10, 0x14, 0x18, 0x1C]
                + [0x01, 0x05, 0x09, 0x0D, 0x11, 0x15, 0x19, 0x1D]
                + [0x02, 0x06, 0x0A, 0x0E, 0x12, 0x16, 0x1A, 0x1E]
                + [0x03, 0x07, 0x0B, 0x0F, 0x13, 0x17, 0x1B, 0x1F]
            )
        xbase = xbasechooser[xbasei]

        # kludge part 2...
        # pixels in certain parts of the output are wrongly arranged in a predictable
        # way, so this manually fixes them
        line = linebase + lineadd
        kludgeline = (0, 1, 2, 3, 8, 9, 10, 11)
        kludgexbase = [4, 5, 6, 7, 12, 13, 14, 15, 20, 21, 22, 23, 28, 29, 30, 31]
        if (xbase in kludgexbase and line in kludgeline) or (
            xbase not in kludgexbase and line not in kludgeline
        ):
            if lineadd == 2:
                lineadd = 0
            else:  # lineadd == 0
                lineadd = 2

        x = column32 * 32 + xbase
        y = half128 * 128 + row16 * 16 + linebase + lineadd
        newi = y * 256 + x
        pixels_deswizzled[newi] = pixel

    return pixels_deswizzled


def deswizzle_palette(swizzled_palette: SeqRGBA) -> SeqRGBA:
    if len(swizzled_palette) != 256:
        raise ValueError("Can only deswizzle palette of length 256")
    deswizzled_palette = list(swizzled_palette)  # shallow copy
    for i, col in enumerate(swizzled_palette):
        if i in palette_deswizzler:
            newi = palette_deswizzler[i]
            deswizzled_palette[newi] = col
    return deswizzled_palette
