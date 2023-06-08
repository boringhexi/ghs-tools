#!/usr/bin/env python3
import os
import struct
import sys


def decompress(file) -> bytearray:
    magic = file.read(4)
    if magic != b"SLID":
        raise ValueError(f"Not a valid SLID file, magic is {magic!r}")
    file_size, decompressed_size, compressed_size = struct.unpack("<3I", file.read(12))
    compressed_data = file.read(compressed_size)

    slid_buffer = bytearray(0x1000)
    decompressed_data = bytearray(decompressed_size)
    s1_processed_bytes = a0_ci = 0
    a1_di = 0
    s2 = 0
    s3 = 0xFEE
    while s1_processed_bytes < compressed_size:
        s2 = s2 >> 1
        if not s2 & 0x100:
            compressed_byte = compressed_data[a0_ci]
            s2 = compressed_byte | 0xFF00
            s1_processed_bytes += 1
            a0_ci += 1

        if s2 & 1:
            compressed_byte = compressed_data[a0_ci]
            a0_ci += 1
            s1_processed_bytes += 1
            decompressed_data[a1_di] = compressed_byte
            a1_di += 1
            slid_buffer[s3 & 0xFFF] = compressed_byte
            s3 = (s3 + 1) & 0xFFF
            continue

        t0_byte1 = compressed_data[a0_ci]
        a3_byte2 = compressed_data[a0_ci + 1]
        s1_processed_bytes += 2
        a0_ci += 2
        t8 = (a3_byte2 & 0xF) + 2
        s4 = t0_byte1 | ((a3_byte2 & 0xF0) << 4)
        if t8 < 0:  # impossible condition? it's there in the original asm
            continue

        t9 = 0
        s0 = t8 - 8
        # if not (t8 + 1) < 9:
        if not t8 < 8:
            while True:
                decompressed_byte = slid_buffer[s4 & 0xFFF]
                decompressed_data[a1_di] = decompressed_byte
                slid_buffer[s3 & 0xFFF] = decompressed_byte

                decompressed_byte = slid_buffer[(s4 + 1) & 0xFFF]
                decompressed_data[a1_di + 1] = decompressed_byte
                slid_buffer[(s3 + 1) & 0xFFF] = decompressed_byte

                decompressed_byte = slid_buffer[(s4 + 2) & 0xFFF]
                decompressed_data[a1_di + 2] = decompressed_byte
                slid_buffer[(s3 + 2) & 0xFFF] = decompressed_byte

                decompressed_byte = slid_buffer[(s4 + 3) & 0xFFF]
                decompressed_data[a1_di + 3] = decompressed_byte
                slid_buffer[(s3 + 3) & 0xFFF] = decompressed_byte

                decompressed_byte = slid_buffer[(s4 + 4) & 0xFFF]
                decompressed_data[a1_di + 4] = decompressed_byte
                slid_buffer[(s3 + 4) & 0xFFF] = decompressed_byte

                decompressed_byte = slid_buffer[(s4 + 5) & 0xFFF]
                decompressed_data[a1_di + 5] = decompressed_byte
                slid_buffer[(s3 + 5) & 0xFFF] = decompressed_byte

                decompressed_byte = slid_buffer[(s4 + 6) & 0xFFF]
                decompressed_data[a1_di + 6] = decompressed_byte
                slid_buffer[(s3 + 6) & 0xFFF] = decompressed_byte

                decompressed_byte = slid_buffer[(s4 + 7) & 0xFFF]
                decompressed_data[a1_di + 7] = decompressed_byte
                slid_buffer[(s3 + 7) & 0xFFF] = decompressed_byte

                a1_di += 8
                s3 += 8
                s4 += 8
                t9 += 8

                if t9 >= s0:  # wait, is it >= or > ...? either seems to work
                    break

        while True:
            decompressed_byte = slid_buffer[s4 & 0xFFF]
            decompressed_data[a1_di] = decompressed_byte
            slid_buffer[s3 & 0xFFF] = decompressed_byte

            a1_di += 1
            s3 += 1
            s4 += 1
            t9 += 1
            if t9 > t8:
                break

    return decompressed_data


def main(args=tuple(sys.argv[1:])):
    if not args:
        print(f"{sys.argv[0]} [.sli file] [.sli file] ...")
    for filepath in args:
        print(os.path.basename(filepath))
        with open(filepath, "rb") as file:
            decompressed_data = decompress(file)
        with open(f"{filepath}_dec", "wb") as file:
            file.write(decompressed_data)


if __name__ == "__main__":
    main()
