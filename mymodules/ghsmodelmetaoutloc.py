# ghs modelmeta output locations
# tells where to put .ghs files and what to name them
from typing import Optional

characters = {
    0x00: ("02c.sli.tex", "boy"),
    0x02: ("02e.sli.tex", "girl"),
    0x04: ("0aa.stm/000.sli.tex", "gregory"),
    0x06: ("0aa.stm/002.sli.tex", "judgmentboy"),
    0x08: ("0aa.stm/004.sli.tex", "nekozombie"),
    0x0A: ("0aa.stm/006.sli.tex", "lostdoll"),
    0x0C: ("0aa.stm/008.sli.tex", "hellschef"),
    0x0E: ("0aa.stm/00a.sli.tex", "catherine"),
    0x10: ("0aa.stm/00c.sli.tex", "mummypapa"),
    0x12: ("0aa.stm/00e.sli.tex", "mummydog"),
    0x14: ("0aa.stm/010.sli.tex", "cactusgunman"),
    0x16: ("0aa.stm/012.sli.tex", "cactusgirl"),
    0x18: ("0aa.stm/014.sli.tex", "tvfish"),
    0x1A: ("0aa.stm/016.sli.tex", "clockmaster"),
    0x1C: ("0aa.stm/018.sli.tex", "myson"),
    0x1E: ("0aa.stm/01a.sli.tex", "rouletteboy"),
    0x20: ("0aa.stm/01c.sli.tex", "angeldog"),
    0x22: ("0aa.stm/01e.sli.tex", "judgmentboygold"),
    0x24: ("0b0.sli.tex", "gregorymama"),
    0x26: ("0aa.stm/022.sli.tex", "james"),
    0x28: ("0b4.sli.tex", "gregoryghost"),
    0x2A: ("0aa.stm/000.sli.tex", "gregory_duplicate"),
    0x2C: ("04d.sli.stm/009.sli.tex", "frogfortuneteller"),
    0x2E: ("0b2.sli.tex", "death"),
    0x30: ("0aa.stm/02c.sli.tex", "devildog"),
    0x32: ("0aa.stm/000.sli.tex", "gregory_duplicate"),
}

character_shadows = {
    0x01: ("02c.sli.tex", "boy"),
    0x03: ("02e.sli.tex", "girl"),
    0x05: ("0aa.stm/000.sli.tex", "gregory"),
    0x07: ("0aa.stm/002.sli.tex", "judgmentboy"),
    0x09: ("0aa.stm/004.sli.tex", "nekozombie"),
    0x0B: ("0aa.stm/006.sli.tex", "lostdoll"),
    0x0D: ("0aa.stm/008.sli.tex", "hellschef"),
    0x0F: ("0aa.stm/00a.sli.tex", "catherine"),
    0x11: ("0aa.stm/00c.sli.tex", "mummypapa"),
    0x13: ("0aa.stm/00e.sli.tex", "mummydog"),
    0x15: ("0aa.stm/010.sli.tex", "cactusgunman"),
    0x17: ("0aa.stm/012.sli.tex", "cactusgirl"),
    0x19: ("0aa.stm/014.sli.tex", "tvfish"),
    0x1B: ("0aa.stm/016.sli.tex", "clockmaster"),
    0x1D: ("0aa.stm/018.sli.tex", "myson"),
    0x1F: ("0aa.stm/01a.sli.tex", "rouletteboy"),
    0x21: ("0aa.stm/01c.sli.tex", "angeldog"),
    0x23: ("0aa.stm/01e.sli.tex", "judgmentboygold"),
    0x25: ("0b0.sli.tex", "gregorymama"),
    0x27: ("0aa.stm/022.sli.tex", "james"),
    0x29: ("0b4.sli.tex", "gregoryghost"),
    0x2B: ("0aa.stm/000.sli.tex", "gregory_duplicate"),
    0x2D: ("04d.sli.stm/009.sli.tex", "frogfortuneteller"),
    0x2F: ("0b2.sli.tex", "death"),
    0x31: ("0aa.stm/02c.sli.tex", "devildog"),
    0x33: ("0aa.stm/000.sli.tex", "gregory_duplicate"),
}

