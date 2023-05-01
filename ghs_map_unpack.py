#!/usr/bin/env python3

import os
from sys import argv

from mymodules.ghsmap import GHSMap


def main(args=tuple(argv[1:])):
    if not args:
        print(f"{argv[0]} [file.map] [file2.map] ...")
    for path in args:
        print(os.path.basename(path))
        with open(path, "rb") as infile:
            ghsmap = GHSMap.from_mapfile(infile)

        outdir = f"{path}_extract"
        if not os.path.exists(outdir):
            os.mkdir(outdir)

        for i, contentfile in enumerate(ghsmap):
            outname = f"{i:08}{os.path.extsep}{contentfile.ext}"
            outpath = f"{outdir}{os.path.sep}{outname}"
            with open(outpath, "wb") as outfile:
                outfile.write(contentfile.data)


if __name__ == "__main__":
    main()
