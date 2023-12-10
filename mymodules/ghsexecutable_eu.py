from struct import unpack
from typing import BinaryIO

modelmeta_start = 0x1FF510
modelmeta_len = 0x45A


def into_executable(ps2_pointer: int) -> int:
    """from a ps2 pointer, return the equivalent pointer into the executable data

    :param ps2_pointer: ps2 pointer, such as seen in ps2dis
    :return: pointer into executable file's data
    """
    return ps2_pointer - 0xFFF80


def get_stmindex(modelmeta_index: int, execfile: BinaryIO) -> int:
    stmindex_start = modelmeta_start + (0x10 * modelmeta_index) + 0xC
    execfile.seek(stmindex_start)
    (stmindex,) = unpack("<i", execfile.read(4))
    return stmindex


def get_boneparentinfo_and_numbones(
    modelmeta_index: int, execfile: BinaryIO
) -> tuple[list, int]:
    boneparentinfo = []
    bpidata_start = modelmeta_start + (0x10 * modelmeta_index)
    execfile.seek(bpidata_start)
    (bpipointer,) = unpack("<I", execfile.read(4))
    if bpipointer == 0:
        return boneparentinfo, 0
    execfile.seek(into_executable(bpipointer))
    (sentinel,) = unpack("<i", execfile.read(4))
    numbones = 0
    while sentinel != -1:
        numbones += 1
        parent, unk1, unk2, unk3, unk4 = unpack("<hhfff", execfile.read(16))
        if parent == -1:
            parent = None
        boneparentinfo.append(
            {"parent": parent, "unk1": unk1, "unk2": unk2, "unk3": unk3, "unk4": unk4}
        )
        (sentinel,) = unpack("<i", execfile.read(4))
    return boneparentinfo, numbones


def get_default_body_parts(modelmeta_index: int, numbones: int, execfile: BinaryIO):
    defaultbodyparts = []
    dbpdata_start = modelmeta_start + (0x10 * modelmeta_index) + 4
    execfile.seek(dbpdata_start)
    (dbppointer,) = unpack("<I", execfile.read(4))
    if dbppointer == 0:
        return defaultbodyparts
    execfile.seek(into_executable(dbppointer))

    for x in range(numbones):
        defaultbodypart, unk = unpack("<hh", execfile.read(4))
        if defaultbodypart == -1:
            defaultbodypart = None
        defaultbodyparts.append({"pm2": defaultbodypart, "unk": unk})
    return defaultbodyparts


def get_anims(modelmeta_index: int, numbones: int, execfile: BinaryIO):
    allanims = []
    allanimsdata_start = modelmeta_start + (0x10 * modelmeta_index) + 8
    execfile.seek(allanimsdata_start)
    (allanimspointer,) = unpack("<I", execfile.read(4))
    if allanimspointer == 0:
        return allanims

    # allanims pointer
    #  list of: (s32 num frames, u32 pointer to allbodyparts)
    #   list of: pointer to a body part keyframes
    #    list of: keyframe

    execfile.seek(into_executable(allanimspointer))
    (num_frames,) = unpack("<i", execfile.read(4))
    while num_frames != -1:
        this_anim = []
        (animbodyparts_pointer,) = unpack("<I", execfile.read(4))
        if animbodyparts_pointer != 0:
            savemyplace_in_allanims = execfile.tell()
            execfile.seek(into_executable(animbodyparts_pointer))

            for x in range(numbones):
                this_bodypart = []
                abp_unk, bodypartkeyframes_pointer = unpack("<iI", execfile.read(8))
                if bodypartkeyframes_pointer != 0:
                    savemyplace_in_animbodyparts = execfile.tell()

                    execfile.seek(into_executable(bodypartkeyframes_pointer))
                    while True:
                        (keyframestart,) = unpack("<f", execfile.read(4))
                        (
                            boneidx_unused,
                            pm2,
                            interp_type,
                            bpkf_unk,
                            interp_start,
                            interp_delta,
                        ) = unpack("<BbbBff", execfile.read(12))
                        if pm2 == -1:
                            pm2 = None
                        this_keyframe = {
                            "keyframe_start": keyframestart,
                            "boneidx_unused": boneidx_unused,
                            "pm2": pm2,
                            "interp_type": interp_type,
                            "unknown": bpkf_unk,
                            "interp_start": interp_start,
                            "interp_delta": interp_delta,
                        }
                        this_bodypart.append(this_keyframe)
                        if keyframestart >= 999:
                            break

                    execfile.seek(savemyplace_in_animbodyparts)
                this_anim.append(this_bodypart)

            execfile.seek(savemyplace_in_allanims)

        allanims.append({"anim_len": num_frames, "animation_data": this_anim})
        (num_frames,) = unpack("<i", execfile.read(4))

    return allanims
