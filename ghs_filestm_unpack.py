#!/usr/bin/env python3

import argparse
import os
import sys
from io import SEEK_END, BytesIO
from pathlib import Path
from sys import argv
from typing import BinaryIO, Optional

from ghs_sli_decompress import decompress
from mymodules.common import is_eof
from mymodules.ghsmap import GHSMap, GHSMapx, quickcheck_mapx_file
from mymodules.ghsmeshposrot import quickcheck_mpr_file
from mymodules.ghsstmcontainer import (
    GHSStmContainer,
    quickcheck_stm_file,
    quickget_num_contentfiles_from_stm,
)
from mymodules.ghsteximage import (
    GHSTexExtraDataException,
    GHSTexImageSingle,
    quickcheck_tex2_file,
    quickcheck_tex_file,
)


def build_argparser():
    parser = argparse.ArgumentParser()
    parser.description = (
        "Unpack contents from the provided Gregory Horror Show FILE.STM"
    )
    parser.add_argument(
        metavar="FILE_STM",
        dest="file_stm_path",
        help=f"path to FILE.STM from the EU or JP version of Gregory Horror Show",
    )
    parser.add_argument(
        "-d",
        "--directory",
        metavar="ALTERNATE_DIR",
        dest="alternate_dir",
        help="By default, contents are unpacked to a directory named "
        " GHS_EU_FILE_STM or GHS_JP_FILE_STM depending on which version it comes from. "
        "Use this to override the name of the directory.",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        dest="verbose",
        action="store_true",
        help="list contents as they are unpacked",
    )
    return parser


def vindent(num: int) -> str:
    """verbose indent. Return the str of whitespace with which to indent verbose output

    :param num: indentation level
    :return: str of whitespace with which to indent verbose output
    """
    return "  " * num


def main(args=tuple(argv[1:])):
    """args: sequence of command line argument strings"""
    parser = build_argparser()
    parsed_args = parser.parse_args(args)

    file_stm_path = parsed_args.file_stm_path
    alternate_dir = parsed_args.alternate_dir
    verbose = parsed_args.verbose
    vindentlvl = 0  # verbose output indentation level

    with open(file_stm_path, "rb") as file_stm:
        if not quickcheck_stm_file(file_stm):
            print(f"{file_stm_path} is not a valid STM file", file=sys.stderr)
            sys.exit(1)

        num_contentfiles = quickget_num_contentfiles_from_stm(file_stm)
        if alternate_dir is None:
            if num_contentfiles == 300:
                root_dir = "GHS_EU_FILE_STM"
            elif num_contentfiles == 212:
                root_dir = "GHS_JP_FILE_STM"
            else:
                root_dir = "GHS_UNK_FILE_STM"
        else:
            root_dir = alternate_dir
        root_dir = Path(root_dir)
        os.makedirs(root_dir, exist_ok=True)
        process_stm(
            file_stm,
            root_dir,
            subdirname_idx=None,
            verbose=verbose,
            vindentlvl=vindentlvl,
        )


