#!/usr/bin/env python3
import os
from sys import argv

from mymodules.ghsteximage import (
    GHSTexExtraDataException,
    GHSTexImageSingle,
    GHSTexUnknownPixFormat,
    is_eof,
    quickcheck_tex2_file,
    quickcheck_tex_file,
)


def main(args=tuple(argv[1:])):
    if not args:
        print(f"{argv[0]} [texture file] [texture file] ...")
    for path in args:
        with open(path, "rb") as file:
            print(os.path.basename(path))
            is_ghstex = quickcheck_tex_file(file)
            read_tex = GHSTexImageSingle.from_ghstexfile
            if not is_ghstex:
                is_ghstex2 = quickcheck_tex2_file(file)
                if is_ghstex2:
                    read_tex = GHSTexImageSingle.from_ghstex2file
                else:
                    print("!! Not a GHS texture file")
                    continue
            ghstexs = []
            while not is_eof(file):
                try:
                    ghstexs.append(read_tex(file))
                except GHSTexUnknownPixFormat as e:
                    print(f"!! {e}")
                    continue
                except GHSTexExtraDataException:
                    pass
        outpath_base = os.path.splitext(path)[0]
        digits = len(str(len(ghstexs)))
        for i, ghstex in enumerate(ghstexs):
            if len(ghstexs) > 1:
                outpath = f"{outpath_base}-{i:0{digits}}_{ghstex.tex_offset:#05x}.png"
            else:
                outpath = f"{outpath_base}_{ghstex.tex_offset:#05x}.png"
            with open(outpath, "wb") as outfile:
                ghstex.write_to_png(outfile)


if __name__ == "__main__":
    main()
