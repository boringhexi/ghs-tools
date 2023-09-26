#!/usr/bin/env python3

import argparse
import json
import os
import sys
from pathlib import Path
from sys import argv

from mymodules.ghsexecutable_eu import (
    get_anims,
    get_boneparentinfo_and_numbones,
    get_default_body_parts,
    get_stmindex,
    modelmeta_len,
)
from mymodules.ghsmodelmetaoutloc import get_modelmeta_outloc


def build_argparser():
    parser = argparse.ArgumentParser()
    parser.description = (
        "Extract ###.ghs files from the provided Gregory Horror Show "
        "executable, which can then be imported into Blender"
    )
    parser.add_argument(
        metavar="EXECUTABLE",
        dest="executable_path",
        help="path to executable from the EU (SLES_519.33) or JP (SLPM_653.24) version "
        "of Gregory Horror Show",
        type=Path,
    )
    parser.add_argument(
        "-d",
        "--directory",
        metavar="ALTERNATE_DIR",
        dest="alternate_dir",
        help="By default, the files are extracted into a directory named "
        "GHS_EU_FILE_STM or GHS_JP_FILE_STM depending on which version the executable "
        "is from. Use this to override the name of the directory.",
        type=Path,
    )
    return parser


def main(args=tuple(argv[1:])):
    """args: sequence of command line argument strings"""
    parser = build_argparser()
    parsed_args = parser.parse_args(args)

    executable_path: Path = parsed_args.executable_path
    alternate_dir: Path = parsed_args.alternate_dir

    if executable_path.name.upper() == "SLES_519.33":
        version = "EU"
    elif executable_path.name.upper() == "SLPM_653.24":
        version = "JP"
        print(
            "Sorry, Japanese version is not supported yet... "
            "Please use the European version for now",
            file=sys.stderr,
        )
        sys.exit(1)
    else:
        print(
            f"unknown executable filename {executable_path.name!r}, "
            "expecting 'SLES_519.33' or 'SLPM_653.24'",
            file=sys.stderr,
        )
        sys.exit(1)

    if alternate_dir:
        destdir = alternate_dir
    elif version == "EU":
        destdir = Path("GHS_EU_FILE_STM")
    elif version == "JP":
        destdir = Path("GHS_JP_FILE_STM")
    else:
        # should never happen due to above check
        destdir = Path("GHS_UNK_FILE_STM")

    with open(executable_path, "rb") as executable_file:
        ghs_unmatched_dir = destdir / "ghs_unmatched"
        os.makedirs(ghs_unmatched_dir, exist_ok=True)

        for modelmeta_i in range(modelmeta_len):
            stm_index = get_stmindex(modelmeta_i, executable_file)
            boneparentinfo, num_bones = get_boneparentinfo_and_numbones(
                modelmeta_i, executable_file
            )
            defaultbodyparts = get_default_body_parts(
                modelmeta_i, num_bones, executable_file
            )
            allanims = get_anims(modelmeta_i, num_bones, executable_file)
            outdata = {
                "bone_parenting_info": boneparentinfo,
                "default_body_parts": defaultbodyparts,
                "animations": allanims,
            }

            subdir, filename = get_modelmeta_outloc(modelmeta_i, stm_index)
            if subdir is None:
                outdir = ghs_unmatched_dir
            else:
                outdir = destdir / subdir
                os.makedirs(outdir, exist_ok=True)
            with open(outdir / filename, "wt") as ghsfile:
                json.dump(outdata, ghsfile)


if __name__ == "__main__":
    main()
