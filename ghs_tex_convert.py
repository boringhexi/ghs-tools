#!/usr/bin/env python3
import os
from sys import argv

from mymodules.ghsteximage import (
    GHSTexUnknownPixFormat,
    GHSTexImageMulti,
    quickcheck_tex_file,
)


def main(args=tuple(argv[1:])):
    for path in args:
        with open(path, "rb") as file:
            print(os.path.basename(path))
            is_ghstex = quickcheck_tex_file(file)
            if not is_ghstex:
                print("!! Not a GHS texture file")
                continue
            file.seek(0)  # since read position is undefined after quickcheck_tex_file
            try:
                ghstexmulti = GHSTexImageMulti.from_ghstexfile(file)
            except GHSTexUnknownPixFormat as e:
                print(f"!! {e}")
                continue
        outpath_base = os.path.splitext(path)[0]
        for ghstex in ghstexmulti:
            outpath = f"{outpath_base}_{ghstex.tex_offset:#05x}.png"
            with open(outpath, "wb") as outfile:
                ghstex.write_to_png(outfile)


if __name__ == "__main__":
    main()