def process_stm(
    file: BinaryIO,
    outdir: Path,
    subdirname_idx: Optional[int],
    from_sli: bool = False,
    verbose: bool = False,
    vindentlvl: int = 0,
):
    if subdirname_idx is not None:
        dot_sli = ".sli" if from_sli else ""
        outname = f"{subdirname_idx:03x}{dot_sli}.stm"
        outdir /= outname
        if verbose:
            print(f"{vindent(vindentlvl)}{outname}")
        os.makedirs(outdir, exist_ok=True)

    stmcontainer = GHSStmContainer.from_stmfile(file)
    for i, contentdata in enumerate(stmcontainer):
        contentfile = BytesIO(contentdata)
        if contentdata.startswith(b"SLI"):
            process_sli(
                contentfile, outdir, i, verbose=verbose, vindentlvl=vindentlvl + 1
            )
        elif contentdata.startswith(b"MAP"):
            process_map(
                contentfile, outdir, i, verbose=verbose, vindentlvl=vindentlvl + 1
            )
        elif contentdata.startswith(b"PM2"):
            process_file_with_ext(
                contentfile,
                "pm2",
                outdir,
                i,
                verbose=verbose,
                vindentlvl=vindentlvl + 1,
            )
        elif contentdata.startswith(b"ATR"):
            process_file_with_ext(
                contentfile,
                "atr",
                outdir,
                i,
                verbose=verbose,
                vindentlvl=vindentlvl + 1,
            )
        elif contentdata.startswith(b"SDW"):
            process_file_with_ext(
                contentfile,
                "sdw",
                outdir,
                i,
                verbose=verbose,
                vindentlvl=vindentlvl + 1,
            )
        elif quickcheck_tex_file(contentfile):
            process_tex(
                contentfile, outdir, i, verbose=verbose, vindentlvl=vindentlvl + 1
            )
        elif quickcheck_tex2_file(contentfile):
            process_tex(
                contentfile,
                outdir,
                i,
                tex2=True,
                verbose=verbose,
                vindentlvl=vindentlvl + 1,
            )
        elif quickcheck_stm_file(contentfile, len(contentdata)):
            process_stm(
                contentfile, outdir, i, verbose=verbose, vindentlvl=vindentlvl + 1
            )
        elif quickcheck_mpr_file(contentfile):
            process_file_with_ext(
                contentfile,
                "mpr",
                outdir,
                i,
                verbose=verbose,
                vindentlvl=vindentlvl + 1,
            )
        elif quickcheck_mapx_file(contentfile, len(contentdata)):
            process_mapx(
                contentfile, outdir, i, verbose=verbose, vindentlvl=vindentlvl + 1
            )
        else:
            process_dat_000_fff(
                contentfile, outdir, i, verbose=verbose, vindentlvl=vindentlvl + 1
            )


def process_sli(
    file: BinaryIO,
    outdir: Path,
    filename_idx: int,
    verbose: bool = False,
    vindentlvl: int = 0,
):
    if verbose:
        outname = f"{filename_idx:03x}.sli"
        print(f"{vindent(vindentlvl)}decompressing {outname}")

    contentdata = decompress(file)
    contentfile = BytesIO(contentdata)
    if quickcheck_tex_file(contentfile):
        process_tex(
            contentfile,
            outdir,
            filename_idx,
            from_sli=True,
            verbose=verbose,
            vindentlvl=vindentlvl,
        )
    elif quickcheck_tex2_file(contentfile):
        process_tex(
            contentfile,
            outdir,
            filename_idx,
            from_sli=True,
            tex2=True,
            verbose=verbose,
            vindentlvl=vindentlvl,
        )
    elif quickcheck_stm_file(contentfile, len(contentdata)):
        process_stm(
            contentfile,
            outdir,
            filename_idx,
            from_sli=True,
            verbose=verbose,
            vindentlvl=vindentlvl,
        )
    else:
        process_dat_000_fff(
            contentfile,
            outdir,
            filename_idx,
            from_sli=True,
            verbose=verbose,
            vindentlvl=vindentlvl,
        )


def process_map(
    file: BinaryIO,
    outdir: Path,
    subdirname_idx: int,
    verbose: bool = False,
    vindentlvl: int = 0,
):
    outname = f"{subdirname_idx:03x}.map"
    if verbose:
        print(f"{vindent(vindentlvl)}{outname}")
    outdir /= outname
    os.makedirs(outdir, exist_ok=True)

    mapcontainer = GHSMap.from_mapfile(file)
    for i, content in enumerate(mapcontainer):
        contentdata = content.data
        contentfile = BytesIO(contentdata)
        if contentdata.startswith(b"PM2"):
            process_file_with_ext(
                contentfile,
                "pm2",
                outdir,
                i,
                verbose=verbose,
                vindentlvl=vindentlvl + 1,
            )
        elif contentdata.startswith(b"ATR"):
            process_file_with_ext(
                contentfile,
                "atr",
                outdir,
                i,
                verbose=verbose,
                vindentlvl=vindentlvl + 1,
            )
        else:
            process_dat_000_fff(
                contentfile, outdir, i, verbose=verbose, vindentlvl=vindentlvl + 1
            )