held_objects = {
    0x35: ("029.stm/000.sli.stm", "candle"),
    0x36: ("029.stm/001.sli.stm", "bigknife"),
    0x37: ("029.stm/002.sli.stm", "syringe"),
    0x39: ("029.stm/003.sli.stm", "smallknife"),
    0x3A: ("029.stm/004.sli.stm", "grayfolded"),
    0x3B: ("029.stm/01b.sli.stm", "graystick"),
    0x3C: ("029.stm/005.sli.stm", "pill"),
    0x3E: ("029.stm/01d.sli.stm", "shinyspot"),
    0x3F: ("029.stm/01a.sli.stm", "donut"),
    0x40: ("029.stm/019.sli.stm", "fork"),
    0x41: ("029.stm/018.sli.stm", "pencil"),
    0x42: ("029.stm/006.sli.stm", "unuseddoll"),
    0x43: ("029.stm/007.sli.stm", "gun"),
    0x44: ("029.stm/01e.sli.stm", "starburst"),
    0x45: ("029.stm/008.sli.stm", "roses"),
    0x46: ("029.stm/009.sli.stm", "heavenorhelldoor"),
    0x47: ("029.stm/01f.sli.stm", "star"),
    0x49: ("029.stm/00a.sli.stm", "starwand"),
    0x4A: ("029.stm/00b.sli.stm", "lasso"),
    0x4D: ("029.stm/00c.sli.stm", "obento"),
    0x4E: ("029.stm/00d.sli.stm", "broom"),
    0x4F: ("029.stm/00e.sli.stm", "eyeglasses"),
    0x50: ("029.stm/00f.sli.stm", "chopsticks"),
    0x51: ("029.stm/01c.sli.stm", "papers"),
    0x52: ("029.stm/010.sli.stm", "potatochips"),
    0x53: ("029.stm/011.sli.stm", "foodplate"),
    0x54: ("029.stm/012.sli.stm", "ghsbook"),
    0x55: ("029.stm/013.sli.stm", "bananapeel"),
    0x56: ("029.stm/014.sli.stm", "doll"),
    0x57: ("029.stm/015.sli.stm", "dirtybook"),
    0x58: ("029.stm/020.sli.stm", "whitedots"),
    0x59: ("029.stm/016.sli.stm", "remotecontrol"),
    0x5B: ("029.stm/023.sli.stm", "10tweight"),
    0x5D: ("029.stm/024.sli.stm", "shinyspot2"),
    0x5E: ("029.stm/025.sli.stm", "dollarsign"),
    0x5F: ("029.stm/026.sli.stm", "heart"),
    0x60: ("029.stm/027.sli.stm", "greenbook"),
    0x63: ("029.stm/021.sli.stm", "sunburst"),
    0x64: ("029.stm/017.sli.stm", "soulcollection"),
}

figurines = {
    0x418: ("03c.sli.stm/001.tex2", "gregory_figurine"),
    0x419: ("03c.sli.stm/003.tex2", "james_figurine"),
    0x41A: ("03c.sli.stm/005.tex2", "nekozombie_figurine"),
    0x41B: ("03c.sli.stm/007.tex2", "catherine_figurine"),
    0x41C: ("03c.sli.stm/009.tex2", "judgmentboy_figurine"),
    0x41D: ("03c.sli.stm/00b.tex2", "lostdoll_figurine"),
    0x41E: ("03c.sli.stm/00d.tex2", "mummydog_figurine"),
    0x41F: ("03c.sli.stm/00f.tex2", "mummypapa_figurine"),
    0x420: ("03c.sli.stm/011.tex2", "cactusgunman_cactusgirl_figurine"),
    0x421: ("03c.sli.stm/013.tex2", "hellschef_figurine"),
    0x422: ("03c.sli.stm/015.tex2", "tvfish_figurine"),
    0x423: ("03c.sli.stm/017.tex2", "rouletteboy_figurine"),
    0x424: ("03c.sli.stm/019.tex2", "clockmaster_figurine"),
    0x425: ("03c.sli.stm/01b.tex2", "myson_figurine"),
    0x426: ("03c.sli.stm/01d.tex2", "angeldog_devildog_figurine"),
    0x427: ("03c.sli.stm/01f.tex2", "judgmentboygold_figurine"),
}

effects = {
    0x66: ("027.sli.stm/002.stm", "soulbottle"),
    0x67: ("027.sli.stm/003.stm", "knockeffect"),
    0x68: ("027.sli.stm/004.stm", "remotecontrol_beam"),
}

rouletteboy_horrorshow = (0xA0, 0xA1, 0xA2, 0xA3, 0xA4)
rouletteboy_horrorshow = {
    i: ("0c0.sli.stm", "rouletteboy_horrorshow") for i in rouletteboy_horrorshow
}

doors = range(0xA7, 0xEE + 1)
doors = {i: ("028.stm", "door") for i in doors}


def get_modelmeta_outloc(
    modelmeta_i: int, stm_index: int = -1
) -> tuple[Optional[str], str]:
    """returns outsubdir, outfilename

    outsubdir will be None if there is no match, in that case it's up to the caller to
    decide what to do
    """
    outsubdir = None
    outfilename = f"{modelmeta_i:03x}.ghs"

    ghs_stuff = (
        characters | held_objects | figurines | effects | rouletteboy_horrorshow | doors
    )
    if modelmeta_i in ghs_stuff:
        outsubdir, namepart = ghs_stuff[modelmeta_i]
        if namepart:
            outfilename = f"{modelmeta_i:03x}_{namepart}.ghs"
            
    elif modelmeta_i in character_shadows:
        outsubdir, namepart = character_shadows[modelmeta_i]
        if namepart:
            outfilename = f"{modelmeta_i:03x}_{namepart}.ghs-shadow"
            
    elif stm_index != -1:  # room props that provide a .stm index
        outsubdir = f"{stm_index:03x}.sli.stm"

    return outsubdir, outfilename
