# ghs-tools

Various tools for Gregory Horror Show (PS2) data

## Requirements
- A resonably recent version of Python 3
- [Pillow](https://pypi.org/project/Pillow/) for texture conversion

## Included tools
### ghs_filestm_unpack.py
Unpacks FILE.STM (European or Japanese version), automatically unpacking and decompressing all contents and converting all textures.

### ghs_modelmeta_extract.py
Extracts various model data from the executable file, then drops the resulting .ghs files into the existing FILE.STM folder structure.

## Importing models into Blender
1. Run `ghs_filestm_unpack.py -v FILE.STM` to unpack the EU version's FILE.STM contents.
   - The resulting folder will be named `GHS_EU_FILE_STM`.
2. Then, use `ghs_modelmeta_extract.py [path_to_executable]` on the EU version executable file.
   - The EU version executable file is named `SLES_519.33`.
   - This will extract `###.ghs` files into the existing `GHS_EU_FILE_STM` folder structure.
3. Finally, use [the Blender addon](https://github.com/boringhexi/blender3d_GregoryHorrorShow) to import the .ghs files into Blender.