def process_mapx(
    file: BinaryIO,
    outdir: Path,
    subdirname_idx: int,
    verbose: bool = False,
    vindentlvl: int = 0,
):
    outname = f"{subdirname_idx:03x}.mapx"
    if verbose:
        print(f"{vindent(vindentlvl)}{outname}")
    outdir /= outname
    os.makedirs(outdir, exist_ok=True)

    mapcontainer = GHSMapx.from_mapxfile(file)
    for i, content in enumerate(mapcontainer):
        contentdata = content.data
        contentfile = BytesIO(contentdata)
        if contentdata.startswith(b"PM2"):
            process_file_with_ext(
                contentfile,
                "pm2",
                outdir,
                i,
                verbose=verbose,
                vindentlvl=vindentlvl + 1,
            )
        else:
            process_dat_000_fff(
                contentfile, outdir, i, verbose=verbose, vindentlvl=vindentlvl + 1
            )


def process_dat_000_fff(
    file: BinaryIO,
    outdir: Path,
    filename_idx: int,
    from_sli=False,
    verbose: bool = False,
    vindentlvl: int = 0,
):
    dot_sli = ".sli" if from_sli else ""
    first16 = file.read(16)
    filesize = file.seek(0, SEEK_END)
    file.seek(0)
    if first16 == b"\x00" * 16 and filesize == 16:
        outname = f"{filename_idx:03x}{dot_sli}.000"
    elif first16 == b"\xff" * 16 and filesize == 16:
        outname = f"{filename_idx:03x}{dot_sli}.fff"
    else:
        outname = f"{filename_idx:03x}{dot_sli}.dat"

    if verbose:
        print(f"{vindent(vindentlvl)}{outname}")
    outpath = outdir / outname
    with open(outpath, "wb") as outfile:
        outfile.write(file.read())


def process_file_with_ext(
    file: BinaryIO,
    ext: str,
    outdir: Path,
    filename_idx: int,
    verbose: bool = False,
    vindentlvl: int = 0,
):
    outname = f"{filename_idx:03x}.{ext}"
    if verbose:
        print(f"{vindent(vindentlvl)}{outname}")
    outpath = outdir / outname
    with open(outpath, "wb") as outfile:
        outfile.write(file.read())


def process_tex(
    file: BinaryIO,
    outdir: Path,
    subdirname_idx: int,
    from_sli: bool = False,
    tex2: bool = False,
    verbose: bool = False,
    vindentlvl: int = 0,
):
    dot_sli = ".sli" if from_sli else ""
    dot_tex = ".tex2" if tex2 else ".tex"
    outname = f"{subdirname_idx:03x}{dot_sli}{dot_tex}"
    if verbose:
        print(f"{vindent(vindentlvl)}{outname}")
    outdir /= outname
    os.makedirs(outdir, exist_ok=True)

    if tex2:
        read_tex = GHSTexImageSingle.from_ghstex2file
    else:
        read_tex = GHSTexImageSingle.from_ghstexfile
    ghstexs = []
    while not is_eof(file):
        try:
            ghstexs.append(read_tex(file))
        # except GHSTexUnknownPixFormat as e:
        #     print(f"!! {e}")
        #     continue
        except GHSTexExtraDataException:
            pass

    for i, ghstex in enumerate(ghstexs):
        tex_outname = f"{i:03x}_{ghstex.tex_offset:#05x}.png"
        tex_outpath = outdir / tex_outname
        with open(tex_outpath, "wb") as outfile:
            if verbose:
                print(f"{vindent(vindentlvl + 1)}{tex_outname}")
            ghstex.write_to_png(outfile)


if __name__ == "__main__":
    main()
